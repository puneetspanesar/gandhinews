"""Infographic cover for a story that has no correct, current photo.

Usage (repo root):  python3 newsroom/scripts/make_infographic.py <story-id> [<story-id> ...] [--preview]
Reads the `infographic:` block from the story's English and Hindi frontmatter (content/ or newsroom/held/),
renders four images and registers them as the story's main picture in content/photos.map.json:
  public/photos/i-<id>-<lang>-1280.jpg / -640.jpg   16:9 cover (article hero, homepage 16:9 slots)
  public/photos/i-<id>-<lang>-3x2-1280.jpg / -640.jpg  3:2 card (lists and cards)
--preview: render only, into /home/claude/gn-work/infographics/, no map change.

The `infographic:` block (both language files, each in its own language):
  kicker: "Q2 results"                       short red label
  headline: "Zydus Wellness back in profit"  max about 8 words
  dek: "Revenue jumps 73% in the September quarter"     optional, one line
  stats:                                     2 or 3 key numbers (never more)
    - {icon: trend-up, value: "₹1,126.6 cr", label: "revenue, up 73.2%"}
  chart:                                     ONE of chart / timeline / steps / compare (optional but expected)
    {type: columns|bars, title: "Quarterly revenue, ₹ crore", unit: "", highlight: -1,
     items: [{label: "Q2 FY26", value: 650.5, display: "650.5"}, ...]}
  timeline: [{date: "Oct 30", text: "High Court stays the notification"}, ...]   3 to 5 points
  steps: [{title: "Special leave petition", text: "Goa files by Wednesday"}, ...] 3 to 4 steps
  compare: {left: {title, value, text}, right: {title, value, text}}
  source: "Company filing to the exchanges, November 3, 2026"
Icons are Phosphor duotone names (newsroom/phosphor/<name>-duotone.svg). Never robot or sparkle icons.
Every number must come from the story itself.
"""
import sys as _s2, os as _o2; _s2.path.insert(0, _o2.path.dirname(_o2.path.abspath(__file__))); from gnrules import ihash as _ihash
import os as _gn_os; GN_ROOT = _gn_os.environ.get('GN_ROOT') or _gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.dirname(_gn_os.path.abspath(__file__)))) + '/'  # repo root (works in any clone)
import sys, os, re, json, html, glob, io
import yaml
from PIL import Image

R = GN_ROOT + ''
PH = R + 'newsroom/phosphor/'
SEAL = open(R + 'src/components/seal.svg.txt').read()
RED, INK = '#cc0000', '#0d0d0d'
FONTS = f"""
@font-face{{font-family:GS;src:url(file://{R}newsroom/fonts/GoogleSans-500.ttf);font-weight:500}}
@font-face{{font-family:GS;src:url(file://{R}newsroom/fonts/GoogleSans-700.ttf);font-weight:700}}
@font-face{{font-family:ND;src:url(file://{R}newsroom/fonts/NotoSansDevanagari.ttf);font-weight:100 900}}
"""


def find(sid, lang):
    for p in glob.glob(f'{R}content/{lang}/*/{sid}.md') + glob.glob(f'{R}newsroom/held/{lang}/**/{sid}.md', recursive=True):
        return yaml.safe_load(open(p).read().split('---')[1]) or {}
    return None


def ico(name, size, color='#ff5a5a'):
    p = f'{PH}{name}-duotone.svg'
    if not os.path.exists(p): p = f'{PH}info-duotone.svg'
    s = open(p).read().replace('fill="currentColor"', f'fill="{color}"')
    return s.replace('<svg ', f'<svg width="{size}" height="{size}" ', 1)


e = lambda s: html.escape(str(s or ''))


def num(v):
    try: return float(str(v).replace(',', ''))
    except Exception: return 0.0


def chart_html(c, w, h, lang):
    items = c.get('items') or []
    if not items: return ''
    vals = [num(i.get('value')) for i in items]
    mx = max(vals) or 1
    hi = c.get('highlight', -1)
    hi = hi % len(items) if isinstance(hi, int) else -1
    title = f'<div class="ct">{e(c.get("title"))}</div>'
    if c.get('type') == 'bars':
        rows = ''.join(
            f'<div class="hb"><div class="hl">{e(i.get("label"))}</div><div class="ht"><i style="width:{max(v / mx * 100, 2):.1f}%;background:{RED if k == hi else "#7a1d1d"}"></i>'
            f'<b>{e(i.get("display", i.get("value")))}</b></div></div>' for k, (i, v) in enumerate(zip(items, vals)))
        return f'{title}<div class="hbs">{rows}</div>'
    n = len(items); bw = min(96, (w - (n - 1) * 22) / n)
    cols = ''.join(
        f'<div class="col" style="width:{bw:.0f}px"><b>{e(i.get("display", i.get("value")))}</b>'
        f'<i style="height:{max(v / mx * 100, 2):.1f}%;background:{RED if k == hi else "#7a1d1d"}"></i>'
        f'<span>{e(i.get("label"))}</span></div>' for k, (i, v) in enumerate(zip(items, vals)))
    return f'{title}<div class="cols">{cols}</div>'


def timeline_html(t):
    pts = ''.join(f'<div class="tp"><div class="ti">{ico(p.get("icon", "calendar-dots"), 48)}</div><div class="td">{e(p.get("date"))}</div><div class="dot"></div><div class="tx">{e(p.get("text"))}</div></div>' for p in t)
    return f'<div class="tl"><div class="tline"></div>{pts}</div>'


def steps_html(s):
    out = []
    for k, st in enumerate(s):
        if k: out.append(f'<div class="arr">{ico("arrow-right", 30, "#ff5a5a")}</div>')
        out.append(f'<div class="st"><div class="sn">{k + 1:02d}</div><div class="sh">{e(st.get("title"))}</div><div class="sx">{e(st.get("text"))}</div></div>')
    return f'<div class="steps">{"".join(out)}</div>'


def compare_html(c):
    side = lambda d: f'<div class="cs"><div class="cst">{e(d.get("title"))}</div><div class="csv">{e(d.get("value"))}</div><div class="csx">{e(d.get("text"))}</div></div>'
    return f'<div class="cmp">{side(c.get("left") or {})}<div class="vs">{ico("arrows-left-right", 40, "#ff5a5a")}</div>{side(c.get("right") or {})}</div>'


def page(g, lang, W, H):
    hi = lang == 'hi'
    fam = "ND, GS, sans-serif" if hi else "GS, ND, sans-serif"
    up = '' if hi else 'text-transform:uppercase;'
    stats = (g.get('stats') or [])[:3]
    st = ''.join(f'<div class="s1">{ico(s.get("icon", "info"), 58)}<div><div class="sv">{e(s.get("value"))}</div><div class="sl">{e(s.get("label"))}</div></div></div>' for s in stats)
    c = g.get('chart')
    if c and len(c.get('items') or []) <= 3: c = dict(c, type='bars')
    if c: body = chart_html(c, W - 112, 0, lang)
    elif g.get('timeline'): body = timeline_html(g['timeline'])
    elif g.get('steps'): body = steps_html(g['steps'])
    elif g.get('compare'): body = compare_html(g['compare'])
    else: body = ''
    if not body and stats:
        # No chart, timeline, steps or comparison: the numbers fill the panel instead of leaving it empty.
        body = '<div class="bigst">' + ''.join(f'<div class="b1">{ico(x.get("icon", "info"), 76)}<div class="bv">{e(x.get("value"))}</div><div class="bl">{e(x.get("label"))}</div></div>' for x in stats) + '</div>'
        st = ''
    tall = H > 760
    hl = e(g.get('headline'))
    hsize = (54 if len(g.get('headline', '')) < 40 else 46) - (4 if hi else 0)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{W}px;height:{H}px;background:{INK};color:#fff;font-family:{fam};overflow:hidden}}
.wm{{position:absolute;right:-60px;bottom:-70px;opacity:.07}}
.wrap{{position:absolute;inset:0;padding:{48 if tall else 40}px 56px 30px;display:flex;flex-direction:column;gap:{30 if tall else 22}px}}
.top{{display:flex;gap:32px;align-items:flex-start}}
.tt{{flex:1}}
.kick{{display:inline-block;background:{RED};font-weight:700;font-size:{20 if hi else 21}px;padding:7px 14px;{up}letter-spacing:{0 if hi else .3}px}}
h1{{text-wrap:balance;font-weight:700;font-size:{hsize}px;line-height:{1.22 if hi else 1.02};margin-top:16px;{up}}}
.dek{{font-weight:500;font-size:22px;line-height:1.3;margin-top:12px}}
.seal{{width:104px;height:104px;flex:none;outline:4px solid #fff;outline-offset:0}}
.seal svg{{width:104px;height:104px;display:block}}
.stats{{display:grid;grid-template-columns:repeat({max(len(stats), 1)},1fr);border-top:3px solid #fff;border-bottom:1px solid #4a4a4a}}
.s1{{display:flex;gap:16px;align-items:flex-start;padding:{22 if tall else 18}px 22px {22 if tall else 18}px 0}}
.s1+.s1{{border-left:1px solid #4a4a4a;padding-left:22px}}
.s1 svg{{flex:none;margin-top:2px}}
.sv{{font-weight:700;font-size:{34 if hi else 38}px;line-height:1.05;white-space:nowrap}}
.sl{{text-wrap:pretty;font-weight:500;font-size:18px;line-height:1.3;margin-top:6px}}
.vis{{flex:1;display:flex;flex-direction:column;justify-content:center;min-height:0}}
.ct{{font-weight:700;font-size:18px;{up}letter-spacing:{0 if hi else .4}px;color:#ff5a5a;margin-bottom:16px}}
.cols{{height:100%;display:flex;align-items:flex-end;gap:22px;border-bottom:2px solid #fff;padding-bottom:0;margin-bottom:34px}}
.col{{height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;position:relative}}
.col i{{display:block;width:100%}}
.col b{{font-weight:700;font-size:20px;margin-bottom:8px}}
.col span{{position:absolute;bottom:-30px;font-weight:500;font-size:16px;white-space:nowrap}}
.hbs{{display:flex;flex-direction:column;gap:{22 if tall else 16}px}}
.hb{{display:grid;grid-template-columns:230px 1fr;align-items:center;gap:20px}}
.hl{{font-weight:700;font-size:20px;line-height:1.2}}
.ht{{display:flex;align-items:center;gap:14px}}
.ht i{{display:block;height:{64 if tall else 52}px}}
.ht b{{font-weight:700;font-size:30px;white-space:nowrap}}
.tl{{position:relative;display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:28px}}
.ti{{height:60px}}
.tline{{position:absolute;left:0;right:0;top:111px;height:4px;background:{RED}}}
.tp{{position:relative}}
.td{{font-weight:700;font-size:24px;height:36px;color:#ff5a5a;white-space:nowrap}}
.dot{{width:26px;height:26px;border-radius:50%;background:#fff;border:5px solid {RED};margin:2px 0 18px}}
.tx{{text-wrap:pretty;font-weight:500;font-size:{23 if tall else 21}px;line-height:1.32}}
.steps{{display:flex;align-items:flex-start;gap:10px}}
.st{{flex:1;border-top:4px solid {RED};padding-top:14px}}
.arr{{padding-top:26px}}
.sn{{font-weight:700;font-size:32px;color:#ff5a5a}}
.sh{{font-weight:700;font-size:22px;line-height:1.2;margin-top:6px}}
.sx{{font-weight:500;font-size:19px;line-height:1.32;margin-top:8px}}
.cmp{{display:flex;align-items:center;gap:24px}}
.cs{{flex:1;border-top:4px solid {RED};padding-top:14px}}
.cst{{font-weight:700;font-size:20px;{up}}}
.csv{{font-weight:700;font-size:44px;margin-top:8px}}
.csx{{font-weight:500;font-size:19px;line-height:1.32;margin-top:8px}}
.bigst{{display:grid;grid-template-columns:repeat(auto-fit,minmax(0,1fr));gap:0;border-top:3px solid #fff}}
.b1{{padding:28px 26px 10px 0}}
.b1+.b1{{border-left:1px solid #4a4a4a;padding-left:26px}}
.bv{{font-weight:700;font-size:{48 if hi else 54}px;line-height:1.05;margin-top:18px;white-space:nowrap}}
.bl{{font-weight:500;font-size:22px;line-height:1.3;margin-top:10px;text-wrap:pretty}}
.foot{{display:flex;justify-content:space-between;align-items:baseline;border-top:1px solid #4a4a4a;padding-top:12px;font-size:15px;font-weight:500}}
.foot b{{color:#ff5a5a;font-weight:700}}
</style></head><body><div class="wm">{ico(g.get('motif') or (stats[0].get('icon') if stats else 'newspaper'), 460, '#ffffff')}</div><div class="wrap">
<div class="top"><div class="tt"><span class="kick">{e(g.get('kicker'))}</span><h1>{hl}</h1>{f'<div class="dek">{e(g.get("dek"))}</div>' if g.get('dek') else ''}</div><div class="seal">{SEAL}</div></div>
{f'<div class="stats">{st}</div>' if st else ''}
<div class="vis">{body}</div>
<div class="foot"><span><b>{'स्रोत' if hi else 'Source'}:</b> {e(g.get('source'))}</span><span><b>gandhinews.com</b></span></div>
</div></body></html>"""


def thumb(g, lang, W, H):
    """Card and small-slot version: one number or the headline, big enough to read at 200px wide."""
    hi = lang == 'hi'
    fam = "ND, GS, sans-serif" if hi else "GS, ND, sans-serif"
    up = '' if hi else 'text-transform:uppercase;'
    st = (g.get('thumb') or (g.get('stats') or [None])[0]) if not g.get('thumb_headline') else None
    motif = g.get('motif') or (st or {}).get('icon') or 'newspaper'
    if st:
        core = f'<div class="v">{e(st.get("value"))}</div><div class="l">{e(st.get("label"))}</div>'
    else:
        core = f'<div class="h">{e(g.get("headline"))}</div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{W}px;height:{H}px;background:{INK};color:#fff;font-family:{fam};overflow:hidden;position:relative}}
.ic{{position:absolute;right:70px;top:50%;transform:translateY(-50%)}}
.tx{{position:absolute;left:84px;right:520px;top:50%;transform:translateY(-50%)}}
.k{{display:inline-block;background:{RED};font-weight:700;font-size:{40 if hi else 42}px;padding:10px 22px;{up}line-height:1.15}}
.v{{font-weight:700;font-size:{118 if len(str((st or {}).get('value', ''))) < 9 else 96}px;line-height:1;margin-top:34px;letter-spacing:-.01em;white-space:nowrap}}
.l{{font-weight:500;font-size:46px;line-height:1.22;margin-top:22px;text-wrap:balance}}
.h{{font-weight:700;font-size:{70 if hi else 74}px;line-height:{1.2 if hi else 1.04};margin-top:30px;{up}text-wrap:balance}}
.sl{{position:absolute;left:84px;bottom:56px;width:84px;height:84px;outline:4px solid #fff}}
.sl svg{{width:84px;height:84px;display:block}}
</style></head><body><div class="ic">{ico(motif, 380)}</div>
<div class="tx"><span class="k">{e(g.get('kicker'))}</span>{core}</div></body></html>"""


def render(jobs):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        for htm, W, H, out in jobs:
            pg = b.new_page(viewport={'width': W, 'height': H})
            tmp = out + '.html'; open(tmp, 'w').write(htm)
            pg.goto('file://' + tmp, wait_until='load'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(200); os.remove(tmp)
            im = Image.open(io.BytesIO(pg.screenshot(type='png'))).convert('RGB')
            im.save(out + '-1280.jpg', quality=90, optimize=True)
            im.resize((640, round(640 * H / W)), Image.LANCZOS).save(out + '-640.jpg', quality=88, optimize=True)
            pg.close()
        b.close()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    preview = '--preview' in sys.argv
    outdir = '/home/claude/gn-work/infographics/' if preview else R + 'public/photos/'
    os.makedirs(outdir, exist_ok=True)
    M = json.load(open(R + 'content/photos.map.json'))
    for sid in args:
        en, hi = find(sid, 'en'), find(sid, 'hi')
        if not en or not en.get('infographic'): print(f'{sid}: no infographic block, skipped'); continue
        gs = {'en': en['infographic'], 'hi': (hi or {}).get('infographic') or en['infographic']}
        jobs, base = [], {}
        for lang, g in gs.items():
            jobs.append((page(g, lang, 1280, 720), 1280, 720, f'{outdir}i-{sid}-{lang}'))
            jobs.append((thumb(g, lang, 1280, 853), 1280, 853, f'{outdir}i-{sid}-{lang}-3x2'))
            jobs.append((thumb(g, lang, 1280, 720), 1280, 720, f'{outdir}i-{sid}-{lang}-t'))
        render(jobs)
        if preview: print('preview:', f'{outdir}i-{sid}-*'); continue
        u = lambda lang, s='': (f'/photos/i-{sid}-{lang}{s}-1280.jpg', f'/photos/i-{sid}-{lang}{s}-640.jpg')
        M[sid] = {'id': f'i-{sid}', 'src': u('en', '-3x2')[0], 'src800': u('en', '-3x2')[1], 'width': 1280, 'height': 853,
                  'credit': 'Graphic: Gandhi News', 'licence': '', 'graphic': True, 'alt': f"Gandhi News graphic: {gs['en'].get('headline', '')}", 'alt_hi': f"गांधी न्यूज़ ग्राफ़िक: {gs['hi'].get('headline', '')}",
                  'page': None, 'ihash': _ihash(gs), 'byLang': {'hi': {'src': u('hi', '-3x2')[0], 'src800': u('hi', '-3x2')[1]}},
                  'thumb': {'en': dict(zip(('src', 'src800'), u('en', '-t'))), 'hi': dict(zip(('src', 'src800'), u('hi', '-t')))},
                  'cover': {'width': 1280, 'height': 720, 'en': dict(zip(('src', 'src800'), u('en'))), 'hi': dict(zip(('src', 'src800'), u('hi')))}}
        print(f'{sid}: infographic cover registered')
    if not preview:
        json.dump(M, open(R + 'content/photos.map.json', 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
