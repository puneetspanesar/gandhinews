// Homepage view model. Layout choices live in /content/homepage.json (which stories go where);
// every title, standfirst, number and date is read from the content collections and tracker data.
import fs from 'node:fs';
import path from 'node:path';
import HOME from '../../content/homepage.json';
import PHOTO_MAP from '../../content/photos.map.json';
import MARKETS_DATA from '../../content/data/markets.json';
// A story whose picture is not ready yet never goes on the homepage (no grey camera boxes).
const hasPic = (id?: string) => !!id && !!(PHOTO_MAP as Record<string, any>)[id] && !(PHOTO_MAP as Record<string, any>)[id].nohome;   // nohome: a broken cover (the same person twice) stays off the homepage
import { content, urlOf, kicker, fmtShort, labelParts, topicLink, iconFor, type Entry } from './site';
import { DATA, tr } from './data';
import { verdictKey, VERDICT_ORDER, type Lang } from './i18n';
// @ts-ignore - plain JS module
import { renderChart, renderInfographic, fmtNum, esc } from './blocks.mjs';
import { iconSvg } from './icons.mjs';
// @ts-ignore - plain JS module
import { ROOT } from './routes.mjs';

export const H = {
  en: {
    briefing: "Today's briefing", morningBrief: 'Get the Morning Brief by email',
    fromDesk: 'From', desk: 'the editorial desk', keyPoints: 'Key points',
    numbers: 'India in numbers', numbersX: 'Latest releases, each with its source', dashboard: 'Economy dashboard',
    topStories: 'Top stories', startHere: 'Start here', explainers: 'Explainers',
    trackers: 'Trackers', trackersX: 'Where things stand, updated as the record changes', allTrackers: 'All trackers',
    dataDesk: 'Data desk', moreCharts: 'Election calendar', early: 'Early 2027', late: 'Late 2027', others: 'Others',
    state: 'State', termEnds: 'Term ends',
    mapSource: (d: string) => `Source: Gandhi News election calendar, as of ${d}. Where a term-end date is not in our calendar, the month the poll is expected is shown.`,
    parl: 'Parliament tracker', sittings: 'Sittings', lsProd: 'Lok Sabha productivity', billsPassed: 'Bills passed',
    bill: 'Bill', cols: ['Introduced', 'Committee', 'Lok Sabha', 'Rajya Sabha'],
    done: 'Done', cur: 'Current stage', not: 'Not yet', skip: 'Not referred', prs: 'Source: PRS Legislative Research',
    fc: 'Fact check', fcX: 'Viral claims, checked against the record', allFc: 'All fact checks', whatWeFound: 'What we found.',
    ask: 'Send us a claim, photo or video to check', steps: ['Trace the original source', 'Check official records', 'Publish verdict and evidence'],
    howRate: 'How we rate claims', method: 'Our method', wa: 'Send on WhatsApp', checked: 'claims checked so far',
    weekAhead: 'The week ahead', explained: 'Explained', allExplainers: 'All explainers', opinion: 'Opinion', opinionX: 'From the editorial desk', allEditorials: 'All editorials',
    more: 'More', corrections: 'Corrections', correctionsNone: 'None yet. When we get something wrong, the correction and the date will appear here, and on the story.', correctionsLog: 'Corrections log',
    pillars: [
      { icon: 'file-text', b: 'Checked against the record', p: 'Every report is built from documents, data and on-record statements, with the official papers linked where they exist.', href: '/standards/' },
      { icon: 'pencil-simple-line', b: 'Corrections in public', p: 'Mistakes are fixed on the story and logged with the date.', href: '/corrections/' },
      { icon: 'scales', b: 'News and opinion kept apart', p: 'Opinion is always labelled and never mixed into reporting.', href: '/standards/' },
      { icon: 'shield-check', b: 'Ownership declared', p: 'Who owns and funds Gandhi News, published in full.', href: '/ownership/' },
    ],
    bypollSeats: (n: number) => `${n} seats`, seat: 'Seat', winner: 'Winner', margin: 'Margin',
    lsProdPrs: 'Lok Sabha productivity (PRS)', rsProdPrs: 'Rajya Sabha productivity (PRS)', qh: 'Lok Sabha Question Hour, whole session', minister: 'Bills passed with only the minister speaking',
    of: 'of', min: 'min', to: 'to',
    trk: {
      billsBig: 'Bills tracked', passed: 'Passed both Houses', inCommittee: 'In committee', failed: 'Defeated or dropped', assent: 'Assent or in force', reported: 'Committee reported',
      winter: 'Reports due in the Winter Session', bills: 'Bills',
      pollsBig: 'elections and bypolls', assembly: 'Assembly elections', bypolls: 'Bypolls, held', rs: 'Rajya Sabha, held', president: 'Presidential vote', next: 'Expected next', assemblies: (n: number) => `${n} assemblies`,
      promisesBig: 'promises tracked', byArea: 'Promises by area', otherAreas: 'Other areas',
      casesBig: 'cases followed', decided: 'Decided', reserved: 'Judgment reserved', pending: 'Pending', other: 'Other stages', reservedOn: 'Judgment reserved on',
    },
  },
  hi: {
    briefing: 'आज की ब्रीफिंग', morningBrief: 'मॉर्निंग ब्रीफ ईमेल पर पाएं',
    fromDesk: '', desk: 'संपादकीय डेस्क से', keyPoints: 'मुख्य बातें',
    numbers: 'आंकड़ों में भारत', numbersX: 'ताज़ा आंकड़े, हर एक के स्रोत के साथ', dashboard: 'अर्थव्यवस्था डैशबोर्ड',
    topStories: 'बड़ी खबरें', startHere: 'यहां से शुरू करें', explainers: 'समझिए',
    trackers: 'ट्रैकर', trackersX: 'अभी क्या स्थिति है, रिकॉर्ड बदलते ही अपडेट', allTrackers: 'सभी ट्रैकर',
    dataDesk: 'डेटा डेस्क', moreCharts: 'चुनाव कैलेंडर', early: '2027 की शुरुआत', late: '2027 का आखिर', others: 'बाकी',
    state: 'राज्य', termEnds: 'कार्यकाल खत्म',
    mapSource: (d: string) => `स्रोत: गांधी न्यूज़ चुनाव कैलेंडर, ${d} की स्थिति। जहां कार्यकाल खत्म होने की तारीख हमारे कैलेंडर में नहीं है, वहां चुनाव का संभावित महीना दिया गया है।`,
    parl: 'संसद ट्रैकर', sittings: 'बैठकें', lsProd: 'लोकसभा का कामकाज', billsPassed: 'विधेयक पास',
    bill: 'विधेयक', cols: ['पेश', 'समिति', 'लोकसभा', 'राज्यसभा'],
    done: 'पूरा', cur: 'अभी इस चरण में', not: 'अभी नहीं', skip: 'समिति को नहीं भेजा', prs: 'स्रोत: पीआरएस लेजिस्लेटिव रिसर्च',
    fc: 'फैक्ट चेक', fcX: 'वायरल दावे, रिकॉर्ड से जांचे गए', allFc: 'सभी फैक्ट चेक', whatWeFound: 'हमने क्या पाया।',
    ask: 'जांच के लिए हमें कोई दावा, फोटो या वीडियो भेजें', steps: ['मूल स्रोत तक पहुंचना', 'सरकारी रिकॉर्ड से मिलान', 'निष्कर्ष और सबूत प्रकाशित करना'],
    howRate: 'हम दावों को कैसे आंकते हैं', method: 'हमारी जांच का तरीका', wa: 'व्हाट्सऐप पर भेजें', checked: 'दावे अब तक जांचे गए',
    weekAhead: 'इस हफ़्ते', explained: 'समझिए', allExplainers: 'सभी लेख', opinion: 'राय', opinionX: 'संपादकीय डेस्क से', allEditorials: 'सभी संपादकीय',
    more: 'और', corrections: 'सुधार', correctionsNone: 'अभी कोई नहीं। जब हमसे कोई गलती होगी, तो सुधार और उसकी तारीख यहां और खबर पर दिखेगी।', correctionsLog: 'सुधारों का रिकॉर्ड',
    pillars: [
      { icon: 'file-text', b: 'रिकॉर्ड से जांची गई', p: 'हर रिपोर्ट दस्तावेज़ों, आंकड़ों और आधिकारिक बयानों पर आधारित है, और जहां मूल दस्तावेज़ उपलब्ध हैं वहां उनका लिंक दिया गया है।', href: '/standards/' },
      { icon: 'pencil-simple-line', b: 'सुधार सबके सामने', p: 'गलतियां खबर पर ही सुधारी जाती हैं और तारीख के साथ दर्ज होती हैं।', href: '/corrections/' },
      { icon: 'scales', b: 'खबर और राय अलग', p: 'राय पर हमेशा लेबल होता है और वह रिपोर्टिंग में नहीं मिलाई जाती।', href: '/standards/' },
      { icon: 'shield-check', b: 'स्वामित्व की घोषणा', p: 'गांधी न्यूज़ का मालिक और फंड देने वाले कौन हैं, पूरी जानकारी।', href: '/ownership/' },
    ],
    bypollSeats: (n: number) => `${n} सीटें`, seat: 'सीट', winner: 'विजेता', margin: 'अंतर',
    lsProdPrs: 'लोकसभा का कामकाज (पीआरएस)', rsProdPrs: 'राज्यसभा का कामकाज (पीआरएस)', qh: 'लोकसभा में प्रश्नकाल, पूरे सत्र में', minister: 'सिर्फ मंत्री के बोलने पर पास हुए विधेयक',
    of: 'में से', min: 'मिनट', to: 'से',
    trk: {
      billsBig: 'विधेयकों पर नज़र', passed: 'दोनों सदनों से पास', inCommittee: 'समिति में', failed: 'नामंज़ूर या निष्प्रभावी', assent: 'मंजूरी मिली या लागू', reported: 'समिति की रिपोर्ट आई',
      winter: 'शीतकालीन सत्र में आने वाली रिपोर्टें', bills: 'विधेयक',
      pollsBig: 'चुनाव और उपचुनाव', assembly: 'विधानसभा चुनाव', bypolls: 'उपचुनाव, हो चुके', rs: 'राज्यसभा, हो चुके', president: 'राष्ट्रपति चुनाव', next: 'आगे क्या', assemblies: (n: number) => `${n} विधानसभाएं`,
      promisesBig: 'वादों पर नज़र', byArea: 'क्षेत्र के हिसाब से वादे', otherAreas: 'बाकी क्षेत्र',
      casesBig: 'मामलों पर नज़र', decided: 'फैसला हो चुका', reserved: 'फैसला सुरक्षित', pending: 'लंबित', other: 'बाकी चरण', reservedOn: 'इन पर फैसला सुरक्षित',
    },
  },
};

const WORDS: Record<Lang, string[]> = {
  en: ['None', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'],
  hi: ['शून्य', 'एक', 'दो', 'तीन', 'चार', 'पांच', 'छह', 'सात', 'आठ', 'नौ', 'दस'],
};
const word = (n: number, lang: Lang) => WORDS[lang][n] ?? String(n);
const stripParen = (s: string) => String(s ?? '').replace(/\s*\([^)]*\)/g, '').trim();
const firstSentence = (s: string) => (String(s).match(/^.*?[.।](\s|$)/)?.[0] ?? s).trim();
const isoLike = (s: string) => /^\d{4}-\d{2}/.test(s);

/** Short publisher name for a one-line source note: "Ministry of ... (NSO)" -> "NSO", "UNI (reporting CGA data)" -> "UNI". */
const ACRONYMS: Record<string, string> = { 'Reserve Bank of India': 'RBI', 'Ministry of Statistics and Programme Implementation': 'MoSPI' };
function shortPub(p: string) {
  const paren = p.match(/\(([A-Z]{2,6})\)/);
  if (paren) return paren[1];
  const base = p.split(/[;(]/)[0].trim();
  return ACRONYMS[base] ?? base;
}
const MONTHS_FULL: Record<string, string> = { Jan: 'January', Feb: 'February', Mar: 'March', Apr: 'April', Jun: 'June', Jul: 'July', Aug: 'August', Sep: 'September', Oct: 'October', Nov: 'November', Dec: 'December' };
const MONTHS_SHORT_RE = /\b(January|February|March|April|June|July|August|September|October|November|December)\b/g;
/** "February to March 2027" -> "Feb to Mar 2027" (English only). */
const abbrMonths = (s: string, lang: Lang) => (lang === 'en' ? String(s).replace(MONTHS_SHORT_RE, (m) => m.slice(0, 3)) : String(s));
/** Drop the year from a period label: "Apr-Jun 2026" -> "Apr-Jun", "week ended 2 Oct 2026" -> "week ended 2 Oct". */
const noYear = (s: string) => stripParen(s).replace(/,?\s+\d{4}\b/g, '').trim();


/** Stale on the front page, in every band (owner, November 12): a preview whose event day has passed, and any headline
 *  that says today, tonight or tomorrow from an earlier day. `enTitle` is the English headline (the rule reads English). */
export function expiredOnHome(d: any, enTitle: string, nowMs = Date.now()) {
  const day = (t: number) => new Date(t + 330 * 60000).toISOString().slice(0, 10);
  const today = day(nowMs), t = String(enTitle || d?.title || '');
  if (day(+new Date(d?.published)) < today && /\b(today|tonight|tomorrow)\b/i.test(t)) return true;
  const up = d?.upcoming?.date;
  if (up && (up instanceof Date ? up.toISOString() : String(up)).slice(0, 10) < today) return true;   // its event day has passed
  if (nowMs - +new Date(d?.published) > 36 * 3600000 && /\\b(?:to (?:spend|visit|open|launch|address|meet|hold|attend|inaugurate|begin|start|host|release|announce|unveil|flag|chair|travel|vote|hear|play|face|take|tour|lay|present|table|decide|rule)|set to|ahead of(?! schedule)|on the eve)\\b/i.test(t)) return true;   // a look-ahead headline, a day and a half on
  return false;
}
/** A headline that pins a figure to a clock time ("30.5% by 1 pm") more than 2 hours ago is stale on the front page. */
function staleClock(d: any) {
  const m = String(d?.title ?? '').match(/\b(?:by|at|till|until|as of)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b/i);
  if (!m) return false;
  const pub = new Date(d.updated ?? d.published);
  const ist = new Date(pub.getTime() + 330 * 60000);
  const h = (+m[1] % 12) + (m[3].toLowerCase() === 'pm' ? 12 : 0);
  const at = Date.UTC(ist.getUTCFullYear(), ist.getUTCMonth(), ist.getUTCDate(), h, +(m[2] ?? 0)) - 330 * 60000;
  return Date.now() - at > 2 * 3.6e6;
}

function need<T>(v: T | undefined, what: string): T {
  if (v === undefined || v === null) throw new Error(`[homepage.json] ${what} not found`);
  return v;
}

function chartFromBody(e: Entry, n: number, lang: Lang) {
  // The lead's visual: the nth chart or infographic block in the story.
  const blocks = [...String((e as any).body ?? '').matchAll(/```(chart|infographic)\n([\s\S]*?)\n```/g)];
  const b = blocks[n - 1];
  if (!b) return '';
  const d = JSON.parse(b[2]);
  return (b[1] === 'chart' ? renderChart(d, lang) : renderInfographic(d, lang, (x: string) => iconSvg(x, 'i'))) as string;
}

/** Sparkline: a polyline that stretches to its box, with a round end dot that stays round. */
export function spark(values: number[], stroke = '#0d0d0d', dot = '#cc0000') {
  if (values.length < 2) return '';
  const mn = Math.min(...values), mx = Math.max(...values);
  const X = (i: number) => (i / (values.length - 1)) * 100;
  const Y = (v: number) => (mx === mn ? 18 : 33 - ((v - mn) / (mx - mn)) * 30);
  const pts = values.map((v, i) => `${X(i).toFixed(2)},${Y(v).toFixed(2)}`).join(' ');
  const n = values.length - 1;
  return `<svg viewBox="0 0 100 36" preserveAspectRatio="none" aria-hidden="true"><polyline points="${pts}" fill="none" stroke="${stroke}" stroke-width="1.6" stroke-linejoin="round" vector-effect="non-scaling-stroke"/><path d="M${X(n).toFixed(2)},${Y(values[n]).toFixed(2)}h0" stroke="${dot}" stroke-width="6" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>`;
}

function indicatorPair(lang: Lang, id: string) {
  const en = need((DATA.en.economy as any).indicators.find((i: any) => i.id === id), `indicator "${id}"`);
  const loc = (DATA[lang].economy as any).indicators.find((i: any) => i.id === id) ?? en;
  return { en, loc };
}

/** Format an indicator's value with its unit, e.g. 5.50%, ₹96.72, $734.6 bn, 72,472.33. */
export function fmtIndicator(lang: Lang, id: string, decimals?: number) {
  const { en } = indicatorPair(lang, id);
  const v = en.latest_value as number;
  const dec = decimals ?? Math.max(0, (String(v).split('.')[1] || '').length);
  const n = fmtNum(v, dec);
  const u: string = en.unit;
  if (u.startsWith('%')) return `${n}%`;
  if (u.startsWith('₹ per')) return `₹${n}`;
  if (u === '$ billion') return lang === 'hi' ? `$${n} अरब` : `$${n} bn`;
  if (u === '₹ lakh crore') return lang === 'hi' ? `₹${n} लाख करोड़` : `₹${n} lakh crore`;
  return n;
}

function periodLabel(p: string, lang: Lang) {
  return isoLike(p) ? fmtShort(p.slice(0, 7), lang) : stripParen(p);
}

function changeLine(lang: Lang, id: string) {
  const { en, loc } = indicatorPair(lang, id);
  const c = en.change_vs_previous;
  if (c?.change == null) return '';
  const sign = fmtNum(c.change, Math.max(1, (String(Math.abs(c.change)).split('.')[1] || '').length), true);
  const pts = c.change_unit === 'percentage points';
  const unit = pts ? (lang === 'hi' ? 'अंक' : 'pts') : '';
  let prevMonth = c.basis === 'previous month' ? stripParen(loc.change_vs_previous?.previous_period ?? c.previous_period ?? '').replace(/\s*\d{4}$/, '') : '';
  if (lang === 'en') prevMonth = MONTHS_FULL[prevMonth] ?? prevMonth;
  if (lang === 'hi') {
    if (c.basis === 'previous month') return `${prevMonth} से ${sign} ${unit}`;
    if (c.basis === 'previous level') return `${sign} ${unit}, ${fmtNum(c.previous_value, 2)}% से`;
    if (/year earlier/.test(c.basis)) return `साल भर पहले से ${sign} ${unit}`;
    return `${sign} ${unit}`;
  }
  if (c.basis === 'previous month') return `${sign} ${unit} on ${prevMonth}`;
  if (c.basis === 'previous level') return `${sign} ${unit}, from ${fmtNum(c.previous_value, 2)}%`;
  if (/year earlier/.test(c.basis)) return `${sign} ${unit} on a year earlier`;
  return `${sign} ${unit}`;
}

// India map (state name -> path id), read from the static map file.
let MAP_IDS: Map<string, string> | null = null;
function mapIds() {
  if (MAP_IDS) return MAP_IDS;
  const svg = fs.readFileSync(path.join(ROOT, 'public/maps/india.svg'), 'utf8');
  MAP_IDS = new Map([...svg.matchAll(/<path id="([a-z]+)"[^>]*><title>([^<]+)<\/title>/g)].map((m) => [m[2], m[1]]));
  return MAP_IDS;
}
// Each state's outline box in public/maps/india.svg, so a state can be drawn on its own (state-by-state block)
let STATE_BOX: Map<string, { id: string; vb: string; sw: string }> | null = null;
export function stateBox(name: string) {
  if (!STATE_BOX) {
    STATE_BOX = new Map();
    const svg = fs.readFileSync(path.join(ROOT, 'public/maps/india.svg'), 'utf8');
    for (const m of svg.matchAll(/<path id="([a-z]+)" d="([^"]+)"[^>]*><title>([^<]+)<\/title>/g)) {
      const toks = m[2].match(/[mlzML]|-?\d*\.?\d+(?:e-?\d+)?/gi) ?? [];
      let cmd = 'm', x = 0, y = 0, sx = 0, sy = 0, first = true, x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      for (let i = 0; i < toks.length; i++) {
        const t = toks[i];
        if (/^[mlzML]$/.test(t)) { cmd = t; if (t === 'z' || t === 'Z') { x = sx; y = sy; } continue; }
        const a = +t, b = +toks[++i];
        if (cmd === 'm' || cmd === 'l') { if (first) { x = a; y = b; } else { x += a; y += b; } } else { x = a; y = b; }
        if (cmd === 'm' || cmd === 'M') { sx = x; sy = y; cmd = cmd === 'm' ? 'l' : 'L'; }
        first = false;
        x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y);
      }
      const pad = Math.max(x1 - x0, y1 - y0) * 0.04;
      STATE_BOX.set(m[3], { id: m[1], sw: (Math.max(x1 - x0, y1 - y0) / 30).toFixed(2), vb: `${(x0 - pad).toFixed(1)} ${(y0 - pad).toFixed(1)} ${(x1 - x0 + 2 * pad).toFixed(1)} ${(y1 - y0 + 2 * pad).toFixed(1)}` });
    }
  }
  return STATE_BOX.get(name) ?? null;
}
const MONTH_IDX: Record<string, number> = { january: 0, february: 1, march: 2, april: 3, may: 4, june: 5, july: 6, august: 7, september: 8, october: 9, november: 10, december: 11 };

export async function homeModel(lang: Lang) {
  const c = (await content())[lang];
  const t = H[lang];
  const D: any = DATA[lang];
  const DE: any = DATA.en;
  const get = (id: string) => need(c.all.get(id), `id "${id}" (${lang})`);
  // A story listed in homepage.json can disappear (held, renamed): skip it instead of failing the whole build.
  const has = (id: string | undefined) => !!id && c.all.has(id);
  const card = (id: string) => {
    const e = get(id);
    return { id, d: e.data as any, href: urlOf(e.data), k: kicker(e.data) };
  };

  // ---- Lead
  // If the chosen lead has no picture yet, the next pictured headline leads (without the lead's own data strip).
  const leadId = [HOME.lead.id, ...HOME.lead.relatedBeside, ...HOME.topStories.list].find((x: string) => hasPic(x) && c.all.get(x)) ?? HOME.lead.id;
  const leadSwapped = leadId !== HOME.lead.id;
  const leadE = get(leadId);
  const lead = {
    ...card(leadId),
    // Lead photo with a news strip over its lower part (lead.overlay). "photo": false hides it.
    swapped: leadSwapped,
    photo: HOME.lead.photo !== false,
    overlay: HOME.lead.overlay && !leadSwapped ? { k: HOME.lead.overlay.kicker[lang], v: HOME.lead.overlay.value[lang], t: HOME.lead.overlay.text[lang] } : null,
    chart: chartFromBody(leadE, HOME.lead.chart ?? 1, lang),
    // Each box is either a tracker indicator or a fixed value from the story (value: {en, hi}).
    dataBox: (leadSwapped ? [] : HOME.lead.dataBox).map((x: any) => ({ ...x, value: x.value ? x.value[lang] : fmtIndicator(lang, x.indicator, x.decimals), label: x.label[lang] })),
    below: HOME.lead.relatedBelow.filter((x: string) => has(x) && hasPic(x) && x !== leadId).map(card),
    beside: HOME.lead.relatedBeside.filter((x: string) => has(x) && hasPic(x) && x !== leadId).map(card),
  };

  // ---- Briefing
  const briefing = HOME.briefing.items.filter((b: any) => has(b.link)).map((b: any) => ({ lead: b.lead[lang], text: b.text[lang], href: urlOf(get(b.link).data), icon: b.icon ?? iconFor(get(b.link).data) }));

  // ---- India in numbers
  const numbers = HOME.numbers.items.map((x: any) => {
    const { en, loc } = indicatorPair(lang, x.indicator);
    const hist = (loc.history ?? en.history ?? []) as any[];
    return {
      label: x.label[lang], icon: x.icon,
      value: fmtIndicator(lang, x.indicator, x.decimals),
      change: changeLine(lang, x.indicator),
      up: (en.change_vs_previous?.change ?? 0) >= 0,
      spark: spark(hist.map((h) => h.value), x.highlight ? '#cc0000' : '#0d0d0d', x.highlight ? '#cc0000' : '#0d0d0d'),
      x0: hist.length ? periodLabel(hist[0].period, lang) : '', x1: hist.length ? periodLabel(hist[hist.length - 1].period, lang) : '',
      src: `${stripParen(loc.period)} · ${shortPub(en.source.publisher)}`,
    };
  });
  const dashHref = urlOf(get(HOME.numbers.tracker).data);

  // ---- Top stories, start here
  const bigId = has(HOME.topStories.big.id) ? HOME.topStories.big.id : [...HOME.topStories.list, ...HOME.lead.relatedBeside].find((x: string) => has(x) && x !== leadId);
  const big = card(bigId);
  const bigAlso = HOME.topStories.big.also.filter(has).map((id: string) => {
    const x = card(id);
    const pre = x.d.type === 'topic' ? (lang === 'hi' ? 'विषय' : 'Topic') : x.d.type === 'explainer' ? t.explained : labelParts(x.d.format_label)[0];
    return { ...x, label: `${pre}: ${x.d.title}` };
  });
  const top = HOME.topStories.list.filter(has).map(card);
  const start = HOME.startHere.filter((id: string) => has(id) && hasPic(id)).map((id: string) => { const x = card(id); return { ...x, icon: iconFor(x.d), meta: labelParts(x.d.format_label).slice(-1)[0] }; });

  // ---- Trackers band
  const trackers = HOME.trackers.filter((tk: any) => has(tk.id)).map((tk: any) => {
    const x = card(tk.id);
    return { ...x, short: tk.title?.[lang] ?? x.d.title.split(':')[0].trim(), area: labelParts(x.d.format_label).slice(-1)[0], line: firstSentence(x.d.standfirst) };
  });
  const T = t.trk;
  const pctOf = (n: number, max: number) => `${Math.max(4, Math.round((n / max) * 100))}%`;
  // Bills
  const bills: any[] = D.bills.bills;
  const st = (s: string[]) => bills.filter((b) => s.includes(b.current_stage)).length;
  const billRows = [
    { l: T.passed, n: st(['passed_both']) },
    { l: T.inCommittee, n: st(['in_committee']) },
    { l: T.failed, n: st(['negatived', 'infructuous']) },
    { l: T.assent, n: st(['assent', 'in_force']), rd: true },
    { l: T.reported, n: st(['committee_reported']) },
  ].sort((a, b) => b.n - a.n);
  const winterGroups = new Map<string, any[]>();
  for (const b of DE.bills.bills) {
    const cm = b.stages.committee;
    if (cm && !cm.report && /Winter Session/.test(cm.report_due ?? '')) {
      if (!winterGroups.has(cm.name)) winterGroups.set(cm.name, []);
      winterGroups.get(cm.name)!.push(bills.find((x) => x.id === b.id) ?? b);
    }
  }
  const winter = [...winterGroups.values()].map((g) => {
    const name = tr(g[0], 'name', lang) as string;
    if (g.length > 1) { const m = name.match(/\(([^()]+)\)\s*$/); if (m) return `${m[1]} ${T.bills}`; }
    return name.replace(/,\s*\d{4}$/, '');
  });
  const billsCard = { big: bills.length, rows: billRows.map((r) => ({ ...r, w: pctOf(r.n, billRows[0].n) })), winter };
  // Economy
  const cpi = indicatorPair(lang, 'cpi-inflation');
  const cpiItem: any = HOME.numbers.items.find((x: any) => x.indicator === 'cpi-inflation');
  const econCard = {
    big: fmtIndicator(lang, 'cpi-inflation'),
    bigLabel: `${cpiItem?.label[lang] ?? stripParen(cpi.loc.name)}, ${stripParen(cpi.loc.period)}`,
    spark: spark(cpi.loc.history.map((h: any) => h.value), '#e6e6e6', '#cc0000'),
    x0: `${noYear(periodLabel(cpi.loc.history[0].period, lang))} ${fmtNum(cpi.loc.history[0].value, 2)}%`,
    x1: `${noYear(periodLabel(cpi.loc.history.at(-1).period, lang))} ${fmtNum(cpi.loc.history.at(-1).value, 2)}%`,
    rows: HOME.numbers.items.filter((x: any) => x.indicator !== 'cpi-inflation').map((x: any) => {
      const { loc } = indicatorPair(lang, x.indicator);
      return { l: x.label[lang], p: noYear(loc.period), v: fmtIndicator(lang, x.indicator, x.decimals) };
    }),
  };
  // Elections
  const er: any[] = D.elections.rows;
  const erEn: any[] = DE.elections.rows;
  const isAssembly = (r: any) => r.house === 'Legislative Assembly';
  const elRows = [
    { l: T.assembly, n: er.filter((r) => isAssembly(r) && r.status !== 'held').length, rd: true },
    { l: T.bypolls, n: er.filter((r) => r.status === 'held' && (isAssembly(r) || r.house === 'Lok Sabha')).length },
    { l: T.rs, n: er.filter((r) => r.status === 'held' && r.house === 'Rajya Sabha').length },
    { l: T.president, n: er.filter((r) => r.house === 'President of India').length },
  ];
  const nextGroups = new Map<string, any[]>();
  for (const r of er.filter((r) => isAssembly(r) && r.status !== 'held')) {
    const key = r.expected_window ?? r.date;
    if (!nextGroups.has(key)) nextGroups.set(key, []);
    nextGroups.get(key)!.push(r);
  }
  const elNext = [...nextGroups.entries()].map(([w, g]) => ({ l: g.length > 1 ? T.assemblies(g.length) : tr(g[0], 'state', lang), v: abbrMonths(w, lang) }));
  const elMax = Math.max(...elRows.map((r) => r.n));
  const elCard = { big: er.length, rows: elRows.map((r) => ({ ...r, w: pctOf(r.n, elMax) })), next: elNext };
  // Budget
  const pr: any[] = D.budget.promises;
  const prEn: any[] = DE.budget.promises;
  const statusLabel = (s: string) => (lang === 'hi' ? D.budget.status_labels_hi?.[s] : null) ?? s;
  const bStat = [
    { s: 'delivered', c: 'var(--red)' }, { s: 'in progress', c: '#e6e6e6' }, { s: 'no update found', c: '#4a4a4a' },
  ].map((x) => ({ ...x, n: prEn.filter((p) => p.status === x.s).length, l: statusLabel(x.s) }));
  const cats = new Map<string, number>();
  for (const p of pr) { const k = tr(p, 'category', lang); cats.set(k, (cats.get(k) ?? 0) + 1); }
  const catList = [...cats.entries()].sort((a, b) => b[1] - a[1]);
  const top3 = catList.slice(0, 3);
  const rest = catList.slice(3).reduce((s, x) => s + x[1], 0);
  const budgetCard = { big: pr.length, stat: bStat, areas: [...top3.map(([l, n]) => ({ l, n })), ...(rest ? [{ l: T.otherAreas, n: rest }] : [])] };
  // Supreme Court
  const cs: any[] = D.sc.cases;
  const scRows = [
    { l: T.decided, n: cs.filter((x) => x.status === 'decided').length },
    { l: T.reserved, n: cs.filter((x) => x.status === 'reserved').length, rd: true },
    { l: T.pending, n: cs.filter((x) => x.status === 'pending').length },
  ];
  scRows.push({ l: T.other, n: cs.length - scRows.reduce((s, r) => s + r.n, 0), gr: true } as any);
  const scMax = Math.max(...scRows.map((r) => r.n));
  const shortCase = (s: string) => s.split(/\s+v\.\s+|\s+बनाम\s+|\s*\(|:/)[0].trim();
  const scCard = {
    big: cs.length,
    rows: scRows.map((r) => ({ ...r, w: pctOf(r.n, scMax) })),
    reserved: cs.filter((x) => x.status === 'reserved').map((x) => ({ l: shortCase(tr(x, 'case', lang)), v: fmtShort(x.last_date, lang, false) })),
  };

  // ---- Data desk: map
  const MAP = HOME.dataDesk.map;
  const assemblies = erEn.filter((r) => isAssembly(r) && r.status !== 'held');
  const ids = mapIds();
  const mapStates = assemblies.map((r) => {
    const loc = er.find((x) => x.id === r.id) ?? r;
    const mon = MONTH_IDX[String(r.expected_window ?? '').split(/\s+/)[0].toLowerCase()] ?? 11;
    const mapId = ids.get(r.state);
    if (!mapId) throw new Error(`[homepage] state "${r.state}" is not on the India map`);
    return {
      mapId, early: mon < 6, name: tr(loc, 'state', lang),
      when: r.term_end ? fmtShort(r.term_end, lang) : abbrMonths(String(loc.expected_window), lang),
      sort: r.term_end ?? `${r.expected_window?.match(/\d{4}/)?.[0]}-${String(mon + 1).padStart(2, '0')}-99`,
    };
  }).sort((a, b) => a.sort.localeCompare(b.sort));
  const fill = new Map(mapStates.map((s) => [s.mapId, s.early ? '#cc0000' : '#0d0d0d']));
  const allMapIds = [...ids.values()];
  const n = mapStates.length;
  const mapModel = {
    href: urlOf(get(MAP.tracker).data),
    topicHref: urlOf(get(MAP.topic).data),
    kicker: MAP.kicker[lang],
    title: MAP.title[lang].replace('{n}', lang === 'en' ? word(n, lang) : word(n, lang)),
    text: MAP.text[lang],
    paths: allMapIds.map((id) => ({ id, fill: fill.get(id) ?? '#e2e2e2' })),
    states: mapStates,
    asOf: fmtShort(String(DE.elections.updated).slice(0, 10), lang),
  };

  // ---- Data desk: parliament tracker
  const PT = HOME.dataDesk.parliament;
  const sess = need(D.sessions.sessions.find((s: any) => s.id === PT.session), `session "${PT.session}"`);
  const sessEn = DE.sessions.sessions.find((s: any) => s.id === PT.session);
  const sd = (s: string | null) => (s ? fmtShort(s, lang, false) : '');
  const ptBills = PT.bills.map((bid: string) => {
    const b = need(bills.find((x) => x.id === bid), `bill "${bid}"`);
    const s = b.stages; const cs2 = b.current_stage; const cm = s.committee;
    const lsHome = b.house_introduced === 'Lok Sabha';
    const committee = cm ? (cs2 === 'in_committee' ? 'c' : 'y') : 's';
    const waitingFloor = cs2 === 'committee_reported' || (!cm && !s.passed_ls && !s.passed_rs);
    const ls = s.passed_ls ? 'y' : waitingFloor && lsHome ? 'c' : (s.passed_rs && !lsHome ? 'c' : 'n');
    const rs = s.passed_rs ? 'y' : (s.passed_ls && lsHome ? 'c' : waitingFloor && !lsHome ? 'c' : 'n');
    let note = '';
    if (cs2 === 'in_committee') note = lang === 'hi'
      ? `${cm.type === 'joint' ? 'संयुक्त समिति' : 'स्थायी समिति'} के पास, ${sd(cm.referred)} से`
      : `With ${cm.type === 'joint' ? 'joint' : 'standing'} committee since ${sd(cm.referred)}`;
    else if (cs2 === 'committee_reported') note = lang === 'hi' ? `समिति की रिपोर्ट ${sd(cm.report)}` : `Committee reported ${sd(cm.report)}`;
    else if (cs2 === 'passed_both') note = lang === 'hi' ? `दोनों सदनों से पास, ${sd(s.passed_rs ?? s.passed_ls)}` : `Passed both Houses, ${sd(s.passed_rs ?? s.passed_ls)}`;
    else if (cs2 === 'assent') note = lang === 'hi' ? `राष्ट्रपति की मंजूरी, ${sd(s.assent)}` : `Assent ${sd(s.assent)}`;
    else if (cs2 === 'in_force') note = lang === 'hi' ? `लागू, मंजूरी ${fmtShort(s.assent, lang)}` : `In force; assent ${fmtShort(s.assent, lang)}`;
    return { name: tr(b, 'name', lang), note, cells: ['y', committee, ls, rs], href: `${urlOf(get(PT.tracker).data)}#${b.id}` };
  });
  const parl = {
    name: sess.name, href: urlOf(get(PT.tracker).data),
    sittings: sessEn.lok_sabha.sittings, prod: `${sessEn.lok_sabha.productivity_prs_pct}%`, passed: sessEn.bills_passed_prs,
    bills: ptBills,
  };

  // ---- Fact check
  const fcAll = c.articles.filter((e: any) => e.data.type === 'factcheck');
  // the three newest fact checks, always (owner, November 7: every section updates by itself, never a hand-kept list)
  const fcNewest = [...fcAll].filter((e: any) => e.data.factcheck && hasPic(e.data.id)).sort((a: any, b: any) => +new Date(b.data.published) - +new Date(a.data.published)).slice(0, 3).map((e: any) => e.data.id);
  const fcCards = fcNewest.filter((id: string) => has(id)).map((id: string) => {
    const x = card(id);
    const f = need(x.d.factcheck, `factcheck block for "${id}"`);
    const pubs: string[] = [];
    for (const s of [...x.d.sources].sort((a: any, b: any) => Number(!!b.primary) - Number(!!a.primary))) {
      const pub = s.publisher ?? s.title;
      if (pubs.some((p) => p.startsWith(pub))) continue;
      const dt = s.date ? fmtShort(s.date instanceof Date ? s.date.toISOString().slice(0, 10) : String(s.date), lang, false) : '';
      pubs.push(dt ? `${pub}, ${dt}` : pub);
      if (pubs.length === 3) break;
    }
    return { ...x, vk: verdictKey(f.verdict), verdict: f.verdict, claim: f.claim, who: f.claimant, found: f.finding, src: pubs.join('; ') };
  });
  const counts = VERDICT_ORDER.map((v) => ({ v, n: fcAll.filter((e: any) => verdictKey(e.data.factcheck.verdict) === v).length })).filter((x) => x.n > 0);
  const fcStats = { total: fcAll.length, counts };

  // ---- Explained, opinion
  const explained = HOME.explained.filter((x: any) => has(x.id)).map((x: any) => ({ ...card(x.id), topic: labelParts(get(x.id).data.format_label).slice(-1)[0], kn: x.kn.map((k: any) => ({ v: k.value[lang], l: k.label[lang] })) }));
  // the homepage list first, then the newest editorials to make up seven (owner, November 8: a denser opinion block)
  const opIds = [...HOME.opinion.filter((id: string) => has(id))];
  for (const e of [...c.articles].filter((x: any) => x.data.type === 'editorial').sort((a: any, b: any) => +new Date(b.data.published) - +new Date(a.data.published))) { if (opIds.length >= 7) break; if (!opIds.includes(e.data.id)) opIds.push(e.data.id); }
  const opinion = await Promise.all(opIds.map(async (id: string) => {
    const x = card(id);
    const tp = x.d.topics[0] ? (await topicLink(x.d.topics[0], lang)).label : '';
    return { ...x, topic: tp, icon: iconFor(x.d) };
  }));

  // ---- Section blocks
  const sections = HOME.sections.map((s: any) => {
    const ok = [s.lead, ...(s.list ?? [])].filter((x: string) => has(x) && hasPic(x));
    const out: any = { key: s.section, lead: ok[0] ? card(ok[0]) : null, list: ok.slice(1).map(card), module: null };
    const m = s.module;
    if (m?.type === 'bypolls' && has(m.article)) {
      const art = get(m.article);
      const blk = String((art as any).body).match(/```chart\n([\s\S]*?)\n```/);
      const chart = JSON.parse(need(blk?.[1], `chart in "${m.article}"`));
      const rows = chart.data.map((r: any) => {
        const i = r.label.lastIndexOf(',');
        return { seat: r.label.slice(0, i).trim(), party: r.label.slice(i + 1).trim(), margin: fmtNum(r.value, 0) };
      });
      out.module = { type: 'bypolls', title: chart.title, n: rows.length, rows, href: urlOf(art.data) };
    } else if (m?.type === 'markets') {
      out.module = {
        type: 'markets',
        rows: m.indicators.map((id: string) => {
          const { en, loc } = indicatorPair(lang, id);
          const pct = en.change_vs_previous?.change_pct;
          return { l: `${stripParen(loc.name)}, ${noYear(loc.period)}`, v: fmtIndicator(lang, id, en.unit === 'index points' ? 2 : undefined), pct: pct != null ? `${pct > 0 ? '+' : pct < 0 ? '−' : ''}${Math.abs(pct).toFixed(2)}%` : null, up: (pct ?? 0) >= 0 };
        }),
      };
    } else if (m?.type === 'session') {
      const se = DE.sessions.sessions.find((x: any) => x.id === m.session);
      const sl = D.sessions.sessions.find((x: any) => x.id === m.session) ?? se;
      out.module = {
        type: 'session', name: sl.name, when: `${sd(se.start)} ${t.to} ${sd(se.end)}`,
        rows: [
          { l: t.lsProdPrs, v: `${se.lok_sabha.productivity_prs_pct}%` },
          { l: t.rsProdPrs, v: `${se.rajya_sabha.productivity_prs_pct}%` },
          { l: t.qh, v: `${se.lok_sabha.question_hour_minutes} ${t.min}` },
          { l: t.minister, v: lang === 'hi' ? `${se.lok_sabha.bills_passed_excl_finance_appropriation} में से ${se.lok_sabha.bills_passed_with_only_minister_speaking}` : `${se.lok_sabha.bills_passed_with_only_minister_speaking} of ${se.lok_sabha.bills_passed_excl_finance_appropriation}` },
        ],
      };
    }
    return out;
  });

  // ---- The week ahead (editor's diary in homepage.json)
  const ENC = (await content()).en;
  // a diary line links to a story only when that story is about the same thing and is not itself out of date (owner, November 12)
  const weekLinkOk = (x: any) => { const d: any = (ENC.all.get(x.link) as any)?.data; if (!d || expiredOnHome(d, String(d.title ?? ''))) return false;
    const tw = new Set(String(x.text?.en ?? '').toLowerCase().match(/[a-z]{5,}/g) ?? []); return String(x.link).split('-').some((w: string) => w.length >= 5 && tw.has(w)); };
  const week = (HOME.weekAhead ?? []).map((x: any) => ({ icon: x.icon, date: x.date[lang], text: x.text[lang], href: has(x.link) && weekLinkOk(x) ? urlOf(get(x.link).data) : null }));

  // ---- 2026 front page (Gandhi News): headline grid, live band, India block, markets band, other-language links
  const used = new Set<string>([lead.id, ...lead.below.map((x: any) => x.id)]);
  const short = (x: any) => {
    const k = labelParts(x.d.format_label).slice(-1)[0] ?? '';
    return { ...x, kk: k && !String(x.d.title).toLowerCase().startsWith(k.toLowerCase()) ? k : '' };
  };
  const pick = (ids: (string | undefined)[], n: number) => {
    const out: any[] = [];
    for (const id of ids) {
      if (!id || out.length >= n || used.has(id) || !c.all.get(id) || !hasPic(id)) continue;
      if ((c.all.get(id) as any).data.type === 'news' && (Date.now() - +new Date((c.all.get(id) as any).data.published)) / 3.6e6 > 168) continue;  // owner (November 9): sections below the top may run up to 7 days old
      used.add(id); out.push(short(card(id)));
    }
    return out;
  };
  const sec = (k: string): any => HOME.sections.find((s: any) => s.section === k) ?? {};
  // Backfill: when a chosen story is held back (no picture yet), the newest pictured stories fill the gap, so no slot is ever empty.
  const freshIds = (secs?: string[]) => [...c.articles].filter((x: any) => x.data.type === 'news' && hasPic(x.data.id) && (!secs || secs.includes(x.data.section)))
    .sort((a: any, b: any) => +new Date(b.data.published) - +new Date(a.data.published)).slice(0, 40).map((x: any) => x.data.id);
  const chosen = pick([...HOME.lead.relatedBeside, HOME.topStories.big.id, ...HOME.topStories.list, ...HOME.topStories.big.also], 8);
  // Backfill never repeats a subject already in the headlines (same distinctive word in the slug: murasu, qeshm...)
  // and never puts a third story from one section in.
  const words = (id: string) => id.split('-').filter((w) => w.length >= 6 && !/^(points|crore|percent|record|october|november|december|supreme|minister|series|tonight|monday|tuesday|wednesday|thursday|friday|saturday|sunday)$/.test(w));
  const taken = new Set([lead.id, ...chosen.map((x: any) => x.id)].flatMap(words));
  const secCount = (sec: string) => chosen.filter((x: any) => x.d.section === sec).length;
  for (const id of freshIds()) {
    if (chosen.length >= 8) break;
    if (used.has(id) || words(id).some((w) => taken.has(w))) continue;
    const e: any = c.all.get(id); if (!e || secCount(e.data.section) >= 2) continue;
    used.add(id); chosen.push(short(card(id))); words(id).forEach((w) => taken.add(w));
  }
  const headlines = chosen;
  // ---- Desks: world, science and tech, sports. Never repeat a story or a photo already shown above, and never show
  // news older than 48 hours (owner's rule).
  const shownSrc = new Set<string>(  // same alt text = same photo (reused photos get new file names)
    [lead.id, ...headlines.map((x: any) => x.id), ...lead.below.map((x: any) => x.id)].map((id) => (PHOTO_MAP as any)[id]?.alt).filter(Boolean));
  const shownIds = new Set<string>([lead.id, ...headlines.map((x: any) => x.id), ...lead.below.map((x: any) => x.id)]);
  const ageH = (id: string) => (Date.now() - +new Date((c.all.get(id) as any)?.data.published)) / 3.6e6;
  const deskFill = (sec: string) => [...c.articles].filter((x: any) => x.data.type === 'news' && x.data.section === sec && hasPic(x.data.id)).sort((a: any, b: any) => +new Date(b.data.published) - +new Date(a.data.published)).slice(0, 12).map((x: any) => x.data.id);
  const desks = (HOME.desks ?? []).map((s: any) => {
    const pool = [...new Set([s.lead, ...(s.list ?? []), ...deskFill(s.section)])].filter((x: string) => has(x) && hasPic(x) && !shownIds.has(x));
    // owner (November 9): only the top of the page must be fresh; desks may run stories up to 7 days old, newest first
    const fresh = pool.filter((x) => ageH(x) <= 168), older: string[] = [];
    const ok: string[] = []; const src = new Set(shownSrc);
    // Same alt text can mean the same photo reused: check:photos already keeps a source photo out of two stories within 7 days,
    // so the alt test is only needed for older stories (two Kohli photos from this week share an alt but are different pictures).
    for (const x of [...fresh, ...older]) { const p = (PHOTO_MAP as any)[x]?.alt; if (p && src.has(p) && ageH(x) > 168) continue; if (p) src.add(p); ok.push(x); if (ok.length >= 5) break; }
    // a desk shows a full row (4 cards, sport 3) or is left out: never a half-empty row
    return ok.length >= (s.section === 'sports' ? 3 : 4) ? { key: s.section, lead: card(ok[0]), list: ok.slice(1).map(card) } : null;
  }).filter(Boolean);

  const india = pick([sec('states').lead, ...(sec('politics').list ?? []), ...(sec('states').list ?? []), ...(sec('policy').list ?? []), sec('policy').lead, ...freshIds(['states', 'politics', 'policy'])], 3);
  const econ = pick([sec('economy').lead, ...(sec('economy').list ?? []), ...freshIds(['economy'])], 3);
  const L0: any = HOME.lead;
  const leadTopic = leadE.data.topics?.[0] ? (await topicLink(leadE.data.topics[0], lang)).label : '';
  const live = {
    title: L0.live?.title?.[lang] || leadTopic || lead.k,
    feature: lead.below[0] ? short(lead.below[0]) : null,
    // Never an empty column: when the running story has fewer than two follow-ups, fill with the newest pictured stories from the lead's section.
    filler: lead.below.length < 3,
    // Always three follow-ups in the right column: the running story's own updates first, then the newest pictured stories from the lead's section that are not already in the headlines.
    list: [...lead.below.slice(1).filter((x: any) => !staleClock(x.d)), ...c.articles.filter((x: any) => x.data.type === 'news' && x.data.section === lead.d.section && (Date.now() - +new Date(x.data.published)) / 3.6e6 <= 24 && x.data.id !== lead.id && !lead.below.some((b: any) => b.id === x.data.id) && !chosen.some((h: any) => h.id === x.data.id) && hasPic(x.data.id)).slice(0, 3).map((x: any) => card(x.data.id))].slice(0, 3).map(short),
    points: (lead.d.keyPoints ?? []).map((k: string) => String(k).replace(/\*\*/g, '')),
    facts: lead.dataBox.slice(0, 3),
  };
  // Charts for the markets band
  const hist = (id: string) => { const { en, loc } = indicatorPair(lang, id); return ((loc.history ?? en.history ?? []) as any[]).slice(-8); };
  const W = 330, Ht = 160;
  const lineChart = (id: string, label: string) => {
    const h = hist(id); if (h.length < 2) return '';
    const vs = h.map((x) => x.value as number);
    const mn = Math.min(...vs), mx = Math.max(...vs);
    const step = Math.pow(10, Math.floor(Math.log10(mx - mn || 1)));
    const lo = Math.floor(mn / step) * step, hi2 = Math.ceil(mx / step) * step;
    const X = (i: number) => 48 + (i * (W - 60)) / (vs.length - 1);
    const Y = (v: number) => 130 - ((v - lo) / (hi2 - lo || 1)) * 118;
    const ticks = [lo, hi2];
    const pts = vs.map((v, i) => `${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');
    const last = vs.length - 1;
    const f = (v: number) => fmtNum(v, step >= 1 ? 0 : 2);
    return `<svg viewBox="0 0 ${W} ${Ht}" width="100%" role="img" aria-label="${esc(label)}">`
      + ticks.map((t) => `<line x1="48" y1="${Y(t).toFixed(1)}" x2="${W - 6}" y2="${Y(t).toFixed(1)}" stroke="#3a3a3a"/><text x="0" y="${(Y(t) + 4).toFixed(1)}" font-size="9.5" fill="#fff">${f(t)}</text>`).join('')
      + `<polyline points="${pts}" fill="none" stroke="#fff" stroke-width="2.5" stroke-linejoin="round"/>`
      + `<circle cx="${X(last).toFixed(1)}" cy="${Y(vs[last]).toFixed(1)}" r="4.5" fill="#ff4d4d"/>`
      + `<text x="48" y="152" font-size="9.5" fill="#fff">${esc(periodLabel(h[0].period, lang))}</text><text x="${W - 6}" y="152" font-size="9.5" fill="#fff" text-anchor="end">${esc(periodLabel(h[last].period, lang))}</text></svg>`;
  };
  const barChart = (id: string, label: string) => {
    const h = hist(id); if (h.length < 2) return '';
    const vs = h.map((x) => x.value as number);
    const mx = Math.ceil(Math.max(...vs));
    const bw = (W - 40) / vs.length;
    const Y = (v: number) => 130 - (v / (mx || 1)) * 110;
    const last = vs.length - 1;
    return `<svg viewBox="0 0 ${W} ${Ht}" width="100%" role="img" aria-label="${esc(label)}">`
      + [mx / 2, mx].map((t) => `<line x1="30" y1="${Y(t).toFixed(1)}" x2="${W - 4}" y2="${Y(t).toFixed(1)}" stroke="#3a3a3a"/><text x="0" y="${(Y(t) + 4).toFixed(1)}" font-size="9.5" fill="#fff">${fmtNum(t, 0)}%</text>`).join('')
      + `<line x1="30" y1="130" x2="${W - 4}" y2="130" stroke="#fff"/>`
      + vs.map((v, i) => `<rect x="${(34 + i * bw).toFixed(1)}" y="${Y(v).toFixed(1)}" width="${(bw - 9).toFixed(1)}" height="${(130 - Y(v)).toFixed(1)}" fill="${i === last ? '#ff4d4d' : '#fff'}"/>`).join('')
      + `<text x="${(34 + last * bw + (bw - 9) / 2).toFixed(1)}" y="${(Y(vs[last]) - 6).toFixed(1)}" font-size="9.5" font-weight="700" fill="#fff" text-anchor="middle">${fmtNum(vs[last], 2)}%</text>`
      + `<text x="34" y="146" font-size="9.5" fill="#fff">${esc(periodLabel(h[0].period, lang))}</text><text x="${W - 4}" y="146" font-size="9.5" fill="#fff" text-anchor="end">${esc(periodLabel(h[last].period, lang))}</text></svg>`;
  };
  const sx = indicatorPair(lang, 'sensex'), cp = indicatorPair(lang, 'cpi-inflation');
  const markets = {
    asOf: fmtShort(sx.en.release_date, lang, false),
    sensexTitle: lang === 'hi' ? 'सेंसेक्स, पिछले आठ कारोबारी दिन' : 'Sensex, last eight sessions',
    sensex: lineChart('sensex', lang === 'hi' ? 'पिछले आठ कारोबारी दिनों में सेंसेक्स' : 'Sensex over the last eight sessions'),
    cpiTitle: lang === 'hi' ? `खुदरा महंगाई, ${stripParen(cp.loc.period)}` : `Retail inflation to ${stripParen(cp.loc.period)}`,
    cpi: barChart('cpi-inflation', lang === 'hi' ? 'आठ महीनों की खुदरा महंगाई' : 'Retail inflation over eight months'),
    figs: [
      { l: lang === 'hi' ? 'निफ्टी 50' : 'Nifty 50', v: fmtIndicator(lang, 'nifty-50', 2) },
      { l: lang === 'hi' ? 'रुपया प्रति डॉलर' : 'Rupee per dollar', v: fmtIndicator(lang, 'usd-inr', 2) },
      { l: lang === 'hi' ? 'रेपो रेट' : 'Repo rate', v: fmtIndicator(lang, 'repo-rate', 2) },
    ],
  };
  // The same top stories in the other language
  const oc = (await content())[lang === 'en' ? 'hi' : 'en'];
  const altLang = [lead.id, ...headlines.map((x: any) => x.id)].map((id) => oc.all.get(id)).filter(Boolean).slice(0, 4)
    .map((e: any) => ({ title: e.data.title, href: urlOf(e.data) }));

  // ---- Dense front page (owner, November 7: the Indian Express style). Every block fills itself from the newest stories,
  // never shows one story twice, never news older than 48 hours, never a stale clock figure.
  const enLabel = (id: string) => String((ENC.all.get(id) as any)?.data.format_label ?? '');
  const enTitle = (id: string) => String((ENC.all.get(id) as any)?.data.title ?? '');
  const dense = (() => {
    const seen = new Set<string>([lead.id]);
    const age = (id: string) => (Date.now() - +new Date((c.all.get(id) as any)?.data.published)) / 3.6e6;
    const real = (id: string) => hasPic(id) && !(PHOTO_MAP as any)[id]?.graphic;
    const sameSubj = (a: string, b: string) => { const wb = new Set(words(b)); return words(a).filter((w) => wb.has(w)).length >= 2; };
    const pool = (secs: string[] | null, h = 168) => [...c.articles]   // sections: newest first, up to 7 days (owner, November 9)
      .filter((x: any) => x.data.type === 'news' && (!secs || secs.includes(x.data.section)) && age(x.data.id) <= h && hasPic(x.data.id) && !staleClock(x.data) && !expiredOnHome(x.data, enTitle(x.data.id)))
      .filter((x: any) => !((HOME as any).drop ?? []).includes(x.data.id))   // refresh_home.py --drop also keeps these out of the dense blocks (editor, hourly-13, November 13: dropped previews still filled Must Read)
      .sort((a: any, b: any) => +new Date(b.data.published) - +new Date(a.data.published)).map((x: any) => x.data.id as string);
    const take = (ids: string[], n: number, photoFirst = false) => {
      const ok = [...new Set(ids)].filter((id) => !seen.has(id) && c.all.get(id) && age(id) <= 168 && !expiredOnHome(get(id).data, enTitle(id)));
      if (photoFirst) { const i = ok.findIndex(real); if (i > 0) ok.unshift(ok.splice(i, 1)[0]); }
      // one story per subject in a band (owner, November 12): the newest stays, so a preview never sits beside its result
      const out: string[] = [];
      for (const id of ok) { if (out.length >= n) break; if (!out.some((o) => sameSubj(o, id))) out.push(id); }
      out.forEach((id) => seen.add(id));
      return out.map((id) => ({ ...short(card(id)), st: labelParts(get(id).data.format_label).slice(-1)[0] ?? '', real: real(id) }));
    };
    const hl = headlines.map((x: any) => x.id);
    const leadLinks = take([...lead.below.map((x: any) => x.id), ...pool(['politics', 'policy', 'states', 'world', 'economy'].filter((s) => s !== lead.d.section), 24)], 6);   // no older pieces of the lead's own running story under it (editor, 18:00 run, November 11)   // three rows under the lead (hourly-06, November 13: 213px gap under the lead at 1440px with two rows)
    // the middle column always opens with a real photo: from the headlines, else the newest pictured news of the last 24 hours
    const second = take([...hl, ...pool(['politics', 'policy', 'states', 'world', 'economy'], 24)].filter((id) => real(id) && !['sports', 'science', 'tech'].includes(get(id).data.section)), 1);
    const secN: Record<string, number> = { [lead.d.section]: 1 }; second.forEach((x: any) => { const sc = get(x.id).data.section; secN[sc] = (secN[sc] ?? 0) + 1; });
    const capSec = (ids: string[]) => [...new Set(ids)].filter((id) => !seen.has(id) && c.all.get(id)).filter((id) => { const sc = get(id).data.section; if ((secN[sc] ?? 0) >= 2) return false; secN[sc] = (secN[sc] ?? 0) + 1; return true; });   // rule 14: at most two per section in the top eight (18:00 run, November 11)
    const col2 = take(capSec([...hl, ...pool(['politics', 'policy', 'states', 'world', 'economy'], 24), ...pool(null, 23)]).filter((id) => age(id) <= 23), 7);   // seven lines in English too (hourly-23, November 12: 193px gap at 1440px with six); six lines: five left a gap under the middle column when the Hindi lead headline runs to three lines (stall check, November 10)
    const must = take([...pool(['politics', 'states', 'world', 'economy', 'policy'], 24), ...pool(['politics', 'states', 'world', 'economy', 'policy'], 48)], 6);   // six rows: 209px gap under Must Read on /hi/ at 1440px, hourly-16 November 13; a quiet morning tops up from the last 48 hours so the column never ends short (08:00 run, November 11)
    // ---- news-dense blocks (owner, November 8): headline lists grouped the way readers look for news
    const isCourt = (id: string) => /Courts|Supreme Court|High Court/.test(enLabel(id)) || /Supreme Court|High Court/.test(enTitle(id));
    const courts = take(pool(['politics', 'policy', 'states']).filter(isCourt), 5);
    const PIC_IC: [RegExp, string][] = [[/Defence|Armed/, 'shield-check'], [/Home Affairs|Police|security/i, 'police-car'], [/Health/, 'drop'], [/Fuel|Oil|Petrol/, 'gas-pump'], [/Rail/, 'train'], [/Trade|Commerce/, 'handshake'], [/Agri|Farm|Food/, 'plant'], [/Education/, 'scroll'], [/Election/, 'flag-banner']];
    // alone (no courts list), policy fills two columns of three
    const policy = take(pool(['policy']), courts.length >= 3 ? 5 : 6).map((x: any) => ({ ...x, ic: (PIC_IC.find(([rx]) => rx.test(enLabel(x.id))) ?? [null, 'bank'])[1] }));
    // courts and policy sit side by side: equal lengths so neither column leaves empty space; a courts list under 3 is dropped
    if (courts.length && courts.length < 3) courts.length = 0;
    if (courts.length && policy.length > courts.length) policy.length = courts.length;
    if (policy.length && courts.length > policy.length) courts.length = policy.length;
    const politics = take(pool(['politics']), 7, true);
    // the Politics band always fills both columns (owner, November 9): top up from Parliament, then States, then Policy
    if (politics.length < 7) politics.push(...take(pool(['parliament', 'states', 'policy']), 7 - politics.length));
    // state by state: every state with fresh news, the busiest first, up to three headlines each
    const stIds = pool(['states']).filter((id) => !seen.has(id)).filter((id, i, all) => !all.slice(0, i).some((o) => sameSubj(o, id)));   // one story per subject across the whole grid
    const byState = new Map<string, string[]>();
    for (const id of stIds) { const k = labelParts(get(id).data.format_label).slice(-1)[0] ?? ''; const ek = enLabel(id).split('/').pop()!.trim(); if (!k || /Weather|Aviation|security/i.test(ek)) continue; if (!byState.has(k)) byState.set(k, []); byState.get(k)!.push(id); }
    for (const [k, ids] of byState) { const f = ids.filter((id) => age(id) <= 96); if (!f.length || age(f[0]) > 48) byState.delete(k); else byState.set(k, f); }   // a state shows only with news from the last two days, and nothing older than four (owner, November 12)
    const stateGrid = [...byState.entries()].sort((a, b) => b[1].length - a[1].length).slice(0, 8)
      .map(([name, ids]) => ({ name, shape: stateBox(enLabel(ids[0]).split('/').pop()!.trim()), items: take(ids, 3), href: `${lang === 'hi' ? '/hi' : ''}/states/` })).filter((g) => g.items.length > 0);
    // world by region, from the English label
    const REG: [string, RegExp, string][] = [['me', /Middle East|Iran|Israel|Gaza|Saudi|Qatar|Yemen|Iraq|Syria|Lebanon|Gulf/, lang === 'hi' ? 'पश्चिम एशिया' : 'Middle East'], ['sa', /Pakistan|Bangladesh|Nepal|Sri Lanka|Afghanistan|Bhutan|Maldives|Myanmar|South Asia/, lang === 'hi' ? 'दक्षिण एशिया' : 'South Asia'], ['am', /United States|US|America|Canada|Brazil|Mexico/, lang === 'hi' ? 'अमेरिका' : 'Americas'], ['eu', /Europe|UK|Britain|Russia|Ukraine|France|Germany/, lang === 'hi' ? 'यूरोप' : 'Europe'], ['ap', /China|Japan|Korea|Australia|New Zealand|Asia|Pacific|Taiwan|Philippines|Indonesia/, lang === 'hi' ? 'एशिया-प्रशांत' : 'Asia-Pacific']];
    const wIds = pool(['world']).filter((id) => !seen.has(id));
    const regOf = (id: string) => (REG.find(([, rx]) => rx.test(enLabel(id).split('/').pop() ?? '')) ?? REG.find(([, rx]) => rx.test(enTitle(id))) ?? [null])[0];
    const regIds = (key: string) => wIds.filter((id) => regOf(id) === key);
    const regions = REG.filter(([key]) => regIds(key).length >= 2).map(([key, , name]) => ({ key, name, items: take(regIds(key), 3) })).filter((r) => r.items.length > 0);
    const worldRest = take(wIds, 3);
    if (worldRest.length) regions.push({ key: 'ot', name: lang === 'hi' ? 'और दुनिया' : 'Elsewhere', items: worldRest });
    const states: any[] = [];
    const econ = take(pool(['economy']), 8, true);
    // three columns at the foot: world, sports, science; a column with fewer than three fresh stories gives way to policy, then politics
    const cols = [['sports', ['sports']], ['science', ['science', 'tech']], ['policy', ['policy']], ['politics', ['politics']]]
      .map(([key, secs]: any) => { const ids = pool(secs).filter((id) => !seen.has(id)); return ids.length >= 3 ? { key, items: take(ids, 4, true) } : null; })
      .filter(Boolean).slice(0, 2);
    const MK: any = MARKETS_DATA;
    const row = (id: string) => [...(MK.indices ?? []), ...(MK.rates ?? [])].find((r: any) => r.id === id);
    const sxh = ((row('sensex')?.history ?? []) as any[]).slice(-22).map((x: any) => x.close as number);
    const mn = Math.min(...sxh), mx = Math.max(...sxh);
    const spark = sxh.length > 1 ? sxh.map((v, i) => `${(i * 280 / (sxh.length - 1)).toFixed(1)},${(62 - (v - mn) / (mx - mn || 1) * 56).toFixed(1)}`).join(' ') : '';
    const sxFirst = ((row('sensex')?.history ?? []) as any[]).slice(-22)[0]?.date;
    const mkRows = [['nifty-50', lang === 'hi' ? 'निफ्टी 50' : 'Nifty 50'], ['nifty-bank', lang === 'hi' ? 'निफ्टी बैंक' : 'Nifty Bank'], ['usd-inr', lang === 'hi' ? 'रुपया प्रति डॉलर' : 'Rupee a dollar'], ['brent', lang === 'hi' ? 'ब्रेंट, $ प्रति बैरल' : 'Brent, $ a barrel'], ['india-vix', 'India VIX']]
      .map(([id, l]) => { const r = row(id); return r && r.value != null ? { l, v: fmtNum(r.value, 2), p: r.pct, up: id === 'usd-inr' ? r.pct <= 0 : r.pct >= 0 } : null; }).filter(Boolean);
    const sx = row('sensex');
    // one line per event: two diary lines about the same event (same date, three shared long words) count once
    const wset = (s: string) => new Set(String(s).toLowerCase().match(/[\p{L}\p{M}]{5,}/gu) ?? []);
    const sameEv = (a: any, b: any) => a.date === b.date && [...wset(a.text)].filter((w) => wset(b.text).has(w)).length >= 3;
    const weekD = week.filter((x: any, i: number, all: any[]) => all.findIndex((y: any) => y.text === x.text || (y.href && y.href === x.href) || sameEv(x, y)) === i).slice(0, 4);
    return {
      leadLinks, second, col2, must, states, econ, cols, weekD, courts, policy, politics, stateGrid, regions,
      explained: start.slice(0, 4), opinion: opinion.slice(0, 7), fc: fcCards.slice(0, 2),
      sensex: sx ? { v: fmtNum(sx.value, 2), ch: fmtNum(sx.change, 0, true), p: sx.pct, spark, from: sxFirst ? fmtShort(String(sxFirst), lang, false) : '', to: fmtShort(String(MK.session_date), lang, false), n: sxh.length } : null,
      mkRows, mkDate: fmtShort(String(MK.session_date), lang, false), mkOpen: MK.status === 'open',
    };
  })();

  return { headlines, india, econ, live, markets, altLang, kk: short, week, desks, lead, briefing, numbers, dashHref, big, bigAlso, top, start, trackers, billsCard, econCard, elCard, budgetCard, scCard, mapModel, parl, fcCards, fcStats, explained, opinion, sections, dense };
}

export { esc };
