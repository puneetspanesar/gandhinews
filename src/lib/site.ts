import { getCollection, type CollectionEntry } from 'astro:content';
import type { Lang } from './i18n';
import { TOPIC_FALLBACK } from './i18n';
import PHOTOS from '../../content/photos.map.json';
// @ts-ignore - plain JS module shared with the Markdown plugin
import { routeFor, prefix, SECTIONS } from './routes.mjs';

export const SITE_URL = (import.meta.env.SITE_URL || process.env.SITE_URL || 'https://gandhinews.example').replace(/\/$/, '');
export const SITE_LIVE = String(import.meta.env.SITE_LIVE ?? process.env.SITE_LIVE ?? '').toLowerCase() === 'true';
export { prefix, SECTIONS };

export type Entry =
  | CollectionEntry<'articles_en'>
  | CollectionEntry<'articles_hi'>
  | CollectionEntry<'topics_en'>
  | CollectionEntry<'topics_hi'>
  | CollectionEntry<'trackers_en'>
  | CollectionEntry<'trackers_hi'>;
export type Data = Entry['data'];

export const abs = (path: string) => SITE_URL + path;
export const urlOf = (d: Pick<Data, 'lang' | 'type' | 'section' | 'id'>) => routeFor(d) as string;
export const otherLang = (l: Lang): Lang => (l === 'en' ? 'hi' : 'en');
/** Same path in the other language. */
export function swapLangPath(path: string, to: Lang) {
  const bare = path.startsWith('/hi/') ? path.slice(3) : path === '/hi' ? '/' : path;
  return to === 'hi' ? `/hi${bare}` : bare;
}

const byDate = (a: Entry, b: Entry) => +b.data.published - +a.data.published || a.data.title.localeCompare(b.data.title);

let store: Record<Lang, { articles: Entry[]; topics: Entry[]; trackers: Entry[]; all: Map<string, Entry> }> | null = null;
export async function content() {
  if (store) return store;
  const s: any = {};
  for (const lang of ['en', 'hi'] as Lang[]) {
    const articles = (await getCollection(`articles_${lang}`)).sort(byDate);
    const topics = (await getCollection(`topics_${lang}`)).sort((a, b) => a.data.title.localeCompare(b.data.title, lang));
    const trackers = (await getCollection(`trackers_${lang}`)).sort(byDate);
    const all = new Map<string, Entry>();
    for (const e of [...articles, ...topics, ...trackers]) {
      if (all.has(e.data.id)) throw new Error(`Duplicate id "${e.data.id}" in ${lang}`);
      if (e.data.lang !== lang) throw new Error(`${e.data.id}: lang "${e.data.lang}" does not match folder "${lang}"`);
      all.set(e.data.id, e);
    }
    s[lang] = { articles, topics, trackers, all };
  }
  // Validate cross references once.
  for (const lang of ['en', 'hi'] as Lang[]) {
    for (const e of s[lang].all.values()) {
      for (const r of e.data.related) {
        if (!s[lang].all.has(r)) throw new Error(`[${lang}] ${e.data.id}: related id "${r}" not found`);
      }
      for (const t of e.data.topics) {
        const ok = s[lang].all.get(t)?.data.type === 'topic' || TOPIC_FALLBACK[t];
        if (!ok) throw new Error(`[${lang}] ${e.data.id}: unknown topic "${t}"`);
      }
    }
  }
  store = s;
  return s as NonNullable<typeof store>;
}

/** Resolve a topic id to {label, href} for tags. */
export async function topicLink(id: string, lang: Lang) {
  const c = (await content())[lang];
  const t = c.all.get(id);
  if (t && t.data.type === 'topic') return { label: t.data.title, href: urlOf(t.data) };
  const f = TOPIC_FALLBACK[id];
  return { label: f[lang], href: `${prefix(lang)}/${f.to}` };
}

// ---------- Dates (IST) ----------
const MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const MONTHS_HI = ['जनवरी', 'फरवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर'];
const DAYS_EN = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const DAYS_HI = ['रविवार', 'सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार'];

function ist(d: Date) {
  const t = new Date(d.getTime() + 330 * 60000);
  return { y: t.getUTCFullYear(), m: t.getUTCMonth(), d: t.getUTCDate(), h: t.getUTCHours(), min: t.getUTCMinutes(), wd: t.getUTCDay() };
}

/** "11 October 2026, 9:00 am IST" / "11 अक्टूबर 2026, सुबह 9:00 बजे" */
export function fmtDateTime(date: Date, lang: Lang) {
  const p = ist(date);
  const mm = String(p.min).padStart(2, '0');
  if (lang === 'hi') {
    const part = p.h < 4 ? 'रात' : p.h < 12 ? 'सुबह' : p.h < 16 ? 'दोपहर' : p.h < 20 ? 'शाम' : 'रात';
    const h12 = p.h % 12 || 12;
    return `${p.d} ${MONTHS_HI[p.m]} ${p.y}, ${part} ${h12}:${mm} बजे`;
  }
  const h12 = p.h % 12 || 12;
  return `${p.d} ${MONTHS_EN[p.m]} ${p.y}, ${h12}:${mm} ${p.h < 12 ? 'am' : 'pm'} IST`;
}
/** "11 October 2026" */
export function fmtDate(date: Date | string, lang: Lang) {
  const d = typeof date === 'string' ? parseISOish(date) : ist(date);
  if (!d) return String(date);
  const months = lang === 'hi' ? MONTHS_HI : MONTHS_EN;
  return d.d ? `${d.d} ${months[d.m]} ${d.y}` : `${months[d.m]} ${d.y}`;
}
/** "11 Oct" style short date for tables. */
export function fmtShort(date: string | null | undefined, lang: Lang, withYear = true) {
  if (!date) return '';
  const d = parseISOish(date);
  if (!d) return date;
  const m = lang === 'hi' ? MONTHS_HI[d.m] : MONTHS_EN[d.m].slice(0, 3);
  const y = withYear ? ` ${d.y}` : '';
  return d.d ? `${d.d} ${m}${y}` : `${m}${y}`;
}
function parseISOish(s: string) {
  const m = String(s).match(/^(\d{4})-(\d{2})(?:-(\d{2}))?/);
  if (!m || +m[2] < 1 || +m[2] > 12) return null;
  return { y: +m[1], m: +m[2] - 1, d: m[3] ? +m[3] : 0, h: 0, min: 0, wd: 0 };
}
export function monthKey(s: string) {
  const d = parseISOish(s);
  return d ? `${d.y}-${String(d.m + 1).padStart(2, '0')}` : null;
}
export function monthLabel(key: string, lang: Lang) {
  const [y, m] = key.split('-').map(Number);
  return `${(lang === 'hi' ? MONTHS_HI : MONTHS_EN)[m - 1]} ${y}`;
}
export function todayLine(lang: Lang, now = new Date()) {
  const p = ist(now);
  return lang === 'hi' ? `${DAYS_HI[p.wd]}, ${p.d} ${MONTHS_HI[p.m]}` : `${DAYS_EN[p.wd]}, ${p.d} ${MONTHS_EN[p.m]}`;
}
export const isoDate = (d: Date | string) => (typeof d === 'string' ? d : new Date(d).toISOString().replace('.000Z', 'Z'));

/** Split a format label "Economy / RBI" into parts. */
export const labelParts = (s: string) => s.split('/').map((x) => x.trim()).filter(Boolean);
/** Short kicker for cards: first part of the format label. */
export const kicker = (d: Data) => labelParts(d.format_label).join(' · ');

/** Hero photo for a story: a fetched photo (content/photos.map.json) wins over frontmatter hero.src. */
export function heroOf(d: any): { src?: string | null; credit?: string | null; caption?: string | null; alt?: string; page?: string | null } {
  const f = (PHOTOS as Record<string, any>)[d.id];
  if (f) {
    const alt = d.lang === 'hi' ? (f.alt_hi ?? f.alt) : f.alt;
    return { src: f.src, credit: `${f.credit}, ${f.licence}`, caption: alt, alt, page: f.page ?? null };
  }
  return { src: d.hero?.src, credit: d.hero?.credit, caption: d.hero?.caption, alt: d.hero?.alt };
}
