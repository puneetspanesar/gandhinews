"""One new main picture for one story, start to finish: candidate -> download (GitHub workflow) -> files -> photos.json + map.

  python3 newsroom/scripts/one_photo.py <story-id> <candidates-dir> <query-key> <n> "<English alt>" "<Hindi alt>"

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
sid, cdir, key, n, alt, alt_hi = sys.argv[1], sys.argv[2].rstrip('/'), sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6]
C = json.load(open(f'{cdir}/photo-candidates/candidates.json'))
c = next(x for x in C[key]['candidates'] if x['n'] == n)
lic = str(c.get('licence') or '')
if re.search(r'\b(nc|nd)\b', lic.lower().replace('godl-india', '')): sys.exit(f'licence {lic} is not allowed')
if (c.get('width') or 0) < 900: sys.exit(f'{c.get("width")} px wide: too small for a main picture')
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
for p in P:
    if fileof(p.get('sourceUrl')) == fileof(c['url']):
        s = re.sub(r'--(p\d+|bg|in|c)$', '', str(p.get('articleId', '')).replace('part:', '').split(':')[0])
        if s in pub and (now - pub[s]).days < 7: sys.exit(f'this photo was used by {s} on {pub[s]:%B %d}: the 7-day rule')
pid = f'o-{sid}'[:90]  # o- = one_photo; x-, v-, c-, i-, r- belong to other tools
credit = clean_credit(c.get('author') or '') or 'Wikimedia Commons contributor'
P = [p for p in P if p['id'] != pid] + [{'id': pid, 'articleId': sid, 'sourceUrl': c['url'], 'credit': f'Photo: {credit} / Wikimedia Commons',
     'licence': lic, 'alt': alt, 'alt_hi': alt_hi, 'page': c['page']}]
json.dump(P, open('content/photos.json', 'w'), ensure_ascii=False, indent=1); open('content/photos.json', 'a').write('\n')
tag = re.sub(r'[^a-z0-9]', '', sid)[:12] + now.strftime('%H%M')
r = subprocess.run([sys.executable, 'newsroom/scripts/photos_gh.py', 'download', tag, pid], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip())
raw = f'{W}raw-{tag}/{pid}.jpg'
if not os.path.exists(raw): sys.exit('download failed; photos.json entry left in place, run again')
im = Image.open(raw).convert('RGB')
for w, sfx in ((1280, '1280'), (640, '640')):
    x = im.copy(); x.thumbnail((w, w * 2)); x.save(f'public/photos/{pid}-{sfx}.jpg', quality=82, optimize=True, progressive=True)
h = round(im.height * 1280 / im.width)
M[sid] = {'id': pid, 'src': f'/photos/{pid}-1280.jpg', 'src800': f'/photos/{pid}-640.jpg', 'width': 1280, 'height': h,
          'credit': f'Photo: {credit} / Wikimedia Commons', 'licence': lic, 'alt': alt, 'alt_hi': alt_hi, 'page': c['page']}
json.dump(M, open('content/photos.map.json', 'w'), ensure_ascii=False, indent=1); open('content/photos.map.json', 'a').write('\n')
print(f'{sid}: {alt} ({credit}, {lic}) {M[sid]["src"]}')
