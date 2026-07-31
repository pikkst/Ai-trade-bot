# Experiment Operations, Scheduled Cycle, Incident, and Audit Timeline Workspace Implementation Specification

Last reviewed: 2026-07-31  
Status: Sprint 10 authoritative experiment-operations and audit workspace specification

## 1. Purpose

This document defines the implementation contract for the Experiment Operations, Scheduled Research Cycle, Incident, Recovery, and Audit Timeline Workspace of The Daily Roast AI.

The workspace explains which frozen configuration governs an experiment, whether preflight gates passed, how scheduled cloud research cycles are progressing, which services and evidence each cycle used, whether any cycle was delayed, duplicated, incomplete, failed, reconciled, or halted, how incidents and recovery actions were handled, and whether the experiment remains valid for final research review.

Sprint 10 may expose tightly controlled paper-experiment lifecycle commands: preflight, start, pause, resume when separately approved, and halt. These commands are owner-authorized, idempotent, server-validated, confirmation-gated, and fully audited. They must never enable private Binance order placement, live capital, mutable financial evidence, risk bypass, or AI authority over experiment state.

## 2. Scope

Sprint 10 covers:

- experiment list, detail, configuration, preflight, cycles, incidents, audit, exports, recovery, and report routes;
- frozen experiment configuration and configuration hash;
- lifecycle states and immutable transitions;
- preflight checks and release-blocking gates;
- owner-only paper-experiment start, pause, approved resume, and halt commands;
- scheduled GitHub Actions cycle evidence;
- one-shot research-cycle CLI state and idempotency evidence;
- intended, actual, and completed cycle timing;
- database lock or lease evidence;
- market, Gemini, strategy, risk, order, fill, ledger, reconciliation, and audit lineage per cycle;
- delayed, missed, duplicate, partial, failed, and recovered cycle states;
- GitHub Actions, Render, Supabase, Binance, Gemini, frontend, and domain-health summaries;
- incidents, halts, review state, runbooks, recovery, export, and restore evidence;
- 30-day experiment progress and final report status;
- cash and buy-and-hold benchmark context;
- immutable audit-event timeline;
- responsive, accessible, secure, observable, and testable presentation.

Sprint 10 does not implement:

- live trading;
- private exchange credentials;
- automatic restart or resume after a safety halt;
- browser-side database repair;
- mutation or deletion of audit, cycle, order, fill, ledger, or reconciliation evidence;
- direct GitHub Actions secret display;
- direct database or service-role access from the browser;
- AI authority to start, pause, resume, halt, repair, or approve an experiment;
- automatic strategy or risk-policy changes during a running experiment;
- exact-time or high-frequency scheduling guarantees.

## 3. User Outcomes

A user should be able to answer:

1. Which experiment am I viewing, and what is its lifecycle state?
2. Which immutable configuration, versions, limits, services, and virtual capital govern it?
3. Did every preflight gate pass before start?
4. Who approved the start, pause, resume, halt, or completion transition?
5. When was each scheduled cycle intended to run, when did it actually run, and when did it finish?
6. Did the cycle obtain the database lock and use the expected idempotency key?
7. Which market snapshot, Gemini result, strategy decision, risk result, order, fill, ledger, and reconciliation records belong to the cycle?
8. Was a cycle delayed, missed, duplicated, partial, failed, recovered, or invalidated?
9. Are GitHub Actions, Render, Supabase, Binance, Gemini, Auth, and the frontend within documented operating limits?
10. Is market data fresh, Gemini within budget, risk policy active, and portfolio accounting reconciled?
11. Which incident or halt is active, what caused it, and what evidence remains unresolved?
12. Which runbook and recovery actions were used?
13. Were database exports and restore drills completed at the required cadence?
14. Is the experiment still valid for the planned 30-day report?
15. What does the immutable audit timeline show across users, systems, cycles, and domain entities?
16. How does current paper performance compare with cash and buy-and-hold without implying future profitability?

## 4. Canonical Routes

```text
/experiments
/experiments/:experimentId
/experiments/:experimentId/configuration
/experiments/:experimentId/preflight
/experiments/:experimentId/cycles
/experiments/:experimentId/cycles/:cycleId
/experiments/:experimentId/incidents
/experiments/:experimentId/incidents/:incidentId
/experiments/:experimentId/audit
/experiments/:experimentId/recovery
/experiments/:experimentId/exports
/experiments/:experimentId/report
/audit
/audit/events/:eventId
```

The workspace must be reachable from Today’s Roast, market evidence, Gemini analysis, strategy and risk decisions, paper portfolio, backtests, system status, and final research reports.

Route access must be authorization-aware. Lifecycle command routes must be visually and programmatically separate from read-only evidence routes.

## 5. Information Architecture

The experiment detail page is ordered as follows:

1. environment, simulation, lifecycle, halt, reconciliation, freshness, and validity state;
2. experiment identity, planned period, and owner approval;
3. frozen configuration and safety limits;
4. preflight result and unresolved blockers;
5. latest successful and latest attempted cycle;
6. expected schedule and delay classification;
7. cycle completeness and lineage;
8. service and dependency status;
9. portfolio, risk, Gemini, and benchmark summary;
10. incidents, halts, and recovery state;
11. export, backup, and restore evidence;
12. immutable audit timeline;
13. report progress, limitations, and lifecycle commands.

An active halt, reconciliation mismatch, invalid configuration, missing cycle evidence, stale market data, failed preflight, or unresolved critical incident must visually dominate performance or completion metrics.

## 6. Recommended Read Models

Recommended experiment contract:

```ts
interface ExperimentOperationsReadModel {
  schemaVersion: string;
  experiment: ExperimentIdentity;
  lifecycle: ExperimentLifecycleSummary;
  configuration: FrozenExperimentConfigurationSummary;
  preflight: ExperimentPreflightSummary | null;
  schedule: ExperimentScheduleSummary;
  latestAttempt: ResearchCycleSummary | null;
  latestSuccess: ResearchCycleSummary | null;
  cycleHealth: ExperimentCycleHealthSummary;
  dependencies: DependencyStatusSummary[];
  domainSafety: ExperimentDomainSafetySummary;
  portfolio: ExperimentPortfolioSummary | null;
  benchmarks: ExperimentBenchmarkSummary[];
  incidents: IncidentSummary[];
  halts: TradingHaltSummary[];
  recovery: RecoverySummary;
  exports: ExperimentExportSummary;
  report: ExperimentReportStatusSummary;
  diagnostics: DiagnosticSummary[];
  limitations: LimitationSummary[];
  permissions: ExperimentCommandPermissions;
  links: ExperimentResourceLinks;
}
```

Recommended cycle contract:

```ts
interface ResearchCycleDetailReadModel {
  schemaVersion: string;
  cycle: ResearchCycleIdentity;
  schedule: CycleScheduleEvidence;
  lock: CycleLockEvidence;
  idempotency: CycleIdempotencyEvidence;
  status: ResearchCycleStatusSummary;
  market: CycleMarketEvidence | null;
  gemini: CycleGeminiEvidence | null;
  strategy: CycleStrategyEvidence | null;
  risk: CycleRiskEvidence | null;
  execution: CycleExecutionEvidence | null;
  accounting: CycleAccountingEvidence | null;
  reconciliation: ReconciliationSummary | null;
  auditEvents: AuditEventReference[];
  workflow: WorkflowRunEvidence | null;
  diagnostics: DiagnosticSummary[];
  validity: CycleValiditySummary;
  links: CycleResourceLinks;
}
```

Recommended preflight contract:

```ts
interface ExperimentPreflightReadModel {
  schemaVersion: string;
  run: PreflightRunIdentity;
  experiment: ExperimentReference;
  configurationHash: string;
  checks: PreflightCheckResult[];
  outcome: "passed" | "failed" | "blocked" | "expired";
  blockers: PreflightBlocker[];
  warnings: PreflightWarning[];
  evidence: PreflightEvidenceReference[];
  approvedBy: ActorReference | null;
  expiresAt: string | null;
}
```

Recommended audit contract:

```ts
interface AuditTimelineReadModel {
  schemaVersion: string;
  events: AuditEventSummary[];
  page: CursorPage;
  integrity: AuditIntegritySummary;
  filters: AuditFilterSummary;
  diagnostics: DiagnosticSummary[];
}
```

The frontend must not calculate authoritative experiment validity, cycle completeness, delay classification, preflight outcome, reconciliation state, command permission, incident severity, or audit integrity.

## 7. Experiment Identity

Required fields:

- immutable experiment ID;
- workspace ID;
- name and approved description;
- experiment type;
- environment;
- explicit paper or simulation mode;
- lifecycle state;
- frozen configuration ID and hash;
- paper portfolio ID;
- virtual starting capital and base currency;
- planned start and end timestamps;
- actual start and end timestamps;
- expected cycle cadence;
- owner and approval references;
- report ID or status;
- active halt and incident references;
- archive or supersession state.

The public or authenticated UI must never describe the experiment as live trading.

## 8. Experiment Lifecycle

Supported lifecycle states include:

- draft;
- preflight pending;
- preflight failed;
- ready;
- running;
- paused;
- halted;
- completing;
- completed;
- failed;
- archived.

Every state transition must create immutable evidence containing:

- transition ID;
- from and to state;
- actor type and actor ID;
- source: user, workflow, risk, reconciliation, integrity, or system;
- reason code;
- safe explanation;
- timestamp;
- correlation and request references;
- preflight, incident, halt, or report reference where applicable.

Historical transitions must not be rewritten.

## 9. Frozen Configuration Contract

Required configuration fields include:

- configuration ID, version, and hash;
- allowed exchange, symbol, and interval;
- scheduled-cycle cadence and timezone;
- market-data freshness policy;
- feature-set version;
- Gemini mode, provider configuration, prompt, schema, validation, and budget references;
- strategy version and parameters;
- risk-policy version and limits;
- execution-model version;
- accounting-policy version;
- portfolio initial funding;
- benchmark definitions;
- export cadence;
- retention and report policy;
- environment and service references without secrets;
- code commit, dependency lock, and migration revision where required.

A running experiment must not silently adopt a new configuration.

Any approved change requires a new experiment or an explicit versioned transition policy that preserves complete history.

## 10. Baseline EUR 20 Experiment Profile

The approved baseline profile includes:

- virtual EUR 20 initial capital;
- BTC/EUR;
- one-hour finalized candles;
- approximately hourly best-effort scheduled cycles;
- maximum position 25%;
- maximum order EUR 5;
- daily drawdown halt 5%;
- total drawdown halt 15%;
- maximum one open order;
- no leverage;
- no margin;
- no futures;
- no shorting;
- Gemini cost budget EUR 0 by default;
- cash and buy-and-hold benchmarks;
- live trading and private Binance access disabled.

The workspace must display actual frozen values rather than assuming the baseline.

## 11. Preflight Contract

Preflight checks include at minimum:

- frozen configuration completeness and hash;
- environment correctness;
- database connectivity;
- required migration revision;
- Supabase Auth and RLS checks;
- service-role isolation;
- paper portfolio and initial funding evidence;
- Binance public market-data connectivity;
- finalized candle availability and freshness;
- Gemini mode, key availability where applicable, allowance, budget, and deterministic fallback;
- strategy, risk, execution, and accounting version compatibility;
- idempotency and duplicate-side-effect protections;
- database advisory lock or lease behavior;
- ledger and reconciliation invariants;
- halt controls;
- GitHub Actions workflow configuration;
- Render API health;
- Cloudflare frontend and CORS configuration;
- export procedure;
- restore drill evidence;
- observability and runbook availability;
- secret scanning;
- owner approval.

Preflight blockers prevent Ready or Running state.

Preflight results must expire when material evidence or configuration changes.

## 12. Lifecycle Command Contract

Supported paper-experiment commands may include:

```http
POST /api/v1/experiments/{experiment_id}/preflight
POST /api/v1/experiments/{experiment_id}/start
POST /api/v1/experiments/{experiment_id}/pause
POST /api/v1/experiments/{experiment_id}/resume
POST /api/v1/experiments/{experiment_id}/halt
```

`resume` is available only when explicitly implemented and approved. It must not clear an unresolved risk, reconciliation, or integrity halt.

Every command requires:

- authenticated owner role unless a documented internal safety command applies;
- server-side authorization;
- valid current state;
- idempotency key;
- expected version or concurrency guard;
- canonical reason code;
- explicit confirmation for state-changing UI actions;
- correlation ID;
- immutable audit event;
- safe response containing resulting state and evidence links.

The browser must not directly update experiment-control tables.

## 13. Start Gate

Starting an experiment requires:

- current state Ready;
- passed and unexpired preflight;
- exact configuration-hash match;
- owner approval;
- no active workspace or portfolio halt;
- reconciled initial portfolio;
- valid future planned end time;
- valid schedule configuration;
- export baseline completed;
- no unresolved critical incident;
- live trading disabled;
- private exchange credentials absent.

The start transition records actual start time, planned end time, approval, configuration hash, initial state hash, and first expected cycle.

## 14. Pause, Resume, Halt, and Completion Semantics

### Pause

Pause stops new scheduled research actions according to policy while preserving read access and all evidence.

Pause does not clear open orders, halts, incidents, or reconciliation requirements unless a separate deterministic command handles them.

### Resume

Resume is allowed only from an eligible paused state after a compatibility and safety check. It is prohibited while a risk, reconciliation, integrity, or unresolved critical incident halt remains active.

### Halt

Halt immediately blocks new entry actions. It records scope, source, reason, evidence, and review state.

### Completion

Completion requires the planned or approved early end condition, final cycle closure, portfolio reconciliation, export, report generation state, and no hidden unresolved integrity failure.

A completed experiment may still contain documented incidents and unfavorable performance.

## 15. Scheduled Cycle Identity

Required cycle fields:

- immutable cycle ID;
- experiment ID;
- stable occurrence key;
- intended schedule time;
- actual start time;
- finish time;
- duration;
- environment;
- workflow run and attempt identifiers where available;
- job or command version;
- code commit and dependency lock reference;
- configuration hash;
- status;
- safe terminal error code;
- correlation ID;
- database lock outcome;
- idempotency outcome;
- data freshness;
- Gemini outcome;
- snapshot, feature, analysis, strategy, risk, order, fill, ledger, reconciliation, audit, and incident references.

The stable occurrence key must make retries idempotent.

## 16. Cycle Status and Completeness

Supported cycle statuses include:

- expected;
- delayed;
- started;
- lock rejected;
- running;
- completed;
- completed with warning;
- skipped by policy;
- failed;
- timed out;
- cancelled;
- duplicate attempt;
- recovered;
- invalidated.

Cycle completeness must classify whether required stages exist and are valid.

A cycle is not complete merely because the process exited successfully.

Required stage checks include:

- schedule and occurrence identity;
- lock and idempotency;
- market-data result;
- snapshot and feature result;
- Gemini mode result;
- strategy result;
- risk result;
- permitted action result;
- order and fill result when applicable;
- ledger result when a financial event occurred;
- reconciliation result;
- audit closure;
- terminal status.

## 17. Delay, Missed-Cycle, and Schedule Semantics

GitHub Actions schedules are best effort.

Required schedule fields:

- configured cadence;
- intended occurrence time;
- expected tolerance window;
- actual start time;
- delay duration;
- delay classification;
- next expected occurrence estimate;
- last successful and last attempted occurrence;
- consecutive delay or failure count;
- schedule-source status.

The UI must label the next cycle as an estimate, not a guarantee.

A missed or delayed cycle does not automatically justify replaying financial actions against stale evidence.

Recovery behavior must be versioned and conservative.

## 18. Database Lock and Concurrency Evidence

Every cycle must expose where applicable:

- lock or lease type;
- lock key;
- acquisition attempt time;
- acquisition outcome;
- owner or session-safe reference;
- lease expiration where applicable;
- release outcome;
- overlapping occurrence reference;
- duplicate-side-effect check.

Lock rejection should produce a safe terminal or skipped state without duplicate financial side effects.

No network call may remain inside a financial database transaction.

## 19. Idempotency Evidence

Required idempotency fields:

- stable occurrence key;
- command idempotency key;
- existing cycle reference when duplicate;
- side-effect identities;
- duplicate attempt count;
- final deduplication outcome;
- safe diagnostic code.

Retries must return or link to existing results rather than create duplicate snapshots, analyses, decisions, orders, fills, ledger postings, or audit events.

## 20. Cycle Lineage

Canonical cycle lineage:

```text
scheduled occurrence
  -> cycle command
  -> database lock
  -> finalized market-data ingestion and gap repair
  -> immutable market snapshot
  -> feature calculation
  -> optional Gemini analysis and validation
  -> deterministic strategy evaluation
  -> deterministic risk evaluation
  -> permitted paper action
  -> paper order
  -> simulated fill
  -> append-only ledger transaction
  -> portfolio state version
  -> reconciliation
  -> audit closure
```

Optional stages must be explicitly marked. Required missing stages are integrity failures.

## 21. Market and Freshness Evidence

Cycle detail must expose:

- latest eligible finalized candle;
- snapshot ID and hash;
- interval and market;
- data-quality result;
- gap-detection and repair result;
- source request or ingestion references;
- freshness threshold;
- freshness outcome;
- stale-data rejection reason where applicable.

Stale or incomplete market data must block entry actions according to risk and cycle policy.

## 22. Gemini Budget and Outcome Evidence

Cycle detail must expose:

- Gemini mode;
- provider and configured model identifier;
- prompt, schema, and validation versions;
- request, retry, latency, usage, and cost estimate where safe;
- budget period, allowance, reserved and committed usage;
- quota, rate-limit, provider, safety, refusal, schema, and fallback outcomes;
- validated report reference where available;
- deterministic fallback or HOLD result.

Secrets, raw prompt bodies, and unrestricted provider responses must not be exposed.

## 23. Strategy, Risk, and Execution Evidence

Cycle detail must link to:

- strategy evaluation and version;
- strategy intent and reason codes;
- portfolio-state version used;
- risk-policy version;
- risk outcome and binding constraints;
- requested and approved exposure;
- permitted paper action;
- order, fill, fee, spread, slippage, precision, and execution-model evidence;
- absence reasons when no action occurred.

A positive Gemini or strategy output must not bypass deterministic risk.

## 24. Accounting and Reconciliation Evidence

Cycle detail must expose when applicable:

- order reservation;
- fills;
- ledger transaction IDs and sequence range;
- portfolio state version and state hash;
- fee and cost postings;
- reconciliation run;
- matched, mismatch, or unable-to-reconcile outcome;
- halt reference;
- correction or rebuild comparison references.

A reconciliation mismatch invalidates the cycle’s financial completion and creates or references a critical halt.

## 25. Dependency and Service Status

The workspace may present approved status summaries for:

- GitHub Actions schedule and latest workflow run;
- Supabase database and Auth;
- migration revision;
- Render API live and ready health;
- Cloudflare frontend deployment and configuration version;
- Binance public REST connectivity and freshness;
- Gemini provider, allowance, and budget;
- export destination or procedure status;
- local or external recovery environment where relevant.

Status must include source, observed timestamp, freshness, safe outcome, limitation, and evidence link.

Provider dashboards and logs are operational sources, not the sole audit record.

## 26. Incident Contract

An incident record includes:

- immutable incident ID;
- experiment and workspace references;
- severity;
- category;
- status;
- title and safe description;
- detection source;
- detected and acknowledged timestamps;
- actor or system references;
- affected cycles and entities;
- canonical reason codes;
- active halt reference;
- containment actions;
- recovery actions;
- evidence links;
- resolution and review state;
- post-incident or follow-up reference.

Incidents must not be deleted to make the final report appear cleaner.

## 27. Incident Categories

Categories include:

- scheduled workflow delayed or failed;
- database unavailable or paused;
- migration mismatch;
- authentication or authorization failure;
- Render deploy or readiness failure;
- stale or incomplete Binance data;
- Gemini quota, provider, safety, schema, or budget failure;
- duplicate workflow suspicion;
- duplicate financial side-effect suspicion;
- risk halt;
- ledger posting failure;
- reconciliation mismatch;
- export cadence missed;
- restore failure;
- secret or security event;
- configuration drift;
- report-generation failure.

Severity and state are server-defined and versioned.

## 28. Halt and Review Contract

Required halt fields:

- halt ID;
- scope;
- source;
- reason code;
- severity;
- activated timestamp;
- affected experiment, portfolio, cycle, or entity;
- incident reference;
- evidence references;
- review state;
- reviewed by and timestamp;
- superseding transition;
- unresolved blockers.

A reviewed halt is not necessarily cleared. Clearing or resuming requires the exact approved domain workflow.

The UI must not offer a generic bypass action.

## 29. Runbook and Recovery Evidence

Required runbook categories include:

- scheduled cycle failed or delayed;
- Supabase unavailable or paused;
- Render cold start or deploy failure;
- Binance data stale;
- Gemini unavailable or quota exhausted;
- risk halt;
- ledger reconciliation mismatch;
- duplicate workflow suspicion;
- database export and restore;
- experiment halt and evidence collection.

Recovery evidence includes:

- runbook version;
- trigger;
- actor;
- start and finish timestamps;
- actions taken;
- commands or tools referenced without secrets;
- validation checks;
- affected resources;
- resulting state;
- unresolved items;
- audit and incident references.

Recovery must not mutate immutable evidence or conceal failed attempts.

## 30. Export, Backup, and Restore Evidence

The experiment workspace must show:

- baseline export before start;
- scheduled export cadence;
- last successful export;
- next expected export;
- missed cadence warning;
- export format and schema version;
- source database or workspace reference;
- artifact hash and location reference without secret URL;
- restore drill target environment;
- restore start, finish, and outcome;
- verification checks;
- migration and data-integrity results;
- operator and audit references.

A provider backup promise must not be inferred when the free tier does not guarantee it.

## 31. Audit Event Contract

Every audit event includes:

- immutable event ID;
- workspace and experiment references;
- timestamp;
- actor type and actor ID;
- event type;
- entity type and entity ID;
- outcome;
- canonical reason or error code;
- correlation, request, cycle, workflow, and job references where safe;
- bounded safe details;
- integrity hash where implemented;
- predecessor or chain reference where implemented.

Audit events are append-only and authorization-filtered.

## 32. Audit Timeline

The audit timeline must support bounded filters for:

- date range;
- actor;
- actor type;
- event type;
- entity type and ID;
- cycle;
- incident;
- halt;
- outcome;
- error code;
- correlation ID where authorized.

The timeline must preserve deterministic ordering and cursor pagination.

Critical security, integrity, reconciliation, halt, and lifecycle events must remain visible according to role and policy.

## 33. Audit Integrity

The workspace should expose where implemented:

- event count and range;
- missing sequence detection;
- integrity hash status;
- chain verification status;
- duplicate event detection;
- retention status;
- export verification;
- diagnostic limitations.

Missing or corrupted audit evidence must not appear as an empty history.

## 34. Experiment Validity Contract

Experiment validity is a server-calculated classification based on:

- frozen configuration integrity;
- valid lifecycle transitions;
- preflight status;
- cycle completeness;
- market-data quality and freshness;
- Gemini mode and budget policy;
- strategy and risk evidence;
- duplicate-side-effect protections;
- ledger and reconciliation state;
- unresolved incidents and halts;
- export and restore evidence;
- report completeness;
- documented service limitations.

Possible classifications include:

- valid and running;
- valid with warnings;
- paused for review;
- halted;
- invalidated;
- completed with complete evidence;
- completed with limitations;
- failed.

The frontend must not derive this classification.

## 35. 30-Day Progress Contract

Required progress fields:

- planned start and end;
- actual start;
- elapsed and remaining planned duration;
- expected, attempted, successful, warned, failed, delayed, duplicate, skipped, and invalidated cycle counts;
- longest cycle gap;
- latest successful cycle;
- current data freshness;
- active incident and halt count;
- reconciliation status;
- export cadence status;
- report-generation readiness.

Time progress must not be presented as evidence completeness.

## 36. Current and Final Experiment Report

The report includes:

- experiment identity and frozen configuration;
- planned and actual period;
- service and schedule limitations;
- cycle completeness statistics;
- market-data quality and gaps;
- Gemini validity, budget, usage, failures, and fallback behavior;
- strategy and risk outcomes;
- portfolio, P&L, fees, exposure, drawdown, and turnover;
- cash and buy-and-hold benchmarks;
- orders, fills, ledger, and reconciliation summary;
- incidents, halts, recovery, and manual actions;
- export and restore evidence;
- audit-integrity state;
- reliability, cost, quota, and cold-start evidence;
- user-interface and comprehension findings where collected;
- limitations;
- explicit simulated-results and non-guarantee statement;
- decision to stop, repeat, improve, or progress to the next approved stage.

Profit is not an experiment exit criterion.

## 37. Benchmark and Portfolio Summary

The workspace may show current paper performance against:

- virtual cash;
- buy-and-hold using compatible period and execution assumptions;
- approved backtest references.

Every comparison must expose period, capital, data, valuation, fee, spread, slippage, precision, version, reconciliation, and limitation evidence.

Performance must not suppress reliability or integrity failures.

## 38. Filtering and History

Experiment and cycle history may filter by approved bounded fields:

- lifecycle state;
- planned or actual date range;
- cycle status;
- delay class;
- market freshness;
- Gemini outcome;
- strategy or risk outcome;
- order or fill presence;
- reconciliation outcome;
- incident or halt;
- workflow run;
- error code;
- validity classification;
- export or restore state.

Filters must be URL-stable where appropriate, server-approved, authorization-aware, and cursor-paginated.

## 39. Export Contract

Authorized exports may include:

- experiment configuration package;
- preflight report;
- lifecycle-transition history;
- cycle status and lineage package;
- service-status evidence;
- incident and halt package;
- recovery record;
- export and restore record;
- audit-event range;
- current or final experiment report.

Every export must include:

- schema and generation versions;
- experiment and workspace identity;
- configuration hash;
- simulation disclaimer;
- timestamps and timezone;
- lifecycle, validity, warning, incident, halt, reconciliation, and completeness state;
- provenance and integrity hashes where available;
- limitations;
- authorization context without secrets.

Exports must be generated server-side and must not omit unresolved critical evidence.

## 40. Page-State Matrix

Explicit states include:

- loading;
- no experiments;
- draft;
- preflight pending;
- preflight failed;
- ready;
- starting;
- running;
- paused;
- resuming;
- halted;
- completing;
- completed;
- failed;
- archived;
- no cycles yet;
- cycle expected;
- cycle delayed;
- cycle running;
- cycle complete;
- cycle warning;
- cycle failed;
- lock rejected;
- duplicate attempt;
- missed cycle;
- stale market data;
- Gemini fallback;
- risk halt;
- reconciliation mismatch;
- active incident;
- recovery in progress;
- export overdue;
- restore failed;
- report incomplete;
- audit-integrity failure;
- schema mismatch;
- unauthorized;
- not found;
- backend unavailable;
- command conflict;
- export unavailable.

Critical safety and evidence failures must not render as ordinary empty or successful states.

## 41. Responsive Behavior

Requirements:

- simulation, lifecycle, validity, halt, reconciliation, and freshness state remains first;
- scheduled and actual cycle times remain distinguishable;
- configuration and preflight tables provide narrow-layout alternatives;
- cycle lineage remains chronological;
- incidents, halts, and audit events retain severity, reason, timestamp, and entity context;
- command controls remain separated from evidence and are not sticky in a way that encourages accidental activation;
- long IDs, hashes, workflow references, and reason codes wrap or copy safely;
- no critical evidence is hover-only;
- dense tables preserve headers and context.

## 42. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- keyboard-accessible filters, disclosures, tabs, timelines, and command confirmations;
- semantic tables with captions and headers;
- accessible definitions for lifecycle, cycle, incident, halt, audit, and service states;
- visible focus;
- status announcements for material asynchronous changes;
- confirmation dialogs with clear action, consequence, and cancellation;
- no reliance on color alone;
- reflow at 200% and relevant cases at 400% zoom;
- reduced-motion support;
- screen-reader-readable timestamps, durations, counts, IDs, hashes, and statuses;
- safe copy controls.

## 43. Security and Authority Boundaries

The workspace must not:

- expose service-role, database, Gemini, GitHub, Render, Supabase, Cloudflare, or exchange secrets;
- start or resume an experiment without owner authorization and valid gates;
- clear risk, reconciliation, integrity, or incident halts generically;
- mutate financial, audit, cycle, incident, or transition history;
- bypass RLS or server-side command validation;
- accept arbitrary executable workflow, strategy, risk, or recovery commands from browser input;
- create private Binance orders;
- enable live trading;
- trust browser-calculated validity, delay, completeness, or permissions;
- expose stack traces, SQL, tokens, cookies, authorization headers, raw prompts, or unrestricted provider responses.

Internal safety systems may halt an experiment but may not silently resume it.

## 44. Command Confirmation and Abuse Prevention

State-changing commands require:

- explicit command name;
- target experiment identity;
- current and resulting state;
- reason code;
- consequence summary;
- unresolved blocker display;
- user confirmation;
- idempotency key;
- anti-CSRF protection where applicable;
- rate limiting;
- expected-version guard;
- audit logging;
- safe success or conflict response.

Repeated confirmation must not create duplicate transitions.

## 45. Privacy and Data Minimization

The UI, exports, logs, and telemetry must avoid:

- secrets and credentials;
- authorization headers and cookies;
- raw prompt bodies;
- unrestricted provider responses;
- internal database URLs;
- private workflow environment values;
- unnecessary personal identifiers;
- sensitive incident details outside authorized roles;
- full financial records where a bounded summary is sufficient.

## 46. Observability

Safe telemetry may include:

- experiments by lifecycle and validity state;
- preflight outcome and duration;
- state-transition outcomes;
- cycles by status;
- intended-to-actual delay;
- duration;
- lock and duplicate outcomes;
- market freshness;
- Gemini outcome and safe budget status;
- strategy and risk outcome counts;
- order, fill, ledger, and reconciliation outcomes;
- incidents and halts by safe category;
- recovery outcome and duration;
- export and restore status;
- report-generation status;
- audit-integrity outcome;
- command conflicts and denied authorization;
- approved correlation IDs;
- client build version.

Telemetry must not include secrets, raw prompts, unrestricted provider payloads, or full private financial evidence.

## 47. Testing Strategy

### Contract Tests

Validate schemas, enums, decimals, units, timestamps, lifecycle states, cycle states, reason codes, links, nullability, command conflicts, and compatibility behavior.

### Lifecycle Integration Tests

Validate draft, preflight, ready, start, running, pause, approved resume, halt, completing, completed, failed, and archived transitions with authorization, idempotency, expected versions, and audit evidence.

### Preflight Tests

Validate every required gate, blocker, expiry rule, configuration-hash match, secret absence, export baseline, restore evidence, and failure mapping.

### Cycle Integration Tests

Validate schedule identity, intended and actual times, lock acquisition and rejection, idempotency, market data, Gemini fallback, strategy, risk, execution, ledger, reconciliation, audit closure, timeout, duplicate, retry, and recovery behavior.

### Scheduling Tests

Validate delayed, missed, duplicate, skipped, best-effort, tolerance-window, and next-estimate semantics without exact-time guarantees.

### Incident and Halt Tests

Validate detection, severity, containment, halt activation, review, unresolved blockers, recovery linkage, and prohibition of generic bypass.

### Export and Restore Tests

Validate baseline and cadence exports, artifact hashes, restore into an isolated environment, migration compatibility, integrity checks, and visible failures.

### Audit Tests

Validate append-only behavior, authorization, deterministic ordering, filters, cursor pagination, correlation links, retention, duplicate detection, and integrity-chain checks where implemented.

### Authorization and RLS Tests

Validate anonymous, viewer, operator, owner, and service-role boundaries. Verify browser users cannot write critical domain tables directly.

### Route and Component Tests

Validate navigation, filters, state hierarchy, preflight, cycles, services, incidents, recovery, audit, report, command confirmation, conflicts, and safe errors.

### Accessibility Tests

Validate keyboard flow, headings, landmarks, tables, timelines, definitions, focus, announcements, confirmations, copy controls, zoom, reflow, and contrast.

### Visual Regression

Capture draft, preflight, ready, running, delayed, warning, paused, halted, failed, completed, incident, reconciliation mismatch, export overdue, restore failure, report incomplete, and audit-integrity states across themes and viewports.

### Security Tests

Validate CSRF protection, rate limits, expected-version conflicts, secret scanning, log redaction, hostile-content sanitization, command authorization, and absence of live-trading paths.

### Export Tests

Validate deterministic content, provenance, unresolved-warning preservation, simulation labeling, authorization, prohibited-field absence, and integrity hashes.

## 48. Acceptance Criteria

Sprint 10 documentation is accepted when:

1. experiment identity, lifecycle, configuration hash, planned period, and simulation state are explicit;
2. all lifecycle transitions are immutable, authorized, idempotent, and audited;
3. start requires passed unexpired preflight, exact configuration match, reconciliation, export baseline, and owner approval;
4. scheduled cycles expose intended and actual time, lock, idempotency, lineage, completion, and validity;
5. GitHub schedule delay is treated as best effort rather than an exact-time guarantee;
6. duplicate attempts cannot create duplicate financial side effects;
7. market, Gemini, strategy, risk, execution, accounting, reconciliation, and audit evidence is traceable per cycle;
8. incidents, halts, recovery, exports, and restore drills remain immutable and visible;
9. experiment validity is server-calculated and cannot be fabricated by the browser;
10. the 30-day report prioritizes evidence completeness, reliability, integrity, cost, incidents, and limitations over profit;
11. no generic halt bypass, automatic resume, private exchange order, live trading, browser repair, or AI operational authority is introduced;
12. security, privacy, accessibility, observability, scheduling, recovery, audit, and test gates are explicit.

## 49. Definition of Done

The Sprint 10 specification is complete when:

- this document is committed;
- `SPRINT_10_TASKS.md` is committed;
- terminology matches cloud MVP, observability, deployment, experiment, API, database, market, Gemini, strategy, risk, execution, portfolio, backtest, security, and testing documents;
- all lifecycle, preflight, command, cycle, schedule, dependency, incident, halt, recovery, export, restore, audit, validity, report, accessibility, and security states are explicit;
- both commits are fetched and verified.

## 50. Next Sprint Boundary

Sprint 11 defines the **Gemini Analysis, Validation, Evidence, and Research Narrative Workspace**, including provider and configured-model identity, prompt and schema versions, structured report validation, safety and refusal state, evidence references, budget and usage, deterministic fallback, comparison, export, and strict separation from strategy and execution authority.
