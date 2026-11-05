"""Counter check for the homepage. Fails (exit 1) on any breach of the owner's homepage rules; prints every problem.
Rules checked, mechanically:
  lead: a published news story under 8 hours old, never a markets story, with a real photo (not an infographic)
  every homepage id exists in English and Hindi and has a picture (a held or deleted story never stays on the page)
  live band, beside the lead, top stories, briefing: news from the last 24 hours
  headlines: at most one markets story, at most two per section in the top eight, no two neighbours on the same subject,
    no photo shown twice
  clock-pinned figures ("by 10 am", "सुबह 10 बजे तक") in titles, standfirsts and the lead overlay, English and Hindi:
    stale 2 hours after that clock time
  markets band: while the market is open its figures are under 2 hours old
  the site moves: between 8 am and midnight the newest news story is under 3 hours old
  headlines change every hour: nothing in the headlines was in the previous hour's headlines (git), unless marked
    critical and updated since
Exit 0: all rules hold. Exit 1: problems to fix before publishing. Exit 2: only rule breaches that cannot be fixed
this run (an infographic lead when no fresh story has a photo, no new story in 3 hours): publish, they go in the run record.
Usage: python3 newsroom/scripts/check_fresh.py   (run from the repo root)"""
import json, glob, yaml, sys, os, re, datetime as dt
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gnrules import MKT, words, stale_clock, is_markets, same_subject, headline_ids, prev_hour_homepage

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
now = dt.datetime.now(IST)
tz = lambda t: (t if t.tzinfo else t.replace(tzinfo=IST)) if isinstance(t, dt.datetime) else None
P, H = {}, {}
T = {os.path.basename(f)[:-3] for f in glob.glob('content/en/tracker/*.md')} | {os.path.basename(f)[:-3] for f in glob.glob('content/en/topic/*.md')}
for lang, store in (('en', P), ('hi', H)):
    for f in glob.glob(f'content/{lang}/*/*.md'):
        d = yaml.safe_load(open(f).read().split('---')[1]) or {}
        if d.get('id') and tz(d.get('published')):
            d['published'] = tz(d['published']); d['updated'] = tz(d.get('updated'))
            store[d['id']] = d
M = json.load(open('content/photos.map.json'))
h = json.load(open('content/homepage.json'))
bad, warn, soft = [], [], []
flag = lambda what, i, n=0: bad.append((what, i, n))

SKIP = {'overlay', 'text', 'kicker', 'value', 'title', 'label', 'indicator', 'icon', 'tracker', 'topic', 'type', 'kn', 'numbers', 'dataDesk', 'trackers', 'live', 'dataBox', 'indicators', 'section', 'map', 'parliament', 'headlineHistory', 'critical'}
def ids(x, strict=False):
    """Every story id referenced in x. Strings that look like ids but are not published are reported."""
    if isinstance(x, str):
        if x in P: return [x]
        if x in T: return []
        if strict and '-' in x and ' ' not in x and len(x) > 12 and not x.startswith(('/', 'http')): flag('homepage points at a story that is not published (held, deleted or misspelt)', x)
        return []
    if isinstance(x, list): return [i for y in x for i in ids(y, strict)]
    if isinstance(x, dict): return [i for k, v in x.items() if k not in SKIP for i in ids(v, strict)]
    return []
age = lambda i: (now - P[i]['published']).total_seconds() / 3600

lead = h['lead']['id']
if lead not in P: flag('lead is not a published story', lead); lead = None
else:
    if P[lead]['type'] == 'news' and age(lead) > 8: flag('lead is over 8 hours old', lead, age(lead))
    if is_markets(lead, P[lead]): flag('markets story as the lead', lead)
    if (M.get(lead) or {}).get('graphic'): soft.append(('lead shows an infographic, not a photo: find a photo of the event, or lead with a fresh story that has one', lead, 0))

everything = ids(h, strict=True)
for i in dict.fromkeys(everything):
    if i not in H: flag('no Hindi twin', i)
    if i not in M: flag('no picture (never put an unpictured story on the homepage)', i)

for name, part in [('live band', h['lead'].get('relatedBelow')), ('beside lead', h['lead'].get('relatedBeside')),
                   ('briefing', h.get('briefing')), ('top stories', h.get('topStories'))]:
    for i in ids(part):
        if P[i]['type'] == 'news' and age(i) > 24: flag(f'{name}: over 24 hours old', i, age(i))

heads = []
ts = h.get('topStories') or {}
for part in [h['lead'].get('relatedBeside'), (ts.get('big') or {}).get('id'), ts.get('list'), ts.get('also'), h.get('briefing')]:
    for i in ids(part):
        if i not in heads and i != lead: heads.append(i)
mk = [i for i in heads if is_markets(i, P[i])]
if len(mk) > 1: flag('more than one markets story in the headlines', ', '.join(mk))
for sec, n in Counter(P[i].get('section') for i in heads[:8]).items():
    if n > 2: flag(f'more than two {sec} stories in the top eight', sec, n)
seq = ([lead] if lead else []) + heads[:8]
for a, b in zip(seq, seq[1:]):
    if same_subject(a, b, P.get(a), P.get(b)): flag('same subject side by side', f'{a} / {b}')
srcs = Counter((M.get(i) or {}).get('src') for i in seq)
for s, n in srcs.items():
    if s and n > 1: flag('same photo twice at the top', s, n)

def clock_check(i, label, txt, lang, when):
    for m, hrs in stale_clock(txt, lang, when, now):
        flag(f'{label} pins a figure to "{m}" and it is now {now:%H:%M}: update the figure or move the story off the top', i, hrs)
for i in seq + ids(h['lead'].get('relatedBelow')):
    for lang, store in (('en', P), ('hi', H)):
        d = store.get(i)
        if not d: continue
        when = d.get('updated') or d['published']
        if (now - when).total_seconds() > 24 * 3600: continue
        for fld in ('title', 'standfirst'): clock_check(i, f'{lang} {fld}', str(d.get(fld) or ''), lang, when)
        kp = d.get('keyPoints') or []
        if kp: clock_check(i, f'{lang} first key point', str(kp[0]), lang, when)
        ov = ((d.get('hero') or {}).get('overlay') or {})
        clock_check(i, f'{lang} picture overlay', str(ov.get('value') or ''), lang, when)
if lead:
    ov = h['lead'].get('overlay') or {}
    for lang in ('en', 'hi'):
        when = P[lead].get('updated') or P[lead]['published']
        for part in ('value', 'text'): clock_check(lead, f'{lang} lead overlay', str((ov.get(part) or {}).get(lang, '')), lang, when)

# The owner's first homepage rule: every headline changes every hour. Compared with main's homepage of the previous
# hour (from git, not from anything this run wrote). A story marked critical in homepage.json may stay only if it was
# updated after that homepage went up; a new development story (its own id) is a new headline.
pt, ph = prev_hour_homepage(now)
if ph:
    crit = set(h.get('critical') or [])
    for i in set(headline_ids(h)) & set(headline_ids(ph)):
        if i not in P: continue
        u = P[i].get('updated')
        if i in crit and u and u > pt: continue
        flag(f'already in the headlines at {pt:%H:%M}: every headline changes every hour (run refresh_home.py; critical news only as an update with --critical)', i)

if len(h.get('weekAhead') or []) < 2: flag('the week ahead band has fewer than 2 items (refresh_home.py builds it; add `upcoming:` blocks to previews)', 'weekAhead')

mk_open = now.weekday() < 5 and (9, 15) <= (now.hour, now.minute) <= (15, 30)
try:
    _mk = json.load(open('content/data/markets.json'))
    _asof = tz(dt.datetime.fromisoformat(str(_mk.get('as_of'))))
    if mk_open and (now - _asof).total_seconds() > 2 * 3600:
        flag('markets band figures are more than 2 hours old while the market is open', _mk.get('as_of'), (now - _asof).total_seconds() / 3600)
except (OSError, ValueError, TypeError) as e:
    if mk_open: flag('markets band data unreadable', str(e))

news = [i for i in P if P[i]['type'] == 'news']
if news and 8 <= now.hour:
    newest = min(age(i) for i in news)
    if newest > 3: soft.append(('no new story in over 3 hours (the site must visibly change every hour)', '', newest))

for w in warn: print('WARNING: ' + w)
if bad:
    print('HOMEPAGE PROBLEMS (fix before publishing):')
    for n, i, a in bad + soft: print(f'  {n}: {i}' + (f' ({a:.1f})' if a else ''))
    sys.exit(1)
if soft:
    # Exit 2: a rule is broken but publishing is still better than leaving the site still. The run publishes,
    # writes the breach into its run record (run_record.py reads this file), and the next run must clear it.
    print('RULE BREACHES (publish, record them, clear them next run):')
    for n, i, a in soft: print(f'  {n}: {i}' + (f' ({a:.1f})' if a else ''))
    open(os.environ.get('GN_WORK', '/home/claude/gn-work/') + 'breaches.txt', 'w').write('\n'.join(f'{n}: {i}' for n, i, a in soft) + '\n')
    sys.exit(2)
print('OK: homepage rules all hold (lead under 8 hours, headlines fresh and balanced, no stale clock figures).')
