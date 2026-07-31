# Core Component Library Implementation Specification

Last reviewed: 2026-07-31  
Status: Sprint 4 authoritative component-library implementation specification

## 1. Purpose

This document translates the approved design-system and component-library foundations into an implementable, testable frontend component architecture for The Daily Roast AI.

The component library must make safe behavior the default. It must reduce visual and interaction inconsistency, preserve accessibility, and prevent product pages from hiding simulation state, risk, uncertainty, freshness, reconciliation, or halt conditions.

The library is a frontend presentation layer. It does not provide authorization, financial calculations, risk decisions, order execution, reconciliation, or AI validation.

## 2. Scope

Sprint 4 covers:

- component package structure;
- component API conventions;
- accessible interaction behavior;
- form and validation primitives;
- navigation and disclosure primitives;
- feedback and state primitives;
- overlay primitives;
- data-display primitives;
- financial-value formatting boundaries;
- Storybook or equivalent documentation;
- automated accessibility, interaction, and visual-regression testing;
- prohibited component usage in safety-critical contexts.

Sprint 4 does not implement complete product pages, market charts, backend integration, authentication flows, or domain calculations.

## 3. Implementation Principles

1. Prefer semantic HTML before custom ARIA.
2. Make the safe state the easiest state to render.
3. Color must never be the only status signal.
4. Loading states must not fabricate financial or market values.
5. Disabled controls must explain why the action is unavailable when material.
6. Destructive or experiment-control actions require explicit confirmation and clear scope.
7. AI-generated content must remain visually distinguishable from deterministic evidence.
8. Simulated financial state must remain labeled.
9. Components must consume versioned design tokens rather than undocumented visual values.
10. Component APIs must be typed, narrow, composable, and resistant to unsafe overrides.
11. Responsive behavior must preserve critical information rather than merely reduce density.
12. Accessibility failures are release-blocking for foundational components.

## 4. Recommended Package Structure

```text
frontend/src/components/
  primitives/
    Button/
    Link/
    IconButton/
    Input/
    Textarea/
    Select/
    Checkbox/
    RadioGroup/
    Switch/
    Field/
    FormMessage/
  feedback/
    Alert/
    Badge/
    StatusLabel/
    Progress/
    Spinner/
    Skeleton/
    EmptyState/
    ErrorState/
    InlineMessage/
  navigation/
    Tabs/
    Breadcrumbs/
    Pagination/
    Menu/
    Disclosure/
  overlays/
    Dialog/
    AlertDialog/
    Drawer/
    Popover/
    Tooltip/
  data-display/
    Card/
    DescriptionList/
    Table/
    DataTable/
    Stat/
    Timestamp/
    Money/
    Percentage/
    CodeValue/
  layout/
    Stack/
    Cluster/
    Grid/
    Container/
    Divider/
  safety/
    EnvironmentBadge/
    SimulationBadge/
    FreshnessIndicator/
    ServiceStateBanner/
    HaltBanner/
  internal/
    VisuallyHidden/
    Portal/
    FocusScope/
    Slot/
```

Each public component directory should contain implementation, types, tests, stories, and an index export. Internal utilities must not be part of the public package contract.

## 5. Public API Conventions

Every component must:

- use explicit TypeScript props;
- forward refs only when consumers need DOM access;
- support `className` only through documented extension rules;
- avoid arbitrary style props for safety-critical semantics;
- expose stable testable states through accessible names and semantic attributes;
- use controlled and uncontrolled modes only where both are necessary;
- document default behavior;
- document invalid prop combinations;
- avoid boolean-prop ambiguity where a typed variant is clearer;
- preserve native attributes unless they would create an unsafe contract.

Safety components must not permit callers to replace canonical status text with misleading language.

## 6. Button and Action Contract

Required variants:

- primary;
- secondary;
- quiet;
- danger;
- link-style;
- icon-only.

Required states:

- default;
- hover;
- focus-visible;
- active;
- disabled;
- loading.

Rules:

- use a native `button` for actions and an anchor for navigation;
- icon-only actions require an accessible name;
- loading state preserves the action label for assistive technology;
- destructive actions use danger styling and confirmation where consequences are material;
- disabled actions must not rely only on reduced opacity;
- a button must not be labeled `Buy`, `Sell`, or `Trade Now` in the active MVP experience;
- repeated submission must be prevented for non-idempotent commands.

## 7. Form Contract

The foundational form system includes:

- `Field`;
- `Label`;
- `Description`;
- `Input`;
- `Textarea`;
- `Select`;
- `Checkbox`;
- `RadioGroup`;
- `Switch`;
- `FormMessage`.

Requirements:

- labels are programmatically associated;
- help and error text use stable IDs;
- validation errors are announced after submission or blur according to form policy;
- required state is expressed in text and semantics;
- placeholder text is not a replacement for a label;
- numeric financial input uses explicit units and server-side validation;
- secret values are never prefilled from server responses;
- risk, budget, and experiment controls show consequences and current effective values;
- switches are reserved for immediate binary settings and not used for irreversible commands.

## 8. Feedback and Status Contract

### 8.1 Alert

Supported intent:

- information;
- success;
- warning;
- critical.

Critical alerts must include a concise title, plain-language impact, and recovery or investigation path when available.

### 8.2 Badge and Status Label

Badges may represent compact metadata. Safety-critical state requires text and icon where space permits. Profit, confidence, and status must not be conflated.

### 8.3 Loading and Skeleton

Skeletons may indicate structure but must never show plausible fabricated prices, percentages, balances, timestamps, or confidence values.

### 8.4 Empty State

An empty state explains what is absent, why it may be absent, and the safe next action. Integrity failure, authorization failure, and stale-data failure must not be rendered as ordinary emptiness.

### 8.5 Error State

Error state must distinguish recoverable request failure from integrity failure, halt state, and authorization failure. Stack traces, provider payloads, tokens, SQL, and secrets must not appear.

## 9. Overlay Contract

### Dialog

Use for bounded tasks requiring focused interaction.

### Alert Dialog

Use for destructive, irreversible, or experiment-control confirmation.

### Drawer

Use for supplementary evidence, filters, and mobile navigation. Critical information must not exist only inside a closed drawer.

### Popover

Use for lightweight contextual controls. It must not contain essential warnings that disappear when focus moves.

### Tooltip

Use only as supplementary explanation. A tooltip cannot be the sole location for an accessible name, risk warning, or required instruction.

All overlays require focus management, Escape behavior where appropriate, return focus, portal layering, scroll handling, and keyboard tests.

## 10. Navigation Contract

### Tabs

Tabs switch between related views of the same resource. They require keyboard arrow navigation and must not be used as hidden authorization boundaries.

### Breadcrumbs

Breadcrumbs describe hierarchy and must use an ordered list with a current-page marker.

### Pagination

Pagination must expose current page, total context where known, and accessible previous/next labels. Cursor-based APIs must not fabricate page counts.

### Menu and Disclosure

Menus are for actions; disclosures are for showing and hiding content. Do not substitute one interaction model for the other.

## 11. Data Display Contract

### Table

Use semantic tables for relational data. Required behavior includes header associations, accessible captions where useful, horizontal overflow handling, and readable empty/error states.

### DataTable

Sorting, filtering, pagination, row selection, and column visibility must be opt-in capabilities. Server-side and client-side behavior must be explicit.

### Money

`Money` accepts a decimal-compatible serialized value and an explicit currency. It must not perform floating-point financial arithmetic. Formatting is presentation-only.

### Percentage

The source scale must be explicit: fractional or percentage. Positive and negative values require text or sign, not color alone.

### Timestamp

Display an understandable local representation while preserving access to the UTC value and freshness meaning.

### Stat

A stat must include label, value, unit, optional comparison, and data state. It must not imply precision beyond source data.

## 12. Safety Component Constraints

The following canonical components are mandatory where applicable:

- `EnvironmentBadge`;
- `SimulationBadge`;
- `FreshnessIndicator`;
- `ServiceStateBanner`;
- `HaltBanner`.

Their semantic variants and canonical labels are project-owned. Consumers may add context but may not downgrade, hide, recolor into neutrality, or replace halted/stale/simulated language with ambiguous wording.

Critical safety components must remain visible at mobile widths and under zoom.

## 13. Accessibility Requirements

The component library targets WCAG 2.2 AA where practical.

Required verification:

- keyboard operation;
- visible focus;
- screen-reader naming and description;
- semantic roles and states;
- no keyboard traps;
- focus restoration for overlays;
- minimum target size where practical;
- zoom and reflow at 200% and 400% for relevant components;
- light and dark contrast;
- reduced-motion behavior;
- error identification and instruction;
- status announcement behavior.

Automated checks supplement but do not replace manual keyboard and screen-reader review.

## 14. Story Documentation Requirements

Every public component must have stories for:

- default state;
- supported variants;
- disabled and loading state where applicable;
- error or invalid state where applicable;
- long content;
- narrow viewport;
- light and dark themes;
- keyboard interaction notes;
- safety-critical usage where relevant.

Stories must not contain real credentials, private data, fabricated performance claims, or unlabeled sample financial results.

## 15. Testing Strategy

### Unit and Interaction Tests

Verify rendering, accessible names, state transitions, keyboard behavior, controlled behavior, disabled behavior, and event contracts.

### Accessibility Tests

Run automated accessibility checks for every foundational story and targeted route integration.

### Visual Regression

Capture approved baselines for light, dark, mobile, focus-visible, loading, error, stale, degraded, and halted states where applicable.

### Contract Tests

Verify canonical safety labels, unsupported prop combinations, design-token consumption, and absence of forbidden action copy.

### Bundle and Export Tests

Verify tree-shakeable exports where practical, no accidental server dependency, no secret-bearing configuration, and no duplicate public exports.

## 16. Versioning and Change Control

Component APIs are internal project contracts but must still evolve deliberately.

A breaking component change requires:

- impact inventory;
- migration notes;
- updated stories and tests;
- updated design documentation;
- review of safety-critical consumers;
- visual-baseline review.

Canonical safety semantics require explicit owner approval before change.

## 17. Acceptance Criteria

Sprint 4 documentation is accepted when:

1. package boundaries and public API conventions are explicit;
2. required primitive, feedback, overlay, navigation, data-display, layout, and safety components are defined;
3. financial formatting boundaries prohibit floating-point domain calculations;
4. loading and empty states prohibit fabricated evidence;
5. overlay and navigation keyboard behavior is specified;
6. safety components cannot be semantically downgraded by consumers;
7. Storybook, accessibility, interaction, visual, contract, and export testing are defined;
8. implementation task cards contain measurable acceptance criteria;
9. no requirement introduces live execution or weakens deterministic controls.

## 18. Definition of Done

The specification is complete when:

- it is committed with `SPRINT_4_TASKS.md`;
- terminology matches brand, UX, security, risk, and architecture documents;
- all referenced component families have explicit contracts;
- prohibited unsafe usage is documented;
- the resulting commit is fetched and verified.

## 19. Next Sprint Boundary

Sprint 5 should define the **Today’s Roast dashboard and evidence-summary experience**, including read models, visual hierarchy, data states, decision lineage, responsive behavior, and implementation tasks. It must build on the Sprint 3 shell and Sprint 4 component contracts without implementing domain calculations in the frontend.
