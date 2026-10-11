// Tracker data (JSON in /content/data, Hindi in /content/data/hi).
import billsEn from '../../content/data/bills.json';
import billsHi from '../../content/data/hi/bills.json';
import budgetEn from '../../content/data/budget-promises.json';
import budgetHi from '../../content/data/hi/budget-promises.json';
import econEn from '../../content/data/economy-dashboard.json';
import econHi from '../../content/data/hi/economy-dashboard.json';
import electEn from '../../content/data/election-calendar.json';
import electHi from '../../content/data/hi/election-calendar.json';
import scEn from '../../content/data/sc-cases.json';
import scHi from '../../content/data/hi/sc-cases.json';
import sessEn from '../../content/data/parliament-sessions.json';
import sessHi from '../../content/data/hi/parliament-sessions.json';
import type { Lang } from './i18n';

export const DATA = {
  en: { bills: billsEn, budget: budgetEn, economy: econEn, elections: electEn, sc: scEn, sessions: sessEn },
  hi: { bills: billsHi, budget: budgetHi, economy: econHi, elections: electHi, sc: scHi, sessions: sessHi },
} as const;

/** Which data view a tracker page uses, keyed by tracker id. */
export const TRACKER_VIEW: Record<string, { kind: 'bills' | 'budget' | 'economy' | 'elections' | 'sc'; file: string }> = {
  'bills-in-parliament-tracker': { kind: 'bills', file: 'bills.json' },
  'budget-2026-27-promise-tracker': { kind: 'budget', file: 'budget-promises.json' },
  'economy-dashboard': { kind: 'economy', file: 'economy-dashboard.json' },
  'election-calendar': { kind: 'elections', file: 'election-calendar.json' },
  'sc-cases-tracker': { kind: 'sc', file: 'sc-cases.json' },
};
export const dataUrl = (file: string, lang: Lang) => `/data/${lang === 'hi' ? 'hi/' : ''}${file}`;

/** Pick the Hindi variant of a field when present (field_hi), else the field itself. */
export function tr(obj: any, key: string, lang: Lang) {
  if (!obj) return undefined;
  if (lang === 'hi' && obj[`${key}_hi`] != null && obj[`${key}_hi`] !== '') return obj[`${key}_hi`];
  return obj[key];
}

export function indicator(lang: Lang, id: string): any {
  return (DATA[lang].economy as any).indicators.find((i: any) => i.id === id);
}
