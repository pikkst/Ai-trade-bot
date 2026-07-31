# Backtest Engine

Last reviewed: 2026-07-31
Status: Authoritative MVP backtesting specification

## 1. Purpose

The backtest engine replays historical finalized market data through the same strategy, risk, paper-execution, and portfolio contracts used by paper trading.

It is a research tool. A positive backtest does not prove future profitability or authorize live trading.

## 2. Core Invariants

- No look-ahead.
- Finalized data only.
- Fees and slippage are mandatory.
- Strategy and risk versions are immutable.
- Execution assumptions are explicit and versioned.
- Identical inputs and versions produce identical results.
- Cash and buy-and-hold benchmarks are always included.
- Optimization, validation, and final test periods are separated.
- Google Gemini output must be either precomputed/versioned or excluded; live Gemini calls during historical replay are prohibited by default.

## 3. Inputs

A backtest configuration includes:

- workspace;
- exchange and symbol;
- interval;
- start and end timestamps;
- immutable historical data version/hash;
- feature-set version;
- strategy version and configuration hash;
- risk-policy version;
- execution-model version;
- accounting-policy version;
- initial virtual capital and base currency;
- benchmark set;
- optional precomputed validated Gemini report dataset version;
- random seed when any stochastic model is used;
- code commit and dependency manifest.

## 4. Historical Data Eligibility

The engine must verify:

- candles are finalized;
- range is complete or documented gaps are handled by explicit policy;
- timestamps and intervals are consistent;
- data-quality status is approved;
- symbol metadata versions are available;
- dataset hash is stable;
- no candle after the current replay event is visible to strategy, risk, or execution.

## 5. Event Loop

Baseline sequence per eligible time step:

1. advance replay clock;
2. reveal only data available at that time;
3. construct or load immutable snapshot;
4. calculate/load versioned features;
5. load optional precomputed validated Gemini report matching that time and version;
6. evaluate deterministic strategy;
7. evaluate deterministic risk;
8. process existing open orders against the current eligible market event;
9. create approved new paper orders according to timing policy;
10. atomically post fills and ledger entries;
11. reconcile portfolio state;
12. record event and metrics.

The exact order of existing-order processing versus new-order activation is part of the execution-model version and must prevent same-event look-ahead.

## 6. Gemini in Backtests

Calling Gemini during every historical step is costly, non-reproducible, and vulnerable to model drift.

Allowed modes:

- `disabled`: strategy ignores AI evidence;
- `precomputed`: use immutable validated reports generated for exact historical snapshots under a pinned configuration;
- `sampled_research`: separate experiment that records provider/model/prompt/schema versions and cost, but is not the default deterministic benchmark.

A backtest must never silently mix reports from different model, prompt, or schema versions.

## 7. Fill and Timing Model

The backtest uses the paper-execution model.

Requirements:

- market orders cannot fill at a price known before order activation unless explicitly justified;
- limit fills require eligible range crossing;
- ambiguous intrabar order resolves conservatively;
- fees, spread, slippage, precision, minimum notional, and partial-fill assumptions apply;
- no fill quantity exceeds approved risk quantity;
- failed reconciliation stops the run.

## 8. Benchmarks

### Cash

Initial capital remains in base currency with zero trades. It provides a no-action baseline.

### Buy and Hold

At the first eligible execution point, acquire the asset using the same fee, slippage, and precision model, then hold to the end and value at the same final mark policy.

Additional benchmarks require versioned definitions.

## 9. Metrics

Required outputs:

- initial and final equity;
- absolute and percentage return;
- cash benchmark return;
- buy-and-hold return;
- excess return versus each benchmark;
- maximum drawdown;
- daily/periodic volatility;
- Sharpe ratio with documented annualization and risk-free assumption;
- Sortino ratio with documented downside calculation;
- win rate;
- loss rate;
- average win and loss;
- profit factor;
- trade count;
- exposure;
- turnover;
- total fees;
- simulated slippage;
- average holding period;
- longest losing sequence;
- halt events;
- equity curve;
- complete simulated ledger and trade list;
- warnings and data-quality events.

Undefined ratios, zero denominators, and insufficient samples must produce explicit null/warning values rather than misleading numbers.

## 10. Return and Metric Conventions

Metric formulas, sampling frequency, annualization factor, and treatment of fees must be documented in code and tests.

Return reports must distinguish:

- gross return before fees/slippage;
- net return after all modeled costs;
- realized and unrealized P&L;
- benchmark-relative return.

## 11. Dataset Splits

At minimum:

- design/train period for initial strategy development;
- validation period for parameter and robustness checks;
- final untouched test period.

Where data volume permits, use walk-forward evaluation.

The final report must state how many strategy/parameter variants were tried to reduce selection-bias concealment.

## 12. Walk-Forward Evaluation

P1 capability:

1. define rolling or expanding training window;
2. choose parameters only from past data;
3. freeze parameters for the next validation window;
4. replay validation window;
5. repeat;
6. aggregate results without using future data.

Walk-forward configuration and all selected versions are persisted.

## 13. Reproducibility Record

Store:

- backtest ID;
- Git commit SHA;
- Python runtime;
- dependency lock hash;
- database migration revision;
- historical dataset hash;
- symbol metadata versions;
- feature-set version;
- strategy and configuration versions;
- risk-policy version;
- execution/accounting model versions;
- optional Gemini dataset/model/prompt/schema versions;
- random seed;
- start/end and replay clock rules;
- generated report hash.

## 14. Parallelism

Backtests may run in parallel only when:

- each run has isolated state;
- worker concurrency is bounded;
- database and memory limits are respected;
- no run mutates shared immutable versions;
- deterministic result ordering is preserved;
- cancellation and timeout are supported.

## 15. Failure Handling

The run fails safely on:

- missing or invalid data;
- inconsistent version references;
- look-ahead assertion failure;
- risk-engine exception;
- missing execution or fee model;
- ledger/reconciliation mismatch;
- unsupported strategy output;
- resource limit or timeout;
- corrupted precomputed Gemini report lineage.

Partial results remain clearly marked incomplete and cannot be compared as final results without warning.

## 16. Anti-Overfitting Controls

- limit free parameters;
- preserve untouched final test data;
- report all material tested variants;
- use parameter-sensitivity analysis;
- include costs and turnover;
- compare simpler baselines;
- avoid selecting only the best symbol or period after inspection;
- report drawdown and tail behavior, not only return;
- archive failed and rejected experiments;
- prohibit AI-generated strategy changes inside a running backtest.

## 17. Reports

A report contains:

- configuration summary;
- data range and quality;
- methodology and limitations;
- performance metrics;
- benchmark comparison;
- equity and drawdown series;
- trade/ledger summaries;
- halt and rejection events;
- reproducibility metadata;
- warnings;
- explicit statement that results are simulated and not a guarantee.

JSON is authoritative. Human-readable HTML/Markdown/CSV exports are derived artifacts.

## 18. Tests

Required tests:

- no-look-ahead assertion;
- next-event order activation;
- finalized data only;
- deterministic repeated run;
- gaps and stale data;
- market and limit fills;
- fee/slippage application;
- partial fills;
- precision/minimum-notional behavior;
- strategy/risk/execution contract reuse;
- ledger conservation and reconciliation;
- cash benchmark;
- buy-and-hold benchmark;
- metric reference cases;
- zero/insufficient-sample metrics;
- run cancellation and timeout;
- precomputed Gemini version matching;
- different versions produce distinct identities.

## 19. Metrics and Operations

Track:

- runs by status;
- run duration;
- replay events per second;
- queue wait time;
- memory and CPU;
- failures by code;
- cancellation;
- data-quality rejection;
- reconciliation failure;
- report-generation outcome.

## 20. Promotion Use

Backtest evidence is one input for strategy lifecycle promotion. Active paper trading additionally requires observation mode, risk compatibility, security/testing gates, and owner approval.

No backtest directly enables Binance sandbox or real trading.

## 21. Related Documents

- `MARKET_DATA.md`
- `STRATEGY_ENGINE.md`
- `RISK_ENGINE.md`
- `PAPER_TRADING.md`
- `PORTFOLIO_ENGINE.md`
- `TESTING.md`
- `DATABASE_SCHEMA.md`
