# Fact check: an NHAI RTI reply about its Guwahati unit read as a list of every legal toll plaza in Assam.
# India locator and Assam from the official map; the four NHAI project units are listed, not placed on the map.
# The road is schematic: the 13 toll plazas stand in the order NHAI's clarification of November 26, 2026 lists them, not to scale.
from gnig import *
NAMES = {'en': ['Telipara', 'Patgaon', 'Dahalpara', 'Galia', 'Madanpur', 'Nazirakhat', 'Raha', 'Rangamati', 'Sulung', 'Ratoa', 'Mikirati', 'Manderdisa', 'Balachera'],
         'hi': ['तेलीपाड़ा', 'पाटगांव', 'डहालपाड़ा', 'गलिया', 'मदनपुर', 'नज़ीराखाट', 'राहा', 'रंगामाटी', 'सुलुंग', 'रतोवा', 'मिकिराटी', 'मंडरदिसा', 'बालाछेड़ा']}
STR = {
 'en': dict(kicker='Fact check: Assam tolls', headline="One unit's list read as the whole state's",
            dek='NHAI has four project units in Assam; the RTI reply covered one',
            source='NHAI regional office, Guwahati, clarification of November 26, 2026',
            india='India', assam='Assam', units_h='Four NHAI project units in Assam', units=['Guwahati', 'Kaziranga', 'Bongaigaon', 'Silchar'],
            rti_n='3 plazas in the RTI reply', rti_t='The RTI reply of November 11, 2026 covered the Guwahati unit only',
            all_n='13 plazas', all_t="in NHAI's list for Assam, November 26, 2026",
            claim='Claimed: only these three are legal', order='Plazas in the order NHAI lists them; the road is not to scale'),
 'hi': dict(kicker='फैक्ट चेक: असम के टोल', headline='एक इकाई की सूची को पूरे राज्य की सूची समझा गया',
            dek='असम में एनएचएआई की चार परियोजना इकाइयां हैं, आरटीआई जवाब एक के बारे में था',
            source='एनएचएआई क्षेत्रीय कार्यालय, गुवाहाटी, 26 नवंबर 2026 का स्पष्टीकरण',
            india='भारत', assam='असम', units_h='असम में एनएचएआई की चार परियोजना इकाइयां', units=['गुवाहाटी', 'काज़ीरंगा', 'बोंगाईगांव', 'सिलचर'],
            rti_n='आरटीआई जवाब में 3 प्लाज़ा', rti_t='11 नवंबर 2026 का आरटीआई जवाब सिर्फ गुवाहाटी इकाई के बारे में था',
            all_n='13 प्लाज़ा', all_t='26 नवंबर 2026 की एनएचएआई की असम सूची में',
            claim='दावा: सिर्फ ये तीन वैध हैं', order='प्लाज़ा उसी क्रम में जिसमें एनएचएआई ने गिनाए; सड़क पैमाने पर नहीं'),
}
def gantry(x, top, bot, P, solid):
    """A toll plaza canopy across the road: roof, three pillars, a booth and a barrier arm; x is its left edge, 70 wide."""
    f = '#fff' if solid else P.bg; dash = '' if solid else ' stroke-dasharray="5 4"'
    s = f'<rect x="{x}" y="{top}" width="70" height="20" fill="{f}" stroke="#fff" stroke-width="2.4"{dash}/>'
    s += ''.join(f'<path d="M{x+px} {top+20} V{bot}" stroke="#fff" stroke-width="3"{dash}/>' for px in (6, 35, 64))
    s += f'<rect x="{x+12}" y="{bot-34}" width="16" height="22" fill="{f}" stroke="#fff" stroke-width="2"{dash}/><path d="M{x+28} {bot-14} H{x+56}" stroke="#fff" stroke-width="3"/>'
    if solid: s += ''.join(f'<rect x="{x+8+k*16}" y="{top+6}" width="8" height="8" fill="{P.bg}"/>' for k in range(4))
    return s
def draw(P, S, lang):
    a, n = [], []
    loc, s0 = india_locator(48, 182, 150, marked=('as',)); a.append(loc); n.append(T(48, 352, S['india'], 13, 700))
    shape, mw, at = state_shape('as', 224, 196, 150, P); a.append(shape)
    x0, y0, x1, y1 = path_bbox(india_paths()['as']); lx, ly = 48 + (x0 + x1) / 2 * s0, 182 + (y0 + y1) / 2 * s0
    a.append(f'<path d="M{lx+6:.1f} {ly:.1f} L224 {196+75}" {A} stroke-width="1.6" stroke-dasharray="3 4"/><circle cx="{lx:.1f}" cy="{ly:.1f}" r="8" {A} stroke-width="1.6"/>')
    n.append(T(224 + mw / 2, 370, S['assam'], 16, 700, 'middle'))
    ux = 224 + mw + 60
    n.append(T(ux, 214, S['units_h'], 18, 700))
    for i, u in enumerate(S['units']):
        y = 250 + i * 30
        n.append(f'<rect x="{ux}" y="{y-14}" width="16" height="16" fill="{"#fff" if i == 0 else P.bg}" stroke="#fff" stroke-width="2"/>' + T(ux + 28, y, u, 16, 700 if i == 0 else 400))
    # the road and the 13 plazas
    top, rt, rb = 492, 560, 612
    a.append(f'<path d="M0 {rt} H{W}" stroke="#fff" stroke-width="3"/><path d="M0 {rb} H{W}" stroke="#fff" stroke-width="3"/><path d="M0 {(rt+rb)/2} H{W}" stroke="#fff" stroke-width="1.6" stroke-dasharray="22 16"/>')
    xs = [52 + i * 89 for i in range(13)]
    for i, x in enumerate(xs):
        a.append(gantry(x, top, rb, P, 4 <= i <= 6))
        n.append(T(x + 35, 642 if i % 2 == 0 else 666, NAMES[lang][i], 14, 700 if 4 <= i <= 6 else 400, 'middle'))
    # brackets
    bx0, bx1 = xs[4] - 6, xs[6] + 76
    n.append(f'<path d="M{bx0} {top-12} v-8 H{bx1} v8" {A} stroke-width="2.2"/>' + T((bx0 + bx1) / 2, top - 52, S['rti_n'], 22, 700, 'middle') + T((bx0 + bx1) / 2, top - 30, S['claim'], 14, 400, 'middle'))
    n.append(f'<path d="M{xs[0]-6} 708 v8 H{xs[12]+76} v-8" {A} stroke-width="2"/>' + T2(xs[0] - 6, 744, S['all_n'], S['all_t'], 22, 15))
    n.append(T(xs[12] + 76, 744, S['order'], 13, 400, 'end'))
    n.append(T(ux, 386, S['rti_t'], 16, 700))
    return ''.join(a), ''.join(n), (40, 180, 1200, 450)
