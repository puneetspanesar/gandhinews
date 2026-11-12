import rss from '@astrojs/rss';
import { content, urlOf, SITE_URL, prefix } from './site';
import { UI, SECTION_NAMES, type Lang } from './i18n';
import { shareImage } from './seo';

/** Feed channels: the whole site, each news section and each format hub (for Google News sections). */
export const FEED_KEYS = ['politics', 'world', 'economy', 'science', 'sports', 'states', 'policy', 'parliament', 'explained', 'fact-check', 'opinion'] as const;
const FORMAT_TYPE: Record<string, string> = { explained: 'explainer', 'fact-check': 'factcheck', opinion: 'editorial' };

function label(lang: Lang, key: string) {
  const t: any = UI[lang];
  if (key === 'explained') return t.explained;
  if (key === 'fact-check') return t.factCheck;
  if (key === 'opinion') return t.opinion;
  return (SECTION_NAMES as any)[lang][key] ?? key;
}

export async function feed(lang: Lang, key?: string) {
  const c = (await content())[lang];
  const pick = (e: any) =>
    !key ? true : FORMAT_TYPE[key] ? e.data.type === FORMAT_TYPE[key] : e.data.section === key && e.data.type !== 'editorial';
  const name = lang === 'hi' ? 'Gandhi News (हिंदी)' : 'Gandhi News';
  // every item carries its picture (owner, November 12): feed readers and news apps such as Flipboard need one to show a story
  const pic = (d: any) => { try { return shareImage(d); } catch { return null; } };
  return rss({
    xmlns: { media: 'http://search.yahoo.com/mrss/' },
    title: key ? `${label(lang, key)} | ${name}` : name,
    description: lang === 'hi'
      ? 'भारत और दुनिया की स्वतंत्र खबरें, हिंदी और अंग्रेज़ी में।'
      : 'Independent news from India and the world, in English and Hindi.',
    site: `${SITE_URL}${prefix(lang)}/${key ? `${key}/` : ''}`,
    items: c.articles.filter(pick).slice(0, 50).map((e: any) => ({
      title: e.data.title,
      link: urlOf(e.data),
      pubDate: e.data.published,
      description: e.data.standfirst,
      categories: [e.data.format_label, ...e.data.topics],
      author: 'Gandhi News Editorial Desk',
      ...(pic(e.data) ? { enclosure: { url: pic(e.data)!.url, length: 0, type: /\.png$/.test(pic(e.data)!.url) ? 'image/png' : 'image/jpeg' }, customData: `<media:content url="${pic(e.data)!.url}" medium="image" width="${pic(e.data)!.width}" height="${pic(e.data)!.height}" />` } : {}),
    })),
    customData: `<language>${lang === 'hi' ? 'hi-in' : 'en-in'}</language>`,
  });
}
