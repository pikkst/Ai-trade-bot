/* =============================================================================
 * The Daily Roast AI — Localization Content Catalog
 * Version: 1.0.0
 *
 * This module provides a minimal content-key boundary so that all user-facing
 * strings and locale-aware formatting are decoupled from component literals.
 * Production i18n can extend this catalog with additional locales while keeping
 * components independent from raw copy.
 * ========================================================================== */

export type ContentKey =
  | 'app.title'
  | 'app.subtitle'
  | 'app.tagline'
  | 'status.paperContext'
  | 'nav.tokenReference'
  | 'nav.productIdentity'
  | 'section.designTokens'
  | 'section.designTokensBody'
  | 'section.referenceMetrics'
  | 'section.accessibilityNotes'
  | 'theme.light'
  | 'theme.dark'
  | 'theme.system'
  | 'metric.portfolio'
  | 'metric.drawdown'
  | 'metric.evidenceFreshness';

export type SupportedLocale = 'en' | 'et';

type ContentCatalog = Record<SupportedLocale, Record<ContentKey, string>>;

const catalog: ContentCatalog = {
  en: {
    'app.title': 'The Daily Roast AI',
    'app.subtitle': 'Design tokens · theme-ready foundation · financial clarity',
    'app.tagline': 'Evidence-Driven Market Intelligence',
    'status.paperContext': 'Paper-only context',
    'nav.tokenReference': 'Token reference',
    'nav.productIdentity': 'Product identity',
    'section.designTokens': 'Design tokens',
    'section.designTokensBody':
      'Versioned visual primitives for calm, trustworthy evidence displays.',
    'section.referenceMetrics': 'Reference metrics',
    'section.accessibilityNotes': 'Accessibility notes',
    'theme.light': 'Light',
    'theme.dark': 'Dark',
    'theme.system': 'System',
    'metric.portfolio': 'Portfolio',
    'metric.drawdown': 'Drawdown',
    'metric.evidenceFreshness': 'Evidence freshness',
  },
  et: {
    'app.title': 'The Daily Roast AI',
    'app.subtitle': 'Disainitokenid · teemavalmis alus · finantsiline selgus',
    'app.tagline': 'Tõenduspõhine turuanalüüs',
    'status.paperContext': 'Ainult paberkaubanduse keskkond',
    'nav.tokenReference': 'Tokenite ülevaade',
    'nav.productIdentity': 'Toote identiteet',
    'section.designTokens': 'Disainitokenid',
    'section.designTokensBody':
      'Versioonitud visuaalsed alusväärtused rahulike ja usaldusväärsete tõendivaadete jaoks.',
    'section.referenceMetrics': 'Näidismõõdikud',
    'section.accessibilityNotes': 'Ligipääsetavuse märkused',
    'theme.light': 'Hele',
    'theme.dark': 'Tume',
    'theme.system': 'Süsteem',
    'metric.portfolio': 'Portfell',
    'metric.drawdown': 'Langus tipust',
    'metric.evidenceFreshness': 'Tõendite värskus',
  },
};

export function getContent(locale: SupportedLocale, key: ContentKey): string {
  return catalog[locale][key] ?? catalog.en[key] ?? key;
}

export function getSupportedLocales(): SupportedLocale[] {
  return ['en', 'et'];
}
