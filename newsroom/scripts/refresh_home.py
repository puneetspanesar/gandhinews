"""Refresh content/homepage.json from the newest published stories. Run EVERY hourly run, even with zero new stories.

Usage (repo root):
  python3 newsroom/scripts/refresh_home.py                 keep the current lead; if it is held, over 8 hours old or a markets story,
                                                           the newest fresh non-markets news story with a real photo takes over
  python3 newsroom/scripts/refresh_home.py --lead <id>     make <id> the lead (overlay from its hero, data box cleared)
  python3 newsroom/scripts/refresh_home.py --pin <id> ...  put these ids first in the headlines (BIG STORIES)
  python3 newsroom/scripts/refresh_home.py --drop <id> ...  keep these ids out of the lead, live band and headlines this hour
                                                           (a story overtaken by events, e.g. a morning preview of a poll that has ended)
  python3 newsroom/scripts/refresh_home.py --critical <id> ...  a nation- or world-changing story that may stay in the
                                                           headlines another hour, ONLY if it was updated (`updated:`) since
                                                           the last hour's homepage; otherwise write the development as a new story

THE OWNER'S FIRST HOMEPAGE RULE: every headline changes every hour. The lead and every story in the headlines (beside the
lead, top stories, briefing, live band) must be different from the homepage of the previous hour (the newest one at
least 40 minutes old, kept in homepage.json headlineHistory and checked independently by check_fresh.py from git).
A new story on the same running subject (a development, with its own id) is a new headline and is fine.

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
from gnrules import MKT, words, stale_clock, is_markets, same_subject, headline_ids, prev_hour_homepage, recent_homepages, core_ids

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
now = dt.datetime.now(IST)
ap = argparse.ArgumentParser(); ap.add_argument('--lead'); ap.add_argument('--pin', nargs='*', default=[]); ap.add_argument('--critical', nargs='*', default=[]); ap.add_argument('--drop', nargs='*', default=[])
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

# ---- the previous hour's headlines: nothing in them may appear in this hour's headlines (critical + updated excepted)
hist = h.setdefault('headlineHistory', [])
_at = lambda e: dt.datetime.fromisoformat(e['at'])
_hour = now.replace(minute=0, second=0, microsecond=0)
prev = next((e for e in reversed(hist) if _at(e) < _hour), None)
_gt, _gh = prev_hour_homepage(now)
if _gh and (not prev or _gt > _at(prev)): prev = {'at': _gt.isoformat(timespec='seconds'), 'ids': headline_ids(_gh)}   # main's own history wins
blocked = set(prev['ids']) if prev else set()
# how many earlier hours showed each story in the headlines, and which stories have led: stories never shown come
# first, a story that already led never leads again (an update leads only as a new development story or via --critical)
shown, led, core6 = {}, set(), set()
for t, hp in recent_homepages(now, 6):
    for i in headline_ids(hp): shown[i] = shown.get(i, 0) + 1
    led.add((hp.get('lead') or {}).get('id')); core6 |= set(core_ids(hp))
for e in hist:   # this homepage's own record too (covers a run that has not reached git yet)
    if (now - _at(e)).total_seconds() < 6 * 3600 and _at(e) < _hour:
        for n, i in enumerate(e.get('ids') or []):
            shown[i] = shown.get(i, 0) + 1
            if n == 0: led.add(i)
def upd(i):
    t = A[i].get('updated')
    return (t if t.tzinfo else t.replace(tzinfo=IST)) if isinstance(t, dt.datetime) else None
def allowed(i):
    if i in a.drop: return False
    if i not in blocked: return True
    return i in a.critical and upd(i) is not None and upd(i) > _at(prev)
for i in a.critical:
    if i in blocked and not allowed(i): print(f'{i}: --critical needs an update since {_at(prev):%H:%M} (set `updated:` and add the new facts), or a new development story')

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
    lbl = lambda d: (d.get('format_label') or '').split('/')[-1].strip()
    L['live'] = {**(L.get('live') or {}), 'title': {'en': lbl(A[i]), 'hi': lbl(HI[i])}}   # the red label on the lead names the lead's own subject
if _pending_lead:
    if not allowed(a.lead): sys.exit(f'{a.lead} led or was in the headlines at {_at(prev):%H:%M}: headlines change every hour (update it and pass --critical, or lead with a new story)')
    set_lead(a.lead)
lead = L['id']
# under 7 hours, so it is still under 8 an hour later; never markets, never an infographic, never a stale clock figure
fresh_photo = lambda d: d['type'] == 'news' and (now - d['_t']).total_seconds() < 7 * 3600 and not is_markets(d['id'], d) and not PIC.get(d['id'], {}).get('graphic') and not clocked(d['id'])
bad = (not ok(lead)) and 'held or unpublished' or (not allowed(lead) and not a.lead and f'already in the headlines at {_at(prev):%H:%M}') or (lead in led and lead not in a.critical and not a.lead and 'it has led before (a story leads only once)') or (is_markets(lead, A.get(lead)) and 'a markets story') or (clocked(lead) and 'pinned to a stale clock figure') or (A[lead]['type'] == 'news' and age(lead) > 8 and f'{age(lead):.0f} hours old')
if not bad and not a.lead and PIC.get(lead, {}).get('graphic'):
    # Rule 13: the lead has a real photo. Swap to the newest fresh story of the SAME running story that has one.
    same = [i for i in newest(fresh_photo) if i != lead and allowed(i) and (len(words(i) & words(lead)) >= 2 or (set(A[i].get('topics') or []) & set(A[lead].get('topics') or []) and A[i]['section'] == A[lead]['section']))]
    if same: print(f'lead {lead} is an infographic; {same[0]} (same story, real photo) leads instead'); set_lead(same[0]); lead = same[0]
if not bad and not a.lead and PIC.get(lead, {}).get('graphic'): bad = 'an infographic (a pictured story leads when one exists)'
if bad and not a.lead:
    # Owner's rule: the lead is under 8 hours old and never a markets story. Pick the replacement mechanically.
    PRIO = {'politics': 0, 'national': 0, 'states': 0, 'india': 0, 'world': 1, 'sports': 2, 'science': 2, 'tech': 2, 'economy': 3}
    cand = sorted([i for i in newest(fresh_photo) if allowed(i) and (i not in led or i in a.critical) and i not in core6], key=lambda i: (PRIO.get(A[i].get('section'), 1), -A[i]['_t'].timestamp()))
    # fallbacks, best first: a pictured story that was beside the lead in the last 6 hours (it never led), then an infographic story
    cand = cand or [i for i in newest(fresh_photo) if allowed(i) and i not in led] or [i for i in newest(lambda d: d['type'] == 'news' and (now - d['_t']).total_seconds() < 7 * 3600 and not is_markets(d['id'], d) and not clocked(d['id'])) if allowed(i) and i not in led and i not in core6]
    if cand:
        print(f'lead {lead} replaced ({bad}) by {cand[0]}'); set_lead(cand[0]); lead = cand[0]
    else:
        print(f'WARNING: the lead {lead} is {bad} and no fresh non-markets story with a real photo exists; publish one and re-run.')
        if not ok(lead): sys.exit(3)

# ---- live band: still-fresh items, topped up with the newest stories sharing a topic or subject words with the lead
lt, lw = set(A[lead].get('topics') or []), words(lead)
rel = [i for i in (L.get('relatedBelow') or []) if ok(i) and allowed(i) and not is_markets(i, A.get(i)) and not clocked(i) and (A[i]['type'] != 'news' or age(i) <= 24)]
for i in newest(lambda d: d['id'] != lead and (d['type'] != 'news' or (now - d['_t']).total_seconds() < 86400)):
    if len(rel) >= 3: break
    if i in rel or is_markets(i, A.get(i)) or clocked(i) or not allowed(i): continue
    if len(lw & words(i)) >= 2 or (lt & set(A[i].get('topics') or []) and A[i]['section'] == A[lead]['section']): rel.append(i)
L['relatedBelow'] = rel[:3]

# ---- headlines
pool = [i for i in a.pin if ok(i) and age(i) < 24] + newest(lambda d: d['type'] == 'news' and (now - d['_t']).total_seconds() < 86400)
# Explainers, editorials and fact checks of the last 48 hours fill what news cannot, so every headline slot changes every hour
pool += newest(lambda d: d['type'] in ('explainer', 'editorial', 'factcheck') and (now - d['_t']).total_seconds() < 48 * 3600)
pins = [i for i in a.pin if ok(i)]
pool = pins + sorted([i for i in dict.fromkeys(pool) if i not in pins], key=lambda i: shown.get(i, 0))   # stable: newest first within each count
taken, secs, mk, used_words = [], {}, 0, set(words(lead))
for i in pool:
    if i == lead or i in taken or i in rel or clocked(i) or not allowed(i): continue
    if is_markets(i, A.get(i)) and mk >= 1: continue
    s = A[i].get('section') or A[i]['type']
    if len(taken) < 8 and secs.get(s, 0) >= 2: continue
    if len(words(i) & used_words) >= 2 or (taken and same_subject(i, taken[-1], A.get(i), A.get(taken[-1]))) or (not taken and same_subject(i, lead, A.get(i), A.get(lead))): continue
    taken.append(i); secs[s] = secs.get(s, 0) + 1; used_words |= words(i); mk += bool(is_markets(i, A.get(i)))
    if len(taken) >= 16: break
nb = len(L.get('relatedBeside') or []) or 4
# the four beside the lead: never in the lead or beside it in the last 6 hours (critical updates excepted)
fresh_core = [i for i in taken if i not in core6 or (i in a.critical and allowed(i))]
# a story showing an infographic never sits beside the lead while a pictured story is available (owner's rule: photos at the top)
fresh_core = [i for i in fresh_core if not PIC.get(i, {}).get('graphic')] + [i for i in fresh_core if PIC.get(i, {}).get('graphic')]
beside = fresh_core[:nb]
if len(beside) < nb: print(f'WARNING: only {len(beside)} stories not in the top five in the last 6 hours: publish more stories this run'); beside += [i for i in taken if i not in beside][:nb - len(beside)]
L['relatedBeside'] = beside
rest = [i for i in taken if i not in beside]
taken = beside + rest
# moving pictured stories beside the lead can put a third story of one section into the top eight: push the extra ones down
for _ in range(len(taken)):
    cnt, mv = {}, None
    for k, i in enumerate(taken[:8]):
        s_ = A[i].get('section') or A[i]['type']; cnt[s_] = cnt.get(s_, 0) + 1
        if cnt[s_] > 2 and k >= nb: mv = k; break
    if mv is None: break
    x = taken.pop(mv); taken.insert(8, x)
rest = taken[len(beside):]
h['topStories'] = {'big': {'id': rest[0], 'also': []}, 'list': rest[1:6], 'also': rest[6:8]} if rest else h['topStories']

def short(lbl): return (lbl.split('/')[-1].strip() or lbl) + ':'
h['briefing']['items'] = [{'link': i, 'lead': {'en': short(A[i].get('format_label', A[i]['section'])), 'hi': short(HI[i].get('format_label', ''))},
                           'text': {'en': A[i]['title'], 'hi': HI[i]['title']}} for i in taken[:8]]

# ---- section and desk lists
for s in h.get('sections', []) + h.get('desks', []):
    ids = newest(lambda d, sec=s['section']: d['type'] == 'news' and d.get('section') == sec and not clocked(d['id']) and d['id'] not in a.drop)  # rule 6: a stale clock figure never sits in a section list
    if not ids: continue
    n = max(len(s.get('list') or []), 3)
    if 'lead' in s: s['lead'], s['list'] = ids[0], ids[1:1 + n]
    else: s['list'] = ids[:n]

# ---- long form
for key, typ in (('startHere', 'explainer'), ('opinion', 'editorial')):
    n = len(h.get(key) or []) or 4
    fresh = newest(lambda d, t=typ: d['type'] == t)
    if fresh: h[key] = fresh[:n]

# ---- the week ahead: built from dated sources every refresh, never hand-kept (week_ahead.py)
import week_ahead
h['weekAhead'] = week_ahead.build(now)
if len(h['weekAhead']) < 3: print(f"WARNING: only {len(h['weekAhead'])} dated items for the week ahead: add an `upcoming:` block to previews")

# ---- remember this hour's headlines (a re-run inside the same hour replaces its own entry)
entry = {'at': now.isoformat(timespec='seconds'), 'ids': [lead] + rel[:3] + taken[:8]}
if hist and _at(hist[-1]) >= _hour: hist[-1] = entry
else: hist.append(entry)
h['headlineHistory'] = hist[-8:]
h['critical'] = [i for i in a.critical if allowed(i)]
if len(taken) < 8: print(f'WARNING: only {len(taken)} fresh headlines not shown last hour: publish more stories this run')

json.dump(h, open('content/homepage.json', 'w'), ensure_ascii=False, indent=2)
open('content/homepage.json', 'a').write('\n')
print('lead:', lead, f'({age(lead):.0f}h)')
print('live band:', rel[:3])
for n, i in enumerate(taken[:12], 1): print(f'  {n}. [{A[i].get("section") or A[i]["type"]}] {age(i):.0f}h {i}')
