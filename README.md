# Gandhi News

Static, bilingual (English and Hindi) news site built with [Astro](https://astro.build). No client framework: pages are plain HTML and CSS, with a few small scripts (compact header, share and save buttons, the budget tracker filter, the saved-stories page).

## Run it

Requirements: Node 22 (see `.nvmrc`) and npm.

```sh
npm install
npm run dev       # local dev server at http://localhost:4321
npm run build     # static build into dist/
npm run preview   # serve the built dist/ locally
npm run clean     # clear Astro's content cache (run this if a Markdown plugin change does not show up)
```

The build fails on: invalid frontmatter, invalid JSON in a chart/facts/timeline block, a broken internal link in a Markdown body, a `related` id or topic id that does not exist, or two pages claiming the same URL.

## Environment variables

| Variable    | Default                      | Purpose |
|-------------|------------------------------|---------|
| `SITE_URL`  | `https://gandhinews.example` | Absolute site URL for canonical links, hreflang, sitemaps, RSS, Open Graph and JSON-LD. No trailing slash. |
| `SITE_LIVE` | unset (preview mode)         | Until this is `true`, every page carries `<meta name="robots" content="noindex,nofollow">` and `robots.txt` disallows everything. Set `SITE_LIVE=true` only for the public launch. |

## Content

Everything editorial lives in `content/`:

```
content/
  en/  news/  explainer/  factcheck/  editorial/  topic/  tracker/   *.md
  hi/  (same folders, same file names)
  data/      *.json   tracker data (English)
  data/hi/   *.json   tracker data (Hindi)
```

- Frontmatter is validated by the schemas in `src/content.config.ts`.
- The file name (without `.md`) is the slug and must equal the `id` field. The Hindi version of a story uses the same file name under `content/hi/`, which is how the two languages are paired for hreflang and the language switch.
- Fenced blocks with the language `chart`, `facts` or `timeline` hold JSON and are turned into designed, accessible components at build time (`src/lib/blocks.mjs`, `src/lib/remark-gn.mjs`). Chart types: `hbar`, `vbar`, `line`; mark a bar or point with `"highlight": true` to show it in red.
- A blockquote whose last line starts with `Source:` (Hindi: `स्रोत:`) becomes a pull quote with that attribution.
- In fact checks, `### 1. Heading` sections become numbered evidence items, and a paragraph starting `Source:` or `Sources:` followed by links becomes a row of source chips.
- Internal links may be written as `/en/news/some-id`, `/hi/explainer/some-id`, a bare id (`some-id`) or `/content/data/file.json`; they are rewritten to the real URLs.
- Tracker data is published as-is at `/data/*.json` and `/data/hi/*.json`.

### Add an article

1. Create `content/en/news/your-slug.md` (or `explainer`, `factcheck`, `editorial`) with frontmatter matching the other files: `id: your-slug`, `lang: en`, `type`, `section`, `format_label`, `topics`, `title`, `standfirst`, `published`, `hero.alt`, `seo.description`, `sources`, `verification`. News needs `keyPoints`; explainers need `shortAnswer` and question-style `##` headings; fact checks need the `factcheck` block.
2. Add the Hindi version at `content/hi/news/your-slug.md` with `lang: hi`.
3. When a photo is ready, put it in `public/images/` and add `hero.src: /images/file.jpg` and `hero.credit: "..."` (optional `hero.caption`). Until then a grey placeholder is shown.
4. Run `npm run build` and fix anything it reports.

## Routes

English at the root, Hindi under `/hi/` with the same structure.

| Page | URL |
|------|-----|
| Article (news, explainer, fact check, editorial) | `/{section}/{slug}/` |
| Section front | `/politics/`, `/policy/`, `/economy/`, `/parliament/`, `/states/`, `/world/` |
| Format hubs | `/explained/`, `/fact-check/`, `/opinion/`, `/trackers/`, `/topics/` |
| Topic | `/topic/{id}/` |
| Tracker | `/trackers/{slug}/` |
| Saved stories (this device only) | `/saved/` |
| Homepage, search | `/`, `/search/` (placeholders for now) |
| Feeds and sitemaps | `/rss.xml`, `/hi/rss.xml`, `/sitemap-index.xml`, `/news-sitemap.xml`, `/robots.txt` |

## Code map

```
src/
  content.config.ts      collections and frontmatter schemas
  lib/routes.mjs         URL rules and internal-link resolution (shared with the Markdown plugin)
  lib/remark-gn.mjs      Markdown plugin: data blocks, pull quotes, fact-check evidence, link rewriting
  lib/blocks.mjs         HTML renderers for charts, fact boxes, timelines, sparklines
  lib/site.ts            content helpers, IST date formatting, env settings
  lib/seo.ts             JSON-LD (NewsArticle, ClaimReview, FAQPage, Dataset, BreadcrumbList)
  lib/i18n.ts            English and Hindi UI labels
  lib/data.ts            tracker JSON imports
  layouts/Base.astro     head/SEO, header, markets strip, footer
  templates/             article, topic, tracker, list and hub templates
  components/            byline, share, sources, photo slot, icons, tracker views
  pages/[...path].astro  the router for every HTML page
  styles/global.css      design tokens and all styles
public/fonts/            self-hosted Google Sans, Inter, Noto Sans Devanagari
src/icons/               Phosphor (regular) SVGs used by Icon.astro
```

## Deploy on Cloudflare Pages

- Framework preset: Astro (or None)
- Build command: `npm run build`
- Build output directory: `dist`
- Node version: 22 (set `NODE_VERSION=22` in the environment variables; `.nvmrc` also says 22)
- Environment variables: `SITE_URL` (for example `https://www.gandhinews.in`) and, at launch only, `SITE_LIVE=true`.

Use a separate preview environment without `SITE_LIVE` so preview deployments stay out of search engines.

## Before launch

- Set the newsletter form `action` in `src/layouts/Base.astro` to the email provider's endpoint.
- Footer items under Trust and Follow (except RSS) are plain text until those pages and accounts exist.
- The homepage and search are placeholders.
