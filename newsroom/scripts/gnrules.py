"""Shared mechanical rules (one definition, used by refresh_home.py, check_fresh.py and audit.py)."""
import re
# A markets story: index moves, currency, commodities, crypto, stock moves. Company results are business, not markets.
MKT = re.compile(r'(dalal-street|share-price|closing-bell|opening-bell|bond-yield|fii-|-fpi-|gift-nifty|sensex|nifty|wall-street|dow-|nasdaq|ftse|kospi|nikkei|hang-seng|^oil-|brent|crude|^gold-|-gold-price|^silver-|rupee-(rises|falls|slips|gains|weakens|strengthens|ends|closes|hits|at)|bitcoin|crypto|markets?-|-shares-|stocks?-|-sales-\d|mcap|market-cap)')
CLOCK_EN = re.compile(r'\b(?:by|at|till|until|as of|as at|up to|upto)\s+(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)', re.I)
HI_NUM = {'एक': 1, 'दो': 2, 'तीन': 3, 'चार': 4, 'पांच': 5, 'पाँच': 5, 'छह': 6, 'सात': 7, 'आठ': 8, 'नौ': 9, 'दस': 10, 'ग्यारह': 11, 'बारह': 12}
CLOCK_HI = re.compile(r'(सुबह|दोपहर|शाम|रात)?\s*(\d{1,2}|' + '|'.join(HI_NUM) + r')(?:[:.](\d{2}))?\s*बजे(?:\s*तक)?')
def clock_hours(txt, lang='en'):
    """Yield (matched text, hour 0-23, minute) for every clock time pinned in txt."""
    if lang == 'en':
        for m in CLOCK_EN.finditer(txt or ''):
            pm = m.group(3).lower().startswith('p')
            yield m.group(0), int(m.group(1)) % 12 + (12 if pm else 0), int(m.group(2) or 0)
    else:
        for m in CLOCK_HI.finditer(txt or ''):
            raw = m.group(2); h = (int(raw) if raw.isdigit() else HI_NUM[raw]) % 12; w = m.group(1) or ''
            if w in ('शाम',) or (w == 'दोपहर' and h < 6) or (w == 'रात' and h >= 6): h += 12
            elif not w and h < 7: h += 12   # no word: daytime reporting hours (polls, markets) 7 am to 6 pm
            yield m.group(0), h, int(m.group(3) or 0)
def is_markets(sid, fm=None):
    """A markets story: by its id, or by its format label (Markets / बाज़ार)."""
    lbl = str((fm or {}).get('format_label') or '')
    return bool(MKT.search(sid)) or bool(re.match(r'\s*(Markets?|बाज़ार|बाजार)\b', lbl.split('/')[-1].strip()))
STOP = {'supreme', 'minister', 'government', 'november', 'october', 'december', 'police', 'india', 'indian', 'explained', 'crore', 'says', 'percent'}
words = lambda i: {w for w in i.split('-') if len(w) >= 6 and w not in STOP}
import re as _re, datetime as _dt
def stale_clock(txt, lang, when, now, hours=2):
    """Clock-pinned figures in txt that are more than `hours` old at `now`. A scheduled time ("the final starts at 7 pm",
    "polling closes at 5 pm") is not a figure: a plain "at <time>" counts only when the same sentence has a % figure."""
    out = []
    for sent in _re.split(r'(?<=[.!?।])\s+', txt or ''):
        for m, hh, mm in clock_hours(sent, lang):
            # "by 1 pm" / "as of 1 pm" always pins a figure; "at", "till", "तक" only when the sentence carries a % figure
            # ("polling till 5 pm" and "शाम 5 बजे तक मतदान" are schedules, "11.71% by 11 am" is a snapshot)
            snap = _re.match(r'(by|as of|as at|up to|upto)\b', m, _re.I) or _re.search(r'\d\s*(%|per cent|प्रतिशत|फ़ीसदी|फीसदी)', sent)
            if not snap: continue
            t = when.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if t > when + _dt.timedelta(hours=1): t -= _dt.timedelta(days=1)  # a figure is never from the future: it is from the day before
            if (now - t).total_seconds() > hours * 3600: out.append((m, (now - t).total_seconds() / 3600))
    return out
import html as _html
def clean_credit(c):
    """A photo credit fit to print: HTML entities decoded (repeatedly), wiki templates and licence boilerplate cut,
    no em dashes, no trailing punctuation."""
    c = str(c or '')
    for _ in range(3): c = _html.unescape(c)
    c = _re.sub(r'<[^>]+>', '', c)
    c = _re.sub(r'\.?\s*All (photographs|photos|images).*$', '', c, flags=_re.I)
    c = _re.sub(r'\{\{[^}]*\}\}', '', c)
    c = _re.sub(r'\s*(released|licen[sc]ed) under.*$', '', c, flags=_re.I)
    c = _re.sub(r'No machine-readable author provided\.\s*(.+?)\s+assumed.*$', r'\1', c)
    c = _re.sub(r'(This (photograph|photo|image) is created by|This image\'s author is|The original uploader was)\s+', '', c)
    c = _re.sub(r'\s+at English Wikipedia\.?', '', c)
    c = _re.sub(r'\s*[\u2014\u2013]\s*You must give.*$', '', c)
    c = _re.sub(r'(?<=\w)~commonswiki', '', c)
    c = c.replace('\u2014', ',').replace('\u2013', '-')
    c = _re.sub(r'\s{2,}', ' ', c).strip(' ,;:-')
    return c[:-1] if c.endswith('.') and not _re.search(r'\b(Ltd|Inc|Co|Jr|Sr|[A-Z])\.$', c) else c
import hashlib as _hl, json as _json
def ihash(gs):
    """Fingerprint of a story's infographic blocks ({'en': ..., 'hi': ...}); stored in photos.map.json by make_infographic.py
    and compared by audit.py, so a graphic whose story figures changed is re-rendered, never left showing old numbers."""
    return _hl.sha1(_json.dumps(gs, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:12]
def same_subject(a, b, fa=None, fb=None):
    """Two stories are on the same subject when their ids share two long words, or they share a topic in the same section."""
    if len(words(a) & words(b)) >= 2: return True
    fa, fb = fa or {}, fb or {}
    return bool(set(fa.get('topics') or []) & set(fb.get('topics') or [])) and fa.get('section') == fb.get('section')
def headline_ids(h):
    """Every story id in the headlines of a homepage.json: lead, live band, beside the lead, top stories, briefing."""
    L = h.get('lead') or {}; ts = h.get('topStories') or {}
    ids = [L.get('id')] + list(L.get('relatedBelow') or []) + list(L.get('relatedBeside') or []) + [(ts.get('big') or {}).get('id')] + list(ts.get('list') or []) + list(ts.get('also') or []) + [i.get('link') for i in (h.get('briefing') or {}).get('items') or []]
    return [i for i in dict.fromkeys(ids) if i]
def prev_hour_homepage(now, root='.', minutes=40):
    """(time, homepage dict) of main's homepage.json as it was in the newest commit at least `minutes` old, read from git,
    so the check does not depend on what a run wrote into homepage.json."""
    import subprocess as sp
    log = sp.run(['git', '-C', root, 'log', '-40', '--format=%H %ct', 'origin/main', '--', 'content/homepage.json'], capture_output=True, text=True).stdout.split('\n')
    for l in log:
        if not l.strip(): continue
        sha, ct = l.split()
        t = _dt.datetime.fromtimestamp(int(ct), now.tzinfo)
        if (now - t).total_seconds() >= minutes * 60:
            try: return t, _json.loads(sp.run(['git', '-C', root, 'show', f'{sha}:content/homepage.json'], capture_output=True, text=True).stdout)
            except ValueError: return None, None
    return None, None
