# Observability

Last reviewed: 2026-08-01  
Status: Authoritative observability and operational-evidence contract mapped to `M005`, `M012`, `M022`, `M029`, and `M030`

## 1. Objectives

Observability must prove whether The Daily Roast AI is operating safely and completely, not merely whether a process is running.

An owner, operator, engineer, or reviewer must be able to determine:

- which environment, revision, deployment, configuration, and behavior set produced an event;
- whether market evidence is finalized, complete, approved, and fresh;
- whether Gemini was attempted, accepted, rejected, blocked, unavailable, or bypassed by deterministic fallback;
- whether strategy and deterministic risk completed;
- whether any paper order/fill/ledger effect occurred atomically;
- whether portfolio state reconciles to the append-only ledger;
- whether a cycle was intended, delayed, started, duplicated, skipped, partial, failed, recovered, or complete;
- whether an experiment, workspace, portfolio, release, or behavior change is blocked or halted;
- whether export, restore, incident, and recovery evidence is current;
- whether provider quota, cost, capacity, and SLO evidence is measured, stale, estimated, or unavailable.

Profit, return, win rate, or outperformance is not an operational health metric or SLO.

## 2. Master-Task Ownership

| Observability capability | Master Tasks |
|---|---|
| structured logging, correlation, safe errors, health foundations | M005 |
| one-shot cycle and stage evidence | M012 |
| API/product status and experiment operations | M014, M016, M022 |
| integrated validation and recovery drills | M026–M027 |
| free-cloud operational evidence and experiment monitoring | M028–M029 |
| SLI/SLO/error budget, performance, capacity, quota, cost, resilience | M030 |
| data, research, incident, and behavior-change evidence | M031–M034 |
| staging and production-research monitoring | M035–M036 |

No documentation or UI may claim an observability capability is complete before its mapped Master Task is verified.

## 3. Evidence Classes

Observability data is classified as:

- **durable domain evidence** — authoritative persisted records used for audit, financial integrity, lifecycle, approval, or reproducibility;
- **structured operational logs** — bounded diagnostic events that may be provider-retained and are not the sole audit source;
- **application metrics** — aggregate measurements with bounded labels and versioned definitions;
- **provider-reported evidence** — dashboard/API/status information from Supabase, Render, Cloudflare, GitHub, Binance, or Gemini;
- **synthetic test evidence** — controlled load, cold-start, resilience, or recovery results;
- **estimated evidence** — derived cost, quota, capacity, or forecast values explicitly labeled as estimates;
- **unavailable evidence** — required data that could not be collected and must never appear healthy by default.

Logs and metrics do not replace immutable business, accounting, incident, approval, or release records.

## 4. Active Free-Cloud Signal Sources

The M028–M029 free profile uses:

- structured JSON logs from FastAPI and the one-shot CLI;
- GitHub Actions run history, logs, and safe diagnostic artifacts;
- Render application, deploy, health, and cold-start logs;
- Supabase database/Auth operational logs and approved provider evidence;
- persistent `research_cycles` and cycle-stage records;
- immutable audit events;
- data-quality and correction events;
- Gemini attempts, validation, usage, budget, and fallback records;
- strategy/risk/order/fill/ledger/state/reconciliation records;
- experiment lifecycle, halt, incident, export, restore, and report records;
- frontend global safety/status projections.

Hosted Prometheus, Grafana, and OpenTelemetry backends are deferred. They must not be represented as implemented or required for M028/M029.

## 5. Correlation and Context Contract

Every material log or durable event includes the applicable bounded context:

- UTC timestamp;
- service/component;
- environment;
- source revision and deployment ID;
- workspace ID;
- experiment ID;
- logical occurrence/cycle ID;
- request/correlation ID;
- job/workflow run and attempt reference where available;
- actor type and actor ID for commands;
- entity type and safe entity ID;
- operation or stage ID;
- outcome and stable error/reason code;
- duration where meaningful;
- configuration and behavior-set references where material.

Identifiers must not become unbounded metric labels. Logs and traces use redaction and access controls appropriate to their classification.

## 6. Persistent Research-Cycle Contract

Every logical cycle stores:

- immutable cycle ID;
- experiment/workspace/environment;
- stable occurrence and idempotency keys;
- intended schedule time;
- actual start and finish times;
- delay and tolerance classification;
- source revision, dependency lock, migration revision, and configuration hash;
- GitHub workflow run/attempt identifiers where available;
- lock or lease type, key, attempt, acquisition, rejection, expiry, release, and competing cycle reference;
- status, completeness, validity, and terminal reason;
- processed/eligible work units where defined;
- market freshness and quality outcome;
- Gemini/provider/validation/fallback/budget outcome;
- strategy and risk outcome;
- order, fill, reservation, ledger, portfolio-state, reconciliation, and halt references;
- incident, audit, export, and report references;
- safe summary and limitations.

A process exit code is operational evidence only. A financial cycle is complete only when all required stages and final reconciliation satisfy the frozen policy.

## 7. Cycle Stage Evidence

Canonical stage IDs include:

1. configuration load and compatibility;
2. lock/lease acquisition;
3. provider server-time lookup;
4. symbol metadata refresh when due;
5. candle fetch;
6. gap detection and repair;
7. data-quality and freshness decision;
8. immutable snapshot creation;
9. feature calculation;
10. Gemini budget reservation/check;
11. Gemini request attempts;
12. parsing and application validation;
13. deterministic fallback selection when required;
14. strategy evaluation;
15. risk evaluation;
16. reservation/order processing;
17. paper execution/fills;
18. atomic ledger/audit/outbox posting;
19. portfolio projection or rebuild;
20. reconciliation;
21. halt/incident creation when applicable;
22. audit closure and cycle completion;
23. lock/lease release.

Each stage records start, finish, duration, outcome, retry count, dependency/source, evidence references, and skipped/unavailable reason.

Stage durations must reconcile with total cycle duration within documented orchestration overhead.

## 8. Cycle Status Semantics

Supported states include:

- expected;
- queued or waiting;
- started;
- running;
- completed;
- completed with warning;
- safely skipped;
- delayed;
- missed;
- duplicate attempt;
- lock rejected;
- partial;
- failed;
- timed out;
- cancelled;
- recovered;
- invalidated;
- unable to determine.

Rules:

- intended and actual times remain distinct;
- a duplicate/lock-rejected attempt cannot be counted as a completed canonical cycle;
- a missed cycle never creates imagined trades;
- an invalidated or unreconciled cycle cannot be successful;
- recovered state preserves the original failure evidence;
- unknown or missing required evidence fails closed.

## 9. Required Frontend Status

The authenticated shell and relevant workspaces display server-authoritative:

- environment and product mode;
- explicit paper/simulation and live-trading-disabled state;
- source revision/deployment where appropriate;
- current experiment lifecycle and frozen configuration;
- latest attempted and latest successful cycle;
- next expected occurrence as an estimate, not a guarantee;
- latest finalized candle and freshness/quality state;
- Gemini provider, validation, fallback, and budget state;
- strategy and deterministic risk status;
- workspace/portfolio halt;
- ledger/reconciliation/integrity state;
- active critical incident or governance/release blocker;
- export/restore freshness where relevant;
- Render cold-start/loading state;
- status observation timestamp and stale/partial/unavailable classification.

Critical security, financial-integrity, reconciliation, halt, invalid experiment, RLS, stale-data, or incident state outranks positive performance.

## 10. Health Endpoints

### `/health/live`

Reports process responsiveness only.

It must not imply:

- database readiness;
- valid migrations;
- schedule health;
- provider health;
- financial integrity;
- complete/reconciled cycle state.

### `/health/ready`

Checks the dependencies required for the specific process to accept work, including as applicable:

- typed configuration validation;
- database connectivity;
- expected migration head;
- required Auth verification configuration;
- mandatory application dependencies;
- absence of unrecoverable startup/safety configuration.

Readiness does not claim experiment or provider health; those use domain/operations projections.

Render sleeping is not a cycle failure because the schedule is independent.

## 11. Structured Logging

Required bounded fields include:

- timestamp;
- level;
- service/component;
- environment and revision;
- event/operation/stage;
- correlation/request/cycle/experiment IDs as applicable;
- safe entity type/ID;
- outcome;
- duration;
- stable error/reason code.

Logs must be machine-readable JSON in cloud/production profiles. Pretty local rendering is optional.

Never log:

- passwords, password hashes, recovery tokens, cookies, or authorization headers;
- JWTs, API keys, service-role keys, database credentials, connection URLs, exchange signatures, or signing material;
- raw Gemini prompt bodies or unrestricted provider responses;
- personal data not explicitly approved for operational evidence;
- raw SQL values;
- secret-bearing environment dumps;
- unbounded arbitrary user or provider text as labels.

## 12. Key Durable Events

At minimum:

- application startup/readiness/shutdown;
- authentication, authorization, recent-authentication, RLS assurance, and denied privileged attempts;
- cycle expected/started/lock acquired/rejected/completed/failed/recovered;
- market fetch, gap, stale, invalid, correction, snapshot, and feature outcomes;
- Gemini budget check, request attempts, provider outcomes, validation, usage, fallback, and report acceptance/rejection;
- strategy intent and deterministic risk outcome;
- order, reservation, fill, fee, cancellation, ledger, state-version, rebuild, and reconciliation transitions;
- experiment preflight/start/pause/halt/resume/completion;
- incident creation, acknowledgement, containment, restoration, integrity verification, resolution, postmortem, and corrective-action verification;
- export, backup, restore, recovery, and verification;
- configuration, access, migration, release, deployment, rollback, and behavior-change transitions;
- documentation/generated-artifact drift and critical release-gate results.

## 13. Critical Conditions

Critical conditions include:

- ledger posting failure or imbalance;
- reconciliation mismatch or inability to reconcile;
- duplicate financial side-effect suspicion;
- negative or impossible balance/position under the active policy;
- database/migration integrity failure;
- Auth/RLS mismatch or service-role exposure;
- confirmed/suspected secret exposure;
- active risk, integrity, security, privacy, or experiment halt;
- missing required financial/cycle lineage;
- invalid frozen configuration or behavior-set drift;
- failed restore or corrupted backup/export evidence;
- unapproved live/private execution flag or path;
- exhausted zero-tolerance invariant.

Critical conditions remain visible until reviewed and resolved through the appropriate incident/governance process.

## 14. Warning Conditions

Warnings include:

- delayed or missed cycle;
- stale/incomplete market evidence;
- repeated workflow or provider failure;
- Gemini quota/rate-limit/schema/safety/grounding failure trend;
- API cold start or latency regression;
- database/storage/connection capacity warning;
- provider quota/term/pricing snapshot stale or changed;
- export cadence missed;
- documentation, runbook, test, generated-artifact, or access-review staleness;
- SLO error-budget burn;
- cost anomaly or forecast uncertainty;
- expiring exception, credential rotation, or maintenance window.

Warnings must state affected outputs and limitations. They cannot silently become healthy because no new sample exists.

## 15. Incident Integration

Observability creates or links incident evidence according to versioned routing policy.

Incident states remain distinct:

- alert detected;
- acknowledged;
- triaged;
- contained;
- service restored;
- financial/data/security integrity verified;
- resolved;
- postmortem/corrective action pending or complete.

Service restoration never automatically clears an unresolved ledger, reconciliation, security, RLS, data, or experiment halt.

## 16. Export, Restore, and Recovery Evidence

Required durable evidence includes:

- export/backup identity, scope, environment, source revision, migration head, time, hash, encryption/protected-storage classification, and outcome;
- restore target, start/finish, migration result, row/evidence checks, projection rebuild, ledger reconciliation, limitations, and outcome;
- recovery command/runbook, actor, incident, expected version, audit references, and post-recovery checks.

A backup-success log without successful restore/reconciliation evidence is insufficient.

## 17. M030 Metrics, SLIs, SLOs, and Error Budgets

M030 introduces versioned definitions and measured evidence for:

- API availability and latency;
- frontend performance and critical-status load;
- scheduled-cycle completion and start delay;
- market-data freshness;
- Gemini provider success versus valid-report rate;
- deterministic fallback availability;
- financial transaction and reconciliation success;
- zero duplicate financial side effects;
- zero unresolved ledger mismatch;
- export/backup and restore success;
- database/backtest/provider capacity;
- provider quota and cost;
- resilience and recovery.

Every metric/SLI specifies source, unit, labels/cardinality, numerator/denominator or aggregation, window, exclusions, version, sample requirements, and limitations.

Zero-tolerance financial/security invariants receive no permissive error budget.

Profit is not an SLI, SLO, availability indicator, or operational success criterion.

## 18. Cost, Quota, and Capacity Evidence

Evidence distinguishes:

- billed;
- free allowance;
- provider reported;
- configured budget;
- application measured;
- estimated;
- forecast;
- unknown/unavailable.

Provider numeric limits, pricing, terms, and reset behavior require current timestamped approved evidence. Documentation prose is not a quota source of truth.

No alert or forecast may automatically purchase, upgrade, scale, or increase a budget.

## 19. Metric and Label Safety

- metric names and units are registered and versioned;
- labels use bounded enums/classes;
- workspace/user/entity/correlation/request/prompt/raw error text is not an unbounded label;
- secrets and personal data are prohibited;
- high-cardinality findings block instrumentation release;
- source revision and environment are represented safely;
- exemplars/traces, if later used, follow the same redaction and access rules.

## 20. Runbooks Required Before M029

- GitHub scheduled cycle failed, delayed, missed, or duplicated;
- Supabase unavailable or paused;
- Render cold start/deploy failure;
- Binance stale, unavailable, or gap repair failed;
- Gemini unavailable, quota exhausted, refused, safety-blocked, or invalid;
- risk/experiment/workspace halt;
- ledger or reconciliation mismatch;
- duplicate side-effect suspicion;
- export/backup failure and restore operation;
- Auth/RLS mismatch or account compromise;
- suspected secret exposure and rotation;
- experiment halt and evidence collection.

Before M036, add deployment, migration, SLO fast burn, capacity, cost, privacy, data lifecycle, support, and status-communication runbooks.

Each runbook has owner, version, prerequisites, safety boundary, steps, validation, rollback/recovery, review date, and drill evidence.

## 21. Retention

- durable domain/audit/financial evidence follows versioned data-retention and hold policy;
- provider logs follow provider retention and are never the sole audit record;
- operational application logs use environment-specific retention;
- raw Gemini/provider content is minimized, access-controlled, and retained only when approved;
- cleanup is idempotent and must not break lineage or active holds;
- archive/restore preserves reproducibility and reconciliation.

## 22. Deferred Hosted Observability

Prometheus, Grafana, OpenTelemetry collectors/backends, centralized log platforms, and paging/status vendors may be introduced only after:

- measured M030 need;
- M034 change proposal;
- ADR;
- privacy/cardinality/cost review;
- migration and compatibility plan;
- tests and resilience evidence;
- staged verification;
- rollback plan;
- owner approval.

Their future possibility does not change the mandatory persistent evidence model.

## 23. Testing

Tests verify:

- log schemas, redaction, and bounded labels;
- correlation propagation;
- cycle status/stage completeness;
- intended versus actual scheduling;
- duplicate/lock behavior;
- provider/fallback/budget states;
- ledger/reconciliation/integrity events;
- frontend priority and stale/partial/unavailable behavior;
- health endpoint semantics;
- alert routing/deduplication;
- incident state separation;
- export/restore evidence;
- metric/SLI reference calculations and sample adequacy;
- quota/cost evidence classification;
- no-auto-purchase/scale behavior;
- retention and cleanup safety.

## 24. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `PERFORMANCE_RESILIENCE_CAPACITY_FINOPS_WORKSPACE_IMPLEMENTATION.md`
- `INCIDENT_RESPONSE_POSTMORTEM_LEARNING_WORKSPACE_IMPLEMENTATION.md`
- `SECURITY.md`
- `TESTING.md`
- `DEPLOYMENT.md`
