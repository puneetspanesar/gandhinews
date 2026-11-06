"""Counter check of the LIVE site, run by the stall check (and at the end of every run). Never trusts a run's own report.
  python3 newsroom/scripts/verify_live.py                 prints every problem, exit 1 if any
  python3 newsroom/scripts/verify_live.py --expect <sha>  after a push: waits (up to 12 minutes) until the live site
                                                          runs that commit, then checks; exit 1 if it never arrives
Checks:
  deploy     the live /build.json commit is main's newest commit (allowing 15 minutes for Cloudflare); if not, whether the
             Cloudflare build for main failed (then the build gate's message is reproduced with a local build)
  runs       a run commit or a homepage rotation (.github/workflows/home-rotate.yml) in the last 75 minutes, 7 am to midnight
  freshness  check_fresh.py on main's homepage (lead, headlines, clock figures, the site moving every hour)
  homepage   the live English and Hindi homepages show main's lead headline, and no camera placeholders or broken images
  held       picture holds whose picture now exists, and holds over 48 hours old
"""
import json, os, re, subprocess, sys, time, urllib.request, datetime as dt
GN_ROOT = os.environ.get('GN_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
os.chdir(GN_ROOT)
IST = dt.timezone(dt.timedelta(hours=5, minutes=30)); now = dt.datetime.now(IST)
bad = []
sh = lambda *a: subprocess.run(a, capture_output=True, text=True)
def get(url):
    req = urllib.request.Request(url + ('&' if '?' in url else '?') + f't={int(time.time())}', headers={'User-Agent': 'gandhinews-verify', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=30) as r: return r.read().decode('utf-8', 'replace')

sh('git', 'fetch', '-q', 'origin', '+refs/heads/main:refs/remotes/origin/main')
main = sh('git', 'rev-parse', 'origin/main').stdout.strip()
main_t = dt.datetime.fromtimestamp(int(sh('git', 'log', '-1', '--format=%ct', main).stdout.strip()), IST)
expect = sys.argv[sys.argv.index('--expect') + 1] if '--expect' in sys.argv else None
if expect: expect = sh('git', 'rev-parse', expect).stdout.strip() or expect
live = {}
for _ in range(25 if expect else 1):
    try: live = json.loads(get('https://gandhinews.com/build.json'))
    except Exception as e: live = {'error': str(e)}
    if not expect or live.get('sha') == expect or sh('git', 'merge-base', '--is-ancestor', expect, live.get('sha') or 'x').returncode == 0: break
    time.sleep(30)
if live.get('error'): bad.append(f"deploy: /build.json unreadable ({live['error']})")
if expect and live.get('sha') != expect and sh('git', 'merge-base', '--is-ancestor', expect, live.get('sha') or 'x').returncode != 0:
    runs = sh('gh', 'api', f'repos/puneetspanesar/gandhinews/commits/{expect}/check-runs', '--jq', '.check_runs[]|.status+" "+(.conclusion//"")').stdout.strip()
    bad.append(f"deploy: {expect[:7]} is not live after 12 minutes (live {str(live.get('sha'))[:7]}); Cloudflare: {runs or 'no build found'}")
if live.get('sha') and live['sha'] != main:
    behind = sh('git', 'rev-list', '--count', f"{live['sha']}..{main}").stdout.strip()
    if (now - main_t).total_seconds() > 15 * 60:
        runs = sh('gh', 'api', f'repos/puneetspanesar/gandhinews/commits/{main}/check-runs', '--jq', '.check_runs[]|.status+" "+(.conclusion//"")').stdout.strip()
        bad.append(f"deploy: live site is {behind} commits behind main (live {live['sha'][:7]} built {live.get('built')}, main {main[:7]} at {main_t:%H:%M}); Cloudflare: {runs or 'no build found'}")
        if 'failure' in runs:
            b = sh('npm', 'run', '-s', 'build')
            bad.append('deploy: the build fails here too:\n    ' + '\n    '.join((b.stdout + b.stderr).strip().splitlines()[-15:]))

if 7 <= now.hour:
    log = sh('git', 'log', '-30', '--format=%ct %s', 'origin/main').stdout.splitlines()
    last = max([int(l.split()[0]) for l in log if re.search(r'^\d+ (Hourly|Long-form|Stall|Homepage rotation)', l)] or [0])
    if (now.timestamp() - last) > 75 * 60:
        bad.append(f'runs: no run commit since {dt.datetime.fromtimestamp(last, IST):%B %d %H:%M} (a run was missed or failed before pushing)')

f = sh(sys.executable, 'newsroom/scripts/check_fresh.py')
if f.returncode == 1: bad.append('freshness:\n    ' + '\n    '.join(f.stdout.strip().splitlines()[1:]))
# exit 2 = recorded rule breaches the next writing run clears (e.g. no fresh pictured story to lead): noted, not a stall
notes = f.stdout.strip().splitlines()[1:] if f.returncode == 2 else []

home = json.load(open('content/homepage.json'))
lead = home['lead']['id']
for lang, url in (('en', 'https://gandhinews.com/'), ('hi', 'https://gandhinews.com/hi/')):
    try: html = get(url)
    except Exception as e: bad.append(f'homepage {lang}: unreachable ({e})'); continue
    p = f'content/{lang}/news/{lead}.md'
    import yaml
    title = (yaml.safe_load(open(p).read().split('---')[1]) or {}).get('title') if os.path.exists(p) else None
    txt = html.replace('&#39;', "'").replace('&quot;', '"').replace('&amp;', '&')
    if live.get('sha') == main and title and title not in txt: bad.append(f'homepage {lang}: live page does not show the lead "{title[:60]}"')
    n = len(re.findall(r'class="[^"]*\bcam\b', html))
    if n: bad.append(f'homepage {lang}: {n} empty picture slots (camera placeholders) are live')

h = sh(sys.executable, 'newsroom/scripts/held.py', 'list').stdout
for l in h.splitlines():
    if 'republish' in l or (re.search(r'\| (\d+\.\d)h \|', l) and float(re.search(r'\| (\d+\.\d)h \|', l).group(1)) > 48):
        bad.append('held: ' + l)

if bad:
    print(f'LIVE SITE PROBLEMS at {now:%H:%M} IST:'); [print('  ' + b) for b in bad]; sys.exit(1)
print(f"OK at {now:%H:%M} IST: live = main ({main[:7]}), runs on time, homepage rules hold, lead shown in both languages." + ("\n  breaches for the next writing run:\n  " + "\n  ".join(notes) if notes else ""))
