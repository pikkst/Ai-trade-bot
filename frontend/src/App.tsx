import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import './App.css';
import './styles/tokens.css';
import { formatCurrency, formatPercent } from './lib/format';

type ThemeOption = 'light' | 'dark' | 'system';

const themeOptions: Array<{ value: ThemeOption; label: string }> = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System' },
];

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

  const metrics = useMemo(
    () => [
      { label: 'Portfolio', value: formatCurrency(12540.5, { currency: 'EUR' }) },
      { label: 'Drawdown', value: formatPercent(-0.085) },
      { label: 'Evidence freshness', value: '2m ago' },
    ],
    []
  );

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-title">
          <p className="muted">Evidence-Driven Market Intelligence</p>
          <h1>The Daily Roast AI</h1>
          <p className="muted">
            Design tokens · theme-ready foundation · financial clarity
          </p>
        </div>
        <div className="theme-switcher" role="group" aria-label="Theme selection">
          {themeOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              aria-pressed={theme === option.value}
              onClick={() => setTheme(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </header>

      <main className="app-main">
        <div className="grid">
          <section className="panel">
            <h2>Design tokens</h2>
            <p className="muted">
              Versioned visual primitives for calm, trustworthy evidence displays.
            </p>
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
            <h3>Reference metrics</h3>
            <div className="token-list">
              {metrics.map((metric) => (
                <div className="token-chip" key={metric.label}>
                  <span>{metric.label}</span>
                  <strong>{metric.value}</strong>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <h3>Accessibility notes</h3>
            <p className="muted">
              High contrast, reduced motion, and semantic status guidance are part of
              the foundation.
            </p>
            <div className="status-pill">
              <span>●</span>
              <span>Paper-only context</span>
            </div>
          </section>
        </div>

        <div className="panel" style={{ marginTop: '1rem' }}>
          <h3>Navigation</h3>
          <div className="link-list">
            <Link to="/">Token reference</Link>
            <a href="https://thedailyroast.online" target="_blank" rel="noreferrer">
              Product identity
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
