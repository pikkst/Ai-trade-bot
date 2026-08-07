import { readFileSync } from 'node:fs';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router';
import App from '../App';
import { formatCurrency, formatPercent } from '../lib/format';
import { getContent } from '../lib/content';
import { contrastRatio } from './contrast';

const appCss = readFileSync(new URL('../App.css', import.meta.url), 'utf8');
const baseTokensCss = readFileSync(
  new URL('../styles/tokens.css', import.meta.url),
  'utf8'
);
const statusTokensCss = readFileSync(
  new URL('../styles/status-tokens.css', import.meta.url),
  'utf8'
);

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function tokenValue(css: string, token: string, selector = ':root'): string {
  const block = css.match(
    new RegExp(`${escapeRegExp(selector)}\\s*\\{([\\s\\S]*?)\\}`)
  );
  if (!block) throw new Error(`Missing CSS selector: ${selector}`);

  const match = block[1].match(new RegExp(`${escapeRegExp(token)}\\s*:\\s*([^;]+);`));
  if (!match) throw new Error(`Missing token ${token} in ${selector}`);
  return match[1].trim();
}

describe('App', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
  });

  it('renders the token reference experience and product identity', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    expect(
      screen.getByRole('heading', { name: /the daily roast ai/i })
    ).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /design tokens/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /token reference/i })).toBeInTheDocument();
  });

  it('switches to dark theme and persists the preference', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    await user.click(screen.getByRole('button', { name: /dark/i }));

    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(localStorage.getItem('daily-roast-theme')).toBe('dark');
  });

  it('formats financial values for evidence-first displays', () => {
    expect(formatCurrency(1234.5, { currency: 'EUR' })).toBe('€1,234.50');
    expect(formatPercent(0.125)).toBe('12.5%');
  });
});

describe('Localization', () => {
  it('currency formatting is locale-aware (en-IE vs et-EE)', () => {
    const en = formatCurrency(1234567.89, { currency: 'EUR', locale: 'en' });
    const et = formatCurrency(1234567.89, { currency: 'EUR', locale: 'et' });

    expect(en).toBe('€1,234,567.89');
    expect(et).not.toBe(en);
    expect(et).toContain('€');
    expect(et).not.toMatch(/^€/);
    expect(et).toContain(',');
    expect(et).not.toContain('.');
  });

  it('percent formatting is locale-aware (en-IE vs et-EE)', () => {
    const en = formatPercent(0.1235, { locale: 'en' });
    const et = formatPercent(0.1235, { locale: 'et' });

    expect(en).toBe('12.4%');
    expect(et).toBe('12,4%');
    expect(et).not.toBe(en);
  });

  it('keeps the official product name unchanged across locales', () => {
    expect(getContent('et', 'app.title')).toBe('The Daily Roast AI');
  });

  it('exposes reviewed Estonian content keys', () => {
    expect(getContent('en', 'nav.tokenReference')).toBe('Token reference');
    expect(getContent('et', 'nav.tokenReference')).toBe('Tokenite ülevaade');
    expect(getContent('et', 'theme.dark')).toBe('Tume');
  });
});

describe('Accessibility — design token contract', () => {
  it('tests WCAG contrast against the actual light theme CSS tokens', () => {
    const checks = [
      ['--color-brand-on', '--color-brand'],
      ['--color-status-healthy-on', '--color-status-healthy-bg'],
      ['--color-status-degraded-on', '--color-status-degraded-bg'],
      ['--color-status-halted-on', '--color-status-halted-bg'],
      ['--color-status-paused-on', '--color-status-paused-bg'],
    ] as const;

    for (const [foreground, background] of checks) {
      expect(
        contrastRatio(
          tokenValue(baseTokensCss, foreground),
          tokenValue(baseTokensCss, background)
        )
      ).toBeGreaterThanOrEqual(4.5);
    }
  });

  it('defines complete AI and deterministic semantic status token sets', () => {
    for (const state of ['ai', 'deterministic']) {
      for (const suffix of ['', '-bg', '-border', '-on']) {
        expect(
          tokenValue(statusTokensCss, `--color-status-${state}${suffix}`)
        ).toBeTruthy();
      }
    }
  });

  it('keeps reduced-motion tokens and production media-query behavior', () => {
    expect(baseTokensCss).toContain('--motion-duration-none: 0s');
    expect(baseTokensCss).toContain('--motion-duration-fast: 160ms');
    expect(baseTokensCss).toContain('--motion-duration-base: 240ms');
    expect(appCss).toContain('@media (prefers-reduced-motion: reduce)');
    expect(appCss).toContain('animation-duration: 0.01ms !important');
    expect(appCss).toContain('transition-duration: 0.01ms !important');
    expect(appCss).toContain('scroll-behavior: auto !important');
  });
});
