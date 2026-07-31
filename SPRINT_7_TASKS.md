# Sprint 7 Tasks — Strategy and Risk Decision Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a read-only workspace that explains deterministic strategy intent, risk-policy evaluation, requested and approved exposure, binding constraints, reason codes, decision lineage, and links to simulated execution without introducing execution authority.

## Authoritative References

- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`
- `docs/MARKET_EVIDENCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/TODAYS_ROAST_DASHBOARD_IMPLEMENTATION.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `AGENTS.md`

## S7.1 Define Versioned Decision Schemas

### Objective

Create explicit API contracts for decision identity, strategy intent, risk evaluation, exposure, constraints, reason codes, evidence, lineage, execution links, diagnostics, and export metadata.

### Work

- define `StrategyRiskDecisionReadModel` and nested schemas;
- define allowed, reduced, rejected, halted, and not-applicable outcomes;
- use decimal-safe exposure fields and explicit units;
- include versions, IDs, timestamps, status, and links;
- publish schemas in OpenAPI;
- document compatibility and nullability rules.

### Acceptance Criteria

- intent and risk outcome are separate fields;
- requested and approved exposure are distinct;
- every reason and constraint is machine-readable;
- timestamps are UTC;
- schema compatibility tests pass.

## S7.2 Implement Decision List Endpoint

### Objective

Expose bounded, filterable decision history.

### Work

- implement `GET /api/v1/decisions`;
- support approved filters for date, market, strategy, policy, outcome, reason code, cycle, execution, and reconciliation;
- use cursor pagination;
- enforce authorization and RLS;
- provide safe sort options;
- add latency and result-count telemetry.

### Acceptance Criteria

- filters are deterministic and bounded;
- cursor pagination does not fabricate totals;
- unauthorized data is not exposed;
- history includes immutable decision IDs and versions;
- integration and abuse tests pass.

## S7.3 Implement Decision Detail Endpoint

### Objective

Return the complete persisted strategy and risk decision projection.

### Work

- implement `GET /api/v1/decisions/{decision_id}`;
- join strategy, policy, evidence, exposure, constraints, action, execution, ledger, and reconciliation references;
- classify missing required lineage as integrity failure;
- classify missing optional execution separately;
- map errors safely;
- add correlation IDs.

### Acceptance Criteria

- the same persisted records produce the same response;
- historical decisions remain immutable;
- missing optional execution does not invalidate the decision;
- missing required evidence fails closed;
- integration tests cover every outcome.

## S7.4 Implement Decision Lineage Endpoint

### Objective

Expose ordered lineage from market snapshot through reconciliation.

### Work

- implement `GET /api/v1/decisions/{decision_id}/lineage`;
- return type, ID, timestamp, version, status, reason, and detail link;
- distinguish optional and required steps;
- validate chronological and relational consistency;
- sanitize diagnostics.

### Acceptance Criteria

- lineage ordering is deterministic;
- missing required steps are critical failures;
- optional steps are labeled;
- source links are traceable;
- lineage integrity tests pass.

## S7.5 Add Strategy and Risk Routes

### Objective

Create list, detail, and comparison routes in the application shell.

### Work

- implement `/decisions`;
- implement `/decisions/:decisionId`;
- implement `/decisions/:decisionId/compare`;
- add navigation and cross-links from related workspaces;
- preserve filter and decision state on refresh;
- add route-level error boundaries.

### Acceptance Criteria

- routes are directly addressable and keyboard reachable;
- historical selections remain stable;
- invalid IDs and filters fail safely;
- no mutation or execution controls exist;
- route tests pass.

## S7.6 Implement Decision Identity Header

### Objective

Present cycle, market, strategy, policy, environment, simulation, reconciliation, halt, and supersession context before interpretation.

### Work

- render IDs, versions, timestamps, status, and links;
- render canonical safety components;
- expose local time with accessible UTC;
- show related snapshot and cycle;
- show supersession without rewriting history.

### Acceptance Criteria

- critical state remains visible at all widths;
- identity is traceable;
- stale, halted, unreconciled, and superseded states cannot appear ordinary;
- no execution language is introduced;
- responsive and accessibility tests pass.

## S7.7 Implement Strategy Intent Section

### Objective

Present deterministic strategy output without implying approval.

### Work

- render strategy name, version, intent category, reasons, parameters, timestamp, and evidence references;
- show requested action or exposure when applicable;
- show not-applicable reasons;
- link to market evidence;
- distinguish strategy language from AI commentary.

### Acceptance Criteria

- intent is never labeled approved before risk evaluation;
- reasons and evidence are inspectable;
- parameter and version context is visible;
- absent intent is explicit;
- unit and component tests pass.

## S7.8 Implement Risk Evaluation Section

### Objective

Present the authoritative deterministic risk result and evaluated state.

### Work

- render policy name and version;
- render allowed, reduced, rejected, halted, or not-applicable outcome;
- render reconciled equity, exposure, open orders, drawdowns, limits, freshness, and halt preconditions;
- render reason codes and evaluation timestamp;
- link to policy evidence.

### Acceptance Criteria

- outcome is understandable without color;
- rejected and halted states dominate positive strategy signals;
- frontend performs no risk calculation;
- unavailable required state fails closed;
- tests cover all outcomes.

## S7.9 Implement Requested and Approved Exposure Comparison

### Objective

Show how risk policy changed or blocked requested exposure.

### Work

- render requested and approved order values and portfolio percentages;
- render current and projected exposure;
- render applicable maximums and residual capacity;
- use decimal-safe formatted values and explicit units;
- explain unavailable and not-applicable values.

### Acceptance Criteria

- requested and approved values cannot be confused;
- reduced exposure shows the binding cause;
- rejected exposure shows zero or not-applicable according to contract;
- frontend derives no final values;
- precision and currency tests pass.

## S7.10 Implement Reason Code and Constraint Explorer

### Objective

Make policy explanations traceable and understandable.

### Work

- render canonical reason codes, categories, severity, policy rule, explanation, and evidence;
- distinguish evaluated, binding, rejecting, and halt rules;
- provide definitions and links;
- support filtering without hiding critical constraints;
- sanitize all text.

### Acceptance Criteria

- every binding outcome has at least one supporting reason or explicit integrity failure;
- critical reasons are not collapsed by default;
- code and explanation remain associated programmatically;
- hostile text is sanitized;
- accessibility tests pass.

## S7.11 Implement Evidence Input Panel

### Objective

Expose the persisted inputs used by strategy and risk evaluation.

### Work

- show snapshot, feature values, portfolio state, open orders, drawdown, reconciliation, halt flags, and configuration versions;
- link to immutable resources;
- classify missing evidence;
- preserve source timestamps;
- avoid raw private payload exposure.

### Acceptance Criteria

- each material input has a stable reference;
- missing required evidence is critical;
- private or secret fields are absent;
- stale input is labeled;
- integration tests pass.

## S7.12 Implement Permitted Action and Execution Linkage

### Objective

Keep permission, order creation, fill, ledger, and reconciliation visibly separate.

### Work

- render permitted paper action;
- render order, fill, ledger, and reconciliation links when present;
- explain absent later steps;
- show timestamps and statuses;
- prohibit action controls.

### Acceptance Criteria

- permission is never presented as execution;
- a paper order is never presented as a fill;
- unreconciled execution is critical;
- optional absence is explicit;
- lineage tests pass.

## S7.13 Implement Decision History Table

### Objective

Provide an accessible, filterable overview of historical decisions.

### Work

- render decision time, market, strategy, policy, intent, outcome, exposure summary, reasons, execution, and reconciliation;
- use semantic table structures;
- provide mobile row details;
- use cursor pagination;
- link each row to detail.

### Acceptance Criteria

- outcome and simulation state are textually clear;
- critical fields remain available on narrow screens;
- filters preserve URL state;
- row counts are bounded;
- accessibility tests pass.

## S7.14 Implement Non-Mutating Version Comparison

### Objective

Compare the historical decision with an approved replay or hypothetical configuration.

### Work

- implement compatibility validation;
- use the same immutable evidence where required;
- show strategy, policy, parameter, reason, constraint, exposure, and outcome differences;
- label replay results as hypothetical;
- prohibit execution and automatic promotion;
- preserve original decision identity.

### Acceptance Criteria

- replay never overwrites history;
- incompatible comparisons fail explicitly;
- every changed outcome identifies its cause;
- hypothetical labeling remains visible;
- deterministic comparison tests pass.

## S7.15 Implement Decision Export

### Objective

Generate an authorized provenance-preserving decision package.

### Work

- implement structured JSON and approved human-readable export;
- include IDs, versions, evidence, intent, outcome, exposure, reasons, constraints, lineage, and simulation disclaimer;
- generate exports server-side;
- record safe telemetry;
- enforce authorization.

### Acceptance Criteria

- output is deterministic for the same decision and format;
- provenance cannot be omitted;
- no secret or raw private payload appears;
- simulation state is explicit;
- export tests pass.

## S7.16 Add Explicit State Handling

### Objective

Define rendering for every decision-workspace state.

### Work

- implement loading, empty, not found, unauthorized, stale evidence, missing optional execution, integrity failure, unreconciled execution, superseded, schema mismatch, backend unavailable, halted, incompatible comparison, and export failure states;
- define retry policy;
- prevent infinite retries;
- preserve safe cached data where policy allows.

### Acceptance Criteria

- integrity and reconciliation failures do not appear empty;
- loading fabricates no values;
- retry is offered only when safe;
- cached stale data is labeled;
- state-matrix tests pass.

## S7.17 Add Responsive and Accessibility Verification

### Objective

Ensure decision evidence remains usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, and zoom layouts;
- test heading hierarchy, landmarks, focus, keyboard operation, reason definitions, tables, lineage, and comparison;
- verify reduced motion and contrast;
- test long policy names and codes;
- record screen-reader spot checks.

### Acceptance Criteria

- no critical evidence is hover-only;
- no outcome relies only on color;
- critical content is not clipped;
- no critical automated violation remains;
- manual evidence is recorded.

## S7.18 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make fail-closed decision presentation release-blocking.

### Work

- add contract, integration, route, E2E, accessibility, visual, comparison, and export tests;
- add RLS and authorization tests;
- add secret and unsafe-content scans;
- instrument safe latency, outcome, reason, integrity, comparison, and export metrics;
- test prohibited telemetry fields;
- verify no browser mutation or execution path exists.

### Acceptance Criteria

- all outcome and integrity fixtures pass;
- unauthorized access fails closed;
- no AI or browser path can mutate decisions;
- telemetry contains no prohibited fields;
- visual changes require review;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| API contracts | OpenAPI, enums, decimal, unit, timestamp and compatibility tests |
| Strategy | Intent, version, reason and evidence tests |
| Risk | Outcome, limit, drawdown, halt, reconciliation and constraint tests |
| Exposure | Requested/approved separation and precision tests |
| Lineage | Required/optional step and execution linkage tests |
| Comparison | Immutable-history and hypothetical-label tests |
| Accessibility | Keyboard, tables, definitions, zoom and manual review |
| Security and privacy | RLS, sanitization, no-mutation and telemetry-field tests |

## Sprint Exit Gate

Sprint 7 is complete only when:

- S7.1 through S7.18 are implemented and verified;
- strategy intent, risk decision, permitted action, order, fill, ledger, and reconciliation remain separate;
- every decision is traceable to immutable evidence and versions;
- requested and approved exposure use explicit decimal-safe units;
- reason codes and binding constraints explain outcomes;
- historical decisions remain immutable;
- comparisons are non-mutating and clearly hypothetical;
- accessibility, responsive, security, privacy, contract, integration, E2E, export, comparison, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commit is fetched and verified.

## Next Sprint

Sprint 8 defines and implements the Paper Portfolio, Orders, Fills, Ledger, and Reconciliation Workspace.