"""The week ahead band, built mechanically every refresh so it is never empty or stale.
Sources, all dated: content/data/election-calendar.json (polling and counting days, with the Hindi file for names),
stories with an `upcoming:` block in their front matter ({date: YYYY-MM-DD, en: "...", hi: "..."}; desks add it to
previews and to stories that name a date ahead), and the fixed official release calendar (CPI on the 12th, forex reserves
every Friday, GST collections on the 1st). Only the next 7 days; at most 6 items, soonest first.
  python3 newsroom/scripts/week_ahead.py      prints the items (refresh_home.py calls build() and writes them)
"""
import json, glob, datetime as dt, yaml, calendar
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
MON_EN = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MON_HI = ['', 'जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर']
FULL_EN = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
def label(d, today):
    if d == today: return {'en': 'Today', 'hi': 'आज'}
    if d == today + dt.timedelta(days=1): return {'en': 'Tomorrow', 'hi': 'कल'}
    return {'en': f'{MON_EN[d.month]} {d.day}', 'hi': f'{d.day} {MON_HI[d.month]}'}
def build(now=None, root='.'):
    now = now or dt.datetime.now(IST); today = now.date(); end = today + dt.timedelta(days=7)
    items = []
    add = lambda d, icon, en, hi, link=None: items.append((d, icon, en, hi, link))
    try:
        E = json.load(open(f'{root}/content/data/election-calendar.json')); EH = {r['id']: r for r in json.load(open(f'{root}/content/data/hi/election-calendar.json'))['rows']}
        for r in E['rows']:
            hn = EH.get(r['id'], {}).get('name') or r['name']
            for k, en, hi in (('date', 'Polling', 'मतदान'), ('counting_date', 'Counting', 'मतगणना')):
                v = r.get(k)
                if not v or (k == 'date' and r.get('counting_date') == v): continue
                d = dt.date.fromisoformat(v)
                if today <= d <= end and not (k == 'date' and d == today and now.hour >= 18):
                    if k == 'counting_date' and r.get('date') == v: en, hi = 'Polling and counting', 'मतदान और मतगणना'
                    add(d, 'calendar-check', f"{en}: {r['name']}", f'{hi}: {hn}')
    except (OSError, ValueError, KeyError): pass
    for f in glob.glob(f'{root}/content/en/*/*.md'):
        src = open(f).read()
        if '\nupcoming:' not in src: continue
        fm = yaml.safe_load(src.split('---')[1]) or {}
        u = fm.get('upcoming') or {}
        try: d = u['date'] if isinstance(u.get('date'), dt.date) else dt.date.fromisoformat(str(u.get('date')))
        except ValueError: continue
        if today <= d <= end and u.get('en') and u.get('hi'): add(d, 'calendar-blank', u['en'], u['hi'], fm.get('id'))
    d = today
    while d <= end:
        prev = (d.replace(day=1) - dt.timedelta(days=1))
        if d.day == 12: add(d, 'chart-line', f'Retail inflation (CPI) for {FULL_EN[prev.month]}, 4 pm', f'{MON_HI[prev.month]} की खुदरा महंगाई (सीपीआई), शाम 4 बजे')
        if d.weekday() == 4: add(d, 'bank', "RBI's weekly forex reserves figures", 'आरबीआई के साप्ताहिक विदेशी मुद्रा भंडार के आंकड़े')
        if d.day == 1: add(d, 'receipt', f'GST collections for {FULL_EN[prev.month]}', f'{MON_HI[prev.month]} का जीएसटी संग्रह')
        d += dt.timedelta(days=1)
    seen, out = set(), []
    for d, icon, en, hi, link in sorted(items, key=lambda x: x[0]):
        if en in seen: continue
        seen.add(en)
        out.append({'icon': icon, 'date': label(d, today), 'text': {'en': en, 'hi': hi}, **({'link': link} if link else {})})
    return out[:6]
if __name__ == '__main__':
    for x in build(): print(x['date']['en'], '|', x['text']['en'], '|', x['text']['hi'])
