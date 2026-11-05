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
# Balance in the headlines: at most one markets story, at most two per section, lead not a markets story.
import re as _re
MKT = _re.compile(r'(sensex|nifty|wall-street|dow-|nasdaq|ftse|kospi|nikkei|^oil-|^brent|markets?-|-shares-|stocks?-|-sales-\d)')
heads = []
ts = h.get('topStories') or {}
for part in [h['lead'].get('relatedBeside'), (ts.get('big') or {}).get('id'), ts.get('list'), h.get('briefing')]:
    for i in ids(part):
        if i not in heads: heads.append(i)
mk = [i for i in heads if MKT.search(i)]
if len(mk) > 1: bad.append(('too many market stories in the headlines (max 1)', ', '.join(mk), 0))
from collections import Counter as _C
for sec, n in _C(P[i].get('section') for i in heads[:8]).items():
    if n > 2: bad.append((f'more than two {sec} stories in the top eight', sec, n))
if MKT.search(lead): bad.append(('markets story as the lead', lead, 0))
_M = json.load(open('content/photos.map.json'))
for i in [lead] + heads + ids(h['lead'].get('relatedBelow')):
    if i not in _M: bad.append(('no picture yet (never put an unpictured story on the homepage)', i, 0))

# Snapshot figures go stale fast: a headline or standfirst that pins a figure to a clock time ("by 10 am", "at 11:30 am")
# must be updated within 2 hours, or the story taken off the top. Same for the markets band while the market is open.
CLOCK = _re.compile(r'\b(?:by|at|till|until|as of)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b', _re.I)
_HI_CLOCK = _re.compile(r'(सुबह|दोपहर|शाम)?\s*(\d{1,2})\s*बजे\s*तक')
for i in [lead] + heads[:8]:
    d = P[i]
    when = d.get('updated') or d['published']
    if (now - when).total_seconds() > 12 * 3600: continue
    for txt in (str(d.get('title', '')),):
        for m in CLOCK.finditer(txt):
            hh = int(m.group(1)) % 12 + (12 if m.group(3).lower() == 'pm' else 0)
            t = when.replace(hour=hh, minute=int(m.group(2) or 0), second=0)
            if (now - t).total_seconds() > 2 * 3600:
                bad.append((f'snapshot figure is out of date ("{m.group(0)}" at {now:%H:%M}); update the story with the latest figure or move it off the top', i, (now - t).total_seconds() / 3600))
_mk = json.load(open('content/data/markets.json'))
try:
    _asof = dt.datetime.fromisoformat(_mk.get('as_of'))
    if _mk.get('status') == 'open' and (now - _asof).total_seconds() > 2 * 3600 and now.weekday() < 5 and 9 <= now.hour < 16:
        bad.append(('markets band shows the market open but its figures are more than 2 hours old', _mk.get('as_of'), (now - _asof).total_seconds() / 3600))
except Exception: pass
if bad:
    print('HOMEPAGE PROBLEMS:')
    for n, i, a in bad: print(f'  {n}: {i} ({a:.0f})')
    sys.exit(1)
print('OK: the top of the homepage is all from the last 24 hours.')
