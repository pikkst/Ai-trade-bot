export function formatCurrency(value: number, options?: { currency?: string }) {
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency: options?.currency ?? 'EUR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatPercent(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}
