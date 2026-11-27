# News: TRAI's Phase II direction for the 1601 series (November 27, 2026).
# A phone receiving a 1601 call; a street of the kinds of companies now covered (generic buildings and vehicles, schematic);
# a timeline to scale from the Phase I direction (August 10, 2026) to the end of the 180 days (May 26, 2027, our count).
from gnig import *
import datetime as dt
STR = {
 'en': dict(kicker='Telecom: the 1601 series', headline='One number series for genuine service calls',
            dek="TRAI's Phase II direction of November 27, 2026 and the 180 days operators have",
            source='TRAI directions of August 10 and November 27, 2026; end of the 180 days counted by Gandhi News',
            incoming='Incoming call', num='1601 XXX XXXX', verified='Verified company', service='Service or transaction',
            nosale='Never for sales calls', p1='Phase I: utilities, logistics, couriers', p2='Phase II: 13 more sectors',
            hosp='Hospital', shop='Retail', bar1='₹500 crore turnover or more', bar1t='in one of the last three years',
            bar2='10 lakh subscribers', bar2t='for DTH, cable and IPTV',
            ev=[('August 10, 2026', ['Phase I', 'direction']), ('November 27, 2026', ['Phase II', 'direction']), ('May 26, 2027', ['180 days end', 'for operators'])],
            window='180 days to move every eligible company'),
 'hi': dict(kicker='दूरसंचार: 1601 सीरीज़', headline='असली सर्विस कॉल के लिए एक नंबर सीरीज़',
            dek='27 नवंबर 2026 का ट्राई का दूसरे चरण का निर्देश और ऑपरेटरों के पास 180 दिन',
            source='ट्राई के 10 अगस्त और 27 नवंबर 2026 के निर्देश; 180 दिन की गिनती गांधी न्यूज़ की',
            incoming='आती कॉल', num='1601 XXX XXXX', verified='सत्यापित कंपनी', service='सर्विस या ट्रांज़ैक्शन',
            nosale='बिक्री की कॉल कभी नहीं', p1='पहला चरण: बिजली-पानी सेवाएं, लॉजिस्टिक्स, कूरियर', p2='दूसरा चरण: 13 और क्षेत्र',
            hosp='अस्पताल', shop='रिटेल', bar1='₹500 करोड़ या ज़्यादा टर्नओवर', bar1t='पिछले तीन में से एक साल में',
            bar2='दस लाख ग्राहक', bar2t='डीटीएच, केबल और आईपीटीवी के लिए',
            ev=[('10 अगस्त 2026', ['पहले चरण का', 'निर्देश']), ('27 नवंबर 2026', ['दूसरे चरण का', 'निर्देश']), ('26 मई 2027', ['ऑपरेटरों के', '180 दिन पूरे'])],
            window='हर पात्र कंपनी को लाने के लिए 180 दिन'),
}
def phone(x, y, w, h, P, S):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="34" fill="#fff"/><rect x="{x+12}" y="{y+40}" width="{w-24}" height="{h-84}" rx="8" fill="{P.sh}"/>'
    s += f'<rect x="{x+w/2-30:.1f}" y="{y+18}" width="60" height="8" rx="4" fill="{P.sh}"/><circle cx="{x+w/2:.1f}" cy="{y+h-22}" r="11" fill="none" stroke="{P.sh}" stroke-width="3"/>'
    cx = x + w / 2
    s += T(cx, y + 92, S['incoming'], 16, 400, 'middle') + T(cx, y + 136, S['num'], 23, 700, 'middle')
    # verified badge: a shield with a tick
    by = y + 176
    s += f'<path d="M{cx-22:.1f} {by} h44 v22 q0 22 -22 32 q-22 -10 -22 -32 z" fill="none" stroke="#fff" stroke-width="2.6"/><path d="M{cx-10:.1f} {by+22} l7 8 l14 -16" {A} stroke-width="3"/>'
    s += T(cx, by + 82, S['verified'], 16, 700, 'middle') + T(cx, by + 104, S['service'], 15, 400, 'middle')
    # answer and decline buttons
    ky = y + h - 96
    s += f'<circle cx="{cx-56:.1f}" cy="{ky}" r="24" fill="none" stroke="#fff" stroke-width="2.6"/><circle cx="{cx+56:.1f}" cy="{ky}" r="24" fill="#fff"/>'
    s += f'<path d="M{cx-64:.1f} {ky-8} l16 16 M{cx-48:.1f} {ky-8} l-16 16" {A} stroke-width="3.4"/><path d="M{cx+45:.1f} {ky} l7 8 l14 -16" fill="none" stroke="{P.sh}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    return s
def hospital(x, y, P, S):
    s = f'<rect x="{x}" y="{y-150}" width="150" height="150" fill="{P.sh}" stroke="#fff" stroke-width="2.6"/>'
    s += ''.join(f'<rect x="{x+14+i*34}" y="{y-128+j*36}" width="20" height="18" fill="#fff"/>' for i in range(4) for j in range(3))
    s += f'<rect x="{x+58}" y="{y-34}" width="34" height="34" fill="#fff"/><rect x="{x+48}" y="{y-196}" width="54" height="46" fill="#fff"/>'
    s += f'<path d="M{x+75} {y-188} v30 M{x+60} {y-173} h30" stroke="{P.bg}" stroke-width="7"/>'
    return s + T(x + 75, y - 206, S['hosp'], 14, 700, 'middle')
def shop(x, y, P, S):
    s = f'<rect x="{x}" y="{y-104}" width="132" height="104" fill="{P.sh}" stroke="#fff" stroke-width="2.6"/>'
    s += f'<path d="M{x-6} {y-104} h144 l-8 -22 h-128 z" fill="#fff"/>' + ''.join(f'<path d="M{x+6+k*22} {y-104} q11 16 22 0" fill="#fff"/>' for k in range(6))
    s += f'<rect x="{x+12}" y="{y-70}" width="58" height="44" fill="none" stroke="#fff" stroke-width="2"/><rect x="{x+86}" y="{y-66}" width="32" height="66" fill="#fff"/>'
    s += ''.join(f'<rect x="{x+18+k*16}" y="{y-44}" width="10" height="16" fill="#fff"/>' for k in range(3))
    return s + T(x + 66, y - 136, S['shop'], 14, 700, 'middle')
def plane(x, y, P):
    s = f'<path d="M{x} {y} q0 -12 16 -12 h120 q22 0 34 12 q-12 12 -34 12 h-120 q-16 0 -16 -12 z" fill="#fff"/>'
    s += f'<path d="M{x+70} {y+4} l-26 34 h18 l40 -34 z M{x+70} {y-6} l-22 -22 h14 l30 22 z M{x+8} {y-6} l-6 -26 h12 l18 26 z" fill="#fff"/>'
    return s + ''.join(f'<circle cx="{x+40+k*16}" cy="{y-2}" r="3" fill="{P.bg}"/>' for k in range(6)) + f'<path d="M{x+150} {y-6} q10 0 16 6 h-16 z" fill="{P.bg}"/>'
def draw(P, S, lang):
    a, n = [], []
    a.append(mobile_tower(372, 470, 210))
    a.append(phone(70, 182, 262, 520, P, S))
    g = 470                                   # the street
    a.append(f'<path d="M346 {g} H1240" stroke="#fff" stroke-width="3"/><path d="M346 {g+22} H1240" stroke="#fff" stroke-width="1.6" stroke-dasharray="22 16"/>')
    a.append(truck(430, g, P))
    a.append(hospital(640, g, P, S) + shop(820, g, P, S))
    a.append(car(985, g, P) + motorbike(1110, g, P))
    a.append(plane(1000, 252, P))
    # phase brackets above the street
    n.append(f'<path d="M424 {g-84} v-8 H548 v8" {A} stroke-width="2"/>' + TL(424, g - 128, S['p1'].split(': ', 1)[:1] + [S['p1'].split(': ', 1)[1]], 14, 700))
    n.append(f'<path d="M636 196 v-8 H1180 v8" {A} stroke-width="2"/>' + T(636, 180, S['p2'], 18, 700))
    # who qualifies
    n.append(T(424, g + 58, S['bar1'], 18, 700) + T(424, g + 78, S['bar1t'], 14))
    n.append(T(820, g + 58, S['bar2'], 18, 700) + T(820, g + 78, S['bar2t'], 14))
    n.append(T(201, 730, S['nosale'], 16, 700, 'middle'))
    # timeline to scale
    ty = 660; t0, t1 = dt.date(2026, 7, 20), dt.date(2027, 6, 20); TX = lambda d: 430 + (d - t0).days / (t1 - t0).days * 800
    d = [dt.date(2026, 8, 10), dt.date(2026, 11, 27), dt.date(2027, 5, 26)]; anc = ['start', 'middle', 'end']
    n.append(hatch(P, 'hz', 8, 3) + f'<rect x="{TX(d[1]):.1f}" y="{ty-9}" width="{TX(d[2])-TX(d[1]):.1f}" height="18" fill="url(#hz)" stroke="#fff" stroke-width="2"/>')
    n.append(timeline(430, 1230, ty, [(TX(x), S['ev'][i][0], S['ev'][i][1], anc[i]) for i, x in enumerate(d)], lang))
    n.append(T((TX(d[1]) + TX(d[2])) / 2, ty - 20, S['window'], 15, 700, 'middle'))
    n += [f'<path d="M{TX(dt.date(yr, mo, 1)):.1f} {ty-5} v10" stroke="#fff" stroke-width="1.4"/>' for yr, mo in [(2026, m) for m in range(8, 13)] + [(2027, m) for m in range(1, 7)]]
    return ''.join(a), ''.join(n), (60, 170, 1190, 560)
