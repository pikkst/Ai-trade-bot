import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import './App.css';
import './styles/tokens.css';
import { formatCurrency, formatPercent } from './lib/format';
import { getContent, type SupportedLocale, type ContentKey } from './lib/content';

type ThemeOption = 'light' | 'dark' | 'system';

const themeOptions: Array<{ value: ThemeOption; labelKey: ContentKey }> = [
  { value: 'light', labelKey: 'theme.light' },
  { value: 'dark', labelKey: 'theme.dark' },
  { value: 'system', labelKey: 'theme.system' },
];

const ACTIVE_LOCALE: SupportedLocale = 'en';

function App() {
  const [theme, setTheme] = useState<ThemeOption>(() => {
    if (typeof window === 'undefined') return 'system';
    return (
      (window.localStorage.getItem('daily-roast-theme') as ThemeOption | null) ??
      'system'
    );
  });

  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    window.localStorage.setItem('daily-roast-theme', theme);
  }, [theme]);

  const t = (key: ContentKey) => getContent(ACTIVE_LOCALE, key);

  const metrics = useMemo(
    () => [
      {
        label: t('metric.portfolio'),
        value: formatCurrency(12540.5, { currency: 'EUR', locale: ACTIVE_LOCALE }),
      },
      {
        label: t('metric.drawdown'),
        value: formatPercent(-0.085, { locale: ACTIVE_LOCALE }),
      },
      { label: t('metric.evidenceFreshness'), value: '2m ago' },
    ],
    []
  );

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-title">
          <p className="muted">{t('app.tagline')}</p>
          <h1>{t('app.title')}</h1>
          <p className="muted">{t('app.subtitle')}</p>
        </div>
        <div className="theme-switcher" role="group" aria-label="Theme selection">
          {themeOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              aria-pressed={theme === option.value}
              onClick={() => setTheme(option.value)}
            >
              {t(option.labelKey)}
            </button>
          ))}
        </div>
      </header>

      <main className="app-main">
        <div className="grid">
          <section className="panel">
            <h2>{t('section.designTokens')}</h2>
            <p className="muted">{t('section.designTokensBody')}</p>
            <div className="token-list">
              <div className="token-chip">
                <span className="value-row">
                  <span
                    className="swatch"
                    style={{ background: 'var(--color-brand)' }}
                  />
                  Brand
                </span>
                <code>brand</code>
              </div>
              <div className="token-chip">
                <span className="value-row">
                  <span
                    className="swatch"
                    style={{ background: 'var(--color-accent)' }}
                  />
                  Accent
                </span>
                <code>roast</code>
              </div>
              <div className="token-chip">
                <span className="value-row">
                  <span
                    className="swatch"
                    style={{ background: 'var(--color-danger)' }}
                  />
                  Danger
                </span>
                <code>danger</code>
              </div>
            </div>
          </section>

          <section className="panel">
            <h3>{t('section.referenceMetrics')}</h3>
            <div className="token-list">
              {metrics.map((metric) => (
                <div className="token-chip" key={metric.label}>
                  <span>{metric.label}</span>
                  <strong className="financial">{metric.value}</strong>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <h3>{t('section.accessibilityNotes')}</h3>
            <p className="muted">
              High contrast, reduced motion, and semantic status guidance are part of
              the foundation.
            </p>
            <div className="status-pill">
              <span>&#9679;</span>
              <span>{t('status.paperContext')}</span>
            </div>
          </section>
        </div>

        <div className="panel" style={{ marginTop: 'var(--space-4)' }}>
          <h3>Navigation</h3>
          <div className="link-list">
            <Link to="/">{t('nav.tokenReference')}</Link>
            <a href="https://thedailyroast.online" target="_blank" rel="noreferrer">
              {t('nav.productIdentity')}
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
