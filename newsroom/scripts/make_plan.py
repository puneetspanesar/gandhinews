"""Build the picture plan for every story that has no photo yet.
Reads hero.subjects / hero.suggested_source from each story's front matter, and every in-story
```photo block (planned as "<story id>--p<n>", a single panel).
Writes /home/claude/gn-work/plan.json, vq.json and scripts/photo-queries-<tag><n>.json (about 45 queries each).
Usage: python3 make_plan.py <tag>      e.g. tag 'a' -> parts a0, a1, a2 ...
Prints the part names to pass to find-photos.yml."""
import json, os, re, sys, glob, yaml
R = '/home/claude/gandhinews/'; W = '/home/claude/gn-work/'
tag = sys.argv[1] if len(sys.argv) > 1 else 'a'
M = json.load(open(R + 'content/photos.map.json'))
have = set(M) | {p['articleId'] for p in json.load(open(R + 'content/photos.json'))}
PLACE = re.compile(r'\b(court|park|place|stadium|station|airport|port|building|headquarters|office|hq|exchange|club|ground|bhawan|bhavan|sadan|palace|temple|city|district|river|strait|crossing|base|campus|university|college|hospital|market|dam|lake|fort|gate|mall|tower|towers|centre|center|street|road|bridge|kremlin|square|secretariat|assembly|parliament|house|airbase|ground|island|valley|hills|town|village|nagar|chowk|maidan|ghat|museum|mosque|church|refinery|plant|factory|mine|port)\b|,', re.I)
def fm(p):
    t = open(p).read().split('---')
    return yaml.safe_load(t[1]) if len(t) > 2 else {}
BLOCK = re.compile(r"```photo\s*\n(.*?)\n```", re.S)
def inline_photos(p):
    """In-story ```photo blocks: [(n, subject)]."""
    out = []
    for m in BLOCK.finditer(open(p).read()):
        try: d = json.loads(m.group(1))
        except Exception: print('bad photo block in', os.path.basename(p)); continue
        if d.get('n') and d.get('subject'): out.append((int(d['n']), d['subject']))
    return out
plan = {}
for p in sorted(glob.glob(R + 'content/en/news/*.md') + glob.glob(R + 'content/en/explainer/*.md') + glob.glob(R + 'content/en/editorial/*.md')):
    sid = os.path.basename(p)[:-3]
    for n, q in inline_photos(p):
        if f'{sid}--p{n}' not in have:
            plan[f'{sid}--p{n}'] = {'layout': 'single', 'panels': [{'q': q, 'what': q, 'kind': 'place' if PLACE.search(q) else 'person'}]}
    d0 = fm(p); cv = d0.get('cover') or {}
    for suf, key in (('bg', 'bg'), ('in', 'inset')):
        q = cv.get(key)
        if q and f'{sid}--{suf}' not in have:
            plan[f'{sid}--{suf}'] = {'layout': 'single', 'panels': [{'q': q, 'what': q, 'kind': 'place'}]}
    if cv.get('people') and f'{sid}--c' not in have:   # cover people when the main picture is a place
        ps = cv['people'][:2]
        plan[f'{sid}--c'] = {'layout': 'split' if len(ps) > 1 else 'single', 'panels': [{'q': q, 'what': q, 'kind': 'person'} for q in ps]}
    if sid in have: continue
    d = d0; h = d.get('hero') or {}
    subj = [s for s in (h.get('subjects') or []) if s][:2] or ([h['suggested_source']] if h.get('suggested_source') else [])
    if not subj: continue
    panels = [{'q': s, 'what': s, 'kind': 'place' if PLACE.search(s) else 'person'} for s in subj]
    ss = h.get('suggested_source')
    if ss and ss not in subj: panels[0]['alts'] = [ss]
    plan[sid] = {'layout': 'split' if len(panels) > 1 else 'single', 'panels': panels}
qs = []
for v in plan.values():
    for pn in v['panels']:
        for q in [pn['q']] + pn.get('alts', []):
            if q not in qs: qs.append(q)
vq = {}; files = {}
for i, q in enumerate(qs):
    part = f'{tag}{i // 45}'; k = f'{tag}q{i}'
    vq[k] = q
    files.setdefault(part, {})[k] = q + ('||10' if PLACE.search(q) else '||12')
json.dump(plan, open(W + 'plan.json', 'w'), indent=1, ensure_ascii=False)
json.dump(vq, open(W + 'vq.json', 'w'), indent=1, ensure_ascii=False)
for part, d in files.items():
    json.dump(d, open(f'{R}scripts/photo-queries-{part}.json', 'w'), indent=0, ensure_ascii=False)
print(len(plan), 'stories,', len(qs), 'queries; parts:', ' '.join(files))
