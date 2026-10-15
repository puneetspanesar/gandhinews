// State election pages: data lives in content/data/elections/{state}.json, with a Hindi string map
// in {state}.hi.json and official/free portraits in portraits.json.
import PUNJAB from '../../content/data/elections/punjab.json';
import PUNJAB_HI from '../../content/data/elections/punjab.hi.json';
import UP from '../../content/data/elections/up.json';
import UP_HI from '../../content/data/elections/up.hi.json';
import PORTRAITS from '../../content/data/elections/portraits.json';
import type { Lang } from './i18n';

export interface StateGuide { data: any; hi: Record<string, string>; slug: string; name: { en: string; hi: string }; pp: string; related: RegExp; mid?: string }
/** pp: prefix of this state's keys in portraits.json. related: matches story titles and labels for "Latest from". */
export const ELECTIONS: Record<string, StateGuide> = {
  punjab: { data: PUNJAB, hi: PUNJAB_HI as any, slug: 'punjab-2027', name: { en: 'Punjab', hi: 'पंजाब' }, pp: '', related: /punjab|पंजाब|\bmann\b|मान/i },
  'uttar-pradesh': { data: UP, hi: UP_HI as any, slug: 'uttar-pradesh-2027', name: { en: 'Uttar Pradesh', hi: 'उत्तर प्रदेश' }, pp: 'up-', related: /uttar pradesh|उत्तर प्रदेश|\byogi\b|योगी|akhilesh|अखिलेश|lucknow|लखनऊ|mayawati|मायावती/i },
};

/** Party look: colour and an icon standing in for its election symbol. */
export const PARTY: Record<string, { short: string; hi: string; color: string; icon?: string; symbol?: { en: string; hi: string } }> = {
  AAP: { short: 'AAP', hi: 'आप', color: '#0b6fb5', icon: 'broom', symbol: { en: 'Broom', hi: 'झाड़ू' } },
  INC: { short: 'Congress', hi: 'कांग्रेस', color: '#1c9be0', icon: 'hand-palm', symbol: { en: 'Hand', hi: 'हाथ' } },
  BJP: { short: 'BJP', hi: 'भाजपा', color: '#f07c18', icon: 'flower-lotus', symbol: { en: 'Lotus', hi: 'कमल' } },
  SAD: { short: 'Akali Dal', hi: 'अकाली दल', color: '#1d3a8a', icon: 'scales', symbol: { en: 'Scales', hi: 'तराज़ू' } },
  BSP: { short: 'BSP', hi: 'बसपा', color: '#2a4fa8', symbol: { en: 'Elephant', hi: 'हाथी' } },
  SP: { short: 'SP', hi: 'सपा', color: '#d1202f', icon: 'bicycle', symbol: { en: 'Bicycle', hi: 'साइकिल' } },
  RLD: { short: 'RLD', hi: 'रालोद', color: '#1d7a3a', icon: 'drop', symbol: { en: 'Hand pump', hi: 'हैंडपंप' } },
  ADS: { short: 'Apna Dal (S)', hi: 'अपना दल (एस)', color: '#7a3e9d', icon: 'coffee', symbol: { en: 'Cup and saucer', hi: 'कप-प्लेट' } },
  SBSP: { short: 'SBSP', hi: 'सुभासपा', color: '#d4a106' },
  NISHAD: { short: 'NISHAD', hi: 'निषाद पार्टी', color: '#b5562c' },
  JSDL: { short: 'JSD(L)', hi: 'जनसत्ता दल (लो.)', color: '#5a5a5a' },
  ADK: { short: 'Apna Dal (K)', hi: 'अपना दल (क)', color: '#9a7bb0' },
  AIMIM: { short: 'AIMIM', hi: 'एआईएमआईएम', color: '#2e6b4f' },
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
