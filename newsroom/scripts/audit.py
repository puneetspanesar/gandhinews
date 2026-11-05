#!/usr/bin/env python3
"""Pre-push gate for Gandhi News. Every run must pass this before `git push`.

Usage (repo root, after `npm run build`):
  python3 newsroom/scripts/audit.py                 all checks, recent content (published/updated in the last 48 h + homepage)
  python3 newsroom/scripts/audit.py --all           lint every story (backlog report; slow, expect old failures)
  python3 newsroom/scripts/audit.py --skip style    skip a group: content, photos, home, site, style (repeatable)
  python3 newsroom/scripts/audit.py --hours 6       what counts as recent
Exit code 0 = pass, 1 = at least one FAIL, 2 = the gate itself could not run (missing dist/, bad JSON...).
Warnings never fail the gate; they are printed so a person can look.

Needs: Python 3.10+, PyYAML, Pillow (optional, for image checks), Playwright + Chromium (for the style group).
"""
import argparse, datetime as dt, glob, hashlib, html, json, os, re, subprocess, sys, threading, http.server, socketserver, functools
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:
    print('audit: PyYAML is required (pip install pyyaml)'); sys.exit(2)

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
NOW = dt.datetime.now(IST)
SITE = 'https://gandhinews.com'
MONTHS = 'January|February|March|April|May|June|July|August|September|October|November|December'
MON3 = 'Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec'
HI_MONTHS = 'जनवरी|फरवरी|फ़रवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|सितम्बर|अक्टूबर|नवंबर|नवम्बर|दिसंबर|दिसम्बर'
# Owner rule 3: month day year. Set to False if the owner decides Hindi keeps the usual "5 नवंबर 2026" order.
HINDI_MONTH_FIRST = False
OUTLETS_EN = ['NDTV', 'PTI', 'ANI', 'IANS', 'UNI', 'Reuters', 'AFP', 'AP', 'Associated Press', 'Bloomberg', 'BBC', 'CNN', 'Al Jazeera',
              'The Hindu', 'Hindustan Times', 'Times of India', 'TOI', 'Indian Express', 'India Today', 'Business Standard', 'Economic Times',
              'Mint', 'LiveMint', 'Moneycontrol', 'News18', 'Republic', 'ETV Bharat', 'Deccan Herald', 'ThePrint', 'The Print', 'Scroll',
              'The Wire', 'LiveLaw', 'Bar and Bench', 'Financial Express', 'Firstpost', 'WION', 'Zee News', 'Aaj Tak', 'DSIJ', 'Upstox',
              'Kotak Neo', 'Goodreturns', 'Trendlyne', '5paisa', 'HDFC Sky', 'ChiniMandi', 'Washington Post', 'New York Times', 'Guardian',
              'Financial Times', 'Wall Street Journal', 'Telegraph', 'Dawn', 'Xinhua', 'TASS', 'Kyodo', 'Yonhap']
OUTLETS_HI = ['एनडीटीवी', 'पीटीआई', 'एएनआई', 'आईएएनएस', 'यूएनआई', 'रॉयटर्स', 'एएफपी', 'ब्लूमबर्ग', 'बीबीसी', 'अल जज़ीरा', 'अल जजीरा',
              'द हिंदू', 'हिंदुस्तान टाइम्स', 'टाइम्स ऑफ इंडिया', 'इंडियन एक्सप्रेस', 'इंडिया टुडे', 'बिजनेस स्टैंडर्ड', 'बिज़नेस स्टैंडर्ड',
              'इकोनॉमिक टाइम्स', 'मनीकंट्रोल', 'न्यूज़18', 'आज तक', 'दैनिक भास्कर', 'अमर उजाला', 'दैनिक जागरण', 'लाइव लॉ', 'ईटीवी भारत']
MARKETS_RE = re.compile(r'(sensex|nifty|wall-street|dow-|nasdaq|ftse|kospi|nikkei|hang-seng|(^|-)oil-|brent|crude-price|markets?(-|$)|-shares?-|stocks?-|'
                        r'rupee-(ends|closes|falls|rises|slips|gains|hits|at|near|weakens|strengthens)|gold-(price|hits|rises|falls|record)|silver-price|'
                        r'bond-yield|ipo-|market-cap|closing-bell|-sales-\d)')
AI_TELLS = [
    (re.compile(r"\b(it|this|that)(?:'|’)s not (?:just |only |about )?[^.;:]{1,60}?[,;]\s*(?:it|this|that)(?:'|’)s\b", re.I), "it's not X, it's Y"),
    (re.compile(r"\bnot (?:just|only|merely) [^.;]{1,60}?, but (?:also )?", re.I), 'not just X, but Y'),
    (re.compile(r"\b(delve|tapestry|in today's fast-paced|a testament to|navigat(?:e|ing) the complexities|in the ever-evolving|it is worth noting that|moreover,)\b", re.I), 'stock AI phrase'),
]
# Traces of the tooling that writes the site. (Not "AI-generated" or "OpenAI": those are legitimate news words.)
TRACE_RE = re.compile(r'\b(Claude|Anthropic|Co-Authored-By|as an AI(?: language)? model|I am an AI)\b', re.I)
CLOCK_EN = re.compile(r'\b(?:by|at|till|until|as of|as at)\s+(\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)', re.I)
CLOCK_HI = re.compile(r'(सुबह|दोपहर|शाम|रात)\s*(\d{1,2})(?::(\d{2}))?\s*बजे')
PLACE_WORDS = re.compile(r'\b(Court|Assembly|Parliament|Capitol|Port|Institute|University|Station|Stadium|House|Bhavan|Bhawan|Ministry|Bank|Exchange|Office|Temple|Airport|Building|Market|River|System|Party|Commission|Council|Police)\b')
FORBIDDEN_ICONS = re.compile(r'\b(robot|sparkle|sparkles|magic-wand|star-four|shooting-star)\b')

# ---------------------------------------------------------------- reporting
FAILS, WARNS = [], []
def fail(group, where, msg): FAILS.append((group, where, msg))
def warn(group, where, msg): WARNS.append((group, where, msg))

# ---------------------------------------------------------------- loading
def split_md(path):
    raw = open(path, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n?(.*)$', raw, re.S)
    if not m: return None, raw, raw
    return m.group(1), m.group(2), raw

def to_ist(v):
    """Frontmatter date -> aware IST datetime, or None. Naive or date-only values are errors the caller reports."""
    if isinstance(v, dt.datetime): return v.astimezone(IST) if v.tzinfo else None
    if isinstance(v, str):
        try: d = dt.datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError: return None
        return d.astimezone(IST) if d.tzinfo else None
    return None

def load_stories(root):
    S = {'en': {}, 'hi': {}}
    for lang in ('en', 'hi'):
        for path in sorted(glob.glob(f'{root}/content/{lang}/*/*.md')):
            folder = path.split('/')[-2]
            fm_txt, body, raw = split_md(path)
            rel = os.path.relpath(path, root)
            if fm_txt is None:
                fail('content', rel, 'no front matter block'); continue
            try: fm = yaml.safe_load(fm_txt) or {}
            except yaml.YAMLError as e:
                fail('content', rel, f'front matter is not valid YAML: {str(e).splitlines()[0]}'); continue
            fm['_path'], fm['_rel'], fm['_body'], fm['_folder'], fm['_raw'] = path, rel, body, folder, raw
            fm['_pub'] = to_ist(fm.get('published')); fm['_upd'] = to_ist(fm.get('updated'))
            S[lang][os.path.basename(path)[:-3]] = fm
    return S

def line_of(raw, needle):
    i = raw.find(needle)
    return raw.count('\n', 0, i) + 1 if i >= 0 else 0

def age_h(fm):
    t = fm.get('_pub')
    return (NOW - t).total_seconds() / 3600 if t else None

def visible_fields(fm):
    """Text a reader sees: title, standfirst, key points, short answer, hero alt/caption, fact-check block, infographic text, body."""
    out = [('title', fm.get('title')), ('standfirst', fm.get('standfirst')), ('shortAnswer', fm.get('shortAnswer')),
           ('seo.description', (fm.get('seo') or {}).get('description'))]
    for i, k in enumerate(fm.get('keyPoints') or []): out.append((f'keyPoints[{i}]', k))
    h = fm.get('hero') or {}
    out += [('hero.alt', h.get('alt')), ('hero.caption', h.get('caption'))]
    for k, v in (fm.get('factcheck') or {}).items(): out.append((f'factcheck.{k}', v))
    ig = fm.get('infographic') or {}
    def walk(x, p):
        if isinstance(x, str): out.append((p, x))
        elif isinstance(x, dict): [walk(v, f'{p}.{k}') for k, v in x.items() if k not in ('icon', 'motif', 'type', 'unit', 'highlight')]
        elif isinstance(x, list): [walk(v, f'{p}[{i}]') for i, v in enumerate(x)]
    walk(ig, 'infographic')
    body = re.sub(r'```(?:chart|facts|timeline|infographic|compare)\n.*?\n```', '', fm.get('_body', ''), flags=re.S)
    out.append(('body', body))
    return [(k, str(v)) for k, v in out if v]

# ---------------------------------------------------------------- A. content lint
DAY_MONTH_EN = re.compile(rf'\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTHS}|{MON3})\.?\b(?:,?\s+(\d{{4}}))?')
NUMERIC_DATE = re.compile(r'\b(\d{1,2})[/.](\d{1,2})[/.](\d{2,4})\b')
DAY_MONTH_HI = re.compile(rf'(?<![\d,.])(\d{{1,2}})\s+({HI_MONTHS})(?:\s+(\d{{4}}))?')
NUM_RE = re.compile(r'(?<![\w.])\d[\d,]*(?:\.\d+)?')
DEV_DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')

def numbers(text):
    out = set()
    for n in NUM_RE.findall(text.translate(DEV_DIGITS)):
        n = n.replace(',', '').rstrip('.')
        try:
            if float(n) >= 10: out.add(n.rstrip('0').rstrip('.') if '.' in n else n)
        except ValueError: pass
    return out

def lint_story(lang, sid, fm, twin):
    rel, raw = fm['_rel'], fm['_raw']
    G = 'content'
    for k in ('id', 'lang', 'type', 'section', 'format_label', 'title', 'standfirst', 'published'):
        if not fm.get(k): fail(G, rel, f'front matter is missing "{k}"')
    if fm.get('id') and fm['id'] != sid: fail(G, rel, f'id "{fm["id"]}" does not match the file name')
    if fm.get('lang') and fm['lang'] != lang: fail(G, rel, f'lang "{fm["lang"]}" but the file is under content/{lang}/')
    if fm.get('published') and not fm['_pub']: fail(G, f'{rel}:{line_of(raw, "published:")}', 'published must be a full time with a UTC offset, e.g. 2026-11-05T15:50:00+05:30')
    if fm.get('updated') and not fm['_upd']: fail(G, f'{rel}:{line_of(raw, "updated:")}', 'updated must be a full time with a UTC offset')
    if fm['_pub'] and fm['_pub'] > NOW + dt.timedelta(minutes=10): fail(G, rel, f'published is in the future ({fm["_pub"]:%Y-%m-%d %H:%M} IST)')
    if fm['_upd'] and fm['_pub'] and fm['_upd'] < fm['_pub']: fail(G, rel, 'updated is earlier than published')
    if not (fm.get('seo') or {}).get('description'): fail(G, rel, 'seo.description is missing')
    vs = (fm.get('verification') or {}).get('status')
    # Hindi twin
    if fm.get('type') in ('news', 'explainer', 'factcheck', 'editorial'):
        if twin is None: fail(G, rel, f'no {"Hindi" if lang == "en" else "English"} twin (content/{"hi" if lang == "en" else "en"}/{fm.get("_folder")}/{sid}.md)')
        elif lang == 'en':
            for k in ('type', 'section'):
                if twin.get(k) != fm.get(k): fail(G, rel, f'Hindi twin has {k} "{twin.get(k)}", English has "{fm.get(k)}"')
            if twin['_pub'] and fm['_pub'] and abs((twin['_pub'] - fm['_pub']).total_seconds()) > 3600: fail(G, rel, 'Hindi twin published time differs by more than an hour')
            en_n = numbers(' '.join(str(x) for x in [fm.get('title'), fm.get('standfirst'), *(fm.get('keyPoints') or [])]))
            hi_n = numbers(' '.join(str(x) for x in [twin.get('title'), twin.get('standfirst'), *(twin.get('keyPoints') or [])]))
            if en_n - hi_n: fail(G, rel, f'numbers in the English title/standfirst/key points missing from the Hindi twin: {", ".join(sorted(en_n - hi_n)[:6])}')
            if hi_n - en_n: fail(G, twin['_rel'], f'numbers in the Hindi twin not in the English: {", ".join(sorted(hi_n - en_n)[:6])}')
            if len(fm.get('keyPoints') or []) != len(twin.get('keyPoints') or []): fail(G, rel, 'English and Hindi have a different number of key points')
    # Visible text rules
    for field, text in visible_fields(fm):
        where = f'{rel}:{line_of(raw, text[:40]) or line_of(raw, field.split(".")[0] + ":")}'
        if '\u2014' in text: fail(G, where, f'em dash in {field}')
        if re.search(r'\d\s*\u2013\s*\d', text): fail(G, where, f'en dash in a number range in {field} (write "to")')
        elif '\u2013' in text: fail(G, where, f'en dash in {field}')
        if field != 'seo.description' or True:
            for m in DAY_MONTH_EN.finditer(text):
                fail(G, where, f'date "{m.group(0)}" in {field}: write month day year ("{m.group(2)} {m.group(1)}{", " + m.group(3) if m.group(3) else ""}")'); break
            for m in NUMERIC_DATE.finditer(text):
                if int(m.group(2)) <= 12 and int(m.group(1)) <= 31: fail(G, where, f'numeric date "{m.group(0)}" in {field}: write it out (November 5, 2026)'); break
            if lang == 'hi' and HINDI_MONTH_FIRST:
                for m in DAY_MONTH_HI.finditer(text):
                    fail(G, where, f'date "{m.group(0)}" in {field}: owner rule is month day year ("{m.group(2)} {m.group(1)}{", " + m.group(3) if m.group(3) else ""}")'); break
        if TRACE_RE.search(text): fail(G, where, f'AI/tool trace "{TRACE_RE.search(text).group(0)}" in {field}')
        if field in ('title', 'standfirst', 'body') or field.startswith('keyPoints'):
            names = OUTLETS_HI if lang == 'hi' else OUTLETS_EN
            for o in names:
                if lang == 'en':
                    pat = rf'\b(?:according to|reported by|citing|told|said to|in an interview (?:with|to)|quoted by|as per|per a report (?:in|by))\s+(?:the\s+)?{re.escape(o)}\b|\b{re.escape(o)}\s+(?:reported|said|quoted|news agency)\b'
                else:
                    pat = rf'{re.escape(o)}\s*(?:के\s*(?:मुताबिक|अनुसार|हवाले)|ने\s*(?:बताया|रिपोर्ट|कहा)|से\s*बातचीत)|(?:मुताबिक|अनुसार)\s*{re.escape(o)}'
                m = re.search(pat, text, re.I)
                if m: fail(G, where, f'outlet cited in the story text ({field}): "{m.group(0)}" (sources belong in the sources list)'); break
            if field == 'body' and re.search(r'^\s*(Sources?|स्रोत)\s*:\s*\[', text, re.M): fail(G, where, 'a "Source:" link line in the body shows outlet names to readers')
        for rx, label in AI_TELLS:
            m = rx.search(text)
            if m: (fail if label == "it's not X, it's Y" else warn)(G, where, f'{label}: "{m.group(0)[:80]}"')
    # Bold rules (news): every key point has a bolded key fact, not the whole point; body has some bold, not whole sentences
    if fm.get('type') == 'news':
        for i, k in enumerate(fm.get('keyPoints') or []):
            k = str(k); b = re.findall(r'\*\*(.+?)\*\*', k)
            if not b: fail(G, f'{rel}:{line_of(raw, k[:30])}', f'key point {i + 1} has no bolded key fact')
            elif sum(len(x) for x in b) > 0.75 * len(k.replace('*', '')): fail(G, f'{rel}:{line_of(raw, k[:30])}', f'key point {i + 1} is almost all bold')
        body = fm.get('_body', '')
        words = len(re.findall(r'\w+', re.sub(r'```.*?```', '', body, flags=re.S)))
        bolds = re.findall(r'\*\*(.+?)\*\*', body)
        if words > 120 and not bolds: fail(G, rel, 'no bold key phrases in the body')
        for b in bolds:
            if len(b.split()) > 14: fail(G, f'{rel}:{line_of(raw, b[:30])}', f'bold runs a whole sentence ("{b[:50]}...")'); break
        if not fm.get('keyPoints'): fail(G, rel, 'news story has no keyPoints')
    # Headline pinned to a clock time (recent stories only)
    when = fm['_upd'] or fm['_pub']
    if when and NOW - when < dt.timedelta(hours=30):
        for field in ('title', 'standfirst'):
            t = str(fm.get(field) or '')
            for m in CLOCK_EN.finditer(t):
                hh = int(m.group(1)) % 12 + (12 if m.group(3).lower().startswith('p') else 0)
                tt = when.replace(hour=hh, minute=int(m.group(2) or 0), second=0, microsecond=0)
                if NOW - tt > dt.timedelta(hours=2): fail(G, rel, f'{field} pins a figure to "{m.group(0)}", now {NOW:%-I:%M %p}: update the figure or move the story off the top')
            for m in CLOCK_HI.finditer(t):
                hh = int(m.group(2)) % 12 + (12 if m.group(1) in ('दोपहर', 'शाम', 'रात') and int(m.group(2)) < 12 else 0)
                tt = when.replace(hour=hh, minute=int(m.group(3) or 0), second=0, microsecond=0)
                if NOW - tt > dt.timedelta(hours=2): fail(G, rel, f'{field} pins a figure to "{m.group(0)}", more than 2 hours ago')
    # Code blocks must be valid JSON; forbidden icons
    for m in re.finditer(r'```(chart|facts|timeline|infographic|compare|photo)\n(.*?)\n```', fm.get('_body', ''), re.S):
        try: json.loads(m.group(2))
        except ValueError as e: fail(G, f'{rel}:{line_of(raw, m.group(2)[:30])}', f'```{m.group(1)} block is not valid JSON: {e}')
        if FORBIDDEN_ICONS.search(m.group(2)): fail(G, rel, f'forbidden icon ({FORBIDDEN_ICONS.search(m.group(2)).group(0)}) in a ```{m.group(1)} block')
    if FORBIDDEN_ICONS.search(json.dumps(fm.get('infographic') or {})): fail(G, rel, 'forbidden icon (robot/sparkle) in the infographic block')
    # Byline is a template constant; a story must not carry a personal byline
    if fm.get('author') or fm.get('byline'): fail(G, rel, 'stories carry no personal byline (From the editorial desk)')

# ---------------------------------------------------------------- B. picture integrity
def file_of(u):
    u = str(u or '').split('?')[0]
    u = re.sub(r'/\d+px-[^/]+$', '', u).replace('/thumb/', '/')
    return re.sub(r'%[0-9A-Fa-f]{2}', lambda m: bytes.fromhex(m.group(0)[1:]).decode('latin-1'), u).split('/')[-1].lower()

def ahash(path):
    try:
        from PIL import Image
        im = Image.open(path).convert('L').resize((16, 16))
        px = list(im.get_flattened_data() if hasattr(im, 'get_flattened_data') else im.getdata()); avg = sum(px) / len(px)
        return int(''.join('1' if p > avg else '0' for p in px), 2)
    except Exception:
        return None

def check_photos(root, S, scope):
    G = 'photos'
    try:
        M = json.load(open(f'{root}/content/photos.map.json')); P = json.load(open(f'{root}/content/photos.json'))
    except (OSError, ValueError) as e:
        fail(G, 'content/photos*.json', f'cannot read: {e}'); return {}
    pub = {sid: fm['_pub'] for sid, fm in S['en'].items() if fm.get('_pub')}
    def need_files(sid, e):
        out = [e.get('src'), e.get('src800')]
        for k in ('cover', 'thumb', 'byLang'):
            for lg in ('en', 'hi'):
                v = (e.get(k) or {}).get(lg) or {}
                out += [v.get('src'), v.get('src800')]
        return [x for x in out if x]
    for sid, fm in S['en'].items():
        if fm.get('type') not in ('news', 'explainer', 'editorial', 'factcheck'): continue
        e = M.get(sid)
        if not e:
            (fail if sid in scope else warn)(G, fm['_rel'], 'no main picture in content/photos.map.json (the article page shows a grey camera box)'); continue
        if sid not in scope: continue
        for f in need_files(sid, e):
            if not os.path.exists(f'{root}/public{f}'): fail(G, f'photos.map.json[{sid}]', f'file {f} does not exist')
        if not str(e.get('alt') or '').strip(): fail(G, f'photos.map.json[{sid}]', 'empty English alt text')
        if not re.search(r'[\u0900-\u097F]', str(e.get('alt_hi') or '')): fail(G, f'photos.map.json[{sid}]', 'Hindi alt text missing or not in Hindi')
        for k in ('alt', 'alt_hi'):
            a = str(e.get(k) or '')
            if '\u2014' in a: fail(G, f'photos.map.json[{sid}]', f'em dash in {k}')
            if DAY_MONTH_EN.search(a): fail(G, f'photos.map.json[{sid}]', f'day-month date in {k}: "{DAY_MONTH_EN.search(a).group(0)}"')
        cr = str(e.get('credit') or '')
        if re.search(r'https?://|www\.', cr): fail(G, f'photos.map.json[{sid}]', f'credit contains a web address: "{cr[:80]}"')
        if re.search(r'licen[cs]e|released under|\{\{|\}\}', cr, re.I): fail(G, f'photos.map.json[{sid}]', f'credit contains licence boilerplate: "{cr[:80]}"')
        if re.search(r'unknown author', cr, re.I): fail(G, f'photos.map.json[{sid}]', 'credit says "Unknown author" (CC BY needs a named author)')
        people = [x for x in ((fm.get('hero') or {}).get('subjects') or []) if re.fullmatch(r'[A-Z][a-z.]+(?: [A-Z][a-z.]+){1,3}', str(x)) and not PLACE_WORDS.search(str(x))]
        if e.get('graphic') and people:
            warn(G, f'photos.map.json[{sid}]', f'infographic used although the story is about {people[:2]} (rule 9: a named person gets a photo)')
        if any(re.search(r'\b(logo|screenshot|stock photo|watermark)\b', str(e.get(k) or ''), re.I) for k in ('alt',)):
            warn(G, f'photos.map.json[{sid}]', f'alt mentions a logo/screenshot: "{e.get("alt")[:80]}"')
    # Reuse within 7 days: same source file, or a near-identical image, across ALL story types
    story_of = lambda aid: re.sub(r'--(p\d+|bg|in|c)$', '', str(aid).replace('part:', '').split(':')[0])
    by_src = defaultdict(set)
    for p in P:
        if str(p.get('articleId', '')).startswith('portrait:') or p.get('composite'): continue
        by_src[file_of(p.get('sourceUrl'))].add(story_of(p.get('articleId')))
    for src, stories in by_src.items():
        ss = sorted(s for s in stories if s in pub)
        for i in range(len(ss)):
            for j in range(i + 1, len(ss)):
                if (ss[i] in scope or ss[j] in scope) and abs((pub[ss[i]] - pub[ss[j]]).total_seconds()) < 7 * 86400:
                    fail(G, src, f'same source photo in {ss[i]} and {ss[j]}, published less than 7 days apart')
    # Near-duplicate images (catches the same picture saved from a different URL or file name)
    hashes = {}
    recent = [s for s in M if story_of(s) in pub and NOW - pub[story_of(s)] < dt.timedelta(days=7)]
    for s in recent:
        f = f'{root}/public{M[s].get("src800") or M[s].get("src")}'
        if M[s].get('graphic') or not os.path.exists(f): continue
        h = ahash(f)
        if h is None: continue
        for s2, h2 in hashes.items():
            if story_of(s2) != story_of(s) and bin(h ^ h2).count('1') <= 6 and (story_of(s) in scope or story_of(s2) in scope):
                fail(G, f'photos.map.json[{s}]', f'looks like the same picture as {s2} (perceptual hash), within 7 days')
        hashes[s] = h
    return M

# ---------------------------------------------------------------- C. homepage (what actually rendered in dist/)
def read(p):
    try: return open(p, encoding='utf-8').read()
    except OSError: return None

def page_ids(htm, lang):
    """Story ids linked inside a block of homepage HTML, in order."""
    pre = '/hi' if lang == 'hi' else ''
    ids = []
    for m in re.finditer(r'<a\b[^>]*\bhref\s*=\s*["\']([^"\']+)["\']', htm, re.I):
        mm = re.match(rf'^{pre}/(?:politics|world|economy|science|sports|states|policy|parliament)/([a-z0-9-]+)/$', m.group(1))
        if mm and mm.group(1) not in ids: ids.append(mm.group(1))
    return ids

def section_block(htm, start_pat):
    m = re.search(start_pat, htm)
    if not m: return ''
    end = htm.find('</section>', m.end())
    return htm[m.start(): end if end > 0 else len(htm)]

def check_home(root, dist, S, M):
    G = 'home'
    for lang in ('en', 'hi'):
        path = f'{dist}/{"hi/" if lang == "hi" else ""}index.html'
        htm = read(path)
        if htm is None: fail(G, path, 'homepage not built'); continue
        st = S[lang]
        L = f'[{lang} homepage]'
        head = section_block(htm, r'<section[^>]*aria-labelledby="hl-h"')
        live = section_block(htm, r'<section[^>]*aria-labelledby="live-h"')
        ids = page_ids(head, lang)
        if not ids: fail(G, L, 'could not find the headline grid'); continue
        lead, tops = ids[0], ids[1:9]
        if len(tops) < 8: fail(G, L, f'only {len(tops)} of 8 headline slots filled')
        live_ids = page_ids(live, lang)
        def fmf(i): return st.get(i) or {}
        # Lead
        a = age_h(fmf(lead))
        if fmf(lead).get('type') != 'news': fail(G, L, f'lead "{lead}" is not a news story')
        if a is None or a > 8: fail(G, L, f'lead "{lead}" is {a and round(a, 1)} hours old (limit 8)')
        if MARKETS_RE.search(lead) or 'markets' in str(fmf(lead).get('format_label', '')).lower(): fail(G, L, f'lead "{lead}" is a markets story')
        # Freshness of everything at the top
        for i in tops + live_ids:
            a = age_h(fmf(i))
            if fmf(i).get('type') == 'news' and (a is None or a > 24): fail(G, L, f'"{i}" at the top is {a and round(a)} hours old (limit 24)')
        # Balance
        mk = [i for i in [lead] + tops if MARKETS_RE.search(i) or 'markets' in str(fmf(i).get('format_label', '')).lower()]
        if len(mk) > 1: fail(G, L, f'{len(mk)} markets stories in the top headlines (max 1): {", ".join(mk)}')
        for sec, n in Counter(fmf(i).get('section') for i in tops).items():
            if n > 2: fail(G, L, f'{n} {sec} stories in the top eight (max 2)')
        stop = {'supreme', 'minister', 'government', 'november', 'october', 'december', 'police', 'india', 'indian', 'explained', 'crore',
                'points', 'percent', 'record', 'series', 'states', 'centre', 'congress', 'after', 'before', 'against'}
        words = lambda i: {w for w in i.split('-') if len(w) >= 5 and w not in stop}
        order = [lead] + tops
        for x, y in zip(order, order[1:]):
            shared = words(x) & words(y)
            tx, ty = set(fmf(x).get('topics') or []), set(fmf(y).get('topics') or [])
            if shared or (tx & ty):
                fail(G, L, f'"{x}" and "{y}" sit next to each other and share a subject ({", ".join(sorted(shared or (tx & ty)))})')
        # Running story takes the lead or one slot: lead's subject must not reappear in the eight
        for i in tops:
            if len(words(lead) & words(i)) >= 2: fail(G, L, f'running story "{lead}" also takes headline slot "{i}"')
        # Same photo twice near the top
        imgs = [re.sub(r'-(640|1280)\.jpg$', '', m) for m in re.findall(r'<img\b[^>]*\bsrc\s*=\s*["\']([^"\']+)', head + live, re.I)]
        for src, n in Counter(imgs).items():
            if n > 1: fail(G, L, f'the same picture appears {n} times at the top: {src}')
        # Grey camera boxes anywhere on the homepage
        n_ph = len(re.findall(r'class="ph[ "]', htm))
        if n_ph: fail(G, L, f'{n_ph} grey camera placeholder(s) on the homepage')
        # Rule 16: data/fact check/trackers/standards come after every news section
        pos = lambda pat: (re.search(pat, htm).start() if re.search(pat, htm) else None)
        news_last = max([p for p in (pos(r'aria-labelledby="in-h"'), pos(r'aria-labelledby="op-h"'), pos(r'aria-label="(?:Sports|खेल)"')) if p] or [0])
        for name, pat in (('trackers', r'aria-labelledby="trk-h"'), ('data desk', r'aria-labelledby="dd-h"'), ('fact check', r'aria-labelledby="fc-h"'), ('standards', r'class="std2"')):
            p = pos(pat)
            if p is None: warn(G, L, f'{name} band not found')
            elif p < news_last: fail(G, L, f'{name} band sits above news sections (rule 16)')
        # Masthead date must be today in IST, month first
        md = re.search(r'class="mh-date">([^<]+)<', htm)
        if md:
            txt = html.unescape(md.group(1))
            if lang == 'en' and not re.search(rf'({MONTHS}) {NOW.day}\b', txt): fail(G, L, f'masthead date "{txt}" is not today written month first ({NOW:%B} {NOW.day})')
            if lang == 'hi' and HINDI_MONTH_FIRST and not re.search(rf'({HI_MONTHS}) {NOW.day}\b', txt): fail(G, L, f'masthead date "{txt}" is not month first')
    # Markets band
    mk = read(f'{root}/content/data/markets.json')
    try: mk = json.loads(mk or '')
    except ValueError: fail(G, 'content/data/markets.json', 'not valid JSON'); mk = {}
    asof = to_ist(mk.get('as_of')) if mk else None
    if mk and not asof: fail(G, 'content/data/markets.json', f'as_of "{mk.get("as_of")}" is missing or has no UTC offset')
    if asof:
        trading = NOW.weekday() < 5 and str(NOW.date()) not in set(mk.get('holidays', []))
        open_ = trading and dt.time(9, 15) <= NOW.time() <= dt.time(15, 30)
        if open_:
            if mk.get('status') != 'open': warn(G, 'markets.json', f'market hours but status is "{mk.get("status")}"')
            if NOW - asof > dt.timedelta(hours=2): fail(G, 'markets.json', f'market is open and the band is {round((NOW - asof).total_seconds() / 3600, 1)} hours old (limit 2)')
        elif trading and NOW.time() > dt.time(16, 30):
            if mk.get('session_date') != str(NOW.date()) or asof.time() < dt.time(15, 30) or mk.get('status') != 'closed':
                fail(G, 'markets.json', f'after the close the band must carry today\'s closing figures (session_date {mk.get("session_date")}, as_of {asof:%H:%M}, status {mk.get("status")})')
    # The homepage must change every run: compare with what is on origin/main
    try:
        old = subprocess.run(['git', '-C', root, 'show', 'origin/main:content/homepage.json'], capture_output=True, text=True, timeout=20)
        if old.returncode == 0:
            cur = json.load(open(f'{root}/content/homepage.json')); prev = json.loads(old.stdout)
            key = lambda h: json.dumps([h.get('lead', {}).get('id'), h.get('lead', {}).get('relatedBeside'), h.get('topStories'), h.get('lead', {}).get('relatedBelow')])
            if key(cur) == key(prev) and 6 <= NOW.hour <= 23: fail(G, 'content/homepage.json', 'top of the homepage is identical to the live one (the site must visibly change every run)')
    except Exception as e:
        warn(G, 'content/homepage.json', f'could not compare with origin/main: {e}')

# ---------------------------------------------------------------- D. built-site crawl
ATTR = re.compile(r'\b(href|src|content|srcset|data-src)\s*=\s*("([^"]*)"|\'([^\']*)\')', re.I)
# Case-sensitive on purpose: "Nan Excella" and "null and void" are real words; NaN/undefined/null are template leaks.
JUNK = re.compile(r'\b(undefined|NaN|Infinity)\b|\[object Object\]|&nbsp;|&amp;(?:nbsp|amp|quot|#\d+);|\{\{|\}\}|\bnull\b(?! and void)|\bTODO\b|[Ll]orem ipsum|\bleft null\b')
def visible_text(htm):
    t = re.sub(r'<(script|style|svg|noscript|template)\b.*?</\1>', ' ', htm, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', t)

def check_site(root, dist, recent_paths):
    G = 'site'
    AGG = defaultdict(list)   # the same template problem on many pages is reported once, with a count
    def agg(key, rel): AGG[key].append(rel)
    pages = sorted(glob.glob(f'{dist}/**/*.html', recursive=True))
    if not pages: fail(G, dist, 'no HTML in dist/ (run npm run build first)'); return
    exists = functools.lru_cache(maxsize=None)(lambda p: os.path.exists(p))
    def target(u):
        u = html.unescape(u).split('#')[0].split('?')[0]
        if u.startswith(SITE): u = u[len(SITE):] or '/'
        if not u.startswith('/') or u.startswith('//'): return None
        p = f'{dist}{u}'
        return p + 'index.html' if u.endswith('/') else (p + '/index.html' if os.path.isdir(p) else p)
    seen_bad = set(); counts = Counter()
    for path in pages:
        rel = '/' + os.path.relpath(path, dist).replace('index.html', '')
        htm = read(path) or ''
        is_recent = rel in recent_paths or rel in ('/', '/hi/')
        lang = 'hi' if rel.startswith('/hi/') else 'en'
        # links and assets (double/single quotes, any case, absolute own-domain URLs included)
        for m in ATTR.finditer(htm):
            name, val = m.group(1).lower(), m.group(3) if m.group(3) is not None else m.group(4)
            vals = [v.strip().split()[0] for v in val.split(',') if v.strip()] if name == 'srcset' else [val]
            for v in vals:
                if name == 'content' and not v.startswith(SITE): continue
                if name in ('href', 'src') and (v == '' or v in ('undefined', 'null', '#undefined')):
                    fail(G, rel, f'{name}="{v}"'); continue
                t = target(v)
                if t and not exists(t) and (rel, v) not in seen_bad:
                    seen_bad.add((rel, v)); fail(G, rel, f'{name} -> {v} does not exist')
        for m in re.finditer(r'url\(\s*["\']?(/[^)"\']+)', htm):
            t = target(m.group(1))
            if t and not exists(t): fail(G, rel, f'CSS url({m.group(1)}) does not exist')
        if rel.startswith('/pagefind/'): continue
        # head metadata
        if not re.search(r'<title>[^<]{3,}</title>', htm): fail(G, rel, 'missing <title>')
        if not re.search(r'<meta name="description" content="[^"]{20,}"', htm) and '404' not in rel: fail(G, rel, 'missing or short meta description')
        can = re.search(r'<link rel="canonical" href="([^"]+)"', htm)
        if can and can.group(1) != SITE + rel and not rel.startswith('/404'): fail(G, rel, f'canonical {can.group(1)} is not this page')
        hl = re.search(r'<html lang="([a-z]+)"', htm)
        if hl and hl.group(1) != lang: fail(G, rel, f'<html lang="{hl.group(1)}"> on a {lang} page')
        for m in re.finditer(r'<link rel="alternate" hreflang="([a-zA-Z-]+)" href="([^"]+)"', htm):
            t = target(m.group(2))
            if t and not exists(t): fail(G, rel, f'hreflang {m.group(1)} points at a missing page {m.group(2)}')
        # JSON-LD
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', htm, re.S):
            try: d = json.loads(m.group(1))
            except ValueError as e: fail(G, rel, f'JSON-LD does not parse: {e}'); continue
            for item in (d if isinstance(d, list) else [d]):
                if isinstance(item, dict) and 'NewsArticle' in str(item.get('@type')):
                    if len(str(item.get('headline', ''))) > 110: fail(G, rel, 'NewsArticle headline over 110 characters')
                    if not re.search(r'[+-]\d\d:\d\d$|Z$', str(item.get('datePublished', ''))): fail(G, rel, 'NewsArticle datePublished without a timezone')
        # images: alt attribute present
        for m in re.finditer(r'<img\b([^>]*)>', htm, re.I):
            if not re.search(r'\balt\s*=', m.group(1), re.I): fail(G, rel, f'<img> without alt: {m.group(1)[:80]}')
        # visible text
        text = visible_text(htm)
        for m in JUNK.finditer(text):
            counts[m.group(0)] += 1
            if is_recent or counts[m.group(0)] <= 3: fail(G, rel, f'junk text "{m.group(0)}" ... {text[max(0, m.start() - 40):m.end() + 30]!r}')
        if '\u2014' in text: fail(G, rel, f'em dash on the page: {text[max(0, text.find(chr(0x2014)) - 40):text.find(chr(0x2014)) + 20]!r}')
        if is_recent:
            if re.search(r'<!--[^>]*\bTODO\b', htm): agg('a TODO comment ships in the public HTML', rel)
            if TRACE_RE.search(text): fail(G, rel, f'AI/tool trace on the page: "{TRACE_RE.search(text).group(0)}"')
            for m in re.finditer(r'<time[^>]*>([^<]+)</time>|class="mh-date">([^<]+)<', htm):
                t = html.unescape(m.group(1) or m.group(2))
                if (lang == 'en' and DAY_MONTH_EN.search(t)) or (lang == 'hi' and HINDI_MONTH_FIRST and DAY_MONTH_HI.search(t)):
                    agg(f'UI dates are day-month, owner wants month day year (e.g. "{re.sub(r"[0-9]+", "N", t)[:40]}")', rel); break
            n_ph = len(re.findall(r'class="ph[ "]', htm))
            if n_ph: fail(G, rel, f'{n_ph} grey camera placeholder(s)')
    if counts: warn(G, 'dist', f'junk text totals across the site: {dict(counts)}')
    for key, rels in AGG.items(): fail(G, f'{len(rels)} pages', f'{key}; e.g. {", ".join(rels[:3])}')

# ---------------------------------------------------------------- E. computed styles on the built homepage
STYLE_JS = r"""
() => {
  const out = [];
  const grey = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const [r,g,b,a=1] = m[1].split(',').map(Number);
    const neutral = Math.max(r,g,b) - Math.min(r,g,b) <= 14; const avg = (r+g+b)/3;
    return { r, g, b, a, isGrey: neutral && avg > 24 && avg < 235, translucent: a < 0.999 }; };
  const okFont = (f) => /^\s*["']?(Google Sans|Inter|Noto Sans Devanagari)["']?\s*(,|$)/i.test(f);
  const seen = new Set(); const sizes = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const n = walker.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || seen.has(el)) continue; seen.add(el);
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (el.closest('.sr-only,[hidden],[aria-hidden="true"] svg,.ck,.so')) continue;
    const label = (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : el.tagName.toLowerCase()) + ': "' + n.textContent.trim().slice(0, 40) + '"';
    const g = grey(cs.color);
    if (g && (g.isGrey || g.translucent)) out.push(['grey', `${cs.color} ${label}`]);
    let op = 1; for (let e = el; e; e = e.parentElement) op *= parseFloat(getComputedStyle(e).opacity);
    if (op < 0.999) out.push(['opacity', `opacity ${op.toFixed(2)} ${label}`]);
    if (!okFont(cs.fontFamily)) out.push(['font', `${cs.fontFamily.slice(0, 50)} ${label}`]);
    sizes.add(cs.fontSize);
    if (parseFloat(cs.fontSize) < 12) out.push(['small', `${cs.fontSize} ${label}`]);
    // pills: short text in a rounded box with a fill or border
    const rad = parseFloat(cs.borderTopLeftRadius) || 0;
    const filled = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(cs.borderTopWidth) > 0;
    if (rad >= 6 && filled && n.textContent.trim().length < 40 && r.height < 48) out.push(['pill', `radius ${cs.borderTopLeftRadius} ${label}`]);
  }
  document.querySelectorAll('body *').forEach((el) => {
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    const lab = (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').join('.') : el.tagName.toLowerCase()).slice(0, 60);
    if (/gradient/.test(cs.backgroundImage)) out.push(['gradient', lab]);
    if (cs.boxShadow !== 'none' && !/inset/.test(cs.boxShadow) && el !== document.activeElement) out.push(['shadow', `${cs.boxShadow.slice(0, 40)} ${lab}`]);
    if (cs.textShadow !== 'none') out.push(['shadow', `text-shadow ${lab}`]);
    if (el.matches('.ph')) out.push(['camera', lab]);
    if (el.tagName === 'IMG' && !(el.complete && el.naturalWidth > 0)) out.push(['broken-img', el.getAttribute('src')]);
  });
  out.push(['sizes', [...sizes].sort().join(' ')]);
  // At least one face of each brand font must have actually loaded (a missing file silently falls back to system-ui).
  const loaded = new Set([...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family.replace(/["']/g, '')));
  const missing = ['Google Sans', 'Inter'].filter((f) => !loaded.has(f));
  if (missing.length) out.push(['font-load', 'no face loaded for: ' + missing.join(', ')]);
  return out;
}
"""

class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def check_style(dist):
    G = 'style'
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        fail(G, 'playwright', 'Playwright is not installed: the style checks could not run (pip install playwright && playwright install chromium)'); return
    handler = functools.partial(_Quiet, directory=dist)
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), handler)   # port 0: never collides with a parallel run
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for path, w in (('/', 1440), ('/', 390), ('/hi/', 1440), ('/hi/', 390)):
                pg = b.new_page(viewport={'width': w, 'height': 900})
                pg.goto(f'http://127.0.0.1:{port}{path}', wait_until='networkidle')
                for y in range(0, 20000, 800): pg.evaluate(f'window.scrollTo(0,{y})'); pg.wait_for_timeout(40)
                pg.wait_for_timeout(600)
                res = pg.evaluate(STYLE_JS)
                L = f'[{path} {w}px]'
                by = defaultdict(list)
                for kind, msg in res: by[kind].append(msg)
                for kind in ('grey', 'opacity', 'font', 'pill', 'gradient', 'shadow', 'camera', 'broken-img', 'font-load', 'small'):
                    items = by.get(kind, [])
                    if items:
                        uniq = list(dict.fromkeys(items))
                        (warn if kind == 'small' else fail)(G, L, f'{kind}: {len(uniq)} element(s), e.g. ' + ' | '.join(uniq[:4]))
                sizes = (by.get('sizes') or [''])[0].split()
                if len(sizes) > 9: warn(G, L, f'{len(sizes)} different font sizes on the page (owner wants a small type scale): {" ".join(sizes)}')
                pg.close()
            b.close()
    finally:
        srv.shutdown()

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.'); ap.add_argument('--dist', default=None)
    ap.add_argument('--hours', type=float, default=48); ap.add_argument('--all', action='store_true')
    ap.add_argument('--changed', action='store_true', help='lint only stories this run changed (git diff against origin/main) + the homepage')
    ap.add_argument('--skip', action='append', default=[], help='groups to skip, comma separated: content,photos,home,site,style')
    ap.add_argument('--max', type=int, default=60, help='failures printed per group')
    a = ap.parse_args()
    root = os.path.abspath(a.root); dist = os.path.abspath(a.dist or f'{root}/dist')
    if not os.path.isdir(f'{root}/content'): print(f'audit: {root} is not the repo root (no content/)'); sys.exit(2)
    S = load_stories(root)
    try: H = json.load(open(f'{root}/content/homepage.json'))
    except (OSError, ValueError) as e: print(f'audit: content/homepage.json unreadable: {e}'); sys.exit(2)
    def ids_in(x):
        if isinstance(x, str): return [x] if x in S['en'] else []
        if isinstance(x, list): return [i for y in x for i in ids_in(y)]
        if isinstance(x, dict): return [i for v in x.values() for i in ids_in(v)]
        return []
    on_home = set(ids_in(H))
    recent = {sid for sid, fm in S['en'].items() if a.all or any(t and NOW - t < dt.timedelta(hours=a.hours) for t in (fm['_pub'], fm['_upd']))}
    if a.changed:
        d = subprocess.run(['git', '-C', root, 'diff', '--name-only', 'origin/main', '--', 'content/en', 'content/hi'], capture_output=True, text=True)
        u = subprocess.run(['git', '-C', root, 'ls-files', '--others', '--exclude-standard', 'content/en', 'content/hi'], capture_output=True, text=True)
        if d.returncode != 0: print(f'audit: --changed needs git and origin/main: {d.stderr.strip()}'); sys.exit(2)
        recent = {os.path.basename(f)[:-3] for f in (d.stdout + u.stdout).split() if f.endswith('.md')}
    scope = recent | on_home
    for lang in ('en', 'hi'):
        for sid in on_home:
            if sid not in S[lang]: fail('content', 'content/homepage.json', f'homepage id "{sid}" has no {lang} story file')
    a.skip = [g.strip() for x in a.skip for g in x.split(',') if g.strip()]
    assert set(a.skip) <= {'content', 'photos', 'home', 'site', 'style'}, f'unknown --skip group: {a.skip}'
    if 'content' not in a.skip:
        for lang in ('en', 'hi'):
            other = S['hi' if lang == 'en' else 'en']
            for sid, fm in S[lang].items():
                if sid in scope or (lang == 'hi' and sid not in S['en'] and (a.all or (fm['_pub'] and NOW - fm['_pub'] < dt.timedelta(hours=a.hours)))):
                    lint_story(lang, sid, fm, other.get(sid))
    M = check_photos(root, S, scope) if 'photos' not in a.skip else {}
    built = os.path.exists(f'{dist}/index.html')
    if not built and not set(a.skip) >= {'home', 'site', 'style'}: print(f'audit: {dist}/index.html not found: run npm run build first'); sys.exit(2)
    if 'home' not in a.skip: check_home(root, dist, S, M)
    if 'site' not in a.skip:
        rp = set()
        for sid in scope:
            fm = S['en'].get(sid) or {}
            if fm.get('section') and fm.get('type') in ('news', 'explainer', 'factcheck', 'editorial'):
                rp |= {f'/{fm["section"]}/{sid}/', f'/hi/{fm["section"]}/{sid}/'}
        check_site(root, dist, rp)
    if 'style' not in a.skip: check_style(dist)
    # report
    by = defaultdict(list)
    for g, w, m in FAILS: by[g].append((w, m))
    for g in ('content', 'photos', 'home', 'site', 'style'):
        if g in a.skip: print(f'--  {g}: skipped'); continue
        items = list(dict.fromkeys(by.get(g, [])))
        print(f'{"FAIL" if items else "ok  "} {g}: {len(items)} problem(s)')
        for w, m in items[:a.max]: print(f'       {w}: {m}')
        if len(items) > a.max: print(f'       ... and {len(items) - a.max} more')
    if WARNS:
        print(f'warnings ({len(WARNS)}, do not block):')
        for g, w, m in list(dict.fromkeys(WARNS))[:40]: print(f'       [{g}] {w}: {m}')
    print(f'scope: {len(scope)} stories ({"all" if a.all else "changed since origin/main + homepage" if a.changed else f"last {a.hours:g} h + homepage"}), checked at {NOW:%B %-d, %Y %-I:%M %p} IST')
    sys.exit(1 if FAILS else 0)

if __name__ == '__main__':
    main()
