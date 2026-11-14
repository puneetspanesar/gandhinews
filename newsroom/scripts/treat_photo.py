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
import glob, hashlib, json, os, random, re, sys
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
    f = next((R + f'content/en/{t}/{sid}.md' for t in ('news', 'explainer', 'editorial', 'factcheck') if os.path.exists(R + f'content/en/{t}/{sid}.md')), None)
    if not f: return {}
    try: return yaml.safe_load(open(f).read().split('---')[1]) or {}
    except Exception: return {}


def words(t):
    return {w for w in re.findall(r"[A-Za-z][A-Za-z\-]{2,}", t or '') if w.lower() not in STOP}


def people(alt):
    """Personal names in an alt text (two capitalised words that are not a place or an institution)."""
    out = set()
    for n in NAME.findall(alt or ''):
        if PLACEWORDS.search(n) or n.split()[0] in ('The', 'A', 'An', 'In', 'At'): continue
        if re.search(re.escape(n) + r"(?:'s)?\s+(?:Nagar|district|Road|Marg|Chowk|Ghar|Market|Bhawan|Bhavan|Hall|Stadium|clock|tower|House|Gate|Park|Airport|station|Bridge|Ground)", alt, re.I): continue
        out.add(n)
    return out


# topic buckets: (words in the story, words in a library photo's alt that show that topic)
BUCKETS = [
    (r'elect|voter|poll|ballot|\bSIR\b|EVM|Election Commission|by-?poll|panchayat|parishad', r'polling|voters|ballot|EVM|Election Commission|Nirvachan|booth|electoral|enumeration'),
    (r'Parliament|Lok Sabha|Rajya Sabha|\bbill\b|session|MPs\b', r'Parliament|Lok Sabha|Rajya Sabha|Samvidhan'),
    (r'court|verdict|judge|bench|petition|\bSC\b|\bHC\b|bail|hearing', r'Supreme Court|High Court|court'),
    (r'army|troops|soldier|defen[cs]e|navy|air force|jawan|BSF|CRPF|border|Rajnath|military', r'soldiers|troops|\barmy\b|Indian Navy|warship|\bINS\b|submarine|\bBSF\b|jawans|Air Force|fighter jet|\btanks? on'),
    (r'Naxal|Maoist|insurg|terror|security review|internal security', r'CRPF|security forces|Bastar|Dantewada|Sukma|jungle'),
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
    text = re.sub(r'\b(?:Monsoon|Winter|Budget) [Ss]ession', 'Parliament session', ' '.join(str(d.get(k) or '') for k in ('title', 'standfirst', 'format_label')))   # the Monsoon Session is Parliament, not rain
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
        if k == sid or x.get('graphic') or x.get('notile') or not x.get('src') or not x.get('alt') or k.startswith('x-'): continue
        alt = x['alt']
        if people(alt) or os.path.basename(x['src']).split('-1280')[0] == own: continue   # places and scenes only
        if PERSONISH.search(alt): continue
        if d.get('section') != 'world' and FOREIGN.search(alt): continue                              # no foreign scenes on Indian stories
        if FOREIGN.search(alt) and not any(re.search(COUNTRY[c][1], alt) for c in country_of(text)): continue   # only the story's own country
        if (d.get('section') == 'world' or abroad_story(d)) and (re.search(INDIAN_RX, alt) or any(c in alt for c in list(ALIAS) + list(STATES))): continue   # no Indian scenes on world stories
        if state and any(st in alt for st in STATES if st not in (state, 'Delhi')) and state not in alt: continue   # another state's scene
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
        if any(same_pic('public' + M[k]['src'], 'public' + M[o]['src']) for o in out): continue
        seenalt.add(frozenset(caps)); out.append(k)
        if len(out) >= n: break
    return out


ALIAS = {'New Delhi': 'Delhi', 'Mumbai': 'Maharashtra', 'Bengaluru': 'Karnataka', 'Kolkata': 'West Bengal', 'Chennai': 'Tamil Nadu',
         'Hyderabad': 'Telangana', 'Lucknow': 'Uttar Pradesh', 'Srinagar': 'Jammu and Kashmir', 'Patna': 'Bihar', 'Bhopal': 'Madhya Pradesh',
         'Jaipur': 'Rajasthan', 'Raipur': 'Chhattisgarh', 'Ranchi': 'Jharkhand', 'Bhubaneswar': 'Odisha', 'Thiruvananthapuram': 'Kerala',
         'Guwahati': 'Assam', 'Dehradun': 'Uttarakhand', 'Shimla': 'Himachal Pradesh', 'Amaravati': 'Andhra Pradesh', 'Gandhinagar': 'Gujarat',
         'Ahmedabad': 'Gujarat', 'Chandigarh': 'Punjab', 'Gangtok': 'Sikkim', 'Imphal': 'Manipur', 'Panaji': 'Goa', 'Nagpur': 'Maharashtra',
         'Varanasi': 'Uttar Pradesh', 'Ayodhya': 'Uttar Pradesh', 'Bastar': 'Chhattisgarh', 'Dantewada': 'Chhattisgarh',
         'Sukma': 'Chhattisgarh', 'Nainital': 'Uttarakhand', 'Dispur': 'Assam', 'Noida': 'Uttar Pradesh', 'Gurugram': 'Haryana'}
FOREIGN = re.compile(r'Yemen|Houthi|Moscow|Kyiv|Kharkiv|Strasbourg|Brussels|NATO|Geneva|New York|Oslo|Somalia|Gulf of|Red Sea|Kenya|Taiwan|China|Chinese|Pakistan|Bangladesh|Nepal|Sri Lanka|United States|\bUS\b|American|Oklahoma|Texas|'
                     r'Washington|London|British|UK\b|France|French|Paris|Germany|German|Russia|Russian|Ukrain|Japan|Tokyo|Korea|Australia|'
                     r'Canada|Brazil|Iran|Israel|Gaza|Saudi|Qatar|Dubai|Turkey|Türkiye|Africa|Europe|Italy|Spain|Afghan|Myanmar')
STATES = set(ALIAS.values()) | {'Punjab', 'Haryana', 'Bihar', 'Kerala', 'Assam', 'Odisha', 'Goa', 'Tripura', 'Meghalaya', 'Mizoram',
                                 'Nagaland', 'Arunachal Pradesh', 'Telangana', 'Andhra Pradesh', 'Tamil Nadu', 'Karnataka'}


COUNTRY = {  # story words -> scene words for that country
    'Ukraine': (r'Ukrain|Zelensk|Kyiv', r'Ukrain|Kyiv'), 'Russia': (r'Russia|Putin|Kremlin|Moscow', r'Russia|Moscow|Kremlin'),
    'United States': (r'United States|\bUS\b|America|Trump|Washington|White House|Rubio|Congress\b.*US|\bSenate\b|House chairmen|Wall Street|Nasdaq|\bDow\b|Federal Reserve|Silicon Valley|midterm', r'White House|Capitol|United States|Wall Street|New York'),
    'China': (r'China|Chinese|Beijing|\bXi\b', r'China|Beijing'), 'Iran': (r'Iran|Tehran|Hormuz', r'Iran|Tehran|Hormuz'),
    'Israel': (r'Israel|Gaza|Netanyahu', r'Israel|Gaza|Jerusalem'), 'Nepal': (r'Nepal|Kathmandu', r'Nepal|Kathmandu'),
    'Bangladesh': (r'Bangladesh|Dhaka', r'Bangladesh|Dhaka'), 'Pakistan': (r'Pakistan|Islamabad', r'Pakistan|Islamabad'),
    'United Kingdom': (r'\bUK\b|Britain|London|Starmer', r'London|Britain|\bUK\b'), 'Japan': (r'Japan|Tokyo', r'Japan|Tokyo'),
    'European Union': (r'\bEU\b|European|Brussels', r'Brussels|European'), 'Turkey': (r'Turkey|Türkiye|Antalya|Ankara', r'Turkey|Türkiye|Antalya|Ankara'),
    'Sri Lanka': (r'Sri Lanka|Colombo', r'Sri Lanka|Colombo'), 'Maldives': (r'Maldives|Male\b', r'Maldives'),
}
INSTITUTION = [  # story words -> Indian institutions and settings that belong with it
    (r'Naxal|Maoist|CRPF|CoBRA|security forces|insurg', r'CRPF|BSF|jawans|troops|soldiers|Bastar|Dantewada|Sukma'),
    (r'Election Commission|ECI|\bCEC\b|EVM|SIR\b|voter|electoral roll|delimitation|ballot|polling', r'Nirvachan|Election Commission|polling|voter|ballot|inked finger|Indelible'),
    (r'talks|summit|visit|bilateral|diplomat|ambassador|envoy|phone call|speaks to|Jaishankar|MEA|treaty|partnership', r'Hyderabad House|External Affairs|South Block|diplomat|summit'),
    (r'BJP|Congress|party|election|polls?\b|vote|Lok Sabha|Rajya Sabha|MP\b|MLA|opposition|rally|campaign', r'Parliament|Election Commission|Nirvachan|polling|Vidhan|Lok Sabha|Rajya Sabha'),
    (r'court|judge|bench|bail|petition|verdict|hearing|Supreme Court|High Court', r'Supreme Court|High Court|court'),
    (r'Sensex|Nifty|shares|market|stock|SEBI|IPO|profit|revenue|quarter|Q[1-4]', r'Stock Exchange|BSE|NSE|Dalal|exchange'),
    (r'RBI|rupee|inflation|bank|GDP|Budget|tax|GST|fiscal', r'Reserve Bank|North Block|bank'),
    (r'army|troops|soldier|jawan|BSF|CRPF|border|security forces', r'soldiers|troops|BSF|jawans|\bArmy\b'),
    (r'navy|naval|warship', r'Indian Navy|warship|\bINS\b'), (r'air force|IAF|fighter', r'Air Force|fighter jet|airbase'),
    (r'cancer|health|hospital|AIIMS|doctor|vaccine|screening|disease|medical|patients', r'hospital|AIIMS|health|medical|clinic'),
    (r'school|university|college|students|exam|NEET|JEE|CBSE|UGC|IIT\b', r'school|university|college|campus|IIT\b|students'),
    (r'farmer|crop|MSP|paddy|wheat|kharif|rabi|mandi|stubble', r'farm|field|paddy|wheat|mandi|farmer|harvest'),
    (r'railway|train|Vande Bharat|station\b', r'railway|train|station'), (r'airport|airline|flight|IndiGo|Air India|aviation', r'airport|aircraft|airline'),
    (r'police|arrest|murder|killed|shot dead|crime|FIR', r'police'), (r'rain|flood|cyclone|storm|landslide|monsoon', r'rain|flood|cyclone|storm'),
    (r'smog|AQI|air quality|pollution|GRAP', r'smog|haze|pollution'),
]
UNIVERSAL = [  # settings that fit a story anywhere in the world
    (r'cricket|Test|ODI|T20|IPL', r'cricket|stadium'), (r'tennis|ATP|WTA|Masters|Open\b', r'tennis'), (r'badminton|shuttler', r'badminton|shuttle'), (r'hockey|football|athlet|Olympic|chess|shoot|Formula|F1\b|Grand Prix', r'stadium|circuit|sports arena'),
    (r'ISRO|NASA|rocket|launch|satellite|space|orbit|moon|Mars', r'rocket|launch|satellite|space|ISRO|NASA'),
    (r'semiconductor|Nvidia|chipmaker|chip stocks|data centre|TSMC|ASML', r'semiconductor|chip|wafer|data cent|server'),
    (r'oil|crude|Brent|OPEC|refiner|gas\b|LNG', r'oil|refinery|tanker|OPEC|LNG'), (r'ship|vessel|port|shipping|Hormuz|Red Sea', r'port|ship|vessel|tanker'),
]


INDIAN_RX = r'\bIndia|Indian|Parliament|Sansad|Lok Sabha|Rajya Sabha|Nirvachan|Election Commission|Rashtrapati|North Block|South Block|Vidhan|Bhavan|Bhawan|Reserve Bank|BSE|Dalal|ISRO|High Court|Delhi|Mumbai|Kolkata|Chennai|Bengaluru|inked finger|voter'


def simalt(a, b):
    wa = {w.lower() for w in words(a or '') if w.lower() not in ('file', 'photo', 'new', 'delhi', 'building', 'india')}
    wb = {w.lower() for w in words(b or '') if w.lower() not in ('file', 'photo', 'new', 'delhi', 'building', 'india')}
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= .4


def country_of(text):
    return [c for c, (srx, arx) in COUNTRY.items() if re.search(srx, text)]


INDIA_MARK = r'\bIndia|Indian|Delhi|Modi|Lok Sabha|Rajya Sabha|BJP|Supreme Court of India|Mumbai|Kolkata|Chennai|Bengaluru|Hyderabad|crore|lakh|₹'


def abroad_story(d):
    """A story about another country with no Indian angle: no Indian institutions behind it."""
    text = re.sub(r'\b(?:Monsoon|Winter|Budget) [Ss]ession', 'Parliament session', ' '.join(str(d.get(k) or '') for k in ('title', 'standfirst', 'format_label')))   # the Monsoon Session is Parliament, not rain
    if re.search(INDIA_MARK, text) or any(re.search(rf'\b{re.escape(x)}\b', text) for x in list(STATES) + list(ALIAS)): return False
    return (d.get('section') in ('world', 'science', 'technology', 'sports') or bool(country_of(text)) or bool(FOREIGN.search(text))
            or bool(re.search(r'Wall Street|Nasdaq|\bDow\b|Washington|House chairmen|\bSenate\b|White House|Pentagon|Federal Reserve|Silicon Valley|world.s', text)))


def own_scenes(sid, M, own_only=False):
    """The story's own in-story photos, then (for tiles) the main photos of the stories it links to: scenes and places only."""
    d = fm(sid); out = []
    keys = [k for k in M if k.startswith(sid + '--')] + ([] if own_only else [k for k in (d.get('related') or []) if isinstance(k, str)])
    for k in keys:
        x = M.get(k) or {}
        alt = x.get('alt') or ''
        if not x.get('src') or x.get('graphic') or x.get('notile') or not os.path.exists('public' + x['src']): continue
        if os.path.basename(x['src']).startswith(('t-', 'i2-', 'i-', 'v-')) or people(alt) or named_people(alt) or PERSONISH.search(alt): continue
        if re.search(r'chart|graphic|diagram|map of|logo', alt, re.I): continue
        if abroad_story(d) and re.search(INDIAN_RX, alt): continue
        if any(same_pic('public' + x['src'], 'public' + M[o]['src']) for o in out): continue
        out.append(k)
    return out


def fill_tiles(sid, M, have, n=3):
    """Three background scenes that clearly belong with the story: its own topic and names first, then its country or state,
    then the Indian institution the story is about. Places and scenes only, never a person, never an unrelated country."""
    out = [k for k in own_scenes(sid, M) if k not in have][:n]
    out += [k for k in related(sid, M, n) if k not in have and k not in out][:max(0, n - len(out))]
    d = fm(sid); fp = next((R + f'content/en/{t}/{sid}.md' for t in ('news', 'explainer', 'editorial', 'factcheck') if os.path.exists(R + f'content/en/{t}/{sid}.md')), '')
    body = (open(fp).read().split('---', 2)[-1][:1500] if os.path.exists(fp) else '')
    text = re.sub(r'\b(?:Monsoon|Winter|Budget) [Ss]ession', 'Parliament session', ' '.join(str(d.get(k) or '') for k in ('title', 'standfirst', 'format_label')))   # the Monsoon Session is Parliament, not rain   # headline and standfirst only
    countries = country_of(str(d.get('title') or '') + ' ' + str(d.get('standfirst') or ''))
    loc = str(d.get('location') or '')
    state = next((ALIAS.get(x.strip(), x.strip()) for x in loc.split(',')[::-1] if ALIAS.get(x.strip(), x.strip()) in STATES
                  and ALIAS.get(x.strip(), x.strip()) != 'Delhi'), None)
    allowed = [COUNTRY[c][1] for c in countries]
    abroad = abroad_story(d)
    story = text + ' ' + body
    if not state:   # a Delhi dateline: the state the headline is about, if any (Bastar -> Chhattisgarh)
        for nm in sorted(list(ALIAS) + list(STATES), key=len, reverse=True):
            if nm not in ('New Delhi', 'Delhi') and re.search(rf'\b{re.escape(nm)}\b', text): state = ALIAS.get(nm, nm); break
    def state_ok(alt):   # a scene from a state the story never mentions does not belong (UP's Vidhan Bhawan behind Advani)
        if re.search(r'High Court', alt) and not re.search(r'High Court', story): return False   # another court behind a Supreme Court story (owner, November 12)
        for nm in list(STATES) + list(ALIAS):
            if nm in ('New Delhi', 'Delhi') or not re.search(rf'\b{re.escape(nm)}\b', alt): continue
            stn = ALIAS.get(nm, nm)
            if stn != state and not re.search(rf'\b{re.escape(stn)}\b', story) and not re.search(rf'\b{re.escape(nm)}\b', story): return False
        return True
    def ok_scene(k, x):
        alt = x.get('alt') or ''
        if k == sid or k in have or k in out or x.get('graphic') or x.get('notile') or not x.get('src') or k.startswith('x-'): return False
        if os.path.basename(x['src']).startswith(('t-', 'i2-', 'i-', 'lib-')) or 'photos)' in alt or people(alt) or PERSONISH.search(alt): return False
        if not os.path.exists('public' + x['src']): return False
        fo = FOREIGN.search(alt)
        if fo and not any(re.search(a, alt) for a in allowed): return False            # a foreign scene only for that country's story
        if state and any(st in alt for st in STATES if st not in (state, 'Delhi')) and state not in alt: return False
        if state and any(c in alt for c, st in ALIAS.items() if st != state and c != 'New Delhi') and state not in alt: return False
        if not state_ok(alt): return False
        for rx in (r'bear|tiger|leopard|elephant|National Park|wildlife|bird', r'stadium|cricket|ground', r'coal|power station|thermal|mine\b'):
            if re.search(rx, alt, re.I) and not re.search(rx, story, re.I): return False   # off-topic: a sloth bear behind a political story
        if re.search(r'-bg-\d+\.jpg$', x['src']) or re.search(r'chart|graphic|diagram|seat', alt, re.I): return False
        if abroad and re.search(INDIAN_RX, alt): return False   # Indian Parliament behind Jensen Huang or a US Senate race
        if plain_backdrop(Image.open('public' + x['src']).convert('RGB')): return False
        return True
    out[:] = [k for k in out if state_ok(M[k].get('alt') or '')]
    def pick(rx, k_max):
        c = sorted((USED.get(k, 0), k) for k, x in M.items() if ok_scene(k, x) and re.search(rx, x.get('alt') or ''))
        took = 0
        for _, k in c:
            if len(out) >= n or took >= k_max: break
            if any(same_pic('public' + x['src'], 'public' + M[o]['src']) for o in list(out) + list(have) for x in [M[k]]): continue
            if any(simalt(M[o].get('alt'), M[k].get('alt')) for o in out): continue   # two views of one building
            out.append(k); took += 1
    sport = d.get('section') == 'sports'
    for c in countries: pick(COUNTRY[c][1] if not sport else rf'(?=[^\n]*(?:{COUNTRY[c][1]}))(?=[^\n]*(?:stadium|arena|gymnasium|badminton|sport|ground|court|match))', 2)   # Kyiv for a Zelenskyy story; a sports story takes only that country's sports venues (no Tokyo stock board behind a badminton player)
    if state:   # civic landmarks of the dateline's state only
        st_rx = re.escape(state) + '|' + '|'.join(re.escape(c) for c, st in ALIAS.items() if st == state)
        civic = r'Vidhan|Bhavan|Bhawan|Secretariat|Writers|headquarters|High Court|assembly|skyline|city|Raj Bhavan|Nabanna|Lalbazar'
        civic += r'|Nagar|Raipur|town|clock tower|Ghanta Ghar|Governor|capital|Legislative|Dispur|view|street|market'
        c = sorted((USED.get(k, 0), k) for k, x in M.items() if ok_scene(k, x) and re.search(st_rx, x.get('alt') or '') and re.search(civic, x.get('alt') or '', re.I))
        for _, k in c:
            if len(out) >= n: break
            if any(same_pic('public' + M[k]['src'], 'public' + M[o]['src']) for o in list(out) + list(have)): continue
            if sum(1 for o in out if re.search(st_rx, M[o].get('alt') or '')) >= 2: break
            if any((M[o].get('alt') or '') == (M[k].get('alt') or '') for o in out): continue
            out.append(k)
    for srx, arx in ([] if abroad else INSTITUTION) + UNIVERSAL:
        if len(out) >= n: break
        if re.search(rf'\b(?:{srx})', text, re.I): pick(arx, 2)
    return out[:n]


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
PERSONISH = re.compile(r'\b(leaders|delegates|ministers|officials|group photo|family photo|Justice|Dr|Mr|Mrs|Ms|Shri|Smt|minister|leader|chief|CM|MP|MLA|chairman|chairperson|CEO|president|woman|man|girl|boy|portrait|speaks|speaking|addresses|addressing|actor|player|batter|bowler|captain|coach)\b|\bGovernor(?= [A-Z][a-z]+ [A-Z][a-z]+)', re.I)
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


def library_portrait(pk, i=0):
    """Download (once, as a Wikimedia thumbnail) the first licensed photo of a library person: (path, credit) or None."""
    import urllib.request, io, time
    phs = PEOPLE[pk].get('photos') or []
    if i >= len(phs) or not phs[i].get('url'): return None
    ph = phs[i]
    path = f'public/photos/lib-{pk}-1280.jpg' if i == 0 else f'public/photos/lib-{pk}-{i}-1280.jpg'
    if not os.path.exists(path):
        u = ph['url'].split('?')[0]
        m = re.match(r'https://upload\.wikimedia\.org/wikipedia/commons/(\w)/(\w\w)/([^/]+)$', u)
        if m and (ph.get('width') or 0) > 1280 and not u.lower().endswith(('.svg', '.tif', '.tiff')):
            u = f'https://upload.wikimedia.org/wikipedia/commons/thumb/{m[1]}/{m[2]}/{m[3]}/1280px-{m[3]}'
        for wait in (1.5, 15, 45):
            time.sleep(wait)
            try:
                req = urllib.request.Request(u, headers={'User-Agent': 'GandhiNewsDesk/1.0 (https://gandhinews.com)'})
                im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=40).read())).convert('RGB')
                im.thumbnail((1280, 1600)); im.save(path, quality=88); break
            except Exception as ex:
                err = ex
        else:
            print(f'  library photo for {pk} not downloaded: {err}'); return None
    return path, f"{(ph.get('author') or 'Wikimedia Commons').strip()} / Wikimedia Commons, {ph.get('licence', '')}".strip(', ')


SUBJ_USED = {}   # subject photos already in a collage, keyed by a picture hash (two files of one photo count as one)
TILE_HASH = {}


def ahash(path):
    """A 64-bit average hash: the same picture saved twice under two names gets the same (or a very close) hash."""
    if path not in TILE_HASH:
        g = np.asarray(Image.open(path).convert('L').resize((8, 8), Image.BILINEAR)).astype(np.float32)
        TILE_HASH[path] = int(''.join('1' if v > g.mean() else '0' for v in g.flatten()), 2)
    return TILE_HASH[path]


def same_pic(a, b):
    return bin(ahash(a) ^ ahash(b)).count('1') <= 6


def subj_used(path):
    h = ahash(path)
    return sum(n for k, n in SUBJ_USED.items() if bin(k ^ h).count('1') <= 6)


def plain_backdrop(im):
    """True for a studio shot on a white or flat backdrop: it looks empty as a whole panel."""
    a = np.asarray(im.convert('L').resize((64, 64))).astype(np.float32)
    edge = np.concatenate([a[:6].ravel(), a[:, :6].ravel(), a[:, -6:].ravel()])
    return edge.mean() > 225 or edge.std() < 9


def portraits(sid, M):
    """Every solo photo we can use of the headline's first-named person, least-used first: [(path, credit), ...]."""
    d = fm(sid); title = str(d.get('title') or ''); fp = next((R + f'content/en/{t}/{sid}.md' for t in ('news', 'explainer', 'editorial', 'factcheck') if os.path.exists(R + f'content/en/{t}/{sid}.md')), '')
    full = title + ' ' + (open(fp).read() if os.path.exists(fp) else '') + ' ' + str(M.get(sid, {}).get('alt') or '')
    for pk in named_people(title)[:1]:
        # a surname alone is not enough: the full name must appear in the story (Tata Steel is not Ratan Tata)
        if not any(nm in full for nm in [PEOPLE[pk]['en']] + list(PEOPLE[pk].get('aliases') or [])): return []
        name = PEOPLE[pk]['en']; c = []
        for mk, x in M.items():
            alt = x.get('alt') or ''
            if mk == sid or x.get('graphic') or x.get('nocut') or mk.startswith('x-') or not x.get('src'): continue
            if os.path.basename(x['src']).startswith(('t-', 'i2-', 'i-', 'lib-')) or 'photos)' in alt: continue
            if name not in alt or re.search(r'Stadium|Mandapam\b.*\(file photo\)$|statue|poster|cutout|hoarding', alt) or named_people(alt) != [pk] or re.search(r'\band\b|\bwith\b|calls on|meets|photos\)', alt): continue
            if os.path.exists('public' + x['src']): c.append(('public' + x['src'], x.get('credit', '').replace('Photo: ', '')))
        for i in range(len(PEOPLE[pk].get('photos') or [])):
            lp = library_portrait(pk, i)
            if lp and lp[0] not in [p for p, _ in c]: c.append(lp)
        h = int(hashlib.md5(sid.encode()).hexdigest()[:6], 16)
        c.sort(key=lambda pc: (subj_used(pc[0]), (hash(pc[0]) ^ h) & 0xffff))
        return c
    return []


def _cuts_v(im):
    """A side-by-side panel picture of two or three people: each panel cut out, the people set side by side."""
    a = np.asarray(im.convert('L')).astype(np.float32)
    white = np.where((a.mean(0) > 242) & (a.std(0) < 12))[0]
    cuts, x0 = [], 0
    edges = [c for i, c in enumerate(white) if i == 0 or c != white[i - 1] + 1] if len(white) else []
    bounds = []
    for c in edges:
        run_end = c
        while run_end + 1 in set(white): run_end += 1
        if 40 < c < im.width - 40: bounds.append((x0, c)); x0 = run_end + 1
    bounds.append((x0, im.width))
    if not 2 <= len(bounds) <= 3: return None
    for l, r in bounds:
        res = _cuts(im.crop((l, 0, r, im.height)), loose=True)
        if not res or res[1]:
            if cuts: break                      # a person and a place: the person alone
            return None
        c = res[0]; bb = c.split()[-1].getbbox()
        if not bb: return None
        cuts.append(c.crop(bb))
    h = max(c.height for c in cuts)
    cuts = [c.resize((int(c.width * h / c.height), h), Image.LANCZOS) for c in cuts]
    ov = int(min(c.width for c in cuts) * .12)
    out = Image.new('RGBA', (sum(c.width for c in cuts) - ov * (len(cuts) - 1), h), (0, 0, 0, 0)); x = 0
    for c in cuts: out.alpha_composite(c, (x, 0)); x += c.width - ov
    return out, False


def _cuts(im, loose=False):
    """(cut-out, touches_top) when the photo gives one clean subject, else None."""
    cut, a = cutout(im)
    if not (.05 < a.mean() < .7 and a[-int(a.shape[0] * .2):].mean() > .04): return None    # nothing, or not standing on the bottom
    ew = max(2, int(a.shape[1] * .02))
    if not loose and (a[:, :ew].mean() > .12 or a[:, -ew:].mean() > .12): return None      # someone sliced by the side edge
    from scipy import ndimage
    lab, n = ndimage.label(a > .5)
    if sum(1 for sz in ndimage.sum(a > .5, lab, range(1, n + 1)) if sz > a.size * .03) > 2: return None   # a group
    sizes = list(ndimage.sum(a > .5, lab, range(1, n + 1))) if n else []
    if n > 1:   # keep the subject (and a second person of similar size); drop specks and slivers of bystanders
        big = max(sizes); keep = [i + 1 for i, sz in enumerate(sizes) if sz >= big * .3]
        km = ndimage.binary_dilation(np.isin(lab, keep), iterations=4)
        a = a * km
        cut = cut.copy(); cut.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    m = a > .5; cols = np.where(m.any(0))[0]
    if len(cols) == 0: return None
    bw = m[-max(2, int(a.shape[0] * .05)):].any(0).sum()                                    # width across the bottom rows
    if bw < (cols[-1] - cols[0] + 1) * .55: return None                                     # a face on a neck, no shoulders
    rows = np.where(m.any(1))[0]
    if (rows[-1] - rows[0]) < a.shape[0] * .45: return None                                 # a tiny figure in a big frame
    rs = m.sum(1); r15 = rows[0] + int((rows[-1] - rows[0]) * .15)
    if not loose and rs[r15] > rs.max() * .72: return None                                  # a face filling the frame, no shoulders below
    return cut, a[:max(2, int(a.shape[0] * .03))].mean() > .03


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


def pattern_tile(w, h, rnd, sides='tblr'):
    """A slot with no on-topic photo: a torn paper panel of fine halftone lines, never an unrelated picture."""
    im = Image.new('RGBA', (w, h), (234, 222, 214, 255)); dr = ImageDraw.Draw(im)
    for yy in range(-h, w + h, 9): dr.line([(0, yy), (w, yy - w * .6)], fill=(176, 120, 112, 255), width=2)
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


def treat_scenes(sid, M):
    return treat(sid, M, scenes_only=True)


def treat(sid, M, scenes_only=False):
    e = M[sid]
    # the subject: the story's own photo, unless it is an infographic or a cover of one person twice; then the headline
    # person's solo photo (ours or the library's); otherwise a collage of clearly related scenes
    alt0 = e.get('alt', '')
    single = (e.get('src') or '').split('/')[-1].startswith('v-') and len(named_people(alt0)) <= 1 and not re.search(r'\band\b|\bwith\b', alt0)
    is_v = (e.get('src') or '').split('/')[-1].startswith('v-') and not single   # side-by-side panels of two people
    own_ok = not e.get('graphic') and not single and not e.get('nocut')   # nocut: a face crop or screenshot, never the subject
    pre = None
    if own_ok:
        if is_v or named_people(alt0) or people(alt0) or PERSONISH.search(alt0):
            _im = Image.open('public' + e['src']).convert('RGB')
            pre = _cuts_v(_im) if is_v else (_cuts(_im) or (len(named_people(alt0)) <= 1 and _cuts(_im, loose=True)) or None)
    # the story's own photo when it cuts out cleanly, or when it shows an event or a place; a plain file headshot that
    # will not cut out (head cropped at the top, white backdrop) is swapped for a clean solo photo of the same person
    generic_head = own_ok and bool(named_people(alt0)) and not SCENE.search(alt0) and re.search(r'\(file photo\)\s*$', alt0)
    own_path = 'public' + e['src']
    own_cr = e.get('credit', '').replace('Photos: ', '').replace('Photo: ', '')
    subj_path = subj_credit = src_key = None
    whole_ok = True
    if own_ok:
        im0 = Image.open(own_path).convert('RGB')
        # a person's photo that does not cut out goes in whole only when it shows an event (a rally, a visit), never a face
        whole_ok = not is_v and not ((named_people(alt0) or people(alt0) or PERSONISH.search(alt0)) and (im0.height > im0.width * .9 or not SCENE.search(alt0))) and not plain_backdrop(im0)
    # never the same picture on two collages (owner, November 10): the story's own photo if it is fresh and usable, else a
    # fresh solo photo of the headline person that cuts out cleanly, else a collage of the story's scenes
    # the story's own photo is always the subject when it cuts out (a close crop may run off the top) or shows a
    # scene: it was already chosen as the story's picture, so it is on topic by definition (owner, November 11:
    # never swap in an unrelated scene, never leave a photo untreated)
    # a close crop of the story's own photo (head running off the top) fills the cover with a face: a clean full
    # portrait of the same person comes first when we hold one (owner, November 11)
    if own_ok and ((pre and not pre[1]) or (not pre and not generic_head and whole_ok)):
        subj_path, subj_credit, src_key = own_path, own_cr, sid
    else:
        tried = []
        for pth, c in portraits(sid, M):
            r = _cuts(Image.open(pth).convert('RGB'))
            if r and not r[1]: tried.append((subj_used(pth), pth, c))
            if tried and tried[-1][0] == 0: break
        if tried:
            _, pth, c = min(tried, key=lambda t: t[0]); subj_path, subj_credit, src_key = pth, c, 'portrait'
        elif own_ok and pre:   # no clean portrait: the story's own close crop
            subj_path, subj_credit, src_key = own_path, own_cr, sid
    if scenes_only: subj_path = subj_credit = src_key = None
    if subj_path: SUBJ_USED[ahash(subj_path)] = SUBJ_USED.get(ahash(subj_path), 0) + 1
    main_scene = None
    if src_key is None:
        pool = own_scenes(sid, M, own_only=True)   # the centre comes only from the story's own pictures, never a related story's
        fresh = [k for k in pool if subj_used('public' + M[k]['src']) == 0 and not plain_backdrop(Image.open('public' + M[k]['src']).convert('RGB'))]
        if fresh:
            main_scene = [fresh[0]] + [k for k in pool if k != fresh[0]]
            SUBJ_USED[ahash('public' + M[fresh[0]]['src'])] = SUBJ_USED.get(ahash('public' + M[fresh[0]]['src']), 0) + 1
        elif pool:
            main_scene = pool
        elif own_ok:   # nothing else on topic: the story's own photo, framed whole in the collage
            subj_path, subj_credit, src_key = own_path, own_cr, sid
            SUBJ_USED[ahash(own_path)] = SUBJ_USED.get(ahash(own_path), 0) + 1
        else:
            return None, False, []
    orig = Image.open(subj_path).convert('RGB') if subj_path else None
    rnd = random.Random(int(hashlib.md5(sid.encode()).hexdigest()[:8], 16))
    flip = rnd.random() < .5
    X = (lambda x, w: W - x - w) if flip else (lambda x, w: x)      # mirror a box when the subject sits on the right
    can = grain(Image.new('RGB', (W, H), PAPER), 6, rnd.randrange(1 << 30)).convert('RGBA')

    if main_scene:
        rel = main_scene[1:4]; centre = main_scene[0]
        if len(rel) < 3: rel += fill_tiles(sid, M, set(main_scene), 3 - len(rel))
    else:
        rel = fill_tiles(sid, M, set(), 3)   # always three scenes that belong with the story
        centre = None
    paths = ['public' + M[k]['src'] for k in rel]

    a0 = alt0 if src_key == sid else 'portrait'
    is_person = src_key == 'portrait' or bool(named_people(a0) or people(a0) or PERSONISH.search(a0))
    if src_key == sid and (len(named_people(a0)) > 2 or re.search(r'\b(group|team|members|delegation|crowd|officials|medallists|contingent|personnel|soldiers|troops)\b', a0, re.I)):
        is_person = False                                  # a group never cuts out cleanly: show the photo whole
    top = False
    if orig is not None and (is_person or (is_v and src_key == sid)):
        r = _cuts_v(orig) if (is_v and src_key == sid) else (_cuts(orig) or (src_key == sid and len(named_people(a0)) <= 1 and _cuts(orig, loose=True)) or None)
        ok = bool(r) and (src_key == sid or not r[1])
        if ok: cut, top = r
    else:
        ok = False
    if src_key == 'portrait' and not ok: return None, False, []


    can.alpha_composite(grid(220, 154), (X(36, 220), 40))
    can.alpha_composite(dots(176, 112), (X(W - 220, 176), H - 150))
    boxes = [(560, 60, 640, 420, 'tbr'), (40, 300, 380, 280, 'tblr'), (900, 440, 300, 220, 'tlr')]
    if not ok: boxes = [(20, 60, 320, 230, 'tblr'), (940, 500, 320, 240, 'tblr'), (30, 500, 300, 220, 'tlr')]
    for i, (x, y, w, h, sd) in enumerate(boxes):
        can.alpha_composite(tile(paths[i], w, h, rnd, True, sd) if i < len(paths) else pattern_tile(w, h, rnd, sd), (X(x, w), y))
    can.alpha_composite(bars(120, 90, rnd), (X(1130, 120), 28) if not flip else (30, 28))
    for (x, y, s) in [(410, 270, 26), (1180, 680, 18)]:
        can.alpha_composite(Image.new('RGBA', (s, s), RED + (255,)), (X(x, s), y))

    cxs = int(W * (.42 if not flip else .58))
    if ok:
        cut = cut.crop(cut.getbbox())
        if top: s = min(H / cut.height, W * .6 / cut.width)          # a close crop: the head runs off the top of the cover
        else: s = min(H * .94 / cut.height, W * .56 / cut.width)
        cut = cut.resize((round(cut.width * s), round(cut.height * s)), Image.LANCZOS)
        aw = int(min(max(cut.width * .8, 320), 520)); ah = int(H * .78)
        can.alpha_composite(arch(aw, ah), (cxs - aw // 2, H - ah))
        rim = Image.new('RGBA', cut.size, (250, 246, 238, 255)); rim.putalpha(cut.split()[-1].filter(ImageFilter.MaxFilter(7)))
        x0 = min(max(0, cxs - cut.width // 2), W - cut.width); y0 = H - cut.height
        can.alpha_composite(rim, (x0, y0)); can.alpha_composite(cut, (x0, y0))
    else:
        cw, ch = 820, 560
        tx = (W - cw) // 2 + (40 if not flip else -40)
        aw, ah = 280, 220     # a red dome rising from behind the top edge of the main photo
        can.alpha_composite(arch(aw, ah), ((tx + cw - aw - 70) if not flip else (tx + 70), 120 - 110))
        main = 'public' + (M[centre]['src'] if centre else e['src'])
        can.alpha_composite(tile(main, cw, ch, rnd, False, 'tblr'), (tx, 120))

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
                    **({'subj': format(ahash(subj_path), 'x')} if subj_path else {'subj': format(ahash('public' + M[centre]['src']), 'x')} if centre else {}),
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
        for f in glob.glob('content/en/news/*.md') + glob.glob('content/en/explainer/*.md') + glob.glob('content/en/editorial/*.md') + glob.glob('content/en/factcheck/*.md'):
            sid = os.path.basename(f)[:-3]; e = M.get(sid)
            if not e or e.get('notreat') or (e.get('treated') and os.path.exists('public' + e['treated']['src'])): continue
            m = re.search(r'^published: (\S+)', open(f).read(600), re.M)
            if m and str(m.group(1)) >= cut: ids.append((str(m.group(1)), sid))
        ids = [s for _, s in sorted(ids, reverse=True)]   # newest first: today's stories get the fresh portraits
    for sid in ids:   # a story being made again does not count its own old collage
        if sid in M: M[sid].pop('treated', None)
    import datetime as _D
    _week = (_D.datetime.now(_D.timezone.utc) - _D.timedelta(hours=48)).isoformat()[:16]
    _pub = {}
    for f in glob.glob('content/en/*/*.md'):
        mm = re.search(r'^published: (\S+)', open(f).read(600), re.M)
        if mm: _pub[os.path.basename(f)[:-3]] = str(mm.group(1))
    for sk, x in M.items():
        for k in (x.get('treated') or {}).get('with', []): USED[k] = USED.get(k, 0) + 1
        if _pub.get(sk, '') < _week: continue   # a picture may front another collage after 48 hours (owner, November 12)
        h = (x.get('treated') or {}).get('subj')
        if h: SUBJ_USED[int(h, 16)] = SUBJ_USED.get(int(h, 16), 0) + 1   # pictures already fronting a collage
    import time as _t
    t0 = _t.time(); budget = float(os.environ.get('TREAT_BUDGET_MIN', '0')) * 60   # stop cleanly before the job times out
    for i, sid in enumerate(ids):
        if budget and _t.time() - t0 > budget: print(f'time budget reached, {len(ids) - i} stories left for the next run'); break
        if i and i % 20 == 0: json.dump(M, open('content/photos.map.json', 'w'), ensure_ascii=False, indent=1)
        e = M.get(sid)
        if not e: print(f'{sid}: no photo entry, skipped'); continue
        if e.get('notreat'): e.pop('treated', None); print(f'{sid}: own photo kept, no collage (notreat)'); continue
        pid, ok, rel = treat(sid, M)
        if pid is None: e.pop('treated', None); print(f'{sid}: nothing suitable to build a cover from'); continue
        for k in M[sid].get('treated', {}).get('with', []): USED[k] = USED.get(k, 0) + 1
        print(f'{sid}: {pid} ({"cut-out" if ok else "scene"}; with {", ".join(rel) or "nothing"})')
    json.dump(M, open('content/photos.map.json', 'w'), ensure_ascii=False, indent=1)
