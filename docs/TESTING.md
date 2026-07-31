# Testing

Last reviewed: 2026-07-31
Status: Authoritative MVP test strategy

## 1. Objectives

Testing must prove deterministic behavior, financial conservation, safe degradation, authorization, idempotency, reproducibility, and correct separation between Google Gemini analysis and deterministic trading controls.

A passing happy-path suite is insufficient. Failure behavior is a first-class product requirement.

## 2. Test Pyramid

### Unit Tests

Pure domain calculations, value objects, state machines, reason-code mapping, validation, and policy logic.

### Property-Based Tests

Use Hypothesis for broad invariant coverage of decimal values, ledger transactions, precision boundaries, drawdown, risk sizing, and idempotency.

### Integration Tests

Use real PostgreSQL and Redis test containers for repositories, migrations, transactions, queue behavior, locks, and outbox publication.

### Contract Tests

Verify project-owned Binance and Gemini adapters against fixtures, recorded public responses, or dedicated test environments. Normal CI must not make paid Gemini calls or private exchange calls.

### End-to-End Tests

Exercise critical flows through the API and workers with fake external providers.

### Security Tests

Authorization matrix, secret redaction, unsafe configuration, prompt injection, dependency scans, and halt enforcement.

### Performance and Resilience Tests

Measure key read paths, job throughput, restart safety, timeout behavior, and bounded recovery.

## 3. Determinism and Reproducibility

Tests must verify that identical inputs and versions produce identical:

- feature values and hashes;
- strategy intents;
- risk decisions;
- paper fills under deterministic model configuration;
- ledger entries;
- backtest metrics and event sequence.

Persisted reproducibility metadata must be sufficient to rerun a backtest or explain why exact reproduction is impossible.

Gemini output itself is probabilistic. Tests validate schema handling, grounding, policy behavior, and versioned fixtures rather than requiring identical live model prose.

## 4. Core Domain Test Matrix

### Market Data

- valid finalized candles;
- invalid OHLC relationships;
- negative volume;
- duplicate candle;
- out-of-order candle;
- missing interval;
- stale data;
- WebSocket reconnect and REST gap repair;
- retry and rate-limit behavior;
- immutable finalized candle correction flow;
- snapshot hash stability.

### Feature Engineering

- SMA and EMA reference values;
- RSI boundary and insufficient-history behavior;
- ATR and volatility reference values;
- decimal/precision behavior;
- deterministic feature hashes;
- missing-data rejection;
- version change produces a distinct result identity.

### Google Gemini Integration

- successful structured response;
- schema mismatch;
- unknown fields under strict validation;
- missing required fields;
- invalid confidence range;
- unsupported evidence reference;
- authentication failure;
- 429 rate limit;
- timeout;
- retryable 5xx;
- terminal provider error;
- safety block;
- refusal;
- empty response;
- budget exhaustion before request;
- prompt injection and malicious evidence;
- secret never included in prompt or log;
- fake provider behavior in CI.

### Strategy

- HOLD, ENTER, EXIT, and REDUCE intents;
- identical input determinism;
- AI report optionality and rejection behavior;
- stale or invalid input rejection;
- strategy version isolation;
- no direct order side effect.

### Risk

- position limit;
- order-notional limit;
- gross exposure limit;
- daily drawdown halt;
- total drawdown halt;
- volatility guard;
- cooldown;
- open-order limit;
- duplicate protection;
- precision and minimum-notional rejection;
- missing policy version;
- stale data;
- fail-closed exception behavior;
- portfolio and workspace halt.

### Paper Execution

- market order;
- limit order crossing and non-crossing;
- partial fill;
- cancellation;
- fee calculation;
- spread and slippage;
- conservative intrabar ambiguity;
- duplicate order command;
- restart after order creation;
- fill quantity never exceeds approved quantity;
- terminal state immutability.

### Portfolio and Ledger

- balanced double-entry transaction;
- cash reservation and release;
- buy and sell fills;
- fee posting;
- realized and unrealized P&L;
- equity and exposure;
- drawdown high-water mark;
- non-negative balance policy;
- ledger sequence uniqueness;
- rebuild projections from ledger;
- mismatch detection and halt;
- atomic fill and ledger commit.

### Backtesting

- no look-ahead;
- finalized data only;
- fee and slippage always applied;
- cash benchmark;
- buy-and-hold benchmark;
- deterministic replay;
- date boundary and missing-data handling;
- strategy/risk/execution contract reuse;
- metric reference calculations;
- reproducibility metadata stored.

### API

- authentication and role matrix;
- workspace isolation;
- request validation;
- decimal string serialization;
- UTC timestamp serialization;
- pagination and deterministic ordering;
- idempotency replay and conflict;
- stable error envelopes;
- no secret or stack trace leakage;
- OpenAPI examples validate.

## 5. Property-Based Invariants

At minimum:

1. Every ledger transaction balances.
2. Replaying an idempotent command does not create additional side effects.
3. Filled quantity never exceeds approved quantity.
4. Risk-approved notional never exceeds configured limits.
5. Drawdown is never negative and is consistent with the equity high-water mark.
6. Monetary calculations preserve configured decimal precision.
7. Reconstructed portfolio state equals persisted reconciled state.
8. Strategy output belongs to the allowed intent enum.
9. Invalid or stale AI output cannot produce an approved order.
10. A halt prevents all new entry orders.

## 6. Migration Tests

CI must verify:

- upgrade from empty database to head;
- upgrade from previous supported revision;
- downgrade only where explicitly supported;
- one migration head unless a merge migration is intentional;
- constraints and indexes exist;
- already-applied migrations are unchanged;
- data migrations are restartable where relevant.

## 7. External Provider Test Policy

### Gemini

- normal CI uses deterministic fake provider;
- optional scheduled contract job may call Gemini only with dedicated key, strict budget, and no secret output;
- model-dependent evaluations use versioned datasets and record configured model ID;
- failures never block safe deterministic tests from running.

### Binance

- normal CI uses fixtures and fake transport;
- public contract tests may run on a controlled schedule;
- no private credentials in MVP;
- rate-limit-sensitive tests remain bounded.

## 8. End-to-End Scenarios

Required MVP E2E scenarios:

1. Valid candle ingestion to snapshot and features.
2. Valid fake Gemini report to deterministic strategy HOLD.
3. Gemini invalid schema to safe rejection and HOLD.
4. Strategy ENTER to risk approval to paper order and atomic fill.
5. Strategy ENTER to risk rejection with no order.
6. Duplicate command produces no duplicate order or ledger entry.
7. Ledger mismatch activates halt.
8. Stale market data prevents analysis-dependent entry.
9. Backtest generates cash and buy-and-hold comparison.
10. Owner starts, pauses, and halts an experiment; viewer cannot.

## 9. Coverage Policy

Coverage is a diagnostic, not the sole quality measure.

Targets:

- at least 90% branch coverage for risk, execution, portfolio, and accounting domains;
- at least 85% branch coverage for other core backend domains;
- every public API operation has at least one automated contract or E2E test;
- every stable error code has at least one test;
- every critical security control has a test or scan.

Uncovered critical branches require explicit justification in the pull request.

## 10. Performance Tests

Before sandbox progression, measure:

- common read endpoint p50/p95/p99;
- candle ingestion throughput and lag;
- feature calculation duration;
- backtest throughput for representative ranges;
- queue depth recovery after restart;
- PostgreSQL query plans for recurring queries;
- memory behavior for large backtests.

Design targets in documentation must be replaced by measured results where available.

## 11. Resilience Tests

- kill worker during a job and verify safe retry;
- restart after order creation before fill;
- restart after fill before response publication;
- PostgreSQL unavailable;
- Redis unavailable;
- Gemini timeout and outage;
- Binance disconnect;
- duplicate queue delivery;
- malformed queue payload;
- clock drift outside tolerance;
- exhausted AI budget;
- disk or storage failure where testable.

## 12. Security Tooling

Required CI checks:

- Ruff;
- MyPy strict;
- Pytest;
- Bandit;
- Semgrep;
- dependency vulnerability review;
- secret scanning;
- Trivy filesystem and container scanning;
- SBOM generation before sandbox release.

## 13. Test Data

- no production secrets or personal data;
- deterministic factories and seeds;
- representative decimal precision and minimum-notional values;
- explicit UTC timestamps;
- versioned market fixtures;
- malicious prompt-injection fixtures;
- expected metric reference datasets.

## 14. Flaky Test Policy

Flaky tests are defects.

- do not blindly rerun until green;
- quarantine only with issue, owner, reason, and expiry;
- remove time dependence through fake clocks;
- remove random dependence through explicit seeds;
- remove provider dependence through fakes;
- investigate race conditions rather than increasing sleeps.

## 15. Release Gates

A release candidate requires:

- formatting, linting, and strict typing pass;
- unit, property, integration, contract, and required E2E tests pass;
- migration tests pass;
- no unresolved critical security finding;
- no unresolved high finding without approved time-limited exception;
- required coverage thresholds met;
- no flaky critical-path test;
- paper-trading smoke test passes;
- reconciliation and halt tests pass;
- generated OpenAPI and documentation are current;
- live trading remains disabled.

## 16. Evidence in Pull Requests

Every implementation PR must report:

- tests added or changed;
- commands executed;
- relevant result summary;
- coverage impact;
- security scan result;
- migration result;
- untested risk and justification;
- documentation updated.

## 17. Related Documents

- `/AGENTS.md`
- `PRODUCT_REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `GEMINI_INTEGRATION.md`
- `RISK_ENGINE.md`
- `PAPER_TRADING.md`
- `PORTFOLIO_ENGINE.md`
- `SECURITY.md`
