// Fails if any photo is used by more than one story. Every story gets its own image.
import fs from 'node:fs';
const map = JSON.parse(fs.readFileSync('content/photos.map.json', 'utf8'));
const byPhoto = {};
for (const [article, p] of Object.entries(map)) (byPhoto[p.id] ??= []).push(article);
// The same source image saved under two ids counts as a repeat too.
const list = JSON.parse(fs.readFileSync('content/photos.json', 'utf8'));
const bySrc = {};
for (const p of list) if (!String(p.articleId).startsWith('portrait:')) (bySrc[String(p.sourceUrl).replace(/\/\d+px-[^/]+$/, '').replace('/thumb/', '/')] ??= []).push(p.articleId);
for (const [src, a] of Object.entries(bySrc)) if (a.length > 1) byPhoto[src] = a;
const dups = Object.entries(byPhoto).filter(([, a]) => a.length > 1);
if (dups.length) {
  console.error(`${dups.length} photos are used by more than one story:`);
  for (const [id, a] of dups) console.error(`  ${id}: ${a.join(', ')}`);
  process.exit(1);
}
console.log(`OK: ${Object.keys(map).length} stories, every photo unique.`);
