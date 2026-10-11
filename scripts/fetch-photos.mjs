// Photo pipeline. Reads content/photos.json, downloads each listed image, writes two JPEGs
// (1600px and 800px wide) to public/photos/, and regenerates content/photos.map.json, which the
// Photo component and article pages read (keyed by article id, shared by English and Hindi).
//
// content/photos.json is a list of:
//   {
//     "id": "rbi-headquarters-mumbai",            // file name for the photo (lowercase, hyphens)
//     "articleId": "rbi-raises-repo-rate-to-5-50",  // the story it illustrates (same id in en and hi)
//     "sourceUrl": "https://...",                  // direct link to the original image file
//     "credit": "Photo: Name / Agency",            // shown on the photo
//     "licence": "CC BY-SA 4.0",                   // or "Used with permission", "PIB (government)"...
//     "alt": "Reserve Bank of India headquarters in Mumbai"
//   }
//
// Usage:  npm run photos            (download what is missing, rebuild the map)
//         npm run photos -- --force (download everything again)
// Runs in GitHub Actions via .github/workflows/fetch-photos.yml.
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const ROOT = process.cwd();
const LIST = path.join(ROOT, 'content/photos.json');
const MAP = path.join(ROOT, 'content/photos.map.json');
const OUT = path.join(ROOT, 'public/photos');
const WIDTHS = [1600, 800];
const force = process.argv.includes('--force');

const list = JSON.parse(fs.readFileSync(LIST, 'utf8'));
if (!Array.isArray(list)) throw new Error('content/photos.json must be a JSON list');
fs.mkdirSync(OUT, { recursive: true });

const required = ['id', 'articleId', 'sourceUrl', 'credit', 'licence', 'alt'];
const seen = new Set();
for (const p of list) {
  const missing = required.filter((k) => !p[k]);
  if (missing.length) throw new Error(`photos.json entry ${JSON.stringify(p.id ?? p)} is missing: ${missing.join(', ')}`);
  if (!/^[a-z0-9-]+$/.test(p.id)) throw new Error(`photo id "${p.id}" must be lowercase letters, numbers and hyphens`);
  if (seen.has(p.articleId)) throw new Error(`two photos for article "${p.articleId}"; keep one`);
  seen.add(p.articleId);
}

const file = (id, w) => path.join(OUT, `${id}-${w}.jpg`);
const map = {};
let failed = 0;
for (const p of list) {
  try {
    const have = WIDTHS.every((w) => fs.existsSync(file(p.id, w)));
    if (force || !have) {
      const res = await fetch(p.sourceUrl, { headers: { 'User-Agent': 'GandhiNewsPhotoFetcher/1.0 (newsroom photo pipeline)' } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const buf = Buffer.from(await res.arrayBuffer());
      for (const w of WIDTHS) {
        await sharp(buf)
          .rotate() // respect EXIF orientation
          .resize({ width: w, withoutEnlargement: true })
          .jpeg({ quality: 82, progressive: true, mozjpeg: true })
          .toFile(file(p.id, w)); // sharp drops EXIF/XMP metadata unless asked to keep it
      }
      console.log(`fetched  ${p.id}`);
    } else {
      console.log(`have     ${p.id}`);
    }
    const meta = await sharp(file(p.id, 1600)).metadata();
    if ((meta.width ?? 0) < 1600) console.warn(`warning  ${p.id}: source is only ${meta.width}px wide`);
    map[p.articleId] = {
      id: p.id,
      src: `/photos/${p.id}-1600.jpg`,
      src800: `/photos/${p.id}-800.jpg`,
      width: meta.width,
      height: meta.height,
      credit: p.credit,
      licence: p.licence,
      alt: p.alt,
      alt_hi: p.alt_hi,
      page: p.page,
    };
  } catch (e) {
    failed++;
    console.error(`FAILED   ${p.id}: ${e.message}`);
  }
}

// Remove files for photos no longer listed.
const keep = new Set(list.flatMap((p) => WIDTHS.map((w) => `${p.id}-${w}.jpg`)));
for (const f of fs.readdirSync(OUT)) if (f.endsWith('.jpg') && !keep.has(f)) { fs.unlinkSync(path.join(OUT, f)); console.log(`removed  ${f}`); }

fs.writeFileSync(MAP, JSON.stringify(map, null, 2) + '\n');
console.log(`\n${Object.keys(map).length} photo(s) in content/photos.map.json${failed ? `, ${failed} failed` : ''}.`);
if (failed) process.exit(1);
