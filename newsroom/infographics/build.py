"""Draw a story's infographic from its scene file and register it as the story's picture.

Usage (repo root):
  python3 newsroom/infographics/build.py <story-id> [--preview] [--nophoto "<what was searched>"]
Reads newsroom/infographics/scenes/<story-id>.py and writes, for English and Hindi:
  public/photos/s-<id>-<lang>-3x2-1280.jpg / -640.jpg   the detailed graphic (story page)
  public/photos/s-<id>-<lang>-t-1280.jpg / -640.jpg     the drawing alone, 16:9 (cards and lists)
  public/photos/s-<id>-<lang>-1280.jpg / -640.jpg       headline over the drawing, 16:9 (share picture)
then records them in content/photos.map.json with style "scene".
--preview: render only, as PNG, into $GN_WORK/infographics/ (default /home/claude/gn-work/); nothing is registered.
Always look at the previews (Read the PNG files) before registering: see README.md for what to check.
"""
import sys, os, json, glob, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gnig import *
sys.path.insert(0, GN + 'newsroom/scripts')
from PIL import Image
def fonts():
    f = lambda fam, w, file: f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(file://{GN}public/fonts/{file})}}"
    return (f('PT Serif', 400, 'pt-serif-latin-400-normal.woff2') + f('PT Serif', 700, 'pt-serif-latin-700-normal.woff2')
            + f('Noto Serif Devanagari', 400, 'noto-serif-devanagari-devanagari-400-normal.woff2') + f('Noto Serif Devanagari', 700, 'noto-serif-devanagari-devanagari-700-normal.woff2'))
def load(sid):
    p = f'{GN}newsroom/infographics/scenes/{sid}.py'
    if not os.path.exists(p): sys.exit(f'no scene file: {p} (write it first; README.md in this folder says how)')
    spec = importlib.util.spec_from_file_location('scene_' + sid.replace('-', '_'), p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for lang in ('en', 'hi'):
        for k in ('kicker', 'headline', 'dek', 'source'):
            if not m.STR.get(lang, {}).get(k): sys.exit(f'{sid}: STR["{lang}"]["{k}"] is missing')
    return m
def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; preview = '--preview' in sys.argv
    nophoto = sys.argv[sys.argv.index('--nophoto') + 1] if '--nophoto' in sys.argv else None
    if nophoto in args: args.remove(nophoto)
    if not args: sys.exit(__doc__)
    from playwright.sync_api import sync_playwright
    work = (os.environ.get('GN_WORK') or '/home/claude/gn-work/').rstrip('/') + '/infographics/'; os.makedirs(work, exist_ok=True)
    P = RED; jobs = []; meta = {}
    for sid in args:
        m = load(sid); meta[sid] = m
        for lang in ('en', 'hi'):
            S = m.STR[lang]; art, notes, box = m.draw(P, S, lang)
            jobs += [(full(P, S, art, notes, lang), W, H, sid, lang, '-3x2'), (tile(P, art, box), 1280, 720, sid, lang, '-t'), (cover(P, S, art, box, lang), 1280, 720, sid, lang, '')]
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}, device_scale_factor=1)
        for svg, w, h, sid, lang, suf in jobs:
            hp = f'{work}{sid}-{lang}{suf or "-cover"}.html'
            open(hp, 'w', encoding='utf-8').write(f'<html><head><meta charset="utf-8"><style>{fonts()}body{{margin:0}}svg{{display:block}}</style></head><body>{svg}</body></html>')
            pg.goto('file://' + hp); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(350)
            png = hp[:-5] + '.png'; pg.screenshot(path=png, clip={'x': 0, 'y': 0, 'width': w, 'height': h}); os.remove(hp)
            if not preview:
                im = Image.open(png).convert('RGB'); out = f'{GN}public/photos/s-{sid}-{lang}{suf}'
                im.save(out + '-1280.jpg', quality=92, optimize=True); im.resize((640, round(640 * h / w)), Image.LANCZOS).save(out + '-640.jpg', quality=90, optimize=True)
        b.close()
    if preview:
        print('previews in ' + work + ':'); [print('  ' + os.path.basename(f)) for sid in args for f in sorted(glob.glob(f'{work}{sid}-*.png'))]; return
    mp = GN + 'content/photos.map.json'; M = json.load(open(mp, encoding='utf-8'))
    from gnrules import ihash
    import yaml
    for sid in args:
        m = meta[sid]; old = M.get(sid) or {}
        u = lambda lang, suf: (f'/photos/s-{sid}-{lang}{suf}-1280.jpg', f'/photos/s-{sid}-{lang}{suf}-640.jpg')
        e = {'id': f's-{sid}', 'src': u('en', '-3x2')[0], 'src800': u('en', '-3x2')[1], 'width': 1280, 'height': 853, 'credit': 'Graphic: Gandhi News', 'licence': '', 'graphic': True, 'style': 'scene',
             'alt': 'Gandhi News graphic: ' + m.STR['en']['headline'], 'alt_hi': 'गांधी न्यूज़ ग्राफ़िक: ' + m.STR['hi']['headline'], 'page': None,
             'byLang': {'hi': dict(zip(('src', 'src800'), u('hi', '-3x2')))},
             'thumb': {'en': dict(zip(('src', 'src800'), u('en', '-t'))), 'hi': dict(zip(('src', 'src800'), u('hi', '-t')))},
             'cover': {'width': 1280, 'height': 720, 'en': dict(zip(('src', 'src800'), u('en', ''))), 'hi': dict(zip(('src', 'src800'), u('hi', '')))}}
        # the story's own infographic: block, where it has one, is still fingerprinted so the audit notices changed figures
        gs = {}
        for lang in ('en', 'hi'):
            f = glob.glob(f'{GN}content/{lang}/*/{sid}.md') + glob.glob(f'{GN}newsroom/held/{lang}/*/{sid}.md')
            if f:
                ig = (yaml.safe_load(open(f[0], encoding='utf-8').read().split('---')[1]) or {}).get('infographic')
                if ig: gs[lang] = ig
        if gs.get('en'): e['ihash'] = ihash({'en': gs['en'], 'hi': gs.get('hi') or gs['en']})
        np = nophoto or old.get('nophoto')
        if np: e['nophoto'] = np
        M[sid] = e
        # the old card's files go with it
        for f in glob.glob(f'{GN}public/photos/i-{sid}-*') + glob.glob(f'{GN}public/photos/i2-{sid}-*'): os.remove(f)
        print(f'{sid}: scene graphic registered' + (' (no photo exists: never the lead)' if np else ''))
    json.dump(M, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if __name__ == '__main__': main()
