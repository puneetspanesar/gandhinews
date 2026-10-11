// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { unified } from '@astrojs/markdown-remark';
import remarkGandhi from './src/lib/remark-gn.mjs';

const SITE_URL = (process.env.SITE_URL || 'https://gandhinews.example').replace(/\/$/, '');

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
      filter: (page) => !/\/(search|saved)\/$/.test(page),
    }),
  ],
});
