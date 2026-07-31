# Sprint 9 Tasks — Backtest, Benchmark, Reproducibility, and Experiment Comparison Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a read-only research workspace that exposes immutable backtest configuration, dataset and code provenance, replay methodology, costs, metrics, benchmarks, trade and ledger lineage, robustness evidence, reproducibility verification, and backtest-to-paper comparison without enabling automatic promotion, live execution, or browser-side authoritative calculations.

## Authoritative References

- `docs/BACKTEST_EXPERIMENT_COMPARISON_WORKSPACE_IMPLEMENTATION.md`
- `docs/BACKTEST_ENGINE.md`
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`
- `docs/PAPER_TRADING.md`
- `docs/PORTFOLIO_ENGINE.md`
- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`
- `docs/MARKET_EVIDENCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/GEMINI_INTEGRATION.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `docs/OBSERVABILITY.md`
- `AGENTS.md`

## S9.1 Define Versioned Backtest Workspace Schemas

### Objective

Create explicit contracts for run identity, status, immutable configuration, dataset provenance, methodology, metrics, benchmarks, series, trades, events, ledger, reconciliation, robustness, reproducibility, comparisons, warnings, limitations, and links.

### Work

- define `BacktestWorkspaceReadModel` and nested schemas;
- define reproducibility and comparison read models;
- use decimal strings and explicit units for financial and statistical values;
- define null, insufficient-sample, incomplete, warning, and unavailable states;
- include data, code, dependency, migration, strategy, risk, execution, accounting, feature, Gemini, and report versions;
- publish schemas in OpenAPI.

### Acceptance Criteria

- authoritative metrics never use JSON floating point;
- every metric exposes definition and unit metadata;
- null values include machine-readable reasons;
- compatibility behavior is explicit;
- contract tests pass.

## S9.2 Implement Backtest List Endpoint

### Objective

Expose bounded, filterable research-run history.

### Work

- implement `GET /api/v1/backtests` or the approved workspace-scoped equivalent;
- support filters for status, symbol, interval, period, split category, strategy, risk, execution, accounting, Gemini mode, benchmark set, reproducibility, warning code, and experiment;
- use cursor pagination and safe sort options;
- include completeness, reconciliation, warning, and report state summaries;
- enforce authorization and RLS;
- add latency and result-count telemetry.

### Acceptance Criteria

- completed, failed, cancelled, timed-out, and partial runs remain discoverable;
- filters are bounded and server-approved;
- pagination does not fabricate totals;
- unauthorized runs are not exposed;
- API tests pass.

## S9.3 Implement Backtest Detail Endpoint

### Objective

Return the complete persisted workspace projection for one backtest.

### Work

- implement `GET /api/v1/backtests/{backtest_id}`;
- return identity, status, configuration, dataset, methodology, reproducibility, metric summaries, benchmarks, series references, trade summary, costs, risk events, reconciliation, robustness, warnings, diagnostics, limitations, and links;
- classify missing required provenance and report evidence;
- map safe errors and correlation IDs;
- enforce authorization and RLS.

### Acceptance Criteria

- identical persisted evidence produces an identical response;
- complete and partial results cannot be confused;
- missing provenance fails closed;
- current status and terminal state are explicit;
- integration tests pass.

## S9.4 Implement Backtest Routes and Navigation

### Objective

Add backtest list, detail, report, trades, events, ledger, reproducibility, and comparison routes.

### Work

- implement the approved canonical route family;
- add application-shell navigation;
- add cross-links from strategies, decisions, portfolio, experiments, and audit lineage;
- preserve approved filters and comparison selections in URL state;
- add route-level error boundaries;
- prohibit mutation and promotion controls.

### Acceptance Criteria

- routes are directly addressable and keyboard reachable;
- refresh preserves stable read state;
- invalid IDs and filters fail safely;
- no live-execution or automatic-promotion control exists;
- route tests pass.

## S9.5 Implement Run Identity and Safety Header

### Objective

Present simulation, completeness, data quality, reconciliation, reproducibility, and warning state before performance.

### Work

- render run, workspace, symbol, interval, range, split, configuration, code commit, report hash, and timestamps;
- render status, completeness, reconciliation, reproducibility, data-quality, and warning components;
- render simulation and non-guarantee labels;
- expose local time with accessible UTC;
- preserve critical state at narrow widths.

### Acceptance Criteria

- incomplete, failed, unreconciled, or non-reproducible results cannot appear ordinary;
- positive return never overrides warnings;
- run identity and report hash are inspectable;
- simulation is always explicit;
- responsive and accessibility tests pass.

## S9.6 Implement Run Progress and Terminal-State Presentation

### Objective

Expose persisted progress and safe terminal outcomes.

### Work

- render queued, validating, running, reconciling, report-generation, completed, failed, cancelled, and timed-out states;
- render processed and eligible event counts where known;
- render queue wait, duration, replay cursor, terminal reason, partial-result state, and report state;
- announce material changes accessibly;
- prevent fabricated progress.

### Acceptance Criteria

- progress comes from persisted work units;
- indeterminate progress is labeled;
- partial results remain prominent;
- terminal reason codes are inspectable;
- state tests pass.

## S9.7 Implement Immutable Configuration Panel

### Objective

Expose every frozen input that defines the run.

### Work

- render workspace configuration version and hash;
- render market, interval, range, initial capital, and base currency;
- render dataset, symbol metadata, feature, strategy, risk, execution, accounting, benchmark, Gemini, random-seed, replay-clock, timeout, and resource-policy versions;
- link to immutable resources;
- classify inconsistent references.

### Acceptance Criteria

- no used configuration is implicit;
- hashes and versions are copyable and accessible;
- running and completed configuration cannot appear mutable;
- inconsistent lineage fails closed;
- contract and component tests pass.

## S9.8 Implement Dataset Provenance Panel

### Objective

Present historical-data eligibility, quality, completeness, and hash evidence.

### Work

- render exchange, symbol, interval, requested and actual range, candle count, finalized status, quality state, gap count, handling policy, dataset IDs, dataset hash, metadata versions, and source references;
- explain excluded, replaced, missing, or rejected data;
- link to market evidence;
- expose timezone and calendar assumptions;
- sanitize source diagnostics.

### Acceptance Criteria

- finalized-data status is explicit;
- data gaps cannot be hidden;
- dataset hash and metadata versions are visible;
- unavailable provenance is critical;
- integration tests pass.

## S9.9 Implement Dataset Split and Leakage Evidence

### Objective

Make design, validation, final test, and walk-forward usage explicit.

### Work

- render split category, range, policy version, parameter-selection use, untouched-test status, and related artifacts;
- render overlap and leakage checks;
- render walk-forward training and validation windows;
- warn when a final test period influenced selection;
- expose comparison compatibility.

### Acceptance Criteria

- split purpose is understandable without hidden methodology;
- overlap and leakage warnings are prominent;
- untouched-test claims are evidence-backed;
- window ordering is deterministic;
- split tests pass.

## S9.10 Implement Replay Methodology and No-Look-Ahead Panel

### Objective

Expose event timing and executable research constraints.

### Work

- render replay clock, finalized-data, snapshot, feature, Gemini, strategy, risk, order-processing, activation, market-fill, limit-fill, intrabar, partial-fill, cost, precision, ledger, reconciliation, and failure rules;
- render no-look-ahead assertion status;
- link to execution-model and test evidence;
- classify missing methodology versions.

### Acceptance Criteria

- next-event behavior is explicit;
- same-event or future-data leakage cannot appear acceptable;
- execution assumptions are versioned;
- missing required rules fail closed;
- methodology content tests pass.

## S9.11 Implement Gemini Replay Evidence

### Objective

Distinguish disabled, precomputed, and sampled-research Gemini modes.

### Work

- render mode, dataset, model, prompt, schema, validation, snapshot mapping, report hashes, cost, and limitations where applicable;
- verify exact snapshot compatibility for precomputed reports;
- render provider-drift and reproducibility warnings for sampled research;
- prohibit silent live calls in ordinary runs;
- link to Gemini evidence.

### Acceptance Criteria

- every run has an explicit Gemini mode;
- incompatible reports fail closed;
- sampled research is not presented as deterministic baseline evidence;
- secrets and unrestricted prompts are absent;
- contract and integration tests pass.

## S9.12 Implement Metric Definition Registry and Endpoint

### Objective

Make every displayed metric machine-readable, versioned, and explainable.

### Work

- define canonical metric codes;
- expose formula version, unit, sampling frequency, annualization, risk-free assumption, gross/net classification, sample requirements, and null conditions;
- implement approved metric metadata endpoint or embed versioned definitions;
- validate report metrics against definitions;
- add reference fixtures.

### Acceptance Criteria

- each metric maps to one versioned definition;
- units and formulas cannot be inferred ambiguously;
- undefined metrics include explicit reasons;
- breaking definition changes require versioning;
- reference tests pass.

## S9.13 Implement Performance and Risk Metric Summary

### Objective

Present complete net, gross, risk, exposure, and trade metrics without misleading precision.

### Work

- render initial and final equity, gross and net return, P&L, maximum drawdown, volatility, Sharpe, Sortino, win/loss rates, average win/loss, profit factor, trade count, exposure, turnover, fees, slippage, holding period, losing sequence, halts, and rejections;
- render units, sample counts, definitions, periods, warnings, and null reasons;
- link to authoritative report data;
- avoid browser calculations.

### Acceptance Criteria

- gross and net results remain separate;
- undefined and insufficient-sample metrics remain null;
- percentages and decimals preserve contract precision;
- warning state is accessible without color;
- metric tests pass.

## S9.14 Implement Required Benchmark Comparison

### Objective

Compare results with cash and buy-and-hold using compatible assumptions.

### Work

- render benchmark code, version, capital, period, data hash, timing, valuation, fee, spread, slippage, precision, minimum-notional, metrics, and limitations;
- render excess return and risk differences where persisted;
- validate comparison compatibility;
- link to benchmark evidence;
- use non-promotional language.

### Acceptance Criteria

- cash and buy-and-hold are always present for complete runs;
- assumptions are visible and comparable;
- incompatibility is explicit;
- a benchmark is not framed as advice;
- benchmark tests pass.

## S9.15 Implement Equity, Drawdown, Exposure, and Cost Series

### Objective

Present authoritative time-series evidence with accessible summaries.

### Work

- render equity, benchmark equity, drawdown, exposure, cumulative fees, cumulative slippage, and approved position series;
- consume server-provided series and display metadata;
- support approved display downsampling without changing authoritative data;
- provide text summaries and tabular alternatives;
- link to authorized full-resolution export.

### Acceptance Criteria

- charts preserve units, period, sampling, and benchmark identity;
- downsampling is labeled;
- authoritative metrics do not depend on chart pixels;
- gaps and interpolation policies are explicit;
- visual and accessibility tests pass.

## S9.16 Implement Trade List and Detail

### Objective

Expose complete trade episodes and financial lineage.

### Work

- render winning, losing, breakeven, incomplete, open, and cancelled-remainder cases;
- render entry and exit times, quantities, prices, gross and net P&L, fees, costs, holding period, reasons, and state;
- link strategy, risk, orders, fills, ledger, portfolio states, valuation, reconciliation, and market evidence;
- use cursor pagination and approved filters;
- provide mobile semantic details.

### Acceptance Criteria

- incomplete episodes are not hidden;
- gross and net P&L remain separate;
- every material amount links to evidence;
- lineage failures are critical;
- trade integration and accessibility tests pass.

## S9.17 Implement Replay Event Explorer

### Objective

Expose deterministic event order and decisions across the historical replay.

### Work

- render replay clock, snapshot, feature, Gemini, strategy, risk, order, fill, ledger, reconciliation, halt, warning, cancellation, and failure events;
- render event sequence, timestamp, status, version references, reason codes, and links;
- support bounded filters and cursor pagination;
- classify missing required sequence or evidence;
- sanitize diagnostics.

### Acceptance Criteria

- event ordering is deterministic;
- missing required lineage fails closed;
- future data is not exposed to earlier events;
- critical events are not collapsed by default;
- explorer tests pass.

## S9.18 Implement Ledger and Reconciliation Views

### Objective

Prove accounting conservation and final-state validity.

### Work

- render initial funding, reservations, fills, fees, releases, realized P&L, final valuation, ledger sequence, state hashes, and reconciliation runs;
- link to portfolio accounting specifications;
- render matched, mismatch, and unable-to-reconcile outcomes;
- stop final-report presentation on failed reconciliation according to policy;
- expose invariant failures.

### Acceptance Criteria

- unreconciled performance cannot appear final;
- ledger sequence and state hashes are inspectable;
- every fill has accounting evidence;
- mismatch references canonical reasons;
- accounting and reconciliation tests pass.

## S9.19 Implement Warning and Failure Explorer

### Objective

Make every limitation, warning, and terminal failure traceable.

### Work

- define canonical warning and failure codes;
- render category, severity, scope, explanation, evidence, timestamp, and impact;
- cover data gaps, leakage, sample limits, undefined metrics, missing benchmarks, look-ahead, configuration, Gemini, execution, accounting, reconciliation, resource, timeout, cancellation, incomplete report, and reproducibility failures;
- prevent critical collapse;
- sanitize content.

### Acceptance Criteria

- every terminal failure has a canonical code;
- every material warning explains affected outputs;
- critical warnings remain visible;
- hostile content is sanitized;
- warning accessibility tests pass.

## S9.20 Implement Tested-Variant and Anti-Overfitting Disclosure

### Objective

Expose selection context rather than only the chosen result.

### Work

- render strategy, parameter, symbol, period, cost, and methodology variants tested;
- render selected, rejected, failed, cancelled, and incomplete variants;
- render train, validation, and final-test use;
- render parameter-selection policy and material manual choices;
- render selection-bias warnings;
- link to related runs.

### Acceptance Criteria

- failed and unfavorable variants remain discoverable;
- the selected run is not shown without tested-range context;
- final-test contamination is warned;
- variant counts are evidence-backed;
- anti-overfitting tests pass.

## S9.21 Implement Parameter Sensitivity and Robustness Views

### Objective

Show whether conclusions survive nearby assumptions and periods.

### Work

- render changed and unchanged inputs;
- compare nearby parameters, costs, periods, regimes, symbols, delays, walk-forward windows, and approved stress cases;
- render compatibility, sample counts, metric changes, warning changes, and limitations;
- prohibit unsupported rankings;
- link to source runs and reports.

### Acceptance Criteria

- every robustness result identifies changed inputs;
- incompatible results are blocked or labeled;
- no single best value is promoted without range context;
- insufficient samples remain explicit;
- comparison tests pass.

## S9.22 Implement Reproducibility Verification Endpoint and View

### Objective

Compare an original run with an identical repeated run.

### Work

- compare configuration hash, dataset hash, code commit, dependency lock, migration revision, seed, event count and order, trades, ledger sequence, state hashes, metrics, benchmarks, and report hash;
- return verified, mismatch, incomplete, or not-run outcome;
- render machine-readable differences;
- preserve both immutable runs;
- add safe telemetry.

### Acceptance Criteria

- approximate display rounding cannot hide mismatches;
- verified requires all required comparisons;
- mismatch differences are traceable;
- incomplete reruns do not verify;
- deterministic repeat tests pass.

## S9.23 Implement Backtest Comparison Workspace

### Objective

Compare compatible runs without mutating source evidence.

### Work

- support comparison across strategy, risk, execution, accounting, feature, data, period, symbol, parameter, cost, and Gemini dimensions;
- validate compatibility;
- render configuration, dataset, metric, series, trade, cost, halt, rejection, warning, robustness, and reproducibility differences;
- preserve original identities;
- support authorized export.

### Acceptance Criteria

- changed and unchanged dimensions are explicit;
- misleading incompatible comparisons fail closed;
- source runs remain immutable;
- every metric difference preserves unit and definition version;
- comparison tests pass.

## S9.24 Implement Backtest-to-Paper Experiment Comparison

### Objective

Explain differences between historical replay and forward paper observation.

### Work

- validate strategy, risk, execution, accounting, feature, market, and interval compatibility;
- render period, data source, schedule, missing cycle, cloud runtime, Gemini, latency, cost, valuation, return, drawdown, exposure, turnover, trade, halt, rejection, reconciliation, and incident differences;
- explain methodological differences;
- link to paper portfolio and experiment evidence;
- avoid promotional interpretation.

### Acceptance Criteria

- historical and forward evidence are not conflated;
- compatibility and normalization are explicit;
- experiment incidents and missing cycles remain visible;
- differences are server-provided;
- cross-mode comparison tests pass.

## S9.25 Implement Promotion-Evidence Boundary

### Objective

Support manual research review without automatic lifecycle changes.

### Work

- render evidence checklist for strategy lifecycle review;
- include backtest, validation, final test, robustness, reproducibility, paper observation, security, testing, and owner-approval requirements;
- render missing gates;
- link to strategy lifecycle records when available;
- prohibit activation, policy changes, order creation, testnet, or live execution.

### Acceptance Criteria

- no positive result triggers promotion;
- missing gates remain explicit;
- owner approval remains separate;
- live-trading state cannot be reached;
- authority tests pass.

## S9.26 Implement Authorized Backtest Export

### Objective

Generate provenance-preserving research packages.

### Work

- support authoritative JSON and approved HTML, Markdown, and CSV derivatives;
- include identity, simulation disclaimer, configuration, dataset, code, dependencies, migrations, methods, metric definitions, benchmarks, series, trades, events, ledger, reconciliation, robustness, reproducibility, comparisons, warnings, completeness, report hash, and limitations;
- generate server-side;
- enforce authorization and RLS;
- record safe telemetry.

### Acceptance Criteria

- JSON remains authoritative;
- critical warnings and incomplete state cannot be omitted;
- no secret or unsafe environment detail appears;
- stable report hashes are verified where required;
- export tests pass.

## S9.27 Add Explicit State Handling

### Objective

Define rendering for every run and comparison state.

### Work

- implement loading, empty, queued, validating, running, reconciling, generating, complete, failed, cancelled, timed out, partial, missing report, invalid dataset, gap warning, leakage warning, insufficient sample, undefined metric, missing benchmark, look-ahead failure, Gemini mismatch, accounting failure, reconciliation failure, reproducibility mismatch, incompatible comparison, schema mismatch, unauthorized, not found, backend unavailable, and export failure states;
- define safe retry policy;
- prevent infinite retries;
- label cached data stale.

### Acceptance Criteria

- critical states never render as ordinary complete results;
- loading fabricates no metrics;
- retries are bounded and appropriate;
- stale cached data is explicit;
- state-matrix tests pass.

## S9.28 Add Responsive and Accessibility Verification

### Objective

Ensure dense research evidence is usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom layouts;
- test headings, landmarks, focus, keyboard operation, charts, summaries, tables, definitions, warnings, comparisons, lineage, and copy controls;
- provide chart text alternatives;
- verify reduced motion and contrast;
- record screen-reader spot checks;
- test long hashes, versions, metric names, and warning codes.

### Acceptance Criteria

- no critical evidence is hover-only;
- charts have accessible summaries;
- no outcome relies only on color;
- table context remains available at narrow widths;
- no critical automated violation remains;
- manual evidence is recorded.

## S9.29 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make reproducibility, no-look-ahead, immutable research evidence, and authority boundaries release-blocking.

### Work

- add contract, integration, metric, benchmark, reproducibility, split, leakage, robustness, comparison, route, E2E, accessibility, visual, export, authorization, and RLS tests;
- add sandbox, resource-limit, hostile-content, secret, and unsafe-path checks;
- verify no browser strategy-code execution, mutation, promotion, provider-secret, order, or live-trading path exists;
- instrument safe run, warning, failure, queue, performance, reconciliation, report, reproducibility, comparison, and export metrics;
- test prohibited telemetry fields;
- verify deterministic fixtures and no paid provider calls in normal CI.

### Acceptance Criteria

- no-look-ahead and deterministic-repeat tests pass;
- unauthorized access fails closed;
- failed and unfavorable evidence remains discoverable;
- no AI or browser path gains promotion or execution authority;
- telemetry contains no prohibited fields;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| API contracts | OpenAPI, schema, enum, decimal, unit, timestamp, null, warning, link, and compatibility tests |
| Provenance | Dataset, metadata, code, dependency, migration, feature, strategy, risk, execution, accounting, Gemini, seed, and report-hash tests |
| Methodology | Finalized data, replay clock, next-event, no-look-ahead, fill timing, cost, precision, ledger, and reconciliation tests |
| Metrics | Return, P&L, drawdown, volatility, ratios, trade statistics, exposure, turnover, costs, null, and sample tests |
| Benchmarks | Cash, buy-and-hold, comparable assumptions, timing, costs, valuation, and report-hash tests |
| Research quality | Split, overlap, leakage, variants, sensitivity, walk-forward, robustness, and selection-bias tests |
| Reproducibility | Repeated-run hashes, event ordering, trades, ledger sequence, state hashes, metrics, benchmarks, and report tests |
| Comparison | Compatibility, changed inputs, metrics, series, trades, costs, warnings, paper experiment, and immutable-source tests |
| Accessibility | Keyboard, charts, summaries, tables, definitions, warnings, comparison, zoom, reflow, and manual review |
| Security and privacy | RLS, authorization, sandbox, resource limits, sanitization, no-mutation, no-promotion, no-live-trading, secret scan, and telemetry tests |

## Sprint Exit Gate

Sprint 9 is complete only when:

- S9.1 through S9.29 are implemented and verified;
- every run identifies immutable dataset, code, dependency, migration, feature, strategy, risk, execution, accounting, benchmark, Gemini, seed, and report evidence where applicable;
- finalized-data, replay-clock, next-event, and no-look-ahead rules are explicit and tested;
- run completeness, reconciliation, warnings, and reproducibility appear before performance;
- gross and net metrics remain separate;
- undefined and insufficient-sample metrics remain null with reasons;
- cash and buy-and-hold benchmarks preserve comparable assumptions;
- train, validation, final test, walk-forward, variant, sensitivity, and selection-bias evidence is explicit;
- failed, cancelled, incomplete, and unfavorable runs remain discoverable;
- reproducibility compares hashes, events, trades, ledger, metrics, benchmarks, and reports;
- backtest and paper-experiment comparisons preserve compatibility and methodological limits;
- no browser or AI mutation, optimization, promotion, provider-secret, order, testnet, or live-trading authority exists;
- accessibility, responsive, security, privacy, contract, integration, metric, benchmark, split, robustness, reproducibility, comparison, E2E, export, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 10 defines and implements the Experiment Operations, Scheduled Cycle, Incident, and Audit Timeline Workspace.
