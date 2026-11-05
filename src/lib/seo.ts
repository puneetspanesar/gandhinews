import { abs, urlOf, SITE_URL } from './site';
import PHOTOS from '../../content/photos.map.json';
import { verdictKey, VERDICT_RATING, UI, SECTION_NAMES, type Lang } from './i18n';

/** Ways people write the name: one word, lower case, in Devanagari, and the site's former name Gandhi News. */
export const NAME_VARIANTS = ['GandhiNews', 'gandhinews', 'गांधी न्यूज़', 'गांधी न्यूज'];
/** Official profiles elsewhere. Add each one here as it is created, so Google can tie them to this site. */
// Add the Gandhi News social profiles here once they exist.
export const SAME_AS: string[] = [];

export const PUBLISHER = {
  '@type': 'NewsMediaOrganization',
  '@id': `${SITE_URL}/#organization`,
  name: 'Gandhi News',
  alternateName: NAME_VARIANTS,
  url: `${SITE_URL}/`,
  logo: { '@type': 'ImageObject', url: `${SITE_URL}/logo.png`, width: 512, height: 512 },
  description: 'Gandhi News is an independent Indian news website publishing news from India and the world, covering politics, the economy, science and technology and sports, in English and Hindi.',
  slogan: 'India and the world, in English and Hindi',
  foundingDate: '2026',
  areaServed: { '@type': 'Country', name: 'India' },
  knowsLanguage: ['en-IN', 'hi-IN'],
  publishingPrinciples: `${SITE_URL}/standards/`,
  ethicsPolicy: `${SITE_URL}/standards/`,
  correctionsPolicy: `${SITE_URL}/corrections/`,
  ownershipFundingInfo: `${SITE_URL}/ownership/`,
  masthead: `${SITE_URL}/about/`,
  verificationFactCheckingPolicy: `${SITE_URL}/fact-check/methodology/`,
  noBylinesPolicy: `${SITE_URL}/ai-policy/`,
  actionableFeedbackPolicy: `${SITE_URL}/contact/`,
  founder: { '@type': 'Person', name: 'Puneet Panesar', url: `${SITE_URL}/editor/` },
  ...(SAME_AS.length ? { sameAs: SAME_AS } : {}),
};
export const AUTHOR = { '@type': 'Organization', name: 'Gandhi News Editorial Desk', url: `${SITE_URL}/about/`, parentOrganization: { '@id': `${SITE_URL}/#organization` } };
export const EDITOR = { '@type': 'Person', name: 'Puneet Panesar', jobTitle: 'Editor-in-Chief', url: `${SITE_URL}/editor/`, worksFor: { '@type': 'NewsMediaOrganization', name: 'Gandhi News', url: `${SITE_URL}/` } };
const inLang = (l: Lang) => (l === 'hi' ? 'hi-IN' : 'en-IN');
const img = () => ({ '@type': 'ImageObject', url: `${SITE_URL}/og-default.png`, width: 1200, height: 630 });
/** The story's own photo (content/photos.map.json), for og:image and schema; null when it has none. */
export function storyImage(d: any): { url: string; width: number; height: number; alt: string } | null {
  const f = (PHOTOS as Record<string, any>)[d?.id];
  if (!f?.src) return null;
  return { url: abs(f.src), width: f.width ?? 1280, height: f.height ?? 720, alt: (d.lang === 'hi' ? f.alt_hi ?? f.alt : f.alt) ?? '' };
}
/** Social share image: the story's 16:9 cover when it has one (it carries the headline), else its photo.
 *  Structured data keeps the plain photo (imagesFor), since Google prefers pictures without text on them. */
export function shareImage(d: any): { url: string; width: number; height: number; alt: string } | null {
  const f = (PHOTOS as Record<string, any>)[d?.id];
  const cv = f?.cover ? (f.cover[d.lang] ?? f.cover.en) : null;
  if (cv) return { url: abs(cv.src), width: f.cover.width, height: f.cover.height, alt: (d.lang === 'hi' ? f.alt_hi ?? f.alt : f.alt) ?? '' };
  return storyImage(d);
}
/** Google asks for news images in 16:9, 4:3 and 1:1. The two extra crops are made at build time by scripts/schema-crops.mjs. */
const imagesFor = (d: any) => {
  const s = storyImage(d);
  if (!s) return [img()];
  const W = s.width, H = s.height;
  let ww = W, wh = Math.round((W * 9) / 16);
  if (wh > H) { wh = H; ww = Math.round((H * 16) / 9); }
  const sq = Math.min(W, H, 800);
  const base = s.url.replace(/\/photos\/([^/]+)\.jpg$/, '/photos/x/$1');
  const out: any[] = [{ '@type': 'ImageObject', url: s.url, width: W, height: H, ...(s.alt ? { caption: s.alt } : {}) }];
  if (base !== s.url) out.unshift({ '@type': 'ImageObject', url: `${base}-16x9.jpg`, width: ww, height: wh }), out.push({ '@type': 'ImageObject', url: `${base}-1x1.jpg`, width: sq, height: sq });
  return out;
};
/** Keywords: the story's topics, else its format label and the people or places it is about. */
const keywordsFor = (d: any) => {
  const k = [...(d.topics ?? []), ...String(d.format_label ?? '').split('/').map((x: string) => x.trim()), ...(d.hero?.subjects ?? []), d.location].filter(Boolean);
  return [...new Set(k)].join(', ');
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
    keywords: keywordsFor(d),
    isAccessibleForFree: true,
    image: imagesFor(d),
    author: [AUTHOR],
    editor: EDITOR,
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
    isPartOf: { '@type': 'WebSite', name: 'Gandhi News', url: `${SITE_URL}/` },
    mainEntity: {
      '@type': 'ItemList',
      itemListElement: items.slice(0, 30).map((e, i) => ({ '@type': 'ListItem', position: i + 1, url: abs(urlOf(e.data)), name: e.data.title })),
    },
  };
}

export function websiteLd(lang: Lang) {
  return [
    { '@context': 'https://schema.org', ...PUBLISHER },
    { '@context': 'https://schema.org', '@type': 'WebSite', '@id': `${SITE_URL}/#website`, name: 'Gandhi News', alternateName: NAME_VARIANTS, url: `${SITE_URL}/`, inLanguage: ['en-IN', 'hi-IN'], publisher: { '@id': PUBLISHER['@id'] } },
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
    name: lang === 'hi' ? 'गांधी न्यूज़ सेक्शन' : 'Gandhi News sections',
    itemListElement: items.map(([name, href], i) => ({
      '@type': 'SiteNavigationElement', position: i + 1, name, url: `${SITE_URL}${href}`,
    })),
  };
}
