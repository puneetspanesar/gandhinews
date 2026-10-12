// Fails if any photo is used by more than one story. Every story gets its own image.
import fs from 'node:fs';
const map = JSON.parse(fs.readFileSync('content/photos.map.json', 'utf8'));
const byPhoto = {};
for (const [article, p] of Object.entries(map)) (byPhoto[p.id] ??= []).push(article);
const dups = Object.entries(byPhoto).filter(([, a]) => a.length > 1);
if (dups.length) {
  console.error(`${dups.length} photos are used by more than one story:`);
  for (const [id, a] of dups) console.error(`  ${id}: ${a.join(', ')}`);
  process.exit(1);
}
console.log(`OK: ${Object.keys(map).length} stories, every photo unique.`);
