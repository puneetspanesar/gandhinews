"""Add more licensed solo photos of a library person from Wikimedia Commons (owner, November 10: never the same picture on
two collages, so the people we cover most need many different photos).

Usage (repo root): python3 newsroom/scripts/more_portraits.py <person-key> [<how many to add, default 8>] ...
Takes only CC BY, CC BY-SA, CC0, public-domain and GODL-India files at least 900px wide whose title names the person and
nobody else (no "with", "and", "meets"). treat_photo.py still rejects any that will not cut out as one clean figure.
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
UA = {'User-Agent': 'GandhiNewsDesk/1.0 (https://gandhinews.com)'}
OK_LIC = re.compile(r'^(CC BY(-SA)? [0-9.]+|CC0|Public domain|GODL-India)', re.I)
BAD_T = re.compile(r'\b(with|and|meets?|meeting|greets?|receives?|calls on|delegation|bilateral|family|group|signing|'
                   r'cabinet|summit|statue|poster|cutout|hoarding|wax|mural|painting|cartoon|logo|map|signature)\b|&|\bvs\b', re.I)


def api(params):
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(dict(params, format='json'))
    for wait in (0, 30, 60, 120, 240):
        time.sleep(wait)
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40))
        except urllib.error.HTTPError as ex:
            if ex.code != 429: raise
    raise SystemExit('Wikimedia keeps refusing (429): try again later')


def main():
    P = json.load(open(R + 'newsroom/library/people.json'))
    args = sys.argv[1:]
    pairs = []
    while args:
        k = args.pop(0); n = int(args.pop(0)) if args and args[0].isdigit() else 8
        pairs.append((k, n))
    for pk, want in pairs:
        v = P[pk]; name = v['en']; have = {p.get('title') for p in v.get('photos') or []}
        added = 0; cont = {}
        others = [x['en'] for k, x in P.items() if k != pk]
        while added < want:
            d = api(dict(action='query', generator='search', gsrsearch=f'intitle:"{name}" filetype:bitmap', gsrnamespace=6,
                         gsrlimit=50, prop='imageinfo', iiprop='url|size|extmetadata', **cont))
            for p in sorted((d.get('query') or {}).get('pages', {}).values(), key=lambda p: p.get('index', 0)):
                t = p['title']; ii = p['imageinfo'][0]; em = ii.get('extmetadata', {})
                lic = re.sub('<[^>]+>', '', (em.get('LicenseShortName') or {}).get('value', '')).strip()
                if t in have or not OK_LIC.match(lic) or ii['width'] < 900 or BAD_T.search(t) or any(o in t for o in others): continue
                if not t.lower().endswith(('.jpg', '.jpeg')): continue
                author = re.sub('<[^>]+>', '', (em.get('Artist') or {}).get('value', '')).strip()[:120] or 'Wikimedia Commons'
                v.setdefault('photos', []).append({'url': ii['url'], 'page': ii.get('descriptionurl'), 'author': author, 'licence': lic,
                                                    'width': ii['width'], 'height': ii['height'], 'title': t,
                                                    'date': re.sub('<[^>]+>', '', (em.get('DateTimeOriginal') or {}).get('value', ''))[:19], 'crop': None})
                have.add(t); added += 1
                if added >= want: break
            if 'continue' not in d: break
            cont = {k: x for k, x in d['continue'].items()}
            time.sleep(1)
        print(f'{pk}: added {added} (now {len(v["photos"])})', flush=True)
        json.dump(P, open(R + 'newsroom/library/people.json', 'w'), ensure_ascii=False, indent=1)
        time.sleep(5)
    json.dump(P, open(R + 'newsroom/library/people.json', 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
