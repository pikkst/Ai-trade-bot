# Backtest, Benchmark, Reproducibility, and Experiment Comparison Workspace Implementation Specification

Last reviewed: 2026-07-31  
Status: Sprint 9 authoritative backtest and experiment-comparison workspace specification

## 1. Purpose

This document defines the implementation contract for the Backtest, Benchmark, Reproducibility, and Experiment Comparison Workspace of The Daily Roast AI.

The workspace explains how a historical replay was configured, which immutable data and code versions were used, how strategy, risk, paper execution, and accounting contracts were applied, what simulated outcomes occurred, how results compare with approved benchmarks, and whether the run is reproducible, complete, and suitable as research evidence.

The workspace is read-only in Sprint 9. It must not modify a completed run, hide failed variants, optimize against an untouched test period, promote a strategy automatically, enable live execution, or allow AI-generated changes inside historical replay.

## 2. Scope

Sprint 9 covers:

- backtest list, detail, report, trades, events, ledger, reproducibility, and comparison routes;
- immutable backtest configuration and identity;
- run status, progress, cancellation outcome, failure state, and completeness;
- dataset range, quality, split, and hash evidence;
- code, dependency, migration, strategy, risk, execution, accounting, feature, and optional Gemini provenance;
- replay clock, timing, no-look-ahead, and finalized-data evidence;
- performance, risk, cost, exposure, trade, and benchmark metrics;
- equity and drawdown series;
- trade, decision, order, fill, ledger, halt, and reconciliation lineage;
- cash, buy-and-hold, and approved deterministic benchmark comparison;
- train, validation, final test, and walk-forward methodology;
- parameter sensitivity, variant disclosure, robustness evidence, and anti-overfitting warnings;
- deterministic repeated-run comparison;
- backtest-to-paper-experiment comparison;
- authorized export;
- responsive, accessible, secure, observable, and testable presentation.

Sprint 9 does not implement:

- strategy optimization algorithms;
- automatic parameter search;
- automatic strategy promotion;
- live Gemini calls during ordinary historical replay;
- real exchange execution;
- browser-side authoritative metric calculations;
- deletion or mutation of failed, cancelled, or completed run evidence;
- selective suppression of unfavorable results;
- investment recommendations or profitability guarantees.

## 3. User Outcomes

A user should be able to answer:

1. Which backtest run am I viewing, and is it complete?
2. What exact immutable configuration produced the result?
3. Which historical dataset, symbol metadata, feature set, code commit, dependencies, and migrations were used?
4. Were finalized data, no-look-ahead, next-event activation, fees, slippage, precision, and reconciliation rules enforced?
5. Which strategy, risk, execution, and accounting versions were applied?
6. Was Gemini disabled, precomputed, or used only in an explicitly non-default research mode?
7. Which period was used for design, validation, final test, or walk-forward evaluation?
8. How did the strategy perform after all modeled costs?
9. How did it compare with cash and buy-and-hold under comparable assumptions?
10. Which trades, decisions, orders, fills, ledger entries, halts, and warnings explain the result?
11. Are metrics undefined, insufficiently sampled, stale, incomplete, or otherwise limited?
12. How sensitive were results to parameters, periods, symbols, assumptions, or versions?
13. Does an identical rerun produce the same report hash and outputs?
14. How do backtest results differ from the related paper experiment?
15. Is the evidence sufficient for manual research review without implying production or live-trading approval?

## 4. Canonical Routes

```text
/backtests
/backtests/:backtestId
/backtests/:backtestId/report
/backtests/:backtestId/trades
/backtests/:backtestId/events
/backtests/:backtestId/ledger
/backtests/:backtestId/reproducibility
/backtests/:backtestId/compare
/backtests/:backtestId/compare/:comparisonId
```

Optional workspace-scoped forms may be used when required by the application shell:

```text
/workspaces/:workspaceId/backtests
/workspaces/:workspaceId/backtests/:backtestId
```

The chosen route family must be consistent, directly addressable, authorization-aware, and documented.

The workspace must be reachable from strategy and risk decisions, paper portfolio, experiment status, audit lineage, and research reports.

## 5. Information Architecture

The backtest detail page is ordered as follows:

1. simulation, completeness, data-quality, reproducibility, reconciliation, and warning state;
2. run identity and immutable configuration;
3. dataset range, split, and provenance;
4. methodology and replay timing;
5. result summary and benchmark comparison;
6. equity, drawdown, and exposure series;
7. cost and trade summary;
8. strategy, risk, halt, and rejection evidence;
9. trade and event lineage;
10. ledger and reconciliation evidence;
11. robustness, parameter sensitivity, and tested-variant disclosure;
12. repeated-run and paper-experiment comparison;
13. limitations, promotion boundaries, and export.

Incomplete, failed, unreconciled, non-reproducible, insufficient-sample, or data-quality-warning states must visually dominate positive return metrics.

## 6. Recommended Read Models

Recommended run contract:

```ts
interface BacktestWorkspaceReadModel {
  schemaVersion: string;
  run: BacktestRunIdentity;
  status: BacktestRunStatusSummary;
  configuration: BacktestConfigurationSummary;
  dataset: BacktestDatasetSummary;
  methodology: BacktestMethodologySummary;
  reproducibility: BacktestReproducibilitySummary;
  metrics: BacktestMetricSummary[];
  benchmarks: BacktestBenchmarkSummary[];
  series: BacktestSeriesSummary;
  trades: BacktestTradeSummary;
  costs: BacktestCostSummary;
  riskEvents: BacktestRiskEventSummary[];
  reconciliation: ReconciliationSummary;
  robustness: BacktestRobustnessSummary;
  diagnostics: DiagnosticSummary[];
  warnings: BacktestWarningSummary[];
  limitations: LimitationSummary[];
  links: BacktestResourceLinks;
}
```

Recommended reproducibility contract:

```ts
interface BacktestReproducibilityReadModel {
  schemaVersion: string;
  backtestId: string;
  gitCommitSha: string;
  runtimeVersion: string;
  dependencyLockHash: string;
  migrationRevision: string;
  datasetHash: string;
  symbolMetadataVersions: VersionReference[];
  featureSetVersion: VersionReference;
  strategyVersion: VersionReference;
  riskPolicyVersion: VersionReference;
  executionModelVersion: VersionReference;
  accountingPolicyVersion: VersionReference;
  geminiMode: "disabled" | "precomputed" | "sampled_research";
  geminiEvidence: GeminiBacktestEvidence | null;
  randomSeed: string | null;
  replayClockPolicy: VersionReference;
  reportHash: string | null;
  reproducibilityOutcome: "verified" | "mismatch" | "not_run" | "incomplete";
  repeatedRunReference: string | null;
}
```

Recommended comparison contract:

```ts
interface BacktestComparisonReadModel {
  schemaVersion: string;
  comparison: ComparisonIdentity;
  primaryRun: BacktestRunReference;
  candidateRuns: BacktestRunReference[];
  compatibility: ComparisonCompatibilitySummary;
  configurationDifferences: ConfigurationDifference[];
  datasetDifferences: DatasetDifference[];
  metricDifferences: MetricDifference[];
  seriesDifferences: SeriesDifferenceSummary[];
  tradeDifferences: TradeDifferenceSummary;
  robustnessDifferences: RobustnessDifferenceSummary;
  warnings: BacktestWarningSummary[];
  limitations: LimitationSummary[];
}
```

The frontend must not calculate authoritative returns, ratios, benchmarks, drawdown, exposure, trade statistics, report hashes, or compatibility outcomes.

## 7. Backtest Identity

Required fields:

- immutable backtest ID;
- workspace ID;
- name or approved label;
- status;
- creation, queue, start, completion, cancellation, and failure timestamps;
- requested and actual data range;
- symbol and interval;
- initial virtual capital and base currency;
- frozen configuration version;
- code commit SHA;
- dependency manifest or lock hash;
- migration revision;
- report generation version;
- report hash;
- correlation, request, and job references where safe;
- related experiment or comparison references.

Completed, failed, and cancelled run identities are immutable.

## 8. Run Status and Completeness

Supported statuses include:

- queued;
- validating;
- running;
- reconciling;
- generating report;
- completed;
- failed;
- cancelled;
- timed out.

Required status fields:

- safe status code;
- progress based on persisted work units;
- replay cursor or event position where safe;
- processed and total eligible events where known;
- queue wait and run duration;
- terminal reason code;
- partial-result availability;
- completeness classification;
- reconciliation state;
- report state.

A partial, failed, cancelled, or timed-out run must never appear comparable to a complete final result without a prominent warning.

## 9. Immutable Configuration Contract

Required configuration references:

- workspace configuration version and hash;
- exchange and normalized symbol;
- interval;
- start and end timestamps;
- initial capital and base currency;
- historical dataset version and hash;
- symbol metadata versions;
- feature-set version and configuration hash;
- strategy version and configuration hash;
- risk-policy version and configuration hash;
- execution-model version and configuration hash;
- accounting-policy version;
- benchmark definitions and versions;
- optional Gemini dataset, model, prompt, schema, and validation versions;
- random seed where applicable;
- replay-clock and event-ordering rules;
- timeout and resource policy version.

No configuration used by a running or completed backtest may be silently changed.

## 10. Dataset and Provenance Contract

Required dataset fields:

- exchange and symbol;
- interval;
- requested range;
- actual eligible range;
- candle count;
- first and last event timestamps;
- finalized-data status;
- data-quality status;
- gap count and handling policy;
- snapshot or dataset IDs;
- dataset hash;
- symbol metadata versions;
- ingestion or source references;
- timezone and calendar assumptions;
- retention and availability status.

The workspace must explain any excluded, missing, replaced, or quality-rejected market data.

Data after the current replay event must not appear in strategy, risk, execution, or AI evidence for that event.

## 11. Dataset Split Contract

Supported split categories include:

- design or train;
- validation;
- final untouched test;
- walk-forward training window;
- walk-forward validation window;
- full-period descriptive run when explicitly labeled.

Required split fields:

- split ID and category;
- start and end timestamps;
- selection policy version;
- whether parameters were selected using the split;
- whether the period remained untouched before final evaluation;
- related parameter-selection artifact;
- warnings about overlap, leakage, or reuse.

A final test period must not be presented as untouched when it influenced parameter selection.

## 12. Replay Methodology and Timing

Required methodology evidence:

- replay-clock rule;
- finalized-data rule;
- snapshot construction rule;
- feature calculation timing;
- optional precomputed Gemini matching rule;
- strategy evaluation timing;
- risk evaluation timing;
- existing-order processing order;
- new-order activation timing;
- market-order reference-price rule;
- limit-order crossing and intrabar rule;
- partial-fill rule;
- fee, spread, slippage, precision, and minimum-notional rules;
- ledger posting and reconciliation frequency;
- stop and failure behavior.

The workspace must expose a clear no-look-ahead statement and link to executable assertion evidence when available.

## 13. Gemini Historical-Replay Contract

Allowed modes:

- `disabled`;
- `precomputed`;
- `sampled_research`.

For `precomputed`, required evidence includes:

- immutable report dataset version;
- exact market snapshot mapping;
- provider and configured model identifier;
- prompt version;
- report-schema version;
- validation-policy version;
- report hashes;
- missing or incompatible report handling.

For `sampled_research`, the workspace must prominently state that results may not be reproducible in the same way as the deterministic baseline and must disclose cost and provider drift limitations.

Ordinary backtests must not make silent live Gemini calls.

## 14. Metric Contract

Supported metrics may include:

- initial and final equity;
- gross return;
- net return;
- realized and unrealized P&L;
- cash benchmark return;
- buy-and-hold return;
- excess return versus each benchmark;
- maximum drawdown;
- volatility;
- Sharpe ratio;
- Sortino ratio;
- win and loss rates;
- average win and loss;
- profit factor;
- trade count;
- exposure;
- turnover;
- total fees;
- modeled spread and slippage;
- average holding period;
- longest losing sequence;
- halt and rejection counts.

Every metric must include:

- canonical metric code;
- decimal string value or explicit null;
- unit;
- formula or definition version;
- sampling frequency;
- annualization assumption where relevant;
- risk-free-rate assumption where relevant;
- gross or net classification;
- start and end timestamps;
- sample count;
- warning or undefined reason;
- benchmark reference where applicable.

Undefined ratios, zero denominators, and insufficient samples must produce explicit null values and warnings.

## 15. Benchmark Contract

Cash and buy-and-hold are required.

Every benchmark must identify:

- canonical benchmark code;
- definition version;
- initial capital;
- data range and hash;
- entry timing;
- valuation policy;
- fee, spread, slippage, precision, and minimum-notional assumptions;
- resulting metrics;
- limitations;
- report hash or evidence reference.

Benchmark comparison must use comparable assumptions or explain every normalization difference.

A benchmark is evidence, not a recommendation.

## 16. Equity, Drawdown, and Exposure Series

Required series metadata:

- series ID and type;
- start and end timestamps;
- point count;
- sampling frequency;
- currency or percentage unit;
- valuation policy version;
- data hash;
- gap and interpolation policy;
- downsampling method for display;
- authoritative download link where permitted.

Supported series include:

- equity;
- cash benchmark equity;
- buy-and-hold equity;
- drawdown;
- gross exposure;
- net exposure;
- cumulative fees;
- cumulative modeled slippage;
- position quantity where useful.

Display downsampling must not change authoritative metrics or exported data.

## 17. Trade Summary and Trade Detail

Required trade summary fields:

- trade count;
- winning, losing, breakeven, and incomplete counts;
- average holding period;
- gross and net P&L;
- fees and modeled execution costs;
- turnover;
- symbol and side distribution;
- partial-fill and cancellation counts;
- halt and rejection context.

Each trade or closed-position episode must link to:

- strategy evaluation;
- risk evaluation;
- paper order or orders;
- fills;
- ledger transactions;
- portfolio state versions;
- valuation events;
- reconciliation results;
- relevant market evidence.

A trade summary must not hide open positions, cancelled remainders, or incomplete episodes.

## 18. Event and Decision Lineage

The event explorer may include:

- replay clock advances;
- snapshot creation;
- feature calculations;
- Gemini evidence loads;
- strategy evaluations;
- risk evaluations;
- order activations;
- fills;
- ledger postings;
- reconciliations;
- halts;
- warnings;
- run cancellation or failure.

Every event must expose type, sequence, timestamp, status, version references, safe reason codes, and detail links.

Missing required lineage is an integrity failure.

## 19. Ledger and Reconciliation Evidence

The backtest must preserve or reference:

- initial funding;
- reservations;
- fills;
- fees;
- releases;
- realized P&L;
- final valuation;
- ledger sequence;
- portfolio state hashes;
- reconciliation runs.

A failed reconciliation must stop the run and mark the report incomplete or failed according to domain policy.

The workspace must not present unreconciled results as final performance.

## 20. Warnings and Failure Codes

Warnings and failures require canonical codes, severity, category, explanation, evidence, and scope.

Categories include:

- data gaps;
- stale or invalid metadata;
- split leakage;
- insufficient sample;
- undefined metric;
- missing benchmark;
- look-ahead assertion;
- configuration mismatch;
- Gemini evidence mismatch;
- unsupported strategy output;
- execution-model failure;
- accounting invariant failure;
- reconciliation mismatch;
- resource limit;
- timeout;
- cancellation;
- incomplete report;
- reproducibility mismatch.

Critical warnings must not be collapsed by default.

## 21. Anti-Overfitting Evidence

The workspace must expose where available:

- number of strategy versions tested;
- number of parameter variants tested;
- symbols and periods inspected;
- design, validation, and final test separation;
- walk-forward windows;
- parameter-selection policy;
- selected and rejected variants;
- sensitivity results;
- turnover and cost sensitivity;
- benchmark comparison;
- tail and drawdown behavior;
- known selection-bias risks.

Failed and rejected variants must remain discoverable within authorized research history.

## 22. Parameter Sensitivity and Robustness

Robustness evidence may include:

- nearby parameter values;
- different cost assumptions;
- different eligible periods;
- different market regimes;
- different symbols when explicitly comparable;
- delayed entry or execution assumptions;
- bootstrap or resampling summaries when approved;
- walk-forward aggregates;
- missing-data stress cases.

Each robustness result must identify changed inputs, unchanged inputs, compatibility, sample count, and limitations.

The UI must not identify one best parameter without showing tested range and selection context.

## 23. Reproducibility Verification

A reproducibility check compares an original run with an identical repeated run.

Required comparisons:

- configuration hash;
- dataset hash;
- code commit;
- dependency lock hash;
- migration revision;
- random seed;
- event count and ordering;
- trade identities;
- ledger sequence and state hashes;
- metrics;
- benchmark results;
- report hash.

Possible outcomes:

- verified;
- mismatch;
- incomplete;
- not run.

A mismatch must identify machine-readable differences and must not be hidden by approximate display rounding.

## 24. Backtest Comparison

The comparison workspace may compare:

- strategy versions;
- risk-policy versions;
- execution-model versions;
- accounting-policy versions;
- feature-set versions;
- data periods;
- symbols;
- parameter configurations;
- cost assumptions;
- deterministic and precomputed-Gemini modes.

Compatibility rules must prevent misleading comparisons.

Required comparison dimensions:

- changed and unchanged configuration;
- data overlap and split category;
- metric differences;
- benchmark-relative differences;
- drawdown and exposure differences;
- trade and turnover differences;
- cost differences;
- halt and rejection differences;
- reproducibility state;
- warning differences;
- limitations.

The original runs remain immutable.

## 25. Backtest-to-Paper Experiment Comparison

A historical backtest may be compared with a related paper experiment when mappings are explicit.

Required evidence:

- strategy, risk, execution, accounting, and feature compatibility;
- market and interval compatibility;
- experiment period and backtest period;
- data source and quality differences;
- scheduled-cycle versus continuous replay differences;
- Gemini mode differences;
- latency, missing-cycle, and cloud-runtime effects;
- fees, spread, slippage, and valuation assumptions;
- return, drawdown, exposure, turnover, trade, halt, and rejection differences;
- paper reconciliation and incident state.

The comparison must explain that historical replay and forward paper observation answer different research questions.

## 26. Promotion Evidence Boundary

Backtest evidence may inform a manual strategy lifecycle review.

The workspace must not:

- activate a strategy;
- change an active policy;
- start paper trading automatically;
- enable Binance test or live environments;
- suppress failed or unfavorable runs;
- present a single positive metric as sufficient evidence.

Promotion review requires separate owner approval, observation evidence, compatibility checks, testing, security, and operational gates.

## 27. Filtering and History

Backtest history may filter by approved bounded fields:

- date created;
- run status;
- symbol and interval;
- data range;
- split category;
- strategy version;
- risk-policy version;
- execution-model version;
- accounting-policy version;
- Gemini mode;
- benchmark set;
- reproducibility outcome;
- warning or failure code;
- related experiment.

Filters must be URL-stable where appropriate, server-approved, authorization-aware, and cursor-paginated.

## 28. Export Contract

Authorized exports may include:

- authoritative JSON report;
- configuration and provenance package;
- metric package;
- benchmark package;
- equity, drawdown, and exposure series;
- trade list;
- event lineage;
- ledger and reconciliation evidence;
- reproducibility comparison;
- backtest comparison;
- backtest-to-paper comparison;
- human-readable HTML, Markdown, or CSV derivatives.

Every export must include:

- schema and generation versions;
- run identity;
- simulation disclaimer;
- data, code, dependency, migration, and configuration provenance;
- metric definitions and units;
- benchmark assumptions;
- completeness, warnings, and reconciliation state;
- report hash;
- limitations;
- authorization context without secrets.

JSON remains authoritative.

## 29. Page-State Matrix

Explicit states include:

- loading;
- no backtests;
- queued;
- validating;
- running;
- reconciling;
- generating report;
- completed;
- failed;
- cancelled;
- timed out;
- partial results;
- missing report;
- invalid dataset;
- data gap warning;
- split leakage warning;
- insufficient sample;
- undefined metric;
- missing benchmark;
- look-ahead failure;
- Gemini evidence mismatch;
- accounting or reconciliation failure;
- non-reproducible result;
- incompatible comparison;
- stale comparison artifact;
- schema mismatch;
- unauthorized;
- not found;
- backend unavailable;
- export unavailable.

Critical warnings and incomplete states must not render as ordinary completed results.

## 30. Responsive Behavior

Requirements:

- simulation, completeness, warning, reconciliation, and reproducibility state remains first;
- configuration and provenance tables provide narrow-layout alternatives;
- charts preserve units, period, benchmark identity, and accessible summaries;
- metric cards expose definition and warning state;
- trade and event tables retain lineage links;
- long hashes and version identifiers wrap or copy safely;
- comparison dimensions remain aligned and labeled;
- no critical evidence is hover-only;
- dense tables support horizontal containment without losing headers or context.

## 31. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- keyboard-accessible filters, disclosures, tabs, charts, comparisons, and lineage;
- semantic tables with captions and headers;
- text summaries for every chart;
- accessible metric definitions, warnings, and null reasons;
- visible focus;
- status announcements for material asynchronous state changes;
- no reliance on color alone;
- reflow at 200% and relevant cases at 400% zoom;
- reduced-motion support;
- screen-reader-readable decimals, percentages, dates, and units;
- safe copy controls for IDs and hashes.

## 32. Security and Authority Boundaries

The workspace must not:

- mutate completed or running backtests;
- alter immutable configuration or result evidence;
- hide failed or rejected variants;
- trigger arbitrary executable strategy code from browser input;
- make unrestricted provider calls;
- expose Gemini or exchange credentials;
- execute live trades;
- activate strategies or policies;
- trust browser-calculated metrics or compatibility;
- expose stack traces, SQL, tokens, secrets, unrestricted raw provider payloads, or unsafe filesystem paths.

Application authorization, RLS, immutable records, sandboxing, resource limits, and server-side calculations remain authoritative.

## 33. Privacy and Data Minimization

The UI and telemetry must avoid:

- secrets and credentials;
- raw private provider payloads;
- unrestricted prompts;
- unnecessary personal identifiers;
- internal filesystem paths;
- full dependency or environment details beyond approved reproducibility metadata;
- sensitive incident information outside authorized roles.

Exports must enforce the same authorization and minimization rules as API responses.

## 34. Observability

Safe telemetry may include:

- run counts by safe status;
- queue wait and run duration;
- replay events per second;
- worker memory and CPU summaries;
- failures and warnings by canonical code;
- cancellation and timeout counts;
- data-quality rejection counts;
- look-ahead assertion failures;
- reconciliation outcomes;
- report-generation outcomes;
- reproducibility outcomes;
- comparison compatibility failures;
- export status;
- approved correlation IDs;
- client build version.

Telemetry must not include secrets, raw strategy code, unrestricted prompts, full private datasets, or arbitrary financial payloads.

## 35. Testing Strategy

### Contract Tests

Validate schema versions, enums, decimals, units, timestamps, nullability, links, run states, warning codes, metric definitions, benchmark definitions, and compatibility behavior.

### Backtest Integration Tests

Validate finalized-data eligibility, no look-ahead, next-event activation, snapshot and feature timing, deterministic strategy and risk reuse, market and limit fills, costs, precision, partial fills, ledger posting, reconciliation, cancellation, timeout, and report generation.

### Metric Reference Tests

Validate returns, P&L, drawdown, volatility, Sharpe, Sortino, win rate, profit factor, exposure, turnover, fees, slippage, holding period, losing sequence, null conditions, and sample warnings.

### Benchmark Tests

Validate cash and buy-and-hold timing, fees, slippage, precision, valuation, report hashes, and comparable-assumption rules.

### Reproducibility Tests

Validate identical repeated runs, configuration hashes, dataset hashes, event ordering, trade identities, ledger sequences, state hashes, metrics, benchmarks, and report hashes.

### Robustness and Split Tests

Validate train, validation, final test, walk-forward windows, overlap detection, leakage warnings, variant disclosure, sensitivity comparisons, and incompatible-result handling.

### Authorization and RLS Tests

Validate workspace isolation and owner, operator, and viewer read permissions. Verify no browser route gains strategy, execution, or promotion authority.

### Route and Component Tests

Validate filters, URL state, configuration, provenance, metrics, warnings, charts, trades, events, reproducibility, comparison, safe errors, and export links.

### Accessibility Tests

Validate keyboard flow, headings, landmarks, tables, chart summaries, metric definitions, focus, announcements, copy controls, zoom, reflow, and contrast.

### Visual Regression

Capture empty, queued, running, completed, failed, cancelled, timed-out, insufficient-sample, missing-benchmark, warning, reconciliation-failure, reproducibility-mismatch, and incompatible-comparison states across themes and viewports.

### Export Tests

Validate authoritative JSON, derived formats, provenance, metric definitions, benchmark assumptions, completeness, warnings, reconciliation state, simulation labeling, prohibited-field absence, and stable report hashes.

## 36. Acceptance Criteria

Sprint 9 documentation is accepted when:

1. every backtest is tied to immutable data, code, dependency, migration, strategy, risk, execution, accounting, and feature evidence;
2. finalized-data and no-look-ahead rules are explicit;
3. run status, completeness, warnings, reconciliation, and reproducibility are visible before performance;
4. gross and net results remain separate;
5. undefined and insufficient-sample metrics remain explicit nulls with reasons;
6. cash and buy-and-hold benchmarks preserve comparable assumptions;
7. train, validation, final test, and walk-forward evidence remains explicit;
8. tested variants, sensitivity, and selection-bias risks are visible;
9. identical repeated runs can be compared by hashes and financial lineage;
10. historical and paper-experiment comparisons preserve compatibility and limitations;
11. failed, cancelled, incomplete, and unfavorable evidence remains discoverable;
12. no strategy promotion, live execution, browser-side metric authority, or silent Gemini drift is introduced;
13. security, privacy, accessibility, observability, reproducibility, and test gates are explicit.

## 37. Definition of Done

The Sprint 9 specification is complete when:

- this document is committed;
- `SPRINT_9_TASKS.md` is committed;
- terminology matches backtest, portfolio, paper trading, strategy, risk, market evidence, Gemini, API, database, architecture, security, testing, and observability documents;
- all run, dataset, split, methodology, metric, benchmark, series, trade, lineage, robustness, reproducibility, comparison, export, accessibility, and security states are explicit;
- both commits are fetched and verified.

## 38. Next Sprint Boundary

Sprint 10 defines the **Experiment Operations, Scheduled Cycle, Incident, and Audit Timeline Workspace**, including frozen experiment configuration, lifecycle transitions, cycle completeness, cloud-runtime evidence, halts, incidents, recovery, export, and 30-day experiment reporting.
