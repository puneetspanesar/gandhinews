#!/usr/bin/env python3
"""Daily health report (owner, November 12): one screen of numbers on how the site ran in the last 24 hours, so a
slide in quality shows up the same day and not when the owner notices it.

  python3 newsroom/scripts/health_report.py        prints the report; exit 0 all within limits | 1 something over a limit

Every line is a count taken from the repo, the run records, GitHub and the live site: nothing is estimated.
Limits: 30 new stories a day; at most 1 in 4 on an infographic; no plain (untreated) photo; every hour from 7 am to
11 pm with a homepage change; no writing run with fewer than 3 stories; no open hold older than a day; live check clean."""
import datetime as dt, glob, json, os, re, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
os.chdir(R)
IST = dt.timezone(dt.timedelta(hours=5, minutes=30)); now = dt.datetime.now(IST); since = now - dt.timedelta(hours=24)
sh = lambda *a: subprocess.run(a, capture_output=True, text=True)
sh('git', 'fetch', '-q', 'origin', '+refs/heads/main:refs/remotes/origin/main')
ok, bad = [], []
def line(good, text): (ok if good else bad).append(text)

# stories published in the last 24 hours
M = json.load(open('content/photos.map.json')); new = []
for f in glob.glob('content/en/*/*.md'):
    m = re.search(r'^published:\s*["\']?([^"\'\n]+)', open(f).read(3000), re.M)
    try: t = dt.datetime.fromisoformat(m.group(1).strip())
    except Exception: continue
    if t.tzinfo and t >= since and '/tracker/' not in f: new.append((os.path.basename(f)[:-3], f.split('/')[2]))
kinds = {}
for _, k in new: kinds[k] = kinds.get(k, 0) + 1
line(len(new) >= 30, f"{len(new)} new stories in 24 hours (limit: at least 30): " + ', '.join(f'{v} {k}' for k, v in sorted(kinds.items())))
news = [i for i, k in new if k == 'news']
graphic = [i for i in news if (M.get(i) or {}).get('graphic')]
line(len(graphic) * 4 <= max(len(news), 1), f"{len(graphic)} of {len(news)} news stories went up on an infographic (limit: 1 in 4)" + (': ' + ', '.join(graphic[:6]) if graphic else ''))
plain = [i for i, _ in new if M.get(i) and not M[i].get('graphic') and not M[i].get('treated')]
line(not plain, f"{len(plain)} new stories show a plain photo without the collage" + (': ' + ', '.join(plain[:6]) if plain else ''))
nopic = [i for i, _ in new if i not in M]
line(not nopic, f"{len(nopic)} new stories have no picture" + (': ' + ', '.join(nopic[:6]) if nopic else ''))

# the runs, from their own records
recs = []
for f in sorted(glob.glob('newsroom/runs/*.json'))[-80:]:
    try: d = json.load(open(f)); t = dt.datetime.fromisoformat(d.get('end') or d.get('start'))
    except Exception: continue
    if t >= since: recs.append(d)
wr = [d for d in recs if str(d.get('run', '')).startswith('hourly')]
# a lead run (odd hours) writes 1 story; a full run (even hours and midnight) at least 3
need = lambda d: 1 if (str(d.get('run', ''))[-2:].isdigit() and int(str(d['run'])[-2:]) % 2 == 1) else 3
PUBT = {}
for f in glob.glob('content/en/*/*.md'):
    m = re.search(r'^published:\s*["\']?([^"\'\n]+)', open(f).read(3000), re.M)
    try: PUBT[os.path.basename(f)[:-3]] = dt.datetime.fromisoformat(m.group(1).strip())
    except Exception: pass
def nn(d):
    """New stories a run added: stories published between its start and its end (a second publish rewrites the record's list)."""
    try: a, b = dt.datetime.fromisoformat(d['start']), dt.datetime.fromisoformat(d['end'])
    except Exception: return 0
    return sum(1 for t in PUBT.values() if t.tzinfo and a - dt.timedelta(minutes=10) <= t <= b)
thin = [f"{d['run']} ({nn(d)})" for d in wr if nn(d) < need(d)]
sched = [h for h in range(24) if h == 0 or 6 <= h <= 23]
done = {str(d.get('run', ''))[-2:] for d in wr}
HOURLY_FROM = dt.datetime(2026, 11, 12, 20, 0, tzinfo=IST)   # odd-hour lead runs began at 9 pm on November 12
due = []
for h in sched:
    t = now.replace(hour=h, minute=50, second=0, microsecond=0)
    if t > now: t -= dt.timedelta(days=1)
    if t > since and (h % 2 == 0 or t >= HOURLY_FROM): due.append(f'{h:02d}')
silent = [h + ':03' for h in due if h not in done]
line(not silent, f"{len(due) - len(silent)} of {len(due)} writing runs published" + (' (nothing from ' + ', '.join(silent) + ')' if silent else ''))
lf = [d for d in recs if str(d.get('run', '')).startswith('longform')]
line(len(lf) >= 2, f"{len(lf)} of 2 long-form runs published")
line(not thin, f"{len(thin)} writing runs published fewer stories than they should (full runs 3, lead runs 1)" + (': ' + ', '.join(thin) if thin else ''))
held = sum(len(d.get('held') or []) for d in recs); efail = sum(1 for d in recs if d.get('editor') == 'FAIL' or d.get('editor_fail'))
line(efail * 3 <= max(len([d for d in recs if d.get('editor')]), 1), f"the editor's first check failed in {efail} of {len([d for d in recs if d.get('editor')])} runs; {held} stories held")
stall = [d for d in recs if str(d.get('run', '')).startswith('stall')]
line(len(stall) <= 3, f"the stall check had to step in {len(stall)} times (limit 3)")

# the homepage changed every hour, 7 am to 11 pm
log = sh('git', 'log', '--since=24 hours ago', '--format=%ct', 'origin/main', '--', 'content/homepage.json').stdout.split()
hours = {dt.datetime.fromtimestamp(int(t), IST).strftime('%d %H') for t in log}
want = []; t = since.replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=1)
while t < now.replace(minute=0, second=0, microsecond=0):
    if 7 <= t.hour <= 23: want.append(t.strftime('%d %H'))
    t += dt.timedelta(hours=1)
miss = [h.split()[1] + ':00' for h in want if h not in hours]
line(len(miss) <= 1, f"the homepage changed in {len(want) - len(miss)} of {len(want)} hours between 7 am and 11 pm" + (' (no change at ' + ', '.join(miss) + ')' if miss else ''))
g = sh('gh', 'run', 'list', '--workflow', 'home-rotate.yml', '-L', '100', '--json', 'createdAt,conclusion,event')
try:
    runs = [r for r in json.loads(g.stdout) if dt.datetime.fromisoformat(r['createdAt'].replace('Z', '+00:00')) >= since]
    f = sum(1 for r in runs if r['conclusion'] == 'failure')
    line(f <= 1, f"GitHub ran the rotation job {len(runs)} times, {f} failed")
except Exception: ok.append('GitHub rotation job: could not be read from here')

# holds and the live site
H = [json.load(open(f)) for f in glob.glob('newsroom/held/*.json')]
old = [h for h in H if (now - dt.datetime.fromisoformat(h['held_at']).astimezone(IST)).total_seconds() > 24 * 3600 and h.get('kind') != 'picture']
line(not old, f"{len(H)} stories on hold, {len(old)} of them older than a day")
v = sh(sys.executable, 'newsroom/scripts/verify_live.py')
line(v.returncode == 0, 'live site check: ' + ('clean' if v.returncode == 0 else ' | '.join(l.strip() for l in v.stdout.strip().splitlines()[:6])))

print(f"Gandhi News health, {now:%B} {now.day}, {now.year}, {now:%-I:%M %p} IST")
if bad:
    print('NEEDS ATTENTION'); [print('  ' + x) for x in bad]
print('WITHIN LIMITS' if ok else ''); [print('  ' + x) for x in ok]
sys.exit(1 if bad else 0)
