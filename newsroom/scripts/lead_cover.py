"""Photo cover for a lead-worthy story with no single usable photo: 2-3 real photos side by side (owner, November 8).

The homepage lead is ALWAYS a photograph, never an infographic. When no one photo fits, mix 2-3 photos of the people,
place or thing in the story (e.g. the Chief Minister + the border fence) into one 16:10 cover.

Usage (repo root):
  python3 newsroom/scripts/lead_cover.py <story-id> "<English alt>" "<Hindi alt>" <photo> <photo> [<photo>]
<photo> is a library photo's story id or file in public/photos (any existing photo, reuse allowed for a cover), or
path:x0,x1 to take only the horizontal slice x0..x1 (0-1) of that image (e.g. one panel of an older composite).
Each panel is scaled to the full height and cropped to its share of the width around its centre (or the slice).
Credits and licences are joined from the sources. Replaces the story's map entry (an infographic cover is dropped).
"""
import json, os, sys
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
os.chdir(R)
sid, alt, alt_hi, *srcs = sys.argv[1:]
assert 2 <= len(srcs) <= 3, 'give 2 or 3 photos'
M = json.load(open('content/photos.map.json')); P = json.load(open('content/photos.json'))
W, H, G = 1280, 800, 6
parts, credits, lic = [], [], []
for s in srcs:
    sl = None
    if ':' in s and ',' in s.rsplit(':', 1)[1]: s, r = s.rsplit(':', 1); sl = [float(x) for x in r.split(',')]
    e = M.get(s)
    path = 'public' + e['src'] if e else (s if os.path.exists(s) else 'public/photos/' + s)
    im = Image.open(path).convert('RGB')
    if sl: im = im.crop((int(sl[0] * im.width), 0, int(sl[1] * im.width), im.height))
    parts.append(im)
    if e:
        for c in e['credit'].replace('Photos: ', '').replace('Photo: ', '').split('; '):
            if c not in credits: credits.append(c)
        if e.get('licence') and e['licence'] not in lic: lic.append(e['licence'])
# widths in proportion to each panel's natural width at full height, so nothing is stretched or over-zoomed
nat = [im.width * H / im.height for im in parts]
avail = W - G * (len(parts) - 1)
ws = [int(avail * n / sum(nat)) for n in nat]; ws[-1] = avail - sum(ws[:-1])
out, x = Image.new('RGB', (W, H), 'white'), 0
for im, w in zip(parts, ws):
    sc = max(H / im.height, w / im.width)
    r = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    l, t = (r.width - w) // 2, (r.height - H) // 2
    out.paste(r.crop((l, t, l + w, t + H)), (x, 0)); x += w + G
pid = 'v-' + sid[:60]
out.save(f'public/photos/{pid}-1280.jpg', quality=88); out.resize((640, 400), Image.LANCZOS).save(f'public/photos/{pid}-640.jpg', quality=86)
cr = ('Photos: ' if len(credits) > 1 else 'Photo: ') + '; '.join(credits)
M[sid] = {'id': pid, 'src': f'/photos/{pid}-1280.jpg', 'src800': f'/photos/{pid}-640.jpg', 'width': W, 'height': H, 'credit': cr,
          'licence': ' and '.join(lic), 'alt': alt, 'alt_hi': alt_hi, 'page': None, 'srcWidth': W}
json.dump(M, open('content/photos.map.json', 'w'), ensure_ascii=False, indent=1)
P = [p for p in P if p.get('articleId') != sid] + [{'id': 'x-' + sid, 'articleId': sid, 'sourceUrl': '', 'credit': cr, 'licence': ' and '.join(lic), 'alt': alt, 'alt_hi': alt_hi, 'page': None, 'composite': ['lead-cover']}]
json.dump(P, open('content/photos.json', 'w'), ensure_ascii=False, indent=1)
print(f'{sid}: photo cover {pid} ({len(parts)} panels, {cr}). Read public/photos/{pid}-1280.jpg before publishing.')
