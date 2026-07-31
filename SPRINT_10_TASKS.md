# Sprint 10 Tasks — Experiment Operations, Scheduled Cycle, Incident, and Audit Timeline Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement an evidence-first experiment operations workspace that presents frozen configuration, preflight gates, lifecycle transitions, scheduled cloud-cycle timing and completeness, lock and idempotency evidence, dependency health, incidents, halts, recovery, export and restore status, audit history, and 30-day report readiness while restricting state-changing commands to owner-authorized, idempotent, server-validated paper-experiment workflows.

## Authoritative References

- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `CLOUD_MVP_TASKS.md`
- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/OBSERVABILITY.md`
- `docs/DEPLOYMENT.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `docs/MARKET_EVIDENCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`
- `docs/BACKTEST_EXPERIMENT_COMPARISON_WORKSPACE_IMPLEMENTATION.md`
- `AGENTS.md`

## S10.1 Define Versioned Experiment Operations Schemas

### Objective

Create explicit contracts for experiment identity, lifecycle, frozen configuration, preflight, schedule, cycles, locks, idempotency, dependencies, domain safety, portfolio summary, incidents, halts, recovery, exports, report status, audit timeline, diagnostics, limitations, permissions, and links.

### Work

- define `ExperimentOperationsReadModel` and nested schemas;
- define research-cycle, preflight, incident, recovery, export, and audit read models;
- define lifecycle, cycle, validity, command, and audit-integrity enums;
- use decimal strings and explicit units for financial values;
- define stale, unavailable, incomplete, warning, blocker, conflict, and expiry states;
- publish schemas in OpenAPI.

### Acceptance Criteria

- every state and command result is machine-readable;
- no authoritative financial or timing duration value uses unsafe numeric representation;
- command permissions are server-provided;
- compatibility and nullability are explicit;
- contract tests pass.

## S10.2 Implement Experiment List Endpoint

### Objective

Expose bounded, filterable experiment history.

### Work

- implement `GET /api/v1/experiments` or the approved workspace-scoped equivalent;
- support filters for lifecycle, validity, date range, configuration, portfolio, halt, incident, reconciliation, cycle health, report, and archive state;
- use cursor pagination and safe sort options;
- include latest attempt, latest success, active blocker, and report summaries;
- enforce authorization and RLS;
- add safe telemetry.

### Acceptance Criteria

- draft, running, paused, halted, completed, failed, and archived experiments remain discoverable;
- filters are bounded and server-approved;
- unauthorized experiments are not exposed;
- pagination does not fabricate totals;
- API tests pass.

## S10.3 Implement Experiment Detail Endpoint

### Objective

Return the complete experiment operations projection.

### Work

- implement `GET /api/v1/experiments/{experiment_id}`;
- return identity, lifecycle, configuration, preflight, schedule, latest cycles, cycle health, dependencies, domain safety, portfolio, benchmarks, incidents, halts, recovery, exports, report, diagnostics, limitations, permissions, and links;
- classify missing required evidence and configuration drift;
- map safe errors and correlation IDs;
- enforce authorization and RLS.

### Acceptance Criteria

- identical persisted evidence produces the same response;
- lifecycle and validity remain distinct;
- blockers and critical incidents cannot be hidden;
- missing provenance fails closed;
- integration tests pass.

## S10.4 Implement Experiment Operations Routes

### Objective

Add experiment, configuration, preflight, cycle, incident, audit, recovery, export, and report routes.

### Work

- implement the approved canonical route family;
- add application-shell navigation and cross-links;
- preserve approved filters in URL state;
- add route-level error boundaries;
- visually separate lifecycle commands from evidence views;
- ensure command routes are unavailable to unauthorized users.

### Acceptance Criteria

- routes are directly addressable and keyboard reachable;
- refresh preserves stable read state;
- invalid IDs and filters fail safely;
- command availability matches server permissions;
- route tests pass.

## S10.5 Implement Experiment Identity and Safety Header

### Objective

Present environment, simulation, lifecycle, validity, halt, reconciliation, freshness, period, and approval state before other content.

### Work

- render experiment, workspace, configuration, portfolio, owner, approval, planned period, actual period, cadence, report, halt, and incident references;
- render simulation, lifecycle, validity, reconciliation, freshness, and integrity components;
- expose local timestamps with accessible UTC;
- preserve critical state at narrow widths;
- prevent live-trading language.

### Acceptance Criteria

- simulation is always explicit;
- active halt, invalidity, mismatch, or stale state cannot appear normal;
- configuration hash and period are inspectable;
- performance never dominates safety state;
- responsive and accessibility tests pass.

## S10.6 Implement Frozen Configuration View

### Objective

Expose every immutable value governing the experiment.

### Work

- render exchange, symbol, interval, cadence, freshness, feature, Gemini, strategy, risk, execution, accounting, portfolio, benchmark, export, retention, report, environment, code, dependency, and migration references;
- render risk limits and virtual capital;
- display configuration ID, version, and hash;
- link to immutable evidence;
- detect and classify drift.

### Acceptance Criteria

- actual frozen values are displayed rather than assumed defaults;
- running configuration cannot appear editable;
- drift is critical;
- secrets and internal connection values are absent;
- configuration tests pass.

## S10.7 Implement Baseline EUR 20 Profile Verification

### Objective

Verify and present the approved first-experiment profile without hard-coding it as universal behavior.

### Work

- validate virtual EUR 20 capital, BTC/EUR, one-hour finalized candles, approximate hourly cadence, 25% maximum position, EUR 5 maximum order, 5% daily drawdown halt, 15% total drawdown halt, one open order, no leverage, no shorting, Gemini EUR 0 default budget, and required benchmarks;
- render differences from baseline;
- link to configuration and owner approval;
- block start on unapproved differences.

### Acceptance Criteria

- baseline checks are evidence-backed;
- actual values remain authoritative;
- unapproved drift blocks Ready or Running state;
- live trading and private Binance access remain disabled;
- profile tests pass.

## S10.8 Implement Preflight Execution and Result Endpoint

### Objective

Run and expose release-blocking experiment readiness checks.

### Work

- implement `POST /api/v1/experiments/{experiment_id}/preflight` and the approved read endpoint;
- require owner or approved operator role, idempotency, expected version, and correlation ID;
- validate configuration, environment, database, migrations, Auth, RLS, service-role isolation, portfolio funding, market data, Gemini, strategy, risk, execution, accounting, idempotency, locks, ledger, reconciliation, halts, workflow, API, frontend, export, restore, observability, runbooks, secret scan, and approval;
- persist immutable check results;
- define expiry.

### Acceptance Criteria

- failed or blocked checks prevent Ready and Start;
- preflight result is tied to exact configuration hash;
- repeated identical commands do not duplicate evidence improperly;
- secret values are absent;
- integration tests pass.

## S10.9 Implement Preflight Workspace

### Objective

Present every check, blocker, warning, evidence link, approval, and expiry.

### Work

- render preflight identity, configuration hash, outcome, checks, blockers, warnings, evidence, approver, timestamps, and expiry;
- group checks by domain;
- keep critical blockers expanded;
- explain remediation through runbook links without browser repair controls;
- support accessible status announcements.

### Acceptance Criteria

- passed, failed, blocked, and expired remain distinct;
- every blocker links to evidence;
- critical checks are not hidden;
- expiry is visible;
- accessibility tests pass.

## S10.10 Implement Immutable Lifecycle Transition Model

### Objective

Persist and expose every experiment state change.

### Work

- define draft, preflight pending, preflight failed, ready, running, paused, halted, completing, completed, failed, and archived states;
- persist transition ID, from, to, actor, source, reason, timestamp, correlation, request, incident, halt, preflight, and report references;
- enforce valid transitions and optimistic concurrency;
- prevent mutation or deletion;
- expose transition history.

### Acceptance Criteria

- invalid transitions fail deterministically;
- history is append-only;
- actor and reason are always present;
- repeated commands do not create duplicate transitions;
- state-machine tests pass.

## S10.11 Implement Start Command and Gate

### Objective

Start a paper experiment only after all safety and evidence gates pass.

### Work

- implement `POST /api/v1/experiments/{experiment_id}/start`;
- require owner role, idempotency key, expected version, explicit reason, and confirmation context;
- verify Ready state, unexpired preflight, exact configuration hash, owner approval, no active halt, reconciled initial portfolio, valid period, schedule, baseline export, no critical incident, live trading disabled, and private exchange credentials absent;
- persist transition and audit event;
- return first expected cycle.

### Acceptance Criteria

- any missing gate blocks start;
- duplicate requests return the existing transition;
- browser cannot update state directly;
- start evidence is complete and immutable;
- authorization and integration tests pass.

## S10.12 Implement Pause, Approved Resume, and Halt Commands

### Objective

Provide controlled paper-experiment lifecycle commands without generic safety bypass.

### Work

- implement owner-only pause and halt;
- implement resume only if separately approved;
- require idempotency, expected version, reason, confirmation, and audit evidence;
- prevent resume while risk, reconciliation, integrity, or critical incident halt remains;
- preserve open-order and accounting policy semantics;
- return safe conflicts and resulting state.

### Acceptance Criteria

- pause, resume, and halt have distinct semantics;
- halt blocks new entries immediately;
- no generic clear-halt action exists;
- repeated commands are idempotent;
- command-security tests pass.

## S10.13 Implement Command Confirmation UX

### Objective

Prevent accidental paper-experiment state changes.

### Work

- show command, experiment identity, current state, resulting state, consequence, unresolved blockers, reason code, and cancellation option;
- require explicit confirmation;
- preserve keyboard and screen-reader operation;
- handle `409` conflicts and stale expected versions safely;
- prevent double submission;
- display audit reference after success.

### Acceptance Criteria

- confirmation clearly states consequences;
- focus is managed correctly;
- stale state cannot silently execute;
- duplicate submissions do not duplicate transitions;
- accessibility and E2E tests pass.

## S10.14 Implement Research Cycle List Endpoint

### Objective

Expose bounded scheduled-cycle history.

### Work

- implement a portfolio- or experiment-scoped cycle list endpoint;
- support filters for intended and actual time, status, delay, lock, duplicate, freshness, Gemini, strategy, risk, order, fill, reconciliation, incident, workflow, error, and validity;
- use cursor pagination;
- include completeness and lineage summaries;
- enforce authorization and safe telemetry.

### Acceptance Criteria

- expected, delayed, started, completed, warned, skipped, failed, timed-out, duplicate, recovered, and invalidated cycles remain discoverable;
- schedule and actual times remain separate;
- filters are bounded;
- unauthorized cycles are not exposed;
- endpoint tests pass.

## S10.15 Implement Research Cycle Detail Endpoint

### Objective

Return the complete persisted cycle, schedule, lock, idempotency, domain, accounting, workflow, audit, and validity evidence.

### Work

- implement cycle detail projection;
- return identity, schedule, lock, idempotency, status, market, Gemini, strategy, risk, execution, accounting, reconciliation, audit, workflow, diagnostics, validity, and links;
- classify missing required stages;
- preserve optional stage absence reasons;
- map safe errors.

### Acceptance Criteria

- successful process exit is not sufficient for complete status;
- required missing stages fail closed;
- optional stages are explicit;
- duplicate attempts link to canonical cycle;
- integration tests pass.

## S10.16 Implement Schedule, Delay, and Missed-Cycle View

### Objective

Explain best-effort GitHub scheduling without false exact-time promises.

### Work

- render cadence, intended occurrence, tolerance window, actual start, delay, delay class, next expected estimate, last success, last attempt, and consecutive failures;
- implement server-defined delayed and missed classifications;
- label next occurrence as estimate;
- expose schedule source and freshness;
- link to workflow evidence.

### Acceptance Criteria

- intended and actual times cannot be confused;
- exact-time guarantees are not implied;
- delayed and missed states use persisted policy;
- stale estimates are labeled;
- scheduling tests pass.

## S10.17 Implement Lock and Concurrency Evidence

### Objective

Prove overlapping cycles cannot create duplicate side effects.

### Work

- render lock or lease type, key, attempt, outcome, safe owner reference, expiry, release, overlap reference, and duplicate check;
- handle lock-rejected cycles as safe skipped or terminal states;
- link to competing cycle where authorized;
- expose concurrency diagnostics without secrets;
- test advisory lock or lease behavior.

### Acceptance Criteria

- only one eligible cycle owns the critical section;
- lock rejection creates no duplicate financial side effect;
- missing lock evidence is critical;
- release failures are visible;
- concurrency tests pass.

## S10.18 Implement Cycle Idempotency Evidence

### Objective

Make retry and duplicate handling traceable.

### Work

- render occurrence key, command key, canonical cycle, side-effect identities, duplicate attempts, and deduplication outcome;
- validate unique constraints for snapshots, analyses, decisions, orders, fills, ledger, and audit effects;
- return existing resources on retry;
- classify duplicate suspicion;
- add safe telemetry.

### Acceptance Criteria

- retries cannot duplicate financial effects;
- canonical and duplicate attempts remain linked;
- deduplication outcome is machine-readable;
- suspicious divergence triggers incident or halt policy;
- idempotency tests pass.

## S10.19 Implement Cycle Lineage Timeline

### Objective

Present the complete research-cycle evidence chain.

### Work

- render occurrence, command, lock, market ingestion, snapshot, features, Gemini, strategy, risk, action, order, fill, ledger, state version, reconciliation, and audit closure;
- render sequence, timestamps, versions, statuses, reasons, and links;
- distinguish required and optional stages;
- classify missing or inconsistent lineage;
- sanitize diagnostics.

### Acceptance Criteria

- lineage is chronological and deterministic;
- required missing evidence is critical;
- positive AI or strategy evidence cannot bypass risk;
- financial completion requires ledger and reconciliation;
- lineage tests pass.

## S10.20 Implement Market Freshness and Data-Quality Cycle Panel

### Objective

Expose the market evidence used by each scheduled cycle.

### Work

- render latest finalized candle, snapshot, interval, data-quality result, gap detection, gap repair, source references, freshness threshold, outcome, and stale rejection;
- link to Market Evidence workspace;
- distinguish no-new-data and failure states;
- preserve source timestamps;
- avoid browser freshness authority.

### Acceptance Criteria

- stale or incomplete data blocks entries according to persisted policy;
- freshness is server-calculated;
- data gaps remain visible;
- source evidence is traceable;
- integration tests pass.

## S10.21 Implement Gemini Budget and Cycle Outcome Panel

### Objective

Expose provider status, validation, allowance, cost, and fallback without secrets.

### Work

- render mode, provider, configured model, prompt, schema, validation, request, retry, latency, usage, estimate, budget period, allowance, reservation, commitment, quota, rate limit, safety, refusal, provider, schema, fallback, and report references;
- render deterministic HOLD or fallback behavior;
- link to Gemini workspace;
- enforce privacy and redaction.

### Acceptance Criteria

- budget and provider failures cannot silently appear successful;
- Gemini output does not override deterministic risk;
- secrets and raw prompts are absent;
- fallback is explicit;
- contract and privacy tests pass.

## S10.22 Implement Strategy, Risk, Execution, and Accounting Cycle Summary

### Objective

Show domain outcomes and financial evidence for every cycle.

### Work

- render strategy intent, risk outcome, constraints, requested and approved exposure, permitted action, order, fill, fees, spread, slippage, precision, ledger sequence, state version, and reconciliation;
- render absence reasons;
- link to detailed workspaces;
- classify missing required accounting evidence;
- preserve simulation labels.

### Acceptance Criteria

- intent, approval, order, fill, ledger, and reconciliation remain separate;
- no-action cycles remain explainable;
- missing ledger or reconciliation evidence is critical;
- frontend performs no calculations;
- integration tests pass.

## S10.23 Implement Dependency and Service Status View

### Objective

Present approved operational status without treating provider dashboards as the sole audit source.

### Work

- render GitHub Actions, Supabase database, Auth, migration, Render API, Cloudflare frontend, Binance public REST, Gemini, and export-procedure status;
- include observed timestamp, source, freshness, outcome, limitation, and evidence link;
- distinguish API cold start from cycle failure;
- classify stale status;
- sanitize diagnostics.

### Acceptance Criteria

- every status includes observation time and limitation;
- sleeping Render does not invalidate independent GitHub cycles;
- provider status is not the sole audit record;
- secrets are absent;
- component tests pass.

## S10.24 Implement Incident Model and Workspace

### Objective

Persist and expose operational, integrity, security, and domain incidents.

### Work

- define incident identity, severity, category, status, title, detection, acknowledgement, actors, affected cycles and entities, reasons, halt, containment, recovery, evidence, resolution, and review;
- implement list and detail endpoints;
- support bounded filters;
- link to cycle, halt, runbook, audit, and report;
- prevent deletion or history rewrite.

### Acceptance Criteria

- unresolved incidents remain visible;
- severity and status are server-defined;
- incidents cannot be removed to improve report appearance;
- all critical incidents link to evidence;
- integration tests pass.

## S10.25 Implement Halt Review View

### Objective

Explain halt scope, source, evidence, blockers, and review without a generic bypass.

### Work

- render halt ID, scope, source, reason, severity, activation, affected resources, incident, evidence, review, reviewer, superseding transition, and blockers;
- distinguish reviewed from cleared;
- link to approved recovery workflow;
- prevent generic resume or clear actions;
- expose accessibility definitions.

### Acceptance Criteria

- reviewed state never implies safe resume automatically;
- unresolved blockers remain visible;
- internal safety halts are traceable;
- generic bypass is absent;
- halt tests pass.

## S10.26 Implement Runbook and Recovery Workspace

### Objective

Record and validate evidence-based recovery without mutating history.

### Work

- implement runbook registry and version references;
- cover scheduled workflow, Supabase, Render, Binance, Gemini, risk, reconciliation, duplicate suspicion, export/restore, and experiment halt scenarios;
- render trigger, actor, timing, actions, validations, resources, result, unresolved items, audit, and incident links;
- prevent secret display and arbitrary browser commands;
- preserve failed recovery attempts.

### Acceptance Criteria

- every recovery links to a versioned runbook;
- validation checks are explicit;
- failed attempts remain visible;
- immutable evidence is not rewritten;
- recovery tests pass.

## S10.27 Implement Export and Restore Evidence Workspace

### Objective

Track baseline export, cadence, artifact integrity, and isolated restore drills.

### Work

- render baseline export, cadence, last success, next expected, overdue state, schema, source, artifact hash, location reference, restore target, timing, outcome, migration, integrity, operator, and audit;
- implement authorized export and restore-read endpoints;
- classify missed cadence and failed restore;
- link to runbooks and incidents;
- avoid secret artifact URLs.

### Acceptance Criteria

- pre-start baseline export is verifiable;
- missed cadence is visible;
- restore occurs in an isolated environment;
- artifact hash and verification are preserved;
- export and restore tests pass.

## S10.28 Implement Audit Event Endpoint and Global Timeline

### Objective

Expose immutable, authorization-filtered audit history.

### Work

- implement `GET /api/v1/audit/events` and event detail;
- return event, workspace, experiment, timestamp, actor, type, entity, outcome, reason, correlation, request, cycle, workflow, job, bounded details, and integrity references;
- support approved filters and cursor pagination;
- preserve deterministic ordering;
- enforce RLS and role-specific detail minimization.

### Acceptance Criteria

- events are append-only;
- critical lifecycle, security, integrity, reconciliation, and halt events remain discoverable;
- pagination is deterministic;
- unauthorized details are absent;
- API tests pass.

## S10.29 Implement Audit Integrity View

### Objective

Expose missing, duplicate, corrupted, or retention-limited audit evidence.

### Work

- render event count and range, sequence gaps, integrity hash, chain verification, duplicate detection, retention, export verification, and limitations;
- classify integrity failure separately from empty history;
- link to incidents and recovery;
- add safe telemetry;
- test tamper and gap fixtures where implemented.

### Acceptance Criteria

- missing evidence never appears as no activity;
- integrity state is server-calculated;
- failures remain prominent;
- unsupported integrity features are labeled unavailable;
- integrity tests pass.

## S10.30 Implement Experiment Validity Classification

### Objective

Provide an authoritative server-calculated assessment of research validity.

### Work

- evaluate configuration integrity, lifecycle, preflight, cycles, data, Gemini, strategy, risk, idempotency, accounting, reconciliation, incidents, halts, exports, restore, report, and service limitations;
- return valid running, valid with warnings, paused for review, halted, invalidated, complete, complete with limitations, or failed;
- include reason codes and evidence;
- expose compatibility version;
- prohibit frontend derivation.

### Acceptance Criteria

- validity is deterministic for the same evidence;
- every non-valid state has reasons;
- positive performance cannot override invalidity;
- missing evidence fails closed;
- classification tests pass.

## S10.31 Implement 30-Day Progress and Completeness View

### Objective

Distinguish elapsed time from evidence completeness.

### Work

- render planned and actual period, elapsed and remaining time, expected, attempted, successful, warned, failed, delayed, duplicate, skipped, and invalidated counts, longest gap, latest success, freshness, incidents, halts, reconciliation, export cadence, and report readiness;
- use server-calculated counts;
- expose definitions and limitations;
- provide accessible summaries;
- avoid progress-as-success framing.

### Acceptance Criteria

- time progress and evidence completeness remain separate;
- counts link to filtered cycle history;
- current blockers are visible;
- no profit target is used as completion evidence;
- component tests pass.

## S10.32 Implement Current and Final Experiment Report

### Objective

Generate a complete research record prioritizing reliability, integrity, and limitations.

### Work

- include identity, configuration, period, services, schedule, cycle completeness, market quality, Gemini, strategy, risk, portfolio, benchmarks, orders, fills, ledger, reconciliation, incidents, halts, recovery, exports, restore, audit, reliability, cost, quotas, cold starts, UX findings, limitations, simulation statement, and next-stage decision;
- generate authoritative JSON and approved human-readable derivatives;
- preserve unresolved warnings;
- enforce authorization;
- record report hash.

### Acceptance Criteria

- profit is not an exit criterion;
- unresolved incidents and integrity failures cannot be omitted;
- report provenance is complete;
- simulation and non-guarantee language is explicit;
- report tests pass.

## S10.33 Implement Benchmark and Portfolio Summary

### Objective

Present current paper performance with compatible cash, buy-and-hold, and backtest evidence.

### Work

- render period, capital, data, valuation, costs, precision, versions, reconciliation, and limitations;
- compare current portfolio with cash and buy-and-hold;
- link to related backtest evidence;
- classify incompatible periods or assumptions;
- use non-promotional language.

### Acceptance Criteria

- assumptions remain visible;
- unreconciled performance cannot appear final;
- incompatibility is explicit;
- performance does not suppress operational failures;
- comparison tests pass.

## S10.34 Implement Authorized Experiment Export

### Objective

Generate provenance-preserving experiment, cycle, incident, recovery, audit, and report packages.

### Work

- support configuration, preflight, lifecycle, cycles, services, incidents, halts, recovery, export/restore, audit, validity, and report packages;
- generate server-side;
- include schema, identity, configuration hash, simulation, timestamps, lifecycle, validity, warnings, incidents, halts, reconciliation, completeness, provenance, integrity, limitations, and authorization context;
- preserve critical unresolved evidence;
- record safe telemetry.

### Acceptance Criteria

- the same resource and format produce deterministic content where required;
- critical warnings cannot be omitted;
- secrets and private environment values are absent;
- integrity hashes are verified where applicable;
- export tests pass.

## S10.35 Add Explicit State Handling

### Objective

Define safe rendering for every experiment, cycle, incident, command, recovery, and audit state.

### Work

- implement loading, empty, draft, preflight pending/failed, ready, starting, running, paused, resuming, halted, completing, completed, failed, archived, no cycles, expected, delayed, running, complete, warning, failed, lock rejected, duplicate, missed, stale market, Gemini fallback, risk halt, reconciliation mismatch, incident, recovery, export overdue, restore failed, report incomplete, audit failure, schema mismatch, unauthorized, not found, backend unavailable, command conflict, and export failure states;
- define bounded retry policy;
- prevent infinite retries;
- label cached data stale.

### Acceptance Criteria

- critical states never render as success or empty;
- loading fabricates no cycle or health data;
- conflicts preserve current server state;
- stale cached data is explicit;
- state-matrix tests pass.

## S10.36 Add Responsive and Accessibility Verification

### Objective

Ensure operational evidence and confirmations remain usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom layouts;
- test headings, landmarks, focus, keyboard operation, tables, timelines, definitions, filters, command confirmations, announcements, copy controls, and status hierarchy;
- verify reduced motion and contrast;
- test long IDs, hashes, workflow references, reason codes, and service names;
- record screen-reader spot checks.

### Acceptance Criteria

- no critical evidence is hover-only;
- no state relies only on color;
- confirmations are fully keyboard and screen-reader operable;
- table and timeline context survives narrow widths;
- no critical automated violation remains;
- manual evidence is recorded.

## S10.37 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make lifecycle authority, scheduling integrity, idempotency, recovery, audit, and no-live-trading boundaries release-blocking.

### Work

- add contract, lifecycle, preflight, scheduling, cycle, lock, idempotency, incident, halt, recovery, export, restore, audit, validity, report, route, E2E, accessibility, visual, authorization, and RLS tests;
- add CSRF, rate-limit, expected-version, hostile-content, secret, log-redaction, and unsafe-command tests;
- verify browser users cannot write critical domain tables directly;
- verify internal safety systems may halt but not silently resume;
- instrument safe experiment, preflight, transition, cycle, delay, lock, duplicate, data, Gemini, strategy, risk, execution, reconciliation, incident, recovery, export, restore, report, audit, conflict, and denied-authorization metrics;
- test prohibited telemetry fields.

### Acceptance Criteria

- unauthorized and stale commands fail closed;
- duplicate commands and cycles create no duplicate financial effects;
- no browser or AI path enables live trading, private exchange orders, database repair, halt bypass, or automatic resume;
- audit and critical evidence remain append-only;
- telemetry contains no prohibited fields;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| API contracts | OpenAPI, schema, enum, decimal, unit, timestamp, null, blocker, conflict, permission, and compatibility tests |
| Lifecycle | Transition, authorization, idempotency, expected-version, confirmation, audit, pause, resume, halt, completion, and archive tests |
| Preflight | Configuration hash, services, RLS, market, Gemini, domain versions, locks, idempotency, ledger, reconciliation, exports, restore, runbook, and secret tests |
| Cycles | Schedule, intended/actual timing, delay, missed, lock, duplicate, market, Gemini, strategy, risk, order, fill, ledger, reconciliation, audit, timeout, and recovery tests |
| Operations | Service status, incident, halt, runbook, recovery, export cadence, restore drill, validity, and final report tests |
| Audit | Append-only, filters, pagination, correlation, integrity, retention, authorization, and export tests |
| Accessibility | Keyboard, timelines, tables, definitions, confirmations, announcements, zoom, reflow, and manual review |
| Security and privacy | RLS, command authorization, CSRF, rate limits, expected version, sanitization, secret scan, log redaction, no-bypass, no-private-order, no-live-trading, and telemetry tests |

## Sprint Exit Gate

Sprint 10 is complete only when:

- S10.1 through S10.37 are implemented and verified;
- experiment configuration is frozen, hashed, inspectable, and drift-protected;
- preflight is complete, versioned, expiring, and release-blocking;
- lifecycle commands are owner-authorized, idempotent, confirmation-gated, expected-version protected, and audited;
- start cannot proceed without valid configuration, preflight, reconciliation, export baseline, approval, schedule, and no active blockers;
- every cycle exposes intended and actual time, status, lock, idempotency, domain lineage, accounting, reconciliation, audit closure, and validity;
- GitHub scheduling is represented as best effort rather than exact-time execution;
- duplicate attempts create no duplicate financial side effects;
- incidents, halts, recovery, exports, restore drills, and audit evidence remain immutable and visible;
- experiment validity is server-calculated;
- the 30-day report prioritizes evidence completeness, reliability, integrity, costs, incidents, and limitations over profit;
- no browser or AI database repair, generic halt bypass, automatic resume, private Binance order, testnet, or live-trading authority exists;
- accessibility, responsive, security, privacy, contract, lifecycle, scheduling, cycle, lock, idempotency, incident, recovery, export, restore, audit, validity, report, E2E, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 11 defines and implements the Gemini Analysis, Validation, Evidence, and Research Narrative Workspace.
