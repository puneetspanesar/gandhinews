"""Fails if the top of the homepage carries stale news.
Lead: published in the last 18 hours. Live band (lead.relatedBelow), lead.relatedBeside, briefing and topStories:
news published in the last 24 hours. Explainers, editorials and other long forms are not checked here.
Usage: python3 newsroom/scripts/check_fresh.py   (run from the repo root)"""
import json, glob, yaml, sys, datetime as dt
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
now = dt.datetime.now(IST)
P = {}
for f in glob.glob('content/en/*/*.md'):
    d = yaml.safe_load(open(f).read().split('---')[1]) or {}
    if d.get('published'): P[d['id']] = d
h = json.load(open('content/homepage.json'))
def ids(x):
    if isinstance(x, str): return [x] if x in P else []
    if isinstance(x, list): return [i for y in x for i in ids(y)]
    if isinstance(x, dict): return [i for v in x.values() for i in ids(v)]
    return []
age = lambda i: (now - P[i]['published']).total_seconds() / 3600
bad = []
lead = h['lead']['id']
if P[lead]['type'] == 'news' and age(lead) > 18: bad.append(('lead', lead, age(lead)))
for name, part in [('live band', h['lead'].get('relatedBelow')), ('beside lead', h['lead'].get('relatedBeside')),
                   ('briefing', h.get('briefing')), ('top stories', h.get('topStories'))]:
    for i in ids(part):
        if P[i]['type'] == 'news' and age(i) > 24: bad.append((name, i, age(i)))
if bad:
    print('STALE on the homepage (hours old):')
    for n, i, a in bad: print(f'  {n}: {i} ({a:.0f} h)')
    sys.exit(1)
print('OK: the top of the homepage is all from the last 24 hours.')
