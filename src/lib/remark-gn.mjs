// remark plugin for LokVox Markdown.
// - ```chart / ```facts / ```timeline JSON blocks -> designed HTML components
// - blockquotes ending in "Source: ..." / "स्रोत: ..." -> pull quote with attribution
// - fact checks: "### 1. ..." evidence sections -> numbered evidence items; "Source(s):" lines -> source chips
// - internal links (/en/..., /hi/..., bare ids, /content/data/...) rewritten to real routes; broken ones fail the build
import { visit, SKIP } from 'unist-util-visit';
import { renderChart, renderFacts, renderTimeline, renderInfographic, renderCompare } from './blocks.mjs';
import { resolveHref } from './routes.mjs';
import { iconSvg } from './icons.mjs';

const SOURCE_RE = /^\s*(Sources?|स्रोत)\s*:\s*/;

function textOf(node) {
  if (!node) return '';
  if (typeof node.value === 'string') return node.value;
  return (node.children || []).map(textOf).join('');
}

/** Remove a leading "Source:" label from the first text node of a paragraph. */
function stripLabel(par) {
  const first = par.children?.[0];
  if (first && first.type === 'text') first.value = first.value.replace(SOURCE_RE, '');
  return par;
}

export default function remarkGandhi() {
  return (tree, file) => {
    const fm = file.data?.astro?.frontmatter ?? {};
    const where = file.path || fm.id || 'unknown file';
    const lang = fm.lang || (/\/content\/hi\//.test(String(file.path)) ? 'hi' : 'en');
    const type = fm.type;
    const errors = [];

    // 1. Data blocks
    visit(tree, 'code', (node, index, parent) => {
      if (!['chart', 'facts', 'timeline', 'infographic', 'compare'].includes(node.lang)) return;
      let data;
      try {
        data = JSON.parse(node.value);
      } catch (e) {
        throw new Error(`[gandhi] Invalid JSON in \`\`\`${node.lang} block in ${where}: ${e.message}`);
      }
      let html;
      try {
        html = node.lang === 'chart' ? renderChart(data, lang) : node.lang === 'facts' ? renderFacts(data, lang) : node.lang === 'infographic' ? renderInfographic(data, lang, (n) => iconSvg(n, 'i')) : node.lang === 'compare' ? renderCompare(data, lang, (n) => iconSvg(n, 'i')) : renderTimeline(data, lang);
      } catch (e) {
        throw new Error(`[gandhi] Could not render \`\`\`${node.lang} block in ${where}: ${e.message}`);
      }
      parent.children[index] = { type: 'html', value: html };
      return SKIP;
    });

    // 2. Pull quotes
    visit(tree, 'blockquote', (node, index, parent) => {
      const kids = node.children || [];
      const last = kids[kids.length - 1];
      if (!last || last.type !== 'paragraph' || !SOURCE_RE.test(textOf(last))) return;
      const quote = kids.slice(0, -1);
      parent.children[index] = {
        type: 'gnFigure',
        data: { hName: 'figure', hProperties: { className: ['pq'] } },
        children: [
          { type: 'html', value: iconSvg('quotes') },
          {
            type: 'gnDiv',
            data: { hName: 'div' },
            children: [
              { type: 'blockquote', children: quote },
              { type: 'gnCap', data: { hName: 'figcaption' }, children: stripLabel(last).children },
            ],
          },
        ],
      };
      return SKIP;
    });

    // 3. Fact-check structure
    if (type === 'factcheck') {
      const out = [];
      let current = null;
      for (const node of tree.children) {
        const isEvidence = node.type === 'heading' && node.depth === 3 && /^\s*\d+\.\s+/.test(textOf(node));
        if (isEvidence) {
          const num = textOf(node).match(/^\s*(\d+)\./)[1];
          // strip "1. " from the heading text
          const t = node.children[0];
          if (t && t.type === 'text') t.value = t.value.replace(/^\s*\d+\.\s+/, '');
          current = {
            type: 'gnEv',
            data: { hName: 'article', hProperties: { className: ['ev-item'] } },
            children: [
              { type: 'html', value: `<span class="n" aria-hidden="true">${num}</span>` },
              { type: 'gnEvBody', data: { hName: 'div' }, children: [node] },
            ],
          };
          out.push(current);
          continue;
        }
        if (current && node.type === 'heading' && node.depth <= 3) current = null;
        if (current) current.children[1].children.push(node);
        else out.push(node);
      }
      tree.children = out;
    }

    // 4. "Source:" lines (fact checks and elsewhere) -> source chips
    visit(tree, 'paragraph', (node, index, parent) => {
      if (parent?.type === 'gnCap') return;
      const first = node.children?.[0];
      if (!first || first.type !== 'text' || !SOURCE_RE.test(first.value)) return;
      if (!node.children.some((c) => c.type === 'link')) return;
      const label = first.value.match(SOURCE_RE)[1];
      first.value = first.value.replace(SOURCE_RE, '');
      node.children = node.children.filter((c) => !(c.type === 'text' && /^[\s;,]*$/.test(c.value)));
      node.data = { hProperties: { className: ['srcline'] } };
      node.children.unshift({ type: 'html', value: `<span class="sl">${label}:</span>` });
    });

    // 5. Links
    visit(tree, 'link', (node) => {
      const url = node.url;
      if (/^(https?:|mailto:|tel:|#)/i.test(url)) {
        if (/^https?:/i.test(url)) {
          node.data = { hProperties: { rel: 'noopener', target: '_blank' } };
        }
        return;
      }
      const resolved = resolveHref(url, lang);
      if (!resolved) errors.push(url);
      else node.url = resolved;
    });

    if (errors.length) {
      throw new Error(`[gandhi] Broken internal link(s) in ${where}: ${errors.join(', ')}`);
    }
  };
}
