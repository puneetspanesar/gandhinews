// Tells Bing, Yandex, Seznam, Naver and other IndexNow search engines about new or changed pages.
// Usage after a deploy has gone live: node scripts/indexnow.mjs [hours=3]
// Sends every article (both languages) published or updated in the last N hours, plus both homepages and the news sitemap.
import fs from 'node:fs';
import path from 'node:path';
const KEY = '54bf101875803ded5ee886afc6566af9';
const HOST = 'gandhinews.com';
const hours = Number(process.argv[2] ?? 3);
const since = Date.now() - hours * 3600e3;
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const urls = new Set([`https://${HOST}/`, `https://${HOST}/hi/`]);
for (const lang of ['en', 'hi']) {
  const base = path.join(ROOT, 'content', lang);
  for (const type of fs.readdirSync(base)) {
    const dir = path.join(base, type);
    if (!fs.statSync(dir).isDirectory() || ['tracker', 'topic'].includes(type)) continue;
    for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.md'))) {
      const t = fs.readFileSync(path.join(dir, f), 'utf8').slice(0, 3000);
      const g = (k) => (t.match(new RegExp(`^${k}:\\s*["']?([^"'\\n]+)`, 'm')) || [])[1]?.trim();
      const when = +new Date(g('updated') || g('published') || 0);
      const id = g('id'), sec = g('section');
      if (!id || !sec || !(when >= since)) continue;
      urls.add(`https://${HOST}${lang === 'hi' ? '/hi' : ''}/${sec}/${id}/`);
    }
  }
}
const urlList = [...urls].slice(0, 10000);
const r = await fetch('https://www.bing.com/indexnow', {
  method: 'POST',
  headers: { 'content-type': 'application/json; charset=utf-8' },
  body: JSON.stringify({ host: HOST, key: KEY, keyLocation: `https://${HOST}/${KEY}.txt`, urlList }),
});
console.log(`IndexNow: ${urlList.length} URLs, HTTP ${r.status}`);
