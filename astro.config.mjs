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
      filter: (page) => !/\/(search|saved|check-email|confirmed|unsubscribed)\/$/.test(page) && !DRAFTS.some((d) => page.endsWith(d)),
    }),
  ],
});
