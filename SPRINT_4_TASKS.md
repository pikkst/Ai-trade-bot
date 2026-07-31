# Sprint 4 Tasks — Core Accessible Component Library

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Define and implement the reusable, accessible, token-driven component foundation required by The Daily Roast AI product screens while making unsafe or misleading presentation difficult by default.

## Authoritative References

- `docs/CORE_COMPONENT_LIBRARY_IMPLEMENTATION.md`
- `docs/COMPONENT_LIBRARY.md`
- `docs/DESIGN_SYSTEM.md`
- `docs/UI_UX_GUIDELINES.md`
- `docs/FRONTEND_APPLICATION_SHELL.md`
- `docs/DESIGN_PRINCIPLES.md`
- `docs/NAMING_CONVENTIONS.md`
- `docs/SECURITY.md`
- `AGENTS.md`

## S4.1 Establish Component Package Boundaries

### Objective

Create the public and internal component package structure with controlled exports.

### Work

- create primitive, feedback, navigation, overlay, data-display, layout, safety, and internal directories;
- define public barrel exports;
- prevent internal utilities from becoming public API;
- document naming and file conventions;
- add duplicate-export and circular-dependency checks;
- ensure frontend components do not import backend or server-only modules.

### Acceptance Criteria

- package structure matches the Sprint 4 specification;
- all public exports are intentional and typed;
- internal modules cannot be imported through the public package entry point;
- no circular dependency exists;
- no server secret or server-only dependency is bundled.

## S4.2 Implement Action Primitives

### Objective

Implement buttons, links, and icon actions with correct semantics and safe states.

### Work

- implement `Button`, `Link`, and `IconButton`;
- implement primary, secondary, quiet, danger, link-style, and icon-only variants;
- implement disabled and loading behavior;
- preserve accessible labels during loading;
- add focus-visible behavior;
- document forbidden execution-oriented MVP labels.

### Acceptance Criteria

- actions use native button or anchor semantics correctly;
- icon-only actions require accessible names;
- disabled state is not communicated by opacity alone;
- loading prevents duplicate activation where required;
- keyboard and automated accessibility tests pass;
- stories cover every variant and state.

## S4.3 Implement Form Foundation

### Objective

Create accessible form controls and validation relationships.

### Work

- implement `Field`, `Label`, `Description`, `Input`, `Textarea`, `Select`, `Checkbox`, `RadioGroup`, `Switch`, and `FormMessage`;
- associate labels, help text, and errors through stable IDs;
- support required, disabled, read-only, invalid, and loading states;
- define numeric and financial input unit presentation;
- prohibit secret-prefill patterns;
- document when switches are inappropriate.

### Acceptance Criteria

- every control has a programmatic name;
- help and error descriptions are announced;
- placeholder text is never the only label;
- validation behavior is deterministic and tested;
- financial inputs display explicit units;
- no component performs financial domain arithmetic.

## S4.4 Implement Feedback and Page-State Primitives

### Objective

Standardize alerts, status metadata, loading, empty, and error experiences.

### Work

- implement `Alert`, `Badge`, `StatusLabel`, `Progress`, `Spinner`, `Skeleton`, `InlineMessage`, `EmptyState`, and `ErrorState`;
- define information, success, warning, and critical semantics;
- prohibit plausible fabricated financial skeleton values;
- distinguish empty, unavailable, unauthorized, stale, halted, and integrity-failure states;
- add accessible status announcements where appropriate.

### Acceptance Criteria

- color is never the only status signal;
- critical alerts expose impact and investigation or recovery path;
- loading states do not invent prices, balances, P&L, confidence, or timestamps;
- integrity failures cannot render as ordinary empty states;
- error states expose no stack trace, provider payload, SQL, token, or secret.

## S4.5 Implement Overlay Primitives

### Objective

Create accessible overlays with reliable focus and dismissal behavior.

### Work

- implement `Dialog`, `AlertDialog`, `Drawer`, `Popover`, and `Tooltip`;
- implement portal and layering behavior;
- implement focus trapping only where required;
- restore focus after close;
- handle Escape and outside interaction according to component semantics;
- handle mobile scroll locking;
- document when essential information must not be placed in overlays.

### Acceptance Criteria

- no keyboard trap exists;
- initial and returned focus are correct;
- critical warnings are not tooltip-only or hidden in closed drawers;
- modal background content is correctly unavailable to assistive technology;
- nested overlay behavior is either supported and tested or explicitly prohibited;
- mobile viewport tests pass.

## S4.6 Implement Navigation and Disclosure Primitives

### Objective

Provide accessible building blocks for route and in-page navigation.

### Work

- implement `Tabs`, `Breadcrumbs`, `Pagination`, `Menu`, and `Disclosure`;
- support expected keyboard models;
- distinguish menu actions from disclosures;
- support cursor-based pagination without fabricated page totals;
- identify current page and current tab programmatically;
- verify long labels and narrow widths.

### Acceptance Criteria

- keyboard behavior matches established accessible patterns;
- current route, page, and tab states are programmatically exposed;
- cursor pagination does not claim unknown totals;
- menus are not used as hidden authorization controls;
- responsive behavior preserves reachability.

## S4.7 Implement Data-Display and Formatting Primitives

### Objective

Create trustworthy reusable presentation components for structured and financial data.

### Work

- implement `Card`, `DescriptionList`, `Table`, `DataTable`, `Stat`, `Timestamp`, `Money`, `Percentage`, and `CodeValue`;
- support semantic table headers and captions;
- define overflow and compact behavior;
- require explicit currency and percentage scale;
- expose UTC timestamp context and freshness hooks;
- support tabular numerals;
- provide textual sign and units.

### Acceptance Criteria

- `Money` never uses binary floating-point arithmetic for domain calculations;
- currency and percentage scale are explicit;
- positive and negative values are understandable without color;
- table relationships remain accessible;
- narrow layouts do not hide critical columns without an alternative view;
- values do not imply unsupported precision.

## S4.8 Implement Layout Primitives

### Objective

Standardize spacing and responsive composition without page-specific CSS duplication.

### Work

- implement `Stack`, `Cluster`, `Grid`, `Container`, and `Divider`;
- consume spacing and breakpoint tokens;
- support logical properties and bidirectional-safe layout where practical;
- prevent arbitrary unsafe density overrides;
- test long content, zoom, and reflow.

### Acceptance Criteria

- no foundational layout uses undocumented hardcoded spacing;
- components reflow at 200% and relevant cases at 400% zoom;
- no critical information is clipped;
- layout primitives preserve DOM reading order;
- page components can compose layouts without private token duplication.

## S4.9 Implement Canonical Safety Components

### Objective

Provide non-downgradable components for environment, simulation, freshness, service, and halt state.

### Work

- implement `EnvironmentBadge`;
- implement `SimulationBadge`;
- implement `FreshnessIndicator`;
- implement `ServiceStateBanner`;
- implement `HaltBanner`;
- define canonical labels and icons;
- restrict semantic overrides;
- preserve visibility at mobile widths and zoom.

### Acceptance Criteria

- consumers cannot replace canonical halted, stale, or simulated language with ambiguous text;
- safety components use text, icon, and semantic state;
- halted state is visually stronger than degraded and warning states;
- simulation mode remains visible;
- freshness exposes timestamp or reason context;
- all semantic variants have tests and stories.

## S4.10 Build Storybook Documentation

### Objective

Create an inspectable component catalogue for contributors and reviewers.

### Work

- configure Storybook or an approved equivalent;
- document every public component;
- include supported variants, loading, disabled, invalid, long-content, and narrow-width stories;
- include light and dark themes;
- include keyboard notes and prohibited usage;
- use synthetic, explicitly labeled sample data only.

### Acceptance Criteria

- every public component has at least one story;
- foundational components cover all documented states;
- sample financial values are labeled as sample or simulated;
- no real credential, user data, or unsupported performance claim exists;
- static documentation build succeeds.

## S4.11 Add Accessibility and Interaction Test Suite

### Objective

Make foundational accessibility behavior release-blocking.

### Work

- add automated accessibility checks to stories;
- add keyboard interaction tests;
- test focus-visible behavior;
- test overlay focus restoration;
- test form names, descriptions, and errors;
- test live-region behavior;
- perform documented manual keyboard review;
- document screen-reader spot-check procedure.

### Acceptance Criteria

- no critical automated accessibility violation remains;
- all interactive components are keyboard operable;
- focus does not become lost after route-independent overlay interactions;
- error identification is announced;
- manual review evidence is recorded;
- exceptions require an owner-approved documented rationale.

## S4.12 Add Visual Regression and Contract Verification

### Objective

Detect semantic and visual regressions before product-page integration.

### Work

- capture light and dark baselines;
- capture mobile and desktop baselines;
- capture focus-visible, loading, invalid, stale, degraded, and halted states;
- add canonical-label contract tests;
- add forbidden-copy checks for MVP execution language;
- verify token consumption;
- verify public exports and bundle safety.

### Acceptance Criteria

- deliberate hidden-status, contrast, or canonical-label regressions fail CI;
- baseline updates require review;
- CI artifacts make visual failures inspectable;
- public export inventory is deterministic;
- frontend bundle contains no server secret patterns;
- component package builds reproducibly.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Package boundaries | Export inventory, circular-dependency check, bundle check |
| Accessibility | Automated checks, keyboard tests, manual review record |
| Interaction | Unit and user-interaction tests |
| Visual behavior | Reviewed light, dark, mobile, desktop, focus and safety baselines |
| Safety semantics | Canonical-label and prohibited-override tests |
| Financial display | Decimal-boundary, currency, scale, sign and precision tests |
| Documentation | Static Storybook build and updated component references |

## Sprint Exit Gate

Sprint 4 is complete only when:

- S4.1 through S4.12 are implemented and verified;
- every public component has documentation and tests;
- canonical safety components cannot be semantically downgraded;
- no loading state fabricates evidence;
- no financial formatter performs domain arithmetic;
- keyboard, accessibility, responsive, and visual checks pass;
- static component documentation builds;
- bundle and secret scans pass;
- documentation and changelog are updated;
- the completed sprint is committed and the resulting commit is fetched and verified.

## Next Sprint

Sprint 5 defines and implements the Today’s Roast dashboard and evidence-summary experience using the Sprint 3 shell and Sprint 4 component contracts.
