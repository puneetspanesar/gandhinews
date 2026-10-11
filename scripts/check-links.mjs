// Checks every internal link in the built site (dist/): href, src, srcset and SVG <use href>.
// Markdown links are already checked at build time (src/lib/remark-gn.mjs); this catches links
// written in templates and data. Exits with code 1 if anything points at a file that does not exist,
// or at an #anchor that is not on the target page.
// Usage: npm run build && npm run check:links
import fs from 'node:fs';
import path from 'node:path';

const DIST = path.resolve('dist');
if (!fs.existsSync(DIST)) {
  console.error('dist/ not found. Run `npm run build` first.');
  process.exit(1);
}

const files = [];
(function walk(dir) {
  for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, f.name);
    if (f.isDirectory()) walk(p);
    else if (f.name.endsWith('.html')) files.push(p);
  }
})(DIST);

const idCache = new Map();
function idsOf(file) {
  if (!idCache.has(file)) {
    const html = fs.readFileSync(file, 'utf8');
    idCache.set(file, new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
  }
  return idCache.get(file);
}

function target(urlPath) {
  const clean = decodeURIComponent(urlPath.split('?')[0]);
  const p = path.join(DIST, clean);
  if (clean.endsWith('/')) return path.join(p, 'index.html');
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) return path.join(p, 'index.html');
  return p;
}

const broken = [];
let checked = 0;
for (const file of files) {
  const html = fs.readFileSync(file, 'utf8');
  const page = '/' + path.relative(DIST, file).replace(/index\.html$/, '');
  const refs = [];
  for (const m of html.matchAll(/\s(?:href|src)="([^"]+)"/g)) refs.push(m[1]);
  for (const m of html.matchAll(/\ssrcset="([^"]+)"/g)) for (const part of m[1].split(',')) refs.push(part.trim().split(/\s+/)[0]);
  for (const raw of refs) {
    const ref = raw.replace(/&amp;/g, '&');
    if (/^(https?:|mailto:|tel:|data:|javascript:)/i.test(ref) || ref.startsWith('//')) continue;
    checked++;
    const [p, hash] = ref.split('#');
    if (!p) {
      if (hash && !idsOf(file).has(decodeURIComponent(hash))) broken.push(`${page} -> ${ref} (anchor missing)`);
      continue;
    }
    if (!p.startsWith('/')) { broken.push(`${page} -> ${ref} (relative link)`); continue; }
    const t = target(p);
    if (!fs.existsSync(t)) { broken.push(`${page} -> ${ref}`); continue; }
    if (hash && t.endsWith('.html') && !idsOf(t).has(decodeURIComponent(hash))) broken.push(`${page} -> ${ref} (anchor missing)`);
    if (hash && t.endsWith('.svg') && !fs.readFileSync(t, 'utf8').includes(`id="${hash}"`)) broken.push(`${page} -> ${ref} (svg id missing)`);
  }
}

if (broken.length) {
  console.error(`${broken.length} broken internal link(s) out of ${checked} checked:`);
  for (const b of [...new Set(broken)].slice(0, 200)) console.error('  ' + b);
  process.exit(1);
}
console.log(`Internal links OK: ${checked} links in ${files.length} pages.`);
