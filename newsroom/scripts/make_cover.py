"""Gandhi News cover maker: 16:9 story covers (people over the scene, label, headline, our mark).

Usage (system python3, which has rembg, cv2, cairosvg):
  python3 newsroom/scripts/make_cover.py <raw dir> [story-id ...]
With no ids it makes covers for every story whose English front matter has a `cover:` block and no cover yet.

Front matter (English; the Hindi twin repeats `cover:` with Hindi label/headline/data labels):
  cover:
    template: faceoff | speaker | breaking | sport | business
    label: "CEC row"                       # red tag, 1-3 words
    headline: "'Modi's life is in Gyanesh Kumar'"   # 2 lines max, about 40 characters
    bg: "Ramlila Maidan"                   # Commons search for the scene behind the people (planned as <id>--bg)
    inset: "Iran Ministry of Foreign Affairs"   # breaking only, optional (planned as <id>--in)
    score: ["NZ 192/3", "IND 191/8"]       # sport only, optional
    data: [{icon: trend-up, value: "2.24 lakh", label: "e-two-wheelers registered"}]   # business only, 2-3 items
People are the story's main picture panels (hero.subjects, in order). A clean single-person photo is cut out;
a group photo or a small photo goes in a white-framed panel instead, so a cut-out never looks ghosted.
Writes public/photos/c-<id>-<lang>-1280.jpg / -640.jpg and adds "cover" to the story's entry in photos.map.json.
"""
import json, os, re, sys, io
import numpy as np, cv2, yaml
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

R = '/home/claude/gandhinews/'
FONTS = R + 'newsroom/fonts/'
W, H = 1280, 720
BAND = 330            # dark band at the bottom that carries the text
TEXT_TOP = 470        # nothing important (faces) below this line
RED = (204, 0, 0)
CASC = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
_session = None


def font(lang, size, bold=True):
    if lang == 'hi':
        f = ImageFont.truetype(FONTS + 'NotoSansDevanagari.ttf', size, layout_engine=ImageFont.Layout.RAQM)
        try: f.set_variation_by_axes([100, 700 if bold else 500])
        except Exception: pass
        return f
    return ImageFont.truetype(FONTS + ('GoogleSans-700.ttf' if bold else 'GoogleSans-500.ttf'), size)


def faces(im):
    """Faces as (x, y, w, h), biggest first. YuNet (a small neural detector) finds turned and bearded faces
    that the old Haar cascade misses; the cascade is the fallback."""
    rgb = np.array(im.convert('RGB')); bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    s = min(1.0, 1280 / max(bgr.shape[:2]))
    small = cv2.resize(bgr, None, fx=s, fy=s) if s < 1 else bgr
    try:
        det = cv2.FaceDetectorYN.create(R + 'newsroom/models/yunet.onnx', '', (small.shape[1], small.shape[0]), 0.75)
        _, out = det.detect(small)
        if out is not None and len(out):
            fs = [(x / s, y / s, w / s, h / s) for x, y, w, h in out[:, :4]]
            return sorted(fs, key=lambda r: -r[2] * r[3])
    except Exception:
        pass
    g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    fs = CASC.detectMultiScale(g, 1.1, 6, minSize=(24, 24))
    return sorted([(x / s, y / s, w / s, h / s) for (x, y, w, h) in fs], key=lambda r: -r[2] * r[3])


def can_cut(im, fs):
    """A clean cut-out needs one clear face that dominates the photo, on a photo big enough to stay sharp."""
    if not fs or min(im.size) < 700: return False
    big = fs[0]
    if big[3] < im.size[1] * 0.10 or big[3] < 120: return False
    return not any(f[2] * f[3] > big[2] * big[3] * 0.12 for f in fs[1:])  # any other real face: a group photo, never cut out


def cutout(im, face):
    global _session
    from rembg import remove, new_session
    _session = _session or new_session('u2net_human_seg')
    rgba = remove(im.convert('RGB'), session=_session)
    a = np.array(rgba)[:, :, 3]
    m = (a > 40).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    fx, fy = int(face[0] + face[2] / 2), int(face[1] + face[3] / 2)
    keep = lab[min(fy, lab.shape[0] - 1), min(fx, lab.shape[1] - 1)]
    if keep == 0 and n > 1: keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    a = np.where(lab == keep, a, 0).astype(np.uint8)
    # Soft edge: no hard threshold (that is what makes a cut-out look ghosted or jagged).
    a = cv2.GaussianBlur(a, (3, 3), 0)
    out = rgba.copy(); out.putalpha(Image.fromarray(a))
    return out


def outlined(cut, px=5):
    """White outline and a soft shadow around a cut-out."""
    a = np.array(cut.split()[3])
    ring = cv2.dilate((a > 60).astype(np.uint8) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * px + 1, 2 * px + 1)))
    ring = Image.fromarray(ring).filter(ImageFilter.GaussianBlur(0.8))
    pad = 40
    base = Image.new('RGBA', (cut.width + 2 * pad, cut.height + 2 * pad), (0, 0, 0, 0))
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0)); sh = Image.new('L', base.size, 0); sh.paste(ring, (pad, pad + 12))
    shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.55)))
    base = Image.alpha_composite(base, shadow)
    white = Image.new('RGBA', cut.size, (255, 255, 255, 255)); white.putalpha(ring)
    base.alpha_composite(white, (pad, pad)); base.alpha_composite(cut, (pad, pad))
    return base, pad


def would_cut(src, face_h=200, face_y=240):
    im = ImageOps.exif_transpose(src).convert('RGB'); fs = faces(im)
    if not (fs and can_cut(im, fs)): return False
    f = fs[0]; s = face_h / f[3]
    return (im.height - f[1]) * s + face_y - f[3] * s / 2 >= H - 10


def place_person(canvas, src, cx, face_h, panel=None, face_y=240, force_frame=False):
    """Put one person on the canvas, face centred at (cx, face_y).
    A clean single-person photo is cut out, sized so the body runs off the bottom of the cover (never floating).
    Anything else (a group photo, a small photo, a cut-out that would float) goes in a white frame, using
    `panel`: that person's crop from the story's main picture, which was already checked by eye."""
    im = ImageOps.exif_transpose(src).convert('RGB')
    fs = faces(im)
    if fs and can_cut(im, fs) and not force_frame:
        f = fs[0]
        s = face_h / f[3]
        if (im.height - f[1]) * s + face_y - f[3] * s / 2 >= H - 10:   # body reaches the bottom edge
            cut = cutout(im, f)
            cut = cut.resize((int(cut.width * s), int(cut.height * s)), Image.LANCZOS)
            img, pad = outlined(cut)
            x = int(cx - (f[0] + f[2] / 2) * s) - pad
            y = int(face_y - (f[1] + f[3] / 2) * s) - pad
            paste_clipped(canvas, img, x, y)
            return 'cut'
    bw, bh = 360, 384
    if panel is not None:
        crop = ImageOps.fit(panel, (bw, bh), Image.LANCZOS, centering=(0.5, 0.3))
    else:
        f = fs[0] if fs else (im.width * 0.4, im.height * 0.2, im.width * 0.2, im.height * 0.2)
        sc = bh * 0.36 / f[3]; cw, ch = bw / sc, bh / sc
        fx, fy = f[0] + f[2] / 2, f[1] + f[3] / 2
        cw, ch = min(cw, im.width), min(ch, im.height)
        x0 = min(max(fx - cw / 2, 0), im.width - cw); y0 = min(max(fy - ch * 0.4, 0), im.height - ch)
        crop = ImageOps.fit(im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))), (bw, bh), Image.LANCZOS)
    b = 8
    pnl = Image.new('RGBA', (bw + 2 * b, bh + 2 * b), (255, 255, 255, 255)); pnl.paste(crop, (b, b))
    sh = Image.new('RGBA', (pnl.width + 60, pnl.height + 60), (0, 0, 0, 0))
    m = Image.new('L', sh.size, 0); ImageDraw.Draw(m).rectangle((30, 42, 30 + pnl.width, 42 + pnl.height), fill=150)
    sh.putalpha(m.filter(ImageFilter.GaussianBlur(16)))
    x, y = int(cx - pnl.width / 2), 76
    canvas.alpha_composite(sh, (x - 30, y - 30)); canvas.alpha_composite(pnl, (x, y))
    return 'frame'


def paste_clipped(canvas, img, x, y):
    l, t = max(0, -x), max(0, -y)
    img = img.crop((l, t, min(img.width, W - x), min(img.height, H - y)))
    if img.width > 0 and img.height > 0: canvas.alpha_composite(img, (max(0, x), max(0, y)))


def bg_layer(canvas, path, focus=(0.5, 0.45)):
    im = ImageOps.fit(Image.open(path).convert('RGB'), (W, H), Image.LANCZOS, centering=focus)
    im = Image.eval(im, lambda v: int(v * 0.6))
    canvas.alpha_composite(im.convert('RGBA'))


def band(canvas):
    g = np.zeros((BAND, 1), np.float32)
    for i in range(BAND):
        t = i / (BAND - 1)  # 0 top of band, 1 bottom
        g[i] = 0.0 if t < 0 else (0.75 * min(t / 0.55, 1) + 0.21 * max(0, (t - 0.55) / 0.45))
    a = (np.repeat(g, W, axis=1) * 255).astype(np.uint8)
    layer = Image.new('RGBA', (W, BAND), (13, 13, 13, 255)); layer.putalpha(Image.fromarray(a))
    canvas.alpha_composite(layer, (0, H - BAND))


SEAL = open(R + 'src/components/seal.svg.txt').read()


def svg_png(svg, size, color=None):
    import cairosvg
    if color: svg = svg.replace('fill="currentColor"', f'fill="{color}"')
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size))).convert('RGBA')


def mark(canvas):
    d = ImageDraw.Draw(canvas)
    d.rectangle((36, H - 40 - 176 - 4, 40 + 176 + 3, H - 36), fill=(255, 255, 255, 255))
    canvas.alpha_composite(svg_png(SEAL, 176), (40, H - 40 - 176))


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    lines.append(cur)
    return lines


def text_block(canvas, lang, label, headline):
    d = ImageDraw.Draw(canvas)
    x, maxw = 248, W - 248 - 40
    up = (lambda s: s.upper()) if lang == 'en' else (lambda s: s)
    for size in (60, 54, 48, 44):
        f = font(lang, size)
        lines = wrap(d, up(headline), f, maxw)
        if len(lines) <= 2: break
    lh = int(size * (1.05 if lang == 'en' else 1.25))
    y = H - 40 - lh * len(lines)
    for i, ln in enumerate(lines):
        d.text((x + 1, y + i * lh + 3), ln, font=f, fill=(0, 0, 0, 120))
        d.text((x, y + i * lh), ln, font=f, fill=(255, 255, 255, 255))
    if label:
        lf = font(lang, 28 if lang == 'en' else 26)
        lt = up(label)
        tw = d.textlength(lt, font=lf)
        ly = y - 14 - 48
        d.rectangle((x, ly, x + tw + 28, ly + 46), fill=RED + (255,))
        d.text((x + 14, ly + 23), lt, font=lf, fill=(255, 255, 255, 255), anchor='lm')


def tag(canvas, lang, text):
    d = ImageDraw.Draw(canvas); f = font(lang, 16, bold=False)
    tw = d.textlength(text, font=f)
    d.rectangle((W - 40 - tw - 20, 32, W - 40, 62), fill=(13, 13, 13, 200))
    d.text((W - 40 - tw - 10, 47), text, font=f, fill=(255, 255, 255, 255), anchor='lm')


def icon(name, size, color='#ff4d4d'):
    return svg_png(open(R + f'src/icons/{name}.svg').read(), size, color)


def make(sid, raw, spec, lang, people, bgp, insetp, panels=None):
    panels = panels or [None] * len(people)
    t = spec.get('template', 'speaker')
    c = Image.new('RGBA', (W, H), (13, 13, 13, 255))
    if t == 'business':
        ImageDraw.Draw(c).rectangle((W - 560, 0, W, H), fill=RED + (255,))
        if bgp: bg_layer(c, bgp)  # a business story may still give a scene
    elif bgp: bg_layer(c, bgp)
    elif people:   # no scene photo: the story's own picture, blurred and darkened, so no photo is reused elsewhere
        im = ImageOps.fit(ImageOps.exif_transpose(people[0]).convert('RGB'), (W, H), Image.LANCZOS, centering=(0.5, 0.35))
        im = Image.eval(im.filter(ImageFilter.GaussianBlur(22)), lambda v: int(v * 0.45))
        tint = Image.new('RGB', (W, H), (90, 0, 0))
        c.alpha_composite(Image.blend(im, tint, 0.25).convert('RGBA'))
    modes = []
    if t == 'faceoff' and len(people) >= 2:
        same = not (would_cut(people[0]) and would_cut(people[1]))   # both cut out, or both framed: never mixed
        modes.append(place_person(c, people[0], 330, 200, panels[0], force_frame=same))
        modes.append(place_person(c, people[1], 950, 200, panels[1], force_frame=same))
    elif people:
        cx = {'speaker': 900, 'breaking': 330, 'sport': 930, 'business': 960}.get(t, 900)
        modes.append(place_person(c, people[0], cx, 220, panels[0]) if t != 'business' else place_product(c, people[0]))
    if t == 'breaking' and insetp:
        im = ImageOps.fit(Image.open(insetp).convert('RGB'), (230, 230), Image.LANCZOS)
        m = Image.new('L', (230, 230), 0); ImageDraw.Draw(m).ellipse((0, 0, 229, 229), fill=255)
        ring = Image.new('RGBA', (246, 246), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 245, 245), fill=(255, 255, 255, 255))
        c.alpha_composite(ring, (W - 64 - 238, 80)); im = im.convert('RGBA'); im.putalpha(m); c.alpha_composite(im, (W - 64 - 230, 88))
    band(c)
    if t == 'sport' and spec.get('score'):
        d = ImageDraw.Draw(c); f = font('en', 22); x = 40
        for i, s in enumerate(spec['score'][:2]):
            tw = d.textlength(s, font=f)
            d.rectangle((x, 40, x + tw + 32, 88), fill=((13, 13, 13, 255) if i == 0 else RED + (255,)), outline=(255, 255, 255, 255), width=3)
            d.text((x + 16, 64), s, font=f, fill=(255, 255, 255, 255), anchor='lm'); x += tw + 32
    if t == 'business' and spec.get('data'):
        d = ImageDraw.Draw(c); y = 96
        for it in spec['data'][:3]:
            c.alpha_composite(icon(it.get('icon', 'trend-up'), 48), (48, y + 8))
            d.text((112, y), it['value'], font=font(lang, 40), fill=(255, 255, 255, 255))
            d.text((112, y + 50), it['label'], font=font(lang, 22, bold=False), fill=(255, 255, 255, 255))
            y += 114
    mark(c)
    text_block(c, lang, spec.get('label', ''), spec['headline'])
    if bgp or any(m == 'frame' for m in modes): tag(c, lang, 'File photos' if lang == 'en' else 'फ़ाइल फ़ोटो')
    out = c.convert('RGB')
    base = f'{R}public/photos/c-{sid[:60]}-{lang}'
    out.save(base + '-1280.jpg', quality=86, optimize=True, progressive=True)
    out.resize((640, 360), Image.LANCZOS).save(base + '-640.jpg', quality=84, optimize=True, progressive=True)
    return f'/photos/c-{sid[:60]}-{lang}', modes


def place_product(c, src):
    from rembg import remove, new_session
    s = new_session('isnet-general-use')
    rgba = remove(ImageOps.exif_transpose(src).convert('RGB'), session=s)
    a = np.array(rgba)[:, :, 3]; m = (a > 140).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); m = (lab == keep).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    a = cv2.GaussianBlur((m * 255).astype(np.uint8), (3, 3), 0)
    rgba.putalpha(Image.fromarray(a)); rgba = rgba.crop(rgba.getbbox())
    s_ = min(560 / rgba.width, 470 / rgba.height)
    rgba = rgba.resize((int(rgba.width * s_), int(rgba.height * s_)), Image.LANCZOS)
    img, pad = outlined(rgba)
    c.alpha_composite(img, (W - 30 - rgba.width - pad, 90 - pad))
    return 'cut'


def fm(lang, sid):
    for t in ['news', 'explainer', 'editorial']:
        p = f'{R}content/{lang}/{t}/{sid}.md'
        if os.path.exists(p): return yaml.safe_load(open(p).read().split('---')[1]) or {}
    return {}


def raw_parts(P, aid, raw):
    for p in P:
        if p['articleId'] == aid and p.get('composite'):
            fs = [f'{raw}/{i}.jpg' for i in p['composite']]
            return [f for f in fs if os.path.exists(f)]
    return []


def main():
    raw = sys.argv[1]; ids = sys.argv[2:]
    P = json.load(open(R + 'content/photos.json')); M = json.load(open(R + 'content/photos.map.json'))
    if not ids:
        ids = [os.path.basename(f)[:-3] for t in ['news', 'explainer', 'editorial'] for f in sorted(os.listdir(f'{R}content/en/{t}')) if f.endswith('.md')]
        ids = [s for s in ids if s in M and 'cover' not in M[s] and (fm('en', s).get('cover'))]
    for sid in ids:
        en = fm('en', sid).get('cover'); hi = fm('hi', sid).get('cover') or {}
        if not en or sid not in M: print('skip', sid); continue
        own = raw_parts(P, f'{sid}--c', raw)           # cover-only people (cover.people), when the hero is a place
        people = [Image.open(f) for f in (own or raw_parts(P, sid, raw))]
        comp = f"{R}public{M[sid]['src']}"
        panels = None
        if os.path.exists(comp) and people and not own:
            ci = Image.open(comp).convert('RGB'); n = len(people); pw = (ci.width - 6 * (n - 1)) // n
            panels = [ci.crop((i * (pw + 6), 0, i * (pw + 6) + pw, ci.height)) for i in range(n)]
        if not people: print('no people parts in raw for', sid); continue
        bg = raw_parts(P, f'{sid}--bg', raw); ins = raw_parts(P, f'{sid}--in', raw)
        cov = {}
        for lang, spec in [('en', en), ('hi', {**en, **{k: v for k, v in hi.items() if v}})]:
            if lang == 'hi' and not hi.get('headline'): continue
            base, modes = make(sid, raw, spec, lang, people, bg[0] if bg else None, ins[0] if ins else None, panels)
            cov[lang] = {'src': base + '-1280.jpg', 'src800': base + '-640.jpg'}
        M[sid]['cover'] = {'width': W, 'height': H, **cov}
        print('cover', sid, modes)
    json.dump(M, open(R + 'content/photos.map.json', 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
