"""Contact sheets for review.
  python3 review_sheet.py picks   -> gn-work/ps<N>.jpg: the picked candidate thumbs per story (index, id, file title)
  python3 review_sheet.py final   -> gn-work/out<N>.jpg: the finished 640px composites for every story in picks.json
Open each image with the Read tool and check every panel shows the right person or place."""
import os as _gn_os; GN_ROOT = _gn_os.environ.get('GN_ROOT') or _gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.abspath(__file__)))) + '/'  # repo root (works in any clone)
import json, glob, sys
from PIL import Image, ImageDraw, ImageFont
W = (_gn_os.environ.get('GN_WORK') or '/home/claude/gn-work/'); R = GN_ROOT + ''
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
picks = json.load(open(W + 'picks.json')); ids = [s for s, v in picks.items() if any(v)]
if sys.argv[1] == 'picks':
    th = {}
    for f in glob.glob(W + 'pcv*/photo-candidates/candidates.json'):
        d = f.split('/')[-3]
        for k, v in json.load(open(f)).items():
            for c in v['candidates']: th[(d, k, c['n'])] = f"{W}{d}/photo-candidates/thumbs/{c['thumb']}"
    for b in range(0, len(ids), 12):
        ks = ids[b:b + 12]; im = Image.new('RGB', (1320, 6 * 215), 'white'); dr = ImageDraw.Draw(im)
        for r, s in enumerate(ks):
            x0 = (r % 2) * 660; y = (r // 2) * 215
            dr.text((x0 + 5, y + 2), f'{b + r} {s[:55]}', fill='black', font=F)
            for j, p in enumerate([p for p in picks[s] if p]):
                t = Image.open(th[(p['dir'], p['key'], p['n'])]).convert('RGB'); t.thumbnail((320, 180)); im.paste(t, (x0 + 5 + j * 330, y + 20))
                dr.text((x0 + 5 + j * 330, y + 20), p['title'][5:42], fill='red', font=F)
        im.save(f'{W}ps{b // 12}.jpg', quality=80); print(f'{W}ps{b // 12}.jpg')
else:
    for b in range(0, len(ids), 24):
        ss = ids[b:b + 24]; im = Image.new('RGB', (1280, 6 * 255), 'white'); dr = ImageDraw.Draw(im)
        for i, s in enumerate(ss):
            try: t = Image.open(f'{R}public/photos/v-{s[:60]}-640.jpg')
            except Exception: continue
            t.thumbnail((315, 236)); x = (i % 4) * 320; y = (i // 4) * 255
            im.paste(t, (x, y + 16)); dr.text((x, y), f'{b + i} {s[:45]}', fill='black', font=F)
        im.save(f'{W}out{b // 24}.jpg', quality=78); print(f'{W}out{b // 24}.jpg')
