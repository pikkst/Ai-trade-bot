# Database Schema

Last reviewed: 2026-08-01  
Status: Authoritative logical PostgreSQL/Supabase schema mapped to `M003–M036`; committed migrations become executable source of truth after implementation

## 1. Global Rules

- PostgreSQL is authoritative for cloud and production-research state.
- Primary keys use UUID unless an ADR approves another bounded identifier.
- Timestamps use timezone-aware UTC `timestamptz`.
- Money, price, quantity, fee, P&L, percentage, rate, cost, budget, and metric values use `numeric`; never `float` or `double precision` for authoritative values.
- Asset, currency, unit, timezone, environment, and version references are explicit.
- Used configuration, behavior-set, prompt, schema, strategy, risk, execution, accounting, dataset, approval, and release evidence is immutable.
- Ledger, audit, lifecycle transitions, incidents, approvals, corrections, and evidence histories are append-only.
- Mutable read projections are rebuildable and never replace authoritative event/ledger evidence.
- Foreign keys, unique constraints, checks, exclusion constraints, and indexes enforce invariants where practical.
- Applied migrations are immutable; schema evolution uses new additive migrations and expand-migrate-contract where needed.
- Every Data API-visible object has deny-by-default RLS and approved field exposure.
- Browser identities cannot insert/update/delete critical financial, AI, audit, experiment-control, access, incident, release, or change-management evidence.
- Deletion, anonymization, retention, and archival must not break financial, audit, incident, legal/operational hold, or reproducibility lineage.
- No table or column authorizes private Binance, Binance test orders, or live execution in M001–M036.

## 2. Master-Task Ownership

| Schema area | Master Tasks |
|---|---|
| identity, workspace, migrations, Auth/RLS, configuration | M003, M005 |
| market, features, AI, strategy/risk, execution/accounting, cycle, backtest | M007–M013 |
| API/product projections and preferences | M014–M025 |
| export/restore/security evidence | M026–M027 |
| cloud/experiment operation | M028–M029 |
| performance, datasets, research reviews, incidents, changes | M030–M034 |
| staging/release/production research | M035–M036 |

A table is not implementation-complete because it is listed here. Migrations, RLS, constraints, repositories, tests, and documentation evidence are required in the mapped Master Task.

## 3. Common Columns and Immutability

Mutable aggregate tables generally contain:

- `id uuid primary key`;
- `workspace_id uuid` where workspace-scoped;
- `created_at timestamptz not null`;
- `updated_at timestamptz not null`;
- `version bigint not null` for optimistic concurrency;
- lifecycle/status code;
- creator/last actor where applicable.

Immutable records omit `updated_at` and use append-only state transitions where state history matters.

Canonical hashes include a hash-algorithm/version field where algorithm migration may occur.

No ordinary repository exposes update/delete methods for append-only evidence.

## 4. Identity, Workspaces, and Access

### `users`

Maps application identity to Supabase Auth subject.

Fields:

- Supabase subject;
- normalized safe login/email reference according to privacy policy;
- display name;
- account state;
- provider metadata classification;
- created/disabled/locked/recovery timestamps.

Constraint: unique provider/subject. No password, token, cookie, or recovery secret is stored in ordinary application tables.

### `workspaces`

Fields:

- name;
- base currency;
- lifecycle state;
- active configuration reference;
- retention profile reference;
- archive state;
- owner summary projection.

### `workspace_memberships`

Fields:

- workspace/user;
- role (`owner`, `operator`, `viewer`);
- state;
- grant/revoke actor and reason;
- accepted/changed/revoked/expiry timestamps;
- effective-permission version.

Constraint: unique active workspace/user pair. Application invariant: at least one owner remains.

### `workspace_invitations`

Fields:

- workspace;
- target identity/address classification;
- proposed role;
- inviter;
- token digest/protected reference;
- state;
- created/expiry/accepted/declined/revoked timestamps.

Invitation tokens are never exposed in list/read models after issuance.

### `access_review_runs`

Immutable review identity, reviewer, scope, due period, outcome, findings, timestamps, and audit references.

### `access_review_findings`

Append-only findings for stale membership, privileged identity, owner invariant, denied attempts, role mismatch, or remediation.

### `permission_definitions`

Canonical permission code, resource scope, default role mapping, recent-auth requirement, version, lifecycle, and documentation/test references.

### `effective_permission_snapshots`

Immutable server-calculated actor/workspace permission evidence with rule/RLS versions, reason codes, and verification timestamp.

### `authorization_assurance_runs`

Application and RLS check set, revision, environment, outcome, mismatch count, evidence, and verification time.

### `authorization_mismatches`

Append-only mismatch category, severity, affected resource, environment, API/RLS outcomes, incident/remediation references, and timestamps.

## 5. Sessions and Security Metadata

### `session_security_events`

Immutable safe account/session events such as login failure, revocation, recent-auth requirement, lock, provider unavailable, or denied privileged action. No raw token/cookie is stored.

### `secret_inventory_items`

Metadata only:

- canonical name/purpose;
- environment;
- storage provider/classification;
- owner service;
- presence state;
- created/last rotated/rotation due;
- scope;
- exposure state;
- last verification.

No secret value, retrievable digest, or retrieval link.

### `secret_scan_runs`

Revision, tool/version, scope, result counts, status, timestamps, artifact reference, and audit.

### `secret_exposure_findings`

Append-only redacted finding, severity, source class, incident, rotation, false-positive resolution, and state.

### `secret_rotation_runs`

Trigger, incident, actor, revocation, new-credential verification, dependent-service verification, smoke tests, outcome, and timestamps. No old/new secret values.

## 6. Configuration and Behavior Sets

### `workspace_config_versions`

Immutable canonical JSON and hash plus references to:

- allowed markets/intervals;
- feature set;
- Gemini provider/model/prompt/schema/safety/validation/fallback;
- strategy;
- risk policy;
- execution/accounting model;
- schedule;
- budgets;
- benchmarks;
- retention;
- environment policy;
- code/dependency/migration versions;
- creator, lifecycle, approval, activation/archive timestamps.

Constraint: unique workspace/version and workspace/configuration hash.

### `configuration_state_transitions`

Append-only lifecycle transitions with actor, reason, expected version, validation/approval, dependent-resource checks, and audit.

### `behavior_sets`

Immutable complete behavior identity:

- configuration version;
- provider/model/prompt/schema/validation versions;
- feature/strategy/risk/execution/accounting versions;
- schedule/budget/retention versions;
- code revision;
- dependency lock hash;
- migration revision;
- canonical aggregate hash.

Constraint: unique aggregate hash. Used behavior sets are immutable.

### `configuration_dependencies`

Typed links from configuration/behavior set to experiments, backtests, reports, releases, datasets, or other versions.

## 7. Exchange and Market Data

### `exchanges`

Code, display name, data capability, active state. MVP includes Binance Spot public market data.

### `exchange_symbol_versions`

Effective version of native symbol, normalized base/quote, status, price/quantity precision, tick/step, min/max quantity, minimum notional, metadata hash, retrieved/effective timestamps.

Constraint: unique exchange/native symbol/effective version.

### `market_data_ingestions`

REST request/page identity, provider request metadata, bounded range, checkpoint, status, inserted/duplicate/invalid counts, retries, timing, safe error, cycle/job references.

### `candles`

Fields:

- exchange-symbol version;
- interval;
- open/close time;
- open/high/low/close;
- base/quote volume;
- trade count;
- finalized flag;
- ingestion/source reference;
- content hash.

Constraints:

- unique symbol/interval/open time/version policy;
- positive prices;
- high >= open/close/low;
- low <= open/close/high;
- non-negative volumes/counts;
- close after open;
- finalized required for normal downstream use.

### `data_quality_events`

Append-only event type, severity, affected candle/range/dataset, details, detection, resolution, replacement, invalidation, reviewer, and timestamps.

### `candle_corrections`

Original, replacement, source evidence, reason, effective time, dependent-artifact invalidation state. Original row remains readable.

### `market_snapshots`

Workspace, market, interval, analysis time, first/last candle, count, quality/freshness, snapshot hash, creator/cycle/job, state, invalidation/supersession.

### `market_snapshot_candles`

Exact ordered candle membership.

Constraints: unique snapshot/sequence and snapshot/candle.

## 8. Feature Engineering

### `feature_set_versions`

Name, semantic version, implementation reference, configuration JSON/hash, required history, status, approval/evaluation references.

### `feature_calculations`

Snapshot, feature-set version, idempotency key, status, input/output hashes, start/end, warnings/error, cycle/backtest reference.

Constraint: unique compatible snapshot/feature/configuration hash.

### `feature_values`

Calculation, feature code, typed numeric/string/boolean representation, unit, sequence/timestamp.

Constraint: exactly one typed value representation is populated.

## 9. Gemini and AI Analysis

### `ai_provider_config_versions`

Provider (`google_gemini` or `fake`), configured model identifier, adapter version, timeout, retry/generation settings, safety reference, budget reference, configuration hash, environment/tier classification, lifecycle. No API key.

### `ai_prompt_versions`

Purpose/agent, semantic version, system/task templates, hashes, evidence-envelope version, schema/confidence/fallback expectations, language, lifecycle, evaluation, creator/timestamps. Immutable after use.

### `ai_report_schema_versions`

Schema version, JSON Schema, hash, strictness, compatibility, lifecycle, migration notes.

### `ai_validation_policy_versions`

Parser, schema, grounding, unsupported-claim, false-certainty, injection, source-validity, and policy check versions/configuration/hash.

### `ai_analysis_runs`

Workspace, experiment/cycle/backtest, snapshot, feature calculation, provider/prompt/schema/validation versions, logical request/idempotency key, status, timing, terminal provider/validation/fallback outcome, usage/cost summary, safety/refusal state, safe error.

Constraint: deterministic request/idempotency identity unique within scope.

### `ai_provider_attempts`

Run, attempt sequence/ID, provider request/response IDs where safe, outcome, retry eligibility, latency, usage, cost estimate, timing, safe diagnostics.

### `ai_reports`

Accepted validated structured report JSON plus regime, advisory action, analytical confidence, report hash, schema/version, validation reference. Only accepted reports may be consumed as AI evidence.

### `ai_report_validations`

Immutable validation run and individual check references, outcome, reason codes, validator versions, timestamp.

### `ai_validation_checks`

Canonical check code/category/severity, input/field/claim, outcome, safe explanation, source evidence, timestamp.

### `ai_budget_periods`

Workspace/provider/configuration/period, request/token/cost budgets, reserved, committed, remaining, source/estimate classification, status.

Transaction-safe reservation prevents concurrent overrun.

### `ai_evaluation_runs` and `ai_evaluation_cases`

Candidate/baseline behavior versions, evaluation dataset, repeated runs, metrics, cases, outcomes, warnings, approvals, and evidence hashes.

## 10. Strategy and Risk

### `strategy_versions`

Name, semantic version, implementation/configuration hash, supported market/interval, Gemini dependency policy, lifecycle, evaluation/review/approval references.

### `strategy_evaluations`

Snapshot, features, optional accepted AI report, strategy, exact portfolio-state version, action, direction, requested exposure/notional boundary, reason codes, evidence/contradictions, evaluation hash, cycle/backtest reference, timestamp.

Immutable and deterministic for identical referenced inputs.

### `risk_policy_versions`

Workspace, semantic version, limits/rules JSON, hash, lifecycle, approval, activation/archive timestamps.

### `risk_evaluations`

Strategy evaluation, policy, portfolio-state version, market snapshot, outcome, approved quantity/notional, rule results, reason codes, evaluation hash, cycle/backtest reference, timestamp.

Constraint: one canonical evaluation per intent/policy/portfolio-state identity unless explicitly re-evaluated against new state.

### `risk_rule_results`

Risk evaluation, rule code/version, inputs/reference, threshold, outcome, approved adjustment, reason.

### `trading_halts`

Workspace/portfolio/experiment scope, source (`manual`, `risk`, `reconciliation`, `integrity`, `security`, `incident`), reason, details, activation, actor/source, review/resolution links, terminal state.

Halt history is append-only. No generic deletion/clear.

### `halt_state_transitions`

Append-only review/acknowledgement/scope/resolution transitions.

## 11. Paper Execution and Portfolio

### `paper_portfolios`

Workspace, experiment, base currency, execution/accounting/risk versions, state, current state version, start/end, halt reference, live-disabled assertion.

### `portfolio_funding_transactions`

Immutable virtual funding transaction identity, amount/currency, reason, approval, ledger transaction, timestamp.

### `paper_orders`

Portfolio, approved risk evaluation, idempotency/client key, symbol, side, type, requested/approved/rounded quantity/notional, limit price, time in force, execution-model version, state, timestamps, terminal reason.

Constraints:

- unique portfolio/idempotency key;
- at most one canonical order per approved risk evaluation;
- positive quantity/notional;
- limit price only/required according to type;
- no short/leverage capability.

### `paper_order_state_transitions`

Append-only from/to state, source/actor, reason, timestamp, correlation/cycle.

### `paper_reservations`

Order, asset/currency, category (notional, fee, buffer, asset), amount, consumed/released amounts, state, timestamps, accounting/ledger references.

### `paper_fills`

Order, fill sequence, quantity, reference/fill price, gross notional, spread/slippage, fee amount/asset, net effect, eligible market event, execution-model version, timestamp, ledger transaction, resulting order state.

Constraints: unique order/sequence; cumulative fill never exceeds approval.

### `ledger_transactions`

Portfolio, immutable transaction ID, transaction type, business reference, accounting-policy version, effective/created time, correction lineage, cycle/backtest/experiment references.

### `ledger_entries`

Transaction, portfolio sequence, account code, asset/currency, debit, credit, reference type/ID.

Constraints:

- exactly one positive debit or credit per row;
- non-negative amounts;
- unique portfolio sequence;
- transaction balances by accounting unit through application/database verification;
- no update/delete ordinary path.

### `portfolio_state_versions`

Immutable reconciled projection snapshot: portfolio, version, last ledger sequence, cash/reserved balances, positions summary, equity, realized/unrealized P&L, fees, exposure, drawdown, valuation/accounting versions, state hash, predecessor, timestamp, reconciliation state.

### `positions`

Current rebuildable projection keyed by portfolio and asset/symbol. Not financial source of truth.

### `position_lots` or `position_cost_basis_records`

Used only if selected accounting policy requires lot-level evidence. Immutable/rebuildable relationship to fills/ledger.

### `reconciliation_runs`

Portfolio, compared state, ledger range, expected/actual hashes, check results, outcome (`matched`, `mismatch`, `unable_to_reconcile`), mismatch details, halt, rebuild comparison, timing.

### `reconciliation_checks`

Canonical check code for balances, reservations, orders, fills, positions, fees, P&L, state hash, ledger sequence, evidence availability, and outcome.

### `portfolio_rebuild_runs`

Source ledger range, accounting/valuation versions, prior/rebuilt state hashes, differences, outcome, timing. Rebuild does not rewrite ledger.

## 12. Research Cycles and Scheduling

### `research_cycles`

Experiment/workspace, stable occurrence key, intended time, actual start/finish, delay classification, workflow run/attempt, source revision/dependency/migration/configuration hashes, status, completeness, validity, safe terminal error, lock/idempotency summaries, market/AI/risk/accounting/reconciliation references.

Constraint: unique experiment/occurrence key.

### `research_cycle_attempts`

Canonical cycle, workflow attempt, command version, start/end, outcome, duplicate/deduplication relationship, safe diagnostics.

### `research_cycle_stages`

Cycle, canonical stage ID, sequence, start/end/duration, outcome, retries, dependency, evidence references, skipped/unavailable reason.

Constraints: deterministic cycle/sequence and required-stage policy.

### `cycle_locks`

Cycle/occurrence, lock type/key, attempt, outcome, safe owner reference, acquisition/expiry/release, competing cycle, diagnostics.

### `idempotency_records`

Scope, key, command/side-effect type, request hash, canonical resource/result, status, created/expiry, conflict evidence.

Sensitive request payloads are not stored unrestricted.

### `background_jobs`

Queue/job identity for approved asynchronous work, type, idempotency, workspace, status, attempts, limits, timing, progress work units, result resource, safe error. A job does not replace domain completion evidence.

### `outbox_events`

Aggregate, event type/schema, payload/reference, created/published time, attempts, safe error, ordering/idempotency. Used where reliable post-commit publication matters.

## 13. Backtesting and Benchmarks

### `execution_model_versions`

Versioned fee, spread, slippage, precision, partial-fill, participation, intrabar, timing, time-in-force, minimum-notional, deterministic-seed rules and hash.

### `accounting_policy_versions`

Cost-basis, valuation, P&L, fee, rounding, account mapping, correction, and reconciliation rules plus hash/lifecycle.

### `benchmark_definition_versions`

Cash, buy-and-hold, or approved benchmark timing/cost/valuation/precision rules and hash.

### `backtest_runs`

Workspace, immutable configuration/behavior set, dataset/range/market, initial capital, strategy/risk/execution/accounting/benchmark versions, Gemini mode, status/progress/completeness, code commit, dependency/migration/data hashes, seed, timing, safe error, report hash.

### `backtest_events`

Ordered replay events or immutable references required for deterministic audit/replay.

### `backtest_metrics`

Run, canonical metric code/version, numeric value or null, unit, period, sample count, definition assumptions, warning/null reason.

### `backtest_series`

Series metadata, sampling, unit, hash, gap/downsampling policy, protected artifact/data references.

### `backtest_trades`

Trade episode identity, entry/exit references, quantities, prices, gross/net P&L, fees/costs, holding period, state, complete lineage.

### `backtest_comparisons`

Primary/candidate runs, compatibility, configuration/dataset/metric/series/trade/robustness differences, warnings, hash.

### `backtest_reproducibility_runs`

Original/repeated run, manifest, report/event/state hashes, outcome, differences, timing.

## 14. Experiments and Preflight

### `experiments`

Workspace, name/type, environment, paper mode, lifecycle, frozen configuration/behavior set, portfolio, virtual starting capital, planned/actual period, cadence, owner/approval, report, active halt/incident, archive state.

### `experiment_state_transitions`

Append-only from/to, actor/source, reason, timestamp, correlation/request, preflight/incident/halt/report references.

### `experiment_preflight_runs`

Experiment, configuration hash, run identity, checks, outcome (`passed`, `failed`, `blocked`, `expired`), blockers/warnings, approval, expiry, timing.

### `experiment_preflight_checks`

Canonical check code/domain/severity, outcome, evidence, safe explanation, affected gate.

### `experiment_reports`

Current/final report metadata, metrics/benchmark/artifact references, generation version, hash, status, limitations.

## 15. Incidents, Communications, and Corrective Actions

### `incidents`

Workspace/environment, type, severity, title/safe summary, state, detected/declared timestamps, commander/owner, affected services/resources, customer/data/financial/security impact, halt/release references, source revision, resolution classification.

### `incident_state_transitions`

Append-only detected, acknowledged, triaged, contained, service restored, integrity verified, resolved, closed transitions with actor/source, reason, timestamp, evidence.

### `incident_timeline_events`

Chronological safe event, source, category, affected resources, correlation, evidence links.

### `incident_evidence`

Typed protected references to logs, audit, cycles, data, AI, financial, export/restore, security, deployment, or communication evidence with hash/classification.

### `incident_communications`

Audience, channel, approved safe content/reference, status, author/approver, publication/update timestamps, privacy/security classification.

### `postmortems`

Incident, immutable version, timeline, impact, detection, contributing/systemic factors, what worked/failed, lessons, reviewer/approval, hash, publication visibility.

### `corrective_actions`

Postmortem/incident, action type, owner, priority, due/expiry, state, task/change/release links, completion evidence.

### `corrective_action_verifications`

Action, verifier, method, evidence, effectiveness outcome, observation window, timestamp.

## 16. Data Governance and Lifecycle

### `dataset_versions`

Dataset identity/class, source/market/range, schema version, manifest/hash, lifecycle, quality state, environment, owner, created/approved/archive timestamps.

### `dataset_manifest_items`

Ordered source partitions/files/records with hashes, counts, ranges, metadata versions, correction state.

### `data_lineage_edges`

Typed source/target resource, relationship, transformation/version, created time, invalidation/supersession state.

Constraint: no unauthorized cross-workspace relation exposure; cycles in lineage graph are validated by relationship policy.

### `data_quality_gate_runs`

Dataset/resource, gate version, checks, outcome, quarantine/approval, actor, timing.

### `data_retention_policy_versions`

Data class, environment, retention period, archive/delete/anonymize behavior, hold precedence, approval, lifecycle, hash.

### `data_holds`

Scope/resource/class, hold type/reason, authority/owner, start/expiry/release, state, audit.

### `archive_runs` and `restore_runs`

Scope, source/target environment, revision, migration head, hashes, storage classification, timing, outcome, verification/rebuild/reconciliation, limitations.

### `deletion_reviews` and `anonymization_runs`

Requested scope, dependency analysis, holds, legal/operational/financial/reproducibility blockers, approval, expected version, result, evidence. Authoritative financial/audit evidence is preserved or pseudonymized according to approved policy rather than silently deleted.

## 17. Research Review and Strategy Lifecycle

### `research_hypotheses`

Question, rationale, expected mechanism, non-goals, prior evidence, owner, version/hash, lifecycle.

### `research_test_plans`

Hypothesis, datasets/splits, metrics/benchmarks, variants, thresholds, robustness/walk-forward/paper-observation plan, stop conditions, budget, owners/reviewers, immutable plan hash.

### `research_reviews`

Strategy/change scope, exact evidence snapshot, status, findings, limitations, recommendation, reviewer conflicts, owner decision.

### `research_evidence_items`

Review, evidence type/resource/hash, required/optional status, freshness/compatibility/outcome, limitation.

### `research_variant_records`

Selected/rejected/failed/cancelled/incomplete variants, parameter/configuration behavior set, purpose, result, selection relationship.

### `research_reviewer_assignments` and `reviewer_conflicts`

Role, expertise, scope, due date, acceptance, conflict declaration/resolution, audit.

### `research_approval_snapshots`

Immutable review/hypothesis/test plan/datasets/results/variants/robustness/reproducibility/paper observation/risk/cost/limitations/reviewer set and snapshot hash.

### `strategy_lifecycle_transitions`

Append-only draft, tested, backtested, validated, observation, paper candidate, active paper, rollback, retired, archived transitions. No live state.

## 18. Change Management and Rollout

### `change_proposals`

Workspace/scope, title, problem/rationale/outcome/non-goals, before/after behavior sets, categories, owner/authors, target window, urgency/emergency, lifecycle, source task/ADR/incident/release links.

### `change_state_transitions`

Append-only lifecycle transition, actor, reason, expected version, approval/evidence, timestamp.

### `change_classifications`

Dimension-level financial/risk/execution/data/AI/security/privacy/migration/reliability/cost/accessibility/content/reversibility/scope/uncertainty result and final class.

### `change_diffs`

Field path, category, before/after or redacted metadata state, materiality, compatibility, security/privacy class, required evaluation, affected resources.

### `change_dependencies`

Direct/transitive resource relationship, active/historical/planned/required/optional/unknown state, impact.

### `compatibility_reviews`

Schema/API/event/database/configuration/dataset/report/domain/frontend/provider/rollback/historical-readability outcomes and evidence.

### `change_evidence_plans` and `change_evidence_items`

Immutable required profile, environments, datasets, thresholds, stop conditions, budgets, owners/reviewers, results, freshness/compatibility/outcome.

### `change_approval_snapshots` and `change_approvals`

Immutable complete decision snapshot/hash and actor decision. Material change invalidates prior approval.

### `rollout_plans`

Approval snapshot, target environments/configurations, stages, canary design, entry/exit/stop gates, owners, schedule, rollback/forward-fix, maintenance notices.

### `rollout_stages`, `paper_canary_runs`, and `rollout_observations`

Append-only stage lifecycle, bounded paper scope, baselines, metrics/evidence, stop-condition evaluations, incidents, ledger/reconciliation, outcome.

### `change_freezes`, `emergency_changes`, and `deprecations`

Freeze window/scope/exceptions; emergency containment/expiry/retrospective review; deprecated version/support/usage/removal gates. No live-trading activation state.

## 19. Governance, Security, Privacy, and Releases

### `security_findings`

Finding code/source/category/severity, affected environment/resource/revision, evidence, remediation, exception, incident, state, timestamps.

### `security_exceptions`

Finding, owner approval, rationale, compensating controls, expiry, review, state. Critical exceptions follow policy.

### `privacy_assessments`

Environment/feature/provider, data classes/purposes, transfer/region/terms, retention, rights workflows, findings, approvals, review dates.

### `migration_assurance_runs`

Migration set/commit, source/target revision, clean reset, upgrade, drift, RLS/index, rehearsal, compatibility, backup/restore prerequisites, outcome.

### `release_candidates`

Target environment, source commit, backend/frontend/artifact/dependency/OpenAPI/SBOM/configuration/behavior-set/migration references, lifecycle, blockers, outcome.

### `release_gate_results`

Canonical gate code/version, category, severity, evidence, outcome, exemption, timestamp.

### `release_approvals`

Release, immutable approval snapshot/hash, actor, role, decision, reason, timestamp, invalidation state.

### `deployment_runs`

Release/environment, migration/deploy steps, start/end, artifact hashes, outcome, safe errors, smoke/Auth/RLS/reconciliation references.

### `rollback_runs`

Deployment/release, trigger, target artifact/schema compatibility, actor/approval, steps, outcome, post-rollback verification.

## 20. Product Shell, Preferences, Notifications, and Help

### `user_preferences`

User, locale, timezone, display/accessibility preferences, version. No authoritative financial or permission settings.

### `saved_views`

User/workspace, canonical route/filter/sort/column/display state, compatibility version, visibility, timestamps. No secrets or calculations.

### `recent_items`

User, resource type/ID, safe label, route, last viewed, status/availability. Revoked resources are removed safely.

### `onboarding_progress`

User/workspace/role, onboarding version, stage states, acknowledgement versions/locales, timestamps, reset state.

### `notifications`

User/workspace, source resource/event, category/severity, safe content key/parameters, awareness/review/action classification, created/read/expired state.

Notification read state never mutates source evidence.

### `notification_preferences`

User/channel/category/severity preferences within server-enforced mandatory critical-notice policy.

### `help_content_versions`, `glossary_terms`, and `trust_content_versions`

Canonical localized content keys, versions, status, semantic-equivalence review, source documents, visibility, hashes.

## 21. Developer Portal and Documentation Evidence

### `documentation_registry`

Stable document ID/path/title/category/authority/status/version/owner/review dates/supersession/visibility/language/hash/freshness and related IDs.

### `documentation_health_runs`

Revision, broken links, stale docs, conflicts, generated drift, terminology findings, coverage, outcome.

### `requirement_registry`

Stable requirement ID/source/text hash/category/priority/owner/status/supersession and task/test/release links.

### `task_registry`

Master/detailed task IDs, source, acceptance hashes, dependencies, status, implementation/tests/docs/commit evidence, limitations.

### `adr_registry`

ADR ID/version/status/context/decision/consequences/supersession and dependency links.

### `api_operation_registry`, `schema_registry`, `error_code_registry`, `event_registry`, `permission_registry`, `metric_registry`

Generated/versioned implementation evidence with source, tests, compatibility, hashes, lifecycle.

### `test_runs`, `test_results`, `invariant_results`, and `scan_runs`

Revision/environment/configuration, commands/tools, outcome, coverage/evidence, artifacts, failures/flakes/exceptions.

### `runbook_versions` and `runbook_executions`

Runbook identity/version/owner/prerequisites/safety/steps/validation/recovery/review plus execution/drill evidence.

### `generated_artifact_manifest`

Artifact type/path/source revision/generator/version/command/hash/drift/status.

## 22. Performance, SLO, Quota, Cost, and Capacity

### `metric_definitions`

Canonical name/version/type/unit/description/source/labels/cardinality/privacy/environments/retention/tests/lifecycle.

### `sli_definitions`

Stable ID/version, numerator/denominator or aggregation, sources, inclusion/failure rules, unit, window, sampling, owner, tests, limitations.

### `slo_versions`

SLI, target, objective type, environment, window semantics, exclusions, error-budget/alert policy, owner/approval, lifecycle.

### `slo_measurements` and `error_budget_snapshots`

Window, source revision, result, sample adequacy, compliance, allowed/consumed/remaining budget, burn rates, incidents/exclusions, calculation version.

### `performance_measurements`

Environment/revision/service/operation/stage, metric definition, source quality, window, sample count, aggregate/value, units, cold/warm/synthetic/provider classification, limitations.

### `provider_quota_snapshots`

Provider/service/resource, safe scope, limit/usage/remaining/reset, source classification, observation/freshness/confidence, thresholds, state. No credentials.

### `cost_records`, `cost_allocations`, `budget_versions`, `cost_anomalies`, and `cost_forecasts`

Billed/estimated/free-allowance/configured classification, provider/environment/workspace/experiment/cycle/analysis/backtest/export allocation, pricing-reference version, currency, period, uncertainty, state.

### `capacity_snapshots` and `capacity_forecasts`

Database/API/frontend/workflow/backtest/provider resource, measured/configured/provider source, current/limit/headroom, growth, forecast, uncertainty, trigger evaluation.

### `resilience_test_runs`

Test profile/version, environment/revision/configuration, load/failure scenario, entry/stop/safety conditions, result, recovery, incidents, artifacts, limitations.

No table triggers automatic provider purchase, plan upgrade, scaling, or budget increase.

## 23. Audit

### `audit_events`

Append-only fields:

- workspace/environment;
- actor type/ID;
- event type/schema version;
- entity type/ID;
- correlation/request/cycle/experiment/job/release/change IDs;
- outcome, reason/error codes;
- safe bounded details;
- created time;
- optional integrity-chain metadata/version.

Indexed by workspace/time, entity, actor, event type, outcome, and correlation/cycle.

Audit cleanup follows retention/hold policy and never breaks required legal, financial, incident, release, or reproducibility lineage.

## 24. Exports and Restore

### `export_runs`

Environment/workspace/scope, source revision, migration head, configuration/behavior-set references, start/end, record/artifact counts, protected storage classification/reference, encryption state, hash, outcome, safe error, audit.

### `restore_runs`

Export, isolated target, source/target revisions, migration result, row/hash checks, portfolio rebuild, reconciliation, duration, outcome, limitations, incident/runbook/audit references.

### `recovery_runs`

Incident/resource, runbook version, actor/approval, expected version, steps, outcome, post-recovery Auth/RLS/data/ledger/reconciliation/smoke verification.

## 25. Retention, Archive, Deletion, and Legal Holds

Default design values are not legal guarantees and require versioned policy/review:

- validated market data, snapshots used for decisions, strategy/risk decisions, fills, ledger, portfolio-state/reconciliation, experiment lifecycle, approvals, release/change/audit evidence: long-term/indefinite project history unless approved policy permits otherwise;
- raw Gemini/provider content: minimized and bounded, while validated report and lineage remain;
- operational logs: environment-specific bounded retention;
- failed transient payloads/artifacts: bounded retention according to sensitivity;
- personal account/profile data: minimized and handled through approved access/export/correction/deletion policy;
- secrets: never stored in ordinary database tables.

Active hold precedence:

1. legal/regulatory requirement where applicable;
2. financial/audit/integrity evidence requirement;
3. active incident/security investigation;
4. reproducibility/experiment/release requirement;
5. ordinary retention cleanup.

Cleanup is idempotent and auditable. Archive/restore preserves hashes, manifests, dependencies, and reconciliation.

## 26. Index Requirements

At minimum:

- users by provider/subject and safe normalized identifier;
- memberships by workspace/user/state and role;
- configurations/behavior sets by workspace/version/hash/lifecycle;
- candles by symbol/interval/open time/finalized state;
- snapshots by workspace/market/analysis time/hash;
- feature/analysis/strategy/risk records by source IDs/status/time;
- orders by portfolio/state/time/idempotency/risk evaluation;
- fills by order/sequence/time;
- ledger by portfolio sequence, transaction, business reference, effective time;
- portfolio states/reconciliations by portfolio/version/time/outcome;
- cycles by experiment/occurrence/status/intended/actual time;
- backtests by workspace/status/market/range/strategy/time;
- experiments by workspace/state/period/configuration;
- incidents by environment/workspace/state/severity/time;
- datasets/lineage by class/lifecycle/hash/source/target;
- research reviews/approvals by strategy/status/time/snapshot hash;
- changes/rollouts by state/risk/category/window/behavior hash;
- audit by workspace/time/entity/actor/event/outcome;
- releases/deployments by environment/state/revision/time;
- metrics/SLO/cost/quota/capacity by environment/definition/window/source;
- notifications/preferences/recent views by user/state/time;
- documentation/tasks/tests/runbooks by stable ID/revision/status.

Indexes must not expose secret or unbounded sensitive values and must be verified against actual query plans in M030/M035.

## 27. RLS and Role Requirements

Every Data API-visible table/view defines policies for:

- anonymous/public demo where explicitly approved;
- viewer;
- operator;
- owner;
- application/workflow service;
- read-only operations;
- migration identity where applicable.

Requirements:

- workspace isolation;
- deny by default;
- approved read-only views;
- no browser critical writes;
- privacy-minimized columns;
- archived/revoked resource behavior;
- claim mapping version;
- tests and assurance run reference.

RLS policy changes use migrations and M034 governance when material.

## 28. Migration and Compatibility Requirements

- one committed migration chain/head;
- no editing applied migration files;
- deterministic reset and seed;
- supported upgrade paths;
- expand-migrate-contract for breaking/destructive evolution;
- schema/RLS/index/function/view drift detection;
- staging rehearsal;
- production controlled single execution;
- application rollback or forward-fix compatibility;
- backup/export/restore prerequisite for destructive risk;
- generated schema/OpenAPI/documentation update in the same change.

## 29. Prohibited Schema Patterns

- binary floating-point authoritative financial columns;
- mutable ledger balance as sole financial truth;
- update/delete ordinary paths for fills, ledger, audit, approvals, incidents, used versions, or lifecycle transitions;
- secret values or usable secret hashes in ordinary metadata/read models;
- private Binance credential/order tables in M001–M036;
- live-trading activation columns or states;
- generic bypass/override flags for risk, halt, reconciliation, Auth, RLS, incident, approval, or release controls;
- unversioned JSON blobs that silently change behavior;
- environment-variable values copied into browser-visible configuration tables;
- cascading deletion that breaks required lineage;
- provider SDK objects serialized as public/domain contracts.

## 30. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `PRODUCT_REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `API_SPECIFICATION.md`
- `SECURITY.md`
- `OBSERVABILITY.md`
- `DATA_LIFECYCLE_DATASET_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
- `RESEARCH_REVIEW_STRATEGY_LIFECYCLE_WORKSPACE_IMPLEMENTATION.md`
- `INCIDENT_RESPONSE_POSTMORTEM_LEARNING_WORKSPACE_IMPLEMENTATION.md`
- `CHANGE_MANAGEMENT_ROLLOUT_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
