"""Find freely reusable portraits for people listed in scripts/portrait-people.json.
1) Wikimedia Commons (file search by several name spellings, plus Category:<Name>).
2) Creative Commons (CC BY) YouTube videos: grab frames, keep the largest clear face.
Writes portrait-candidates/candidates.json and image crops for human review."""
import json, os, subprocess, time, urllib.parse, urllib.request
import cv2

UA = {'User-Agent': 'GandhiNewsPortraitFinder/1.0 (newsroom; github.com/puneetspanesar)'}
OUT = 'portrait-candidates'; os.makedirs(OUT + '/img', exist_ok=True)
people = json.load(open('scripts/portrait-people.json'))
OK = ('cc0', 'cc by', 'cc-by', 'public domain', 'pd', 'godl')
face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def get(url):
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r: return r.read()
        except Exception as e:
            print('retry', url[:80], e); time.sleep(4 * (a + 1))
    return None

def commons(q, limit=10):
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': q, 'gsrnamespace': 6, 'gsrlimit': limit, 'prop': 'imageinfo', 'iiprop': 'url|size|mime|extmetadata', 'iiurlwidth': 600})
    b = get(u); time.sleep(1.5)
    if not b: return []
    return list((json.loads(b).get('query') or {}).get('pages', {}).values())

def commons_cat(name):
    u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'generator': 'categorymembers', 'gcmtitle': 'Category:' + name, 'gcmtype': 'file', 'gcmlimit': 20, 'prop': 'imageinfo', 'iiprop': 'url|size|mime|extmetadata', 'iiurlwidth': 600})
    b = get(u); time.sleep(1.5)
    return list((json.loads(b).get('query') or {}).get('pages', {}).values()) if b else []

def best_face(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fs = face.detectMultiScale(g, 1.1, 6, minSize=(60, 60))
    if len(fs) == 0: return None
    x, y, w, h = max(fs, key=lambda f: f[2] * f[3])
    sharp = cv2.Laplacian(g[y:y + h, x:x + w], cv2.CV_64F).var()
    return (w * h, sharp, (x, y, w, h))

def crop(img, box, path):
    x, y, w, h = box; H, W = img.shape[:2]
    s = int(max(w, h) * 2.2); cx, cy = x + w // 2, y + int(h * 0.62)
    x0, y0 = max(0, cx - s // 2), max(0, cy - s // 2); x1, y1 = min(W, x0 + s), min(H, y0 + s)
    c = img[y0:y1, x0:x1]
    if c.size == 0: return False
    cv2.imwrite(path, cv2.resize(c, (400, 400)), [cv2.IMWRITE_JPEG_QUALITY, 90]); return True

res = {}
for p in people:
    key = p['key']; names = [n for n in p['names'] if n]; res[key] = []
    seen = set()
    pages = commons_cat(names[0])
    for n in names: pages += commons(f'"{n}"')
    for pg in pages:
        ii = (pg.get('imageinfo') or [{}])[0]; t = pg.get('title')
        if not ii or t in seen or ii.get('mime') not in ('image/jpeg', 'image/png'): continue
        seen.add(t)
        md = ii.get('extmetadata', {}); lic = (md.get('LicenseShortName', {}).get('value') or '').lower()
        if not lic.startswith(OK) or ' nc' in lic or 'nd' in lic.split(): continue
        b = get(ii['thumburl']);
        if not b: continue
        arr = cv2.imdecode(__import__('numpy').frombuffer(b, 'uint8'), cv2.IMREAD_COLOR)
        if arr is None: continue
        f = best_face(arr)
        if not f: continue
        fn = f'{key}-c{len(res[key])}.jpg'
        if crop(arr, f[2], f'{OUT}/img/{fn}'):
            res[key].append({'kind': 'commons', 'img': fn, 'title': t, 'page': ii.get('descriptionurl'), 'url': ii.get('url'), 'licence': md.get('LicenseShortName', {}).get('value'), 'author': (md.get('Artist', {}).get('value') or '')[:200], 'face': f[0]})
        if len(res[key]) >= 4: break
    # YouTube CC BY
    try:
        q = f'ytsearch15:{names[0]} Punjab minister'
        r = subprocess.run(['yt-dlp', '--skip-download', '-j', '--no-warnings', q], capture_output=True, text=True, timeout=600)
        vids = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    except Exception as e:
        print('yt fail', key, e); vids = []
    cc = [v for v in vids if 'creative commons' in (v.get('license') or '').lower()]
    print(key, 'commons', len(res[key]), 'yt', len(vids), 'cc', len(cc))
    for v in cc[:3]:
        vid = v['id']; tmp = f'/tmp/{key}-{vid}.mp4'
        subprocess.run(['yt-dlp', '-f', 'best[height<=720][ext=mp4]/best[height<=720]', '--download-sections', '*20-80', '-o', tmp, '--no-warnings', f'https://www.youtube.com/watch?v={vid}'], capture_output=True, timeout=600)
        if not os.path.exists(tmp): continue
        cap = cv2.VideoCapture(tmp); fps = cap.get(cv2.CAP_PROP_FPS) or 25; best = None; i = 0
        while True:
            ok, fr = cap.read()
            if not ok: break
            if i % int(fps * 2) == 0:
                f = best_face(fr)
                if f and (best is None or f[0] * min(f[1], 300) > best[0][0] * min(best[0][1], 300)): best = (f, fr.copy())
            i += 1
        cap.release(); os.remove(tmp)
        if best and best[0][0] > 9000:
            fn = f'{key}-y{vid}.jpg'
            if crop(best[1], best[0][2], f'{OUT}/img/{fn}'):
                res[key].append({'kind': 'youtube', 'img': fn, 'title': v.get('title'), 'channel': v.get('channel') or v.get('uploader'), 'page': v.get('webpage_url'), 'licence': v.get('license')})
json.dump(res, open(f'{OUT}/candidates.json', 'w'), indent=1, ensure_ascii=False)
