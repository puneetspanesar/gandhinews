"""Refresh content/homepage.json from the newest published stories. Run EVERY hourly run, even with zero new stories.

Usage (repo root):
  python3 newsroom/scripts/refresh_home.py                 keep the current lead (warns if it is over 12 hours old)
  python3 newsroom/scripts/refresh_home.py --lead <id>     make <id> the lead (overlay from its hero, data box cleared)
  python3 newsroom/scripts/refresh_home.py --pin <id> ...  put these ids first in the headlines (BIG STORIES)

What it does, mechanically, with the owner's balance rules:
  headlines (beside the lead, top stories, briefing): pictured news from the last 24 hours, newest first,
    at most ONE markets story, at most TWO per section in the top eight, no two stories on the same subject.
  live band: keeps items under 24 hours old, tops up with the newest same-topic stories.
  section and desk lists: newest pictured news of that section.  startHere: newest explainers.  opinion: newest editorials.
Then run check_fresh.py and the build as usual.
"""
import json, glob, re, sys, argparse, datetime as dt
import yaml

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
now = dt.datetime.now(IST)
ap = argparse.ArgumentParser(); ap.add_argument('--lead'); ap.add_argument('--pin', nargs='*', default=[])
a = ap.parse_args()

PIC = json.load(open('content/photos.map.json'))
A = {}
for lang in ('en', 'hi'):
    for f in glob.glob(f'content/{lang}/*/*.md'):
        d = yaml.safe_load(open(f).read().split('---')[1]) or {}
        t = d.get('published')
        if not d.get('id') or not isinstance(t, dt.datetime): continue
        if lang == 'en':
            d['_t'] = t if t.tzinfo else t.replace(tzinfo=IST); A[d['id']] = d
        else:
            A.setdefault('_hi', {})[d['id']] = d
HI = A.pop('_hi', {})
ok = lambda i: i in A and i in PIC and i in HI
age = lambda i: (now - A[i]['_t']).total_seconds() / 3600
newest = lambda pred: sorted([i for i in A if ok(i) and pred(A[i])], key=lambda i: A[i]['_t'], reverse=True)
MKT = re.compile(r'(sensex|nifty|wall-street|dow-|nasdaq|ftse|kospi|nikkei|^oil-|^brent|markets?-|-shares-|stocks?-|-sales-\d)')
STOP = {'supreme', 'minister', 'government', 'november', 'october', 'december', 'police', 'india', 'indian', 'explained', 'crore', 'says'}
words = lambda i: {w for w in i.split('-') if len(w) >= 6 and w not in STOP}

h = json.load(open('content/homepage.json'))
L = h['lead']

# ---- lead
if a.lead:
    assert ok(a.lead), f'{a.lead}: not published, or no picture, or no Hindi twin'
    if a.lead != L['id']:
        L['id'] = a.lead
        ov = lambda d: ((d.get('hero') or {}).get('overlay') or {}).get('value', '')
        L['overlay'] = {'kicker': {'en': A[a.lead].get('format_label', ''), 'hi': HI[a.lead].get('format_label', '')},
                        'value': {'en': ov(A[a.lead]), 'hi': ov(HI[a.lead])}, 'text': {'en': '', 'hi': ''}}
        L['dataBox'] = []
        L['relatedBelow'] = []
lead = L['id']
if A[lead]['type'] == 'news' and age(lead) > 12:
    print(f'WARNING: the lead is {age(lead):.0f} hours old. Pick a newer lead with --lead <id> unless it still leads other front pages.')

# ---- live band: still-fresh items, topped up with the newest stories sharing a topic or subject words with the lead
lt, lw = set(A[lead].get('topics') or []), words(lead)
rel = [i for i in (L.get('relatedBelow') or []) if ok(i) and not MKT.search(i) and (A[i]['type'] != 'news' or age(i) <= 24)]
for i in newest(lambda d: d['id'] != lead and (d['type'] != 'news' or (now - d['_t']).total_seconds() < 86400)):
    if len(rel) >= 3: break
    if i in rel or MKT.search(i): continue
    if len(lw & words(i)) >= 2 or (lt & set(A[i].get('topics') or []) and A[i]['section'] == A[lead]['section']): rel.append(i)
L['relatedBelow'] = rel[:3]

# ---- headlines
pool = [i for i in a.pin if ok(i)] + newest(lambda d: d['type'] == 'news' and (now - d['_t']).total_seconds() < 86400)
taken, secs, mk, used_words = [], {}, 0, set(words(lead))
for i in pool:
    if i == lead or i in taken or i in rel: continue
    if MKT.search(i) and mk >= 1: continue
    s = A[i]['section']
    if len(taken) < 8 and secs.get(s, 0) >= 2: continue
    if len(words(i) & used_words) >= 2: continue
    taken.append(i); secs[s] = secs.get(s, 0) + 1; used_words |= words(i); mk += bool(MKT.search(i))
    if len(taken) >= 16: break
nb = len(L.get('relatedBeside') or []) or 4
L['relatedBeside'] = taken[:nb]
rest = taken[nb:]
h['topStories'] = {'big': {'id': rest[0], 'also': []}, 'list': rest[1:6], 'also': rest[6:8]} if rest else h['topStories']

def short(lbl): return (lbl.split('/')[-1].strip() or lbl) + ':'
h['briefing']['items'] = [{'link': i, 'lead': {'en': short(A[i].get('format_label', A[i]['section'])), 'hi': short(HI[i].get('format_label', ''))},
                           'text': {'en': A[i]['title'], 'hi': HI[i]['title']}} for i in taken[:8]]

# ---- section and desk lists
for s in h.get('sections', []) + h.get('desks', []):
    ids = newest(lambda d, sec=s['section']: d['type'] == 'news' and d.get('section') == sec)
    if not ids: continue
    n = max(len(s.get('list') or []), 3)
    if 'lead' in s: s['lead'], s['list'] = ids[0], ids[1:1 + n]
    else: s['list'] = ids[:n]

# ---- long form
for key, typ in (('startHere', 'explainer'), ('opinion', 'editorial')):
    n = len(h.get(key) or []) or 4
    fresh = newest(lambda d, t=typ: d['type'] == t)
    if fresh: h[key] = fresh[:n]

json.dump(h, open('content/homepage.json', 'w'), ensure_ascii=False, indent=1)
open('content/homepage.json', 'a').write('\n')
print('lead:', lead, f'({age(lead):.0f}h)')
print('live band:', rel[:3])
for n, i in enumerate(taken[:8], 1): print(f'  {n}. [{A[i]["section"]}] {age(i):.0f}h {i}')
