import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { formatCurrency, formatPercent } from '../lib/format';
import { contrastRatio } from './contrast';
import { getContent } from '../lib/content';

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

  it('falls back to English content keys', () => {
    expect(getContent('et', 'app.title')).toBe('The Daily Roast AI');
  });

  it('exposes supported locale content keys', () => {
    expect(getContent('en', 'nav.tokenReference')).toBe('Token reference');
    expect(getContent('et', 'nav.tokenReference')).toBe('Atomaadne viide');
  });
});

describe('Accessibility — contrast', () => {
  it('theme button foreground meets WCAG AA on brand background in dark mode', () => {
    const ratio = contrastRatio('#102a5e', '#6ea0ff');
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it('brand-strong heading text meets WCAG AA on dark background', () => {
    const ratio = contrastRatio('#a7c5ff', '#07111f');
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });

  it('all semantic status tokens meet WCAG AA contrast', () => {
    const lightChecks: Array<{ on: string; bg: string; name: string }> = [
      { on: '#102a5e', bg: '#dcf5e7', name: 'healthy-light' },
      { on: '#102a5e', bg: '#fff3e0', name: 'degraded-light' },
      { on: '#102a5e', bg: '#fde8e8', name: 'halted-light' },
      { on: '#07111f', bg: '#e8f2fa', name: 'paused-light' },
    ];
    const darkChecks: Array<{ on: string; bg: string; name: string }> = [
      { on: '#e8eef8', bg: '#1a2d42', name: 'paused-dark' },
      { on: '#e8eef8', bg: '#3a1a1a', name: 'halted-dark-bg' },
      { on: '#e8eef8', bg: '#1a3a2a', name: 'approved-dark-bg' },
      { on: '#e8eef8', bg: '#2a1a3a', name: 'simulated-dark-bg' },
      { on: '#e8eef8', bg: '#3a2a0a', name: 'degraded-dark-bg' },
    ];
    for (const check of [...lightChecks, ...darkChecks]) {
      const ratio = contrastRatio(check.on, check.bg);
      expect(ratio).toBeGreaterThanOrEqual(4.5);
    }
  });
});
