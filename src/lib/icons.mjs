// Inline Phosphor (regular) icons. SVGs live in /src/icons/{name}.svg.
import fs from 'node:fs';
import path from 'node:path';
import { ROOT } from './routes.mjs';

const DIR = path.join(ROOT, 'src/icons');
const cache = new Map();

export function iconInner(name) {
  if (cache.has(name)) return cache.get(name);
  const file = path.join(DIR, `${name}.svg`);
  if (!fs.existsSync(file)) throw new Error(`[icons] Unknown icon "${name}". Copy it into src/icons/.`);
  const inner = fs.readFileSync(file, 'utf8').replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
  cache.set(name, inner);
  return inner;
}

export function iconSvg(name, cls = 'ic', label) {
  const a11y = label ? `role="img" aria-label="${label}"` : 'aria-hidden="true" focusable="false"';
  return `<svg class="${cls}" viewBox="0 0 256 256" fill="currentColor" ${a11y}>${iconInner(name)}</svg>`;
}
