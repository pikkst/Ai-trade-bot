# Sprint 19 Tasks — Model, Prompt, Strategy, Risk, Execution, and Configuration Change Management

Last reviewed: 2026-07-31  
Status: Ready for implementation  
Continuation status: Stop after Sprint 19 per project owner instruction

## Sprint Goal

Implement a server-authoritative change-management workspace that governs model, prompt, schema, data, feature, strategy, risk, execution, accounting, security, privacy, migration, frontend, cost, and infrastructure changes through immutable proposals, behavior-set diffs, impact analysis, profile-driven evidence, approvals, staged paper canaries, activation for future configurations, rollback, emergency expiry, deprecation, and removal gates. No automatic activation, active-experiment mutation, arbitrary configuration editing, automatic spend, Binance test activation, private exchange access, or live-trading authority is permitted.

## Authoritative References

- `docs/CHANGE_MANAGEMENT_ROLLOUT_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/AUTH_CONFIGURATION_SECURITY_RELEASE_WORKSPACE_IMPLEMENTATION.md`
- `docs/GEMINI_ANALYSIS_VALIDATION_WORKSPACE_IMPLEMENTATION.md`
- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`
- `docs/DATA_LIFECYCLE_DATASET_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/RESEARCH_REVIEW_STRATEGY_LIFECYCLE_WORKSPACE_IMPLEMENTATION.md`
- `docs/PERFORMANCE_RESILIENCE_CAPACITY_FINOPS_WORKSPACE_IMPLEMENTATION.md`
- `docs/INCIDENT_RESPONSE_POSTMORTEM_LEARNING_WORKSPACE_IMPLEMENTATION.md`
- `docs/DEVELOPER_PORTAL_DOCUMENTATION_TRACEABILITY_WORKSPACE_IMPLEMENTATION.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `AGENTS.md`

## S19.1 Define Versioned Change-Management Schemas

### Work

- define proposal, classification, behavior-set, diff, impact, dependency, compatibility, evidence, approval, rollout, canary, activation, rollback, freeze, emergency, deprecation, blocker, permission, and export contracts;
- include immutable IDs, versions, hashes, actors, timestamps, environments, states, and limitations;
- publish OpenAPI schemas and generate frontend types.

### Acceptance Criteria

- all lifecycle states are machine-readable;
- activation and rollback eligibility are server-provided;
- no arbitrary environment-value or secret-value fields exist;
- contract tests pass.

## S19.2 Implement Change Proposal Registry

### Work

- implement proposal list and detail endpoints;
- persist problem, rationale, desired outcome, non-goals, before/after behavior sets, owner, authors, target release/window, urgency, source tasks, ADRs, incidents, and audit references;
- support filters and cursor pagination;
- preserve rejected, withdrawn, superseded, and archived proposals.

### Acceptance Criteria

- every material proposal has immutable identity and behavior references;
- authorization and RLS prevent existence leaks;
- proposal history is preserved;
- API tests pass.

## S19.3 Implement Change Lifecycle State Machine

### Work

- implement draft, impact analysis, evidence planning, evaluation, review, approved rollout, rollout states, verified future-paper use, activation, rejection, withdrawal, rollback, deprecation, archive, and emergency states;
- require actor, reason, expected version, idempotency, evidence, and audit;
- prohibit CI-driven automatic progression and live-trading states.

### Acceptance Criteria

- invalid transitions fail closed;
- tests cannot auto-approve or activate;
- emergency expiry is explicit;
- state history is append-only.

## S19.4 Implement Canonical Change Categories

### Work

- register provider/model, prompt, report schema, AI safety, market data, features, strategy, risk, execution, accounting, benchmark, schedule, budget, retention, access, migration, API/event, observability, frontend, infrastructure, and runbook categories;
- map each category to default reviewers, risk dimensions, evidence profiles, and compatibility checks.

### Acceptance Criteria

- every proposal maps to one or more registered categories;
- unknown categories block review;
- category versions and deprecations are preserved.

## S19.5 Implement Change Risk Classification Engine

### Work

- classify financial integrity, risk authority, execution side effects, data, AI, security, privacy, migration, reliability, cost, accessibility, public content, reversibility, scope, and uncertainty;
- calculate low, moderate, high, or critical risk server-side;
- expose dimension-level reasoning and unknowns.

### Acceptance Criteria

- financial-authority, RLS, secret, ledger, or migration changes cannot be low risk;
- uncertainty biases classification safely;
- every class maps to required evidence and approval gates;
- reference tests pass.

## S19.6 Implement Immutable Behavior-Set Registry

### Work

- represent configuration, provider, configured model, prompt, report schema, validation, feature set, strategy, risk, execution, accounting, schedule, budget, retention, code revision, dependency lock, migration revision, and aggregate hash;
- implement canonical serialization and usage references;
- prevent mutation after use.

### Acceptance Criteria

- identical canonical behavior produces the same hash;
- any material behavior change produces a new behavior set;
- used behavior sets are immutable;
- property tests pass.

## S19.7 Implement Field-Level Diff Engine

### Work

- compare complete before/after behavior sets;
- return canonical field path, category, before/after value or redacted metadata state, materiality, compatibility, security/privacy class, required evaluation, affected resources, and explanation;
- provide table and narrative views.

### Acceptance Criteria

- secret values never appear;
- all material changes are visible;
- diffs are deterministic and version-linked;
- accessibility tests pass.

## S19.8 Implement Dependency Impact Analysis

### Work

- calculate direct and transitive impact across configurations, experiments, datasets, reports, strategies, risk, execution, ledger, APIs, schemas, events, permissions, migrations, providers, releases, runbooks, documentation, translations, and public content;
- classify active, historical, planned, required, optional, and unknown dependencies.

### Acceptance Criteria

- active experiment impact is explicit;
- unknown critical dependencies block approval;
- unauthorized resources do not leak;
- dependency tests pass.

## S19.9 Enforce Active Experiment Freeze

### Work

- verify experiment, configuration, and behavior-set locks;
- reject direct mutation or activation against running experiments;
- allow safety suspension or halt only through incident controls;
- require successor configuration and experiment versions for changed behavior;
- audit denied attempts.

### Acceptance Criteria

- running experiments retain exact frozen hashes;
- historical evidence is never rewritten;
- safety interventions do not silently change behavior;
- integration tests pass.

## S19.10 Implement Compatibility Review Engine

### Work

- evaluate schema, API, event, database, configuration, dataset, report, strategy/risk/execution/accounting, frontend, provider, rollback, and historical-readability compatibility;
- return compatible, migration-required, limited, breaking, unknown, or unavailable;
- link evidence and remediation.

### Acceptance Criteria

- unknown critical compatibility fails closed;
- breaking changes require versioning and migration guidance;
- historical evidence readability is tested;
- reference tests pass.

## S19.11 Implement Change Evidence Plan Registry

### Work

- define required evidence profile, environments, datasets, fixtures, thresholds, stop conditions, owners, reviewers, dates, provider limits, budgets, security/privacy boundaries, and plan hash;
- require plan approval before final canary evidence;
- preserve post-hoc changes as new versions.

### Acceptance Criteria

- evidence requirements predate staged rollout;
- thresholds and stop conditions are immutable per plan;
- provider and cost bounds are explicit;
- tests pass.

## S19.12 Implement Evidence Completeness Engine

### Work

- classify evidence as required, optional, not applicable, present, passed, warning, failed, stale, incompatible, missing, or unavailable;
- require reasons for not-applicable items;
- preserve failed evidence and expose blockers;
- calculate descriptive inventory only.

### Acceptance Criteria

- completeness cannot approve a change;
- stale or failed evidence cannot pass;
- missing critical evidence blocks review;
- deterministic tests pass.

## S19.13 Implement Provider and Model Change Review

### Work

- compare provider configuration, configured model, adapter, terms, region, tier, quota, latency, and cost;
- run structured-output, grounding, repeated-run stability, refusal, safety, timeout, rate-limit, malformed-response, injection, and fallback evaluations;
- verify no tool or execution authority.

### Acceptance Criteria

- provider response success and validated-report success remain separate;
- serving implementation claims remain evidence-bounded;
- regressions block rollout;
- no model gains command authority.

## S19.14 Implement Prompt and Report-Schema Change Review

### Work

- generate semantic prompt and schema diffs;
- verify evidence/instruction separation, examples, contract compatibility, grounding, certainty, injection resistance, malicious inputs, rendering, fallback, archival, and reproducibility;
- run approved evaluation comparisons.

### Acceptance Criteria

- schema-breaking changes create new versions;
- evidence cannot become instruction;
- unsupported claims fail validation;
- historical reports remain readable or have migration guidance.

## S19.15 Implement Feature and Strategy Change Review

### Work

- verify feature formulas, warm-up, no-look-ahead, parameter schemas, behavior hashes, design/validation/untouched-final-test results, benchmarks, tested variants, robustness, walk-forward evidence, reproducibility, risk compatibility, and paper-canary plan;
- preserve rejected and unfavorable variants.

### Acceptance Criteria

- contaminated final-test evidence blocks rollout;
- hidden variant selection invalidates approval;
- strategy changes cannot bypass Sprint 17 review;
- tests pass.

## S19.16 Implement Risk Policy Change Review

### Work

- compare changed limits, units, rationale, incident/research references, position, exposure, drawdown, reservation, and halt behavior;
- run invariant, boundary, simulation, compatibility, and portfolio-impact tests;
- require independent financial-integrity review and owner approval for increases.

### Acceptance Criteria

- risk-limit increases are high or critical;
- performance alone cannot justify weaker controls;
- incompatible strategies are blocked;
- property tests pass.

## S19.17 Implement Execution and Accounting Change Review

### Work

- verify order lifecycle, activation and fill timing, fees, spread, slippage, precision, minimum notional, partial fills, cancellation, reservations, atomic ledger posting, balanced transactions, state versions, reconciliation, rebuild, migrations, and rollback/forward-fix plans.

### Acceptance Criteria

- atomicity, decimal precision, idempotency, and reconciliation remain mandatory;
- duplicate side effects remain zero tolerance;
- applied migrations are not edited;
- integration/property tests pass.

## S19.18 Implement Data, Retention, and Provider-Request Review

### Work

- verify dataset classifications, schemas, quality rules, lineage, manifests, corrections, retention, holds, archive/restore, deletion/anonymization, fixture boundaries, provider minimization, privacy, public promotion, and reproducibility impact.

### Acceptance Criteria

- invalid or quarantined data cannot enter rollout;
- active holds and unknown dependencies block destructive changes;
- provider requests contain approved minimum evidence only;
- privacy tests pass.

## S19.19 Implement Security and Access Change Review

### Work

- verify Auth/session behavior, permission catalog, handler checks, RLS/storage policies, service/migration roles, secret posture, threat model, scans, findings, incident/runbook updates, rollback, and independent review.

### Acceptance Criteria

- API/RLS mismatch is critical;
- service-role credentials never reach browsers;
- secret regressions block rollout;
- security tests pass.

## S19.20 Implement Migration Change Review

### Work

- require a new immutable migration, clean reset, upgrade, drift detection, data transformation tests, RLS/index checks, expand-migrate-contract stage, compatibility window, rehearsal, backup/restore prerequisite, lock classification, and rollback/forward-fix strategy.

### Acceptance Criteria

- applied migrations cannot be edited;
- drift or rehearsal failure blocks rollout;
- destructive changes require approved recovery evidence;
- migration tests pass.

## S19.21 Implement Frontend, Accessibility, Content, and Localization Review

### Work

- verify routes, contracts, loading/error/stale/critical states, keyboard, screen readers, zoom, reflow, contrast, reduced motion, English/Estonian semantic parity, product identity, no-hype language, notifications, visual regression, public/private boundaries, and performance budgets.

### Acceptance Criteria

- safety meaning is identical in English and Estonian;
- no guarantee, urgency, or advice language is introduced;
- critical accessibility failures block rollout;
- tests pass.

## S19.22 Implement Cost, Quota, Capacity, and Resilience Review

### Work

- verify pricing-reference versions, billed/estimated status, budget reservations, free-tier constraints, usage forecast, database/workflow/backtest/provider headroom, resilience and recovery evidence, unit-cost impact, anomalies, and no-auto-upgrade state.

### Acceptance Criteria

- insufficient headroom or exhausted budget blocks the relevant stage;
- estimates are not presented as invoices;
- no automatic purchase, scaling, or budget increase occurs;
- tests pass.

## S19.23 Implement Reviewer Assignment and Conflict Workflow

### Work

- assign change owner, domain, financial-integrity, security/privacy, data, accessibility/content, operations, release, and owner-decision roles based on risk profile;
- record expertise, scope, due date, acceptance, conflict declarations, resolution, and audit.

### Acceptance Criteria

- high-risk changes cannot be self-approved by the sole author;
- unresolved required conflicts block approval;
- assignment history is immutable;
- authorization tests pass.

## S19.24 Implement Immutable Approval Snapshot

### Work

- freeze proposal, risk, behavior sets, diff, impact, dependencies, compatibility, evidence plan/results, reviewers/conflicts, limitations, rollout, stop, rollback, deprecation, release, and environment references;
- calculate snapshot hash;
- invalidate approvals after material changes.

### Acceptance Criteria

- every approval maps to one exact snapshot hash;
- changed evidence cannot reuse old approval;
- snapshots are immutable and reproducible;
- tests pass.

## S19.25 Implement Approval Commands

### Work

- support approved-for-staged-paper-rollout, changes-requested, rejected, withdrawn, emergency-containment, rollout-continuation, future-paper-activation, rollback, and deprecation decisions;
- require eligible role, recent authentication, idempotency, expected version, snapshot hash, rationale, blockers, and audit.

### Acceptance Criteria

- no live-trading approval outcome exists;
- tests, scores, or metrics cannot auto-approve;
- stale snapshots fail safely;
- security tests pass.

## S19.26 Implement Rollout Plan Registry

### Work

- persist rollout ID/version, approval snapshot, environments, stages, target configurations, paper-canary design, entry/exit gates, observations, stop conditions, maintenance notices, rollback/forward-fix, owners, schedule, and audit;
- preserve cancelled and failed plans.

### Acceptance Criteria

- rollout plans are immutable after approval;
- stage skips require explicit profile, evidence, and approval;
- every plan remains paper-only;
- API tests pass.

## S19.27 Implement Staged Rollout Engine

### Work

- support local deterministic tests, CI/integration, demo compatibility, isolated staging, bounded paper canary, extended paper observation, future-paper activation approval, and deprecation stages;
- evaluate entry/exit gates server-side;
- require explicit stage-start and stage-completion commands.

### Acceptance Criteria

- stages never progress automatically;
- missing evidence fails closed;
- active freezes and incidents block progression;
- lifecycle tests pass.

## S19.28 Implement Paper Canary Registry

### Work

- persist canary ID, behavior set, workspace/environment, frozen configuration, symbols, interval, dates, cycle/capital limits, provider/cost budget, baseline, success/warning/stop conditions, monitoring, incidents, halts, report, and live-disabled state.

### Acceptance Criteria

- canary configuration is immutable;
- limits and budgets are bounded;
- baseline assumptions are explicit;
- Binance test and live execution remain prohibited.

## S19.29 Implement Canary Stop Conditions

### Work

- enforce ledger/reconciliation, duplicate side effects, invalid/stale data, Gemini safety/validation, strategy/risk disagreement, drawdown/exposure/cost, quota/budget, schedule/cycle, security/privacy, release/migration, and configuration-drift stops;
- route outcomes to halt/pause and incident workflows.

### Acceptance Criteria

- critical stops act immediately according to policy;
- no stop condition auto-resumes;
- all stop evidence is immutable;
- integration tests pass.

## S19.30 Implement Rollout Observation and Comparison

### Work

- record stage, times, behavior hash, datasets, snapshots, decisions, risk outcomes, orders, fills, costs, ledger, reconciliation, provider, quota, latency, budget, SLO, incidents, baseline comparison, differences, and limitations;
- validate compatible comparisons.

### Acceptance Criteria

- observations map to exact behavior sets and evidence;
- positive results cannot suppress incidents or integrity failures;
- incompatible baselines fail closed;
- tests pass.

## S19.31 Implement Rollout Gate Engine

### Work

- evaluate approval snapshot, environment/configuration compatibility, evidence freshness, findings, incidents, data, reproducibility, financial integrity, quotas, budgets, capacity, security, privacy, accessibility, release readiness, stop conditions, and required approvals.

### Acceptance Criteria

- missing required evidence fails closed;
- critical blockers cannot be waived by rollout metrics;
- gate outcomes are deterministic and versioned;
- tests pass.

## S19.32 Implement Future Paper Activation Boundary

### Work

- create a new immutable configuration version referencing the verified behavior set;
- require exact approval snapshot, rollout verification, dependency compatibility, owner role, recent authentication, idempotency, expected version, explicit confirmation, and audit;
- require preflight for every new experiment.

### Acceptance Criteria

- activation affects only future paper configurations;
- running experiments remain frozen;
- no direct behavior-set-to-order path exists;
- live-trading-disabled state remains explicit.

## S19.33 Implement Rollback and Forward-Fix Workflow

### Work

- persist trigger, current/target behavior sets, compatibility, environments, active-experiment handling, database/data impact, halt/read-only behavior, backup/restore prerequisites, runbooks, verification, approvals, and limitations;
- support forward fix when rollback is unsafe;
- preserve failed attempts.

### Acceptance Criteria

- completed evidence is never rewritten;
- post-change health, RLS, data, ledger, reconciliation, and behavior verification are mandatory;
- uncertain integrity keeps the halt active;
- tests pass.

## S19.34 Implement Change Calendar

### Work

- persist change/release reference, environment, scope, planned window, risk, owner/responders, maintenance/communication, conflicts, freeze interaction, actual timing, outcome, and audit;
- detect overlapping high-risk changes and experiment critical periods.

### Acceptance Criteria

- conflicts are explicit before rollout;
- calendar entries do not execute changes;
- actual and planned timing remain distinct;
- tests pass.

## S19.35 Implement Change Freeze and Exception Workflow

### Work

- support freezes for integrity/security incidents, exhausted error budgets, experiment critical periods, migration/restore failure, public events, observation windows, provider instability, and stabilization periods;
- require scope, reason, timing, review, expiry, approver, and audit;
- require necessity, compensating controls, rollback, expiry, and retrospective review for exceptions.

### Acceptance Criteria

- active freeze blocks unauthorized progression;
- critical safety fixes use emergency controls rather than silent bypass;
- exceptions expire and remain auditable;
- tests pass.

## S19.36 Implement Emergency Change Workflow

### Work

- persist incident/reason, exact minimal change, environment/resources, risk/unknowns, actor/approver, start, automatic expiry, verification, rollback, communication, evidence hold, retrospective deadline, and permanent replacement/removal plan;
- enforce paper-only boundaries.

### Acceptance Criteria

- emergency changes cannot enable live trading, edit applied migrations, expose secrets, bypass audit, alter completed evidence, or auto-resume;
- expiry is automatic by policy state;
- overdue retrospective review becomes a blocker;
- security tests pass.

## S19.37 Implement Emergency Retrospective Review

### Work

- review necessity, alternatives, authorization, scope, impact, verification, expiry, permanent fix/removal, tests, runbooks, documentation, release evidence, and process improvements;
- require owner approval;
- preserve failed or unjustified outcomes.

### Acceptance Criteria

- emergency use cannot become permanent silently;
- unresolved permanent fix remains visible;
- lessons link to corrective actions;
- review tests pass.

## S19.38 Implement Deprecation and Removal Registry

### Work

- persist affected behavior/contract, replacement, reason, announcement, support window, active usage, dependencies, migration guide, warnings, removal gates, owner, approval, archive, and reproducibility requirements;
- verify no active configuration/experiment dependency before removal.

### Acceptance Criteria

- historical evidence remains readable;
- removal requires usage, migration, replacement, documentation, restore, and owner evidence;
- deprecation cannot silently disable active resources;
- tests pass.

## S19.39 Implement Change Audit Timeline and Export

### Work

- expose immutable proposal, classification, impact, evidence, reviewers, approvals, rollout, canary, pause, halt, activation, rollback, emergency, freeze, deprecation, removal, incident, release, and invalidation events;
- generate authorized server-side export with schema versions, hashes, environments, blockers, limitations, paper-only state, and redaction.

### Acceptance Criteria

- every transition links to audit evidence;
- failed and rejected evidence remains included;
- secrets and private payloads are excluded;
- export integrity hashes verify.

## S19.40 Add Explicit UI States, Accessibility, Security, and Full Verification

### Work

- implement loading, empty, draft, analysis, evaluation, changes requested, review, approved rollout, planned/running/paused/halted rollout, canary failure, verified, future activation, rejection, withdrawal, rollback, forward fix, freeze, exception, emergency, expired retrospective, deprecation, removal blocked, compatibility unknown, migration failure, exhausted budget, stale evidence, schema mismatch, unauthorized, conflict, backend unavailable, and export failure states;
- verify desktop, tablet, mobile, keyboard, screen readers, zoom, reflow, contrast, reduced motion, diffs, stages, dialogs, timelines, and copy controls;
- add contract, classification, compatibility, evaluation, approval, rollout, canary, activation, rollback, freeze, emergency, deprecation, authorization, RLS, secret, arbitrary-edit, auto-spend, active-experiment, Binance-test, private-exchange, live-trading, E2E, visual, and telemetry tests.

### Acceptance Criteria

- passing tests cannot hide failed canaries, incidents, freezes, or integrity failures;
- no state relies only on color or hover;
- no browser, AI, test, score, or automation path gains arbitrary configuration, SQL, shell, workflow, provider, deployment, budget, scaling, Binance test, private exchange, or live-trading authority;
- prohibited telemetry fields are absent;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Proposal and behavior | Registry, lifecycle, categories, risk, immutable behavior sets, hashes, diffs, dependencies, active-experiment freeze, and audit tests |
| Compatibility and evaluation | Contracts, schemas, migrations, providers/models, prompts, features, strategy, risk, execution, accounting, data, security, frontend, accessibility, cost, and capacity tests |
| Approval | Evidence plans, completeness, reviewer roles, conflicts, immutable snapshots, recent authentication, idempotency, expected versions, blockers, and no-auto-approval tests |
| Rollout | Plans, stages, paper canaries, baselines, budgets, observations, stop conditions, gates, incidents, reconciliation, future activation, and no-auto-resume tests |
| Recovery and lifecycle | Rollback, forward fix, calendar, freezes, exceptions, emergency expiry, retrospective review, deprecation, removal, archive, and historical-readability tests |
| Security and accessibility | Authorization, RLS, secret redaction, no arbitrary editing/execution, no auto-spend/scale, no active-experiment mutation, keyboard, screen readers, zoom, and telemetry tests |

## Sprint Exit Gate

Sprint 19 is complete only when:

- S19.1 through S19.40 are implemented and verified;
- every material change has an immutable proposal, before/after behavior sets, aggregate hashes, classification, impact analysis, dependency graph, and compatibility result;
- running experiments remain frozen;
- evidence requirements are profile-driven and pre-approved;
- failed, stale, incompatible, missing, and unfavorable evidence remains visible;
- approvals are tied to immutable snapshots and invalidated by material changes;
- staged rollout and canaries use immutable paper configurations, bounded capital and provider budgets, baselines, stop conditions, incidents, ledger, and reconciliation evidence;
- activation applies only to future paper configurations after verified rollout and owner approval;
- rollback or forward fix preserves historical evidence and verifies financial integrity;
- freezes, emergency expiry, retrospective review, deprecation, support windows, usage evidence, and removal gates are enforced;
- no AI, browser, CI result, score, or automation can approve, activate, edit arbitrary configuration, mutate active experiments, edit applied migrations, auto-purchase, auto-scale, increase budgets, access Binance test/private exchange, or enable live trading;
- accessibility, responsive, security, privacy, contract, classification, compatibility, evaluation, approval, rollout, rollback, emergency, deprecation, E2E, export, audit, and visual checks pass;
- documentation and changelog are updated;
- both Sprint 19 commits are fetched and verified.

## Project Continuation Boundary

Work stops after Sprint 19. No Sprint 20 documentation or task file is created unless the project owner explicitly requests continuation.
