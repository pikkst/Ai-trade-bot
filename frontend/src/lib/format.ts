import type { SupportedLocale } from './content';

export interface FormatOptions {
  locale?: SupportedLocale;
  currency?: string;
}

const DEFAULT_LOCALE: SupportedLocale = 'en';

function resolveLocale(locale?: SupportedLocale): SupportedLocale {
  return locale ?? DEFAULT_LOCALE;
}

const LOCALE_MAP: Record<SupportedLocale, string> = {
  en: 'en-IE',
  et: 'et-EE',
};

const currencyFormatterCache = new Map<string, Intl.NumberFormat>();

export function formatCurrency(value: number, options?: FormatOptions): string {
  const locale = resolveLocale(options?.locale);
  const currency = options?.currency ?? 'EUR';
  const key = `${LOCALE_MAP[locale]}-${currency}`;
  let formatter = currencyFormatterCache.get(key);
  if (!formatter) {
    formatter = new Intl.NumberFormat(LOCALE_MAP[locale], {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    currencyFormatterCache.set(key, formatter);
  }
  return formatter.format(value);
}

const percentFormatterCache = new Map<string, Intl.NumberFormat>();

export function formatPercent(value: number, options?: FormatOptions): string {
  const locale = resolveLocale(options?.locale);
  let formatter = percentFormatterCache.get(locale);
  if (!formatter) {
    formatter = new Intl.NumberFormat(LOCALE_MAP[locale], {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    });
    percentFormatterCache.set(locale, formatter);
  }
  return formatter.format(value);
}
