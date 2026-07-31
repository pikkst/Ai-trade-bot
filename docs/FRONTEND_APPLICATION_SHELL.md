# Frontend Application Shell Specification

Last reviewed: 2026-07-31  
Status: Sprint 3 authoritative frontend-shell specification

## 1. Purpose

This document defines the first implementable React application shell for The Daily Roast AI. The shell establishes routing, navigation, page-state contracts, accessibility behavior, environment labeling, and evidence-first presentation before feature pages are implemented.

The shell must not imply live trading, guaranteed returns, or autonomous AI execution. Every active product mode remains research or simulated trading.

## 2. Scope

Sprint 3 covers:

- application shell layout;
- route inventory and route metadata;
- global navigation;
- environment and simulation banners;
- global freshness, degraded, paused, and halted states;
- authenticated and unauthenticated boundaries;
- responsive behavior;
- accessibility baseline;
- error, empty, loading, and unavailable-state contracts;
- page placeholders for the approved information architecture.

Sprint 3 does not implement market charts, trading logic, backtests, portfolio accounting, Gemini requests, or production authentication flows.

## 3. Approved Route Inventory

| Route | Page | Minimum role | Primary purpose |
|---|---|---:|---|
| `/` | Landing | Public | Explain the product and open the demo |
| `/login` | Sign in | Public | Authenticate an approved user |
| `/today` | Today's Roast | Viewer | Latest evidence, freshness, contradictions, risk, and simulation status |
| `/markets` | Markets | Viewer | Market universe and data-quality overview |
| `/markets/:symbol` | Market detail | Viewer | Snapshot, features, evidence, and lineage |
| `/research` | Research | Viewer | Deterministic and Gemini-assisted reports |
| `/research/:analysisId` | Research detail | Viewer | Validated report, evidence, uncertainty, and provenance |
| `/strategies` | Strategies | Viewer | Strategy versions and current status |
| `/paper-portfolio` | Paper Portfolio | Viewer | Simulated balances, positions, orders, fills, and reconciliation |
| `/backtests` | Backtests | Viewer | Reproducible runs and benchmarks |
| `/backtests/:runId` | Backtest detail | Viewer | Metrics, assumptions, lineage, and trade ledger |
| `/experiments` | Experiments | Viewer | Paper-experiment status and history |
| `/experiments/:experimentId` | Experiment detail | Viewer | Frozen configuration, cycle status, results, and audit trail |
| `/audit` | Audit | Viewer | Filterable decision and operation history |
| `/settings` | Settings | Owner | Workspace, risk, AI budget, and environment configuration |
| `*` | Not found | Public | Safe route recovery |

Route guards improve usability only. The API and database remain authoritative for authorization.

## 4. Shell Layout

Desktop shell:

1. skip link;
2. top status bar;
3. persistent side navigation;
4. page header with title, context, freshness, and mode;
5. main content region;
6. optional evidence or detail drawer;
7. global notification region.

Mobile shell:

1. skip link;
2. compact status bar;
3. page header;
4. main content;
5. bottom navigation for Today, Markets, Research, Portfolio, and More;
6. modal navigation for remaining routes.

The shell must preserve reading order and keyboard focus when navigation changes.

## 5. Global Status Contract

The shell must expose these independent dimensions:

- environment: local, demo, paper, staging, production research;
- simulation mode: active or unavailable;
- data freshness: fresh, delayed, stale, or unknown;
- service state: healthy, degraded, paused, or halted;
- authentication state: anonymous, authenticated, expired, or unauthorized.

Color may reinforce status but must never be the only signal. Every status requires text and an accessible name.

A halted state must be visually stronger than ordinary warnings and must remain visible across all protected routes.

## 6. Navigation Rules

- Use the approved product names from `docs/NAMING_CONVENTIONS.md`.
- Do not use “Trade Now,” “Buy,” “Sell,” or equivalent execution CTAs in the MVP shell.
- The active route must be programmatically identifiable.
- Collapsed navigation must retain accessible labels and tooltips.
- Navigation badges may show stale, degraded, or halted state but not speculative profit signals.
- Settings is visible only to owner-capable sessions, while authorization remains server-enforced.

## 7. Page-State Contract

Every routed page must support:

- initial loading;
- background refresh;
- empty state;
- partial-data state;
- stale-data state;
- authorization failure;
- recoverable request failure;
- unrecoverable integrity or halt state;
- offline or API-unavailable state.

Loading placeholders must not display fabricated prices, balances, P&L, confidence, or timestamps.

Empty states must explain what evidence or process is missing and must not imply that no risk exists.

## 8. Accessibility Baseline

The implementation target is WCAG 2.2 AA where practical.

Required baseline:

- semantic landmarks and headings;
- keyboard-accessible navigation and controls;
- visible focus indicators;
- skip-to-content link;
- no keyboard traps;
- status messages announced appropriately;
- accessible route-change title and focus management;
- minimum pointer-target sizing;
- reduced-motion support;
- contrast validation for light and dark themes;
- charts and status graphics must have textual equivalents when implemented.

## 9. Responsive Behavior

The shell must support at minimum:

- 360 px mobile viewport;
- 768 px tablet viewport;
- 1280 px desktop viewport;
- 1920 px wide desktop viewport.

No critical status, freshness, risk, simulation, or halt information may disappear at smaller widths.

Wide layouts may add evidence drawers or secondary panels, but the primary content order must remain stable.

## 10. Theme Contract

Supported preferences:

- light;
- dark;
- system.

Theme selection must persist locally without storing secrets or sensitive account data. The initial render should avoid a disruptive theme flash where practical.

Status semantics must remain consistent across themes.

## 11. Frontend Architecture

Required baseline:

- React;
- TypeScript strict mode;
- Vite;
- React Router;
- TanStack Query for server state;
- project-owned design tokens;
- reusable shell and status components;
- route metadata stored in one typed registry;
- error boundaries at application and route level;
- environment variables exposed through an explicit public allowlist.

The shell must not contain provider secrets, service-role credentials, private exchange credentials, or hidden authorization assumptions.

## 12. Required Components

- `AppShell`
- `SkipLink`
- `GlobalStatusBar`
- `EnvironmentBadge`
- `SimulationBadge`
- `FreshnessIndicator`
- `ServiceStateBanner`
- `PrimaryNavigation`
- `MobileNavigation`
- `PageHeader`
- `RouteGuard`
- `LoadingState`
- `EmptyState`
- `ErrorState`
- `UnauthorizedState`
- `NotFoundPage`
- `ErrorBoundary`

Component behavior must follow `docs/COMPONENT_LIBRARY.md` and `docs/DESIGN_SYSTEM.md`.

## 13. Testing Requirements

At minimum:

- route-registry unit tests;
- navigation rendering by role;
- keyboard navigation tests;
- accessibility checks for shell landmarks and labels;
- environment and simulation labeling tests;
- stale, degraded, paused, and halted state tests;
- mobile navigation tests;
- error-boundary tests;
- unknown-route recovery test;
- production build verification;
- frontend-bundle secret scan.

## 14. Acceptance Criteria

Sprint 3 shell implementation is accepted when:

1. every approved route exists as a typed placeholder page;
2. desktop and mobile navigation expose the approved information architecture;
3. environment, simulation, freshness, and service state remain visible;
4. protected routes have client-side usability guards without claiming security authority;
5. all global page states have reusable components;
6. keyboard navigation and focus management are verified;
7. light, dark, and system themes work;
8. no secret is present in source maps or built assets;
9. automated shell tests pass;
10. implementation screenshots or visual-regression baselines are recorded.

## 15. Definition of Done

- implementation matches this document and the design foundation;
- route inventory is documented and generated from typed metadata;
- accessibility checks pass at the agreed baseline;
- responsive layouts are verified at the required viewports;
- risk, freshness, uncertainty, halt, and simulation labels are not hidden;
- tests and build pass;
- documentation and changelog are updated;
- the completed work is committed as one sprint-scoped change.