"""One new main picture for one story, start to finish: candidate -> download (GitHub workflow) -> files -> photos.json + map.

  python3 newsroom/scripts/one_photo.py <story-id> <candidates-dir> <query-key> <n> "<English alt>" "<Hindi alt>"
  python3 newsroom/scripts/one_photo.py <story-id> --person "<name>"     from the people library (checked portraits;
                                                                          the first one not used in the last 7 days)

<candidates-dir> is what `photos_gh.py find` printed (it holds photo-candidates/candidates.json); <query-key> and <n>
pick the candidate you LOOKED AT. Alt text names what is in the picture; add "(file photo)" / "(फ़ाइल फ़ोटो)" when it is
not from this event. Writes public/photos/<id>-1280.jpg and -640.jpg (original aspect ratio), then the entries.
Refuses NC/ND licences, pictures under 900 px wide, and a source already used by a story in the last 7 days.
"""
import json, os, re, sys, subprocess, datetime as dt, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gnrules import clean_credit
from PIL import Image
GN_ROOT = os.environ.get('GN_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
W = os.environ.get('GN_WORK') or '/home/claude/gn-work/'
LIBRARY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'library', 'people.json')
sid = sys.argv[1]
if sys.argv[2] == '--person':
    # the people library: checked portraits of the people most in the news; seconds instead of a search
    who = sys.argv[3].strip().lower()
    LIB = json.load(open(LIBRARY))
    key = next((k for k, v in LIB.items() if who in (k, v['en'].lower()) or who in [x.lower() for x in v.get('aliases', [])]), None)
    if not key: sys.exit(f'{sys.argv[3]} is not in the people library (newsroom/library/people.json): use the finder')
    person = LIB[key]
    cands = person['photos']; alt = f"{person['en']} (file photo)"; alt_hi = f"{person['hi']} (फ़ाइल फ़ोटो)"
else:
    cdir, key, n, alt, alt_hi = sys.argv[2].rstrip('/'), sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6]
    C = json.load(open(f'{cdir}/photo-candidates/candidates.json'))
    cands = [next(x for x in C[key]['candidates'] if x['n'] == n)]
os.chdir(GN_ROOT)
import fcntl
_lk = open('content/.photos.lock', 'w'); fcntl.flock(_lk, fcntl.LOCK_EX)  # never two writers of photos.json at once
P = json.load(open('content/photos.json')); M = json.load(open('content/photos.map.json'))
from urllib.parse import unquote
fileof = lambda u: unquote(str(u).split('?')[0].replace('/thumb/', '/')).split('/')[-1].lower() if 'px-' not in str(u).split('/')[-1] else unquote(str(u).split('/')[-2]).lower()
IST = dt.timezone(dt.timedelta(hours=5, minutes=30)); now = dt.datetime.now(IST)
pub = {}
for f in glob.glob('content/en/*/*.md'):
    m = re.search(r'\npublished:\s*["\']?([0-9T:+\-.]+)', open(f).read())
    if m:
        try: pub[os.path.basename(f)[:-3]] = dt.datetime.fromisoformat(m.group(1))
        except ValueError: pass
BL = {l.strip().lower() for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocklist.txt')) if l.strip() and not l.startswith('#')}
def why_not(c):
    lic = str(c.get('licence') or '')
    if re.search(r'\b(nc|nd)\b', lic.lower().replace('godl-india', '')): return f'licence {lic} is not allowed'
    minw = 560 if 'crop' in c and not c.get('crop') else 900   # a checked library headshot reads well from 560 px
    if c.get('source') == 'pib': minw = 600                       # PIB event photos: usually about 600 px
    if c.get('crop'): minw = 900 / c['crop'][2]                   # a crop must itself be 900 px wide
    if (c.get('width') or 0) < minw: return f'{c.get("width")} px wide: too small for a main picture'
    if fileof(c['url']) in BL or fileof(c['url']).replace(' ', '_') in BL: return f'{fileof(c["url"])} is on the blocklist'
    for p in P:
        if fileof(p.get('sourceUrl')) == fileof(c['url']):
            s_ = re.sub(r'--(p\d+|bg|in|c)$', '', str(p.get('articleId', '')).replace('part:', '').split(':')[0])
            if s_ in pub and s_ != sid and (now - pub[s_]).days < 7: return f'used by {s_} on {pub[s_]:%B %d} (the 7-day rule)'
    return None
reasons = [(c, why_not(c)) for c in cands]
c = next((c for c, r in reasons if not r), None)
if not c: sys.exit('no usable photo: ' + '; '.join(r for _, r in reasons))
lic = str(c.get('licence') or '')
pid = f'o-{sid}'[:90]  # o- = one_photo; x-, v-, c-, i-, r- belong to other tools
credit = clean_credit(c.get('author') or '') or 'Wikimedia Commons contributor'
CREDIT = 'Photo: PIB' if c.get('source') == 'pib' else f'Photo: {credit} / Wikimedia Commons'
# the story's old main picture entries go, so check:photos does not count a picture the story no longer shows
main_of = lambda aid: str(aid).replace('part:', '').split(':')[0]
P = [p for p in P if p['id'] != pid and main_of(p.get('articleId')) != sid] + [{'id': pid, 'articleId': sid, 'sourceUrl': c['url'], 'credit': CREDIT,
     'licence': lic, 'alt': alt, 'alt_hi': alt_hi, 'page': c['page']}]
json.dump(P, open('content/photos.json', 'w'), ensure_ascii=False, indent=1); open('content/photos.json', 'a').write('\n')
tag = re.sub(r'[^a-z0-9]', '', sid)[:12] + now.strftime('%H%M')
raw = f'{W}raw-{tag}/{pid}.jpg'
if c.get('source') == 'pib':   # PIB is reachable directly: no GitHub workflow needed
    import urllib.request; os.makedirs(os.path.dirname(raw), exist_ok=True)
    open(raw, 'wb').write(urllib.request.urlopen(urllib.request.Request(c['url'], headers={'User-Agent': 'Mozilla/5.0 (gandhinews photo desk)'}), timeout=60).read())
else:
    r = subprocess.run([sys.executable, 'newsroom/scripts/photos_gh.py', 'download', tag, pid], capture_output=True, text=True)
    print(r.stdout.strip(), r.stderr.strip())
    if not os.path.exists(raw) and 'upload.wikimedia.org' in str(c['url']):
        # GitHub Actions unavailable (e.g. billing): Commons is reachable directly, so fetch it from here
        import urllib.request, time; os.makedirs(os.path.dirname(raw), exist_ok=True)
        # Wikimedia asks scripts to fetch its standard thumbnail sizes (https://w.wiki/GHai), not originals
        u_ = str(c['url']).split('?')[0]
        if (c.get('width') or 0) > 1920 and '/commons/' in u_ and '/thumb/' not in u_:
            u_ = u_.replace('/commons/', '/commons/thumb/', 1) + '/1920px-' + u_.split('/')[-1]
        elif (c.get('width') or 9999) > 960 and '/commons/' in u_ and '/thumb/' not in u_:
            # wider than 960 px or width unknown: try a standard thumbnail size (1280 or 960 px) first, the original only if that fails
            sz = 1280 if (c.get('width') or 9999) > 1280 else 960
            th = u_.replace('/commons/', '/commons/thumb/', 1) + f'/{sz}px-' + u_.split('/')[-1]
            try:
                data = urllib.request.urlopen(urllib.request.Request(th, headers={'User-Agent': 'GandhiNewsPhotoDesk/1.0 (noreply@anthropic.com)'}), timeout=120).read()
                open(raw, 'wb').write(data); print('downloaded 1280 px thumbnail from Commons')
            except Exception as e:
                print('thumbnail download:', e)
        for t in range(0 if os.path.exists(raw) else 4):
            try:
                data = urllib.request.urlopen(urllib.request.Request(u_, headers={'User-Agent': 'GandhiNewsPhotoDesk/1.0 (noreply@anthropic.com)'}), timeout=120).read()
                open(raw, 'wb').write(data); print('downloaded directly from Commons'); break
            except Exception as e:
                print('direct download:', e); time.sleep(30 * (t + 1))
if not os.path.exists(raw): sys.exit('download failed; photos.json entry left in place, run again')
im = Image.open(raw).convert('RGB')
if c.get('crop'):   # library portraits from big official photos: the crop around the face, worked out when the library was built
    X, Y, w_, h_ = c['crop']; im = im.crop((int(X * im.width), int(Y * im.height), int((X + w_) * im.width), int((Y + h_) * im.height)))
if im.height > im.width * 0.8:
    # A tall portrait goes into wide slots: crop it to 3:2 around the face, never the chest
    ch = int(im.width * 2 / 3); top = int(im.height * 0.06)
    try:
        import cv2, numpy as np
        g = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
        f = sorted(cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(g, 1.1, 6, minSize=(40, 40)), key=lambda r: -r[2])
        if len(f): top = int(f[0][1] + f[0][3] / 2 - 0.45 * ch)
    except Exception:
        pass
    top = max(0, min(top, im.height - ch)); im = im.crop((0, top, im.width, top + ch))
for w, sfx in ((1280, '1280'), (640, '640')):
    x = im.copy(); x.thumbnail((w, w * 2)); x.save(f'public/photos/{pid}-{sfx}.jpg', quality=82, optimize=True, progressive=True)
h = round(im.height * 1280 / im.width)
M[sid] = {'id': pid, 'src': f'/photos/{pid}-1280.jpg', 'src800': f'/photos/{pid}-640.jpg', 'width': 1280, 'height': h,
          'srcWidth': im.width, 'credit': CREDIT, 'licence': lic, 'alt': alt, 'alt_hi': alt_hi, 'page': c['page']}
json.dump(M, open('content/photos.map.json', 'w'), ensure_ascii=False, indent=1); open('content/photos.map.json', 'a').write('\n')
print(f'{sid}: {alt} ({credit}, {lic}) {M[sid]["src"]}')
