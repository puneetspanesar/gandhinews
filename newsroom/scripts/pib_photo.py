"""Official photos from PIB (Press Information Bureau), the first stop for any story about a government event.

PIB's copyright policy lets anyone reproduce its material free of charge with the source acknowledged; it does not
cover third-party material it carries. So only photos inside PIB's own press releases are used, credited "Photo: PIB".

  python3 newsroom/scripts/pib_photo.py find <tag> "<words>" ["<words>" ...]
      Reads PIB's latest press releases (the national feed, English and Hindi), keeps the releases whose English or
      Hindi title or text contains ALL the words of a query (e.g. "Amit Shah Uttarakhand"), and saves their photos as
      candidates in /home/claude/gn-work/pib<tag>/photo-candidates/ (candidates.json, thumbs/, sheet.jpg). LOOK at
      sheet.jpg, then register a pick exactly like a Commons candidate:
  python3 newsroom/scripts/one_photo.py <story-id> /home/claude/gn-work/pib<tag> <key> <n> "<English alt>" "<Hindi alt>"
      (key q1, q2... in query order). one_photo.py downloads it straight from PIB, crops and registers it.
Photos under 600 px wide are left out, and banners. Under 900 px a photo is fine in cards but never the lead's picture.
"""
import json, os, re, sys, io, html, urllib.request
from PIL import Image, ImageDraw

UA = {'User-Agent': 'Mozilla/5.0 (gandhinews photo desk)'}
W = os.environ.get('GN_WORK') or '/home/claude/gn-work/'
FEEDS = ['https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3', 'https://pib.gov.in/RssMain.aspx?ModId=6&Lang=2&Regid=3']
MINW = 600   # most PIB event photos are about 600 px wide: fine in cards; refresh_home.py never leads with one under 900


def get(url, binary=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        d = r.read()
    return d if binary else d.decode('utf-8', 'ignore')


def text(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', h)))).strip()


def release(prid):
    h = get(f'https://pib.gov.in/PressReleasePage.aspx?PRID={prid}')
    t = re.search(r'<h1 id="Titleh2"[^>]*>([\s\S]*?)</h1>', h) or re.search(r'<h2[^>]*>([\s\S]*?)</h2>', h)
    imgs = list(dict.fromkeys(re.findall(r'(https?://static\.pib\.gov\.in/WriteReadData/userfiles/image/[^"\'\s>]+)', h)))
    other = re.findall(r"PressReleasePage\.aspx\?PRID=(\d+)['\"][^>]*>\s*(?:English|हिंदी|Hindi)", h)
    body = text(h[t.end():]) if t else text(h)
    return {'prid': prid, 'title': text(t.group(1)) if t else '', 'images': imgs, 'other': other, 'body': body[:6000],
            'page': f'https://pib.gov.in/PressReleasePage.aspx?PRID={prid}'}


def main():
    if len(sys.argv) < 4 or sys.argv[1] != 'find': sys.exit(__doc__)
    tag, queries = sys.argv[2], sys.argv[3:]
    out = f'{W}pib{tag}/photo-candidates/'; os.makedirs(out + 'thumbs', exist_ok=True)
    prids = []
    for f in FEEDS:
        try: prids += re.findall(r'PRID=(\d+)', get(f))
        except Exception as e: print(f'feed {f}: {e}')
    prids = list(dict.fromkeys(prids))
    rel = {}
    for p in prids:
        try: r = release(p)
        except Exception as e: print(f'PRID {p}: {e}'); continue
        rel[p] = r
        for o in r['other']:          # the English twin of a Hindi release (or the other way): same event, same photos
            if o not in rel and o not in prids:
                try: rel[o] = release(o)
                except Exception: pass
    print(f'{len(rel)} PIB releases read')
    C, seen, dup = {}, {}, {}
    for qi, q in enumerate(queries, 1):
        key, words = f'q{qi}', [w.lower() for w in q.split()]
        cands = []
        for p, r in rel.items():
            hay = (r['title'] + ' ' + r['body']).lower()
            for o in r['other']: hay += ' ' + ((rel.get(o) or {}).get('title', '') + ' ' + (rel.get(o) or {}).get('body', '')).lower()
            if not all(w in hay for w in words): continue
            for u in r['images']:
                if u in seen: im = seen[u]
                else:
                    try: d = get(u, True); im = Image.open(io.BytesIO(d)).convert('RGB')
                    except Exception: continue
                    seen[u] = im
                w_, h_ = im.size
                g = im.convert('L').resize((12, 12)); fp = (w_, h_, bytes(v // 32 for v in g.tobytes()))
                if fp in dup.get(key, set()): continue      # the Hindi and English releases carry the same photos
                dup.setdefault(key, set()).add(fp)
                if w_ < MINW or h_ < 300 or w_ / h_ > 4: continue   # too small, or a banner/strip
                n = len(cands) + 1
                th = im.copy(); th.thumbnail((480, 480)); th.save(f'{out}thumbs/{key}-{n}.jpg', quality=80)
                cands.append({'n': n, 'url': u, 'width': w_, 'height': h_, 'licence': 'PIB (free reproduction with credit)',
                              'author': 'PIB', 'source': 'pib', 'page': r['page'], 'title': next((t for t in [r['title']] + [(rel.get(o) or {}).get('title', '') for o in r['other']] if t and re.search(r'[A-Za-z]{4}', t)), r['title'])})  # the English title when there is one
        C[key] = {'query': q, 'candidates': cands}
        print(f'{key} "{q}": {len(cands)} photos' + ''.join(f"\n   {c['n']}. {c['width']}x{c['height']}  {c['title'][:90]}" for c in cands))
    json.dump(C, open(out + 'candidates.json', 'w'), ensure_ascii=False, indent=1)
    tiles = [(k, c['n']) for k, v in C.items() for c in v['candidates']]
    if tiles:
        cols = 4; rows = (len(tiles) + cols - 1) // cols
        S = Image.new('RGB', (cols * 320, rows * 240), 'white'); dr = ImageDraw.Draw(S)
        for i, (k, n) in enumerate(tiles):
            t = Image.open(f'{out}thumbs/{k}-{n}.jpg'); t.thumbnail((316, 212))
            S.paste(t, ((i % cols) * 320 + 2, (i // cols) * 240 + 2)); dr.text(((i % cols) * 320 + 6, (i // cols) * 240 + 218), f'{k} {n}', fill='black')
        S.save(out + 'sheet.jpg', quality=80); print('sheet:', out + 'sheet.jpg')
    print('candidates dir:', f'{W}pib{tag}')


if __name__ == '__main__':
    main()
