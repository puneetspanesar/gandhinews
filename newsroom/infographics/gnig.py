"""Gandhi News vector infographics (owner, November 27, 2026): the frame, the text helpers and a kit of drawn objects.

A graphic is a detailed drawn scene of the story's subject, white on the brand red. See README.md in this folder.
Every scene file in scenes/ imports from here:  from gnig import *
"""
import math, random, re, html, os
GN = os.environ.get('GN_ROOT') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
W, H = 1280, 853
class Pal:
    """bg: the brand red. sh: the darker red for ground, water and solid shapes. Everything else is white."""
    def __init__(s, bg, sh): s.bg, s.sh, s.w = bg, sh, '#ffffff'
RED = Pal('#cc0000', '#a30000')
esc = html.escape
A = 'fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round"'   # the usual white line

# ---------------------------------------------------------------- text
def T(x, y, txt, size=15, weight=400, anchor='start', ls=0, fill='#fff'):
    sp = f' letter-spacing="{ls}"' if ls else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}"{sp}>{esc(str(txt))}</text>'
def TL(x, y, lines, size=15, weight=400, anchor='start', lh=1.32, fill='#fff'):
    """Several lines, one under the other."""
    return ''.join(T(x, y + i * size * lh, l, size, weight, anchor, fill=fill) for i, l in enumerate(lines))
def T2(x, y, bold, rest, size_b=26, size_r=15, anchor='start', gap=10):
    """A bold figure followed on the same line by its plain description; widths take care of themselves."""
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="#fff"><tspan font-size="{size_b}" font-weight="700">{esc(bold)}</tspan><tspan font-size="{size_r}" dx="{gap}">{esc(rest)}</tspan></text>'
def wordmark(x_right, y, h=24, fill='#fff'):
    svg = open(GN + 'src/components/wordmark.svg.txt').read()
    inner = re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1).replace('currentColor', fill).replace('#cc0000', fill)
    s = h / 984.0
    return f'<g transform="translate({x_right - 5502 * s:.1f},{y:.1f}) scale({s:.5f}) translate(-6,762)">{inner}</g>'
FONT_STACK = "'PT Serif','Noto Serif Devanagari',serif"
def _svg(w, h, P, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT_STACK}"><rect width="{w}" height="{h}" fill="{P.bg}"/>{body}</svg>'
def full(P, S, art, notes, lang='en'):
    """The detailed 3:2 graphic for the story page: kicker, headline, one line under it, the scene, its labels, the source."""
    src = ('स्रोत: ' if lang == 'hi' else 'Source: ') + S['source']
    head = T(48, 64, S['kicker'].upper(), 14, 700, ls=0 if lang == 'hi' else 1.6) + T(48, 106, S['headline'], 34, 700) + T(48, 138, S['dek'], 18) + wordmark(W - 48, 44) + T(48, H - 28, src, 13)
    return _svg(W, H, P, art + notes + head)
def _fit(box, x, y, w, h):
    bx, by, bw, bh = box; s = min(w / bw, h / bh)
    return f'translate({x + (w - bw * s) / 2 - bx * s:.2f},{y + (h - bh * s) / 2 - by * s:.2f}) scale({s:.4f})'
def tile(P, art, box):
    """16:9 picture for cards and lists: the drawing alone, no small labels (the headline sits under the card as text)."""
    return _svg(1280, 720, P, f'<g transform="{_fit(box, 40, 40, 1200, 640)}">{art}</g>')
def cover(P, S, art, box, lang='en'):
    """16:9 share picture: kicker and headline over the drawing."""
    head = T(48, 70, S['kicker'].upper(), 15, 700, ls=0 if lang == 'hi' else 1.6) + T(48, 122, S['headline'], 40, 700) + wordmark(1232, 48)
    return _svg(1280, 720, P, f'<g transform="{_fit(box, 40, 170, 1200, 520)}">{art}</g>' + head)

# ---------------------------------------------------------------- shapes and land
def smooth(pts):
    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(1, len(pts) - 1):
        mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
        d += f' Q{pts[i][0]:.1f} {pts[i][1]:.1f} {mx:.1f} {my:.1f}'
    return d + f' L{pts[-1][0]:.1f} {pts[-1][1]:.1f}'
def ridge(seed, x0, x1, base, amp, step=70):
    """Points of a hill line from x0 to x1; draw it with smooth()."""
    r = random.Random(seed); pts = []; x = x0
    while x <= x1 + step:
        pts.append((x, base - amp * (0.35 + 0.65 * r.random()) * (0.6 + 0.4 * math.sin(x / 170.0 + seed)))); x += step * (0.7 + 0.6 * r.random())
    return pts
def y_on(pts, x):
    for a, b in zip(pts, pts[1:]):
        if a[0] <= x <= b[0]: return a[1] + (x - a[0]) / (b[0] - a[0]) * (b[1] - a[1])
    return pts[-1][1]
def hatch(P, pid='hz', step=9, bar=3.2):
    """<pattern> of white diagonal bars for a disputed, pending or estimated part; use fill="url(#hz)"."""
    return f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="{step}" height="{step}" fill="{P.bg}"/><rect width="{bar}" height="{step}" fill="#fff"/></pattern>'
def waves(x0, x1, y0, rows=4, gap=15, clip=None):
    out = ''
    for k in range(rows):
        n = int((x1 - x0) / 36) + 2
        out += f'<path d="M{x0 - 10 + (k % 2) * 14} {y0 + k * gap} ' + ' '.join('q9 -8 18 0 t18 0' for _ in range(n)) + f'" {A} stroke-width="1.8"' + (f' clip-path="url(#{clip})"' if clip else '') + '/>'
    return out
def birds(pts):
    return f'<path d="' + ' '.join(f'M{x} {y} q{s*7:.0f} {-s*8:.0f} {s*14:.0f} 0 q{s*7:.0f} {-s*8:.0f} {s*14:.0f} 0' for x, y, s in pts) + f'" {A} stroke-width="1.8"/>'
def smoke(x, y, n=3):
    return ''.join(f'<circle cx="{x + k * 18}" cy="{y - k * 21}" r="{9 + k * 3}" {A} stroke-width="2"/>' for k in range(n))

# ---------------------------------------------------------------- trees and crops
def sal(x, y, s, P):
    return (f'<path d="M{x:.1f} {y:.1f} V{y-26*s:.1f}" stroke="#fff" stroke-width="{2*s:.1f}" stroke-linecap="round"/><ellipse cx="{x:.1f}" cy="{y-36*s:.1f}" rx="{13*s:.1f}" ry="{17*s:.1f}" fill="{P.sh}" stroke="#fff" stroke-width="2"/>'
            f'<path d="M{x:.1f} {y-26*s:.1f} V{y-42*s:.1f} M{x:.1f} {y-34*s:.1f} l{-6*s:.1f} {-6*s:.1f} M{x:.1f} {y-30*s:.1f} l{6*s:.1f} {-6*s:.1f}" {A} stroke-width="1.4"/>')
def pine(x, y, s, P, filled=True):
    d = ''.join(f'M{x:.1f} {y-(18+k*13)*s-16*s:.1f} L{x-(13-k*3)*s:.1f} {y-(8+k*13)*s:.1f} H{x+(13-k*3)*s:.1f} Z ' for k in range(3))
    return f'<path d="M{x:.1f} {y:.1f} V{y-10*s:.1f}" stroke="#fff" stroke-width="{2.2*s:.1f}"/><path d="{d}" fill="{"#fff" if filled else P.sh}" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/>'
def forest(P, seed, n, x0, x1, top_y, bottom_y):
    """n trees between x0 and x1; top_y(x) gives the upper limit at x. Nearer trees are drawn larger and on top."""
    r = random.Random(seed); trees = []
    for _ in range(n):
        x = r.uniform(x0, x1); lo = top_y(x); y = r.uniform(lo, bottom_y); trees.append((y, x, r.random(), 0.62 + (y - lo) / (bottom_y - lo + 1) * 0.6))
    return ''.join(pine(x, y, s, P, k < 0.25) if k < 0.5 else sal(x, y, s, P) for y, x, k, s in sorted(trees))
def wheat(x, y, h):
    s = f'<path d="M{x:.1f} {y} q-2 {-h*0.5:.1f} 1 {-h:.1f}" {A} stroke-width="1.8"/>'
    s += ''.join(f'<path d="M{x+1:.1f} {y-h+4+k*5:.1f} l-5 -6 M{x+1:.1f} {y-h+4+k*5:.1f} l5 -6" {A} stroke-width="1.6"/>' for k in range(5))
    return s + f'<path d="M{x-1:.1f} {y-h*0.35:.1f} q-9 -4 -12 -14 M{x:.1f} {y-h*0.5:.1f} q8 -3 11 -12" {A} stroke-width="1.5"/>'

# ---------------------------------------------------------------- vehicles (side view, facing right; y is the ground)
def wheel(x, y, r, P):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{P.sh}" stroke="#fff" stroke-width="3"/><circle cx="{x}" cy="{y}" r="{r*0.28:.1f}" fill="#fff"/>'
def truck(x, y, P):
    s = f'<rect x="{x}" y="{y-58}" width="74" height="42" fill="#fff"/>' + ''.join(f'<path d="M{x+9+i*11} {y-54} v34" stroke="{P.sh}" stroke-width="2"/>' for i in range(6))
    s += f'<path d="M{x+78} {y-50} h20 l14 16 v18 h-34 z" fill="#fff"/><path d="M{x+84} {y-45} h12 l9 11 h-21 z" fill="{P.sh}"/><rect x="{x-2}" y="{y-18}" width="116" height="6" fill="#fff"/>'
    return s + wheel(x + 14, y - 10, 10, P) + wheel(x + 38, y - 10, 10, P) + wheel(x + 94, y - 10, 10, P)
def bus(x, y, P):
    s = f'<path d="M{x} {y-16} v-34 q0 -8 8 -8 h112 q12 0 14 12 l4 30 z" fill="#fff"/>' + ''.join(f'<rect x="{x+8+i*18}" y="{y-51}" width="13" height="14" fill="{P.sh}"/>' for i in range(6))
    s += f'<path d="M{x+118} {y-51} h10 l3 14 h-13 z" fill="{P.sh}"/><path d="M{x+6} {y-30} h124" stroke="{P.sh}" stroke-width="2"/>'
    return s + wheel(x + 26, y - 10, 10, P) + wheel(x + 108, y - 10, 10, P)
def car(x, y, P):
    return f'<path d="M{x} {y-14} v-16 h22 l6 -16 h30 l8 16 h16 q6 0 6 6 v10 z" fill="#fff"/><path d="M{x+31} {y-41} h23 l6 11 h-33 z" fill="{P.sh}"/>' + wheel(x + 18, y - 9, 9, P) + wheel(x + 70, y - 9, 9, P)
def motorbike(x, y, P):
    a = 'stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    return (f'<circle cx="{x}" cy="{y-9}" r="8" {a}/><circle cx="{x+34}" cy="{y-9}" r="8" {a}/><path d="M{x} {y-9} l10 -12 h14 l10 12 M{x+24} {y-21} l5 -10 h7" {a}/>'
            f'<circle cx="{x+17}" cy="{y-44}" r="5.5" fill="#fff"/><path d="M{x+15} {y-37} l-3 15 M{x+15} {y-34} l14 4" {a} stroke-width="4"/>')
def tractor(x, y, P):
    return (f'<path d="M{x+12} {y-46} h54 v-22 h30 l8 22 v18 h-92 z" fill="#fff"/><path d="M{x+16} {y-46} v-40 h44 l8 40" {A} stroke-width="3.2"/><path d="M{x+88} {y-68} v-22" {A} stroke-width="4"/>'
            f'<circle cx="{x+30}" cy="{y-28}" r="28" fill="{P.bg}" stroke="#fff" stroke-width="4"/><circle cx="{x+30}" cy="{y-28}" r="9" fill="#fff"/><circle cx="{x+92}" cy="{y-17}" r="17" fill="{P.bg}" stroke="#fff" stroke-width="4"/><circle cx="{x+92}" cy="{y-17}" r="5" fill="#fff"/>')
def ship(x, y, P):
    """Bulk carrier, about 255 wide; y is the waterline."""
    s = f'<path d="M{x} {y-42} H{x+254} L{x+236} {y+14} H{x+26} Z" fill="#fff"/><path d="M{x+8} {y-4} H{x+244}" stroke="{P.bg}" stroke-width="3"/>'
    s += f'<rect x="{x+18}" y="{y-92}" width="50" height="50" fill="#fff"/>' + ''.join(f'<rect x="{x+24+i*14}" y="{y-84+j*14}" width="9" height="7" fill="{P.bg}"/>' for i in range(3) for j in range(2))
    s += f'<rect x="{x+32}" y="{y-116}" width="18" height="24" fill="#fff"/><rect x="{x+32}" y="{y-110}" width="18" height="5" fill="{P.bg}"/><path d="M{x+41} {y-116} V{y-138} M{x+18} {y-92} H{x+68}" {A} stroke-width="2"/>'
    s += ''.join(f'<path d="M{x+82+i*40} {y-42} v-12 h30 v12" {A} stroke-width="2.2"/><path d="M{x+86+i*40} {y-54} l11 -12 l11 12" fill="#fff"/>' for i in range(4))
    return s + f'<path d="M{x+248} {y-42} V{y-70} M{x+248} {y-66} l-14 8" {A} stroke-width="2"/>'
def quay_crane(x, y, P, reach=156):
    """Port crane on two legs at x and x+40, boom reaching left over the water; y is the quay."""
    s = f'<path d="M{x} {y} V{y-194} M{x+40} {y} V{y-194} M{x} {y-194} H{x+40} M{x} {y-150} H{x+40} M{x} {y-150} L{x+40} {y-70} M{x+40} {y-150} L{x} {y-70} M{x} {y-70} H{x+40} M{x} {y-70} L{x+40} {y} M{x+40} {y-70} L{x} {y} M{x+20} {y-194} V{y-218} M{x-reach} {y-186} H{x+58} M{x-reach} {y-186} L{x+20} {y-218} L{x+58} {y-186} M{x-reach+44} {y-186} V{y-120}" {A} stroke-width="2.4"/>'
    return s + f'<path d="M{x-reach+32} {y-120} h24 l6 22 h-36 z" fill="#fff"/><rect x="{x+46}" y="{y-186}" width="18" height="22" fill="#fff"/>'

# ---------------------------------------------------------------- towers, plants and buildings
def mobile_tower(x, by, h=158, dashed=False):
    """Lattice mast with antenna panels and signal arcs. dashed=True draws it as not built or not counted."""
    top = by - h; s = []; dash = ' stroke-dasharray="4 4"' if dashed else ''
    a = f'fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"{dash}'
    bw, tw = 15, 3.5; mast = top + 20
    lx = lambda t: x - (bw + (tw - bw) * t); rx = lambda t: x + (bw + (tw - bw) * t); yy = lambda t: by + (mast - by) * t
    s.append(f'<path d="M{lx(0):.1f} {by:.1f} L{lx(1):.1f} {mast:.1f} L{rx(1):.1f} {mast:.1f} L{rx(0):.1f} {by:.1f}" {a}/>')
    lv = [0, .2, .4, .58, .74, .88, 1]
    for t0, t1 in zip(lv, lv[1:]):
        s.append(f'<path d="M{lx(t1):.1f} {yy(t1):.1f} H{rx(t1):.1f} M{lx(t0):.1f} {yy(t0):.1f} L{rx(t1):.1f} {yy(t1):.1f} M{rx(t0):.1f} {yy(t0):.1f} L{lx(t1):.1f} {yy(t1):.1f}" {a} stroke-width="1.4"/>')
    s.append(f'<path d="M{x:.1f} {mast:.1f} V{top:.1f}" {a}/>')
    if dashed:
        s.append(f'<rect x="{x-9:.1f}" y="{mast+4:.1f}" width="5" height="16" {a} stroke-width="1.4"/><rect x="{x+4:.1f}" y="{mast+4:.1f}" width="5" height="16" {a} stroke-width="1.4"/>')
    else:
        s.append(f'<rect x="{x-9:.1f}" y="{mast+4:.1f}" width="5" height="16" fill="#fff"/><rect x="{x+4:.1f}" y="{mast+4:.1f}" width="5" height="16" fill="#fff"/><circle cx="{x:.1f}" cy="{top:.1f}" r="2.6" fill="#fff"/>')
        for r in (9, 16):
            s.append(f'<path d="M{x+r*0.72:.1f} {top-r*0.7:.1f} A{r} {r} 0 0 1 {x+r*0.72:.1f} {top+r*0.7:.1f} M{x-r*0.72:.1f} {top-r*0.7:.1f} A{r} {r} 0 0 0 {x-r*0.72:.1f} {top+r*0.7:.1f}" {a} stroke-width="1.6"/>')
    return ''.join(s)
def process_tower(x, y, P, h=218, w=64):
    """Tall process or prilling tower with bands, a cap and a zigzag stair; y is the ground."""
    top = y - h
    s = f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{P.sh}" stroke="#fff" stroke-width="2.6"/>' + ''.join(f'<path d="M{x} {yy} H{x+w}" stroke="#fff" stroke-width="1.5"/>' for yy in range(int(top) + 36, y, 36))
    s += f'<path d="M{x-8} {top} H{x+w+8} L{x+w} {top-18} H{x} Z" fill="#fff"/><rect x="{x+16}" y="{top-34}" width="10" height="16" fill="#fff"/><rect x="{x+38}" y="{top-34}" width="10" height="16" fill="#fff"/>'
    n = int(h / 30) - 0; zz = f'M{x+w} {y} ' + ' '.join(f'L{x+w+14 if k % 2 == 0 else x+w} {y-(k+1)*30}' for k in range(n))
    return s + f'<path d="{zz}" {A} stroke-width="1.8"/><path d="M{x+w+14} {y} V{y-n*30}" {A} stroke-width="1.4"/>'
def silo(x, y, P, h=146, w=50):
    top = y - h
    return (f'<path d="M{x} {y} V{top} q{w/2} -30 {w} 0 V{y} Z" fill="{P.sh}" stroke="#fff" stroke-width="2.6"/><path d="M{x} {top} H{x+w} M{x} {top+56} H{x+w} M{x} {top+104} H{x+w}" stroke="#fff" stroke-width="1.5"/>'
            f'<path d="M{x+w-10} {y} V{top+8} M{x+w-4} {y} V{top+8} ' + ' '.join(f'M{x+w-10} {yy} h6' for yy in range(int(top) + 18, y, 12)) + f'" {A} stroke-width="1.2"/>')
def sphere_tank(x, y, P, r=44):
    cy = y - r - 30
    return (f'<path d="M{x-36} {y} V{cy+24} M{x-16} {y} V{cy+40} M{x+16} {y} V{cy+40} M{x+36} {y} V{cy+24}" {A} stroke-width="2.4"/><circle cx="{x}" cy="{cy}" r="{r}" fill="{P.sh}" stroke="#fff" stroke-width="2.6"/>'
            f'<path d="M{x-r} {cy} q{r} 16 {2*r} 0 M{x} {cy-r} V{cy-r-16} M{x-10} {cy-r-16} H{x+10}" {A} stroke-width="1.6"/>')
def chimney(x, y, P, h=206):
    top = y - h; k = 6 / h
    return f'<path d="M{x-15} {y} L{x-9} {top} H{x+9} L{x+15} {y} Z" fill="{P.sh}" stroke="#fff" stroke-width="2.6"/>' + ''.join(f'<path d="M{x-9-(yy-top)*k:.1f} {yy} H{x+9+(yy-top)*k:.1f} V{yy+16} H{x-9-(yy+16-top)*k:.1f} Z" fill="#fff"/>' for yy in (top + 14, top + 62, top + 110))
def shed(x, y, P, w=56, h=50):
    return f'<path d="M{x} {y} V{y-h} l14 -14 v14 l14 -14 v14 l14 -14 v14 H{x+w} V{y} Z" fill="{P.sh}" stroke="#fff" stroke-width="2.6"/><rect x="{x+12}" y="{y-32}" width="14" height="32" fill="#fff"/>'
def sack(x, y, P, w=44, h=19):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{P.sh}" stroke="#fff" stroke-width="2"/><path d="M{x+7} {y+4} v{h-8} M{x+w-7} {y+4} v{h-8}" stroke="#fff" stroke-width="1.2"/>'
def big_bag(x, y, P, line1, line2, w=86, h=122):
    """Upright filled bag with two lines of lettering; x, y is its top left."""
    s = f'<path d="M{x} {y+10} q0 -10 10 -10 h{w-20} q10 0 10 10 v{h-18} q0 8 -8 8 h-{w-16} q-8 0 -8 -8 z" fill="#fff"/><path d="M{x+6} {y+16} h{w-12}" stroke="{P.bg}" stroke-width="2" stroke-dasharray="5 4"/>'
    return s + T(x + w / 2, y + 62, line1, 24, 700, 'middle', fill=P.bg) + T(x + w / 2, y + 84, line2, 15, 700, 'middle', fill=P.bg) + f'<path d="M{x+18} {y+96} h{w-36}" stroke="{P.bg}" stroke-width="2"/>'
def price_tag(x, y, P, txt, rot=8):
    return f'<g transform="translate({x},{y}) rotate({rot})"><path d="M0 14 L16 0 H112 V30 H16 Z" fill="{P.bg}" stroke="#fff" stroke-width="2.2"/><circle cx="14" cy="15" r="3.4" fill="#fff"/>{T(66, 22, txt, 20, 700, "middle")}</g>'
def sign_board(x, y, P, small, big, w=182, h=62, legs=112):
    """Road sign on two posts; x is its centre, y the ground. Lettering in the brand red on white."""
    s = f'<path d="M{x-w/2+32:.1f} {y} V{y-legs} M{x+w/2-32:.1f} {y} V{y-legs}" stroke="#fff" stroke-width="4"/><rect x="{x-w/2:.1f}" y="{y-legs-12}" width="{w}" height="{h}" fill="#fff"/>'
    return s + T(x, y - legs + 10, small, 10.5, 700, 'middle', 0.8, P.bg) + T(x, y - legs + 38, big, 24, 700, 'middle', fill=P.bg)
def coin(x, y, P, filled=False, r=7.2):
    return f'<circle cx="{x:.1f}" cy="{y}" r="{r}" fill="{"#fff" if filled else "none"}" stroke="#fff" stroke-width="2"/><circle cx="{x:.1f}" cy="{y}" r="{r*0.36:.1f}" fill="{P.bg if filled else "#fff"}"/>'

# ---------------------------------------------------------------- maps (India with its official boundary, from public/maps/india.svg)
_MAP = None
def india_paths():
    """State id -> path data in the map's own 612 x 696 space. Ids are the two-letter codes in public/maps/india.svg (mn, up, wb, jk ...)."""
    global _MAP
    if _MAP is None: _MAP = dict(re.findall(r'<path id="([a-z]+)" d="([^"]+)"', open(GN + 'public/maps/india.svg').read()))
    return _MAP
def path_bbox(d):
    toks = re.findall(r'[mlzML]|-?\d*\.?\d+(?:e-?\d+)?', d); cmd = 'm'; x = y = sx = sy = 0; first = True; xs = []; ys = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t in 'mlzML':
            cmd = t
            if t in 'zZ': x, y = sx, sy
            i += 1; continue
        a, b2 = float(t), float(toks[i + 1]); i += 2
        if cmd in 'ml' and not first: x += a; y += b2
        else: x, y = a, b2
        if cmd in 'mM': sx, sy = x, y; cmd = 'l' if cmd == 'm' else 'L'
        first = False; xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)
def india_locator(x, y, height, marked=()):
    """Small map of India, all states outlined, the states in `marked` filled white. Returns (svg, scale); a point (px, py) of the map sits at (x + px*scale, y + py*scale)."""
    s = height / 696.0
    return f'<g transform="translate({x},{y}) scale({s:.4f})">' + ''.join(f'<path d="{d}" fill="{"#fff" if k in marked else "none"}" stroke="#fff" stroke-width="0.8" vector-effect="non-scaling-stroke" stroke-linejoin="round"/>' for k, d in india_paths().items()) + '</g>', s
def state_shape(code, x, y, height, P, clip_id=None):
    """One state drawn large. Returns (svg, width, place) where place(fx, fy) turns fractions of its box into points; with clip_id it also defines a clip path of the shape."""
    d = india_paths()[code]; x0, y0, x1, y1 = path_bbox(d); s = height / (y1 - y0); w = (x1 - x0) * s
    tr = f'translate({x},{y}) scale({s:.4f}) translate({-x0:.3f},{-y0:.3f})'
    svg = f'<g transform="{tr}"><path d="{d}" fill="{P.sh}" stroke="#fff" stroke-width="3" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></g>'
    if clip_id: svg += f'<clipPath id="{clip_id}"><path d="{d}" transform="{tr}"/></clipPath>'
    return svg, w, (lambda fx, fy: (x + fx * w, y + fy * height))
def hill_mark(x, y, s=1):
    return f'<path d="M{x-9*s:.1f} {y:.1f} l{9*s:.1f} {-11*s:.1f} l{9*s:.1f} {11*s:.1f} M{x+3*s:.1f} {y:.1f} l{7*s:.1f} {-8*s:.1f} l{7*s:.1f} {8*s:.1f}" {A} stroke-width="1.6"/>'

# ---------------------------------------------------------------- charts drawn as part of the scene
def hemicycle(cx, cy, rows, groups, P, label_r=None, r=10.5):
    """Seats of a House in arcs. rows: [(radius, seats)], inner first. groups: [(name, seats, filled)] from left to right.
    Returns (svg, seats) where seats is the list of (angle, radius) in order, for marking a majority line."""
    seats = []
    for rad, n in rows:
        seats += [(math.pi - math.pi * (i + 0.5) / n, rad) for i in range(n)]
    seats.sort(key=lambda t: (-t[0], t[1])); out = []; k = 0; ends = []
    for name, n, filled in groups:
        grp = seats[k:k + n]; k += n; ends.append(grp[-1][0])
        out += [f'<circle cx="{cx + rad * math.cos(a):.1f}" cy="{cy - rad * math.sin(a):.1f}" r="{r}" fill="{"#fff" if filled else "none"}" stroke="#fff" stroke-width="2.4"/>' for a, rad in grp]
    R = max(rad for rad, _ in rows) + r + 12; lr = label_r or R + 15
    edges = [math.pi + 0.03] + [(ends[i] + seats[sum(g[1] for g in groups[:i + 1])][0]) / 2 for i in range(len(groups) - 1)] + [-0.03]
    for i, (name, n, filled) in enumerate(groups):
        a0, a1 = edges[i] - 0.022, edges[i + 1] + 0.022
        pt = lambda a, rr: f'{cx + rr * math.cos(a):.1f} {cy - rr * math.sin(a):.1f}'
        out.append(f'<path d="M{pt(a0, R)} A{R} {R} 0 0 1 {pt(a1, R)} M{pt(a0, R - 8)} L{pt(a0, R)} M{pt(a1, R - 8)} L{pt(a1, R)}" {A} stroke-width="2"/>')
        am = (a0 + a1) / 2; anchor = 'end' if math.cos(am) < -0.2 else 'start' if math.cos(am) > 0.2 else 'middle'
        out.append(T(cx + lr * math.cos(am), cy - lr * math.sin(am) + 5, f'{name} {n}', 17 if i == 0 else 15, 700, anchor))
    return ''.join(out), seats
def timeline(x0, x1, y, events, lang='en'):
    """A line with dated points. events: [(x, date_text, [lines], anchor)]. Put x on a real time scale wherever you can."""
    s = f'<path d="M{x0} {y} H{x1}" stroke="#fff" stroke-width="2.5"/>'
    for x, lab, lines, anc in events:
        s += f'<circle cx="{x:.1f}" cy="{y}" r="7" fill="#fff"/><path d="M{x:.1f} {y} v24" stroke="#fff" stroke-width="2"/>' + T(x, y + 44, lab, 15, 700, anc) + TL(x, y + 64, lines, 14, 400, anc)
    return s
def hexagon(cx, cy, r, P, fill='#fff'):
    pts = ' '.join(f'{cx + r * math.sin(math.radians(a)):.1f},{cy - r * math.cos(math.radians(a)):.1f}' for a in range(0, 360, 60))
    return f'<polygon points="{pts}" fill="{fill}" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>'
