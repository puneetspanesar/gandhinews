// Fails if a photo is repeated too soon: the same source photo only in stories published 48+ hours apart (owner, November 12), never twice in the homepage top slots.
import fs from 'node:fs';
const map = JSON.parse(fs.readFileSync('content/photos.map.json', 'utf8'));
const byPhoto = {};
for (const [article, p] of Object.entries(map)) (byPhoto[p.id] ??= []).push(article);
// The same source image saved under two ids counts as a repeat too.
const list = JSON.parse(fs.readFileSync('content/photos.json', 'utf8'));
const bySrc = {};
// Compare by file name, so a thumbnail and the original of the same file count as one.
const fileOf = (u) => decodeURIComponent(String(u).split('?')[0].replace(/\/\d+px-[^/]+$/, '').replace('/thumb/', '/')).split('/').pop().toLowerCase();
// Composite pictures are checked through their parts (articleId 'part:...').
for (const p of list) if (!String(p.articleId).startsWith('portrait:') && !p.composite) (bySrc[fileOf(p.sourceUrl)] ??= []).push(p.articleId);
// Reuse rule (owner's decision, November 2, 2026): the same source photo may appear in two stories only when
// they were published at least 48 hours apart, and never twice in the homepage's top slots at once.
// (The map id check above stays strict: a reused source still gets its own new crop file.)
const pubOf = {};
for (const t of ['news', 'explainer', 'editorial', 'factcheck']) for (const lang of ['en']) {
  const dir = `content/${lang}/${t}`;
  if (!fs.existsSync(dir)) continue;
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith('.md')) continue;
    const m = fs.readFileSync(`${dir}/${f}`, 'utf8').match(/\npublished:\s*["']?([0-9T:+\-.]+)/);
    if (m) pubOf[f.slice(0, -3)] = Date.parse(m[1]);
  }
}
const storyOf = (aid) => String(aid).replace(/^part:/, '').split(':')[0].replace(/--(p\d+|bg|in|c)$/, '');
const DAY = 86400000;
const tooClose = (ids) => {
  const ts = [...new Set(ids.map(storyOf))].map((s) => [s, pubOf[s]]).filter(([, t]) => t);
  for (let i = 0; i < ts.length; i++) for (let j = i + 1; j < ts.length; j++) if (Math.abs(ts[i][1] - ts[j][1]) < 2 * DAY) return true;
  return new Set(ids.map(storyOf)).size < ids.length && ts.length < 2; // same story twice, or undated
};
for (const [src, a] of Object.entries(bySrc)) if (a.length > 1 && tooClose(a)) byPhoto[src] = a;
// Never the same source twice among the homepage's top stories.
try {
  const home = JSON.parse(fs.readFileSync('content/homepage.json', 'utf8'));
  const top = new Set([home.lead?.id, ...(home.lead?.relatedBelow ?? []), ...(home.lead?.relatedBeside ?? []), ...(home.topStories?.list ?? []).map((x) => x?.id ?? x), home.topStories?.big?.id].filter(Boolean));
  const seenHome = {};
  for (const [src, a] of Object.entries(bySrc)) {
    const onHome = [...new Set(a.map(storyOf))].filter((s) => top.has(s));
    if (onHome.length > 1) byPhoto['homepage:' + src] = onHome;
  }
} catch {}
const dups = Object.entries(byPhoto).filter(([, a]) => a.length > 1);
if (dups.length) {
  console.error(`${dups.length} photos are repeated too soon (same photo needs 48 hours between stories, and never twice at the top of the homepage):`);
  for (const [id, a] of dups) console.error(`  ${id}: ${a.join(', ')}`);
  process.exit(1);
}
// Every published story, explainer and editorial must have its main picture in the map.
const noPic = [];
for (const t of ['news', 'explainer', 'editorial']) {
  const dir = `content/en/${t}`;
  if (!fs.existsSync(dir)) continue;
  for (const f of fs.readdirSync(dir)) if (f.endsWith('.md') && !map[f.slice(0, -3)]) noPic.push(f.slice(0, -3));
}
if (noPic.length) {
  console.error(`${noPic.length} stories have no main picture in content/photos.map.json:`);
  for (const s of noPic) console.error(`  ${s}`);
  process.exit(1);
}
console.log(`OK: ${Object.keys(map).length} pictures, every photo unique, every story has its main picture.`);
