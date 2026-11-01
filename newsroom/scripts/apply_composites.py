"""Build composite story pictures from downloaded parts and register them in photos.map.json."""
import json, sys, os
sys.path.insert(0, '/home/claude/gn-work')
from compose import compose
from PIL import Image
raw = sys.argv[1]
FOCUS = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
os.chdir('/home/claude/gandhinews')
P = json.load(open('content/photos.json')); M = json.load(open('content/photos.map.json'))
def pid_of(a):
    for suf in ('--bg', '--in', '--c'):
        if a.endswith(suf): return 'v-' + a[:-len(suf)][:55] + '-' + suf[2:]
    return 'v-' + (a[:60] if '--p' not in a else a.rsplit('--p', 1)[0][:55] + '-p' + a.rsplit('--p', 1)[1])
def entry(p, pid):
    return {'id': pid, 'src': f'/photos/{pid}-1280.jpg', 'src800': f'/photos/{pid}-640.jpg', 'width': 1280, 'height': 960,
            'credit': p['credit'], 'licence': p['licence'], 'alt': p['alt'], 'alt_hi': p.get('alt_hi'), 'page': None}
for p in P:
    if not p.get('composite'): continue
    # Self-heal: a picture already built whose map entry was lost (e.g. overwritten by a parallel run) is re-added.
    if p['articleId'] not in M and os.path.exists(f"public/photos/{pid_of(p['articleId'])}-1280.jpg"):
        M[p['articleId']] = entry(p, pid_of(p['articleId'])); print('re-added', p['articleId'])
    parts = [f"{raw}/{i}.jpg" for i in p['composite']]
    if not all(os.path.exists(x) for x in parts): print('missing parts', p['articleId']); continue
    try:
        [Image.open(x).verify() for x in parts]
    except Exception:
        print('bad part', p['articleId']); continue
    a = p['articleId']
    # in-story photos '<story>--p<n>' keep their suffix so long slugs never collide
    pid = pid_of(a)
    f = FOCUS.get(p['articleId'])
    if isinstance(f, dict): compose(parts, f'public/photos/{pid}', f.get('focus'), f.get('weights'))
    else: compose(parts, f'public/photos/{pid}', f)
    M[p['articleId']] = {'id': pid, 'src': f'/photos/{pid}-1280.jpg', 'src800': f'/photos/{pid}-640.jpg', 'width': 1280, 'height': 960,
                         'credit': p['credit'], 'licence': p['licence'], 'alt': p['alt'], 'alt_hi': p.get('alt_hi'), 'page': None}
    print('ok', p['articleId'])
json.dump(M, open('content/photos.map.json', 'w'), indent=1, ensure_ascii=False)
