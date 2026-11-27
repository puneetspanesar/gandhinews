# Explainer: front-of-pack warning labels. The back of a packet today (nutrition table, no warning), three pack fronts with the
# hexagons the court has ordered, the three warnings enlarged, a front panel with a hexagon drawn to scale (5% of the panel),
# and a timeline to scale: about four months for the rules, then 365 days. The packs are generic; no brand is shown.
from gnig import *
STR = {
 'en': dict(kicker='Explained · Food labels', headline='One warning hexagon for each nutrient', dek='Supreme Court directions to FSSAI, November 26, 2026',
            source='Supreme Court judgment of November 26, 2026, as reported; FSSAI Labelling and Display Regulations, 2020',
            today='Today', today_t='A nutrition table on the back, no warning', table='Nutrition information', per='per 100 g',
            rows=['Energy', 'Protein', 'Carbohydrate', 'Total sugars', 'Added sugars', 'Total fat', 'Saturated fat', 'Trans fat', 'Sodium'],
            order='What the court has ordered', order_t=['A separate warning on the front for each nutrient over its limit.', 'A pack high in two nutrients carries two hexagons.'],
            chips='Chips', biscuits='Biscuits', juice='Juice',
            warn='The three warnings', counted_t=['Counted on total sugars, salt and saturated fat,', 'not on added sugar and added fat'],
            size='4% to 5%', size_t=['of the front panel,', 'at the least, for', 'each hexagon'], scale=['Here: 5% of the', 'panel, to scale'],
            ev0=('November 26, 2026', ['Supreme Court judgment']), ev1=('10 weeks on', 'FSSAI reports progress to the court'),
            ev2=('About four months on', ['FSSAI finalises the rules,', 'with limits it has redone']), ev3=('365 days after that', ['Transition for food', 'companies ends']),
            span='365 days for companies to switch; no further extension ordinarily'),
 'hi': dict(kicker='समझिए · खाने के लेबल', headline='हर पोषक तत्व के लिए एक चेतावनी षट्भुज', dek='एफएसएसएआई को सुप्रीम कोर्ट के निर्देश, 26 नवंबर 2026',
            source='सुप्रीम कोर्ट का 26 नवंबर 2026 का फ़ैसला, रिपोर्टों के अनुसार; एफएसएसएआई लेबलिंग और डिस्प्ले विनियम, 2020',
            today='आज', today_t='पीछे एक पोषण तालिका, कोई चेतावनी नहीं', table='पोषण की जानकारी', per='प्रति 100 ग्राम',
            rows=['ऊर्जा', 'प्रोटीन', 'कार्बोहाइड्रेट', 'कुल चीनी', 'एडेड चीनी', 'कुल फैट', 'सैचुरेटेड फैट', 'ट्रांस फैट', 'सोडियम'],
            order='कोर्ट ने क्या आदेश दिया', order_t=['सीमा से ऊपर के हर पोषक तत्व की सामने अलग चेतावनी।', 'जिस पैकेट में दो तत्व ज़्यादा हैं, उस पर दो षट्भुज।'],
            chips='चिप्स', biscuits='बिस्कुट', juice='जूस',
            warn='तीन चेतावनियां', counted_t=['गिनती कुल चीनी, नमक और सैचुरेटेड फैट पर,', 'एडेड चीनी और एडेड फैट पर नहीं'],
            size='4% से 5%', size_t=['सामने के हिस्से का,', 'कम से कम, हर', 'षट्भुज के लिए'], scale=['यहां: हिस्से का 5%,', 'सही पैमाने पर'],
            ev0=('26 नवंबर 2026', ['सुप्रीम कोर्ट का फ़ैसला']), ev1=('10 हफ़्ते बाद', 'एफएसएसएआई कोर्ट को प्रगति बताएगा'),
            ev2=('करीब चार महीने बाद', ['एफएसएसएआई नियम पक्के करेगा,', 'दोबारा तय सीमाओं के साथ']), ev3=('उसके 365 दिन बाद', ['खाद्य कंपनियों की', 'बदलाव अवधि खत्म']),
            span='कंपनियों के पास बदलने के लिए 365 दिन; आम तौर पर आगे कोई विस्तार नहीं'),
}
def picto(kind, cx, cy, s, col):
    """The picture inside a hexagon: sugar cubes, a salt shaker, a drop of fat. Drawn in the hexagon's ink."""
    g = f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s})" fill="none" stroke="{col}" stroke-width="{2.2/s:.2f}" stroke-linejoin="round" stroke-linecap="round">'
    if kind == 'sugar':
        cube = lambda x, y: f'<path d="M{x} {y-7} l9 -4.5 l9 4.5 v10 l-9 4.5 l-9 -4.5 Z M{x} {y-7} l9 4.5 l9 -4.5 M{x+9} {y-2.5} v10"/>'
        g += cube(-17, 3) + cube(-1, 3) + cube(-9, -9)
    elif kind == 'salt':
        g += f'<path d="M-8 -3 h16 l3 16 h-22 Z" /><path d="M-8 -3 a8 8 0 0 1 16 0 Z" fill="{col}"/>' + ''.join(f'<circle cx="{x}" cy="{y}" r="1.1" fill="{col}" stroke="none"/>' for x, y in [(-5, 3), (0, 6), (5, 3), (-3, 9), (3, 9)])
    else:
        g += f'<path d="M0 -15 C7 -5 11 0 11 5 a11 11 0 0 1 -22 0 C-11 0 -7 -5 0 -15 Z"/><path d="M-5 6 a5.5 5.5 0 0 0 4 5"/>'
    return g + '</g>'
def warn_hex(kind, cx, cy, r, P, words=None):
    s = hexagon(cx, cy, r, P)
    if words: return s + picto(kind, cx, cy - r * 0.30, r / 46, P.bg) + T(cx, cy + r * 0.30, 'HIGH', r * 0.23, 700, 'middle', fill=P.bg, ls=0.6) + T(cx, cy + r * 0.58, words, r * 0.25, 700, 'middle', fill=P.bg, ls=0.6)
    return s + picto(kind, cx, cy, r / 30, P.bg)
def veg_mark(x, y, s=13):
    return f'<rect x="{x}" y="{y}" width="{s}" height="{s}" {A} stroke-width="1.6"/><circle cx="{x+s/2}" cy="{y+s/2}" r="{s*0.26:.1f}" fill="#fff"/>'
def bag(x, y, w, h, P):
    """A pillow bag: sealed and crimped at the top and bottom."""
    body = f'M{x} {y} H{x+w} V{y+16} q7 {(h-32)/2:.0f} 0 {h-32} V{y+h} H{x} V{y+h-16} q-7 {-(h-32)/2:.0f} 0 {-(h-32)} Z'
    crimp = ''.join(f'M{x+i} {y+3} v10 M{x+i} {y+h-13} v10 ' for i in range(8, w, 9))
    return f'<path d="{body}" fill="{P.sh}" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/><path d="{crimp} M{x} {y+16} H{x+w} M{x} {y+h-16} H{x+w}" {A} stroke-width="1.4"/>'
def draw(P, S, lang):
    a, n = [], []; G = 600
    a.append(f'<rect x="48" y="{G}" width="1184" height="11" fill="{P.sh}" stroke="#fff" stroke-width="2.2"/>')                      # the shelf
    # today: the back of a packet
    bx, by, bw, bh = 86, 290, 204, G - 290
    a.append(bag(bx, by, bw, bh, P) + f'<path d="M{bx+bw/2} {by+16} V{by+44} M{bx+bw/2} {by+bh-44} V{by+bh-16}" {A} stroke-width="1.4" stroke-dasharray="3 4"/>')
    tx, ty, tw = bx + 14, by + 52, bw - 28
    a.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{28+9*19+6}" fill="{P.bg}" stroke="#fff" stroke-width="1.8"/><path d="M{tx} {ty+26} H{tx+tw}" stroke="#fff" stroke-width="1.8"/>')
    a.append(T(tx + 8, ty + 17, S['table'], 10, 700) + T(tx + tw - 8, ty + 17, S['per'], 8.5, 400, 'end'))
    for i, r in enumerate(S['rows']):
        yy = ty + 26 + 19 * (i + 1) - 5; sub = i in (4, 6, 7)
        a.append(T(tx + (16 if sub else 8), yy, r, 10) + f'<path d="M{tx+tw-34} {yy-3} h26" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>'
                 + (f'<path d="M{tx} {yy+6} H{tx+tw}" stroke="#fff" stroke-width="0.8"/>' if i < 8 else ''))
    a.append(f'<path d="M{bx+bw+26} 446 h44 M{bx+bw+58} 436 l12 10 l-12 10" {A} stroke-width="2.4"/>')
    # ordered: three fronts
    cx0, cw = 392, 204
    a.append(bag(cx0, by, cw, bh, P) + veg_mark(cx0 + cw - 30, by + 30) + T(cx0 + 20, by + 62, S['chips'], 26, 700))
    a.append(''.join(f'<g transform="translate({cx0+px},{by+py}) rotate({rot})"><ellipse rx="34" ry="21" {A} stroke-width="2"/><path d="M-26 -7 q26 12 52 0 M-30 3 q30 13 60 0" {A} stroke-width="1.4"/></g>' for px, py, rot in [(72, 122, -14), (132, 150, 12), (84, 178, 6)]))
    a.append(warn_hex('salt', cx0 + 62, by + bh - 62, 31, P) + warn_hex('fat', cx0 + 142, by + bh - 62, 31, P))
    qx, qy, qw = 632, 372, 156
    a.append(f'<rect x="{qx}" y="{qy}" width="{qw}" height="{G-qy}" fill="{P.sh}" stroke="#fff" stroke-width="2.4"/><path d="M{qx} {qy+14} H{qx+qw}" stroke="#fff" stroke-width="1.4"/>' + veg_mark(qx + qw - 26, qy + 26)
             + T(qx + 14, qy + 50, S['biscuits'], 20, 700))
    for px, py in [(50, 92), (104, 104)]:
        a.append(f'<circle cx="{qx+px}" cy="{qy+py}" r="25" {A} stroke-width="2"/><circle cx="{qx+px}" cy="{qy+py}" r="19" {A} stroke-width="1" stroke-dasharray="2 3"/>' + ''.join(f'<circle cx="{qx+px+dx}" cy="{qy+py+dy}" r="1.6" fill="#fff"/>' for dx, dy in [(-7, -7), (7, -7), (0, 0), (-7, 7), (7, 7)]))
    a.append(warn_hex('sugar', qx + 46, G - 46, 26, P) + warn_hex('fat', qx + 110, G - 46, 26, P))
    jx, jy, jw = 824, 398, 96
    a.append(f'<path d="M{jx} {jy} H{jx+jw} V{G} H{jx} Z M{jx} {jy} l14 -28 h{jw-28} l14 28 M{jx+14} {jy-28} v-12 h{jw-28} v12" fill="{P.sh}" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>'
             + veg_mark(jx + jw - 24, jy + 12, 12) + T(jx + 12, jy + 36, S['juice'], 18, 700)
             + f'<circle cx="{jx+48}" cy="{jy+84}" r="24" {A} stroke-width="2"/><path d="M{jx+48} {jy+60} q4 -14 18 -14 q-2 12 -18 14 M{jx+34} {jy+78} a16 16 0 0 1 10 -10" {A} stroke-width="1.6"/>')
    a.append(warn_hex('sugar', jx + 48, G - 44, 25, P))
    # the three warnings, enlarged
    hy, R = 322, 52; hx = [988, 1088, 1188]
    a.append(f'<path d="M{jx+66} {G-62} L{hx[0]-R*0.6:.0f} {hy+R*0.78:.0f}" {A} stroke-width="1.6" stroke-dasharray="3 5"/>')
    for x, k, w in zip(hx, ('sugar', 'salt', 'fat'), ('SUGAR', 'SALT', 'FAT')): a.append(warn_hex(k, x, hy, R - 6, P, w))
    # a front panel with one hexagon at 5% of its area, to scale
    px, pw, ph = 960, 140, 170; py = G - ph; r5 = (0.05 * pw * ph / 2.598) ** 0.5
    a.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="none" stroke="#fff" stroke-width="2.2" stroke-dasharray="6 5"/>' + veg_mark(px + pw - 24, py + 12, 12)
             + f'<path d="M{px+14} {py+22} h56 M{px+14} {py+36} h38" stroke="#fff" stroke-width="2" stroke-linecap="round"/>' + hexagon(px + 14 + r5 * 0.9, py + ph - 14 - r5, r5, P))
    n.append(T(px + pw + 20, py + 44, S['size'], 24, 700) + TL(px + pw + 20, py + 68, S['size_t'], 14) + f'<path d="M{px+14+r5*1.9:.0f} {py+ph-14-r5:.0f} H{px+pw+12}" {A} stroke-width="1.4"/>' + TL(px + pw + 20, py + ph - 14 - r5 - 3, S['scale'], 12, lh=1.3))
    # headings
    n.append(T(48, 198, S['today'], 18, 700) + T(48, 220, S['today_t'], 14))
    n.append(T(392, 198, S['order'], 18, 700) + TL(392, 220, S['order_t'], 14, lh=1.4))
    n.append(T(1232, 198, S['warn'], 18, 700, 'end') + TL(1232, 220, S['counted_t'], 14, 400, 'end', lh=1.4))
    # timeline to scale: about four months (122 days), then 365 days
    ty = 690; X = lambda d: 48 + d / 487 * 1184
    n.append(hatch(P, 'hz', 8, 3) + f'<rect x="{X(122):.1f}" y="{ty-8}" width="{X(487)-X(122):.1f}" height="16" fill="url(#hz)" stroke="#fff" stroke-width="2"/>')
    n.append(timeline(48, 1232, ty, [(X(0), S['ev0'][0], S['ev0'][1], 'start'), (X(122), S['ev2'][0], S['ev2'][1], 'start'), (X(487), S['ev3'][0], S['ev3'][1], 'end')], lang))
    n.append(f'<circle cx="{X(70):.1f}" cy="{ty}" r="7" fill="#fff"/><path d="M{X(70):.1f} {ty} v-22" stroke="#fff" stroke-width="2"/>' + T2(X(70) + 10, ty - 30, S['ev1'][0], S['ev1'][1], 15, 14, gap=8))
    n.append(T((X(122) + X(487)) / 2 + 120, ty - 18, S['span'], 15, 700, 'middle'))
    return ''.join(a), ''.join(n), (60, 262, 1180, 356)
