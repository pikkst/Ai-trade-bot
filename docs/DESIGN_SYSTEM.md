# Design System

Last reviewed: 2026-07-31  
Status: Authoritative visual-system specification

## 1. Purpose

Define the reusable visual language for The Daily Roast AI across the public website, authenticated application, reports, documentation, and future mobile experiences.

## 2. Design Direction

The product should feel:

- analytical;
- calm;
- trustworthy;
- modern;
- evidence-driven;
- operationally clear.

It must not resemble a casino, meme-token campaign, or high-pressure trading terminal.

## 3. Design Tokens

All visual values must be represented as named tokens rather than scattered literals.

Token groups:

- color;
- typography;
- spacing;
- sizing;
- radius;
- shadow;
- border;
- motion;
- z-index;
- chart semantics.

## 4. Color System

### Brand Foundation

- `brand-900`: deep navy for primary surfaces and high-trust headings
- `brand-700`: primary interactive color
- `brand-500`: active and accent state
- `roast-500`: warm amber brand accent
- `slate-*`: neutral surfaces and text

### Semantic Colors

- success: completed, reconciled, healthy
- warning: degraded, threshold proximity, stale soon
- danger: rejected, halted, integrity failure
- info: neutral system information
- ai: Gemini-generated interpretation
- deterministic: rule-derived evidence

Semantic meaning must remain consistent in light and dark themes.

Color alone must never communicate status.

## 5. Theme Strategy

Support:

- light theme;
- dark theme;
- system preference.

Dark mode must be designed, not produced by simple inversion. Charts, borders, focus states, and semantic statuses require explicit dark tokens.

## 6. Typography

Preferred UI typeface: Inter or an equivalent open, highly legible sans-serif.

Preferred monospace typeface: JetBrains Mono or a compatible fallback.

Type scale:

- display;
- page title;
- section title;
- card title;
- body;
- small body;
- label;
- caption;
- code/financial tabular value.

Financial numbers should use tabular numerals where supported.

## 7. Spacing and Layout

Use a 4px base grid.

Recommended spacing scale:

`4, 8, 12, 16, 24, 32, 48, 64`

Use responsive containers and avoid arbitrary page-specific spacing.

Primary application layout:

- global header;
- left navigation on desktop;
- main content region;
- optional context panel;
- mobile bottom or drawer navigation.

## 8. Shape and Elevation

- moderate corner radius;
- subtle borders;
- minimal shadows;
- strong elevation only for overlays and critical dialogs.

Avoid excessive glassmorphism, gradients, and decorative blur that reduce clarity.

## 9. Motion

Motion must explain state changes, not decorate them.

Requirements:

- short, predictable transitions;
- no animation for critical financial values that obscures the final number;
- respect `prefers-reduced-motion`;
- loading skeletons may be used where layout is known;
- no pulsing urgency effects for ordinary market movement.

## 10. Icons

Use one consistent outline icon family.

Icons must:

- support labels for critical actions;
- use accessible names;
- avoid crypto-hype symbols such as rockets and moons;
- distinguish AI, evidence, risk, simulation, audit, and system health.

## 11. Data Visualization

Charts must prioritize accuracy and interpretation.

Rules:

- label units and time zones;
- disclose missing data;
- show benchmark and portfolio series distinctly;
- avoid misleading truncated axes unless clearly indicated;
- provide accessible summaries;
- use consistent colors for cash, portfolio, benchmark, drawdown, risk, and AI overlays;
- never imply live execution where data is simulated.

## 12. Core Visual Patterns

### Evidence Card

Contains metric, source, timestamp, interpretation, and freshness.

### AI Analysis Card

Contains Gemini label, confidence, evidence references, risks, contradictions, and validation state.

### Risk Decision Panel

Contains outcome, reason codes, limits, requested versus approved values, and halt information.

### Portfolio Summary

Contains virtual cash, equity, exposure, P&L, drawdown, fees, and reconciliation.

### Environment Banner

Displays Local, Demo, Paper, Staging, or Production Research.

## 13. Forms

- labels are always visible;
- required fields are explicit;
- validation appears near the field and in summary form when necessary;
- numeric fields show units;
- risk settings show safe ranges and consequences;
- destructive actions are visually separated from normal actions.

## 14. Tables

Tables must support:

- clear column labels;
- deterministic sorting;
- pagination or virtualization;
- keyboard navigation where interactive;
- mobile alternatives;
- decimal alignment;
- empty and error states;
- export where specified.

## 15. Token Governance

Design tokens must live in version-controlled source and be consumable by frontend components.

Changes to semantic tokens require:

- visual review;
- accessibility check;
- component regression review;
- changelog entry if user-visible.

## 16. Definition of Done

The design system is implementation-ready when:

- token files exist;
- light and dark themes are covered;
- typography and spacing are implemented;
- core components consume tokens;
- visual regression tests exist;
- accessibility contrast checks pass;
- Storybook or equivalent component documentation is available.

## 17. Related Documents

- `BRAND_GUIDELINES.md`
- `DESIGN_PRINCIPLES.md`
- `UI_UX_GUIDELINES.md`
- `COMPONENT_LIBRARY.md`
- `LANDING_PAGE.md`
