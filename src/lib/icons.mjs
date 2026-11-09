// Inline Phosphor (regular) icons. SVGs live in /src/icons/{name}.svg.
import fs from 'node:fs';
import path from 'node:path';
import { ROOT } from './routes.mjs';

const DIR = path.join(ROOT, 'src/icons');
const cache = new Map();
// Any Phosphor icon (regular or -duotone) also resolves from the @phosphor-icons/core package, so story data can name any icon.
const PKG = path.join(ROOT, 'node_modules/@phosphor-icons/core/assets');
function findIcon(name) {
  const own = path.join(DIR, `${name}.svg`);
  if (fs.existsSync(own)) return own;
  const pk = name.endsWith('-duotone') ? path.join(PKG, 'duotone', `${name}.svg`) : path.join(PKG, 'regular', `${name}.svg`);
  return fs.existsSync(pk) ? pk : null;
}
export const hasIcon = (name) => !!findIcon(name);
/** The duotone version of an icon when one exists, else the regular one, else the fallback. */
export const duo = (name, fallback = 'circle-duotone') => (name && hasIcon(`${name}-duotone`) ? `${name}-duotone` : name && hasIcon(name) ? name : fallback);

export function iconInner(name) {
  if (cache.has(name)) return cache.get(name);
  const file = findIcon(name);
  if (!file) throw new Error(`[icons] Unknown icon "${name}". Copy it into src/icons/.`);
  const inner = fs.readFileSync(file, 'utf8').replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
  cache.set(name, inner);
  return inner;
}

export function iconSvg(name, cls = 'ic', label) {
  const a11y = label ? `role="img" aria-label="${label}"` : 'aria-hidden="true" focusable="false"';
  return `<svg class="${cls}" viewBox="0 0 256 256" fill="currentColor" ${a11y}>${iconInner(name)}</svg>`;
}
