// Route map shared by the Markdown plugin (runs in Node at config time) and the page templates.
// It reads frontmatter straight from /content so link checking works before collections load.
import fs from 'node:fs';
import path from 'node:path';

// Builds run from the repository root (npm scripts), so cwd is the project root even after bundling.
export const ROOT = process.cwd();
export const CONTENT = path.join(ROOT, 'content');
export const LANGS = ['en', 'hi'];
export const SECTIONS = ['politics', 'world', 'economy', 'science', 'sports', 'states', 'policy', 'parliament'];
export const ARTICLE_TYPES = ['news', 'explainer', 'factcheck', 'editorial'];

/** Path prefix for a language: '' for English, '/hi' for Hindi. */
export const prefix = (lang) => (lang === 'hi' ? '/hi' : '');

/** Public route for a piece of content. */
export function routeFor({ lang, type, section, id }) {
  const p = prefix(lang);
  if (type === 'topic') return `${p}/topic/${id}/`;
  if (type === 'tracker') return `${p}/trackers/${id}/`;
  return `${p}/${section}/${id}/`;
}

function readFront(file) {
  const src = fs.readFileSync(file, 'utf8');
  const m = src.match(/^---\n([\s\S]*?)\n---/);
  if (!m) return null;
  const get = (k) => {
    const r = m[1].match(new RegExp(`^${k}:\\s*"?([^"\\n]*)"?\\s*$`, 'm'));
    return r ? r[1].trim() : undefined;
  };
  return { id: get('id'), lang: get('lang'), type: get('type'), section: get('section') };
}

let cache;
/** { en: Map(id -> {route,type,section}), hi: Map(...) } */
export function contentIndex() {
  if (cache) return cache;
  cache = { en: new Map(), hi: new Map() };
  for (const lang of LANGS) {
    const dir = path.join(CONTENT, lang);
    for (const type of fs.readdirSync(dir)) {
      for (const f of fs.readdirSync(path.join(dir, type))) {
        if (!f.endsWith('.md')) continue;
        const fm = readFront(path.join(dir, type, f));
        const id = f.replace(/\.md$/, '');
        const entry = { id, lang, type: fm?.type ?? type, section: fm?.section };
        cache[lang].set(id, { ...entry, route: routeFor(entry) });
      }
    }
  }
  return cache;
}

/** Trust and legal pages (Markdown in /content/pages/{lang}/{id}.md), id -> path. */
export const TRUST_PAGES = {
  about: 'about',
  editor: 'editor',
  standards: 'standards',
  corrections: 'corrections',
  ownership: 'ownership',
  contact: 'contact',
  grievance: 'grievance',
  'ai-policy': 'ai-policy',
  'fact-check-methodology': 'fact-check/methodology',
  privacy: 'privacy',
  terms: 'terms',
};

/** Fixed (non-content) routes, per language. */
export function staticRoutes(lang) {
  const p = prefix(lang);
  return [
    `${p}/`,
    ...SECTIONS.map((s) => `${p}/${s}/`),
    `${p}/explained/`, `${p}/fact-check/`, `${p}/opinion/`, `${p}/trackers/`, `${p}/topics/`,
    `${p}/search/`, `${p}/saved/`, `${p}/latest/`,
    ...Object.values(TRUST_PAGES).map((x) => `${p}/${x}/`),
  ];
}

const TYPE_DIRS = { news: 1, explainer: 1, factcheck: 1, editorial: 1, topic: 1, tracker: 1 };

/**
 * Resolve an internal href used in a Markdown body. Returns the rewritten href,
 * the original href for external/anchor links, or null when it cannot be resolved.
 */
export function resolveHref(href, lang) {
  if (!href || /^(https?:|mailto:|tel:|#)/i.test(href)) return href;
  const idx = contentIndex();
  const [pathPart, hash = ''] = href.split('#');
  const h = hash ? `#${hash}` : '';
  // Data files: /content/data/x.json -> /data/x.json
  let m = pathPart.match(/^\/?content\/data\/((?:hi\/)?[a-z0-9-]+\.json)$/);
  if (m) {
    const file = path.join(CONTENT, 'data', m[1]);
    return fs.existsSync(file) ? `/data/${m[1]}${h}` : null;
  }
  // /en/{type}/{id} or /hi/{type}/{id}
  m = pathPart.match(/^\/(en|hi)\/([a-z]+)\/([a-z0-9-]+)\/?$/);
  if (m && TYPE_DIRS[m[2]]) {
    const hit = idx[m[1]].get(m[3]);
    return hit ? hit.route + h : null;
  }
  // Bare id
  m = pathPart.match(/^([a-z0-9-]+)$/);
  if (m) {
    const hit = idx[lang].get(m[1]);
    return hit ? hit.route + h : null;
  }
  // Already a site route
  if (pathPart.startsWith('/')) {
    const norm = pathPart.endsWith('/') ? pathPart : `${pathPart}/`;
    const all = new Set([...staticRoutes('en'), ...staticRoutes('hi')]);
    for (const l of LANGS) for (const v of idx[l].values()) all.add(v.route);
    return all.has(norm) ? norm + h : null;
  }
  return null;
}
