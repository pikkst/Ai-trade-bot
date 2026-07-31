# Sprint 24 Tasks — Core Research Domain Contract Synchronization

Last reviewed: 2026-08-01  
Status: Documentation synchronization in progress

## Sprint Goal

Synchronize the M007–M013 domain contracts for market data, feature engineering, Gemini, strategy, risk, paper execution, portfolio/accounting, research-cycle orchestration, and backtesting so implementation uses finalized REST data, one-shot deterministic execution, immutable evidence, non-bypassable risk, append-only accounting, and complete reproducibility without importing deferred WebSocket/worker/live-execution assumptions.

## Authoritative References

- `TASKS.md`
- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`
- `docs/TASK_CATALOG_INDEX.md`
- `docs/ARCHITECTURE.md`
- `docs/BACKEND.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/MARKET_DATA.md`
- `docs/GEMINI_INTEGRATION.md`
- `docs/STRATEGY_ENGINE.md`
- `docs/RISK_ENGINE.md`
- `docs/PAPER_TRADING.md`
- `docs/PORTFOLIO_ENGINE.md`
- `docs/BACKTEST_ENGINE.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/API_SPECIFICATION.md`
- `docs/SECURITY.md`
- `docs/OBSERVABILITY.md`
- `docs/TESTING.md`

## S24.1 Synchronize Market Data and Feature Contracts

- make Binance Spot public REST finalized candles the active M007 profile;
- classify persistent WebSocket ingestion as deferred change-governed work;
- align server time, metadata versions, validation, freshness, gap repair, corrections, snapshots, datasets, lineage, and feature determinism;
- map acceptance and failure evidence to M007–M008.

## S24.2 Synchronize Gemini Contract

- align provider boundary, minimum-data requests, structured output, application validation, grounding, false certainty, injection, retries, budgets, fallback, retention, evaluations, and M034 changes;
- distinguish provider success from accepted report;
- preserve no-tool/no-execution authority.

## S24.3 Synchronize Strategy and Risk Contracts

- align immutable inputs, portfolio-state versioning, actions/outcomes, reason codes, deterministic hashes, missing/stale behavior, risk limits, halts, lifecycle, research review, and behavior changes;
- ensure strategy never creates orders and AI confidence never sizes positions;
- map to M010, M019, M032, and M034.

## S24.4 Synchronize Paper Execution and Portfolio Contracts

- align market/limit timing, reservations, partial fills, fees/spread/slippage/precision/minimum notional, atomic transactions, append-only ledger, cost basis, portfolio state versions, valuation, rebuild, reconciliation, and corrections;
- preserve one approved risk evaluation to at most one paper order;
- map to M011, M020, M027, and M029.

## S24.5 Synchronize Research Cycle and Backtest Contracts

- define one-shot cycle stage order, lock/lease, idempotency, actual eligible data, process-exit versus complete state, recovery, and audit;
- align backtests with shared domain contracts, no-look-ahead, exact datasets/splits, benchmarks, variants, robustness, reproducibility, reconciliation, and research review;
- map to M012–M013, M021–M022, and M029–M032.

## S24.6 Verify Cross-Domain Consistency

- compare all M007–M013 contracts against Product Requirements, Architecture, Backend, API, Schema, Security, Observability, Testing, and workspace specs;
- update task catalog, entry points, audit, changelog, and Sprint status;
- fetch all commits and verify no deferred/live path is introduced.

## Sprint 24 Definition of Done

- M007–M013 domain contracts agree on active runtime and evidence;
- REST finalized data and one-shot execution are canonical;
- strategy/risk/execution/accounting boundaries are non-bypassable;
- backtest and paper paths share domain rules;
- changes are committed and verified;
- product implementation remains not started.
