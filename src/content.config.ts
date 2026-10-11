import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const date = z.coerce.date();
const optStr = z.string().optional().nullable();

const source = z.object({
  title: z.string(),
  publisher: optStr,
  date: z.union([date, z.string()]).optional().nullable(),
  url: optStr,
  primary: z.boolean().optional().nullable(),
});

const base = z.object({
  id: z.string(),
  lang: z.enum(['en', 'hi']),
  type: z.enum(['news', 'explainer', 'factcheck', 'editorial', 'topic', 'tracker']),
  section: z.enum(['politics', 'policy', 'economy', 'parliament', 'states', 'world']),
  format_label: z.string(),
  topics: z.array(z.string()).default([]),
  title: z.string(),
  standfirst: z.string(),
  published: date,
  updated: date.optional(),
  location: optStr,
  keyPoints: z.array(z.string()).optional(),
  shortAnswer: optStr,
  factcheck: z
    .object({
      claim: z.string(),
      claimant: z.string(),
      seenOn: optStr,
      firstSeen: z.union([date, z.string()]).optional().nullable(),
      verdict: z.string(),
      verdict_en: optStr,
      finding: z.string(),
    })
    .optional(),
  hero: z
    .object({
      need: optStr,
      suggested_source: optStr,
      alt: z.string(),
      src: optStr,
      credit: optStr,
      caption: optStr,
    })
    .optional(),
  related: z.array(z.string()).default([]),
  seo: z.object({ description: z.string() }),
  sources: z.array(source).default([]),
  verification: z
    .object({ status: optStr, notes: z.array(z.string()).optional().nullable() })
    .loose()
    .optional(),
  translation_of: optStr,
  data: optStr,
});

const coll = (lang: 'en' | 'hi', pattern: string) =>
  defineCollection({
    loader: glob({
      pattern,
      base: `./content/${lang}`,
      generateId: ({ entry }) => entry.split('/').pop()!.replace(/\.md$/, ''),
    }),
    schema: base,
  });

const page = z.object({
  id: z.string(),
  lang: z.enum(['en', 'hi']),
  path: z.string(),
  title: z.string(),
  description: z.string(),
  updated: date,
});
const pages = (lang: 'en' | 'hi') =>
  defineCollection({
    loader: glob({ pattern: '*.md', base: `./content/pages/${lang}`, generateId: ({ entry }) => entry.replace(/\.md$/, '') }),
    schema: page,
  });

const ARTICLES = '{news,explainer,factcheck,editorial}/*.md';

export const collections = {
  articles_en: coll('en', ARTICLES),
  articles_hi: coll('hi', ARTICLES),
  topics_en: coll('en', 'topic/*.md'),
  topics_hi: coll('hi', 'topic/*.md'),
  trackers_en: coll('en', 'tracker/*.md'),
  trackers_hi: coll('hi', 'tracker/*.md'),
  pages_en: pages('en'),
  pages_hi: pages('hi'),
};
