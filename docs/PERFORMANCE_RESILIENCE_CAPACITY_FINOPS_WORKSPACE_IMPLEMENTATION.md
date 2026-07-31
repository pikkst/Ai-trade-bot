# Performance, Resilience, Capacity, SLO, Cost, Quota, and FinOps Evidence Workspace Specification

Last reviewed: 2026-07-31  
Status: Sprint 15 authoritative performance, reliability, capacity, and cost-evidence specification

## 1. Purpose

This document defines the implementation contract for the Performance, Resilience, Capacity, Service-Level Objective, Cost, Quota, and FinOps Evidence Workspace of The Daily Roast AI.

The workspace measures how the research product behaves under real and simulated load, provider limits, cloud cold starts, scheduler delays, database contention, long backtests, network failures, quota exhaustion, and budget constraints. It explains which service-level indicators are measured, which objectives apply to each environment, how error budgets are consumed, where capacity limits exist, what each research cycle or experiment costs, and which evidence justifies a future architecture or plan change.

This workspace is evidence-first. It must not invent availability guarantees, represent free tiers as permanent capacity, auto-upgrade paid services, auto-scale into unapproved spend, suppress failed resilience tests, or treat profitability as a reliability objective.

## 2. Scope

Sprint 15 covers:

- performance, reliability, capacity, provider quota, cost, and SLO routes;
- API latency, throughput, availability, error, timeout, and cold-start evidence;
- scheduled-cycle intended time, actual start, duration, success, delay, missed, duplicate, and timeout evidence;
- market-data freshness and gap-repair latency;
- Gemini request latency, valid-report rate, retries, token usage, budget, and provider-limit evidence;
- database connection, query, transaction, lock, storage, index, and growth evidence;
- paper execution, ledger posting, reconciliation, and portfolio projection latency;
- backtest queue, runtime, event throughput, memory, CPU, storage, concurrency, cancellation, and timeout limits;
- frontend performance budgets and measured user-experience signals;
- SLI definitions, SLO targets, measurement windows, exclusions, and error budgets;
- incident and release linkage for reliability degradation;
- load, stress, spike, soak, failure, recovery, cold-start, and capacity tests;
- provider free-tier and paid-tier constraint snapshots without assuming permanence;
- cost allocation by provider, environment, workspace, experiment, cycle, analysis, backtest, and export;
- budgets, forecasts, anomalies, unit economics, and scale triggers;
- architecture decision evidence for future persistent workers, pooling, storage, observability, or upgraded plans;
- authorized evidence export;
- responsive, accessible, secure, observable, and testable presentation.

Sprint 15 does not implement:

- automatic purchase, plan upgrade, or cloud resource creation;
- unapproved autoscaling or spend increases;
- exact provider quota values hard-coded from documentation prose;
- automated live-trading capacity;
- high-frequency or sub-hour trading guarantees;
- synthetic success records for missed cycles;
- user billing or invoicing;
- public SLA commitments;
- arbitrary load generation against production research;
- collection of unrestricted user, prompt, financial, or secret-bearing telemetry;
- profit, return, or trading volume as an SLO.

## 3. User Outcomes

An owner, operator, engineer, or reviewer should be able to answer:

1. Which environment, revision, service, and measurement window am I viewing?
2. Which SLI definition and version produced each result?
3. Which SLO applies, and is it an internal objective or an external commitment?
4. How much error budget remains, and which incidents or failures consumed it?
5. What are the measured API latency distributions and error rates?
6. How often does Render cold-start, and how does it affect interactive reads?
7. Does Render availability affect the independent GitHub Actions research cycle?
8. How late do scheduled cycles start, and how often are cycles missed or duplicated?
9. How long do market ingestion, Gemini, strategy, risk, execution, ledger, and reconciliation stages take?
10. Which database queries, locks, connections, tables, or indexes are approaching limits?
11. What backtest size and concurrency can the current environment support safely?
12. Which provider quota, allowance, budget, or rate limit is near exhaustion?
13. Which service limit values are observed, configured, documented, estimated, or unknown?
14. What did each cycle, experiment, Gemini analysis, backtest, export, and environment cost?
15. Is the cost estimated, billed, free allowance, committed, reserved, or unavailable?
16. Which anomalies require investigation?
17. What capacity forecast and uncertainty support a scale decision?
18. Which architecture trigger has actually been reached?
19. Which resilience and recovery tests passed or failed at the current revision?
20. Does any recommendation preserve paper-only and live-trading-disabled boundaries?

## 4. Canonical Routes

```text
/operations/performance
/operations/reliability
/operations/slo
/operations/error-budgets
/operations/capacity
/operations/quotas
/operations/costs
/operations/forecasts
/operations/resilience-tests
/operations/resilience-tests/:testRunId
/operations/services/:serviceId
/operations/environments/:environmentId
/operations/experiments/:experimentId/costs
/operations/backtests/:backtestId/performance
```

The workspace must link to experiments, cycles, Gemini analyses, backtests, incidents, runbooks, releases, deployments, audit evidence, provider configurations, and governance blockers.

## 5. Information Architecture

The operations landing page is ordered as follows:

1. environment, revision, observation freshness, and evidence completeness;
2. critical integrity, reliability, quota, cost, or capacity blockers;
3. SLO and error-budget summary;
4. API and frontend experience;
5. scheduled-cycle reliability and stage latency;
6. database health and capacity;
7. Gemini and external-provider quotas;
8. backtest resource use and limits;
9. cost allocation, budget, and anomalies;
10. forecasts and scale triggers;
11. resilience, recovery, and capacity-test evidence;
12. incidents, releases, limitations, and export.

An integrity failure, exhausted critical quota, failed recovery test, missing measurement, or exceeded safety capacity must visually dominate ordinary latency or cost improvements.

## 6. Recommended Read Models

Recommended workspace contract:

```ts
interface PerformanceFinOpsWorkspaceReadModel {
  schemaVersion: string;
  context: OperationsContextSummary;
  evidenceState: OperationsEvidenceState;
  slo: SloPortfolioSummary;
  errorBudgets: ErrorBudgetSummary[];
  api: ApiPerformanceSummary;
  frontend: FrontendPerformanceSummary;
  cycles: ResearchCyclePerformanceSummary;
  database: DatabaseCapacitySummary;
  providers: ProviderCapacitySummary[];
  backtests: BacktestCapacitySummary;
  costs: CostPortfolioSummary;
  forecasts: CapacityForecastSummary[];
  resilience: ResilienceEvidenceSummary;
  blockers: OperationsBlocker[];
  diagnostics: DiagnosticSummary[];
  limitations: LimitationSummary[];
  links: OperationsResourceLinks;
}
```

Recommended SLO contract:

```ts
interface SloReadModel {
  schemaVersion: string;
  slo: SloIdentity;
  sli: SliDefinitionReference;
  target: DecimalString;
  unit: string;
  objectiveType: "internal" | "experimental" | "contractual";
  environment: string;
  measurementWindow: TimeWindow;
  exclusions: SloExclusionSummary[];
  result: DecimalString | null;
  compliance: "met" | "missed" | "insufficient_data" | "not_applicable";
  errorBudget: ErrorBudgetDetail;
  incidents: IncidentReference[];
  evidence: MetricEvidenceReference[];
  limitations: LimitationSummary[];
}
```

Recommended cost contract:

```ts
interface CostAllocationReadModel {
  schemaVersion: string;
  period: TimeWindow;
  currency: string;
  sourceStatus: "billed" | "estimated" | "free_allowance" | "configured_budget" | "unavailable";
  allocations: CostAllocationItem[];
  unattributed: MoneyValue;
  budgets: BudgetConsumptionSummary[];
  anomalies: CostAnomalySummary[];
  forecast: CostForecastSummary | null;
  pricingReferences: PricingReferenceSummary[];
  limitations: LimitationSummary[];
}
```

The frontend must not calculate authoritative SLO compliance, error budget, quota remaining, cost allocation, forecast, capacity headroom, anomaly severity, or scale-trigger outcome.

## 7. Operations Context

Required fields:

- environment ID and type;
- workspace scope;
- service or component scope;
- source revision and deployment ID;
- measurement start and end;
- observation timestamp;
- timezone;
- metric-definition version;
- SLO-policy version;
- cost-policy version;
- quota-snapshot version;
- data completeness;
- stale, partial, or unavailable status;
- simulation and live-trading-disabled state.

Measurements from different revisions, environments, or definitions must not be silently combined.

## 8. Evidence Quality Contract

Required classifications:

- measured;
- provider-reported;
- billed;
- estimated;
- configured;
- documented snapshot;
- synthetic test;
- inferred;
- unavailable.

Every result must identify source type, timestamp, collection method, sample count, confidence or limitation, and revision.

Provider dashboard values must not be represented as application-measured facts without labeling.

## 9. Service-Level Indicator Registry

Every SLI includes:

- stable SLI ID;
- name;
- description;
- numerator and denominator or aggregation method;
- unit;
- source metrics;
- event inclusion rules;
- failure classification;
- measurement window;
- sampling and aggregation;
- environment applicability;
- version;
- owner;
- tests;
- limitations.

A metric name alone is not an SLI definition.

## 10. Service-Level Objective Registry

Every SLO includes:

- stable SLO ID;
- SLI reference;
- target;
- unit;
- objective type;
- environment;
- measurement window;
- rolling or calendar semantics;
- exclusions;
- error-budget policy;
- alert thresholds;
- owner;
- approval;
- activation and archive timestamps;
- review cadence;
- limitations.

Free-cloud experimental objectives must not be presented as public SLA commitments.

## 11. Baseline SLO Categories

Recommended measured categories:

- authenticated API read availability;
- API read latency;
- privileged command correctness and terminal response;
- scheduled-cycle completion;
- scheduled-cycle start delay;
- market-data freshness;
- Gemini valid-report outcome;
- deterministic fallback availability;
- portfolio reconciliation success;
- zero duplicate financial side effects;
- zero unresolved ledger mismatch;
- backup/export completion;
- restore and reconciliation success;
- documentation and release evidence availability.

Profit is not an SLI or SLO.

## 12. Error Budget Contract

Required fields:

- SLO reference;
- period;
- total allowed failure or bad-event amount;
- consumed amount;
- remaining amount;
- burn rate by short and long windows;
- consuming incidents and events;
- exclusions applied;
- freeze or escalation policy;
- confidence and sample adequacy;
- reset semantics;
- calculation version.

Zero-tolerance invariants such as duplicate financial side effects or unresolved ledger mismatch do not receive a permissive error budget.

## 13. Error Budget Policy

Possible states:

- healthy;
- warning;
- fast burn;
- exhausted;
- insufficient data;
- not applicable;
- frozen by integrity incident.

An exhausted error budget may block feature releases or require reliability work according to policy. It must not trigger unapproved spend automatically.

## 14. API Availability and Error Contract

Required API indicators:

- request count;
- success count;
- client-error count;
- server-error count;
- timeout count;
- cancellation count;
- rate-limit count;
- authentication and authorization denial counts;
- dependency-unavailable count;
- cold-start classification;
- endpoint class;
- method;
- environment;
- revision.

Expected authorization denials must not be counted as service failure unless the SLI definition explicitly includes them.

## 15. API Latency Contract

Required fields:

- endpoint class and operation ID;
- sample count;
- minimum, median, P75, P90, P95, P99, and maximum where appropriate;
- histogram boundaries;
- server processing time;
- dependency time where instrumented;
- cold and warm classification;
- payload-size class;
- cache status;
- timeout threshold;
- revision and environment.

Percentiles require sufficient samples and must be reported as unavailable otherwise.

## 16. Cold-Start Evidence

Required fields:

- service;
- environment;
- previous idle duration where known;
- request start and readiness time;
- total cold-start latency;
- warm request comparison;
- failure or timeout outcome;
- user-visible impact;
- scheduled-cycle impact;
- provider-reported limitations;
- sample count;
- revision.

The workspace must preserve the architectural fact that Render API cold starts do not control the independent GitHub Actions cycle.

## 17. Frontend Performance Contract

Recommended evidence:

- build artifact size;
- route chunk sizes;
- JavaScript and CSS budgets;
- page-load and route-transition measurements;
- LCP, INP, CLS, TTFB, and other approved web-vital measurements;
- authentication bootstrap duration;
- shell and critical-status load duration;
- search response perception;
- slow-device and network profiles;
- error and retry state;
- accessibility impact;
- revision.

Synthetic and real-user measurements must remain separate.

## 18. Research-Cycle Reliability Contract

Required fields:

- expected occurrence count;
- attempted count;
- started count;
- completed count;
- completed-with-warning count;
- failed count;
- timed-out count;
- cancelled count;
- delayed count;
- missed count;
- duplicate-attempt count;
- lock-rejected count;
- recovered count;
- invalidated count;
- latest success;
- longest gap;
- consecutive failures;
- revision and configuration hash.

A successful workflow process exit is insufficient unless required cycle stages and reconciliation completed.

## 19. Schedule Delay Contract

Required fields:

- intended occurrence time;
- actual workflow or CLI start;
- delay duration;
- tolerance policy;
- delay classification;
- provider schedule source;
- queue or platform delay where known;
- latest eligible market event;
- action policy for delayed cycles;
- next occurrence estimate;
- sample distribution.

GitHub Actions scheduling remains best effort and must not be described as exact-hour execution.

## 20. Cycle Stage Latency

Stages include:

- lock acquisition;
- market server-time lookup;
- candle fetch;
- gap detection and repair;
- snapshot creation;
- feature calculation;
- Gemini budget check;
- provider request and retries;
- validation;
- strategy evaluation;
- risk evaluation;
- paper execution;
- ledger posting;
- portfolio projection;
- reconciliation;
- audit closure;
- export or report generation where applicable.

Every stage result includes start, finish, duration, outcome, retry count, dependency, and evidence link.

## 21. Market Freshness and Ingestion Performance

Required indicators:

- finalized candle age;
- provider server-time skew;
- ingestion request latency;
- candles returned;
- pages or requests;
- gaps detected;
- gaps repaired;
- repair duration;
- rejected invalid rows;
- snapshot creation duration;
- freshness outcome;
- stale-entry block count;
- provider error and rate-limit counts.

Faster ingestion must not weaken finalized-data or validation rules.

## 22. Gemini Performance and Validity

Required indicators:

- request count;
- successful provider responses;
- accepted validated reports;
- rejected reports;
- timeout, rate limit, refusal, safety block, empty, malformed, schema, grounding, unsupported-claim, and injection outcomes;
- attempt and retry counts;
- provider latency percentiles;
- validation latency;
- input, output, and total usage;
- estimated cost;
- fallback and HOLD counts;
- budget-blocked count;
- provider and configured-model versions.

Provider success rate and valid-report rate must remain separate.

## 23. Provider Quota Snapshot Contract

Every quota snapshot includes:

- provider and service;
- environment and project;
- resource type;
- limit value and unit when available;
- current usage;
- remaining amount;
- reset time and timezone;
- source: provider API, dashboard, configured policy, documentation snapshot, or unknown;
- observed timestamp;
- freshness;
- confidence;
- applicability;
- warning and exhaustion thresholds;
- limitations;
- snapshot version.

Current provider limits must be observed or configured at runtime rather than hard-coded from this specification.

## 24. Quota States

Supported states:

- healthy;
- warning;
- near limit;
- exhausted;
- throttled;
- disabled;
- unavailable;
- stale;
- inconsistent;
- changed by provider.

A changed provider limit requires review and may invalidate capacity assumptions.

## 25. Supabase Capacity Evidence

Required indicators where available:

- database size and growth;
- table and index size;
- storage allowance state;
- active and maximum connections;
- pool usage;
- transaction rate;
- lock waits and deadlocks;
- slow-query count;
- query latency;
- cache-hit ratio where meaningful;
- WAL or replication state where available;
- Auth request and rate-limit evidence;
- Data API usage;
- project pause or unavailability evidence;
- backup/export state.

Free-tier limits and backup assumptions must be labeled as provider constraints, not guarantees.

## 26. Database Query Evidence

Required fields:

- normalized query or operation ID;
- component and route;
- environment;
- call count;
- latency distribution;
- rows read and written;
- index usage summary;
- lock time;
- timeout and failure count;
- query-plan hash where approved;
- source revision;
- sensitive-text redaction;
- optimization or regression state.

Raw SQL containing secrets or sensitive values must not be exposed.

## 27. Financial Transaction Performance

Required indicators:

- reservation transaction duration;
- order/fill/ledger atomic-commit duration;
- ledger entries per transaction;
- portfolio state projection duration;
- reconciliation duration;
- rebuild duration;
- transaction retry and conflict counts;
- invariant-failure count;
- duplicate-prevention result;
- last ledger sequence;
- state-version reference.

Performance optimization must not weaken atomicity, decimal precision, idempotency, or reconciliation.

## 28. Backtest Capacity Contract

Required dimensions:

- event or candle count;
- date range;
- symbol count;
- interval;
- strategy and feature complexity class;
- Gemini mode;
- run duration;
- events per second;
- CPU time;
- peak memory;
- database reads and writes;
- report and artifact size;
- queue wait;
- concurrency;
- timeout;
- cancellation result;
- reconciliation result;
- environment and revision.

## 29. Backtest Resource Limits

Every environment defines:

- maximum event count;
- maximum date range;
- maximum concurrent runs;
- memory limit;
- CPU or runtime limit;
- output and artifact limit;
- database-write limit;
- timeout;
- queue policy;
- cancellation policy;
- cost budget;
- owner and policy version.

Limits are safety and resource controls, not performance guarantees.

## 30. Load and Capacity Test Profiles

Profiles may include:

- API read baseline;
- authenticated mixed reads;
- safe command contention in isolated test environment;
- database query and connection tests;
- overlapping cycle attempts;
- market-ingestion burst;
- Gemini fake-provider latency and failure profiles;
- backtest size and concurrency steps;
- export and report generation;
- documentation/search load;
- frontend slow-network and slow-device profiles.

No load test may target production research without explicit isolated approval and safety limits.

## 31. Resilience Test Categories

Required categories include:

- provider timeout;
- provider 429 or quota exhaustion;
- provider 5xx or malformed response;
- Binance stale or missing data;
- GitHub Actions delay and duplicate delivery;
- Render cold start or restart;
- Supabase interruption or pause;
- database connection exhaustion;
- lock contention and deadlock;
- partial transaction failure;
- process termination and restart;
- export failure;
- restore and reconciliation;
- frontend offline or stale cache;
- deployment and migration failure;
- observability destination failure.

## 32. Resilience Test Run Contract

Required fields:

- test-run ID;
- profile and version;
- source revision;
- environment;
- target services;
- fault or load injected;
- safety bounds;
- start, finish, and duration;
- expected behavior;
- observed behavior;
- invariant outcomes;
- SLI impact;
- recovery time;
- data-integrity result;
- audit and incident references;
- artifacts;
- outcome;
- limitations.

## 33. Recovery Time Evidence

Required fields:

- failure detection time;
- containment time;
- halt or read-only activation time;
- service restoration time;
- data restoration time;
- reconciliation completion time;
- user-visible recovery time;
- measured RTO comparison;
- data-loss interval and measured RPO comparison;
- unresolved limitations.

Measured recovery evidence must not be replaced by aspirational targets.

## 34. Cost Source Contract

Supported source states:

- provider-billed;
- provider-reported usage;
- free allowance consumed;
- internally estimated;
- configured budget;
- reserved estimate;
- committed estimate;
- unavailable.

Every cost item identifies provider, service, pricing-reference version, usage quantity, unit price or derivation, currency, tax handling state, timestamp, and uncertainty.

## 35. Cost Allocation Dimensions

Costs may be allocated by:

- provider and service;
- environment;
- workspace;
- experiment;
- research cycle;
- Gemini analysis;
- backtest;
- export or report;
- storage class;
- build or workflow;
- shared platform overhead;
- unattributed amount.

Allocation keys and approximation rules must be versioned.

## 36. Budget Contract

Budget fields:

- budget ID;
- scope;
- period;
- currency;
- amount;
- reserved, committed, billed, and forecast values;
- remaining amount;
- warning thresholds;
- exhausted state;
- reset semantics;
- owner;
- approval;
- policy version;
- safe-degradation behavior;
- no-auto-upgrade state.

The baseline cloud experiment targets EUR 0 required monthly infrastructure spend and EUR 0 Gemini paid usage unless explicitly reconfigured and approved.

## 37. Cost Anomaly Contract

Required fields:

- anomaly ID;
- scope;
- observed period;
- baseline method;
- expected range;
- observed value;
- absolute and relative difference;
- source confidence;
- severity;
- suspected cause;
- related release, experiment, provider, incident, or configuration;
- review and resolution state.

Small denominators and incomplete provider billing must not create misleading severity.

## 38. Unit Cost Metrics

Approved unit metrics may include:

- cost per successful research cycle;
- cost per validated Gemini report;
- cost per experiment day;
- cost per backtest event or run;
- cost per active workspace;
- cost per export or report;
- storage cost per retained evidence unit;
- CI or build-minute cost per release.

Each metric must expose allocation assumptions, sample count, source quality, and limitations.

## 39. Free-Tier Constraint Registry

Required fields:

- provider and service;
- tier;
- constraint category;
- observed or documented value;
- unit;
- source and review timestamp;
- change risk;
- behavior on exhaustion;
- current usage and headroom where available;
- fallback;
- promotion impact;
- owner;
- next review date.

Free-tier values are mutable external constraints and must not be embedded as permanent architectural guarantees.

## 40. Capacity Forecast Contract

Required fields:

- resource;
- historical period;
- current utilization;
- growth driver;
- forecast horizon;
- method and version;
- predicted range rather than false precision;
- confidence or uncertainty;
- threshold;
- estimated threshold date;
- scenario assumptions;
- owner;
- decision status;
- limitations.

Insufficient data produces no forecast rather than fabricated extrapolation.

## 41. Scale Trigger Contract

Possible triggers include:

- repeated error-budget burn;
- database connection or storage headroom below threshold;
- slow-query or lock contention;
- scheduled-cycle duration approaching cadence;
- backtest queue or runtime exceeding policy;
- provider quota nearing exhaustion;
- export or restore time exceeding target;
- Render cold-start impact exceeding approved objective;
- observability retention insufficient for incidents;
- measured cost or operational burden justifying an upgrade.

Every trigger requires measured evidence, duration, confidence, affected environment, proposed options, ADR requirement, cost, migration plan, and approval state.

## 42. Architecture Recommendation Boundary

The workspace may recommend investigation of:

- database pooling or plan upgrade;
- persistent worker platform;
- Redis/ARQ or another durable job system;
- Binance WebSocket plus REST repair;
- managed metrics and alerting;
- object storage;
- more reliable scheduler;
- backtest worker isolation;
- caching or read replicas;
- CDN and frontend optimization.

It must not activate these components automatically. Every material architecture change requires an ADR, migration plan, security review, cost approval, and release evidence.

## 43. Capacity Headroom

Required fields:

- resource;
- configured or observed limit;
- current peak and sustained usage;
- headroom amount and percentage;
- measurement period;
- source quality;
- warning and critical thresholds;
- burst allowance;
- recovery behavior;
- limitations.

Unknown limits produce unavailable headroom, not infinite capacity.

## 44. Incident and Release Correlation

Reliability and cost evidence must link to:

- release candidate and deployment;
- configuration version;
- incident and halt;
- provider change;
- migration;
- experiment and cycle;
- runbook execution;
- resilience test;
- rollback or forward fix.

The workspace should support before/after comparison with compatible windows and definitions.

## 45. Performance Regression Contract

Required fields:

- regression ID;
- metric or SLI;
- baseline revision and window;
- candidate revision and window;
- compatible environment and load profile;
- absolute and relative change;
- statistical or sample adequacy;
- severity;
- affected route or component;
- task and release references;
- approval or blocker state.

A faster result is invalid if safety or correctness regressed.

## 46. Evidence Retention

Performance and cost evidence retention must define:

- raw high-cardinality event duration;
- aggregated metric duration;
- test artifact retention;
- billing and quota snapshot retention;
- SLO and error-budget history;
- incident-linked evidence hold;
- anonymization and minimization;
- cleanup verification.

Retention must preserve enough evidence for experiment and release review without retaining secret or personal data.

## 47. Export Contract

Authorized exports may include:

- SLI and SLO definition package;
- error-budget report;
- API and frontend performance report;
- cycle reliability and latency report;
- provider quota snapshot;
- database capacity report;
- backtest capacity and benchmark report;
- resilience test package;
- cost allocation and budget report;
- capacity forecast and scale-trigger report;
- release performance comparison.

Every export includes schema and definition versions, environment, revision, window, source quality, units, sample count, blockers, incidents, limitations, and authorization context without secrets.

## 48. Page-State Matrix

Explicit states include:

- loading;
- no measurements;
- insufficient sample;
- measured healthy;
- warning;
- SLO missed;
- error budget fast burn;
- error budget exhausted;
- cold start;
- cycle delayed;
- cycle missed;
- provider quota warning;
- quota exhausted;
- quota unavailable;
- database capacity warning;
- connection saturation;
- storage near limit;
- backtest queue saturated;
- timeout;
- resilience test running;
- resilience test failed;
- recovery incomplete;
- cost source estimated;
- cost unavailable;
- budget warning;
- budget exhausted;
- anomaly detected;
- forecast insufficient data;
- scale trigger reached;
- evidence stale;
- schema mismatch;
- unauthorized;
- not found;
- backend unavailable;
- export unavailable.

Missing measurement must not be represented as healthy.

## 49. Responsive Behavior

Requirements:

- environment, revision, freshness, SLO, and blockers remain first;
- charts preserve metric, unit, window, source quality, and sample count;
- tables provide narrow-layout alternatives;
- cost values retain currency and estimate status;
- quota values retain source and reset time;
- percentile and histogram context remains available;
- long service, metric, SLO, test, and provider identifiers wrap or copy safely;
- no critical evidence is hover-only;
- dense charts include accessible summaries and data tables.

## 50. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- keyboard-accessible filters, tables, charts, comparisons, disclosures, and exports;
- text summaries and tabular alternatives for charts;
- visible focus;
- accessible definitions for SLI, SLO, error budget, percentile, quota, headroom, forecast, and estimate states;
- no reliance on color alone;
- status announcements for material changes;
- reflow at 200% and relevant 400% zoom;
- reduced motion;
- screen-reader-readable durations, percentages, costs, units, dates, and confidence ranges;
- safe copy controls.

## 51. Security and Authority Boundaries

The workspace must not:

- expose provider keys, billing credentials, database connection strings, tokens, or secret quota identifiers;
- expose unrestricted raw SQL, prompts, provider responses, financial records, or user identifiers;
- run arbitrary load or fault tests;
- target production research without explicit isolated approval;
- auto-purchase, auto-upgrade, or auto-scale paid resources;
- change budgets, quotas, SLOs, or architecture without authorized versioned commands;
- suppress failed tests or integrity events;
- weaken safety invariants for latency;
- treat free tiers as guaranteed capacity;
- enable live trading or private exchange credentials.

## 52. Privacy and Data Minimization

Metrics, traces, costs, quotas, and test evidence must avoid:

- email addresses and personal identifiers;
- full workspace or resource names when bounded IDs suffice;
- order, fill, ledger, or prompt payloads;
- query parameters containing private values;
- raw search or support text;
- secret names where disclosure increases risk;
- provider billing account details.

High-cardinality identifiers must be allowlisted and retained only when required for incident evidence.

## 53. Observability

The workspace consumes and validates observability evidence; it must also expose safe self-observability for:

- metric ingestion lag;
- dropped or rejected samples;
- definition-version mismatch;
- trace sampling and loss;
- quota snapshot freshness;
- cost ingestion completeness;
- forecast execution outcome;
- test evidence ingestion;
- export status;
- client and workspace versions.

Telemetry about telemetry must still follow privacy and cardinality limits.

## 54. Testing Strategy

### Contract Tests

Validate context, evidence-source, SLI, SLO, error-budget, latency, cycle, quota, database, backtest, resilience, cost, budget, anomaly, forecast, trigger, blocker, and export schemas.

### Metric and SLO Tests

Validate numerator/denominator, percentiles, histograms, windows, exclusions, insufficient samples, burn rates, resets, zero-tolerance invariants, and definition versioning.

### API and Frontend Performance Tests

Validate operation classes, warm/cold requests, timeouts, payload classes, frontend budgets, synthetic profiles, accessibility, and regression comparisons.

### Cycle Performance Tests

Validate intended/actual timing, delay, missed cycles, stage durations, retries, locks, duplicates, reconciliation, and independent Render/GitHub behavior.

### Provider and Quota Tests

Validate Gemini, Binance, Supabase, Render, Cloudflare, and GitHub snapshot sources, stale values, limit changes, rate limits, exhaustion, and safe degradation using fakes and protected snapshots.

### Database Capacity Tests

Validate connections, pooling, transactions, locks, deadlocks, slow queries, indexes, storage growth, query redaction, and saturation behavior in isolated environments.

### Backtest Capacity Tests

Validate event counts, concurrency, queues, memory, CPU, runtime, cancellation, timeout, artifacts, cost, and reconciliation.

### Resilience and Recovery Tests

Validate all required fault categories, invariant preservation, detection, containment, halt, recovery, restore, reconciliation, and measured RTO/RPO evidence.

### Cost and FinOps Tests

Validate usage mapping, pricing versions, billed/estimated distinctions, allocation, unattributed cost, budgets, reservations, commitments, anomalies, unit cost, forecasts, and no-auto-upgrade behavior.

### Security and Privacy Tests

Validate cardinality, redaction, secret absence, no arbitrary load/fault execution, no production targeting, no billing authority, and safe exports.

### Accessibility Tests

Validate keyboard flow, chart summaries, data tables, definitions, focus, announcements, zoom, reflow, contrast, and screen-reader number semantics.

### Visual Regression

Capture healthy, insufficient data, SLO missed, budget burn, cold start, delayed cycle, quota warning/exhausted, connection saturation, backtest limit, resilience failure, cost estimate, anomaly, forecast, and trigger states.

## 55. Acceptance Criteria

Sprint 15 documentation is accepted when:

1. every measurement identifies environment, revision, window, definition version, source quality, sample count, and limitations;
2. SLI definitions and SLO objectives remain separate from raw metrics;
3. free-cloud objectives are not represented as public SLA commitments;
4. error budgets preserve zero-tolerance financial and integrity invariants;
5. API warm/cold latency, errors, and sample adequacy are explicit;
6. Render cold starts remain separated from independent scheduled-cycle execution;
7. cycle intended time, actual start, stage duration, completion, delay, missed, duplicate, and reconciliation evidence is complete;
8. provider quota values are observed or configured snapshots rather than permanent hard-coded assumptions;
9. database, backtest, storage, connection, and resource limits are measured and versioned;
10. resilience tests preserve invariants and measured recovery evidence;
11. billed, provider-reported, free-allowance, estimated, configured, reserved, committed, and unavailable costs remain distinct;
12. budgets fail safely without automatic upgrades;
13. forecasts include uncertainty and do not fabricate results with insufficient data;
14. scale triggers require measured evidence, ADR, migration, security, cost, and approval;
15. no arbitrary load/fault execution, secret exposure, auto-purchase, auto-scale, safety weakening, private exchange, or live-trading authority is introduced;
16. security, privacy, accessibility, performance, reliability, capacity, SLO, quota, resilience, recovery, cost, and export gates are explicit.

## 56. Definition of Done

The Sprint 15 specification is complete when:

- this document is committed;
- `SPRINT_15_TASKS.md` is committed;
- terminology matches free-cloud architecture, production development, observability, testing, experiments, Gemini, portfolio, backtest, governance, developer portal, security, and deployment documents;
- all context, evidence-quality, SLI, SLO, error-budget, API, frontend, cold-start, cycle, market, provider, quota, database, transaction, backtest, resilience, recovery, cost, budget, anomaly, forecast, scale-trigger, export, accessibility, and authority states are explicit;
- both commits are fetched and verified.

## 57. Next Sprint Boundary

Sprint 16 defines the **Data Lifecycle, Dataset Registry, Quality, Retention, Archival, Export, Deletion, Anonymization, and Reproducibility Preservation Workspace**, including immutable dataset versions, lineage, quality gates, retention policies, evidence holds, archival tiers, deletion constraints, user-data separation, reproducibility manifests, and safe dataset promotion without weakening financial or audit integrity.
