"""Refresh content/homepage.json from the newest published stories. Run EVERY hourly run, even with zero new stories.

Usage (repo root):
  python3 newsroom/scripts/refresh_home.py                 keep the current lead; if it is held, over 8 hours old or a markets story,
                                                           the newest fresh non-markets news story with a real photo takes over
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
import yaml, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gnrules import MKT, words, stale_clock, is_markets, same_subject

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
now = dt.datetime.now(IST)
ap = argparse.ArgumentParser(); ap.add_argument('--lead'); ap.add_argument('--pin', nargs='*', default=[])
a = ap.parse_args()
import os as _o
if sys.argv[1:]: open((_o.environ.get('GN_WORK') or '/home/claude/gn-work/') + 'home_args', 'w').write(' '.join(sys.argv[1:]))  # publish.sh re-applies these after a merge

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
def clocked(i):
    for lang, d in (('en', A.get(i)), ('hi', HI.get(i))):
        if not d: continue
        when = d.get('updated') or d.get('published')
        if not isinstance(when, dt.datetime): continue
        when = when if when.tzinfo else when.replace(tzinfo=IST)
        txts = [str(d.get('title') or ''), str(d.get('standfirst') or ''), str((d.get('keyPoints') or [''])[0]), str(((d.get('hero') or {}).get('overlay') or {}).get('value') or '')]
        if any(stale_clock(t, lang, when, now) for t in txts): return True
    return False
age = lambda i: (now - A[i]['_t']).total_seconds() / 3600
newest = lambda pred: sorted([i for i in A if ok(i) and pred(A[i])], key=lambda i: A[i]['_t'], reverse=True)

h = json.load(open('content/homepage.json'))
L = h['lead']
_pending_lead = False

# ---- lead
if a.lead:
    assert ok(a.lead), f'{a.lead}: not published, or no picture, or no Hindi twin'
    if a.lead != L['id']:
        assert not is_markets(a.lead, A.get(a.lead)), f'{a.lead}: a markets story never leads'
        L['id'] = a.lead; L['dataBox'] = []; L['relatedBelow'] = []
        _pending_lead = True
def set_lead(i):
    ov = lambda d: ((d.get('hero') or {}).get('overlay') or {}).get('value', '')
    L['id'] = i
    L['overlay'] = {'kicker': {'en': A[i].get('format_label', ''), 'hi': HI[i].get('format_label', '')},
                    'value': {'en': ov(A[i]), 'hi': ov(HI[i])}, 'text': {'en': '', 'hi': ''}}
    L['dataBox'] = []; L['relatedBelow'] = []
if _pending_lead: set_lead(a.lead)
lead = L['id']
fresh_photo = lambda d: d['type'] == 'news' and (now - d['_t']).total_seconds() < 8 * 3600 and not is_markets(d['id'], d) and not PIC[d['id']].get('graphic') and not clocked(d['id'])
bad = (not ok(lead)) and 'held or unpublished' or (is_markets(lead, A.get(lead)) and 'a markets story') or (clocked(lead) and 'pinned to a stale clock figure') or (A[lead]['type'] == 'news' and age(lead) > 8 and f'{age(lead):.0f} hours old')
if not bad and not a.lead and PIC.get(lead, {}).get('graphic'):
    # Rule 13: the lead has a real photo. Swap to the newest fresh story of the SAME running story that has one.
    same = [i for i in newest(fresh_photo) if i != lead and (len(words(i) & words(lead)) >= 2 or (set(A[i].get('topics') or []) & set(A[lead].get('topics') or []) and A[i]['section'] == A[lead]['section']))]
    if same: print(f'lead {lead} is an infographic; {same[0]} (same story, real photo) leads instead'); set_lead(same[0]); lead = same[0]
if bad and not a.lead:
    # Owner's rule: the lead is under 8 hours old and never a markets story. Pick the replacement mechanically.
    cand = newest(fresh_photo)
    if cand:
        print(f'lead {lead} replaced ({bad}) by {cand[0]}'); set_lead(cand[0]); lead = cand[0]
    else:
        print(f'WARNING: the lead {lead} is {bad} and no fresh non-markets story with a real photo exists; publish one and re-run.')
        if not ok(lead): sys.exit(3)

# ---- live band: still-fresh items, topped up with the newest stories sharing a topic or subject words with the lead
lt, lw = set(A[lead].get('topics') or []), words(lead)
rel = [i for i in (L.get('relatedBelow') or []) if ok(i) and not is_markets(i, A.get(i)) and not clocked(i) and (A[i]['type'] != 'news' or age(i) <= 24)]
for i in newest(lambda d: d['id'] != lead and (d['type'] != 'news' or (now - d['_t']).total_seconds() < 86400)):
    if len(rel) >= 3: break
    if i in rel or is_markets(i, A.get(i)) or clocked(i): continue
    if len(lw & words(i)) >= 2 or (lt & set(A[i].get('topics') or []) and A[i]['section'] == A[lead]['section']): rel.append(i)
L['relatedBelow'] = rel[:3]

# ---- headlines
pool = [i for i in a.pin if ok(i) and age(i) < 24] + newest(lambda d: d['type'] == 'news' and (now - d['_t']).total_seconds() < 86400)
taken, secs, mk, used_words = [], {}, 0, set(words(lead))
for i in pool:
    if i == lead or i in taken or i in rel or clocked(i): continue
    if is_markets(i, A.get(i)) and mk >= 1: continue
    s = A[i]['section']
    if len(taken) < 8 and secs.get(s, 0) >= 2: continue
    if len(words(i) & used_words) >= 2 or (taken and same_subject(i, taken[-1], A.get(i), A.get(taken[-1]))) or (not taken and same_subject(i, lead, A.get(i), A.get(lead))): continue
    taken.append(i); secs[s] = secs.get(s, 0) + 1; used_words |= words(i); mk += bool(is_markets(i, A.get(i)))
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
    ids = newest(lambda d, sec=s['section']: d['type'] == 'news' and d.get('section') == sec and not clocked(d['id']))  # rule 6: a stale clock figure never sits in a section list
    if not ids: continue
    n = max(len(s.get('list') or []), 3)
    if 'lead' in s: s['lead'], s['list'] = ids[0], ids[1:1 + n]
    else: s['list'] = ids[:n]

# ---- long form
for key, typ in (('startHere', 'explainer'), ('opinion', 'editorial')):
    n = len(h.get(key) or []) or 4
    fresh = newest(lambda d, t=typ: d['type'] == t)
    if fresh: h[key] = fresh[:n]

json.dump(h, open('content/homepage.json', 'w'), ensure_ascii=False, indent=2)
open('content/homepage.json', 'a').write('\n')
print('lead:', lead, f'({age(lead):.0f}h)')
print('live band:', rel[:3])
for n, i in enumerate(taken[:8], 1): print(f'  {n}. [{A[i]["section"]}] {age(i):.0f}h {i}')
