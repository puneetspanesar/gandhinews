// Pictures for the edition A design (owner's pick, November 27, 2026): the plain photograph, never the collage.
// A story's own graphic (an infographic piece) keeps its graphic. Everything comes from content/photos.map.json.
import PHOTOS from '../../content/photos.map.json';
import type { Lang } from './i18n';

export interface Tile { src: string; srcset?: string; alt: string; width: number; height: number; graphic: boolean }

const M = PHOTOS as Record<string, any>;

/** True when a piece has a picture that can sit in a tile. */
export const hasTile = (id?: string) => !!id && !!M[id] && !M[id].nohome;

/** An old-style graphic (the icon card retired on November 27, 2026). It keeps its place on its own story page and in lists, but takes no picture slot on the front page. */
export const oldCard = (id?: string) => !!id && !!M[id]?.graphic && M[id].style !== 'scene';

/** The picture for a tile or a story top. `big` asks for the detailed graphic where the piece is an infographic. */
export function tileOf(id: string | undefined, lang: Lang, big = false): Tile | null {
  const b = id ? M[id] : null;
  if (!b) return null;
  const alt = (lang === 'hi' ? b.alt_hi : b.alt) ?? b.alt ?? '';
  if (b.graphic) {
    const g = big ? (b.byLang?.[lang] ? { ...b, ...b.byLang[lang] } : b) : (b.thumb?.[lang] ?? b.thumb?.en ?? b.cover?.[lang] ?? b.cover?.en ?? b);
    const w = big ? b.width : 1280, h = big ? b.height : 720;
    return { src: g.src, srcset: g.src800 && g.src800 !== g.src ? `${g.src800} 640w, ${g.src} 1280w` : undefined, alt, width: w, height: h, graphic: true };
  }
  return { src: b.src, srcset: b.src800 && b.src800 !== b.src ? `${b.src800} 640w, ${b.src} 1280w` : undefined, alt, width: b.width, height: b.height, graphic: false };
}

/** Caption and credit under a story's top picture. */
export function creditOf(id: string | undefined, lang: Lang): { caption: string; credit: string; page: string | null; photoId: string } | null {
  const b = id ? M[id] : null;
  if (!b) return null;
  const hi = lang === 'hi';
  const caption = (hi ? b.alt_hi : b.alt) ?? b.alt ?? '';
  if (b.graphic) return { caption, credit: hi ? 'ग्राफ़िक: गांधी न्यूज़' : 'Graphic: Gandhi News', page: null, photoId: b.id };
  const who0 = String(b.credit ?? '').replace(/^Photo:\s*/, '');
  const who = hi ? who0.replace('Wikimedia Commons', 'विकिमीडिया कॉमन्स') : who0;
  const credit = (hi ? 'फ़ोटो: ' : 'Photo: ') + [who, b.licence].filter(Boolean).join(', ');
  return { caption, credit, page: b.page ?? null, photoId: b.id };
}

/** One key per photograph, whichever piece carries it: the picture's source page, else its file. */
export const photoKey = (id?: string): string | null => { const b = id ? M[id] : null; return b ? String(b.page ?? b.src) : null; };
