import rss from '@astrojs/rss';
import { content, urlOf, SITE_URL, prefix } from './site';
import type { Lang } from './i18n';

export async function feed(lang: Lang) {
  const c = (await content())[lang];
  return rss({
    title: lang === 'hi' ? 'Gandhi News (हिंदी)' : 'Gandhi News',
    description: lang === 'hi'
      ? 'राजनीति, नीति, अर्थव्यवस्था और संसद पर स्वतंत्र भारतीय पत्रकारिता।'
      : 'Independent Indian journalism on politics, policy, the economy and Parliament.',
    site: `${SITE_URL}${prefix(lang)}/`,
    items: c.articles.slice(0, 50).map((e: any) => ({
      title: e.data.title,
      link: urlOf(e.data),
      pubDate: e.data.published,
      description: e.data.standfirst,
      categories: [e.data.format_label, ...e.data.topics],
      author: 'Gandhi News Editorial Desk',
    })),
    customData: `<language>${lang === 'hi' ? 'hi-in' : 'en-in'}</language>`,
  });
}
