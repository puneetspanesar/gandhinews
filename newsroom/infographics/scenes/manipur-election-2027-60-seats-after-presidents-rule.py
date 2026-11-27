# Explainer: Manipur 2027. India locator, the state drawn large (valley and hills are schematic), the House elected in 2022, a timeline to scale.
from gnig import *
import datetime as dt
STR = {
 'en': dict(kicker='Explained · Manipur 2027', headline='Manipur votes after three years of conflict', dek="60 seats, 31 for a majority; the assembly's term ends in March 2027",
            source='Election Commission of India; Ministry of Home Affairs; reports',
            india='India', imphal='Imphal', loktak='Loktak', valley='Imphal valley', mapcap='Manipur: the valley and the hills around it',
            parties=['BJP', 'NPP', 'JD(U)', 'Congress', 'NPF', 'Independents', 'KPA'], maj=['31 for a', 'majority'], seats='60 seats', elected='the assembly elected in 2022',
            kuki='Kuki-Zo MLAs hold 10 of the 60 seats, seven of them with the BJP', killed='At least 306 people killed since May 2023', prule="356 days of President's rule",
            ev=[('March 10, 2022', ['BJP wins 32 of', '60 seats']), ('May 3, 2023', ['Ethnic violence', 'breaks out']), ('February 13, 2025', ["President's rule", 'imposed']),
                ('February 4, 2026', ['Khemchand Singh', 'sworn in']), ('March 2027', ["Assembly's term ends;", 'election due'])]),
 'hi': dict(kicker='समझिए · मणिपुर 2027', headline='तीन साल के संघर्ष के बाद मणिपुर में मतदान', dek='60 सीटें, बहुमत के लिए 31; विधानसभा का कार्यकाल मार्च 2027 में खत्म',
            source='भारत निर्वाचन आयोग; गृह मंत्रालय; रिपोर्टें',
            india='भारत', imphal='इंफाल', loktak='लोकटक', valley='इंफाल घाटी', mapcap='मणिपुर: घाटी और उसके चारों ओर पहाड़',
            parties=['भाजपा', 'एनपीपी', 'जदयू', 'कांग्रेस', 'एनपीएफ', 'निर्दलीय', 'केपीए'], maj=['बहुमत के', 'लिए 31'], seats='60 सीटें', elected='2022 में चुनी गई विधानसभा',
            kuki='कुकी-ज़ो विधायकों के पास 60 में से 10 सीटें, इनमें सात भाजपा के', killed='मई 2023 से कम से कम 306 लोग मारे गए', prule='राष्ट्रपति शासन के 356 दिन',
            ev=[('10 मार्च 2022', ['भाजपा ने 60 में से', '32 सीटें जीतीं']), ('3 मई 2023', ['जातीय हिंसा', 'भड़की']), ('13 फरवरी 2025', ['राष्ट्रपति शासन', 'लगा']),
                ('4 फरवरी 2026', ['खेमचंद सिंह ने', 'शपथ ली']), ('मार्च 2027', ['विधानसभा का कार्यकाल', 'खत्म; चुनाव होना है'])]),
}
def draw(P, S, lang):
    a, n = [], []
    loc, s0 = india_locator(52, 176, 164, marked=('mn',)); a.append(loc)
    x0, y0, x1, y1 = path_bbox(india_paths()['mn'])
    mx, my, mh = 256, 204, 356
    shape, mw, at = state_shape('mn', mx, my, mh, P, clip_id='mnclip'); a.append(shape)
    lx, ly = 52 + (x0 + x1) / 2 * s0, 176 + (y0 + y1) / 2 * s0
    a.append(f'<path d="M{lx+5:.1f} {ly:.1f} L{mx+mw*0.10:.1f} {my+mh*0.47:.1f}" {A} stroke-width="1.6" stroke-dasharray="3 4"/><circle cx="{lx:.1f}" cy="{ly:.1f}" r="7" {A} stroke-width="1.6"/>')
    a.append(T(52, 176 + 164 + 20, S['india'], 13, 700))
    vx, vy = at(0.50, 0.50); ix, iy = at(0.52, 0.47); wx, wy = at(0.44, 0.60)
    hills = ''
    for fy in [0.08 + 0.085 * k for k in range(11)]:
        for fx in [0.08 + 0.105 * k for k in range(9)]:
            px, py = at(fx + (0.05 if int(fy * 100) % 2 else 0), fy)
            if ((px - vx) / (mw * 0.24)) ** 2 + ((py - vy - 14) / (mh * 0.27)) ** 2 < 1: continue
            if ix - 6 < px < ix + 92 and iy - 22 < py < iy + 18: continue
            hills += hill_mark(px, py, 0.9)
    a.append(f'<g clip-path="url(#mnclip)">{hills}</g>')
    a.append(f'<ellipse cx="{vx:.1f}" cy="{vy+14:.1f}" rx="{mw*0.17:.1f}" ry="{mh*0.20:.1f}" fill="{P.bg}" stroke="#fff" stroke-width="1.6" stroke-dasharray="2 5" stroke-linecap="round"/>')
    a.append(f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="6" fill="#fff"/><circle cx="{ix:.1f}" cy="{iy:.1f}" r="11" {A} stroke-width="1.6"/>' + T(ix + 17, iy + 5, S['imphal'], 15, 700))
    a.append(''.join(f'<path d="M{wx-16:.1f} {wy+k*6:.1f} q4 -4 8 0 t8 0 t8 0 t8 0" {A} stroke-width="1.5"/>' for k in range(3)) + T(wx + 22, wy + 12, S['loktak'], 12))
    a.append(T(vx, vy + 14 + mh * 0.20 + 20, S['valley'], 13, 700, 'middle'))
    n.append(T(mx + mw / 2, my + mh + 24, S['mapcap'], 15, 700, 'middle'))
    # the House elected in 2022
    cx, cy = 856, 548; counts = [32, 7, 6, 5, 5, 3, 2]
    hc, seats = hemicycle(cx, cy, [(152, 16), (198, 20), (244, 24)], [(S['parties'][i], c, i == 0) for i, c in enumerate(counts)], P)
    a.append(hc)
    am = (seats[30][0] + seats[31][0]) / 2
    a.append(f'<path d="M{cx+128*math.cos(am):.1f} {cy-128*math.sin(am):.1f} L{cx+259*math.cos(am):.1f} {cy-259*math.sin(am):.1f}" stroke="#fff" stroke-width="2.4" stroke-dasharray="6 5"/>')
    a.append(TL(cx + 118 * math.cos(am), cy - 118 * math.sin(am) + 16, S['maj'], 13, 700, 'middle', 1.25))
    a.append(T(cx, cy - 6, S['seats'], 26, 700, 'middle') + T(cx, cy + 14, S['elected'], 15, 400, 'middle'))
    n.append(T(cx, cy + 44, S['kuki'], 15, 400, 'middle'))
    # timeline to scale, March 2022 to March 2027
    ty = 672; t0, t1 = dt.date(2022, 3, 10), dt.date(2027, 3, 31); TX = lambda d: 48 + (d - t0).days / (t1 - t0).days * 1184
    dates = [dt.date(2022, 3, 10), dt.date(2023, 5, 3), dt.date(2025, 2, 13), dt.date(2026, 2, 4), dt.date(2027, 3, 31)]; anc = ['start', 'start', 'end', 'start', 'end']
    n.append(timeline(48, 1232, ty, [(TX(d), S['ev'][i][0], S['ev'][i][1], anc[i]) for i, d in enumerate(dates)], lang))
    p0, p1 = TX(dates[2]), TX(dates[3])
    n.append(hatch(P, 'hz', 8, 3) + f'<rect x="{p0:.1f}" y="{ty-9}" width="{p1-p0:.1f}" height="18" fill="url(#hz)" stroke="#fff" stroke-width="2"/>' + T((p0 + p1) / 2, ty - 20, S['prule'], 15, 700, 'middle'))
    n.append(T(TX(dates[1]), ty - 20, S['killed'], 15, 700))
    n += [f'<path d="M{TX(dt.date(yr, 1, 1)):.1f} {ty-5} v10" stroke="#fff" stroke-width="1.4"/>' for yr in range(2023, 2028)]
    return ''.join(a), ''.join(n), (236, 190, 990, 420)
