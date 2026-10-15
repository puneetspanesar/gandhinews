import { abs, urlOf, SITE_URL } from './site';
import PHOTOS from '../../content/photos.map.json';
import { verdictKey, VERDICT_RATING, UI, SECTION_NAMES, type Lang } from './i18n';

/** Ways people write the name: two words, lower case, and in Devanagari. ("LokVox News" is left out on purpose:
 *  an unrelated Mumbai channel uses that name, and we do not want Google to merge the two.) */
export const NAME_VARIANTS = ['Lok Vox', 'Lokvox', 'lokvox.com', 'लोकवॉक्स', 'लोक वॉक्स'];
/** Official profiles elsewhere. Add each one here as it is created, so Google can tie them to this site. */
export const SAME_AS: string[] = [];

export const PUBLISHER = {
  '@type': 'NewsMediaOrganization',
  '@id': `${SITE_URL}/#organization`,
  name: 'LokVox',
  alternateName: NAME_VARIANTS,
  url: `${SITE_URL}/`,
  logo: { '@type': 'ImageObject', url: `${SITE_URL}/logo.png`, width: 512, height: 512 },
  description: 'LokVox is an independent Indian news website (lokvox.com) publishing news from India and the world, covering politics, the economy, science and technology and sports, in English and Hindi.',
  slogan: 'The people’s newsroom',
  foundingDate: '2026',
  areaServed: { '@type': 'Country', name: 'India' },
  knowsLanguage: ['en-IN', 'hi-IN'],
  publishingPrinciples: `${SITE_URL}/standards/`,
  ethicsPolicy: `${SITE_URL}/standards/`,
  correctionsPolicy: `${SITE_URL}/corrections/`,
  ownershipFundingInfo: `${SITE_URL}/ownership/`,
  masthead: `${SITE_URL}/about/`,
  founder: { '@type': 'Person', name: 'Puneet Singh', url: `${SITE_URL}/editor/` },
  ...(SAME_AS.length ? { sameAs: SAME_AS } : {}),
};
export const AUTHOR = { '@type': 'Organization', name: 'LokVox Editorial Desk', url: `${SITE_URL}/` };
export const EDITOR = { '@type': 'Person', name: 'Puneet Singh', jobTitle: 'Editor and Publisher', url: `${SITE_URL}/editor/`, worksFor: { '@type': 'NewsMediaOrganization', name: 'LokVox', url: `${SITE_URL}/` } };
const inLang = (l: Lang) => (l === 'hi' ? 'hi-IN' : 'en-IN');
const img = () => ({ '@type': 'ImageObject', url: `${SITE_URL}/og-default.png`, width: 1200, height: 630 });
/** The story's own photo (content/photos.map.json), for og:image and schema; null when it has none. */
export function storyImage(d: any): { url: string; width: number; height: number; alt: string } | null {
  const f = (PHOTOS as Record<string, any>)[d?.id];
  if (!f?.src) return null;
  return { url: abs(f.src), width: f.width ?? 1280, height: f.height ?? 720, alt: (d.lang === 'hi' ? f.alt_hi ?? f.alt : f.alt) ?? '' };
}
const imagesFor = (d: any) => {
  const s = storyImage(d);
  return s ? [{ '@type': 'ImageObject', url: s.url, width: s.width, height: s.height }, img()] : [img()];
};

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
    image: imagesFor(d),
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
    { '@context': 'https://schema.org', '@type': 'WebSite', '@id': `${SITE_URL}/#website`, name: 'LokVox', alternateName: NAME_VARIANTS, url: `${SITE_URL}/`, inLanguage: ['en-IN', 'hi-IN'], publisher: { '@id': PUBLISHER['@id'] } },
    navLd(lang),
  ];
}

/** The category tree: sections and format hubs, as the site navigation. */
export function navLd(lang: Lang) {
  const p = lang === 'hi' ? '/hi' : '';
  const t: any = UI[lang];
  const S = SECTION_NAMES[lang];
  const items = [
    ...['politics', 'world', 'economy', 'science', 'sports', 'states', 'policy', 'parliament'].map((k) => [S[k], `${p}/${k}/`]),
    [t.factCheck, `${p}/fact-check/`],
    [t.explained, `${p}/explained/`],
    [t.opinion, `${p}/opinion/`],
    [t.dataTrackers, `${p}/trackers/`],
    [t.topics, `${p}/topics/`],
  ];
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: lang === 'hi' ? 'लोकवॉक्स सेक्शन' : 'LokVox sections',
    itemListElement: items.map(([name, href], i) => ({
      '@type': 'SiteNavigationElement', position: i + 1, name, url: `${SITE_URL}${href}`,
    })),
  };
}
