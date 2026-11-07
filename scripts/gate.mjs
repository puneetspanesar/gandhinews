// Build gate. Runs as the last step of `npm run build`, so Cloudflare refuses to deploy a site that breaks a hard rule
// and the last good version stays live. The stall check sees the refusal (live /build.json behind main) and fixes it.
// Hard rules (exit 1):
//   every English story, explainer, editorial and fact check has a Hindi twin, and both pages were built
//   every story, explainer and editorial has its main picture, and the picture files exist
//   no template junk on any page ({{, &amp;amp;, undefined, NaN, [object Object], Invalid Date)
//   no em dash, and in English no day-month date, in the title, standfirst or text of anything published in the last 48 hours
//   the homepage shows its lead, in English and Hindi
//   no news older than 48 hours linked from the homepages
//   no text cut off with dots: no line-clamp or ellipsis CSS, no card text ending in ... on the homepages
// Then writes dist/build.json ({sha, built}) so anyone can see which commit is live.
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { routeFor } from '../src/lib/routes.mjs';

const bad = [];
const fail = (why, what) => bad.push(`${why}: ${what}`);
const read = (p) => { try { return fs.readFileSync(p, 'utf8'); } catch { return null; } };
const fm = (src) => {
  const m = src.match(/^---\n([\s\S]*?)\n---/);
  const get = (k) => (m?.[1].match(new RegExp(`^${k}:\\s*["']?(.*?)["']?\\s*$`, 'm')) ?? [])[1];
  return { id: get('id'), section: get('section'), type: get('type'), published: get('published'), title: get('title'), standfirst: get('standfirst'), body: src.slice(m ? m[0].length : 0) };
};
function readerText(src) {
  const out = []; let skip = false;
  for (const l of src.split('\n')) {
    if (/^(sources|verification|seo|photo_notes):/.test(l)) { skip = true; continue; }
    if (skip && (/^\s/.test(l) || l === '')) continue;
    skip = false;
    out.push(l.replace(/"subject"\s*:\s*"[^"]*"/g, '').replace(/^\s*(suggested_source|need|subjects):.*$/, ''));
  }
  return out.join('\n');
}
const MAP = JSON.parse(read('content/photos.map.json'));
const urlOf = (d, lang) => routeFor({ ...d, lang }).slice(1) + 'index.html';
const now = Date.now();
let stories = 0;
for (const type of ['news', 'explainer', 'editorial', 'factcheck']) {
  const dir = `content/en/${type}`;
  if (!fs.existsSync(dir)) continue;
  for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.md'))) {
    stories++;
    const id = f.slice(0, -3);
    const en = fm(read(`${dir}/${f}`));
    const hiSrc = read(`content/hi/${type}/${f}`);
    if (!hiSrc) { fail('no Hindi twin', id); continue; }
    const hi = fm(hiSrc);
    for (const [lang, d] of [['en', en], ['hi', hi]]) {
      if (!d.id) d.id = id;
      if (!d.type) d.type = type;
      const page = path.join('dist', urlOf(d, lang));
      if (!fs.existsSync(page)) fail(`${lang} page not built`, page);
    }
    if (type !== 'factcheck') {
      const p = MAP[id];
      if (!p) fail('no main picture', id);
      else for (const k of ['src', 'src800']) if (p[k] && !fs.existsSync(path.join('public', p[k]))) fail('picture file missing', `${id} ${p[k]}`);
    }
    const t = Date.parse(en.published);
    if (t && now - t < 48 * 3600e3) for (const [lang, src] of [['en', read(`${dir}/${f}`)], ['hi', hiSrc]]) {
      // everything a reader sees: front matter (title, standfirst, key points, overlay, cover, infographic) and body,
      // minus the sources and verification blocks and photo-block subject keys
      const text = readerText(src);
      if (text.includes('\u2014')) fail(`em dash in a new ${lang} story`, id);
      if (lang === 'en') { const m = text.match(/\b(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December)\b(?! (?:apply|be|have|not))/); if (m) fail(`day-month date "${m[0]}" in a new story (write "${m[2]} ${m[1]}"; newsroom/scripts/fix_dates.py fixes it)`, id); }
    }
  }
}
const JUNK = [/\{\{/, /&amp;amp;/, />\s*undefined\s*</, /\[object Object\]/, />\s*NaN/, /NaN%/, /Invalid Date/];
let pages = 0;
(function walk(dir) {
  for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, f.name);
    if (f.isDirectory()) { if (f.name !== 'pagefind') walk(p); }
    else if (f.name.endsWith('.html')) {
      pages++;
      const html = read(p).replace(/<script[\s\S]*?<\/script>/g, '').replace(/<style[\s\S]*?<\/style>/g, '');
      for (const re of JUNK) if (re.test(html)) { fail(`junk "${re.source}" on the page`, p); break; }
    }
  }
})('dist');
// Owner's rule (sacrosanct): text is never cut off with dots. No CSS that clips text (line-clamp, text-overflow) and no
// dots at the end of a card's text on the homepages; a short slot gets whole sentences (whole() in src/lib/site.ts).
(function css(dir) {
  for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, f.name);
    if (f.isDirectory()) { if (f.name !== 'pagefind') css(p); }  // pagefind ships its own unused UI stylesheet
    else if (f.name.endsWith('.css') && /line-clamp|text-overflow\s*:\s*ellipsis/.test(read(p))) fail('CSS clips text with dots (line-clamp or text-overflow: ellipsis)', p);
  }
})('dist');
// Owner's rule (November 7): nothing older than 48 hours on the homepage (news; explainers, editorials and trackers keep
// longer). Every news link on the English and Hindi homepages is checked against its story's publish time.
const PUB = new Map();
for (const f of fs.readdirSync('content/en/news').filter((x) => x.endsWith('.md'))) { const d = fm(read(`content/en/news/${f}`)); PUB.set(f.slice(0, -3), Date.parse(d.published)); }
for (const page of ['dist/index.html', 'dist/hi/index.html']) {
  const seen = new Set();
  for (const m of (read(page) ?? '').matchAll(/href="([^"]+)"/g)) {
    const id = m[1].replace(/\/$/, '').split('/').pop();
    if (!PUB.has(id) || seen.has(id)) continue; seen.add(id);
    const h = (now - PUB.get(id)) / 3600e3;
    if (h > 48) fail(`news over 48 hours old on the homepage (${Math.round(h)} hours)`, `${page}: ${id}`);
  }
}
for (const page of ['dist/index.html', 'dist/hi/index.html']) {
  const html = (read(page) ?? '').replace(/<script[\s\S]*?<\/script>/g, '').replace(/<style[\s\S]*?<\/style>/g, '');
  for (const m of html.matchAll(/>([^<>]{0,80}(?:\u2026|\.\.\.))\s*</g)) fail('text cut off with dots on the homepage', `${page}: "${m[1].trim().slice(-60)}"`);
  if (/line-clamp|text-overflow\s*:\s*ellipsis/.test(html)) fail('inline CSS clips text with dots', page);
}
const home = JSON.parse(read('content/homepage.json'));
for (const [lang, page] of [['en', 'dist/index.html'], ['hi', 'dist/hi/index.html']]) {
  const src = read(`content/${lang}/news/${home.lead.id}.md`) ?? '';
  const title = fm(src).title;
  const html = (read(page) ?? '').replace(/&#39;|&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, '&');
  if (!title) fail(`homepage lead is not a published ${lang} news story`, home.lead.id);
  else if (!html.includes(title.replace(/\\"/g, '"'))) fail(`${lang} homepage does not show its lead`, home.lead.id);
}
let sha = process.env.WORKERS_CI_COMMIT_SHA || process.env.GITHUB_SHA || '';
try { sha ||= execSync('git rev-parse HEAD', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); } catch {}
fs.writeFileSync('dist/build.json', JSON.stringify({ sha, built: new Date().toISOString(), stories, pages }) + '\n');
if (bad.length) {
  console.error(`BUILD GATE: ${bad.length} problems. The site is not deployed until they are fixed.`);
  for (const b of bad.slice(0, 60)) console.error('  ' + b);
  if (bad.length > 60) console.error(`  ... and ${bad.length - 60} more`);
  process.exit(1);
}
console.log(`Build gate OK: ${stories} stories in both languages with pictures, ${pages} pages clean, homepage lead shown. build.json ${sha.slice(0, 7)}`);
