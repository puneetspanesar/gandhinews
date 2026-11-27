# Explainer: the nutrient-based fertiliser subsidy. Ship and quay crane (imports), a fertiliser plant, the DAP bag with its price tag, a tractor and wheat.
# Coins show the subsidy bill: one coin for each Rs 2,000 crore, the extra ones this rabi filled.
from gnig import *
STR = {
 'en': dict(kicker='Explained · Fertiliser subsidy', headline='Rabi fertiliser subsidy up 64%', dek='The government pays more so that a bag of DAP stays at ₹1,350', source='Union Cabinet decision, November 11, 2026',
            pays='What the government pays on phosphatic and potassic fertilisers', last='Last rabi', this='This rabi', v1='₹37,952 crore', v2='₹62,370 crore',
            more='₹24,418 crore more, a rise of 64%', coin='One coin = ₹2,000 crore', bag=['DAP', '50 kg'], price='₹1,350',
            cap=[('Bought abroad', ['India imports most of its DAP, nearly all', 'its phosphoric acid and all its potash']), ('Makers and importers', ['are paid a fixed subsidy on every', 'kilogram of nutrient they sell']),
                 ('The farm price holds', ['A 50 kg bag of DAP stays', 'at ₹1,350']), ('Rabi sowing', ['Wheat, pulses and oilseeds', 'need about 35 million tonnes'])]),
 'hi': dict(kicker='समझिए · उर्वरक सब्सिडी', headline='रबी की उर्वरक सब्सिडी 64% बढ़ी', dek='सरकार ज्यादा देती है ताकि डीएपी ₹1,350 प्रति बैग पर रहे', source='केंद्रीय मंत्रिमंडल का फैसला, 11 नवंबर 2026',
            pays='फॉस्फेट और पोटाश वाले उर्वरकों पर सरकार क्या देती है', last='पिछला रबी', this='यह रबी', v1='₹37,952 करोड़', v2='₹62,370 करोड़',
            more='₹24,418 करोड़ ज्यादा, 64% की बढ़ोतरी', coin='एक सिक्का = ₹2,000 करोड़', bag=['डीएपी', '50 किलो'], price='₹1,350',
            cap=[('विदेश से खरीद', ['भारत ज्यादातर डीएपी, लगभग सारा फॉस्फोरिक', 'एसिड और पूरा पोटाश आयात करता है']), ('निर्माता और आयातक', ['बेचे गए हर किलो पोषक तत्व पर', 'तय सब्सिडी पाते हैं']),
                 ('किसान के लिए दाम वही', ['डीएपी का 50 किलो का बैग', '₹1,350 पर बना रहता है']), ('रबी की बुवाई', ['गेहूं, दालों और तिलहन के लिए', 'करीब 3.5 करोड़ टन की जरूरत'])]),
}
def draw(P, S, lang):
    a, n = [], []; G = 590
    a.append(f'<rect x="330" y="{G}" width="{W-330}" height="62" fill="{P.sh}"/><path d="M330 {G} H{W} M330 {G} V{G+62}" stroke="#fff" stroke-width="2.5" fill="none"/>')
    a.append('<clipPath id="sea"><rect x="0" y="560" width="326" height="120"/></clipPath>' + waves(0, 330, G + 6, clip='sea'))
    a.append(ship(52, G, P) + quay_crane(352, G, P))
    a.append('<g transform="translate(-16,0)">' + f'<path d="M500 452 H742 M500 462 H742 M560 452 V{G} M640 452 V{G} M716 452 V{G} M742 462 H774" {A} stroke-width="2"/>'
             + process_tower(436, G, P) + silo(532, G, P) + silo(590, G, P) + sphere_tank(700, G, P) + chimney(785, G, P) + smoke(790, 364) + shed(812, G, P) + '</g>')
    a += [sack(x, y, P) for x, y in [(868, G - 20), (914, G - 20), (960, G - 20), (891, G - 40), (937, G - 40), (914, G - 60)]]
    bx, by = 968, 468
    a.append(big_bag(bx, by, P, S['bag'][0], S['bag'][1]) + f'<path d="M{bx+78} {by+8} q22 -34 46 -22" {A} stroke-width="1.8"/>' + price_tag(bx + 118, by - 30, P, S['price']))
    a += [wheat(x, G, 44 + (i * 7 % 5) * 6) for i, x in enumerate(range(1206, 1276, 13))]
    a.append(tractor(1084, G, P) + birds([(250, 250, 1), (314, 224, 0.86), (210, 280, 0.72)]))
    # the subsidy bill in coins
    cx0, sp = 772, 14.8
    n.append(T(520, 188, S['pays'], 18, 700))
    for row, (lab, val, cnt) in enumerate([(S['last'], S['v1'], 19), (S['this'], S['v2'], 31)]):
        y = 222 + row * 32
        n.append(T(520, y, lab, 14) + T(600, y + 1, val, 19, 700) + ''.join(coin(cx0 + i * sp, y - 6, P, i >= 19) for i in range(cnt)))
    y2 = 254
    n.append(f'<path d="M{cx0+19*sp-8:.1f} {y2+8} v7 H{cx0+30*sp+8:.1f} v-7" {A} stroke-width="2"/>' + T(cx0 + 30 * sp + 8, y2 + 36, S['more'], 15, 700, 'end') + T(520, y2 + 36, S['coin'], 13))
    n.append(f'<path d="M520 306 H150 V430 M452 306 V328" {A} stroke-width="2" stroke-dasharray="5 5"/><path d="M143 420 l7 12 l7 -12 M445 318 l7 12 l7 -12" {A} stroke-width="2"/>')
    for i, (x, (h, lines)) in enumerate(zip((48, 420, 800, 1050), S['cap'])):
        n.append(f'<circle cx="{x+11}" cy="684" r="11" fill="#fff"/>' + T(x + 11, 689, str(i + 1), 14, 700, 'middle', fill=P.bg) + T(x + 30, 690, h, 17, 700) + TL(x, 716, lines, 14))
    n += [f'<path d="M{x-16} 684 h14 M{x-8} 678 l7 6 l-7 6" {A} stroke-width="2"/>' for x in (396, 776, 1026)]
    return ''.join(a), ''.join(n), (330, 330, 950, 330)
