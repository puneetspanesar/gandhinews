// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import fs from 'node:fs';
// Editorials waiting for the editor's approval stay out of the sitemap (and carry noindex).
const DRAFTS = ['en', 'hi'].flatMap((lang) => {
  const dir = `./content/${lang}/editorial`;
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter((f) => f.endsWith('.md')).flatMap((f) => {
    const t = fs.readFileSync(`${dir}/${f}`, 'utf8');
    if (!/status:\s*needs-editor-approval/.test(t)) return [];
    const id = (t.match(/^id:\s*(.+)$/m) || [])[1]?.trim(); const sec = (t.match(/^section:\s*(.+)$/m) || [])[1]?.trim();
    return id && sec ? [`${lang === 'hi' ? '/hi' : ''}/${sec}/${id}/`] : [];
  });
});
// Last-modified date and photo for every article, so the sitemap tells crawlers what changed and when.
const PHOTO_MAP = JSON.parse(fs.readFileSync('./content/photos.map.json', 'utf8'));
const ARTICLE_META = new Map();
for (const lang of ['en', 'hi']) {
  for (const type of fs.existsSync(`./content/${lang}`) ? fs.readdirSync(`./content/${lang}`) : []) {
    const dir = `./content/${lang}/${type}`;
    if (!fs.statSync(dir).isDirectory()) continue;
    for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.md'))) {
      const t = fs.readFileSync(`${dir}/${f}`, 'utf8').slice(0, 4000);
      const g = (k) => (t.match(new RegExp(`^${k}:\\s*["']?([^"'\\n]+)`, 'm')) || [])[1]?.trim();
      const id = g('id'); if (!id) continue;
      const when = g('updated') || g('published');
      const ph = PHOTO_MAP[id];
      ARTICLE_META.set(`${lang}/${id}`, { lastmod: when ? new Date(when) : null, img: ph?.src ? { url: ph.src, caption: lang === 'hi' ? ph.alt_hi || ph.alt : ph.alt } : null });
    }
  }
}
const BUILD_TIME = new Date();
import { unified } from '@astrojs/markdown-remark';
import remarkGandhi from './src/lib/remark-gn.mjs';

const SITE_URL = (process.env.SITE_URL || 'https://gandhinews.com').replace(/\/$/, '');

export default defineConfig({
  site: SITE_URL,
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  markdown: {
    syntaxHighlight: false,
    // Curly quotes on, dash conversion off (no em dashes anywhere).
    processor: unified({
      remarkPlugins: [remarkGandhi],
      smartypants: { dashes: false, ellipses: false, backticks: false },
    }),
  },
  integrations: [
    sitemap({
      i18n: { defaultLocale: 'en', locales: { en: 'en-IN', hi: 'hi-IN' } },
      serialize(item) {
        const u = new URL(item.url);
        const lang = u.pathname.startsWith('/hi/') ? 'hi' : 'en';
        const slug = u.pathname.split('/').filter(Boolean).pop() ?? '';
        const m = ARTICLE_META.get(`${lang}/${slug}`);
        if (m) {
          if (m.lastmod && !isNaN(+m.lastmod)) item.lastmod = m.lastmod.toISOString();
          if (m.img) item.img = [{ url: new URL(m.img.url, SITE_URL).href, caption: m.img.caption }];
        } else {
          // Homepages, sections and hubs change with every update.
          item.lastmod = BUILD_TIME.toISOString();
        }
        return item;
      },
      filter: (page) => !/\/(search|saved|check-email|confirmed|unsubscribed)\/$/.test(page) && !DRAFTS.some((d) => page.endsWith(d)),
    }),
  ],
});
