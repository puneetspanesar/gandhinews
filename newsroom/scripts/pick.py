"""Pick a candidate photo for every panel in plan.json, never reusing a file already on the site.
Reads plan.json, vq.json, every pcv*/photo-candidates/candidates.json in gn-work. Writes picks.json.
A panel's own query is tried first, then its 'alts' queries, then any extra pools listed in extra.json
({panel query: [extra query text, ...]}) from a later search round."""
import os as _gn_os; GN_ROOT = _gn_os.environ.get('GN_ROOT') or _gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.abspath(__file__)))) + '/'  # repo root (works in any clone)
import json, re, os, glob, urllib.parse
import cv2, numpy as np
from PIL import Image
W = (_gn_os.environ.get('GN_WORK') or '/home/claude/gn-work/')
plan = json.load(open(W + 'plan.json')); vq = json.load(open(W + 'vq.json'))
extra = json.load(open(W + 'extra.json')) if os.path.exists(W + 'extra.json') else {}
pools = {}  # clean query text -> [(dir, key, candidates)]
for f in sorted(glob.glob(W + 'pcv*/photo-candidates/candidates.json')):
    d = f.split('/')[-3]
    for k, v in json.load(open(f)).items():
        q = v.get('query', vq.get(k, '')).split('||')[0]
        pools.setdefault(q, []).append((d, k, v['candidates']))
fileof = lambda u: urllib.parse.unquote(re.sub(r'/\d+px-[^/]+$', '', u.split('?')[0]).replace('/thumb/', '/')).split('/')[-1].lower()
P = json.load(open(GN_ROOT + 'content/photos.json'))
# Reuse rule: a photo is off limits only while another story that used it is less than 48 hours old (owner, November 12).
import datetime as _dt, glob as _g
_pub = {}
for _f in _g.glob(GN_ROOT + 'content/en/*/*.md'):
    _m = re.search(r'\npublished:\s*["\']?([0-9T:+\-.]+)', open(_f).read())
    if _m:
        try: _pub[os.path.basename(_f)[:-3]] = _dt.datetime.fromisoformat(_m.group(1))
        except Exception: pass
_now = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=5, minutes=30)))
_story = lambda aid: re.sub(r'--(p\d+|bg|in|c)$', '', aid.split(':')[1] if aid.startswith('part:') else aid)
def _recent(aid):
    t = _pub.get(_story(aid))
    if t is not None and t.tzinfo is None: t = t.replace(tzinfo=_now.tzinfo)
    return t is None or (_now - t).total_seconds() < 48 * 3600
taken = {fileof(p['sourceUrl']) for p in P if not p.get('composite') and p['articleId'].split(':')[1 if p['articleId'].startswith('part:') else 0] not in plan and _recent(p['articleId'])}
used_before = {fileof(p['sourceUrl']) for p in P if not p.get('composite')}   # older uses: allowed, but a fresh photo is preferred
BLOCK = {l.strip().lower() for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocklist.txt')) if l.strip() and not l.startswith('#')} if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocklist.txt')) else set()
taken |= BLOCK
CASC = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def face_score(path):
    try: g = cv2.cvtColor(np.array(Image.open(path).convert('RGB')), cv2.COLOR_RGB2GRAY)
    except Exception: return 0, 0
    fs = CASC.detectMultiScale(g, 1.1, 6, minSize=(20, 20))
    if len(fs) == 0: return 0, 0
    return len(fs), max(w * h for (x, y, w, h) in fs) / (g.shape[0] * g.shape[1])
STOP = {'the', 'and', 'india', 'indian', 'of', 'logo', 'building', 'city', 'new', 'delhi', 'district', 'office', 'headquarters'}
toks = lambda s: [t for t in re.split(r'[^a-z0-9]+', s.lower()) if len(t) > 2 and t not in STOP]
picks = {}
for sid in sorted(plan):
    out = []
    for pn in plan[sid]['panels']:
        best = None
        qt = toks(re.sub(r'\(.*?\)', '', pn['q']))
        kinds = [pn['kind']] + (['place'] if pn['kind'] == 'person' else [])
        for kind in kinds:
          if best: break
          for q in [pn['q']] + pn.get('alts', []) + extra.get(pn['q'], []):
            for d, k, cands in pools.get(q, []):
                for c in cands:
                    f = fileof(c['url'])
                    if f in taken: continue
                    title = (c['title'] + ' ' + (c.get('description') or '')).lower()
                    if kind == 'person':
                        if qt and qt[-1] not in title: continue
                        nf, big = face_score(f"{W}{d}/photo-candidates/thumbs/{c['thumb']}")
                        if nf == 0: continue
                        score = 10 + big * 100 - (nf - 1) * 3
                    else:
                        hits = sum(1 for t in qt if t in title)
                        if qt and not hits: continue
                        if pn['kind'] == 'person' and hits < len(qt): continue  # a person's name used as a place: all words must match
                        score = hits
                    score += min(c['width'], 3000) / 1000 - c['n'] * 0.2 - (3 if f in used_before else 0)
                    if not best or score > best['score']:
                        best = dict(q=pn['q'], dir=d, key=k, n=c['n'], title=c['title'], url=c['url1600'], page=c['page'],
                                    licence=c['licence'], author=c['author'], score=round(score, 2), kind=pn['kind'], what=pn['what'])
        if best: taken.add(fileof(best['url']))
        out.append(best)
    picks[sid] = out
json.dump(picks, open(W + 'picks.json', 'w'), indent=1, ensure_ascii=False)
full = sum(1 for v in picks.values() if all(v)); part = sum(1 for v in picks.values() if any(v) and not all(v))
print('complete', full, 'partial', part, 'none', len(picks) - full - part)
for s, v in picks.items():
    miss = [pn['q'] for pn, x in zip(plan[s]['panels'], v) if not x]
    if miss: print('  missing', s, miss)
