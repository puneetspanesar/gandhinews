// Searches Wikimedia Commons for freely licensed photos for each query in
// scripts/photo-queries.json and writes candidates (with licence and author)
// plus small thumbnails to photo-candidates/. Run in GitHub Actions.
import fs from 'node:fs';
import path from 'node:path';
const UA = { 'User-Agent': 'GandhiNewsPhotoFinder/1.0 (newsroom photo pipeline; contact via github.com/puneetspanesar)' };
const OK = /^(cc0|cc[- ]by(-sa)?[- ]?[0-9.]*|public domain|pd|cc-pd|attribution|godl-india)/i;
const queries = JSON.parse(fs.readFileSync('scripts/photo-queries.json', 'utf8'));
const out = 'photo-candidates';
fs.mkdirSync(path.join(out, 'thumbs'), { recursive: true });
const strip = (s = '') => s.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
const result = {};
for (const [key, q] of Object.entries(queries)) {
  const u = new URL('https://commons.wikimedia.org/w/api.php');
  Object.entries({ action: 'query', format: 'json', generator: 'search', gsrsearch: `${q} filetype:bitmap`, gsrnamespace: '6', gsrlimit: '20',
    prop: 'imageinfo', iiprop: 'url|size|mime|extmetadata', iiurlwidth: '480' }).forEach(([k, v]) => u.searchParams.set(k, v));
  let pages = [];
  try { const r = await fetch(u, { headers: UA }); pages = Object.values((await r.json()).query?.pages || {}); } catch (e) { console.log('fail', key, e.message); }
  pages.sort((a, b) => a.index - b.index);
  const cands = [];
  for (const p of pages) {
    const ii = p.imageinfo?.[0]; if (!ii) continue;
    const m = ii.extmetadata || {};
    const lic = strip(m.LicenseShortName?.value);
    if (!OK.test(lic) || /nc|nd/i.test(lic.replace(/and/i, ''))) continue;
    if (ii.mime !== 'image/jpeg' || ii.width < 1400 || ii.height < 700) continue;
    const n = cands.length;
    const thumb = `${key}-${n}.jpg`;
    try { const t = await fetch(ii.thumburl, { headers: UA }); fs.writeFileSync(path.join(out, 'thumbs', thumb), Buffer.from(await t.arrayBuffer())); } catch { continue; }
    cands.push({ n, title: p.title, page: ii.descriptionurl, url: ii.url, width: ii.width, height: ii.height, licence: lic,
      author: strip(m.Artist?.value).slice(0, 120), credit: strip(m.Credit?.value).slice(0, 120), date: strip(m.DateTimeOriginal?.value).slice(0, 40),
      description: strip(m.ImageDescription?.value).slice(0, 200), thumb });
    if (cands.length >= 6) break;
  }
  result[key] = { query: q, candidates: cands };
  console.log(key, cands.length);
  await new Promise((r) => setTimeout(r, 400));
}
fs.writeFileSync(path.join(out, 'candidates.json'), JSON.stringify(result, null, 2));
