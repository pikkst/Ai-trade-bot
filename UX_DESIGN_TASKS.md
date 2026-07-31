# UX and Design Implementation Tasks

Last reviewed: 2026-07-31  
Status: Active supplemental backlog for The Daily Roast AI frontend

Each task is independently implementable and must follow `AGENTS.md`, `docs/UI_UX_GUIDELINES.md`, and `docs/DESIGN_SYSTEM.md`.

---

## [ ] UX1 — Implement Versioned Design Tokens

**Priority:** P0

### Description

Create the frontend token foundation for color, typography, spacing, radius, border, shadow, motion, z-index, and chart semantics.

### User Story

As the frontend team, I want one version-controlled token system, so that the product remains visually consistent and accessible across themes and components.

### Acceptance Criteria

- Token source files exist in a documented path.
- Light, dark, and system themes are supported.
- Semantic status tokens cover healthy, degraded, stale, paused, halted, approved, rejected, simulated, AI, and deterministic states.
- Components do not use undocumented hardcoded visual values.
- Contrast checks pass for required text and status combinations.
- Tabular numerals are enabled for financial values where supported.
- Reduced-motion tokens exist.

### Definition of Done

- Tokens are consumed by at least one reference component.
- Token documentation is generated or committed.
- Visual and accessibility checks pass.
- Design-system documentation matches implementation.

### Dependencies

- Frontend initialization task

### References

- `docs/DESIGN_SYSTEM.md`
- `docs/BRAND_GUIDELINES.md`

---

## [ ] UX2 — Create Application Shell and Responsive Navigation

**Priority:** P0

### Description

Implement the authenticated application shell, desktop navigation, mobile navigation, breadcrumbs, environment banner, and page layout.

### User Story

As a user, I want consistent navigation and visible environment state, so that I always know where I am and whether I am viewing local, demo, paper, staging, or production research data.

### Acceptance Criteria

- Primary navigation matches `INFORMATION_ARCHITECTURE.md`.
- Current route is visibly identified.
- Keyboard navigation and focus order work.
- Mobile navigation uses the approved reduced structure.
- Environment and simulation state remain visible.
- Unauthorized routes are blocked server-side and represented safely in the UI.
- Deep links and browser refresh work.

### Definition of Done

- Desktop and mobile E2E navigation tests pass.
- Accessibility checks pass.
- No secret appears in rendered configuration.

### Dependencies

- UX1
- Authentication foundation

### References

- `docs/INFORMATION_ARCHITECTURE.md`
- `docs/UI_UX_GUIDELINES.md`

---

## [ ] UX3 — Build Core Accessible Component Library

**Priority:** P0

### Description

Implement the foundational form, feedback, overlay, navigation, and layout components defined in the component-library specification.

### User Story

As a contributor, I want reusable accessible components, so that product screens do not reimplement inconsistent controls and states.

### Acceptance Criteria

- Buttons, links, form fields, select, checkbox, switch, dialog, drawer, tabs, tooltip, alert, badge, skeleton, empty state, and error state are implemented.
- Components consume design tokens.
- Loading, disabled, validation, and error behavior is documented.
- Keyboard interaction follows expected patterns.
- Storybook or an approved equivalent documents states.
- Automated accessibility tests exist.

### Definition of Done

- Component tests and visual regression pass.
- Light and dark stories exist.
- Prohibited usage is documented where safety-relevant.

### Dependencies

- UX1

### References

- `docs/COMPONENT_LIBRARY.md`
- `docs/DESIGN_SYSTEM.md`

---

## [ ] UX4 — Implement System, Data, and Risk Status Components

**Priority:** P0

### Description

Create reusable components for environment, health, freshness, reconciliation, provider, risk, drawdown, and halt states.

### User Story

As a user, I want critical safety state presented consistently, so that stale data, rejected decisions, and integrity failures cannot be overlooked.

### Acceptance Criteria

- EnvironmentBadge, SystemHealthBanner, DataFreshnessIndicator, ReconciliationBadge, ProviderStatus, RiskDecisionPanel, DrawdownGauge, and HaltBanner exist.
- Status is communicated with text and icon, not color alone.
- Reason codes have plain-language explanations.
- Halt state includes scope, trigger, timestamp, and recovery link.
- Tests cover all semantic states.

### Definition of Done

- Accessibility and visual regression pass.
- Components are used in reference screens.
- Risk and reconciliation information cannot be hidden by responsive layouts.

### Dependencies

- UX3

### References

- `docs/UI_UX_GUIDELINES.md`
- `docs/RISK_ENGINE.md`
- `docs/OBSERVABILITY.md`

---

## [ ] UX5 — Build Today Dashboard

**Priority:** P1

### Description

Implement the default authenticated dashboard that summarizes system health, market freshness, latest research, strategy/risk outcome, paper portfolio, and cycle status.

### User Story

As a user, I want one concise daily overview, so that I can understand the current system and market state before opening detailed reports.

### Acceptance Criteria

- Displays environment and simulation labels.
- Displays last successful cycle and data freshness.
- Displays latest regime, evidence summary, Gemini status, strategy intent, and risk outcome.
- Displays paper portfolio equity, exposure, drawdown, and reconciliation.
- Displays warnings, halts, and provider degradation.
- Links to complete decision lineage.
- Supports loading, empty, stale, partial, and error states.

### Definition of Done

- Component, accessibility, responsive, and E2E tests pass.
- Sample content is clearly labeled.
- No AI confidence is presented as expected return.

### Dependencies

- UX2
- UX4
- Backend read models

### References

- `docs/UI_UX_GUIDELINES.md`
- `docs/USER_JOURNEYS.md`

---

## [ ] UX6 — Build Market and Research Detail Experience

**Priority:** P1

### Description

Implement market overview and research detail screens with evidence, Gemini interpretation, contradictions, strategy, risk, and lineage.

### User Story

As an analyst, I want deterministic evidence and AI interpretation presented separately, so that I can inspect the basis and limitations of each decision.

### Acceptance Criteria

- Market tabs match the information architecture.
- Only finalized-data status is represented as decision-ready.
- Gemini report shows model/schema/prompt version, confidence, evidence, contradictions, risks, missing information, and validation state.
- Strategy and risk results link to exact versions.
- Stale or rejected analysis is visibly marked.
- Accessible chart summaries exist.

### Definition of Done

- E2E lineage flow passes.
- Mobile review remains usable.
- No hidden or unsupported claim is introduced by frontend copy.

### Dependencies

- UX3
- UX4
- Market and analysis APIs

### References

- `docs/INFORMATION_ARCHITECTURE.md`
- `docs/AI_ARCHITECTURE.md`
- `docs/MARKET_DATA.md`

---

## [ ] UX7 — Build Paper Portfolio and Backtest Experiences

**Priority:** P1

### Description

Implement the paper portfolio, orders, fills, ledger, performance, reconciliation, backtest builder, and report views.

### User Story

As a user, I want realistic simulation results and assumptions exposed, so that I can evaluate performance without confusing it with live trading.

### Acceptance Criteria

- Paper-trading label remains visible throughout.
- Portfolio shows cash, equity, exposure, fees, P&L, drawdown, and reconciliation.
- Order, fill, and ledger tables support required states and pagination.
- Backtest reports disclose strategy, risk, data range, fees, slippage, benchmark, warnings, and reproducibility metadata.
- Ambiguous or incomplete results are not presented as definitive.
- Export actions enforce authorization.

### Definition of Done

- Financial formatting and accessibility tests pass.
- Cash and buy-and-hold comparisons are visible.
- E2E tests cover rejected order and reconciliation mismatch.

### Dependencies

- UX3
- Portfolio and backtest APIs

### References

- `docs/PAPER_TRADING.md`
- `docs/PORTFOLIO_ENGINE.md`
- `docs/BACKTEST_ENGINE.md`

---

## [ ] UX8 — Implement Public Landing Page

**Priority:** P1

### Description

Build the public The Daily Roast AI landing page at `thedailyroast.online` according to the approved content and trust requirements.

### User Story

As a prospective user, I want to understand the product, methodology, and limitations before signing in, so that I can evaluate it without misleading financial claims.

### Acceptance Criteria

- Hero uses official name and tagline.
- Primary CTA is Open the Demo.
- Methodology, safety, simulation, evidence, risk, and audit sections exist.
- Gemini advisory role is explicit.
- No fabricated statistics, testimonials, or security claims.
- FAQ covers advice, real money, AI authority, data, backtesting, profit, markets, and privacy.
- SEO metadata and social preview are configured.
- Performance and accessibility budgets pass.

### Definition of Done

- Cloudflare Pages preview deploy succeeds.
- Mobile and desktop checks pass.
- Legal/privacy links are present before public production launch.
- No secret or private environment value exists in the bundle.

### Dependencies

- UX1
- UX3

### References

- `docs/LANDING_PAGE.md`
- `docs/BRAND_GUIDELINES.md`

---

## [ ] UX9 — Add Visual Regression and Accessibility CI

**Priority:** P0

### Description

Add automated component accessibility, visual regression, route-state, and responsive checks to CI.

### User Story

As the development team, I want visual and accessibility regressions detected automatically, so that safety-critical state is not lost through styling changes.

### Acceptance Criteria

- Core components have visual snapshots or approved screenshot baselines.
- Accessibility checks run on primary stories and routes.
- Light, dark, mobile, stale, halted, and error states are covered.
- Changes require reviewed baseline updates.
- CI artifacts make failures inspectable.

### Definition of Done

- Deliberate contrast and hidden-status regressions fail CI and are reverted.
- Workflow is documented.

### Dependencies

- UX3
- UX4

### References

- `docs/TEST_ENVIRONMENTS.md`
- `docs/DESIGN_SYSTEM.md`

---

## [ ] UX10 — Generate Frontend Route and Component Inventory

**Priority:** P1

### Description

Create a generated report of frontend routes, required roles, page components, loading/error states, and test coverage.

### User Story

As the development team, I want an automatically generated interface inventory, so that undocumented routes and untested states are identified.

### Acceptance Criteria

- Generator scans the approved route and page directories.
- Report includes route, role, environment availability, source file, major components, and related tests.
- Missing authorization documentation is identified.
- Missing loading, error, stale, or halted tests are identified where required.
- Output is generated as `docs/frontend-inventory.md`.
- CI verifies that the report is current.
- Invalid route metadata causes a non-zero exit.

### Definition of Done

- Generator and package command exist.
- Generated report is committed.
- CI check exists.
- Existing routes are included.
- Tests, lint, type checks, and build pass.

### Dependencies

- UX2

### References

- `docs/INFORMATION_ARCHITECTURE.md`
- `docs/TEST_ENVIRONMENTS.md`

### Notes

This task is largely independent after route initialization and can be worked on in parallel.
