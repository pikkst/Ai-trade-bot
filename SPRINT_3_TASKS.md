# Sprint 3 Tasks — Frontend Application Shell

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Create the first production-quality frontend application shell for The Daily Roast AI, implementing the approved information architecture, global safety states, responsive navigation, accessibility baseline, and typed route placeholders.

## Source Documents

- `docs/FRONTEND_APPLICATION_SHELL.md`
- `docs/UI_UX_GUIDELINES.md`
- `docs/DESIGN_SYSTEM.md`
- `docs/INFORMATION_ARCHITECTURE.md`
- `docs/USER_JOURNEYS.md`
- `docs/COMPONENT_LIBRARY.md`
- `docs/DESIGN_PRINCIPLES.md`
- `docs/SECURITY.md`
- `AGENTS.md`

## S3.1 Create Frontend Tooling Baseline

### Objective

Initialize or normalize the React, TypeScript, Vite, React Router, and TanStack Query frontend foundation.

### Work

- enable TypeScript strict mode;
- configure Vite and production build output;
- add React Router and TanStack Query;
- define public environment-variable allowlist;
- add lint, type-check, test, and build scripts;
- add application and route error boundaries;
- ensure no secret-bearing environment variable can enter the client bundle.

### Acceptance Criteria

- development server starts through a documented command;
- type check passes;
- production build passes;
- only explicitly approved public environment variables are exposed;
- bundle secret scan is automated.

## S3.2 Implement Typed Route Registry

### Objective

Create one authoritative typed registry for all approved routes.

### Work

- define route ID, path, label, icon key, minimum role, navigation group, page title, and feature status;
- generate router configuration from the registry where practical;
- add placeholder pages for every route;
- add a safe not-found route;
- ensure route metadata uses approved product terminology.

### Acceptance Criteria

- every route in `docs/FRONTEND_APPLICATION_SHELL.md` exists;
- duplicate route IDs or paths fail tests;
- route labels match `docs/INFORMATION_ARCHITECTURE.md`;
- unknown routes render a recoverable not-found page.

## S3.3 Build Desktop Application Shell

### Objective

Implement the desktop shell with persistent navigation and global status visibility.

### Work

- add skip link;
- add top status bar;
- add side navigation;
- add page header and main landmark;
- add notification region;
- support optional secondary evidence panel;
- preserve semantic reading and focus order.

### Acceptance Criteria

- landmarks are correct and unique;
- keyboard users can reach all navigation items;
- active route is visually and programmatically identified;
- environment, simulation, freshness, and service state remain visible.

## S3.4 Build Mobile and Tablet Navigation

### Objective

Provide safe, compact navigation without hiding critical state.

### Work

- implement compact status bar;
- implement bottom navigation for primary destinations;
- implement accessible overflow navigation;
- verify 360 px, 768 px, and intermediate widths;
- prevent critical status truncation or disappearance.

### Acceptance Criteria

- all routes remain reachable;
- bottom-navigation items have accessible names;
- no critical status depends on hover;
- no horizontal page overflow exists at required widths.

## S3.5 Implement Global Safety-State Components

### Objective

Create reusable components for environment, simulation, freshness, service health, and halt state.

### Work

- implement `EnvironmentBadge`;
- implement `SimulationBadge`;
- implement `FreshnessIndicator`;
- implement `ServiceStateBanner`;
- define healthy, degraded, paused, halted, fresh, delayed, stale, and unknown semantics;
- provide text, icon, and accessible names for every state.

### Acceptance Criteria

- color is never the only signal;
- halted state is stronger than warning states;
- stale state remains visible on every protected page;
- simulation labeling cannot be hidden by page content.

## S3.6 Implement Reusable Page States

### Objective

Standardize loading, empty, partial, stale, error, unauthorized, and unavailable experiences.

### Work

- implement loading state without fabricated values;
- implement evidence-aware empty state;
- implement partial-data state;
- implement recoverable and unrecoverable error states;
- implement unauthorized and expired-session states;
- implement offline/API-unavailable state.

### Acceptance Criteria

- placeholders never invent prices, balances, P&L, confidence, or timestamps;
- retry actions are bounded and accessible;
- integrity failures do not appear as ordinary empty states;
- error content contains no stack trace or secret.

## S3.7 Implement Theme Foundation

### Objective

Support light, dark, and system preference through versioned design tokens.

### Work

- create token source structure;
- map semantic colors and spacing to CSS variables;
- implement theme provider and persistence;
- avoid disruptive initial theme flash where practical;
- validate status semantics in each theme.

### Acceptance Criteria

- all three preferences work;
- theme controls are keyboard accessible;
- selected preference persists locally;
- contrast checks pass for shell and status components.

## S3.8 Implement Role-Aware Navigation

### Objective

Adapt navigation visibility to viewer, operator, and owner roles while preserving server-side authority.

### Work

- implement client-side route guards for usability;
- hide owner-only settings from non-owner sessions;
- provide unauthorized state for direct navigation;
- document that API and RLS remain authoritative;
- test anonymous, viewer, operator, owner, expired, and malformed sessions.

### Acceptance Criteria

- client guards never substitute for API authorization;
- role-specific navigation tests pass;
- unauthorized routes do not leak protected data;
- authentication transitions preserve safe focus behavior.

## S3.9 Add Accessibility and Interaction Tests

### Objective

Verify the shell’s keyboard, semantic, focus, and announcement behavior.

### Work

- test skip link;
- test keyboard navigation;
- test route-change focus management;
- test visible focus indicators;
- test status announcements;
- test reduced-motion behavior;
- run automated accessibility checks.

### Acceptance Criteria

- no critical automated accessibility violation remains;
- no keyboard trap exists;
- route changes announce a meaningful page title;
- motion respects user preference.

## S3.10 Add Visual and Build Verification

### Objective

Create objective evidence that the shell is stable across states and viewports.

### Work

- capture visual-regression baselines or equivalent screenshots;
- cover desktop, tablet, and mobile;
- cover light and dark themes;
- cover healthy, stale, degraded, paused, and halted states;
- run production build and bundle scan;
- document the verification command set.

### Acceptance Criteria

- visual evidence exists for required combinations;
- production build is reproducible;
- built assets contain no secret patterns;
- route placeholders render without runtime errors.

## Sprint Exit Gate

Sprint 3 is complete only when:

- S3.1 through S3.10 are complete;
- all approved routes are implemented as typed placeholders;
- desktop and mobile shells are verified;
- safety states are globally visible;
- accessibility and role behavior are tested;
- build and bundle scans pass;
- documentation and changelog are updated;
- the completed sprint is committed and the resulting commit is fetched and verified.