// Photo addresses that change when the picture changes (owner, November 12).
// Photos are cached for a day under their file name, so a replaced picture kept showing the old one. After the
// build, every /photos/... address in the pages gets ?v=<first 8 letters of the file's content hash>: the same file
// keeps the same address, a replaced file gets a new one and shows at once.
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';
const DIST = 'dist';
const ver = new Map();
const v = (p) => {
  if (!ver.has(p)) { const f = join(DIST, decodeURI(p)); ver.set(p, existsSync(f) ? createHash('md5').update(readFileSync(f)).digest('hex').slice(0, 8) : ''); }
  return ver.get(p);
};
const RX = /(\/photos\/[^"'\s?#)<>,]+\.(?:jpe?g|png|webp|svg))(?![?\w])/g;
let pages = 0, refs = 0;
const walk = (d) => { for (const e of readdirSync(d, { withFileTypes: true })) {
  const p = join(d, e.name);
  if (e.isDirectory()) { if (!['photos', 'pagefind', '_astro'].includes(e.name)) walk(p); continue; }
  if (!e.name.endsWith('.html')) continue;
  const s = readFileSync(p, 'utf8'); let n = 0;
  const out = s.replace(RX, (m, u) => { const h = v(u); if (!h) return m; n++; return `${u}?v=${h}`; });
  if (n) { writeFileSync(p, out); pages++; refs += n; }
} };
walk(DIST);
console.log(`Photo versions: ${refs} addresses in ${pages} pages, ${ver.size} files.`);
