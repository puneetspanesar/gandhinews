"""Build newsroom/library/people.json from finder results for newsroom/library/people.tsv.
  python3 newsroom/scripts/build_library.py pick <pcv-dir> ...    choose up to 3 portraits per person, write the review sheets
  python3 newsroom/scripts/build_library.py reject <slug>:<n> ...  drop photos the review found wrong (n = position, 1-3)
  python3 newsroom/scripts/build_library.py write                 write people.json from the reviewed picks
A portrait qualifies when the file title or description names the person (every part of the name), it is at least 900 px
wide, the licence allows reuse (no NC/ND), it is not on the blocklist, and the title does not suggest a group
("with", "and", "meeting"). Newest years and "official"/"portrait" titles rank first. Every pick is LOOKED AT on the
review sheets before it goes in the library: a name in a title is not proof of who is in the picture.
"""
import json, re, sys, os, glob, unicodedata
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); LIBD = os.path.join(os.path.dirname(HERE), 'library')
W = os.environ.get('GN_WORK') or '/home/claude/gn-work/'
PICKS = W + 'library-picks.json'
norm = lambda s: re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower())
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()).strip('-')
def people():
    out = {}
    for l in open(os.path.join(LIBD, 'people.tsv')):
        if not l.strip() or l.startswith('#'): continue
        en, hi, q = (l.rstrip('\n').split('|') + ['', ''])[:3]
        out[slug(en)] = {'en': en, 'hi': hi, 'q': q or en}
    return out
BL = {l.strip().lower() for l in open(os.path.join(HERE, 'blocklist.txt')) if l.strip() and not l.startswith('#')}
GROUP = re.compile(r'\b(with|and|meets?|meeting|delegation|team|group|family|crowd|rally|signing)\b|&')
_CV = None
def one_face(path, width=None):
    """The main face, and a 3:2 crop around it, when the picture shows one person clearly enough to use:
    returns {'crop': [x, y, w, h] as fractions, or None for the whole picture} or False.
    The main face must be the only large face (any other under 60% of its size). A small face (a speaker at a podium
    in a big official photo) is fine when a crop around it is still at least 900 px wide in the original."""
    global _CV
    try:
        import cv2
    except ImportError:
        return {'crop': None}
    if _CV is None: _CV = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    im = cv2.imread(path)
    if im is None: return False
    H, Wd = im.shape[:2]
    f = sorted(_CV.detectMultiScale(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), 1.1, 6, minSize=(14, 14)), key=lambda r: -r[2])
    if not len(f): return False
    x, y, fw, fh = [int(v) for v in f[0]]
    if len(f) > 1 and f[1][2] > 0.6 * fw: return False
    scale = (width or Wd) / Wd
    if fw >= 0.12 * Wd: return {'crop': None} if (width or 0) >= 600 else False
    cw = min(Wd, fw * 6.5); ch = min(H, cw * 2 / 3); cw = ch * 3 / 2
    if cw * scale < 900: return False
    cx = min(max(x + fw / 2 - cw / 2, 0), Wd - cw); cy = min(max(y + fh / 2 - 0.38 * ch, 0), H - ch)
    if len(f) > 1:   # another face inside the crop means it is not one person's picture
        for (ox, oy, ow, oh) in f[1:]:
            if ox > cx and ox + ow < cx + cw and oy > cy and oy + oh < cy + ch and ow > 0.35 * fw: return False
    return {'crop': [round(cx / Wd, 4), round(cy / H, 4), round(cw / Wd, 4), round(ch / H, 4)]}
def score(c, name):
    t = norm(c.get('title', '')); d = norm(c.get('description', ''))
    parts = [p for p in norm(name).split() if len(p) > 2] or norm(name).split()
    if not all(p in t or p in d for p in parts): return None
    if not all(p in t for p in parts[-1:]): return None             # the surname at least must be in the file title
    if (c.get('width') or 0) < 600: return None
    lic = str(c.get('licence') or '').lower().replace('godl-india', '')
    if re.search(r'\b(nc|nd)\b', lic): return None
    fn = str(c.get('url', '')).split('/')[-1].lower()
    if fn in BL: return None
    if GROUP.search(t.replace(norm(name), '')): return None
    yrs = [int(y) for y in re.findall(r'\b(20[0-2]\d)\b', t + ' ' + d + ' ' + str(c.get('date', '')))]
    s = (max(yrs) if yrs else 2000) * 10 + (30 if re.search(r'official|portrait|headshot', t) else 0) + min((c.get('height') or 0) / max(c.get('width') or 1, 1), 1.4) * 10
    return s
cmd = sys.argv[1]
if cmd == 'pick':
    PE = people(); picks = json.load(open(PICKS)) if os.path.exists(PICKS) else {}
    new = set()
    for d in sys.argv[2:]:
        C = json.load(open(f'{d}/photo-candidates/candidates.json'))
        for k, v in C.items():
            if k not in PE: continue
            sc = sorted(((score(c, PE[k]['en']), c) for c in v.get('candidates') or []), key=lambda x: -(x[0] or 0))
            ok_ = [dict(c, thumbpath=f'{d}/photo-candidates/thumbs/{c["thumb"]}') for s, c in sc if s is not None]
            got = []
            for c in ok_:
                fc = one_face(c['thumbpath'], c.get('width'))
                if fc: got.append(dict(c, **fc))
            picks[k] = got[:3]; new.add(k)
    json.dump(picks, open(PICKS, 'w'), ensure_ascii=False, indent=1)
    rows = [(k, PE[k]['en'], picks[k]) for k in PE if k in new and picks.get(k)]
    tag = os.path.basename(sys.argv[2].rstrip('/'))
    font = ImageFont.load_default()
    for sn in range(0, len(rows), 16):
        sheet = Image.new("RGB", (1000, 16 * 170), "white"); dr = ImageDraw.Draw(sheet)
        for r, (k, en, ph) in enumerate(rows[sn:sn + 16]):
            y = r * 170; dr.text((5, y + 5), f'{k}', fill='black', font=ImageFont.load_default(size=18))
            for i, c in enumerate(ph):
                try:
                    im = Image.open(c['thumbpath']).convert('RGB')
                    if c.get('crop'): X, Y, w_, h_ = c['crop']; im = im.crop((int(X * im.width), int(Y * im.height), int((X + w_) * im.width), int((Y + h_) * im.height)))
                    im.thumbnail((240, 150)); sheet.paste(im, (220 + i * 260, y + 5)); dr.text((220 + i * 260, y + 155), str(i + 1), fill='red', font=font)
                except OSError: dr.text((220 + i * 260, y + 60), 'no thumb', fill='red', font=font)
            if not ph: dr.text((220, y + 60), 'NO USABLE PORTRAIT', fill='red', font=font)
        sheet.save(f'{W}library-sheet-{tag}-{sn // 16:02d}.jpg', quality=80)
    print(f'{sum(1 for k in new if picks.get(k))} of {len(new)} new people have a portrait ({sum(1 for k in PE if picks.get(k))} of {len(PE)} in all); sheets {W}library-sheet-{tag}-*.jpg')
elif cmd == 'reject':
    picks = json.load(open(PICKS))
    drop = {}
    for a in sys.argv[2:]:
        k, n = a.rsplit(':', 1); drop.setdefault(k, set()).add(int(n) - 1)
    for k, ns in drop.items(): picks[k] = [c for i, c in enumerate(picks.get(k, [])) if i not in ns]
    json.dump(picks, open(PICKS, 'w'), ensure_ascii=False, indent=1); print('rejected', sum(len(v) for v in drop.values()))
elif cmd == 'write':
    PE = people(); picks = json.load(open(PICKS))
    lib = {k: {'en': PE[k]['en'], 'hi': PE[k]['hi'], 'aliases': [], 'photos': [{x: c.get(x) for x in ('url', 'page', 'author', 'licence', 'width', 'height', 'title', 'date', 'crop')} for c in picks[k]]} for k in PE if picks.get(k)}
    json.dump(lib, open(os.path.join(LIBD, 'people.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'{len(lib)} people, {sum(len(v["photos"]) for v in lib.values())} portraits in newsroom/library/people.json')
