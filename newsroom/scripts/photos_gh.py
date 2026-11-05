"""Run the photo workflows for one run tag and wait for them, without pushing anything to main.

  python3 newsroom/scripts/photos_gh.py find <tag> <queries.json>
      Searches Commons for the queries ({"key": "search||N"}), waits, and unpacks the candidates into
      /home/claude/gn-work/pcv<tag>/photo-candidates/ (candidates.json + thumbs/). Prints the folder.
  python3 newsroom/scripts/photos_gh.py download <tag> <photo-id> [<photo-id> ...]
      Downloads exactly these content/photos.json entries (use the ids register.py printed; composite
      parts cx-* included), waits, and unpacks them into /home/claude/gn-work/raw-<tag>/. Prints the folder.
Exits non-zero (with the reason) when the workflow fails or takes longer than its time limit.
"""
import json, subprocess, sys, time, os, shutil, tarfile, io

REPO = 'puneetspanesar/gandhinews'
R = '/home/claude/gandhinews/'
W = '/home/claude/gn-work/'


def sh(*a, check=True):
    r = subprocess.run(a, capture_output=True, text=True)
    if check and r.returncode: sys.exit(f'{" ".join(a[:4])}...: {r.stderr.strip() or r.stdout.strip()}')
    return r.stdout


def dispatch_and_wait(workflow, fields, limit_min):
    before = time.time()
    args = ['gh', 'workflow', 'run', workflow, '-R', REPO, '--ref', 'main']
    for k, v in fields.items(): args += ['-f', f'{k}={v}']
    sh(*args)
    run_id = None
    for _ in range(40):
        time.sleep(3)
        runs = json.loads(sh('gh', 'run', 'list', '-R', REPO, '--workflow', workflow, '-L', '10', '--json', 'databaseId,createdAt,status,conclusion,event'))
        for r in runs:
            t = time.mktime(time.strptime(r['createdAt'], '%Y-%m-%dT%H:%M:%SZ')) - time.timezone
            if r['event'] == 'workflow_dispatch' and t >= before - 5:
                run_id = r['databaseId']; break
        if run_id: break
    if not run_id: sys.exit(f'{workflow}: dispatched but the run never appeared')
    end = time.time() + limit_min * 60
    while time.time() < end:
        r = json.loads(sh('gh', 'run', 'view', str(run_id), '-R', REPO, '--json', 'status,conclusion'))
        if r['status'] == 'completed':
            if r['conclusion'] != 'success':
                log = sh('gh', 'run', 'view', str(run_id), '-R', REPO, '--log-failed', check=False)[-1500:]
                sys.exit(f'{workflow} run {run_id} ended {r["conclusion"]}:\n{log}')
            return run_id
        time.sleep(10)
    sys.exit(f'{workflow} run {run_id} still running after {limit_min} minutes')


def fetch_branch(branch, dest):
    sh('git', '-C', R, 'fetch', '-q', 'origin', f'+{branch}:refs/remotes/origin/{branch}')
    shutil.rmtree(dest, ignore_errors=True); os.makedirs(dest)
    data = subprocess.run(['git', '-C', R, 'archive', f'origin/{branch}'], capture_output=True).stdout
    tarfile.open(fileobj=io.BytesIO(data)).extractall(dest)


mode, tag = sys.argv[1], sys.argv[2]
if mode == 'find':
    q = json.load(open(sys.argv[3]))
    assert isinstance(q, dict) and q, 'queries must be a non-empty JSON object'
    dispatch_and_wait('find-photos.yml', {'part': tag, 'queries': json.dumps(q, ensure_ascii=False)}, 20)
    dest = f'{W}pcv{tag}'; fetch_branch(f'photo-candidates-{tag}', dest)
    c = json.load(open(f'{dest}/photo-candidates/candidates.json'))
    print(dest, '|', sum(len(v.get('candidates') or []) for v in c.values()), 'candidates for', len(c), 'queries')
elif mode == 'download':
    ids = set(sys.argv[3:])
    P = json.load(open(R + 'content/photos.json'))
    ent = [{'id': p['id'], 'url': p['sourceUrl']} for p in P if p['id'] in ids and not p.get('composite')]
    missing = ids - {e['id'] for e in ent} - {p['id'] for p in P if p.get('composite')}
    if missing: sys.exit(f'not in content/photos.json (or composites, which are built, not downloaded): {sorted(missing)}')
    if not ent: sys.exit('nothing to download')
    dispatch_and_wait('download-photos.yml', {'part': tag, 'entries': json.dumps(ent)}, 30)
    dest = f'{W}raw-{tag}'; fetch_branch(f'photo-raw-{tag}', dest)
    got = [f[:-4] for f in os.listdir(dest) if f.endswith('.jpg')]
    print(dest, '|', len(got), 'of', len(ent), 'downloaded')
else:
    sys.exit(__doc__)
