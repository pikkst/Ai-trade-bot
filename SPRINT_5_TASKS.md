# Sprint 5 Tasks — Today’s Roast Dashboard

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Define and implement the Today’s Roast dashboard as a read-only, evidence-driven summary of the latest or selected completed research cycle, preserving simulation, freshness, provenance, reconciliation, uncertainty, and halt semantics.

## Authoritative References

- `docs/TODAYS_ROAST_DASHBOARD_IMPLEMENTATION.md`
- `docs/FRONTEND_APPLICATION_SHELL.md`
- `docs/CORE_COMPONENT_LIBRARY_IMPLEMENTATION.md`
- `docs/COMPONENT_LIBRARY.md`
- `docs/DESIGN_SYSTEM.md`
- `docs/UI_UX_GUIDELINES.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/AI_ARCHITECTURE.md`
- `docs/GEMINI_INTEGRATION.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `AGENTS.md`

## S5.1 Define the Dashboard Read Model

### Objective

Create a versioned backend contract that supplies all dashboard data from authoritative persisted sources.

### Work

- define `TodaysRoastReadModel` and nested schemas;
- define latest-cycle and cycle-by-ID endpoints;
- define explicit nullability and unavailable states;
- include source identifiers, versions, timestamps, reason codes, and resource links;
- include simulation, freshness, reconciliation, degraded, superseded, and halt states;
- prevent the frontend from recalculating indicators, risk, P&L, drawdown, confidence, or benchmarks;
- document schema-version compatibility rules.

### Acceptance Criteria

- the read model is versioned and represented in OpenAPI;
- all monetary values include explicit currency and decimal-safe serialization;
- all timestamps are UTC in the API;
- all summary statements can be traced to evidence or provenance metadata;
- unavailable AI output is represented explicitly rather than fabricated;
- contract tests cover valid, partial, stale, degraded, halted, and incompatible payloads.

## S5.2 Implement Latest and Historical Roast Endpoints

### Objective

Expose deterministic read-only endpoints for the latest completed roast and a selected historical cycle.

### Work

- implement `GET /api/v1/roasts/latest`;
- implement `GET /api/v1/roasts/{cycle_id}`;
- resolve the latest eligible completed cycle deterministically;
- prevent running, failed, unreconciled, or superseded cycles from masquerading as ordinary completed cycles;
- enforce authorization and RLS boundaries;
- map not-found, unavailable, integrity, and schema errors to safe API errors;
- add correlation IDs and request metrics.

### Acceptance Criteria

- latest selection is deterministic and tested;
- historical lookup is immutable by cycle ID;
- unauthorized and not-found responses do not leak existence-sensitive details beyond policy;
- integrity failures fail closed;
- no endpoint mutates domain state;
- API latency, status, and error categories are observable without logging private payloads.

## S5.3 Assemble the Server-Side Read Model

### Objective

Build the dashboard projection from persisted market, strategy, risk, AI, paper-execution, ledger, benchmark, and diagnostic records.

### Work

- implement a dedicated query or projection service;
- join records by immutable cycle and lineage identifiers;
- validate version compatibility;
- select reconciled portfolio values only;
- derive display-ready summaries only from authoritative domain outputs;
- classify missing required lineage as integrity failure;
- classify optional AI absence separately from deterministic-data failure;
- attach links to detail resources.

### Acceptance Criteria

- all required sections derive from authoritative records;
- no binary floating-point financial arithmetic is introduced;
- optional AI absence does not suppress deterministic evidence;
- missing required ledger or reconciliation lineage blocks ordinary portfolio display;
- repeated assembly is deterministic for the same source records;
- integration tests verify complete and partial source combinations.

## S5.4 Create the Today’s Roast Route

### Objective

Add the canonical dashboard route to the Sprint 3 application shell.

### Work

- implement `/todays-roast`;
- implement `/todays-roast/:cycleId` or the approved equivalent;
- add the primary navigation item;
- preserve selected historical cycle on refresh;
- add a clear return path to the latest roast;
- consume shell-provided environment, simulation, service, and account context;
- add route-level metadata and safe error boundaries.

### Acceptance Criteria

- both route forms are directly addressable;
- browser refresh preserves the selected cycle;
- route navigation is keyboard accessible;
- historical views are not automatically replaced by new latest-cycle data;
- route errors render sanitized page states;
- no route introduces live-order or configuration controls.

## S5.5 Implement the Canonical Page Header

### Objective

Present cycle identity and safety context before analytical or performance content.

### Work

- render title, symbol, interval, cycle timestamp, cycle ID, and evidence link;
- render `EnvironmentBadge`, `SimulationBadge`, and `FreshnessIndicator`;
- render reconciliation and service state;
- support latest and historical labels;
- expose local display time and accessible UTC value;
- verify long symbols, IDs, and localized text.

### Acceptance Criteria

- simulation and environment state remain visible at all supported widths;
- stale, degraded, halted, or unreconciled state cannot be visually hidden;
- cycle identity is traceable;
- no unsupported urgency or execution language appears;
- header reflows without ambiguous truncation;
- accessibility tests verify heading and status semantics.

## S5.6 Implement Safety and Integrity Banners

### Objective

Ensure material service, data, reconciliation, and halt conditions precede ordinary dashboard content.

### Work

- compose `ServiceStateBanner` and `HaltBanner` with route state;
- add explicit reconciliation-failure presentation;
- add stale-data and partial-cycle presentation;
- add schema-mismatch and lineage-integrity states;
- include impact and safe investigation path where available;
- prevent dismissal of persistent critical states unless policy explicitly permits it.

### Acceptance Criteria

- critical banners render before positive performance content;
- halted state is stronger than degraded state;
- reconciliation and lineage failures cannot render as ordinary empty states;
- critical information is not tooltip-only or drawer-only;
- screen readers receive material state changes appropriately;
- visual tests cover every critical state.

## S5.7 Implement the Executive Evidence Summary

### Objective

Provide a concise, provenance-labeled overview of the selected cycle.

### Work

- render market-state, strategy-intent, risk-outcome, portfolio-impact, AI-advisory, and limitation statements;
- attach provenance labels and evidence links;
- distinguish deterministic, AI, execution, ledger, benchmark, and system sources;
- support unavailable or not-applicable statements;
- constrain summary length without hiding required limitations;
- prevent AI narrative from being merged into deterministic evidence.

### Acceptance Criteria

- every displayed statement has a provenance category;
- every material claim has an evidence or detail link where available;
- AI content is explicitly advisory;
- absent AI output produces a safe explicit state;
- limitations remain visible;
- summary copy contains no financial advice or profit guarantee.

## S5.8 Implement the Market Snapshot Section

### Objective

Present finalized market evidence without frontend domain calculations.

### Work

- display finalized close, interval return, selected indicators, volume context, and prior-cycle comparison;
- display source snapshot and feature-set version;
- display missing, repaired, stale, and incomplete data annotations;
- use server-provided values and formatting metadata;
- provide accessible textual alternatives for compact visualizations;
- link to the future market-evidence workspace.

### Acceptance Criteria

- only finalized source data is presented as final;
- indicator parameters and units are explicit;
- missing values remain missing and explained;
- direction is not encoded by color alone;
- no unsupported precision is displayed;
- unit, contract, accessibility, and visual tests pass.

## S5.9 Implement Strategy and Risk Outcome

### Objective

Keep strategy intent, deterministic risk evaluation, permitted action, and execution result visibly separate.

### Work

- render strategy name and version;
- render intent and deterministic reason codes;
- render risk-policy version, decision, reason codes, and binding constraints;
- render requested and approved exposure when applicable;
- render drawdown and active limits;
- render permitted paper action separately from actual execution;
- link to strategy, policy, order, and execution evidence.

### Acceptance Criteria

- a rejected or reduced intent cannot appear approved;
- risk reason codes remain inspectable;
- halt and reconciliation preconditions remain visible;
- monetary and percentage values use explicit units and scale;
- frontend code performs no sizing or risk arithmetic;
- tests cover allowed, reduced, rejected, halted, and not-applicable outcomes.

## S5.10 Implement Gemini Advisory Presentation

### Objective

Present validated Gemini analysis as optional, bounded, non-authoritative evidence commentary.

### Work

- render provider, model, contract version, timestamp, observations, uncertainty, and evidence references;
- render validation state;
- render budget-blocked, unavailable, invalid, stale, and omitted states;
- sanitize supported rich text or use structured plain rendering;
- display the AI authority boundary;
- prohibit command controls originating from AI content.

### Acceptance Criteria

- AI content is always labeled advisory;
- invalid or unvalidated output is not displayed as accepted analysis;
- unavailable AI does not block deterministic sections;
- raw prompts, tokens, provider payloads, and secrets are never exposed;
- AI content cannot invoke actions or mutate state;
- tests cover all supported AI states and hostile content fixtures.

## S5.11 Implement Portfolio and Benchmark Summary

### Objective

Present reconciled simulated portfolio state and approved benchmarks without gamification or predictive claims.

### Work

- render simulated equity, cash, position value, realized and unrealized P&L, fees, drawdown, and open paper orders;
- render cash and buy-and-hold benchmarks;
- render experiment start value and elapsed day count;
- keep simulation labeling adjacent;
- provide benchmark methodology links;
- quarantine or block unreconciled values.

### Acceptance Criteria

- only reconciled values receive ordinary display treatment;
- simulation remains explicit;
- gains and losses are understandable without color;
- no annualized projection or forward-return claim is generated;
- no confetti, streak, urgency, or celebratory profit UI exists;
- decimal, currency, sign, precision, and benchmark tests pass.

## S5.12 Implement Decision Lineage Timeline

### Objective

Allow users to trace the selected roast from finalized candle through reconciliation and dashboard projection.

### Work

- render ordered lineage steps;
- include type, ID, timestamp, version, status, reason, and detail link;
- distinguish optional AI steps;
- support compact and expanded views;
- preserve DOM reading order;
- mark missing required steps as integrity failures.

### Acceptance Criteria

- the lineage order is deterministic;
- all available identifiers are copyable or navigable safely;
- optional AI absence is distinguishable from required-step absence;
- missing required lineage triggers a critical state;
- timeline is keyboard and screen-reader accessible;
- mobile presentation preserves chronology and status.

## S5.13 Implement Diagnostics and Limitations

### Objective

Expose interpretation-affecting data-quality and service conditions with safe, actionable context.

### Work

- render missing or repaired candle diagnostics;
- render provider throttling, delayed cycles, budget exhaustion, partial assembly, schema mismatch, and superseded state;
- include severity, impact, affected data, timestamp, and next step;
- render methodology and limitations disclosures;
- sanitize all diagnostic text;
- avoid internal infrastructure leakage.

### Acceptance Criteria

- diagnostics are grouped by severity and impact;
- critical diagnostics are not hidden in collapsed sections;
- stack traces, SQL, internal hosts, tokens, and raw provider errors are absent;
- limitations are reachable from the executive summary;
- empty diagnostics and unavailable diagnostics remain distinct;
- tests cover long and multiple simultaneous diagnostics.

## S5.14 Implement Explicit Page-State Handling

### Objective

Create deterministic full-page and section-level behavior for every supported dashboard state.

### Work

- implement initial loading;
- implement no completed cycle;
- implement running cycle with and without a prior completed cycle;
- implement completed, historical, degraded, stale, and AI-unavailable states;
- implement unauthorized, not-found, backend-unavailable, schema-mismatch, reconciliation-failure, integrity-failure, and halted states;
- define retry eligibility;
- prevent infinite retries for non-retryable failures.

### Acceptance Criteria

- no loading state fabricates prices, P&L, confidence, or timestamps;
- integrity and authorization failures do not appear as emptiness;
- retry controls appear only when retry is safe;
- cached stale data is labeled;
- all state transitions preserve focus appropriately;
- route tests cover the complete state matrix.

## S5.15 Add Responsive and Accessibility Verification

### Objective

Ensure the dashboard remains understandable and operable across supported devices, zoom levels, keyboard use, and assistive technology.

### Work

- verify desktop, tablet, and mobile layouts;
- verify 200% and relevant 400% zoom reflow;
- verify logical headings and landmarks;
- verify keyboard navigation and focus preservation;
- verify live-region policy;
- provide chart and timeline alternatives;
- verify long localized content and reduced motion.

### Acceptance Criteria

- no critical content is clipped or hover-only;
- tables have accessible narrow-layout alternatives;
- cycle changes preserve or intentionally move focus;
- status changes are announced according to severity;
- no critical automated accessibility violation remains;
- manual keyboard and screen-reader spot-check evidence is recorded.

## S5.16 Add Analytics and Observability

### Objective

Measure dashboard reliability and navigation without collecting sensitive financial, authentication, or AI payload data.

### Work

- add approved route and interaction events;
- add read-model latency, error, stale-response, schema-mismatch, and evidence-link metrics;
- propagate approved correlation identifiers;
- add client build version to diagnostics;
- redact or exclude private payloads;
- document retention and access expectations.

### Acceptance Criteria

- analytics contain no credentials, raw prompts, order payloads, ledger payloads, or private identifiers;
- metrics expose safe categories rather than raw exceptions;
- dashboard failures can be correlated with backend requests where approved;
- telemetry has tests for prohibited fields;
- observability failure does not break the dashboard;
- privacy documentation is updated.

## S5.17 Add Contract, Integration, and End-to-End Tests

### Objective

Make dashboard correctness, provenance, and fail-closed behavior release-blocking.

### Work

- add read-model schema tests;
- add API integration tests;
- add route and component tests;
- add evidence-link and lineage tests;
- add hostile AI and diagnostic-content tests;
- add latest and historical-cycle end-to-end tests;
- add stale cache, provider failure, schema mismatch, reconciliation failure, and halt tests.

### Acceptance Criteria

- the same source records produce the same dashboard projection;
- latest and historical routes behave deterministically;
- unsafe payloads are sanitized;
- required lineage loss fails closed;
- AI failure does not suppress deterministic evidence;
- all critical failure-state tests pass in CI.

## S5.18 Add Visual Regression Coverage

### Objective

Detect hierarchy, labeling, state, and responsive regressions before release.

### Work

- capture light and dark themes;
- capture desktop and mobile layouts;
- capture completed, historical, degraded, stale, halted, and reconciliation-failure states;
- capture AI available and unavailable states;
- capture positive, neutral, and negative simulated outcomes;
- capture long reason codes and localization stress cases;
- require review for baseline changes.

### Acceptance Criteria

- hidden simulation, freshness, reconciliation, or halt regressions fail CI;
- critical banners remain visually prior to performance content;
- AI and deterministic content remain distinguishable;
- baseline artifacts are inspectable;
- deliberate changes require reviewed baseline updates;
- visual tests are stable and reproducible.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Read model | OpenAPI schema, contract tests, version-compatibility tests |
| Backend assembly | Deterministic projection and integration tests |
| Route behavior | Latest and historical route tests |
| Safety semantics | Simulation, freshness, reconciliation, degraded, integrity, and halt tests |
| Provenance | Evidence-link and lineage verification |
| AI boundary | Advisory labeling, validation, omission, sanitization, and no-command tests |
| Financial display | Decimal, currency, sign, precision, reconciliation, and benchmark tests |
| Accessibility | Automated checks, keyboard review, screen-reader spot check, zoom and reflow evidence |
| Responsive UI | Mobile, tablet, desktop, long-content, and table-alternative baselines |
| Security and privacy | Authorization, RLS, sanitization, secret scan, and telemetry-field tests |
| Observability | Safe metrics, correlation, and redaction verification |
| Documentation | Updated API, UI, testing, security, and changelog references |

## Sprint Exit Gate

Sprint 5 is complete only when:

- S5.1 through S5.18 are implemented and verified;
- latest and historical Today’s Roast routes work from the application shell;
- all dashboard values originate from the versioned server read model;
- deterministic evidence, risk decisions, AI advisory, paper execution, ledger outcomes, and benchmarks remain distinguishable;
- simulation, freshness, reconciliation, degraded, integrity, and halt state cannot be hidden;
- AI failure degrades safely without fabricated replacement content;
- required lineage loss fails closed;
- no frontend domain calculation or live-trading control is introduced;
- contract, integration, end-to-end, accessibility, security, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint is committed and the resulting commit is fetched and verified.

## Next Sprint

Sprint 6 defines and implements the market evidence and charting workspace, including finalized-candle visualization, indicator overlays, accessible data alternatives, snapshot comparison, data-quality annotations, and evidence export.