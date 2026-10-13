// State election pages: data lives in content/data/elections/{state}.json, with a Hindi string map
// in {state}.hi.json and official/free portraits in portraits.json.
import PUNJAB from '../../content/data/elections/punjab.json';
import PUNJAB_HI from '../../content/data/elections/punjab.hi.json';
import PORTRAITS from '../../content/data/elections/portraits.json';
import type { Lang } from './i18n';

export const ELECTIONS: Record<string, { data: any; hi: Record<string, string>; slug: string; name: { en: string; hi: string } }> = {
  punjab: { data: PUNJAB, hi: PUNJAB_HI as any, slug: 'punjab-2027', name: { en: 'Punjab', hi: 'पंजाब' } },
};

/** Party look: colour and an icon standing in for its election symbol. */
export const PARTY: Record<string, { short: string; hi: string; color: string; icon?: string; symbol?: { en: string; hi: string } }> = {
  AAP: { short: 'AAP', hi: 'आप', color: '#0b6fb5', icon: 'broom', symbol: { en: 'Broom', hi: 'झाड़ू' } },
  INC: { short: 'Congress', hi: 'कांग्रेस', color: '#1c9be0', icon: 'hand-palm', symbol: { en: 'Hand', hi: 'हाथ' } },
  BJP: { short: 'BJP', hi: 'भाजपा', color: '#f07c18', icon: 'flower-lotus', symbol: { en: 'Lotus', hi: 'कमल' } },
  SAD: { short: 'Akali Dal', hi: 'अकाली दल', color: '#1d3a8a', icon: 'scales', symbol: { en: 'Scales', hi: 'तराज़ू' } },
  BSP: { short: 'BSP', hi: 'बसपा', color: '#2a4fa8', symbol: { en: 'Elephant', hi: 'हाथी' } },
  IND: { short: 'Independent', hi: 'निर्दलीय', color: '#8a8a8a' },
};
export const partyOf = (k: string) => PARTY[k] ?? { short: k, hi: k, color: '#8a8a8a' };

export const portrait = (id: string) => (PORTRAITS as Record<string, any>)[id] ?? null;

export function translator(lang: Lang, hi: Record<string, string>) {
  return (s: any) => (s == null ? '' : lang === 'hi' ? hi[String(s)] ?? String(s) : String(s));
}

export const initials = (name: string) =>
  name.replace(/^Dr\.?\s+/i, '').split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join('').toUpperCase();

export const num = (n: number | null | undefined, lang: Lang) => (n == null ? '' : n.toLocaleString(lang === 'hi' ? 'hi-IN' : 'en-IN'));
