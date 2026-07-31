# Sprint 15 Tasks — Performance, Resilience, Capacity, SLO, Cost, Quota, and FinOps Evidence Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement an evidence-first operations workspace that measures API, frontend, scheduled-cycle, market-ingestion, Gemini, database, financial-transaction, and backtest behavior; defines versioned SLIs, SLOs, and error budgets; tracks provider limits and free-tier constraints; validates resilience and recovery; and attributes costs and forecasts capacity without inventing guarantees, weakening invariants, or enabling automatic spend or infrastructure changes.

## Authoritative References

- `docs/PERFORMANCE_RESILIENCE_CAPACITY_FINOPS_WORKSPACE_IMPLEMENTATION.md`
- `docs/OBSERVABILITY.md`
- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `docs/GEMINI_ANALYSIS_VALIDATION_WORKSPACE_IMPLEMENTATION.md`
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`
- `docs/BACKTEST_EXPERIMENT_COMPARISON_WORKSPACE_IMPLEMENTATION.md`
- `docs/AUTH_CONFIGURATION_SECURITY_RELEASE_WORKSPACE_IMPLEMENTATION.md`
- `docs/DEVELOPER_PORTAL_DOCUMENTATION_TRACEABILITY_WORKSPACE_IMPLEMENTATION.md`
- `docs/TESTING.md`
- `docs/SECURITY.md`
- `docs/DEPLOYMENT.md`
- `AGENTS.md`

## S15.1 Define Versioned Operations Schemas

### Objective

Create explicit contracts for context, evidence quality, SLIs, SLOs, error budgets, API, frontend, cycles, database, providers, backtests, resilience, recovery, costs, budgets, anomalies, forecasts, triggers, blockers, and exports.

### Work

- define `PerformanceFinOpsWorkspaceReadModel` and nested schemas;
- define SLO and cost-allocation read models;
- define evidence-source, compliance, budget, quota, forecast, and resilience states;
- require units, windows, revisions, sample counts, source quality, and limitations;
- publish schemas in OpenAPI;
- generate frontend types.

### Acceptance Criteria

- every operational result is machine-readable;
- source quality and sample adequacy are explicit;
- no cost or quota schema exposes credentials;
- compatibility and nullability are versioned;
- contract tests pass.

## S15.2 Implement Operations Context Endpoint

### Objective

Expose environment, workspace, revision, deployment, window, definitions, freshness, completeness, and paper-only state.

### Work

- implement the approved operations aggregate endpoint;
- return environment, scope, revision, deployment, measurement window, observation time, timezone, metric/SLO/cost/quota versions, completeness, stale state, simulation, and live-trading-disabled state;
- enforce authorization;
- prevent incompatible evidence aggregation;
- add safe telemetry.

### Acceptance Criteria

- every result maps to exact revision and environment;
- stale or partial evidence cannot appear current;
- live-trading-disabled remains explicit;
- unauthorized scopes are absent;
- integration tests pass.

## S15.3 Implement Evidence Quality Classification

### Objective

Distinguish measured, provider-reported, billed, estimated, configured, documented, synthetic, inferred, and unavailable evidence.

### Work

- define source-quality registry and version;
- require method, timestamp, sample count, confidence, and limitations;
- validate provider-dashboard versus application-measured sources;
- expose conflicting or stale source state;
- add content definitions.

### Acceptance Criteria

- estimates never appear billed or measured;
- provider reports are labeled;
- unavailable evidence cannot appear healthy;
- classification is server-authoritative;
- tests pass.

## S15.4 Implement SLI Registry

### Objective

Define every service-level indicator with executable measurement semantics.

### Work

- register stable SLI IDs, descriptions, numerator/denominator or aggregation, units, sources, inclusion rules, failures, windows, sampling, environments, versions, owners, tests, and limitations;
- link metrics and traceability;
- reject unnamed or ambiguous SLIs;
- expose list and detail views;
- support lifecycle and deprecation.

### Acceptance Criteria

- a metric name alone cannot satisfy an SLI;
- each SLI has tests and owner;
- definition changes are versioned;
- environments are explicit;
- registry tests pass.

## S15.5 Implement SLO Registry

### Objective

Define internal, experimental, and contractual objectives without false public guarantees.

### Work

- register SLO ID, SLI, target, unit, objective type, environment, window, rolling/calendar semantics, exclusions, error-budget policy, alerts, owner, approval, activation, review, and limitations;
- expose lifecycle and archive state;
- distinguish free-cloud experimental objectives;
- link releases and incidents;
- add validation.

### Acceptance Criteria

- free-cloud objectives are not public SLA claims;
- every SLO uses one versioned SLI;
- exclusions are bounded and approved;
- activation is audited;
- registry tests pass.

## S15.6 Implement Error Budget Engine

### Objective

Calculate allowed, consumed, remaining, and burn-rate evidence server-side.

### Work

- implement period and reset semantics;
- calculate short and long-window burn rates;
- link consuming events and incidents;
- apply approved exclusions;
- handle sample inadequacy;
- freeze permissive interpretation during integrity incidents;
- expose versioned results.

### Acceptance Criteria

- zero-tolerance invariants receive no permissive error budget;
- results are deterministic for the same evidence;
- exclusions are traceable;
- insufficient data is explicit;
- reference tests pass.

## S15.7 Implement SLO and Error-Budget Workspace

### Objective

Present objectives, compliance, remaining budget, burn, incidents, and limitations.

### Work

- render environment, window, objective type, target, result, compliance, budget, burn, exclusions, incidents, evidence, and limitations;
- keep critical and fast-burn states prominent;
- provide accessible charts and tables;
- link runbooks and release blockers;
- support filters and historical comparison.

### Acceptance Criteria

- missed and insufficient-data states remain distinct;
- performance results cannot hide integrity failures;
- charts have text alternatives;
- evidence links are complete;
- accessibility tests pass.

## S15.8 Instrument API Availability and Errors

### Objective

Measure request success, error, timeout, cancellation, rate-limit, denial, dependency, and cold-start outcomes safely.

### Work

- instrument operation ID, endpoint class, method, environment, revision, and safe outcome;
- distinguish expected authorization denials;
- classify dependency and cold-start failures;
- enforce bounded labels;
- expose metric and SLI mappings;
- add tests.

### Acceptance Criteria

- expected denied requests are classified correctly;
- secrets and resource IDs do not become labels;
- every operation maps to a cataloged metric;
- error taxonomy is stable;
- instrumentation tests pass.

## S15.9 Instrument API Latency Distributions

### Objective

Measure warm and cold operation latency with sufficient-sample semantics.

### Work

- record histogram data by approved operation class;
- derive median, P75, P90, P95, P99, minimum, and maximum where valid;
- record processing, dependency, payload, cache, and timeout classes;
- define histogram boundaries and version;
- block percentiles for inadequate samples;
- expose comparisons.

### Acceptance Criteria

- percentiles are mathematically correct;
- warm and cold samples remain separate;
- high-cardinality route values are excluded;
- insufficient samples return unavailable;
- reference tests pass.

## S15.10 Implement Render Cold-Start Evidence

### Objective

Measure interactive API cold starts without conflating them with scheduled research execution.

### Work

- record idle duration when known, request start, readiness, total latency, warm comparison, failure, user impact, sample count, and revision;
- distinguish provider-reported and measured evidence;
- link deployment and incident changes;
- preserve independent GitHub-cycle status;
- expose limitations.

### Acceptance Criteria

- cold-start impact is measurable;
- Render state does not determine cycle success in the model;
- unknown idle duration remains unavailable;
- evidence is revision-linked;
- tests pass.

## S15.11 Implement Frontend Performance Budgets

### Objective

Measure build size, route chunks, loading, interaction, layout, and shell critical-status performance.

### Work

- define JavaScript, CSS, asset, and route budgets;
- collect approved synthetic Web Vitals and optional privacy-reviewed real-user metrics;
- measure authentication bootstrap, shell status, route transition, and search perception;
- separate synthetic and real-user sources;
- link accessibility impacts;
- enforce release thresholds.

### Acceptance Criteria

- synthetic and real-user data remain separate;
- budget failures block applicable release gates;
- no personal or route-private data is collected;
- slow profiles are tested;
- frontend tests pass.

## S15.12 Implement Research-Cycle Reliability Metrics

### Objective

Measure expected, attempted, completed, delayed, missed, duplicate, lock, failure, recovery, and validity outcomes.

### Work

- instrument canonical cycle states;
- calculate latest success, longest gap, consecutive failures, and completeness;
- include revision and configuration hash;
- require reconciliation for financial completion;
- link incidents and workflow runs;
- expose bounded history.

### Acceptance Criteria

- successful process exit alone cannot mark a complete cycle;
- duplicate and lock-rejected states remain visible;
- counts reconcile with cycle records;
- invalidated cycles are not successful;
- integration tests pass.

## S15.13 Implement Schedule Delay Measurement

### Objective

Measure intended versus actual cycle execution under best-effort scheduling.

### Work

- persist intended occurrence, actual start, delay, tolerance version, class, source, provider queue evidence, eligible market event, delayed-action policy, next estimate, and distributions;
- detect missed occurrences;
- avoid exact-time promises;
- link workflow evidence;
- add timezone tests.

### Acceptance Criteria

- intended and actual timestamps remain distinct;
- delay policy is versioned;
- missed cycles cannot be reconstructed as imagined trades;
- next occurrence is labeled estimate;
- scheduling tests pass.

## S15.14 Instrument Cycle Stage Latency

### Objective

Measure every research-cycle stage and dependency.

### Work

- record start, finish, duration, outcome, retries, dependency, and evidence for lock, market, gaps, snapshot, features, budget, Gemini, validation, strategy, risk, execution, ledger, projection, reconciliation, audit, and export stages;
- preserve skipped and unavailable reasons;
- define stage IDs and order;
- detect bottlenecks and regressions;
- avoid unbounded identifiers.

### Acceptance Criteria

- stage totals reconcile with cycle duration within documented overhead;
- skipped stages remain explicit;
- failed stages link to terminal cycle outcome;
- financial completion includes reconciliation;
- latency tests pass.

## S15.15 Implement Market Ingestion and Freshness Performance

### Objective

Measure Binance timing, ingestion, gap repair, snapshot creation, and stale-entry blocking.

### Work

- record finalized candle age, server-time skew, request latency, rows, pages, gaps, repair duration, invalid rows, snapshot duration, freshness, stale blocks, provider errors, and rate limits;
- preserve finalized-data rules;
- link source snapshots;
- define safe provider labels;
- add failure fixtures.

### Acceptance Criteria

- faster processing cannot admit unfinalized data;
- stale entry blocks remain measurable;
- gap repair evidence is complete;
- provider failures degrade safely;
- tests pass.

## S15.16 Implement Gemini Performance and Validity Metrics

### Objective

Measure provider response, application validation, usage, cost, fallback, and budget outcomes separately.

### Work

- instrument provider success, accepted report, rejection categories, attempts, retries, provider latency, validation latency, usage, estimate, fallback, HOLD, and budget-blocked states;
- include provider/model/prompt/schema/validation versions;
- enforce cardinality and privacy policy;
- link analysis evidence;
- expose distributions and trends.

### Acceptance Criteria

- provider success and valid-report rate remain separate;
- retries are fully attributed;
- prompt and raw response content are absent;
- fallback outcomes are measurable;
- tests pass.

## S15.17 Implement Provider Quota Snapshot Registry

### Objective

Track current provider limits, usage, resets, sources, freshness, and uncertainty.

### Work

- support Gemini, Binance, Supabase, Render, Cloudflare, and GitHub resources;
- persist provider, service, project-safe scope, resource, limit, usage, remaining, reset, source, timestamp, freshness, confidence, thresholds, limitations, and version;
- ingest approved APIs, dashboards, configuration, or reviewed documentation snapshots;
- detect provider changes;
- avoid hard-coded permanent values.

### Acceptance Criteria

- every quota value identifies source and observation time;
- stale or unknown limits do not produce headroom;
- provider changes trigger review;
- credentials are absent;
- registry tests pass.

## S15.18 Implement Quota Status and Safe Degradation

### Objective

Classify healthy, warning, near-limit, exhausted, throttled, disabled, stale, unavailable, inconsistent, and changed states.

### Work

- calculate server-authoritative state;
- link budget and fallback policies;
- block optional calls when required;
- create notices and incidents by threshold;
- preserve no-auto-upgrade behavior;
- test reset boundaries.

### Acceptance Criteria

- exhausted optional AI quota degrades to configured fallback;
- inconsistent evidence is critical;
- reset semantics are explicit;
- no provider plan is upgraded automatically;
- policy tests pass.

## S15.19 Implement Supabase Capacity Workspace

### Objective

Expose database storage, connections, transactions, locks, queries, Auth, Data API, pause, and backup/export evidence.

### Work

- ingest approved provider and application metrics;
- render database/table/index size, growth, connections, pool, transactions, waits, deadlocks, slow queries, latency, cache, Auth, Data API, availability, and backup/export state;
- classify evidence source and freshness;
- link migrations and incidents;
- preserve free-tier limitations.

### Acceptance Criteria

- unavailable provider metrics are not fabricated;
- storage and connection headroom is explicit or unavailable;
- service-role details are absent;
- backup guarantees are not overstated;
- integration tests pass.

## S15.20 Implement Database Query Performance Registry

### Objective

Measure normalized operations without exposing raw sensitive SQL.

### Work

- define query/operation IDs;
- collect component, route, calls, latency, rows, index summary, lock time, timeouts, failures, plan hash, revision, and regression state;
- redact SQL and values;
- detect slow and changed plans;
- link source and tasks;
- add thresholds.

### Acceptance Criteria

- no secret or sensitive value appears;
- query IDs are stable;
- plan and latency regressions are traceable;
- thresholds are environment-specific;
- tests pass.

## S15.21 Implement Financial Transaction Performance

### Objective

Measure reservation, fill, ledger, projection, reconciliation, rebuild, conflict, and invariant behavior without weakening atomicity.

### Work

- instrument transaction duration, entry count, projection, reconciliation, rebuild, retries, conflicts, invariant failures, duplicate prevention, sequence, and state versions;
- distinguish successful commit from complete reconciliation;
- link orders, fills, cycles, and incidents;
- use safe bounded labels;
- add property and integration tests.

### Acceptance Criteria

- optimized paths preserve atomicity and decimal precision;
- every fill still links to balanced ledger evidence;
- reconciliation failure remains critical;
- duplicate prevention remains verified;
- performance tests pass.

## S15.22 Implement Backtest Capacity Instrumentation

### Objective

Measure event size, complexity, runtime, throughput, resources, queue, artifacts, and reconciliation.

### Work

- record candles/events, range, symbols, interval, strategy/features, Gemini mode, runtime, events/sec, CPU, memory, reads/writes, artifact size, queue wait, concurrency, timeout, cancellation, reconciliation, environment, and revision;
- preserve immutable run evidence;
- distinguish complete and partial runs;
- link report hash;
- add capacity fixtures.

### Acceptance Criteria

- partial runs cannot appear complete;
- resource measurements identify environment;
- cancellation preserves evidence and accounting;
- events/sec does not hide correctness failures;
- tests pass.

## S15.23 Implement Backtest Resource-Limit Policies

### Objective

Enforce safe per-environment event, range, concurrency, memory, CPU, runtime, output, write, queue, and cost limits.

### Work

- define versioned policies;
- validate before and during runs;
- implement timeout and cancellation behavior;
- return canonical rejection and limit codes;
- link owner approval and configuration;
- expose headroom and limitations.

### Acceptance Criteria

- oversized runs fail before unsafe work where practical;
- concurrency is bounded;
- limits do not imply guaranteed completion;
- cost budgets remain server-authoritative;
- policy tests pass.

## S15.24 Implement Isolated Load and Capacity Profiles

### Objective

Run bounded API, database, cycle, fake-provider, backtest, export, search, and frontend profiles safely.

### Work

- define versioned load profiles and safety bounds;
- target only approved local, CI, or isolated staging environments;
- seed deterministic data;
- capture revision, environment, profile, load, duration, results, invariants, and artifacts;
- prohibit private provider and production targeting;
- add cleanup.

### Acceptance Criteria

- production research is not targeted without separate approval;
- tests cannot create live orders;
- data cleanup is deterministic;
- invariant results accompany performance results;
- security tests pass.

## S15.25 Implement Resilience Test Registry

### Objective

Catalog required provider, scheduler, cold-start, database, transaction, process, export, restore, frontend, deployment, and observability fault tests.

### Work

- define profile ID, category, fault, targets, expected behavior, safety bounds, invariants, recovery, owner, version, review, and environment;
- map runbooks and incidents;
- preserve disabled and deferred tests;
- detect missing critical profiles;
- expose filters.

### Acceptance Criteria

- every critical failure mode has a test or explicit gap;
- test faults and environments are bounded;
- live trading remains impossible;
- registry is revision-linked;
- tests pass.

## S15.26 Implement Resilience Test Execution Evidence

### Objective

Persist fault, load, observed behavior, recovery, integrity, and SLI effects.

### Work

- record run ID, profile, revision, environment, targets, injection, bounds, timing, expected/observed, invariants, SLI impact, recovery, integrity, audit, incidents, artifacts, outcome, and limitations;
- preserve failures;
- support comparison;
- enforce redaction;
- link release gates.

### Acceptance Criteria

- failed tests remain visible;
- invariant failure overrides latency success;
- evidence identifies exact revision;
- secret-bearing artifacts are excluded;
- ingestion tests pass.

## S15.27 Implement Recovery Time and RPO/RTO Evidence

### Objective

Measure detection, containment, halt, restoration, reconciliation, user recovery, and data-loss intervals.

### Work

- persist each recovery milestone;
- compare measured results with versioned targets;
- link runbooks, incidents, backups, releases, and tests;
- distinguish service restoration from financial integrity restoration;
- record unresolved limitations;
- avoid aspirational substitution.

### Acceptance Criteria

- measured and target values remain separate;
- recovery is incomplete until reconciliation where applicable;
- data loss interval is evidence-backed;
- failed restore remains critical;
- tests pass.

## S15.28 Implement Cost Source and Pricing Registry

### Objective

Track billed, provider-reported, allowance, estimated, configured, reserved, committed, and unavailable costs.

### Work

- register provider, service, pricing-reference version, usage unit, derivation, currency, tax state, timestamps, and uncertainty;
- preserve pricing changes;
- avoid hard-coded stale pricing in calculations;
- ingest approved billing or usage evidence;
- enforce role-based detail minimization.

### Acceptance Criteria

- estimates never appear as invoices;
- every cost references pricing version;
- unavailable billing remains explicit;
- credentials and account details are absent;
- registry tests pass.

## S15.29 Implement Cost Allocation Engine

### Objective

Allocate costs across provider, environment, workspace, experiment, cycle, analysis, backtest, export, storage, workflow, overhead, and unattributed categories.

### Work

- define allocation keys and versioned approximation rules;
- calculate server-side;
- preserve unattributed amounts;
- reconcile allocations to source totals within documented precision;
- link usage and resource identities safely;
- expose source quality and limitations.

### Acceptance Criteria

- allocations reconcile or show mismatch;
- unattributed cost is never hidden;
- shared-cost rules are transparent;
- private identifiers are minimized;
- reference tests pass.

## S15.30 Implement Budget Registry and Enforcement Evidence

### Objective

Track amount, reservations, commitments, billing, forecast, thresholds, reset, approval, and safe degradation.

### Work

- implement budget read models for provider, environment, workspace, experiment, analysis, and backtest scopes;
- preserve baseline EUR 0 required infrastructure and Gemini paid-use defaults;
- apply concurrency-safe checks;
- link quota and fallback states;
- enforce no-auto-upgrade;
- audit material changes.

### Acceptance Criteria

- optional paid use cannot occur without approved configuration;
- concurrent reservations cannot bypass budget;
- resets are deterministic;
- exhausted budgets degrade safely;
- budget tests pass.

## S15.31 Implement Cost and Budget Workspace

### Objective

Present source totals, allocations, unattributed amounts, budgets, forecasts, anomalies, and limitations.

### Work

- render periods, currency, source status, allocations, budgets, reservations, commitments, billed values, remaining amounts, pricing references, and limitations;
- link experiments, cycles, analyses, backtests, and releases;
- provide accessible charts and tables;
- preserve estimate labels;
- support authorized export.

### Acceptance Criteria

- estimate, allowance, budget, and billed values remain distinct;
- unattributed amount is visible;
- no sensitive account data appears;
- charts have tabular alternatives;
- accessibility tests pass.

## S15.32 Implement Cost Anomaly Detection

### Objective

Detect material deviations without misleading small-denominator severity.

### Work

- define baseline methods and sample rules;
- calculate expected range, observed value, absolute/relative difference, confidence, and severity;
- link releases, experiments, providers, incidents, and configurations;
- require review and resolution evidence;
- handle incomplete billing.

### Acceptance Criteria

- insufficient data does not create confident anomaly;
- small denominators are handled safely;
- every anomaly has source evidence;
- resolution is audited;
- anomaly tests pass.

## S15.33 Implement Unit Cost Metrics

### Objective

Measure cost per successful cycle, validated report, experiment day, backtest, workspace, export, retained evidence, and release.

### Work

- define metric formulas, sources, allocation rules, samples, units, versions, and limitations;
- preserve successful versus attempted denominator semantics;
- link cost and reliability evidence;
- reject undefined denominators;
- avoid user-billing claims.

### Acceptance Criteria

- unit metrics identify assumptions;
- undefined values remain null;
- failed attempts are not silently excluded;
- metrics are not invoices;
- reference tests pass.

## S15.34 Implement Free-Tier Constraint Registry

### Objective

Track mutable external constraints, exhaustion behavior, fallback, and promotion impact.

### Work

- register provider, service, tier, constraint, observed/documented value, unit, source, review time, change risk, behavior, usage, headroom, fallback, impact, owner, and next review;
- mark unknown or stale values;
- link quota snapshots;
- create review reminders;
- preserve history.

### Acceptance Criteria

- free tiers are not permanent architecture guarantees;
- stale constraints block confident capacity claims;
- provider changes are visible;
- fallback is documented;
- registry tests pass.

## S15.35 Implement Capacity Headroom Engine

### Objective

Calculate headroom only from compatible observed or configured limits and usage.

### Work

- compare peak and sustained use with limit, burst, warning, and critical thresholds;
- include period, source quality, recovery, and limitations;
- return unavailable for unknown limits;
- support database, provider, storage, workflow, backtest, and frontend resources;
- add boundary tests.

### Acceptance Criteria

- unknown limit never means infinite capacity;
- peak and sustained headroom remain distinct;
- source and window are explicit;
- negative headroom is critical;
- reference tests pass.

## S15.36 Implement Capacity Forecasts

### Objective

Forecast threshold ranges with uncertainty and no fabricated extrapolation.

### Work

- define methods, history requirements, drivers, horizons, scenarios, ranges, confidence, thresholds, estimated dates, owners, decisions, and limitations;
- reject insufficient data;
- preserve historical forecasts and outcomes;
- link scale triggers;
- support comparison.

### Acceptance Criteria

- forecasts return ranges rather than false precision;
- assumptions are visible;
- insufficient data yields no forecast;
- changed methods are versioned;
- forecast tests pass.

## S15.37 Implement Scale Trigger Registry and Evaluation

### Objective

Determine when measured evidence justifies architecture investigation.

### Work

- define triggers for error budgets, connections, storage, queries, cycle duration, backtest queues, quotas, recovery, cold starts, retention, cost, and operational burden;
- require duration, confidence, environment, options, ADR, cost, migration, security, and approval state;
- evaluate server-side;
- preserve unmet and historical triggers;
- prohibit automatic activation.

### Acceptance Criteria

- trigger outcomes are evidence-backed;
- reaching a trigger does not auto-scale or spend;
- architecture changes require ADR and governance;
- false trigger due to stale data is prevented;
- tests pass.

## S15.38 Implement Performance Regression Comparison

### Objective

Compare compatible revisions, environments, load profiles, and windows.

### Work

- compare baseline and candidate metric/SLI values;
- validate compatible definitions and samples;
- calculate absolute and relative change;
- classify severity and affected components;
- link task, release, and approval;
- require invariant results.

### Acceptance Criteria

- incompatible comparisons fail closed;
- safety or correctness regression overrides speed improvement;
- sample adequacy is explicit;
- source revisions are immutable;
- regression tests pass.

## S15.39 Implement Incident, Release, and Runbook Correlation

### Objective

Trace reliability and cost changes to deployments, configurations, incidents, providers, migrations, experiments, and recovery.

### Work

- link metric windows to releases and deployments;
- link anomalies and SLO burn to incidents;
- link remediation to runbook executions and rollbacks;
- support before/after views;
- validate compatible windows and definitions;
- preserve causality as evidence, not assumption.

### Acceptance Criteria

- correlations identify supporting evidence;
- temporal proximity alone is labeled inference;
- rollback and forward-fix outcomes are visible;
- unresolved incidents remain prominent;
- traceability tests pass.

## S15.40 Implement Authorized Operations Export

### Objective

Generate provenance-preserving SLO, performance, quota, capacity, resilience, recovery, cost, forecast, and trigger packages.

### Work

- generate server-side JSON and approved derivatives;
- include schema/definition versions, environment, revision, windows, source quality, units, samples, blockers, incidents, limitations, and authorization context;
- enforce redaction;
- preserve failed tests and exhausted states;
- include integrity manifest.

### Acceptance Criteria

- critical evidence cannot be omitted;
- exports identify exact revision and definitions;
- secrets, billing credentials, and private payloads are absent;
- source hashes are verifiable;
- export tests pass.

## S15.41 Add Explicit State Handling

### Objective

Define safe rendering for measurement, SLO, quota, capacity, resilience, cost, forecast, and trigger states.

### Work

- implement loading, no measurement, insufficient sample, healthy, warning, SLO missed, fast burn, exhausted budget, cold start, delayed/missed cycle, quota warning/exhausted/unavailable, connection/storage/backtest saturation, timeout, resilience running/failed, recovery incomplete, estimated/unavailable cost, anomaly, insufficient forecast, trigger reached, stale evidence, schema mismatch, unauthorized, not found, backend unavailable, and export failure;
- define bounded retry;
- distinguish unknown from healthy;
- label cached evidence by revision.

### Acceptance Criteria

- missing measurement never appears healthy;
- critical integrity states remain first;
- retries do not hide deterministic failures;
- stale data is explicit;
- state-matrix tests pass.

## S15.42 Add Responsive and Accessibility Verification

### Objective

Ensure operational charts, tables, definitions, and comparisons remain usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom;
- test headings, landmarks, filters, charts, text summaries, data tables, comparisons, disclosures, exports, focus, announcements, definitions, and copy controls;
- verify reduced motion and contrast;
- test long metric, SLO, provider, test, and cost labels;
- record screen-reader spot checks.

### Acceptance Criteria

- every chart has equivalent text/table evidence;
- no state relies only on color;
- units and estimate status are announced;
- context survives narrow layouts;
- no critical automated violation remains;
- manual evidence is recorded.

## S15.43 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make measurement integrity, cardinality, safe quotas, bounded resilience tests, cost authority, and no-auto-scale boundaries release-blocking.

### Work

- add contract, evidence, SLI, SLO, error-budget, API, frontend, cold-start, cycle, schedule, market, Gemini, quota, database, transaction, backtest, load, resilience, recovery, cost, allocation, budget, anomaly, unit-cost, constraint, headroom, forecast, trigger, regression, correlation, route, E2E, accessibility, visual, authorization, and export tests;
- add secret, billing, identifier, raw-SQL, prompt, payload, arbitrary-load, production-target, auto-purchase, auto-scale, and live-trading checks;
- instrument safe ingestion and workspace self-observability;
- test prohibited telemetry fields;
- link critical failures to release gates.

### Acceptance Criteria

- zero-tolerance invariants remain release-blocking;
- arbitrary load/fault execution and production targeting fail closed;
- no browser or AI path gains quota, budget, purchase, scaling, provider, private exchange, testnet, or live-trading authority;
- telemetry contains no prohibited fields;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Contracts | Context, evidence quality, SLI, SLO, budget, latency, quota, database, backtest, resilience, cost, forecast, trigger, blocker, and export tests |
| Reliability | API availability/errors, cold starts, cycle completeness, schedule delay, stages, market freshness, Gemini validity, reconciliation, and zero-duplicate tests |
| Capacity | Supabase storage/connections/queries, financial transactions, backtest resources/limits, load profiles, headroom, and saturation tests |
| Resilience | Provider, scheduler, Render, Supabase, database, transaction, process, export, restore, frontend, deployment, observability, RTO/RPO, and invariant tests |
| FinOps | Source classification, pricing versions, allocations, unattributed cost, budgets, concurrency, anomalies, unit costs, free-tier constraints, forecasts, and no-auto-upgrade tests |
| Governance | Scale triggers, ADR boundary, migration/security/cost approval, incident/release correlation, retention, and authorized export tests |
| Accessibility and security | Keyboard, chart alternatives, zoom, redaction, cardinality, no arbitrary tests, no credentials, no purchase/scale authority, and telemetry tests |

## Sprint Exit Gate

Sprint 15 is complete only when:

- S15.1 through S15.43 are implemented and verified;
- every measurement identifies environment, revision, window, definition, source quality, sample count, unit, and limitations;
- SLIs, SLOs, and raw metrics remain separate;
- free-cloud objectives are not represented as public SLAs;
- error budgets do not weaken zero-tolerance financial and integrity invariants;
- API warm/cold behavior and frontend budgets are measured;
- Render cold starts remain independent from scheduled-cycle authority;
- cycle intended/actual timing, delay, stages, completion, duplicate prevention, and reconciliation are measured;
- provider quotas are current snapshots rather than hard-coded permanent assumptions;
- database, transaction, backtest, storage, connection, and resource limits are measured and versioned;
- resilience tests preserve invariants and measured recovery evidence;
- cost sources, allocations, budgets, estimates, allowances, billed values, and unattributed amounts remain distinct;
- free-tier constraints and provider changes are reviewed;
- forecasts expose uncertainty and return no result for insufficient evidence;
- scale triggers require measured evidence, ADR, migration, security, cost, and approval and never auto-activate infrastructure;
- no browser or AI arbitrary load/fault, production-target, quota, billing, purchase, auto-scale, private exchange, testnet, or live-trading authority exists;
- accessibility, responsive, security, privacy, contract, SLI, SLO, performance, reliability, quota, capacity, resilience, recovery, FinOps, forecast, regression, E2E, export, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 16 defines and implements the Data Lifecycle, Dataset Registry, Quality, Retention, Archival, Export, Deletion, Anonymization, and Reproducibility Preservation Workspace.
