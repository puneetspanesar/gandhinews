// Fails when the built homepage has empty space: a card or column whose content ends far above its bottom,
// a picture that did not load, or a band with almost no text. Run after the build:
//   node newsroom/scripts/check_layout.cjs        (serves dist/ itself)
const {chromium} = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = path.join(__dirname, '../../dist');
const srv = http.createServer((q, r) => { let f = path.join(root, decodeURIComponent(q.url.split('?')[0])); if (f.endsWith('/')) f += 'index.html'; fs.readFile(f, (e, d) => { if (e) { r.statusCode = 404; r.end(); } else { r.setHeader('content-type', f.endsWith('.html') ? 'text/html' : f.endsWith('.css') ? 'text/css' : f.endsWith('.js') ? 'text/javascript' : f.endsWith('.svg') ? 'image/svg+xml' : 'application/octet-stream'); r.end(d); } }); }).listen(4396);
(async () => {
  const b = await chromium.launch(); let bad = [];
  for (const [w, pathn] of [[1440, '/'], [390, '/'], [1440, '/hi/']]) {
    const p = await b.newPage({viewport: {width: w, height: 900}});
    await p.route(/google-analytics\.com|googletagmanager\.com/, (r) => r.abort());  // our checks never reach Analytics
    await p.goto((process.env.LAYOUT_URL || 'http://localhost:4396') + pathn, {waitUntil: 'networkidle'});
    for (let y = 0; y < 16000; y += 700) { await p.evaluate((y) => scrollTo(0, y), y); await p.waitForTimeout(80); }
    await p.waitForTimeout(1000);
    // the whole page in one viewport, so the hole test below can probe every point
    await p.setViewportSize({width: w, height: Math.min(await p.evaluate(() => document.documentElement.scrollHeight), 16000)}); await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(500);
    const r = await p.evaluate((w) => {
      const out = [], name = (e) => (e.closest('section')?.querySelector('h2')?.textContent || e.closest('section')?.className || '').trim().slice(0, 30);
      document.querySelectorAll('img').forEach((i) => { if (i.offsetParent && !(i.complete && i.naturalWidth > 0)) out.push(`picture did not load (${name(i)}): ${i.getAttribute('src')}`); });
      const gap = w > 700 ? 170 : 120;
      document.querySelectorAll('.home .g-c, .home .g-ll, .home .g-lf').forEach((c) => {
        const cr = c.getBoundingClientRect(); if (cr.height < 120 || !c.offsetParent) return;
        let bottom = cr.top; c.querySelectorAll('*').forEach((k) => { const kr = k.getBoundingClientRect(); if (kr.height > 0 && (k.children.length === 0 || k.tagName === 'A')) bottom = Math.max(bottom, kr.bottom); });
        const empty = cr.bottom - bottom; if (empty > gap) out.push(`empty space ${Math.round(empty)}px under "${(c.innerText || '').trim().slice(0, 50)}" (${name(c)})`);
      });
      document.querySelectorAll('.home > section, .home .g-band').forEach((s) => { if (s.offsetHeight > 150 && s.innerText.trim().length < 80) out.push(`band with no content (${name(s)})`); });
      // Empty grid cells: a hole with no element in it (a column the grid left blank) is invisible to the card test above,
      // so sample the page every 40 px and fail on any 200 x 200 px block where only a band, its container or a grid shows.
      const BG = (e) => !e || e.matches('section, .w, .g-live, .g-g, .g-split, .g-ct, .g-ll, .g-lf, .g-wk, .g-band, .home, main, body, html');
      const st = 40, need = w > 700 ? 5 : 4;
      document.querySelectorAll('.home > section > .w, .home .g-band > .w, .home section.w').forEach((wr) => {
        const r = wr.getBoundingClientRect(); if (!wr.offsetParent || r.height < 200) return;
        const cols = Math.floor(r.width / st), rows = Math.floor(r.height / st), E = [];
        for (let j = 0; j < rows; j++) { E.push([]); for (let i = 0; i < cols; i++) { const x = r.left + st / 2 + i * st, y = r.top + st / 2 + j * st; E[j].push(BG(document.elementFromPoint(x, y))); } }
        let hit = null;
        for (let j = 0; j + need <= rows && !hit; j++) for (let i = 0; i + need <= cols && !hit; i++) {
          let all = true; for (let a = 0; a < need && all; a++) for (let b2 = 0; b2 < need && all; b2++) all = E[j + a][i + b2];
          if (all) hit = [Math.round(i * st), Math.round(j * st)];
        }
        if (hit) out.push(`empty area of ${need * st}px or more at x ${hit[0]}, y ${hit[1]} inside "${name(wr)}"`);
      });
      return out;
    }, w);
    r.forEach((x) => bad.push(`[${w}px ${pathn}] ${x}`)); await p.close();
  }
  await b.close(); srv.close();
  if (bad.length) { console.log('LAYOUT PROBLEMS:'); bad.forEach((x) => console.log('  ' + x)); process.exit(1); }
  console.log('OK: no empty slots, every picture loaded.');
})();
