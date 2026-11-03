"""Build the editor's review pack for the final check before publishing.

Usage (after a clean `npm run build`, from the repo root):
  python3 newsroom/scripts/review_pack.py <story-id> [<story-id> ...]
With no ids: every story published in the last 3 hours.

Writes /home/claude/gn-work/review/:
  home-desktop-1.png, home-desktop-2.png   the homepage top as a reader sees it (1440 wide, two screens)
  home-mobile.png                          the homepage top on a phone (390 wide)
  story-<n>.jpg                            one sheet per story: headline, section, standfirst, main picture,
                                           cover (English and Hindi) and every in-story photo with its caption
  list.txt                                 the sheets and the story ids, in order
"""
import json, os, re, sys, glob, subprocess, time, socket, datetime as dt
import yaml
from PIL import Image, ImageDraw, ImageFont

R = '/home/claude/gandhinews/'
OUT = '/home/claude/gn-work/review/'
FONT = R + 'newsroom/fonts/GoogleSans-700.ttf'
FONT_R = R + 'newsroom/fonts/GoogleSans-500.ttf'
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(OUT + '*'): os.remove(f)


def fm(sid, lang='en'):
    for t in ('news', 'explainer', 'editorial'):
        p = f'{R}content/{lang}/{t}/{sid}.md'
        if os.path.exists(p):
            raw = open(p).read()
            return yaml.safe_load(raw.split('---')[1]) or {}, raw
    return {}, ''


ids = sys.argv[1:]
if not ids:
    now = dt.datetime.now(IST)
    for p in glob.glob(R + 'content/en/*/*.md'):
        d, _ = fm(os.path.basename(p)[:-3])
        t = d.get('published')
        if isinstance(t, dt.datetime):
            t = t if t.tzinfo else t.replace(tzinfo=IST)
            if (now - t).total_seconds() < 3 * 3600: ids.append(d['id'])

# ---- Homepage screenshots from the built site
port = 4391
srv = subprocess.Popen(['python3', '-m', 'http.server', str(port), '-d', R + 'dist'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(40):
    try: socket.create_connection(('localhost', port), 0.5).close(); break
    except OSError: time.sleep(0.25)
js = f"""
const {{chromium}} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{viewport: {{width: 1440, height: 1100}}}});
  await p.goto('http://localhost:{port}/', {{waitUntil: 'networkidle'}});
  await p.screenshot({{path: '{OUT}home-desktop-1.png'}});
  await p.evaluate(() => window.scrollTo(0, 1050)); await p.waitForTimeout(400);
  await p.screenshot({{path: '{OUT}home-desktop-2.png'}});
  const m = await b.newPage({{viewport: {{width: 390, height: 844}}, deviceScaleFactor: 2}});
  await m.goto('http://localhost:{port}/', {{waitUntil: 'networkidle'}});
  await m.screenshot({{path: '{OUT}home-mobile.png', clip: {{x: 0, y: 0, width: 390, height: 1700}}, fullPage: true}});
  await b.close();
}})();
"""
open(OUT + 'shot.js', 'w').write(js)
subprocess.run(['node', OUT + 'shot.js'], cwd=R, check=False)
srv.terminate()

# ---- One sheet per story
M = json.load(open(R + 'content/photos.map.json'))
f_h = ImageFont.truetype(FONT, 30); f_s = ImageFont.truetype(FONT_R, 20); f_c = ImageFont.truetype(FONT_R, 17)


def wrap(d, s, f, w):
    out, cur = [], ''
    for word in str(s).split():
        t = (cur + ' ' + word).strip()
        if d.textlength(t, font=f) <= w or not cur: cur = t
        else: out.append(cur); cur = word
    if cur: out.append(cur)
    return out


def img(path, w):
    p = R + 'public' + path if path and path.startswith('/') else path
    if not p or not os.path.exists(p): return None
    im = Image.open(p).convert('RGB'); im.thumbnail((w, w)); return im


lines = []
for n, sid in enumerate(ids, 1):
    d, raw = fm(sid)
    W = 1500
    sheet = Image.new('RGB', (W, 2400), 'white'); dr = ImageDraw.Draw(sheet); y = 24
    dr.text((24, y), f"{d.get('section', '')} | {d.get('format_label', '')} | {str(d.get('published', ''))[:16]}", font=f_c, fill=(204, 0, 0)); y += 30
    for l in wrap(dr, d.get('title', sid), f_h, W - 48): dr.text((24, y), l, font=f_h, fill='black'); y += 38
    for l in wrap(dr, d.get('standfirst', ''), f_s, W - 48): dr.text((24, y), l, font=f_s, fill='black'); y += 26
    y += 12
    m = M.get(sid) or {}
    row = []
    main = img(m.get('src'), 700)
    row.append(('MAIN PICTURE: ' + str(m.get('alt', 'NONE')), main))
    cv = m.get('cover') or {}
    for lang in ('en', 'hi'):
        if cv.get(lang): row.append((f'COVER ({lang})', img(cv[lang]['src'], 700)))
    x = 24; rowh = 0
    for cap, im in row:
        if x + 720 > W: x = 24; y += rowh + 60; rowh = 0
        if im is None:
            dr.rectangle((x, y, x + 700, y + 300), outline=(204, 0, 0), width=4); dr.text((x + 20, y + 140), 'NO PICTURE', font=f_h, fill=(204, 0, 0)); h = 300
        else:
            sheet.paste(im, (x, y)); h = im.height
        for i, l in enumerate(wrap(dr, cap, f_c, 700)[:2]): dr.text((x, y + h + 6 + i * 20), l, font=f_c, fill='black')
        rowh = max(rowh, h); x += 740
    y += rowh + 70
    for blk in re.finditer(r"```photo\s*\n(.*?)\n```", raw, re.S):
        try: b = json.loads(blk.group(1))
        except Exception: continue
        e = M.get(f"{sid}--p{b.get('n')}")
        im = img(e['src'], 460) if e else None
        if y + 420 > sheet.height: break
        if im is None:
            dr.text((24, y), f"IN-STORY PHOTO {b.get('n')}: NOT FOUND (block will be dropped): {b.get('subject')}", font=f_c, fill=(204, 0, 0)); y += 30; continue
        sheet.paste(im, (24, y))
        for i, l in enumerate(wrap(dr, f"IN-STORY {b.get('n')}: {b.get('caption', '')}  [shows: {e.get('alt', '')}]", f_c, W - 540)[:6]):
            dr.text((510, y + i * 22), l, font=f_c, fill='black')
        y += im.height + 20
    sheet = sheet.crop((0, 0, W, min(sheet.height, y + 20)))
    out = f'{OUT}story-{n:02d}.jpg'; sheet.save(out, quality=82)
    lines.append(f'story-{n:02d}.jpg  {sid}')
open(OUT + 'list.txt', 'w').write('\n'.join(lines) + '\n')
print(f'{len(ids)} story sheets and 3 homepage screenshots in {OUT}')
