import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';
import { formatCurrency, formatPercent } from '../lib/format';

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
