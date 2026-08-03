/* =============================================================================
 * WCAG 2.1 contrast-ratio utilities for accessibility testing.
 * Used by contrast tests; not shipped to production.
 * ========================================================================== */

function hexToComponents(hex: string): [number, number, number] {
  let clean = hex.replace('#', '');
  if (clean.length === 3) {
    clean = clean
      .split('')
      .map((c) => c + c)
      .join('');
  }
  const num = parseInt(clean, 16);
  return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
}

function relativeLuminance(hex: string): number {
  const [r, g, b] = hexToComponents(hex).map((c) => c / 255);
  const channel = (value: number) => {
    return value <= 0.03928 ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);
  };
  const R = channel(r);
  const G = channel(g);
  const B = channel(b);
  return 0.2126 * R + 0.7152 * G + 0.0722 * B;
}

export function contrastRatio(hexA: string, hexB: string): number {
  const lumA = relativeLuminance(hexA);
  const lumB = relativeLuminance(hexB);
  const lighter = Math.max(lumA, lumB);
  const darker = Math.min(lumA, lumB);
  return (lighter + 0.05) / (darker + 0.05);
}

export function passesAA(normal: boolean, ratio: number): boolean {
  return normal ? ratio >= 4.5 : ratio >= 3.0;
}

export function passesAAA(normal: boolean, ratio: number): boolean {
  return normal ? ratio >= 7 : ratio >= 4.5;
}
