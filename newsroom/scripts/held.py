"""Held stories (newsroom/held/{en,hi}/<id>.md + newsroom/held/<id>.json with why/kind/held_at).
  python3 newsroom/scripts/held.py list                       every hold, its age and why
  python3 newsroom/scripts/held.py hold <id> <picture|facts|other> "<why>"   take a story off the site (both languages)
  python3 newsroom/scripts/held.py republish <id>             put it back (only once the reason is fixed: a picture hold
                                                              needs its main picture in content/photos.map.json)
  python3 newsroom/scripts/held.py expire                     delete holds older than 12 hours (that news is gone)
Every run does `list` and `expire` at the start, and republishes picture holds whose picture now exists.
"""
import json, os, sys, glob, shutil, subprocess, datetime as dt
GN_ROOT = os.environ.get('GN_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
os.chdir(GN_ROOT)
IST = dt.timezone(dt.timedelta(hours=5, minutes=30)); now = dt.datetime.now(IST)
H = 'newsroom/held'
def mv(a, b):
    os.makedirs(os.path.dirname(b), exist_ok=True)
    tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', a], capture_output=True).returncode == 0
    subprocess.run(['git', 'mv', '-f', a, b], check=True) if tracked else shutil.move(a, b)
def info(i):
    try: return json.load(open(f'{H}/{i}.json'))
    except OSError: return {'why': '?', 'kind': 'other', 'held_at': dt.datetime.fromtimestamp(os.path.getmtime(f'{H}/en/{i}.md'), IST).isoformat()}
cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
if cmd == 'list':
    ids = sorted(os.path.basename(f)[:-3] for f in glob.glob(f'{H}/en/*.md'))
    for i in ids:
        d = info(i); age = (now - dt.datetime.fromisoformat(d['held_at'])).total_seconds() / 3600
        pic = json.load(open('content/photos.map.json')).get(i)
        print(f"{i} | {d['kind']} | {age:.1f}h | {d['why']}" + (' | picture now exists: republish' if d['kind'] == 'picture' and pic else ''))
    print(f'{len(ids)} held')
elif cmd == 'hold':
    i, kind, why = sys.argv[2], sys.argv[3], sys.argv[4]
    assert kind in ('picture', 'facts', 'other')
    n = 0
    for lang in ('en', 'hi'):
        for f in glob.glob(f'content/{lang}/*/{i}.md'):
            mv(f, f'{H}/{lang}/{i}.md'); n += 1
            open(f'{H}/{i}.type', 'w').write(f.split('/')[2])
    json.dump({'why': why, 'kind': kind, 'held_at': now.isoformat(timespec='minutes')}, open(f'{H}/{i}.json', 'w'), ensure_ascii=False)
    print(f'held {i} ({n} files): {why}')
elif cmd == 'republish':
    i = sys.argv[2]; d = info(i)
    if d['kind'] == 'picture' and i not in json.load(open('content/photos.map.json')): sys.exit(f'{i}: still no main picture')
    if d['kind'] != 'picture' and '--fixed' not in sys.argv: sys.exit(f'{i}: held for {d["kind"]} ({d["why"]}); republish only with --fixed after fixing it and a new editor PASS')
    typ = open(f'{H}/{i}.type').read().strip() if os.path.exists(f'{H}/{i}.type') else 'news'
    for lang in ('en', 'hi'): mv(f'{H}/{lang}/{i}.md', f'content/{lang}/{typ}/{i}.md')
    for x in ('json', 'type'):
        p = f'{H}/{i}.{x}'
        if os.path.exists(p): subprocess.run(['git', 'rm', '-q', '-f', p], capture_output=True); os.path.exists(p) and os.remove(p)
    print(f'republished {i}: set its published time to now if the news is still current')
elif cmd == 'expire':
    for f in glob.glob(f'{H}/en/*.md'):
        i = os.path.basename(f)[:-3]; d = info(i)
        if (now - dt.datetime.fromisoformat(d['held_at'])).total_seconds() > 12 * 3600:
            for p in [f'{H}/en/{i}.md', f'{H}/hi/{i}.md', f'{H}/{i}.json', f'{H}/{i}.type']:
                if os.path.exists(p): subprocess.run(['git', 'rm', '-q', '-f', p], capture_output=True); os.path.exists(p) and os.remove(p)
            print(f'expired {i}')
else: sys.exit(__doc__)
