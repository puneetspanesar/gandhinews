// Searches Wikimedia Commons for freely licensed photos for each query in
// scripts/photo-queries.json and writes candidates (with licence and author)
// plus small thumbnails to photo-candidates/. Run in GitHub Actions.
import fs from 'node:fs';
import path from 'node:path';
const UA = { 'User-Agent': 'GandhiNewsPhotoFinder/1.0 (newsroom photo pipeline; contact via github.com/puneetspanesar)' };
const OK = /^(cc0|cc[- ]by(-sa)?[- ]?[0-9.]*|public domain|pd|cc-pd|attribution|godl-india)/i;
const PART = process.env.PART || '';
const queries = JSON.parse(fs.readFileSync(`scripts/photo-queries${PART ? '-' + PART : ''}.json`, 'utf8'));
const out = 'photo-candidates';
fs.mkdirSync(path.join(out, 'thumbs'), { recursive: true });
const strip = (s = '') => s.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
const result = {};
for (const [key, raw] of Object.entries(queries)) {
  // 'name||N' asks for up to N candidates (default 5).
  const [q, nWant] = String(raw).split('||');
  const want = Math.min(Number(nWant) || 5, 20);
  const u = new URL('https://commons.wikimedia.org/w/api.php');
  Object.entries({ action: 'query', format: 'json', generator: 'search', gsrsearch: `${q} filetype:bitmap`, gsrnamespace: '6', gsrlimit: want > 5 ? '50' : '30',
    prop: 'imageinfo', iiprop: 'url|size|mime|extmetadata', iiurlwidth: '480' }).forEach(([k, v]) => u.searchParams.set(k, v));
  let pages = [];
  for (let attempt = 0; attempt < 5; attempt++) {
    try {
      const r = await fetch(u, { headers: UA });
      if (r.status === 429 || r.status >= 500) { console.log('retry', key, r.status); await new Promise((z) => setTimeout(z, 5000 * (attempt + 1))); continue; }
      const j = await r.json();
      if (j.error) { console.log('api error', key, JSON.stringify(j.error).slice(0, 200)); await new Promise((z) => setTimeout(z, 5000 * (attempt + 1))); continue; }
      pages = Object.values(j.query?.pages || {}); break;
    } catch (e) { console.log('fail', key, e.message); await new Promise((z) => setTimeout(z, 3000)); }
  }
  pages.sort((a, b) => a.index - b.index);
  const cands = [];
  for (const p of pages) {
    const ii = p.imageinfo?.[0]; if (!ii) continue;
    const m = ii.extmetadata || {};
    const lic = strip(m.LicenseShortName?.value);
    if (!OK.test(lic) || /nc|nd/i.test(lic.replace(/and/i, ''))) continue;
    if (!/image\/(jpeg|png)/.test(ii.mime) || Math.max(ii.width, ii.height) < 400) continue;
    const n = cands.length;
    const thumb = `${key}-${n}.jpg`;
    let got = false;
    for (let a = 0; a < 4 && !got; a++) {
      try { await new Promise((z) => setTimeout(z, 700 + a * 4000)); const t = await fetch(ii.thumburl, { headers: UA }); if (t.status === 429 || t.status >= 500) continue; if (!t.ok) break; fs.writeFileSync(path.join(out, 'thumbs', thumb), Buffer.from(await t.arrayBuffer())); got = true; } catch {}
    }
    if (!got) continue;
    cands.push({ n, title: p.title, page: ii.descriptionurl, url: ii.url, width: ii.width, height: ii.height, licence: lic,
      author: strip(m.Artist?.value).slice(0, 120), credit: strip(m.Credit?.value).slice(0, 120), date: strip(m.DateTimeOriginal?.value).slice(0, 40),
      description: strip(m.ImageDescription?.value).slice(0, 200), thumb, url1600: ii.width > 1600 ? ii.thumburl.split('?')[0].replace('thumb.wikimedia.org', 'upload.wikimedia.org').replace(/\/\d+px-/, '/1600px-') : ii.url.split('?')[0] });
    if (cands.length >= want) break;
  }
  result[key] = { query: q, candidates: cands };
  console.log(key, pages.length, cands.length);
  await new Promise((r) => setTimeout(r, 2500));
}
fs.writeFileSync(path.join(out, 'candidates.json'), JSON.stringify(result, null, 2));
