# Gandhi News

Static, bilingual (English and Hindi) news site built with [Astro](https://astro.build). No client framework: pages are plain HTML and CSS, with a few small scripts (compact header, share and save buttons, the budget tracker filter, the saved-stories page).

## Run it

Requirements: Node 22 (see `.nvmrc`) and npm.

```sh
npm install
npm run dev       # local dev server at http://localhost:4321
npm run build     # static build into dist/, then the Pagefind search index into dist/pagefind/
npm run check:links  # after a build: checks every internal link and #anchor in dist/
npm run photos    # download the photos listed in content/photos.json (see "Photos" below)
npm run preview   # serve the built dist/ locally
npm run clean     # clear Astro's content cache (run this if a Markdown plugin change does not show up)
```

The build fails on: invalid frontmatter, invalid JSON in a chart/facts/timeline block, a broken internal link in a Markdown body, a `related` id or topic id that does not exist, or two pages claiming the same URL.

## Environment variables

| Variable    | Default                      | Purpose |
|-------------|------------------------------|---------|
| `SITE_URL`  | `https://gandhinews.com` | Absolute site URL for canonical links, hreflang, sitemaps, RSS, Open Graph and JSON-LD. No trailing slash. |
| `SITE_LIVE` | unset (preview mode)         | Until this is `true`, every page carries `<meta name="robots" content="noindex,nofollow">` and `robots.txt` disallows everything. Set `SITE_LIVE=true` only for the public launch. |

## Content

Everything editorial lives in `content/`:

```
content/
  en/  news/  explainer/  factcheck/  editorial/  topic/  tracker/   *.md
  hi/  (same folders, same file names)
  data/      *.json   tracker data (English)
  data/hi/   *.json   tracker data (Hindi)
  pages/en/  pages/hi/   trust and legal pages (About, Standards, Corrections, ...)
  homepage.json       which stories and modules appear on the homepage
  corrections.json    the public corrections log
  photos.json         photos to fetch; photos.map.json is generated from it
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

## Homepage

`content/homepage.json` decides what goes where on `/` and `/hi/`. It holds article ids, not text: titles, standfirsts, key points, numbers, charts and dates are read from the articles and the tracker data, so editing an article or a data file updates the homepage. The Hindi homepage uses the Hindi version of each id. The only text in the file is what has no other home: the briefing lines, the short labels on the data box and indicators, the two key numbers on each Explained card, and the data-desk headline and paragraph (each with `en` and `hi`).

| Key | What it controls |
|-----|------------------|
| `lead` | Lead story `id`; `chart` (which ```chart block of the story to show, 1 = first); `dataBox` (indicator ids from the economy dashboard, with icon, colour and label); `relatedBelow`, `relatedBeside` (story ids) |
| `briefing.items` | Today's briefing: `{ link: story id, lead: {en, hi}, text: {en, hi} }` |
| `numbers` | India in numbers: indicator ids from `data/economy-dashboard.json`, label, icon, decimals; `tracker` for the link |
| `topStories` | `big.id`, `big.also` (two related ids), `list` (five ids) |
| `startHere` | Explainer ids |
| `trackers` | Tracker ids for the black band, with a short card title |
| `dataDesk.map` | Election map: text in `en`/`hi`; `{n}` in the title becomes the number of states (from `data/election-calendar.json`) |
| `dataDesk.parliament` | Session id from `data/parliament-sessions.json` and bill ids from `data/bills.json` |
| `factCheck.cards` | Three fact-check ids. The counts under the band are computed from every fact check. |
| `explained` | Explainer ids, each with two key numbers `kn` |
| `opinion` | Editorial ids |
| `sections` | Six section blocks: `lead` id, `list` ids, optional `module`: `bypolls` (reads the first chart of the given article), `markets` (indicator ids), `session` (session id) |

A wrong id fails the build with a message naming it. After changing the homepage, check at desktop width (1440px) that side-by-side columns still end at about the same height, and add or drop list items to balance them.

## Trust pages and corrections

Markdown in `content/pages/en/` and `content/pages/hi/`, one file per page; `path` in the frontmatter sets the URL. Text in [square brackets] is a placeholder for company details that must be filled in before launch.

To log a correction, add an entry to `content/corrections.json` (newest first is not required; the page sorts by date):

```json
{ "id": "c-2026-10-20-repo", "date": "2026-10-20", "article": "rbi-raises-repo-rate-to-5-50",
  "correction": { "en": "An earlier version gave the wrong date for the next policy meeting.", "hi": "..." } }
```

It appears on `/corrections/`, `/hi/corrections/` and in the box at the foot of the homepage. Also add an `updated` date to the story.

## Search

`npm run build` runs `pagefind --site dist` after Astro. Article, topic and tracker pages are indexed (their main content carries `data-pagefind-body`), with `type` and `section` filters and `format` and `date` metadata. Pagefind keeps one index per `<html lang>`, so `/search/` searches English pages and `/hi/search/` Hindi pages. Search does not work in `npm run dev`; use `npm run build && npm run preview`.

## Photos

1. Add an entry to `content/photos.json` for each story photo: `id`, `articleId`, `sourceUrl` (direct image link), `credit`, `licence`, `alt`. Only use photos you have permission or a licence for.
2. In GitHub, run the "Fetch photos" workflow (Actions tab). It downloads each photo, writes 1600px and 800px JPEGs to `public/photos/`, regenerates `content/photos.map.json` and commits them. Locally: `npm run photos`.
3. The Photo component uses the fetched photo (with its credit) wherever that story appears, in both languages. Stories without one keep the grey placeholder.

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
| Homepage, search | `/`, `/search/` |
| Latest (all stories, newest first) | `/latest/` |
| Trust and legal | `/about/`, `/standards/`, `/corrections/`, `/ownership/`, `/contact/`, `/grievance/`, `/ai-policy/`, `/fact-check/methodology/`, `/privacy/`, `/terms/` |
| Not found | `/404.html` |
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
  templates/             home, article, topic, tracker, list, hub, search and trust-page templates
  lib/home.ts            homepage view model (reads content/homepage.json)
  components/            byline, share, sources, photo slot, icons, tracker views
  pages/[...path].astro  the router for every HTML page
  styles/global.css      design tokens and all styles
public/fonts/            self-hosted Google Sans, Inter, Noto Sans Devanagari
src/icons/               Phosphor (regular) SVGs used by Icon.astro
public/maps/india.svg    India state outlines (one <path id> per state) for the election map
scripts/                 fetch-photos.mjs (photo pipeline), check-links.mjs (internal link check)
```

## Deploy on Cloudflare Pages

- Framework preset: Astro (or None)
- Build command: `npm run build`
- Build output directory: `dist`
- Node version: 22 (set `NODE_VERSION=22` in the environment variables; `.nvmrc` also says 22)
- Environment variables: `SITE_URL` (for example `https://gandhinews.com`) and, at launch only, `SITE_LIVE=true`.

Use a separate preview environment without `SITE_LIVE` so preview deployments stay out of search engines.

## Before launch

Search the code for `TODO(launch)` and the content for `[` placeholders:

- Newsletter form (`src/layouts/Base.astro`, `data-todo="newsletter-endpoint"`): set `action` to the email provider's signup endpoint and remove the "launching soon" handler.
- WhatsApp tip line (`src/templates/Home.astro`, `data-todo="whatsapp-tipline"`) and footer WhatsApp link (`data-todo="whatsapp-channel"`): point at `https://wa.me/<number>` or the channel.
- "Follow this topic" (`src/components/FollowCard.astro`, `data-todo="topic-follow"`): connect to topic alerts.
- Instagram, YouTube and X in the footer are plain text until the accounts exist.
- Fill every [placeholder] in `content/pages/en/` and `content/pages/hi/` (company name, address, editor, Grievance Officer, emails, ownership, funders, retention periods, data licence, jurisdiction) and have the Grievance, Privacy and Terms pages reviewed by a lawyer.
- Confirm the licence of the India map outline in `public/maps/india.svg`, and that it shows India's official boundaries.
