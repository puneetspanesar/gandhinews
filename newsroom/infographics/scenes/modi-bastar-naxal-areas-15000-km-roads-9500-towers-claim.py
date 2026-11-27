# Fact check: roads and mobile towers claimed for Naxal-hit areas against the Home Ministry's counts.
# The road is a ruler from 0 to 15,000 km; each mast stands for 500 towers, the last two dashed (claimed, not in the record).
from gnig import *
STR = {
 'en': dict(kicker='Fact check · Misleading', headline='Round numbers, bigger than the record',
            dek="The Prime Minister's figures for Naxal-hit areas, against the Home Ministry's published counts",
            source="Ministry of Home Affairs reply, Lok Sabha, August 12, 2025; PIB; Prime Minister's address, November 8, 2026",
            towers_n='8,640 mobile towers', towers_t='commissioned, Home Ministry count of August 2025', claim_n='9,500+ claimed', claim_t='about 860 beyond the record',
            mast='Each mast stands for 500 towers', sign_k='CLAIMED, NOVEMBER 8, 2026', sign_n='15,000+ km', km='km',
            roads_h='Roads built in Naxal-affected areas', roads_t='Solid road: the length every official count supports. Hatched: disputed.',
            a_n='12,012 km', a_t='Home Ministry annexure, August 2025', b_n='14,928 km', b_t="Ministry's reply in the Lok Sabha, August 2025"),
 'hi': dict(kicker='फैक्ट चेक · भ्रामक', headline='गोल संख्याएं, रिकॉर्ड से बड़ी',
            dek='नक्सल प्रभावित इलाकों पर प्रधानमंत्री के आंकड़े, गृह मंत्रालय की प्रकाशित गिनती के सामने',
            source='गृह मंत्रालय का उत्तर, लोकसभा, 12 अगस्त 2025; पीआईबी; प्रधानमंत्री का संबोधन, 8 नवंबर 2026',
            towers_n='8,640 मोबाइल टावर', towers_t='चालू किए गए, गृह मंत्रालय की अगस्त 2025 की गिनती', claim_n='9,500+ का दावा', claim_t='रिकॉर्ड से करीब 860 ज़्यादा',
            mast='हर टावर 500 टावरों के बराबर', sign_k='दावा, 8 नवंबर 2026', sign_n='15,000+ किमी', km='किमी',
            roads_h='नक्सल प्रभावित इलाकों में बनी सड़कें', roads_t='ठोस सड़क: वह लंबाई जो हर सरकारी गिनती में है। धारीदार हिस्सा: विवादित।',
            a_n='12,012 किमी', a_t='गृह मंत्रालय का अनुलग्नक, अगस्त 2025', b_n='14,928 किमी', b_t='लोकसभा में मंत्रालय का उत्तर, अगस्त 2025'),
}
def draw(P, S, lang):
    a, n = [], []                       # a: the drawing; n: the small labels (left out of cards)
    top, bot = 612, 660                 # the road
    back = ridge(3, -40, W + 60, 392, 62, 90); front = ridge(11, -40, W + 60, 470, 34, 80)
    a.append(f'<path d="{smooth(back)}" {A} stroke-width="2"/>')
    a.append(f'<path d="{smooth(front)} L{W+60} {top} L-40 {top} Z" fill="{P.sh}" stroke="#fff" stroke-width="2.5"/>')
    xs = [104 + i * 59.6 for i in range(19)]          # 17 masts counted (8,640), 2 dashed (to 9,500)
    a += [mobile_tower(x, y_on(front, x) + 6, 150 + (i * 37 % 3) * 6, dashed=i >= 17) for i, x in enumerate(xs)]
    a.append(forest(P, 7, 64, 30, W - 30, lambda x: y_on(front, x) + 34, top - 64))
    X = lambda km: 48 + km / 15000 * 1136
    a.append(f'<rect x="0" y="{top}" width="{X(15000):.1f}" height="{bot-top}" fill="#fff"/>' + hatch(P))
    a.append(f'<rect x="{X(12012):.1f}" y="{top}" width="{X(15000)-X(12012):.1f}" height="{bot-top}" fill="url(#hz)" stroke="#fff" stroke-width="2"/>')
    a.append(f'<path d="M0 {top+24} H{X(12012):.1f}" stroke="{P.bg}" stroke-width="4" stroke-dasharray="26 18"/>')
    a.append(bus(210, top, P) + motorbike(455, top, P) + truck(600, top, P) + car(835, top, P))
    a.append(sign_board(X(15000) - 61, top, P, S['sign_k'], S['sign_n']))
    for km in range(0, 15001, 1000):
        big = km % 5000 == 0
        n.append(f'<path d="M{X(km):.1f} {bot} v{14 if big else 8}" stroke="#fff" stroke-width="{2.5 if big else 1.6}"/>')
        if big and km < 15000: n.append(T(X(km), bot + 32, f'{km:,} {S["km"]}', 14, 700, 'middle' if km else 'start'))
    n.append(f'<path d="M{X(12012):.1f} {bot} V{bot+62} H{X(12012)-10:.1f}" {A} stroke-width="2"/>' + T(X(12012) - 18, bot + 72, S['a_n'], 26, 700, 'end') + T(X(12012) - 18, bot + 94, S['a_t'], 15, 400, 'end'))
    n.append(f'<path d="M{X(14928):.1f} {bot} V{bot+124} H{X(14928)-10:.1f}" {A} stroke-width="2"/>' + T(X(14928) - 18, bot + 116, S['b_n'], 26, 700, 'end') + T(X(14928) - 18, bot + 138, S['b_t'], 15, 400, 'end'))
    n.append(T(48, bot + 72, S['roads_h'], 18, 700) + T(48, bot + 94, S['roads_t'], 15))
    ty = 216
    n.append(f'<path d="M{xs[0]-18:.1f} {ty+22} v-8 H{xs[16]+18:.1f} v8" {A} stroke-width="2"/>' + T2(xs[0] - 18, ty, S['towers_n'], S['towers_t']))
    n.append(f'<path d="M{xs[17]-18:.1f} {ty+22} v-8 H{xs[18]+18:.1f} v8" {A} stroke-width="2" stroke-dasharray="4 4"/>' + T(1232, ty - 24, S['claim_n'], 26, 700, 'end') + T(1232, ty, S['claim_t'], 15, 400, 'end'))
    n.append(T(xs[0] - 18, ty + 44, S['mast'], 13))
    return ''.join(a), ''.join(n), (130, 262, 720, 405)
