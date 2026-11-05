"""Instant main picture from photos we already have (no search, no download).

Usage (repo root):
  python3 newsroom/scripts/quick_photo.py <story-id> "<subject>" [--list] [--pick <photo-id>]
<subject> is a person, place or thing as photo captions name it ("Rahul Gandhi", "Bombay Stock Exchange", "Eden Park").
--list   show the candidates (photo id, caption, last used) and stop. Look at them before picking.
--pick   use that candidate. Without --pick, the best candidate is used: a photo of that subject alone,
         not used by any story in the last 7 days (the owner's reuse rule), used least recently, largest.
The picture gets its own file (r-<story-id>-1280/640.jpg) and entries in content/photos.json and photos.map.json,
so check:photos and the photo credits page treat it like any other photo.
"""
import os as _gn_os; GN_ROOT = _gn_os.environ.get('GN_ROOT') or _gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.abspath(__file__)))) + '/'  # repo root (works in any clone)
import json, re, sys, shutil, glob, os, datetime as dt
from urllib.parse import unquote
import yaml

R = GN_ROOT + ''
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
now = dt.datetime.now(IST)
args = [a for a in sys.argv[1:] if not a.startswith('--')]
sid, subject = args[0], args[1]
pick = sys.argv[sys.argv.index('--pick') + 1] if '--pick' in sys.argv else None
listing = '--list' in sys.argv

P = json.load(open(R + 'content/photos.json'))
M = json.load(open(R + 'content/photos.map.json'))
pub = {}
for f in glob.glob(R + 'content/en/*/*.md'):
    m = re.search(r'\npublished:\s*["\']?([0-9T:+\-.]+)', open(f).read())
    if m:
        try: pub[os.path.basename(f)[:-3]] = dt.datetime.fromisoformat(m.group(1))
        except ValueError: pass

fileof = lambda u: unquote(str(u).split('?')[0].replace('/thumb/', '/')).split('/')[-1].lower() if 'px-' not in str(u).split('/')[-1] else unquote(str(u).split('/')[-2]).lower()
story = lambda aid: re.sub(r'--(p\d+|bg|in|c)$', '', str(aid).replace('part:', '').split(':')[0])
uses = {}
for p in P:
    if p.get('composite') or str(p.get('articleId', '')).startswith('portrait:'): continue
    uses.setdefault(fileof(p.get('sourceUrl', '')), []).append(story(p.get('articleId')))
byid = {}
for art, e in M.items(): byid.setdefault(e.get('id'), e)

BL = {l.strip().lower() for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocklist.txt')) if l.strip() and not l.startswith('#')}
import fcntl
_lk = open(R + 'content/.photos.lock', 'w'); fcntl.flock(_lk, fcntl.LOCK_EX)
words = subject.lower()
cands = []
for p in P:
    alt = str(p.get('alt', ''))
    if p.get('composite') or words not in alt.lower(): continue
    if re.search(r'\band\b|,\s*(and|with)\b|\bwith\b', alt.split('(')[0]) and not re.search(r'\b(building|stadium|ground|office|house|bhavan)\b', alt.lower()): continue  # one subject only
    if fileof(p.get('sourceUrl', '')) in BL: continue
    e = byid.get(p['id'])
    if not e: continue
    if str(e.get('alt', '')).split(' (file')[0].strip() != alt.split(' (file')[0].strip(): continue  # the file shows something else (a split or a later crop)
    src = R + 'public' + e['src']
    if not os.path.exists(src): continue
    last = [pub[s] for s in set(uses.get(fileof(p.get('sourceUrl')), [])) if s in pub]
    lastu = max(last) if last else None
    if lastu and (now - lastu).days < 7: continue
    cands.append((lastu or dt.datetime(2000, 1, 1, tzinfo=IST), -int(e.get('height') or 0), p, e))
cands.sort(key=lambda c: (c[0], c[1]))
if listing or not cands:
    print(f'{len(cands)} usable photos of "{subject}" (not used in the last 7 days):')
    for lu, _, p, e in cands[:15]: print(f"  {p['id']}  last used {lu.date() if lu.year > 2000 else 'never'}  {p['alt'][:90]}  {e['src']}")
    if not cands: print('  none: use the photo finder, then an infographic.'); sys.exit(1)
    sys.exit(0)
c = next((x for x in cands if x[2]['id'] == pick), None) if pick else cands[0]
if not c: sys.exit(f'{pick}: not a usable candidate')
_, _, p, e = c
fa = lambda a: a if '(file' in a else a.rstrip() + ' (file photo)'
fh = lambda a: a if ('फ़ाइल' in a or 'फाइल' in a) else a.rstrip() + ' (फ़ाइल फ़ोटो)'
p = dict(p, alt=fa(str(p.get('alt') or '')), alt_hi=fh(str(p.get('alt_hi') or '')))
nid = f'r-{sid}'[:90]
for sz, key in (('1280', 'src'), ('640', 'src800')):
    shutil.copyfile(R + 'public' + e[key], f'{R}public/photos/{nid}-{sz}.jpg')
P.append({k: p.get(k) for k in ('sourceUrl', 'credit', 'licence', 'alt', 'alt_hi', 'page')} | {'id': nid, 'articleId': sid})
M[sid] = {'id': nid, 'src': f'/photos/{nid}-1280.jpg', 'src800': f'/photos/{nid}-640.jpg', 'width': e.get('width'), 'height': e.get('height'),
          'credit': e.get('credit'), 'licence': e.get('licence'), 'alt': p.get('alt'), 'alt_hi': p.get('alt_hi'), 'page': e.get('page')}
json.dump(P, open(R + 'content/photos.json', 'w'), ensure_ascii=False, indent=1)
json.dump(M, open(R + 'content/photos.map.json', 'w'), ensure_ascii=False, indent=1)
print(f'{sid}: {p["alt"]}  ({e["src"]})')
