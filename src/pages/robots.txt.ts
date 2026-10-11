import { SITE_LIVE, SITE_URL } from '../lib/site';
// Preview mode (SITE_LIVE not "true"): block all crawlers.
export const GET = () =>
  new Response(
    SITE_LIVE
      ? `User-agent: *\nAllow: /\n\nSitemap: ${SITE_URL}/sitemap-index.xml\nSitemap: ${SITE_URL}/news-sitemap.xml\n`
      : `# Preview build: not for indexing. Set SITE_LIVE=true at launch.\nUser-agent: *\nDisallow: /\n`,
    { headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
  );
