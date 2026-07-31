# Sprint 17 Tasks — Research Review, Strategy Lifecycle, Evidence Scoring, Decision Governance, and Promotion Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a human-governed research-review workspace that connects falsifiable hypotheses, preregistered plans, immutable strategy versions, complete backtest and paper evidence, robustness, reproducibility, costs, operations, governance, reviewer comments, owner decisions, future-paper promotion, suspension, rollback, and retirement without allowing performance, scores, Gemini, or frontend logic to authorize strategy activation.

## Authoritative References

- `docs/RESEARCH_REVIEW_STRATEGY_LIFECYCLE_WORKSPACE_IMPLEMENTATION.md`
- `docs/STRATEGY_ENGINE.md`
- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`
- `docs/BACKTEST_EXPERIMENT_COMPARISON_WORKSPACE_IMPLEMENTATION.md`
- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `docs/DATA_LIFECYCLE_DATASET_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/GEMINI_ANALYSIS_VALIDATION_WORKSPACE_IMPLEMENTATION.md`
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`
- `docs/PERFORMANCE_RESILIENCE_CAPACITY_FINOPS_WORKSPACE_IMPLEMENTATION.md`
- `docs/AUTH_CONFIGURATION_SECURITY_RELEASE_WORKSPACE_IMPLEMENTATION.md`
- `docs/DEVELOPER_PORTAL_DOCUMENTATION_TRACEABILITY_WORKSPACE_IMPLEMENTATION.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `AGENTS.md`

## S17.1 Define Versioned Research Review Schemas

### Objective

Create explicit contracts for hypotheses, plans, preregistration, strategy versions, lifecycle, reviews, snapshots, completeness, evidence categories, scores, reviewers, conflicts, comments, change requests, decisions, promotions, suspension, rollback, retirement, blockers, permissions, and links.

### Work

- define `ResearchReviewReadModel` and nested schemas;
- define strategy-lifecycle and decision models;
- define review type, outcome, score, blocker, comment, lifecycle, and invalidation states;
- require immutable IDs, hashes, versions, timestamps, actor references, and limitations;
- publish schemas in OpenAPI;
- generate frontend types.

### Acceptance Criteria

- every review and lifecycle state is machine-readable;
- approval and permission fields are server-provided;
- no aggregate auto-approval field exists;
- compatibility and nullability are explicit;
- contract tests pass.

## S17.2 Implement Hypothesis Registry

### Objective

Persist falsifiable research questions, mechanisms, outcomes, benchmarks, confounders, and supersession.

### Work

- implement hypothesis list and detail endpoints;
- store statement, scope, mechanism, rationale, prior evidence, falsification, outcomes, benchmarks, risks, data plan, costs, authors, owner, timestamps, status, and audit;
- validate non-promotional language;
- support versioning and supersession;
- enforce authorization and RLS.

### Acceptance Criteria

- every accepted hypothesis has explicit falsification criteria;
- profit guarantees are rejected;
- old hypotheses remain auditable;
- unauthorized existence is not leaked;
- API tests pass.

## S17.3 Implement Hypothesis Lifecycle

### Objective

Govern draft, review, accepted, rejected, in-progress, falsified, supported, inconclusive, superseded, and archived states.

### Work

- define state transitions and actors;
- require reason, expected version, idempotency, and audit;
- distinguish hypothesis outcome from strategy promotion;
- preserve transition history;
- prevent silent state changes.

### Acceptance Criteria

- invalid transitions fail deterministically;
- falsified hypotheses cannot appear approved;
- repeated commands are idempotent;
- history is immutable;
- state-machine tests pass.

## S17.4 Implement Research Plan Registry

### Objective

Persist versioned methods, stages, splits, metrics, benchmarks, assumptions, robustness, reproducibility, stopping, and review rules.

### Work

- implement plan list/detail;
- store hypothesis, candidates, data, stages, splits, metrics, benchmarks, costs, execution/accounting, robustness, reproducibility, stopping, invalidation, incidents, corrections, authors, reviewers, approval, and hash;
- validate completeness;
- preserve superseded plans;
- link datasets and configurations.

### Acceptance Criteria

- every plan identifies design, validation, final-test, walk-forward, and paper stages where applicable;
- assumptions are versioned;
- plan hashes are deterministic;
- used plans are immutable;
- tests pass.

## S17.5 Implement Pre-Registration Workflow

### Objective

Freeze research criteria before final-test or paper evidence exists.

### Work

- require plan hash, timestamp, metrics, thresholds, parameter boundaries, splits, benchmarks, robustness, paper duration, decision criteria, authors, approvers, and audit;
- verify timing against evidence creation;
- create a new version for post-hoc changes;
- expose contamination warnings;
- require recent authentication for approval.

### Acceptance Criteria

- preregistration after final-test evidence is marked post-hoc;
- immutable hash is preserved;
- changes cannot overwrite original plan;
- final-test readiness checks preregistration;
- workflow tests pass.

## S17.6 Implement Immutable Strategy Version Registry

### Objective

Persist family, version, code, configuration hash, parameters, features, Gemini, market, risk, execution, accounting, lifecycle, owner, and supersession.

### Work

- implement strategy list and detail endpoints;
- define parameter schemas and canonical serialization;
- calculate behavior-set hash;
- prevent update/delete after use;
- create successor versions for changes;
- link tests and source revision.

### Acceptance Criteria

- used strategy versions are immutable;
- behavior dependencies are complete;
- parameter hashes are deterministic;
- successor relations are explicit;
- property tests pass.

## S17.7 Implement Strategy Dependency Assurance

### Objective

Verify exact feature, data, Gemini, risk, execution, accounting, benchmark, configuration, code, dependency, migration, and environment compatibility.

### Work

- register required dependency types and versions;
- compare candidate strategy with review and target configuration;
- detect missing, stale, incompatible, or changed dependencies;
- calculate compatibility server-side;
- link governance and reproducibility evidence.

### Acceptance Criteria

- changed dependency creates a new behavior/review scope;
- incomplete dependencies block promotion;
- frontend cannot infer compatibility;
- evidence is traceable;
- tests pass.

## S17.8 Implement Strategy Lifecycle State Machine

### Objective

Govern idea through approved paper use, suspension, rejection, supersession, retirement, and archive.

### Work

- implement all approved states and transitions;
- require actor, reason, expected version, idempotency, evidence, and audit;
- prohibit live-trading state;
- preserve running-experiment freezes;
- expose lifecycle history.

### Acceptance Criteria

- no state implies live approval;
- invalid transitions fail closed;
- active experiment versions cannot change;
- transition history is append-only;
- state tests pass.

## S17.9 Implement Review Registry and Types

### Objective

Create versioned hypothesis, plan, stage, paper, promotion, suspension, rollback, and retirement reviews.

### Work

- implement review list/detail;
- store review identity, type, target transition, strategy, snapshot, status, reviewers, owner, due dates, revisions, and audit;
- define gate profiles by type;
- support filters and cursor pagination;
- enforce authorization.

### Acceptance Criteria

- every review has one target transition and profile;
- failed and archived reviews remain discoverable;
- unauthorized content is hidden;
- review type is machine-readable;
- API tests pass.

## S17.10 Implement Immutable Evidence Snapshot

### Objective

Freeze all evidence references and definitions used by a review and decision.

### Work

- capture hypothesis, plan, strategy, datasets, manifests, backtests, benchmarks, variants, robustness, reproducibility, experiments, incidents, costs, governance, reviewers, score definitions, and hashes;
- calculate snapshot hash;
- prevent mutation;
- detect changed dependencies;
- create successor snapshot when needed.

### Acceptance Criteria

- decisions map to exact immutable snapshot;
- material changes invalidate old decision scope;
- snapshot completeness is verifiable;
- no evidence is copied as mutable prose only;
- tests pass.

## S17.11 Implement Evidence Inventory and Completeness Engine

### Objective

Classify required, optional, not-applicable, present, missing, stale, invalid, incompatible, warning, and unavailable evidence.

### Work

- define profile-versioned evidence requirements by review type;
- evaluate server-side;
- include references, blockers, period/sample adequacy, and evaluation time;
- expose descriptive inventory percentage only;
- prohibit auto-approval.

### Acceptance Criteria

- 100% completeness does not approve a strategy;
- critical missing evidence blocks relevant transition;
- not-applicable requires reason;
- results are deterministic;
- reference tests pass.

## S17.12 Implement Data and Split Review

### Objective

Verify datasets, hashes, quality, lineage, finalization, metadata, ranges, leakage, corrections, representativeness, and holds.

### Work

- inspect exact dataset versions;
- verify design/validation/final-test/walk-forward ranges;
- detect overlap and look-ahead leakage;
- verify untouched final-test state;
- include corrections and invalidations;
- link retention and reproducibility.

### Acceptance Criteria

- contaminated final test blocks approval;
- invalid datasets block review;
- split boundaries are explicit;
- known gaps remain visible;
- data-review tests pass.

## S17.13 Implement Methodology Review

### Objective

Verify clock, finalization, no-look-ahead, execution timing, costs, fills, ledger, Gemini replay, failure behavior, seeds, and ordering.

### Work

- evaluate methodology versions and settings;
- compare with plan and actual runs;
- detect incompatible or undocumented changes;
- link backtest and paper evidence;
- preserve limitations and reviewer comments.

### Acceptance Criteria

- methodology drift is explicit;
- no-look-ahead is release-blocking;
- cost and accounting assumptions are complete;
- fallback behavior is documented;
- tests pass.

## S17.14 Implement Backtest Evidence Review

### Objective

Aggregate complete, partial, failed, design, validation, final-test, benchmark, trade, ledger, and report evidence.

### Work

- validate run completeness and reconciliation;
- render gross/net, drawdown, volatility, exposure, turnover, costs, sample counts, trades, events, warnings, hashes, definitions, and limitations;
- preserve failed and partial runs;
- compare compatible benchmarks;
- link source data and manifests.

### Acceptance Criteria

- partial runs never appear final;
- unreconciled metrics are not authoritative;
- cash and buy-and-hold assumptions are visible;
- failed runs remain discoverable;
- tests pass.

## S17.15 Implement Tested Variant Disclosure

### Objective

Expose all parameter, period, symbol, cost, methodology, selected, rejected, failed, cancelled, and incomplete variants.

### Work

- register variant identity and selection context;
- link optimization or manual selection method;
- detect undeclared variants;
- expose multiple-comparison and selection-bias limitations;
- preserve final-test contamination state;
- support filters.

### Acceptance Criteria

- cherry-picked-only views are impossible by default;
- failed variants cannot be deleted;
- manual selection is explicit;
- undeclared variants invalidate relevant decision;
- tests pass.

## S17.16 Implement Robustness Review

### Objective

Evaluate neighboring parameters, costs, delays, periods, regimes, symbols, walk-forward windows, gaps, Gemini availability, scheduling, and capital sensitivity.

### Work

- define robustness-study types and versions;
- require changed/unchanged assumptions;
- validate compatible comparisons;
- preserve unfavorable results;
- summarize sensitivity without hidden aggregate;
- link plan requirements.

### Acceptance Criteria

- every robustness result identifies assumptions;
- incompatible comparisons fail closed;
- unfavorable studies remain visible;
- missing planned studies block the relevant review;
- tests pass.

## S17.17 Implement Reproducibility Review

### Objective

Verify manifests, reruns, code, dependencies, migrations, seeds, event ordering, hashes, archive restore, and differences.

### Work

- consume Sprint 16 manifests;
- execute or ingest approved verification runs;
- compare events, trades, ledger, metrics, benchmarks, reports, and state hashes;
- classify verified, limited, mismatch, incomplete, and unavailable;
- link failed evidence to blockers.

### Acceptance Criteria

- mismatches cannot be hidden by similar summary metrics;
- all mandatory manifest fields are checked;
- archived inputs must restore;
- limitations remain visible;
- tests pass.

## S17.18 Implement Paper Experiment Review

### Objective

Review frozen configuration, cycles, schedules, data, Gemini, strategy, risk, execution, accounting, incidents, recovery, benchmarks, and report evidence.

### Work

- validate preflight and actual period;
- analyze expected/attempted/successful/failed/delayed/missed cycle counts;
- verify freshness, budgets, decisions, orders, fills, costs, ledger, and reconciliation;
- include incidents, halts, exports, restore, and report;
- compare backtest-to-paper methodology.

### Acceptance Criteria

- incomplete or unreconciled experiments cannot approve promotion;
- schedule gaps and provider failures remain visible;
- paper and backtest differences are explicit;
- performance does not suppress incidents;
- tests pass.

## S17.19 Implement Operational and Cost Review

### Objective

Assess SLOs, quotas, capacity, resilience, recovery, budgets, unit costs, anomalies, and scale triggers.

### Work

- link Sprint 15 evidence;
- verify cycle duration versus cadence;
- verify provider and database headroom;
- include resilience failures and recovery evidence;
- compare actual cost with plan;
- preserve no-auto-upgrade state.

### Acceptance Criteria

- exhausted quota or failed recovery blocks relevant promotion;
- estimated and billed costs remain distinct;
- insufficient capacity evidence is explicit;
- cost is not profit justification;
- tests pass.

## S17.20 Implement Governance Review

### Objective

Assess Auth, RLS, configuration, secrets, migrations, findings, privacy, retention, terms, backup, accessibility, release, and incidents.

### Work

- consume governance and release evidence;
- classify required gates by review type;
- include expired exceptions and stale terms;
- verify paper-only/live-disabled state;
- preserve unresolved blockers;
- link approvals and audits.

### Acceptance Criteria

- critical security/privacy/RLS failures block approval;
- stale provider terms are explicit;
- accessibility evidence is included;
- live trading remains disabled;
- tests pass.

## S17.21 Implement Evidence Score Registry

### Objective

Version dimension-specific rubrics, formulas, missing-data behavior, thresholds, limitations, owners, and tests.

### Work

- define score IDs for completeness, data, methods, benchmarks, robustness, reproducibility, paper, accounting, operations, cost, governance, accessibility, and limitations;
- prevent hidden aggregate approval totals;
- preserve old definitions;
- link source evidence;
- expose accessible explanations.

### Acceptance Criteria

- every score identifies inputs and version;
- missing data behavior is explicit;
- no score means probability of profit;
- score changes do not rewrite old reviews;
- registry tests pass.

## S17.22 Implement Evidence Score Calculation

### Objective

Calculate independent descriptive dimensions server-side.

### Work

- validate source evidence and compatibility;
- calculate rubric outcomes;
- return null or unavailable where required;
- preserve blockers independent of values;
- include calculation evidence and timestamp;
- add reference fixtures.

### Acceptance Criteria

- scores are deterministic;
- critical blockers override presentation priority;
- no weighted total automatically appears;
- insufficient evidence remains unavailable;
- tests pass.

## S17.23 Implement Evidence Score Workspace

### Objective

Present dimensions, definitions, versions, inputs, missing data, limitations, and related comments.

### Work

- render separate score cards/tables;
- provide no hidden ranking;
- link each value to evidence;
- show critical blockers first;
- support accessible non-color summaries;
- add comparison only for compatible definitions.

### Acceptance Criteria

- users can inspect every input;
- scores cannot be mistaken for approval;
- inaccessible color-only grading is absent;
- incompatible comparisons fail closed;
- accessibility tests pass.

## S17.24 Implement Reviewer Assignment Workflow

### Objective

Assign scope, role, expertise, due date, conflict declaration, and completion state.

### Work

- implement assign, accept, decline, revoke, and complete commands;
- require authorization, idempotency, expected version, and audit;
- support expertise categories and required reviewer profiles;
- preserve prior assignments;
- minimize personal data.

### Acceptance Criteria

- reviewer requirements are profile-driven;
- stale assignments cannot act;
- assignment history is immutable;
- unauthorized changes fail closed;
- workflow tests pass.

## S17.25 Implement Reviewer Conflict Declaration

### Objective

Record self-review, role overlap, selection involvement, disputed evidence creation, and expertise limitations.

### Work

- define conflict categories and severity;
- require reviewer declaration;
- allow owner/policy resolution with rationale and compensating reviewer;
- preserve history;
- avoid legal conclusions;
- block decisions where required.

### Acceptance Criteria

- unresolved required conflicts block decision;
- declarations are auditable;
- sensitive detail is role-limited;
- resolution cannot erase conflict history;
- tests pass.

## S17.26 Implement Review Comments and Evidence Threads

### Objective

Persist immutable comments, edit history, evidence scope, severity, and resolution.

### Work

- implement comment create, edit-with-history, resolve, supersede, and reject workflows;
- sanitize text;
- require evidence references for material findings;
- prevent author-only resolution of critical comments where policy requires verification;
- preserve deleted-account actor references;
- add notifications.

### Acceptance Criteria

- critical comments cannot disappear;
- edit history is visible;
- unsanitized content is inert;
- resolutions require rationale and reviewer authority;
- tests pass.

## S17.27 Implement Change Request Workflow

### Objective

Track required evidence or implementation changes and verification.

### Work

- persist affected resource, reason, required work, owner, due date, severity, status, completion evidence, verifier, and audit;
- link new immutable versions;
- invalidate review snapshot on material change;
- prevent completion from a commit message alone;
- support notifications.

### Acceptance Criteria

- material changes create new versions;
- completion requires evidence and verification;
- overdue blockers remain visible;
- old snapshot is preserved;
- workflow tests pass.

## S17.28 Implement Decision Gate Profiles

### Objective

Version required evidence, reviewers, blockers, owner actions, recent authentication, and invalidation for each review outcome.

### Work

- define plan, final-test, paper readiness, post-experiment, suspension, rollback, and retirement profiles;
- map evidence and score definitions;
- enforce no prohibited blockers;
- preserve profile versions;
- link governance and configuration.

### Acceptance Criteria

- gates differ explicitly by review type;
- missing profile evidence fails closed;
- old decisions retain old profile references;
- live approval profile does not exist;
- tests pass.

## S17.29 Implement Owner Decision Command

### Objective

Record approved-for-future-paper, changes-requested, rejected, suspended, or retired decisions against exact evidence.

### Work

- require owner role, recent authentication, immutable snapshot hash, required reviews, resolved critical comments, no prohibited blockers, scope, rationale, conditions, limitations, invalidation rules, idempotency, expected version, and audit;
- validate current state;
- preserve every attempt and conflict;
- return decision and next allowed transitions.

### Acceptance Criteria

- score alone cannot authorize decision;
- stale snapshot cannot be approved;
- no live-trading outcome exists;
- repeated commands are idempotent;
- security and integration tests pass.

## S17.30 Implement Decision Presentation

### Objective

Show outcome, scope, rationale, conditions, limitations, owner, snapshot, timing, invalidation, and audit.

### Work

- render decision separately from evidence scores;
- keep paper-only scope explicit;
- link unresolved limitations;
- show invalidated and superseded decisions;
- provide accessible definitions;
- avoid promotional language.

### Acceptance Criteria

- approval cannot be confused with live use;
- invalidated decisions remain historical;
- conditions are visible near outcome;
- no guarantee or advice language appears;
- content tests pass.

## S17.31 Implement Strategy Promotion Command

### Objective

Promote only an approved strategy to a future paper-research configuration.

### Work

- require owner/recent auth, decision/snapshot, idempotency, expected version, target configuration, dependency compatibility, no blockers, rollback conditions, confirmation, and audit;
- prevent running-experiment mutation;
- create immutable promotion record;
- update lifecycle safely;
- link preflight requirement.

### Acceptance Criteria

- promotion scope is future paper research only;
- incompatible dependencies block promotion;
- running experiments remain frozen;
- no browser or AI can infer promotion;
- tests pass.

## S17.32 Implement Strategy Activation Boundary

### Objective

Associate approved versions only with future approved configurations and preflighted experiments.

### Work

- verify strategy and configuration lifecycle;
- verify exact dependency compatibility;
- require live-trading-disabled state;
- enforce configuration governance and audit;
- prevent direct active-experiment update;
- expose activation lineage.

### Acceptance Criteria

- activation never bypasses preflight;
- no direct strategy-to-order path exists;
- active experiments cannot switch versions;
- paper-only state is persistent;
- tests pass.

## S17.33 Implement Suspension Workflow

### Objective

Block new strategy use when data, reproducibility, accounting, behavior, security, privacy, provider, risk, release, or audit evidence fails.

### Work

- define trigger codes;
- allow safety-system recommendation and authorized owner action;
- link incidents and affected configurations;
- preserve evidence and active-experiment policy;
- prevent automatic resume;
- require review for release.

### Acceptance Criteria

- suspension blocks new use immediately;
- existing experiments follow documented halt/pause policy;
- no silent resume occurs;
- trigger evidence is complete;
- tests pass.

## S17.34 Implement Rollback Workflow

### Objective

Move future paper configurations to a compatible prior approved version without rewriting history.

### Work

- persist trigger, incident, source/target versions, compatibility, active-experiment behavior, halt/pause, migration/data effects, approval, execution, verification, audit, and limitations;
- require owner and recent auth;
- preserve failed rollback attempts;
- support forward-fix when rollback unsafe;
- link release evidence.

### Acceptance Criteria

- completed experiments and portfolio evidence remain immutable;
- incompatible rollback is blocked;
- failed attempts remain visible;
- verification is mandatory;
- tests pass.

## S17.35 Implement Supersession Workflow

### Objective

Link old and new strategy versions after complete review.

### Work

- require change summary, compatibility, plan/hypothesis, evidence comparison, activation scope, prior state, migration guidance, approval, and audit;
- preserve old version access;
- prevent silent dependent configuration updates;
- link new promotion;
- expose differences.

### Acceptance Criteria

- supersession does not delete old version;
- new version has its own review;
- dependent configurations remain explicit;
- changes are traceable;
- tests pass.

## S17.36 Implement Retirement Workflow

### Objective

End future use while preserving historical review and reproducibility.

### Work

- persist reason, effective time, approval, active configuration/experiment checks, documentation impact, holds, rollback availability, final report, and audit;
- block new configurations;
- archive after retention requirements;
- preserve public methodology references safely;
- notify affected owners/operators.

### Acceptance Criteria

- retired strategy cannot enter new experiments;
- historical evidence remains accessible;
- active dependencies are handled explicitly;
- holds are preserved;
- tests pass.

## S17.37 Implement Decision Invalidation Engine

### Objective

Invalidate decisions when snapshots, data, reproducibility, incidents, governance, dependencies, reports, approvals, or variant disclosure changes.

### Work

- define invalidation rules;
- monitor authoritative events;
- create new lifecycle event without changing original decision;
- notify reviewers and owners;
- block promotion/activation;
- link incident and remediation.

### Acceptance Criteria

- original decisions remain immutable;
- material corrections invalidate scope deterministically;
- no silent revalidation occurs;
- invalidation blocks future use;
- tests pass.

## S17.38 Implement Review Evidence Holds

### Objective

Preserve datasets, runs, reports, decisions, comments, incidents, costs, and releases required for research review.

### Work

- create/release holds through Sprint 16 registry;
- map review type and lifecycle to required evidence;
- preserve rejected and suspended evidence;
- verify archive and restore;
- prevent deletion while active;
- link final retention decision.

### Acceptance Criteria

- review evidence cannot be cleaned up prematurely;
- holds are scoped and audited;
- release conditions are explicit;
- restore verification is available;
- tests pass.

## S17.39 Implement Review Audit Timeline

### Objective

Expose immutable hypothesis, plan, strategy, snapshot, reviewer, comment, score, decision, promotion, suspension, rollback, retirement, and invalidation events.

### Work

- build typed chronological timeline;
- include actor, reason, evidence, timestamp, correlation, and entity links;
- support filters and cursor pagination;
- enforce role-sensitive detail minimization;
- detect missing sequence or integrity issues.

### Acceptance Criteria

- every state change links to audit evidence;
- failed and denied commands remain visible according to role;
- ordering is deterministic;
- integrity failures are critical;
- tests pass.

## S17.40 Implement Authorized Research Review Export

### Objective

Generate provenance-preserving hypothesis, plan, evidence, score, review, decision, lifecycle, and audit packages.

### Work

- generate server-side;
- include schema/generation versions, IDs, snapshot hash, evidence hashes, timestamps, scores/definitions, comments/conflicts by authorization, decision, conditions, paper-only disclaimer, blockers, limitations, and audit;
- preserve failed variants and incidents;
- redact private reviewer and strategy details;
- include integrity manifest.

### Acceptance Criteria

- unfavorable and missing evidence cannot be omitted;
- exports identify exact snapshot;
- paper-only scope is explicit;
- secrets and private payloads are absent;
- export tests pass.

## S17.41 Add Explicit State Handling

### Objective

Define safe rendering for every hypothesis, evidence, review, decision, and lifecycle state.

### Work

- implement loading, empty, hypothesis draft, plan review, preregistered, research, incomplete/stale evidence, invalid data, contaminated final test, reproducibility mismatch, incomplete paper, accounting mismatch, incident, review pending, conflict, changes requested, approved future paper, rejected, suspended, rollback, superseded, retired, archived, invalidated, schema mismatch, unauthorized, unavailable, conflict, and export failure states;
- define bounded retry;
- distinguish missing evidence from healthy;
- label cached review revision.

### Acceptance Criteria

- positive performance never hides critical state;
- stale snapshots cannot display valid approval;
- unauthorized state leaks no review existence;
- deterministic failures are not retried infinitely;
- state tests pass.

## S17.42 Add Responsive and Accessibility Verification

### Objective

Ensure dense evidence, scores, comments, diffs, decisions, and confirmations remain usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom;
- test headings, landmarks, tables, charts and alternatives, score definitions, comments, dialogs, diffs, timelines, filters, focus, announcements, and copy controls;
- verify reduced motion and contrast;
- test long hashes, versions, parameter names, and conditions;
- record screen-reader spot checks.

### Acceptance Criteria

- no decision or score relies only on color;
- comments and evidence remain keyboard accessible;
- charts have tabular alternatives;
- context survives narrow layouts;
- no critical automated violation remains;
- manual evidence is recorded.

## S17.43 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make immutable evidence, human approval, reviewer conflicts, paper-only promotion, suspension, rollback, and no-AI authority release-blocking.

### Work

- add contract, hypothesis, plan, preregistration, strategy, dependency, lifecycle, review, snapshot, completeness, data, methodology, backtest, variants, robustness, reproducibility, paper, operations, governance, score, reviewer, conflict, comment, change request, gate, decision, promotion, activation, suspension, rollback, supersession, retirement, invalidation, hold, timeline, route, E2E, accessibility, visual, authorization, RLS, and export tests;
- add secret, evidence-deletion, hidden-variant, auto-score, AI-approval, arbitrary-execution, running-experiment mutation, Binance test, private exchange, and live-trading checks;
- instrument safe lifecycle and review-state metrics;
- test prohibited telemetry fields;
- link critical failures to release gates.

### Acceptance Criteria

- no score, model, browser, or automated process can approve or activate a strategy;
- failed and unfavorable evidence remains immutable;
- running experiments remain frozen;
- no browser or AI path gains arbitrary parameter/code/configuration, Binance test, private exchange, or live-trading authority;
- telemetry contains no prohibited fields;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Research design | Hypothesis, falsification, plan, preregistration, splits, metrics, benchmarks, robustness, stopping, hashes, and post-hoc-change tests |
| Strategy | Immutable versions, parameters, dependency compatibility, lifecycle, source, configuration, risk, execution, accounting, and environment tests |
| Evidence | Snapshot, completeness, data quality, no-look-ahead, backtests, benchmarks, variants, robustness, reproducibility, paper, incidents, operations, governance, and limitations tests |
| Scoring and review | Score definitions, missing data, no aggregate approval, reviewers, conflicts, comments, change requests, verification, notifications, and audit tests |
| Decisions and lifecycle | Owner/recent-auth, snapshot hash, gate profiles, blockers, promotion, activation boundary, suspension, rollback, supersession, retirement, invalidation, and hold tests |
| Accessibility and security | Keyboard, charts/tables, comments, dialogs, zoom, authorization, RLS, no AI authority, no evidence deletion, no arbitrary execution, no live trading, and telemetry tests |

## Sprint Exit Gate

Sprint 17 is complete only when:

- S17.1 through S17.43 are implemented and verified;
- every hypothesis is falsifiable and every material research study has a versioned preregistered plan;
- strategy versions and dependencies are immutable and complete;
- evidence snapshots are immutable and material changes invalidate decisions;
- evidence completeness remains a descriptive inventory rather than approval;
- data splits, no-look-ahead, untouched final test, benchmarks, costs, variants, robustness, reproducibility, paper experiments, accounting, operations, governance, incidents, and limitations are explicit;
- failed, rejected, cancelled, incomplete, and unfavorable evidence remains visible;
- scores are independent, versioned, explainable, and non-authoritative;
- reviewer assignments, conflicts, comments, change requests, and resolutions are auditable;
- owner decisions require recent authentication, exact snapshot hash, required reviews, no prohibited blockers, idempotency, expected version, and audit;
- promotion and activation apply only to future paper-research configurations and never mutate running experiments;
- suspension, rollback, supersession, retirement, and invalidation preserve historical evidence;
- no AI, score, browser, or automation path gains approval, promotion, activation, arbitrary parameter/code/configuration, Binance test, private exchange, or live-trading authority;
- accessibility, responsive, security, privacy, contract, research, evidence, score, review, decision, lifecycle, E2E, export, audit, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 18 defines and implements the Incident Response, Alerting, Operational Communication, Postmortem, Corrective Action, and Reliability Learning Workspace.
