// Google News sitemap: news articles published in the last 48 hours (at build time).
import { content, urlOf, abs } from '../lib/site';
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
export async function GET() {
  const c = await content();
  const since = Date.now() - 48 * 3600 * 1000;
  const items = (['en', 'hi'] as const).flatMap((lang) =>
    c[lang].articles.filter((e: any) => e.data.type === 'news' && +e.data.published >= since).map((e: any) => ({ lang, d: e.data })),
  );
  const body = items
    .map(({ lang, d }) => `  <url>
    <loc>${abs(urlOf(d))}</loc>
    <news:news>
      <news:publication><news:name>Gandhi News</news:name><news:language>${lang}</news:language></news:publication>
      <news:publication_date>${d.published.toISOString()}</news:publication_date>
      <news:title>${esc(d.title)}</news:title>
    </news:news>
  </url>`)
    .join('\n');
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
${body}
</urlset>
`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
