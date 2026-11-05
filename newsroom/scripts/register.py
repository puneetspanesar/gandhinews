"""Add photos.json entries (parts + composite main entry) for every story in picks.json.
Empty/None panels are dropped. Alt text: the story's own hero.alt (EN) and Hindi twin hero.alt when the
final panels match the planned subjects; otherwise /home/claude/gn-work/alts-override.json must give
{"story-id": ["English alt", "Hindi alt"]}. Stops and lists ids that still need alt text."""
import os as _gn_os; GN_ROOT = _gn_os.environ.get('GN_ROOT') or _gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.abspath(__file__)))) + '/'  # repo root (works in any clone)
import json, os, sys, yaml
R = GN_ROOT + ''; W = (_gn_os.environ.get('GN_WORK') or '/home/claude/gn-work/')
picks = json.load(open(W + 'picks.json')); plan = json.load(open(W + 'plan.json'))
over = json.load(open(W + 'alts-override.json')) if os.path.exists(W + 'alts-override.json') else {}
import re
BLOCK = re.compile(r"```photo\s*\n(.*?)\n```", re.S)
def inline_alt(lang, s):
    """Alt text of in-story photo "<story>--p<n>" from that language's ```photo block."""
    sid, n = s.rsplit('--p', 1)
    for t in ['news', 'explainer', 'editorial']:
        p = f'{R}content/{lang}/{t}/{sid}.md'
        if not os.path.exists(p): continue
        for m in BLOCK.finditer(open(p).read()):
            try: d = json.loads(m.group(1))
            except Exception: continue
            if str(d.get('n')) == n: return d.get('alt')
    return None
def fm(lang, s):
    for t in ['news', 'explainer', 'editorial']:
        p = f'{R}content/{lang}/{t}/{s}.md'
        if os.path.exists(p): return yaml.safe_load(open(p).read().split('---')[1]) or {}
    return {}
P = json.load(open(R + 'content/photos.json')); ids = {p['id'] for p in P}; have = {p['articleId'] for p in P}
need = []; todo = []
for s, v in picks.items():
    v = [x for x in v if x]
    if not v or s in have: continue
    if s in over: en, hi = over[s]
    elif s.endswith('--bg') or s.endswith('--in') or s.endswith('--c'):
        en, hi = v[0]['what'], v[0]['what']   # cover background or inset: shown only inside the cover
    elif '--p' in s and [x['q'] for x in v] == [p['q'] for p in plan[s]['panels']]:
        en = inline_alt('en', s); hi = inline_alt('hi', s)
        if not en or not hi: need.append(s); continue
    elif [x['q'] for x in v] == [p['q'] for p in plan[s]['panels']]:
        en = (fm('en', s).get('hero') or {}).get('alt'); hi = (fm('hi', s).get('hero') or {}).get('alt')
        if not en or not hi: need.append(s); continue
    else: need.append(s); continue
    todo.append((s, v, en, hi))
if need:
    print('NEED alt text in alts-override.json for:'); [print(' ', s, [x['what'] for x in picks[s] if x]) for s in need]; sys.exit(1)
fp = lambda e, h: (e if '(file' in e else e + ' (file photo)', h if ('फ़ाइल' in h or 'फाइल' in h) else h + ' (फ़ाइल फ़ोटो)')
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); from gnrules import clean_credit
au = lambda p: clean_credit((p.get('author') or 'Unknown').strip().replace('Unknown authorUnknown author', 'Unknown author')) or 'Wikimedia Commons contributor'
for s, v, en, hi in todo:
    en, hi = fp(en, hi); parts = []
    for i, p in enumerate(v):
        pid = f'cx-{s[:57]}-{i}'
        while pid in ids: pid += 'b'
        P.append(dict(id=pid, articleId=f'part:{s}:{i}', sourceUrl=p['url'], credit=au(p), licence=p['licence'], alt='', page=p['page']))
        parts.append(pid); ids.add(pid)
    mid = f'x-{s[:60]}'
    while mid in ids: mid += 'b'
    ids.add(mid)
    P.append(dict(id=mid, articleId=s, sourceUrl=v[0]['url'],
                  credit=('Photo: ' if len(v) == 1 else 'Photos: ') + '; '.join(f'{au(p)} / Wikimedia Commons' for p in v),
                  licence=', '.join(dict.fromkeys(p['licence'] for p in v)), alt=en, alt_hi=hi, page=v[0]['page'], composite=parts))
json.dump(P, open(R + 'content/photos.json', 'w'), ensure_ascii=False, indent=1)
print('registered', len(todo))
