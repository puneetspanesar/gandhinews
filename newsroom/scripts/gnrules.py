"""Shared mechanical rules (one definition, used by refresh_home.py, check_fresh.py and audit.py)."""
import re
# A markets story: index moves, currency, commodities, crypto, stock moves. Company results are business, not markets.
MKT = re.compile(r'(sensex|nifty|wall-street|dow-|nasdaq|ftse|kospi|nikkei|hang-seng|^oil-|brent|crude|^gold-|-gold-price|^silver-|rupee-(rises|falls|slips|gains|weakens|strengthens|ends|closes|hits|at)|bitcoin|crypto|markets?-|-shares-|stocks?-|-sales-\d|mcap|market-cap)')
CLOCK_EN = re.compile(r'\b(?:by|at|till|until|as of|as at)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)', re.I)
CLOCK_HI = re.compile(r'(सुबह|दोपहर|शाम|रात)?\s*(\d{1,2})(?::(\d{2}))?\s*बजे(?:\s*तक)?')
def clock_hours(txt, lang='en'):
    """Yield (matched text, hour 0-23, minute) for every clock time pinned in txt."""
    if lang == 'en':
        for m in CLOCK_EN.finditer(txt or ''):
            pm = m.group(3).lower().startswith('p')
            yield m.group(0), int(m.group(1)) % 12 + (12 if pm else 0), int(m.group(2) or 0)
    else:
        for m in CLOCK_HI.finditer(txt or ''):
            h = int(m.group(2)) % 12; w = m.group(1) or ''
            if w in ('शाम', 'रात') or (w == 'दोपहर' and h < 6): h += 12
            yield m.group(0), h, int(m.group(3) or 0)
STOP = {'supreme', 'minister', 'government', 'november', 'october', 'december', 'police', 'india', 'indian', 'explained', 'crore', 'says', 'percent'}
words = lambda i: {w for w in i.split('-') if len(w) >= 6 and w not in STOP}
import re as _re, datetime as _dt
def stale_clock(txt, lang, when, now, hours=2):
    """Clock-pinned figures in txt that are more than `hours` old at `now`. A scheduled time ("the final starts at 7 pm",
    "polling closes at 5 pm") is not a figure: a plain "at <time>" counts only when the same sentence has a % figure."""
    out = []
    for sent in _re.split(r'(?<=[.!?।])\s+', txt or ''):
        for m, hh, mm in clock_hours(sent, lang):
            snap = _re.match(r'(by|as of|as at|till|until)\b', m, _re.I) or m.endswith('तक') or _re.search(r'\d\s*(%|per cent|प्रतिशत)', sent)
            if not snap: continue
            t = when.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if t > when + _dt.timedelta(hours=1):
                if when.hour < 4 and hh >= 18: t -= _dt.timedelta(days=1)
                else: continue
            if (now - t).total_seconds() > hours * 3600: out.append((m, (now - t).total_seconds() / 3600))
    return out
