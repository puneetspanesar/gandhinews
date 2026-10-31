// Extra crops of every story photo for Google (NewsArticle images in 1:1 and 16:9 as well as the 4:3 original).
// Runs before the build; output goes to public/photos/x/ (not committed, rebuilt on every deploy, skipped when present).
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const MAP = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/photos.map.json'), 'utf8'));
const OUT = path.join(ROOT, 'public/photos/x');
fs.mkdirSync(OUT, { recursive: true });
const seen = new Set();
let made = 0;
const jobs = [];
for (const p of Object.values(MAP)) {
  if (!p?.src || seen.has(p.src)) continue;
  seen.add(p.src);
  const src = path.join(ROOT, 'public', p.src);
  if (!fs.existsSync(src)) continue;
  const base = path.basename(p.src, '.jpg');
  const sq = path.join(OUT, `${base}-1x1.jpg`), wd = path.join(OUT, `${base}-16x9.jpg`);
  if (fs.existsSync(sq) && fs.existsSync(wd)) continue;
  jobs.push(async () => { try {
    const img = sharp(src); const m = await img.metadata(); const W = m.width, H = m.height;
    const s = Math.min(W, H);
    await sharp(src).extract({ left: Math.round((W - s) / 2), top: 0, width: s, height: s }).resize(Math.min(s, 800)).jpeg({ quality: 82, mozjpeg: true }).toFile(sq);
    let ww = W, wh = Math.round((W * 9) / 16);
    if (wh > H) { wh = H; ww = Math.round((H * 16) / 9); }
    await sharp(src).extract({ left: Math.round((W - ww) / 2), top: Math.round((H - wh) * 0.25), width: ww, height: wh }).jpeg({ quality: 82, mozjpeg: true }).toFile(wd);
    made++;
  } catch (e) { console.warn(`schema-crops: skipped ${p.src}: ${e.message}`); } });
}
const N = 8;
await Promise.all(Array.from({ length: N }, async (_, i) => { for (let j = i; j < jobs.length; j += N) await jobs[j](); }));
console.log(`schema-crops: ${made} photos cropped, ${seen.size} in the map`);
