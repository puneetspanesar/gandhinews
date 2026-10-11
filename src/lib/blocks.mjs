// Server-side renderers for the ```chart, ```facts and ```timeline blocks.
// Output is plain HTML (and a little SVG); no client JavaScript is needed.

export const esc = (s) =>
  String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const L = {
  en: { source: 'Source', data: 'Data for this chart', label: 'Item', value: 'Value', upcoming: 'Upcoming' },
  hi: { source: 'स्रोत', data: 'इस चार्ट का डेटा', label: 'मद', value: 'मान', upcoming: 'आगे' },
};

let uid = 0;
const nextId = (p) => `${p}-${(++uid).toString(36)}`;

/** Number of decimals used in a list of numbers (6.5 and 6.25 -> 2). */
function decimalsOf(values) {
  return Math.max(0, ...values.map((v) => (String(v).split('.')[1] || '').length));
}

export function fmtNum(v, decimals = 0, signed = false) {
  const abs = Math.abs(v).toLocaleString('en-IN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  if (v < 0) return `−${abs}`;
  return signed && v > 0 ? `+${abs}` : abs;
}

/** Attach a unit to a formatted number. Units not shown inline are carried by the subtitle. */
export function withUnit(n, unit = '') {
  const u = (unit || '').trim();
  if (!u) return n;
  if (u === '%') return `${n}%`;
  if (u.startsWith('₹') || u.startsWith('$')) {
    const sym = u[0];
    const rest = u.slice(1).trim();
    const neg = n.startsWith('−') || n.startsWith('+') ? n[0] : '';
    const body = neg ? n.slice(1) : n;
    return `${neg}${sym}${body}${rest ? ` ${rest}` : ''}`;
  }
  return n;
}

function niceStep(raw) {
  const p = 10 ** Math.floor(Math.log10(raw || 1));
  for (const m of [1, 2, 2.5, 5, 10]) if (m * p >= raw) return m * p;
  return 10 * p;
}
const niceCeil = (v) => (v <= 0 ? 0 : niceStep(v));

function hiddenTable(d, lang, fmt) {
  const t = L[lang];
  const rows = d.data.map((r) => `<tr><th scope="row">${esc(r.label)}</th><td>${esc(fmt(r.value))}</td></tr>`).join('');
  return `<div class="sr-only"><table><caption>${esc(d.title)}${d.subtitle ? `. ${esc(d.subtitle)}` : ''}</caption><thead><tr><th scope="col">${t.label}</th><th scope="col">${t.value}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function figure(d, lang, inner, fmt, cls) {
  const id = nextId('fig');
  const src = d.source ? `<p class="fsrc">${L[lang].source}: ${esc(d.source)}</p>` : '';
  return `<figure class="fig chart ${cls}" aria-labelledby="${id}"><figcaption id="${id}"><span class="ft">${esc(d.title)}</span>${d.subtitle ? `<span class="fs">${esc(d.subtitle)}</span>` : ''}</figcaption><div class="viz" aria-hidden="true">${inner}</div>${hiddenTable(d, lang, fmt)}${src}</figure>`;
}

function hbar(d, lang, fmt) {
  const vals = d.data.map((r) => r.value);
  const hasNeg = vals.some((v) => v < 0);
  const anyHi = d.data.some((r) => r.highlight);
  const max = niceCeil(Math.max(0, ...vals));
  const min = hasNeg ? -niceCeil(-Math.min(...vals)) : 0;
  const span = max - min || 1;
  const zero = ((0 - min) / span) * 100;
  const valW = Math.max(...d.data.map((r) => fmt(r.value).length)) * 8 + 8;
  const rows = d.data
    .map((r) => {
      const w = (Math.abs(r.value) / span) * 100;
      const left = r.value < 0 ? zero - w : zero;
      const cls = r.highlight ? 'hl' : anyHi ? 'lo' : '';
      return `<div class="hb2 ${cls}"><span class="lb">${esc(r.label)}</span><span class="b"><i style="left:${left.toFixed(2)}%;width:${Math.max(w, 0.4).toFixed(2)}%"></i>${hasNeg ? `<em style="left:${zero.toFixed(2)}%"></em>` : ''}</span><span class="v num">${esc(fmt(r.value))}</span></div>`;
    })
    .join('');
  const tickFmt = (v) => withUnit(fmtNum(v, v % 1 ? 1 : 0, hasNeg), d.unit);
  const ticks = hasNeg ? [min, 0, max] : [0, max / 2, max];
  const axis = `<div class="axis"><span></span><div>${ticks.map((v) => `<span>${esc(tickFmt(v))}</span>`).join('')}</div><span></span></div>`;
  return figure(d, lang, `<div class="hbars" style="--vw:${valW}px">${rows}${axis}</div>`, fmt, 'is-hbar');
}

function vbar(d, lang, fmt) {
  const vals = d.data.map((r) => r.value);
  const max = Math.max(...vals.map(Math.abs)) || 1;
  const anyHi = d.data.some((r) => r.highlight);
  const n = d.data.length;
  const cols = d.data
    .map((r) => {
      const h = (Math.abs(r.value) / max) * 100;
      const cls = r.highlight ? 'hl' : anyHi ? '' : 'ink';
      return `<div class="${cls}"><span class="num">${esc(fmt(r.value))}</span><i style="height:${h.toFixed(1)}%"></i></div>`;
    })
    .join('');
  const labs = d.data.map((r) => `<span>${esc(r.label)}</span>`).join('');
  return figure(d, lang, `<div class="vbar" style="--n:${n}">${cols}</div><div class="vlab" style="--n:${n}">${labs}</div>`, fmt, 'is-vbar');
}

function line(d, lang, fmt) {
  const vals = d.data.map((r) => r.value);
  const n = vals.length;
  let mn = Math.min(...vals), mx = Math.max(...vals);
  const range = mx - mn || Math.abs(mx) || 1;
  const step = niceStep(range / 3);
  let lo = Math.floor((mn - range * 0.15) / step) * step;
  let hi = Math.ceil((mx + range * 0.25) / step) * step;
  if (mn >= 0 && lo < 0) lo = 0;
  const ticks = [];
  for (let v = lo; v <= hi + step / 1000; v += step) ticks.push(+v.toFixed(6));
  const X = (i) => 4 + (n === 1 ? 46 : (i / (n - 1)) * 92);
  const Y = (v) => 100 - ((v - lo) / (hi - lo)) * 100;
  const td = decimalsOf(ticks);
  const grid = ticks.map((v) => `<b style="top:${Y(v).toFixed(2)}%"></b>`).join('');
  const tlabels = ticks.map((v) => `<span style="top:${Y(v).toFixed(2)}%">${esc(withUnit(fmtNum(v, td), d.unit))}</span>`).join('');
  const pts = vals.map((v, i) => `${X(i).toFixed(2)},${Y(v).toFixed(2)}`).join(' ');
  const dots = d.data
    .map((r, i) => {
      const cls = r.highlight || (i === n - 1 && !d.data.some((x) => x.highlight)) ? 'hl' : '';
      let pos = i === 0 ? 'first' : i === n - 1 ? 'last' : '';
      if (!pos) {
        // Keep the value label off the line: below a dip, beside the line on a slope.
        const a = vals[i - 1], v = vals[i], b = vals[i + 1];
        pos = a > v && b > v ? 'dn' : a > v && v > b ? 'ur' : a < v && v < b ? 'ul' : '';
      }
      return `<span class="pt ${cls}" style="left:${X(i).toFixed(2)}%;top:${Y(r.value).toFixed(2)}%"></span><span class="pv ${cls} ${pos}" style="left:${X(i).toFixed(2)}%;top:${Y(r.value).toFixed(2)}%">${esc(fmt(r.value))}</span>`;
    })
    .join('');
  const xl = d.data
    .map((r, i) => `<span class="${i === 0 ? 'first' : i === n - 1 ? 'last' : ''}" style="left:${X(i).toFixed(2)}%">${esc(r.label)}</span>`)
    .join('');
  const svg = `<svg viewBox="0 0 100 100" preserveAspectRatio="none"><polyline points="${pts}" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>`;
  return figure(
    d,
    lang,
    `<div class="lc"><div class="plot">${grid}${svg}${dots}</div><div class="yt">${tlabels}</div><div class="xl">${xl}</div></div>`,
    fmt,
    'is-line',
  );
}

export function renderChart(d, lang = 'en') {
  if (!d || !Array.isArray(d.data) || !d.data.length) throw new Error('chart block needs a non-empty "data" array');
  const vals = d.data.map((r) => r.value);
  if (vals.some((v) => typeof v !== 'number' || Number.isNaN(v))) throw new Error('chart values must be numbers');
  const dec = decimalsOf(vals);
  const signed = vals.some((v) => v < 0);
  const fmt = (v) => withUnit(fmtNum(v, dec, signed), d.unit);
  if (d.type === 'hbar') return hbar(d, lang, fmt);
  if (d.type === 'vbar') return vbar(d, lang, fmt);
  if (d.type === 'line') return line(d, lang, fmt);
  throw new Error(`unknown chart type "${d.type}"`);
}

export function renderFacts(d, lang = 'en') {
  if (!d || !Array.isArray(d.items)) throw new Error('facts block needs an "items" array');
  const n = d.items.length;
  const cols = n % 3 === 0 && n <= 6 ? 3 : n >= 4 ? 4 : n;
  const items = d.items
    .map(
      (it) =>
        `<li><b class="num">${esc(it.value)}</b><span>${esc(it.label)}</span>${it.source ? `<small>${L[lang].source}: ${esc(it.source)}</small>` : ''}</li>`,
    )
    .join('');
  return `<section class="facts" aria-label="${esc(d.title || '')}">${d.title ? `<p class="ft">${esc(d.title)}</p>` : ''}<ul class="c${cols}">${items}</ul></section>`;
}

const MONTHS = {
  jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5, jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11,
  'जनवरी': 0, 'फरवरी': 1, 'फ़रवरी': 1, 'मार्च': 2, 'अप्रैल': 3, 'मई': 4, 'जून': 5, 'जुलाई': 6, 'अगस्त': 7, 'सितंबर': 8, 'सितम्बर': 8, 'अक्टूबर': 9, 'नवंबर': 10, 'नवम्बर': 10, 'दिसंबर': 11, 'दिसम्बर': 11,
};
/** Best-effort parse of "7 Oct 2026", "2-4 Dec 2026", "Mar 2027", "12 अक्टूबर 2026". */
function parseLooseDate(s) {
  const m = String(s).match(/(?:(\d{1,2})(?:\s*[-–]\s*\d{1,2})?\s+)?([A-Za-z]{3,}|[ऀ-ॿ]+)\.?\s+(\d{4})/);
  if (!m) return null;
  const mon = MONTHS[m[2].slice(0, 3).toLowerCase()] ?? MONTHS[m[2]];
  if (mon === undefined) return null;
  return new Date(Date.UTC(+m[3], mon, m[1] ? +m[1] : 28));
}

export const AS_OF = new Date(process.env.GN_AS_OF || Date.now());

export function renderTimeline(d, lang = 'en') {
  if (!d || !Array.isArray(d.items)) throw new Error('timeline block needs an "items" array');
  const items = d.items
    .map((it) => {
      const dt = parseLooseDate(it.date);
      const up = dt && dt > AS_OF;
      return `<li${up ? ' class="now"' : ''}><b>${esc(it.date)}</b><span>${esc(it.text)}</span></li>`;
    })
    .join('');
  return `<section class="tlb" aria-label="${esc(d.title || '')}">${d.title ? `<p class="ft">${esc(d.title)}</p>` : ''}<ol class="tl">${items}</ol></section>`;
}

/** Tiny inline sparkline (SVG) for tracker tiles. */
export function sparkline(values, { w = 120, h = 36, stroke = '#0d0d0d', dot = '#cc0000' } = {}) {
  if (!values || values.length < 2) return '';
  const mn = Math.min(...values), mx = Math.max(...values);
  const X = (i) => 3 + (i / (values.length - 1)) * (w - 6);
  const Y = (v) => (mx === mn ? h / 2 : h - 4 - ((v - mn) / (mx - mn)) * (h - 8));
  const pts = values.map((v, i) => `${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');
  const n = values.length - 1;
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" aria-hidden="true"><polyline points="${pts}" fill="none" stroke="${stroke}" stroke-width="1.6" stroke-linejoin="round"/><circle cx="${X(n).toFixed(1)}" cy="${Y(values[n]).toFixed(1)}" r="3" fill="${dot}"/></svg>`;
}
