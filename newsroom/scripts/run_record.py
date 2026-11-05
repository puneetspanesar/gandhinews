"""Run record: newsroom/runs/<YYYY-MM-DD>-<run>.json, the run's own account, which the stall check and the daily audit
compare with what actually reached the live site.
  python3 newsroom/scripts/run_record.py write <run-name> "<summary>"
  python3 newsroom/scripts/run_record.py last          the newest record
"""
import json, os, sys, glob, subprocess, datetime as dt
GN_ROOT = os.environ.get('GN_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
W = os.environ.get('GN_WORK') or '/home/claude/gn-work/'
os.chdir(GN_ROOT)
IST = dt.timezone(dt.timedelta(hours=5, minutes=30)); now = dt.datetime.now(IST)
os.makedirs('newsroom/runs', exist_ok=True)
if sys.argv[1] == 'last':
    f = sorted(glob.glob('newsroom/runs/*.json'), key=os.path.getmtime)
    print(open(f[-1]).read() if f else 'no run records'); sys.exit()
run, summary = sys.argv[2], sys.argv[3]
diff = subprocess.run(['git', 'diff', '--name-status', 'origin/main', '--', 'content/en', 'newsroom/held/en'], capture_output=True, text=True).stdout.split('\n')
added = [l.split('\t')[-1].split('/')[-1][:-3] for l in diff if l.startswith('A') and l.endswith('.md') and 'content/en' in l.split('\t')[-1]]
held = [l.split('\t')[-1].split('/')[-1][:-3] for l in diff if l.split('\t')[-1].startswith('newsroom/held/en')]
try: start = json.load(open(W + 'run.json'))['start']
except Exception: start = None
try: ed = json.load(open(W + 'editor.json'))
except Exception: ed = None
rec = {'run': run, 'start': start, 'end': now.isoformat(timespec='seconds'), 'summary': summary, 'new': added, 'held': held,
       'editor': ed and ed.get('verdict'), 'editor_fail': ed and ed.get('fail'), 'lead': json.load(open('content/homepage.json'))['lead']['id']}
p = f'newsroom/runs/{now:%Y-%m-%d}-{run}.json'
json.dump(rec, open(p, 'w'), ensure_ascii=False, indent=1)
for old in glob.glob('newsroom/runs/*.json'):
    if (now.date() - dt.date.fromisoformat(os.path.basename(old)[:10])).days > 14: os.remove(old)
print(p, json.dumps(rec, ensure_ascii=False)[:300])
if not ed: print('WARNING: no editor.json: the editor check did not run')
