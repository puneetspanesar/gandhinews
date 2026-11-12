"""Held stories (newsroom/held/{en,hi}/<id>.md + newsroom/held/<id>.json with why/kind/held_at).
  python3 newsroom/scripts/held.py list                       every hold, its age and why
  python3 newsroom/scripts/held.py hold <id> <picture|facts|other> "<why>"   take a story off the site (both languages)
  python3 newsroom/scripts/held.py republish <id>             put it back (only once the reason is fixed: a picture hold
                                                              needs its main picture in content/photos.map.json)
  python3 newsroom/scripts/held.py drop <id> "<why>"          delete a hold now (overtaken by events, or we have since published the same news)
  python3 newsroom/scripts/held.py expire                     delete facts and other holds older than 24 hours and picture holds older than 48 hours (picture holds are worth fixing for two days: the story still belongs in its section and archive)
Every run does `list` and `expire` at the start, and republishes picture holds whose picture now exists.
"""
import json, os, sys, glob, shutil, subprocess, datetime as dt
GN_ROOT = os.environ.get('GN_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
os.chdir(GN_ROOT)
IST = dt.timezone(dt.timedelta(hours=5, minutes=30)); now = dt.datetime.now(IST)
H = 'newsroom/held'
def mv(a, b):
    os.makedirs(os.path.dirname(b), exist_ok=True)
    tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', a], capture_output=True).returncode == 0
    subprocess.run(['git', 'mv', '-f', a, b], check=True) if tracked else shutil.move(a, b)
def info(i):
    try: d = json.load(open(f'{H}/{i}.json'))
    except (OSError, ValueError): d = {'why': '?', 'kind': 'other', 'held_at': dt.datetime.fromtimestamp(os.path.getmtime(f'{H}/en/{i}.md'), IST).isoformat()}
    t = dt.datetime.fromisoformat(d['held_at'])
    d['held_at'] = (t if t.tzinfo else t.replace(tzinfo=IST)).isoformat()
    return d
import hashlib
def pic_print(i):
    """Fingerprint of the story's current main picture file (ids get reused, files do not lie)."""
    e = json.load(open('content/photos.map.json')).get(i) or {}
    try: return hashlib.sha1(open('public' + e['src'], 'rb').read()).hexdigest()[:16]
    except (KeyError, OSError): return None
def fixed_picture(i, d):
    """A picture hold is fixed only by a DIFFERENT main picture than the one it was held with."""
    now_ = pic_print(i)
    if not now_: return False
    if d.get('picture_print'): return now_ != d['picture_print']
    e = json.load(open('content/photos.map.json')).get(i) or {}
    return e.get('id') != d.get('picture_at_hold')
cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
if cmd == 'list':
    ids = sorted(os.path.basename(f)[:-3] for f in glob.glob(f'{H}/en/*.md'))
    for i in ids:
        d = info(i); age = (now - dt.datetime.fromisoformat(d['held_at'])).total_seconds() / 3600
        print(f"{i} | {d['kind']} | {age:.1f}h | {d['why']}" + (' | a new picture exists: republish' if d['kind'] == 'picture' and fixed_picture(i, d) else ''))
    print(f'{len(ids)} held')
elif cmd == 'hold':
    i, kind, why = sys.argv[2], sys.argv[3], sys.argv[4]
    if kind not in ('picture', 'facts', 'other'): sys.exit(f'kind must be picture, facts or other, not {kind}')
    if not glob.glob(f'content/en/*/{i}.md'): sys.exit(f'{i}: no such published story (check the id); nothing held')
    os.makedirs(f'{H}/en', exist_ok=True); os.makedirs(f'{H}/hi', exist_ok=True)
    pic = json.load(open('content/photos.map.json')).get(i) or {}
    n = 0
    for lang in ('en', 'hi'):
        for f in glob.glob(f'content/{lang}/*/{i}.md'):
            mv(f, f'{H}/{lang}/{i}.md'); n += 1
            open(f'{H}/{i}.type', 'w').write(f.split('/')[2])
    json.dump({'why': why, 'kind': kind, 'held_at': now.isoformat(timespec='minutes'), 'picture_at_hold': pic.get('id'), 'picture_print': pic_print(i)}, open(f'{H}/{i}.json', 'w'), ensure_ascii=False)
    home = open('content/homepage.json').read()
    if f'"{i}"' in home: print(f'  {i} is on the homepage: run refresh_home.py, then check_fresh.py (it fails on any id still pointing at it)')
    print(f'held {i} ({n} files): {why}')
elif cmd == 'republish':
    i = sys.argv[2]
    if not os.path.exists(f'{H}/en/{i}.md'): sys.exit(f'{i}: not held')
    d = info(i)
    if d['kind'] == 'picture' and not fixed_picture(i, d): sys.exit(f'{i}: still no new main picture (it was held with {d.get("picture_at_hold")})')
    if d['kind'] != 'picture' and '--fixed' not in sys.argv: sys.exit(f'{i}: held for {d["kind"]} ({d["why"]}); republish only with --fixed after fixing it and a new editor PASS')
    typ = open(f'{H}/{i}.type').read().strip() if os.path.exists(f'{H}/{i}.type') else 'news'
    for lang in ('en', 'hi'): mv(f'{H}/{lang}/{i}.md', f'content/{lang}/{typ}/{i}.md')
    for x in ('json', 'type'):
        p = f'{H}/{i}.{x}'
        if os.path.exists(p): subprocess.run(['git', 'rm', '-q', '-f', p], capture_output=True); os.path.exists(p) and os.remove(p)
    print(f'republished {i}: set its published time to now if the news is still current')
elif cmd == 'expire':
    for f in glob.glob(f'{H}/en/*.md'):
        i = os.path.basename(f)[:-3]; d = info(i)
        # a facts or other hold is news going stale: a day. A picture hold is worth two (owner, November 12: holds were piling up)
        if (now - dt.datetime.fromisoformat(d['held_at'])).total_seconds() > (48 if d.get('kind') == 'picture' else 24) * 3600:
            for p in [f'{H}/en/{i}.md', f'{H}/hi/{i}.md', f'{H}/{i}.json', f'{H}/{i}.type']:
                if os.path.exists(p): subprocess.run(['git', 'rm', '-q', '-f', p], capture_output=True); os.path.exists(p) and os.remove(p)
            print(f'expired {i}')
elif cmd == 'drop':
    i = sys.argv[2]
    for p in [f'{H}/en/{i}.md', f'{H}/hi/{i}.md', f'{H}/{i}.json', f'{H}/{i}.type']:
        if os.path.exists(p): subprocess.run(['git', 'rm', '-q', '-f', p], capture_output=True); os.path.exists(p) and os.remove(p)
    print(f'dropped {i}: {" ".join(sys.argv[3:])}')
else: sys.exit(__doc__)
