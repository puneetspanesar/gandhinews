"""Gandhi News photo treatment (owner, November 9): a magazine-style collage cover in the house colours.

Built only from photos we already hold under licence (content/photos.map.json); nothing is generated.

  paper-beige ground with a fine grain
  2 or 3 RELATED photos from our own library (the place, the institution, the scene: Parliament, a polling booth,
  the state assembly, a market, a stadium), toned to the house red and set as overlapping tiles, some with torn edges
  a red arch behind the subject, thin-line chart marks, a line grid, a dot grid and small red squares
  the subject cut out (rembg) and set in front, bottom-anchored

Never a second copy of the subject; never a portrait of anyone else.
An infographic story gets a cover too: the named person's solo library photo cut out, or, failing that, a collage of
3-4 related scene photos (the main one in natural colour). Its story page keeps the infographic. Credits of every photo used are joined.
A story photo with no clear subject to cut out (a place, a crowd, an object) is set whole as the main tile.

Writes public/photos/t-<id>-1280.jpg and -640.jpg and sets "treated" on the story's photos.map.json entry.
Usage (repo root): python3 newsroom/scripts/treat_photo.py <story-id> [...]   |   --missing [hours]  (every story, default last 72 hours)
"""
import hashlib, json, os, random, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
os.chdir(R)
W, H = 1280, 800
PAPER, RED, INK = (240, 233, 221), (204, 0, 0), (13, 13, 13)
_session = None
_DF = None
_DF = None

SCENE = re.compile(r'building|court|Parliament|Sansad|Sadan|assembly|Vidhan|legislat|station|market|mandi|field|crowd|voters|'
                   r'polling|booth|ballot|EVM|farmers|temple|river|road|skyline|stadium|ground|pitch|port|ship|harbour|train|railway|'
                   r'aircraft|plane|airport|office|headquarters|bank|exchange|Dalal|protest|rally|police|soldiers|troops|army|border|'
                   r'smog|rain|flood|factory|plant|refinery|mine|hospital|school|university|campus|bridge|highway|metro|bus|boats|crop|'
                   r'paddy|wheat|forest|hills|mountain|snow|sea|beach|city|street|traffic|monument|fort|palace|Bhavan|Bhawan|Block|'
                   r'secretariat|Raisina|chamber|ministry|cricket|tennis|courtroom|vessel|warship|submarine|fishermen|village|'
                   r'storm|cyclone|fire|houses|homes|ward|queue', re.I)
STOP = set('the a an of in on at to for and with from by as is was are be his her their its new old india indian file photo photos '
           'during after before into over under near says said will first one two three this that than more most who what when'.split())
NAME = re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b')
PLACEWORDS = re.compile(r'House|Court|Sadan|Bhavan|Bhawan|Block|Building|Assembly|Station|Market|Street|Road|Bank|Exchange|Office|'
                        r'Ministry|Commission|Parliament|Secretariat|Stadium|Ground|Port|Airport|Fort|Palace|Temple|River|Hill|Gate|'
                        r'Chowk|Mantar|Sabha|Legislat|University|Hospital|India|Pradesh|Nadu|Bengal|Delhi|Mumbai|Kolkata|Chennai|'
                        r'Bengaluru|Hyderabad|Lucknow|Punjab|Kerala|Karnataka|Gujarat|Rajasthan|Bihar|Odisha|Assam|Haryana|Sikkim|'
                        r'Jharkhand|Telangana|Maharashtra|Andhra|Uttar|Madhya|Himachal|Jammu|Kashmir|Ladakh|Goa|Manipur|Tripura|'
                        r'Meghalaya|Mizoram|Nagaland|Arunachal|Uttarakhand|Chhattisgarh|Washington|London|Paris|Tokyo|Beijing|Moscow|'
                        r'Reserve|State|National|Supreme|High|United|Nations|Lok|Rajya|Election|North|South|Raj|Rashtrapati|Jantar')


def fm(sid):
    import yaml
    f = R + f'content/en/news/{sid}.md'
    if not os.path.exists(f): return {}
    try: return yaml.safe_load(open(f).read().split('---')[1]) or {}
    except Exception: return {}


def words(t):
    return {w for w in re.findall(r"[A-Za-z][A-Za-z\-]{2,}", t or '') if w.lower() not in STOP}


def people(alt):
    """Personal names in an alt text (two capitalised words that are not a place or an institution)."""
    return {n for n in NAME.findall(alt or '') if not PLACEWORDS.search(n)}


# topic buckets: (words in the story, words in a library photo's alt that show that topic)
BUCKETS = [
    (r'elect|voter|poll|ballot|\bSIR\b|EVM|Election Commission|by-?poll|panchayat|parishad', r'polling|voters|ballot|EVM|Election Commission|Nirvachan|booth|electoral|enumeration'),
    (r'Parliament|Lok Sabha|Rajya Sabha|\bbill\b|session|MPs\b', r'Parliament|Lok Sabha|Rajya Sabha|Samvidhan'),
    (r'court|verdict|judge|bench|petition|\bSC\b|\bHC\b|bail|hearing', r'Supreme Court|High Court|court'),
    (r'army|troops|soldier|defen[cs]e|navy|air force|jawan|BSF|CRPF|border|Rajnath|military', r'soldiers|troops|\barmy\b|Indian Navy|warship|\bINS\b|submarine|\bBSF\b|jawans|Air Force|fighter jet|\btanks? on'),
    (r'Naxal|Maoist|insurg|terror|security review|internal security|police', r'CRPF|security forces|Bastar|Dantewada|Sukma|jungle'),
    (r'climate|COP\d*|emission|pollution|AQI|smog|GRAP|heat|monsoon|flood|cyclone|rain', r'smog|pollution|climate|emission|solar|wind|flood|rain|cyclone|haze|skyline'),
    (r'Sensex|Nifty|market|shares|stock|investor|SEBI|IPO', r'Stock Exchange|BSE|NSE|Dalal|exchange'),
    (r'RBI|rupee|inflation|repo\b|repo rate|banks?\b|banking|forex|GDP|fiscal|Budget|tax\b|taxes|GST', r'Reserve Bank|bank|North Block|Finance Ministry|currency|rupee'),
    (r'farm|crop|paddy|wheat|kharif|rabi|MSP|drought|mandi|agricultur', r'farmers|field|crop|paddy|wheat|mandi|harvest|tractor'),
    (r'rail|train|Vande|station', r'railway|train|station|Vande'),
    (r'flight|airline|IndiGo|Air India|airport|aviation|DGCA', r'aircraft|airport|plane|airline|terminal'),
    (r'cricket|\bT20\b|\bODI\b|Test match|IPL|wicket|innings', r'cricket|stadium|pitch'),
    (r'tennis|ATP|WTA', r'tennis'),
    (r'hockey|football|kabaddi|chess|badminton|athlet|Olympic', r'stadium|ground|arena|hall'),
    (r'fires?\b|blaze|gutted', r'fire\b|blaze|firefighters|fire tender|flames'),
    (r'earthquake|quake|tremor|landslide|collapse', r'earthquake|rubble|collapsed|rescue|landslide'),
    (r'Test|ODI|India A|innings|wicket|runs\b', r'cricket|stadium|pitch'),
    (r'hospital|health|doctor|medical|AIIMS|vaccine|disease', r'hospital|AIIMS|medical|clinic'),
    (r'school|exam|student|university|NEET|JEE|CBSE|UGC', r'school|university|campus|students|exam'),
    (r'fishermen|fishing|boat|sea|coast|port', r'fishermen|boats|harbour|port|coast|sea'),
    (r'Iran|Israel|Gaza|Gulf|Middle East|Saudi|Qatar|Hormuz', r'Iran|Tehran|Israel|Gaza|Gulf|Hormuz|Middle East|Saudi|Qatar'),
    (r'United States|\bUS\b|Washington|White House|Trump|Rubio', r'White House|Washington|Capitol|United States'),
    (r'United Nations|\bUN\b|summit|G20|BRICS|COP', r'United Nations|summit|conference|delegates|flags'),
]


def related(sid, M, n=3, strict=False):
    """The best 2-3 scene photos from our own library for this story: same topic, same place, never a portrait."""
    d = fm(sid); e = M[sid]
    text = ' '.join(str(d.get(k) or '') for k in ('title', 'standfirst', 'format_label'))
    loc = str(d.get('location') or '')
    state = None
    for part in [x.strip() for x in loc.split(',')][::-1]:
        st = ALIAS.get(part, part)
        if st in STATES and st != 'Delhi': state = st; break   # a Delhi dateline is national news
    want = [arx for srx, arx in BUCKETS if re.search(rf'\b(?:{srx})', text, re.I)]
    _t = str(d.get('title') or '')
    HEADP = {w for w in re.findall(r'\b[A-Z][A-Za-z]{2,}\b', _t) if w.lower() not in STOP}
    HEADP -= {'Diwali', 'Deepavali', 'India', 'Indian', 'New', 'First', 'Nation', 'Day', 'Year', 'November', 'October', 'December',
              'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'} | {PEOPLE[k]['en'].split()[-1] for k in PEOPLE}
    own = os.path.basename(e['src']).split('-1280')[0]
    cands = []
    for k, x in M.items():
        if k == sid or x.get('graphic') or not x.get('src') or not x.get('alt') or k.startswith('x-'): continue
        alt = x['alt']
        if people(alt) or os.path.basename(x['src']).split('-1280')[0] == own: continue   # places and scenes only
        if PERSONISH.search(alt): continue
        if d.get('section') != 'world' and FOREIGN.search(alt): continue                              # no foreign scenes on Indian stories
        if d.get('section') == 'world' and (re.search(r'\bIndia|Indian\b', alt) or any(c in alt for c in list(ALIAS) + list(STATES))): continue   # no Indian scenes on world stories
        if state and any(st in alt for st in STATES if st != state) and state not in alt: continue   # another state's scene
        if state and any(c in alt for c, st in ALIAS.items() if st != state and c not in ('New Delhi',)) and state not in alt: continue
        place = 1 if state and (state in alt or any(c in alt for c, st in ALIAS.items() if st == state)) else 0
        ap = set(re.findall(r'\b[A-Z][A-Za-z]{2,}\b', alt))
        if not (ap & HEADP) and not place: continue           # must share a proper noun (place, body, event) with the headline
        topic = sum(1 for arx in want if re.search(rf'\b(?:{arx})', alt, re.I))
        if topic == 0: continue                               # and show the story's subject matter
        cands.append((topic * 3 + place * 2 - min(USED.get(k, 0), 4) * 1.2, k, alt))   # spread the library: a much-used photo drops
    cands.sort(key=lambda t: (-t[0], t[1]))
    out, seenalt = [], set()
    for sc, k, alt in cands:
        caps = set(re.findall(r'[A-Z][a-z]+', alt)) | {w.lower() for w in words(alt)}
        if any(len(caps & c) / max(1, len(caps | c)) > .34 for c in seenalt) or not os.path.exists('public' + M[k]['src']): continue
        seenalt.add(frozenset(caps)); out.append(k)
        if len(out) >= n: break
    return out


ALIAS = {'New Delhi': 'Delhi', 'Mumbai': 'Maharashtra', 'Bengaluru': 'Karnataka', 'Kolkata': 'West Bengal', 'Chennai': 'Tamil Nadu',
         'Hyderabad': 'Telangana', 'Lucknow': 'Uttar Pradesh', 'Srinagar': 'Jammu and Kashmir', 'Patna': 'Bihar', 'Bhopal': 'Madhya Pradesh',
         'Jaipur': 'Rajasthan', 'Raipur': 'Chhattisgarh', 'Ranchi': 'Jharkhand', 'Bhubaneswar': 'Odisha', 'Thiruvananthapuram': 'Kerala',
         'Guwahati': 'Assam', 'Dehradun': 'Uttarakhand', 'Shimla': 'Himachal Pradesh', 'Amaravati': 'Andhra Pradesh', 'Gandhinagar': 'Gujarat',
         'Ahmedabad': 'Gujarat', 'Chandigarh': 'Punjab', 'Gangtok': 'Sikkim', 'Imphal': 'Manipur', 'Panaji': 'Goa', 'Nagpur': 'Maharashtra',
         'Varanasi': 'Uttar Pradesh', 'Ayodhya': 'Uttar Pradesh'}
FOREIGN = re.compile(r'Kenya|Taiwan|China|Chinese|Pakistan|Bangladesh|Nepal|Sri Lanka|United States|\bUS\b|American|Oklahoma|Texas|'
                     r'Washington|London|British|UK\b|France|French|Paris|Germany|German|Russia|Russian|Ukrain|Japan|Tokyo|Korea|Australia|'
                     r'Canada|Brazil|Iran|Israel|Gaza|Saudi|Qatar|Dubai|Turkey|Türkiye|Africa|Europe|Italy|Spain|Afghan|Myanmar')
STATES = set(ALIAS.values()) | {'Punjab', 'Haryana', 'Bihar', 'Kerala', 'Assam', 'Odisha', 'Goa', 'Tripura', 'Meghalaya', 'Mizoram',
                                 'Nagaland', 'Arunachal Pradesh', 'Telangana', 'Andhra Pradesh', 'Tamil Nadu', 'Karnataka'}


def generic(sid, M, have, n):
    """Section stand-ins when the story has too few related photos: the institution the section is about."""
    sec = fm(sid).get('section', '')
    want = {'politics': r'Parliament|Election Commission|polling|Vidhan', 'policy': r'North Block|South Block|Parliament|secretariat',
            'parliament': r'Parliament|Lok Sabha|Rajya Sabha', 'states': r'assembly|Vidhan|secretariat|Bhavan',
            'economy': r'Reserve Bank|Stock Exchange|BSE|Dalal|market|port', 'world': r'United Nations|headquarters|flag|summit',
            'sports': r'stadium|ground|pitch|court', 'science': r'laboratory|ISRO|rocket|launch|campus'}.get(sec, r'Parliament')
    out = [k for k, x in sorted(M.items()) if k not in have and not x.get('graphic') and x.get('alt') and not people(x['alt'])
           and re.search(want, x['alt'], re.I) and os.path.exists('public' + x['src'])]
    random.Random(sid).shuffle(out)
    return out[:n]


PEOPLE = json.load(open(R + 'newsroom/library/people.json'))
PERSONISH = re.compile(r'\b(Justice|Dr|Mr|Mrs|Ms|Shri|Smt|minister|leader|chief|CM|MP|MLA|chairman|chairperson|CEO|president|woman|man|girl|boy|portrait|speaks|speaking|addresses|addressing|actor|player|batter|bowler|captain|coach)\b', re.I)
USED = {}   # how often each library photo already sits in a collage (filled in main)


SURNAME = None


def named_people(text):
    """Library people named in a text, in order of mention: full name, alias, or a surname only one person has."""
    global SURNAME
    if SURNAME is None:
        c = {}
        for k, v in PEOPLE.items():
            sn = v['en'].split()[-1]
            if len(sn) >= 4: c.setdefault(sn, []).append(k)
        SURNAME = {sn: ks[0] for sn, ks in c.items() if len(ks) == 1}
    hits = {}
    for k, v in PEOPLE.items():
        for nm in [v['en']] + list(v.get('aliases') or []):
            i = (text or '').find(nm)
            if i >= 0: hits[k] = min(hits.get(k, 1 << 30), i)
    for sn, k in SURNAME.items():
        m = re.search(rf"\b{re.escape(sn)}\b", text or '')
        if m: hits[k] = min(hits.get(k, 1 << 30), m.start())
    return [k for k, _ in sorted(hits.items(), key=lambda t: t[1])]


def library_portrait(pk):
    """Download (once, as a Wikimedia thumbnail) the first licensed photo of a library person: (path, credit) or None."""
    import urllib.request, io, time
    ph = (PEOPLE[pk].get('photos') or [None])[0]
    if not ph or not ph.get('url'): return None
    path = f'public/photos/lib-{pk}-1280.jpg'
    if not os.path.exists(path):
        u = ph['url'].split('?')[0]
        m = re.match(r'https://upload\.wikimedia\.org/wikipedia/commons/(\w)/(\w\w)/([^/]+)$', u)
        if m and (ph.get('width') or 0) > 1280 and not u.lower().endswith(('.svg', '.tif', '.tiff')):
            u = f'https://upload.wikimedia.org/wikipedia/commons/thumb/{m[1]}/{m[2]}/{m[3]}/1280px-{m[3]}'
        time.sleep(1.5)
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'GandhiNewsDesk/1.0 (https://gandhinews.com)'})
            im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=40).read())).convert('RGB')
            im.thumbnail((1280, 1600)); im.save(path, quality=88)
        except Exception as ex:
            print(f'  library photo for {pk} not downloaded: {ex}'); return None
    return path, f"{(ph.get('author') or 'Wikimedia Commons').strip()} / Wikimedia Commons, {ph.get('licence', '')}".strip(', ')


def portrait(sid, M):
    """The headline's first-named person, alone: a solo photo we already hold, else the library portrait. (path, credit)."""
    d = fm(sid); title = str(d.get('title') or ''); full = title + ' ' + str(d.get('standfirst') or '')
    for pk in named_people(title)[:1]:
        # a surname alone is not enough: the person's full name must be in the headline or the standfirst
        # (Tata Steel is not Ratan Tata, Prism Johnson is not Mike Johnson, Azam Khan is not Babar Azam)
        if not any(nm in full for nm in [PEOPLE[pk]['en']] + list(PEOPLE[pk].get('aliases') or [])): return None
        name = PEOPLE[pk]['en']; best = None
        for mk, x in M.items():
            alt = x.get('alt') or ''
            if mk == sid or x.get('graphic') or mk.startswith('x-') or not x.get('src'): continue
            if os.path.basename(x['src']).startswith(('v-', 't-', 'c-', 'i')): continue
            if name not in alt or named_people(alt) != [pk] or re.search(r'\band\b|\bwith\b|calls on|meets|photos\)', alt): continue
            if not os.path.exists('public' + x['src']): continue
            w = x.get('srcWidth') or x.get('width') or 0
            if best is None or w > best[0]: best = (w, mk)
        if best: return 'public' + M[best[1]]['src'], M[best[1]].get('credit', '').replace('Photo: ', '')
        return library_portrait(pk)
    return None


def cutout(im):
    global _session
    from rembg import new_session, remove
    if _session is None: _session = new_session('isnet-general-use')
    out = remove(im, session=_session, post_process_mask=True)
    return out, np.asarray(out.split()[-1]).astype(np.float32) / 255


def grain(img, amt=6, seed=0):
    n = np.random.default_rng(seed).normal(0, amt, (img.height, img.width, 1))
    return Image.fromarray(np.clip(np.asarray(img).astype(np.float32) + n, 0, 255).astype(np.uint8))


def torn_mask(w, h, rnd, rough=9, sides='tblr'):
    m = Image.new('L', (w, h), 0); pts = []; step = 12
    j = lambda side: rnd.uniform(0, rough) if side in sides else 0
    for x in range(0, w + 1, step): pts.append((x, j('t')))
    for y in range(0, h + 1, step): pts.append((w - j('r'), y))
    for x in range(w, -1, -step): pts.append((x, h - j('b')))
    for y in range(h, -1, -step): pts.append((j('l'), y))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(.7))


def tone(im):
    """House tritone: ink shadows, brand-red mid-tones, paper highlights."""
    g = ImageOps.autocontrast(im.convert('L'), cutoff=1)
    t = ImageOps.colorize(g, black=(28, 18, 18), mid=(178, 70, 62), white=(244, 234, 224), midpoint=110)
    return Image.blend(t, ImageOps.colorize(g, (28, 24, 22), (244, 236, 226)), .35)


def cover_fit(im, w, h, cx=.5, cy=.42):
    s = max(w / im.width, h / im.height)
    r = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    l = int((r.width - w) * cx); t = int((r.height - h) * cy)
    return r.crop((l, t, l + w, t + h))


def tile(path, w, h, rnd, toned=True, sides='tblr'):
    im = cover_fit(Image.open(path).convert('RGB'), w, h)
    im = (tone(im) if toned else im).convert('RGBA')
    im.putalpha(torn_mask(w, h, rnd, 8, sides))
    return im


def dots(w, h, color=INK, gap=16, r=1.7):
    t = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    for y in range(2, h, gap):
        for x in range(2, w, gap): d.ellipse((x - r, y - r, x + r, y + r), fill=color + (255,))
    return t


def bars(w, h, rnd):
    t = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    n = 5; bw = w // (n * 2); hi = rnd.randrange(n)
    for i in range(n):
        bh = int(h * (.3 + .7 * (i + 1) / n * rnd.uniform(.75, 1))); x = i * bw * 2
        d.rectangle((x, h - bh, x + bw, h - 1), fill=RED + (255,) if i == hi else None, outline=INK + (255,), width=2)
    d.line((0, h - 1, w, h - 1), fill=INK + (255,), width=2)
    return t


def grid(w, h, gap=22):
    t = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    for x in range(0, w + 1, gap): d.line((x, 0, x, h), fill=INK + (90,), width=1)
    for y in range(0, h + 1, gap): d.line((0, y, w, y), fill=INK + (90,), width=1)
    return t


def arch(w, h, color=RED):
    t = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    d.rectangle((0, w // 2, w, h), fill=color + (255,)); d.ellipse((0, 0, w, w), fill=color + (255,))
    return t


def treat(sid, M):
    e = M[sid]
    # the subject: the story's own photo, unless it is an infographic or a cover of one person twice; then the headline
    # person's solo photo (ours or the library's); otherwise a collage of clearly related scenes
    alt0 = e.get('alt', '')
    single = (e.get('src') or '').split('/')[-1].startswith('v-') and len(named_people(alt0)) <= 1 and not re.search(r'\band\b|\bwith\b', alt0)
    if not e.get('graphic') and not single:
        subj_path, subj_credit, src_key = 'public' + e['src'], e.get('credit', '').replace('Photos: ', '').replace('Photo: ', ''), sid
    else:
        pr = portrait(sid, M)
        subj_path, subj_credit = pr if pr else (None, None)
        src_key = 'portrait' if pr else None
    main_scene = None
    if src_key is None:
        main_scene = related(sid, M, 4, strict=True)
        if len(main_scene) < 3: return None, False, []
    orig = Image.open(subj_path).convert('RGB') if subj_path else None
    rnd = random.Random(int(hashlib.md5(sid.encode()).hexdigest()[:8], 16))
    flip = rnd.random() < .5
    X = (lambda x, w: W - x - w) if flip else (lambda x, w: x)      # mirror a box when the subject sits on the right
    can = grain(Image.new('RGB', (W, H), PAPER), 6, rnd.randrange(1 << 30)).convert('RGBA')

    if main_scene:
        rel = main_scene[1:]; centre = main_scene[0]
    else:
        rel = related(sid, M, 3)   # only tiles that clearly belong to this story; none is better than a wrong one
        centre = None
    paths = ['public' + M[k]['src'] for k in rel]

    a0 = alt0 if src_key == sid else 'portrait'
    is_person = src_key == 'portrait' or bool(named_people(a0) or people(a0) or PERSONISH.search(a0))
    if src_key == sid and (len(named_people(a0)) > 2 or re.search(r'\b(group|team|members|delegation|crowd|officials|medallists|contingent|personnel|soldiers|troops)\b', a0, re.I)):
        is_person = False                                  # a group never cuts out cleanly: show the photo whole
    if orig is not None and is_person:
        cut, a = cutout(orig)
        ok = .05 < a.mean() < .7 and a[-int(a.shape[0] * .2):].mean() > .04
        if ok and a[:max(2, int(a.shape[0] * .03))].mean() > .03: ok = False   # head cut by the photo's top edge: show it whole
        ew = max(2, int(a.shape[1] * .02))
        if ok and (a[:, :ew].mean() > .12 or a[:, -ew:].mean() > .12): ok = False   # someone sliced by the side edge: show it whole
        if ok:
            from scipy import ndimage
            lab, n = ndimage.label(a > .5)
            big = sum(1 for sz in ndimage.sum(a > .5, lab, range(1, n + 1)) if sz > a.size * .03)
            if big > 2: ok = False                                                  # a group: show the photo whole
    else:
        ok = False
    if src_key == 'portrait' and not ok: return None, False, []

    can.alpha_composite(grid(220, 154), (X(36, 220), 40))
    can.alpha_composite(dots(176, 112), (X(W - 220, 176), H - 150))
    boxes = [(560, 60, 640, 420, 'tbr'), (40, 300, 380, 280, 'tblr'), (900, 440, 300, 220, 'tlr')]
    if not ok: boxes = [(30, 90, 330, 240, 'tblr'), (920, 470, 330, 250, 'tblr'), (60, 470, 280, 210, 'tlr')]
    for p, (x, y, w, h, sd) in zip(paths, boxes):
        can.alpha_composite(tile(p, w, h, rnd, True, sd), (X(x, w), y))
    can.alpha_composite(bars(120, 90, rnd), (X(1130, 120), 28) if not flip else (30, 28))
    for (x, y, s) in [(410, 270, 26), (1180, 680, 18)]:
        can.alpha_composite(Image.new('RGBA', (s, s), RED + (255,)), (X(x, s), y))

    cxs = int(W * (.42 if not flip else .58))
    if ok:
        cut = cut.crop(cut.getbbox())
        s = min(H * .82 / cut.height, W * .42 / cut.width)
        if cut.height < cut.width * 1.25: s = min(s, H * .62 / cut.height)   # a tight head crop: keep the face a sane size
        cut = cut.resize((round(cut.width * s), round(cut.height * s)), Image.LANCZOS)
        aw = int(min(max(cut.width * .78, 300), 460)); ah = int(H * .7)
        can.alpha_composite(arch(aw, ah), (cxs - aw // 2, H - ah))
        rim = Image.new('RGBA', cut.size, (250, 246, 238, 255)); rim.putalpha(cut.split()[-1].filter(ImageFilter.MaxFilter(7)))
        x0 = cxs - cut.width // 2; y0 = H - cut.height
        can.alpha_composite(rim, (x0, y0)); can.alpha_composite(cut, (x0, y0))
    else:
        cw, ch = 700, 470
        tx = (W - cw) // 2 + (40 if not flip else -40)
        aw, ah = 280, 220     # a red dome rising from behind the top edge of the main photo
        can.alpha_composite(arch(aw, ah), ((tx + cw - aw - 70) if not flip else (tx + 70), 160 - 120))
        main = 'public' + (M[centre]['src'] if centre else e['src'])
        can.alpha_composite(tile(main, cw, ch, rnd, False, 'tblr'), ((W - cw) // 2 + (40 if not flip else -40), 160))

    out = can.convert('RGB')
    pid = 't-' + sid[:60]
    out.save(f'public/photos/{pid}-1280.jpg', quality=86, optimize=True)
    out.resize((640, 400), Image.LANCZOS).save(f'public/photos/{pid}-640.jpg', quality=84, optimize=True)
    credits = [subj_credit] if subj_credit else []
    for k in ([centre] if centre else []) + rel:
        for c in M[k].get('credit', '').replace('Photos: ', '').replace('Photo: ', '').split('; '):
            if c and c not in credits: credits.append(c)
    e['treated'] = {'src': f'/photos/{pid}-1280.jpg', 'src800': f'/photos/{pid}-640.jpg', 'cutout': bool(ok), 'with': ([centre] if centre else []) + rel,
                    'kind': 'photo' if src_key == sid else 'portrait' if src_key else 'scenes',
                    'credit': ('Photos: ' if len(credits) > 1 else 'Photo: ') + '; '.join(credits)}
    return pid, ok, rel


if __name__ == '__main__':
    M = json.load(open('content/photos.map.json'))
    ids = sys.argv[1:]
    if ids and ids[0] == '--missing':
        hours = int(ids[1]) if len(ids) > 1 else 72
        import glob, datetime as D
        cut = (D.datetime.now(D.timezone.utc) - D.timedelta(hours=hours)).isoformat()[:16]
        ids = []
        for f in glob.glob('content/en/news/*.md'):
            sid = os.path.basename(f)[:-3]; e = M.get(sid)
            if not e or (e.get('treated') and os.path.exists('public' + e['treated']['src'])): continue
            m = re.search(r'^published: (\S+)', open(f).read(600), re.M)
            if m and str(m.group(1)) >= cut: ids.append(sid)
    for x in M.values():
        for k in (x.get('treated') or {}).get('with', []): USED[k] = USED.get(k, 0) + 1
    for sid in ids:
        e = M.get(sid)
        if not e: print(f'{sid}: no photo entry, skipped'); continue
        pid, ok, rel = treat(sid, M)
        if pid is None: e.pop('treated', None); print(f'{sid}: nothing suitable to build a cover from'); continue
        for k in rel: USED[k] = USED.get(k, 0) + 1
        print(f'{sid}: {pid} ({"cut-out" if ok else "scene"}; with {", ".join(rel) or "nothing"})')
    json.dump(M, open('content/photos.map.json', 'w'), ensure_ascii=False, indent=1)
