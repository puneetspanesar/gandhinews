import rss from '@astrojs/rss';
import { content, urlOf, SITE_URL, prefix } from './site';
import { UI, SECTION_NAMES, type Lang } from './i18n';

/** Feed channels: the whole site, each news section and each format hub (for Google News sections). */
export const FEED_KEYS = ['politics', 'policy', 'economy', 'parliament', 'states', 'world', 'explained', 'fact-check', 'opinion'] as const;
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
  const name = lang === 'hi' ? 'LokVox (हिंदी)' : 'LokVox';
  return rss({
    title: key ? `${label(lang, key)} | ${name}` : name,
    description: lang === 'hi'
      ? 'राजनीति, नीति, अर्थव्यवस्था और संसद पर स्वतंत्र भारतीय पत्रकारिता।'
      : 'Independent Indian journalism on politics, policy, the economy and Parliament.',
    site: `${SITE_URL}${prefix(lang)}/${key ? `${key}/` : ''}`,
    items: c.articles.filter(pick).slice(0, 50).map((e: any) => ({
      title: e.data.title,
      link: urlOf(e.data),
      pubDate: e.data.published,
      description: e.data.standfirst,
      categories: [e.data.format_label, ...e.data.topics],
      author: 'LokVox Editorial Desk',
    })),
    customData: `<language>${lang === 'hi' ? 'hi-in' : 'en-in'}</language>`,
  });
}
