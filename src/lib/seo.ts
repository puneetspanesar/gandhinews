import { abs, urlOf, SITE_URL } from './site';
import { verdictKey, VERDICT_RATING, UI, type Lang } from './i18n';

export const PUBLISHER = {
  '@type': 'NewsMediaOrganization',
  '@id': `${SITE_URL}/#organization`,
  name: 'LokVox',
  alternateName: 'लोकवॉक्स',
  url: `${SITE_URL}/`,
  logo: { '@type': 'ImageObject', url: `${SITE_URL}/logo.png`, width: 512, height: 512 },
};
export const AUTHOR = { '@type': 'Organization', name: 'LokVox Editorial Desk', url: `${SITE_URL}/` };
const inLang = (l: Lang) => (l === 'hi' ? 'hi-IN' : 'en-IN');
const img = () => ({ '@type': 'ImageObject', url: `${SITE_URL}/og-default.png`, width: 1200, height: 630 });

export function newsArticleLd(d: any) {
  const url = abs(urlOf(d));
  return {
    '@context': 'https://schema.org',
    '@type': d.type === 'editorial' ? ['NewsArticle', 'OpinionNewsArticle'] : 'NewsArticle',
    '@id': `${url}#article`,
    mainEntityOfPage: { '@type': 'WebPage', '@id': url },
    url,
    headline: d.title.length > 110 ? `${d.title.slice(0, 107)}...` : d.title,
    description: d.seo.description,
    abstract: d.standfirst,
    datePublished: d.published.toISOString(),
    dateModified: (d.updated ?? d.published).toISOString(),
    inLanguage: inLang(d.lang),
    articleSection: d.format_label,
    keywords: d.topics.join(', '),
    isAccessibleForFree: true,
    image: [img()],
    author: [AUTHOR],
    publisher: PUBLISHER,
    ...(d.location ? { contentLocation: { '@type': 'Place', name: d.location } } : {}),
    ...(d.translation_of ? { translationOfWork: { '@id': `${abs(urlOf({ ...d, lang: 'en' }))}#article` } } : {}),
  };
}

/** FAQPage from explainer H2 questions and the first paragraph after each. */
export function faqLd(d: any, html: string) {
  const qa: { q: string; a: string }[] = [];
  const re = /<h2[^>]*>([\s\S]*?)<\/h2>\s*(?:<p[^>]*>([\s\S]*?)<\/p>)?/g;
  let m: RegExpExecArray | null;
  const text = (s: string) => s.replace(/<[^>]+>/g, '').replace(/&#x26;|&amp;/g, '&').replace(/&#x27;|&#39;/g, "'").replace(/&quot;/g, '"').replace(/\s+/g, ' ').trim();
  while ((m = re.exec(html))) {
    const q = text(m[1]);
    if (!/[?？]\s*$/.test(q) || !m[2]) continue;
    qa.push({ q, a: text(m[2]) });
  }
  if (!qa.length) return null;
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    inLanguage: inLang(d.lang),
    url: abs(urlOf(d)),
    mainEntity: qa.map((x) => ({ '@type': 'Question', name: x.q, acceptedAnswer: { '@type': 'Answer', text: x.a } })),
  };
}

export function claimReviewLd(d: any) {
  const fc = d.factcheck;
  const key = verdictKey(fc.verdict);
  const url = abs(urlOf(d));
  const first = fc.firstSeen instanceof Date ? fc.firstSeen.toISOString().slice(0, 10) : fc.firstSeen || undefined;
  return {
    '@context': 'https://schema.org',
    '@type': 'ClaimReview',
    url,
    datePublished: d.published.toISOString(),
    inLanguage: inLang(d.lang),
    headline: d.title,
    claimReviewed: fc.claim,
    author: { ...AUTHOR, '@type': 'Organization' },
    publisher: PUBLISHER,
    itemReviewed: {
      '@type': 'Claim',
      // "Social media users" is not one person; named claimants are.
      author: /social media|सोशल मीडिया/i.test(fc.claimant)
        ? { '@type': 'Organization', name: fc.claimant }
        : { '@type': 'Person', name: fc.claimant.split(/[,;]/)[0].trim(), jobTitle: fc.claimant.split(/[,;]/).slice(1).join(',').trim() || undefined },
      ...(first ? { datePublished: first } : {}),
      ...(fc.seenOn ? { appearance: { '@type': 'CreativeWork', description: fc.seenOn } } : {}),
    },
    reviewRating: {
      '@type': 'Rating',
      ratingValue: VERDICT_RATING[key],
      bestRating: 4,
      worstRating: 1,
      alternateName: UI[d.lang as Lang].verdicts[key],
      ratingExplanation: fc.finding,
    },
  };
}

export function datasetLd(d: any, dataPath: string, asOf?: string) {
  const url = abs(urlOf(d));
  return {
    '@context': 'https://schema.org',
    '@type': 'Dataset',
    name: d.title,
    description: d.seo.description.length >= 50 ? d.seo.description : `${d.seo.description} ${d.standfirst}`,
    url,
    inLanguage: inLang(d.lang),
    isAccessibleForFree: true,
    creator: PUBLISHER,
    publisher: PUBLISHER,
    datePublished: d.published.toISOString(),
    dateModified: (d.updated ?? d.published).toISOString(),
    ...(asOf ? { temporalCoverage: `../${asOf}` } : {}),
    keywords: d.topics,
    distribution: [{ '@type': 'DataDownload', encodingFormat: 'application/json', contentUrl: abs(dataPath) }],
  };
}

export function collectionLd(name: string, description: string, path: string, lang: Lang, items: any[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name,
    description,
    url: abs(path),
    inLanguage: inLang(lang),
    isPartOf: { '@type': 'WebSite', name: 'LokVox', url: `${SITE_URL}/` },
    mainEntity: {
      '@type': 'ItemList',
      itemListElement: items.slice(0, 30).map((e, i) => ({ '@type': 'ListItem', position: i + 1, url: abs(urlOf(e.data)), name: e.data.title })),
    },
  };
}

export function websiteLd(lang: Lang) {
  return [
    { '@context': 'https://schema.org', ...PUBLISHER },
    { '@context': 'https://schema.org', '@type': 'WebSite', name: 'LokVox', url: `${SITE_URL}/`, inLanguage: ['en-IN', 'hi-IN'], publisher: { '@id': PUBLISHER['@id'] } },
  ];
}
