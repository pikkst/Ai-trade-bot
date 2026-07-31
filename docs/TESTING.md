# Testing

Last reviewed: 2026-07-31
Status: Authoritative test strategy

## 1. Objectives

Testing must prove deterministic behavior, financial conservation, safe degradation, authorization, RLS, idempotency, reproducibility, provider isolation, and correct separation between Gemini analysis and deterministic trading controls.

A passing happy-path suite is insufficient. Failure behavior, restart safety, cloud scheduling uncertainty, migration safety, and recovery are first-class requirements.

The detailed environment matrix and promotion gates are defined in `TEST_ENVIRONMENTS.md`.

## 2. Active Test Architecture

The first MVP uses:

- local Supabase/PostgreSQL and Auth for integration and browser tests;
- deterministic fake Binance and Gemini providers for normal CI;
- a one-shot research-cycle CLI rather than Redis/ARQ workers;
- PostgreSQL leases and idempotency for duplicate protection;
- GitHub Actions as an external best-effort scheduler;
- optional protected provider smoke workflows.

Redis, ARQ, persistent WebSocket, and hosted Prometheus/Grafana tests are deferred until an accepted ADR activates those components.

## 3. Test Pyramid

### Unit Tests

Pure domain calculations, value objects, state machines, reason-code mapping, validation, and policy logic.

### Property-Based Tests

Use Hypothesis for decimal values, ledger transactions, precision boundaries, drawdown, risk sizing, idempotency, and reconstruction invariants.

### Integration Tests

Use local Supabase/PostgreSQL for repositories, migrations, transactions, constraints, RLS, Auth, advisory locks, leases, atomic ledger posting, and restore validation.

### Contract Tests

Verify Binance, Gemini, Supabase/PostgREST, Render startup, and Cloudflare build assumptions against fakes, mocks, fixtures, recorded public structures, or protected smoke environments.

### End-to-End Tests

Exercise browser, FastAPI, local Auth, database, fake providers, strategy, risk, paper execution, ledger, and audit lineage.

### Security Tests

Cover authorization, RLS, secret redaction, unsafe configuration, prompt injection, dependency scans, frontend secret absence, and halt enforcement.

### Performance and Resilience Tests

Measure research-cycle runtime, common API reads, backtest limits, duplicate-cycle handling, cold starts, provider timeouts, database interruptions, export, and restore.

## 4. Determinism and Reproducibility

Identical inputs and versions must produce identical:

- feature values and hashes;
- strategy intents;
- risk decisions;
- deterministic paper fills;
- ledger entries;
- portfolio projections;
- backtest metrics and event sequence;
- research-cycle logical result.

Gemini output is probabilistic. Normal tests validate project schemas, grounding, safety, retry, and budget behavior using immutable fixtures and a fake provider.

## 5. Core Domain Matrix

### Market Data

Test finalized candles, invalid OHLC, negative volume, duplicates, ordering, gaps, stale data, REST retry, rate limit, immutable correction, snapshot hash stability, and missed-cycle recovery without fabricated trades.

### Features

Test SMA, EMA, RSI, ATR, volatility, warm-up, missing history, precision, deterministic hashes, and no look-ahead.

### Gemini

Test valid structured output, schema failure, unsupported evidence, auth failure, 429, timeout, 5xx, safety block, refusal, empty output, budget exhaustion, prompt injection, secret exclusion, and fake-provider behavior.

### Strategy

Test HOLD, ENTER, EXIT, REDUCE, determinism, optional Gemini behavior, stale input rejection, version isolation, and absence of direct order effects.

### Risk

Test position, order, exposure, drawdown, volatility, cooldown, duplicate, minimum-notional, precision, missing policy, stale data, exception behavior, and halts.

### Paper Execution

Test market and limit orders, partial fills, cancellation, fee, spread, slippage, precision, conservative intrabar handling, restart, duplicate command, and approved-quantity limits.

### Portfolio and Ledger

Test double-entry balance, reservation, release, fees, realized/unrealized P&L, equity, exposure, drawdown, sequence uniqueness, reconstruction, mismatch detection, and atomic commit.

### Backtesting

Test finalized data, no look-ahead, cost models, benchmarks, deterministic replay, boundaries, missing data, shared contracts, metrics, and reproducibility metadata.

### API and Auth

Test Supabase JWT verification, owner/operator/viewer roles, workspace isolation, validation, decimal serialization, UTC timestamps, pagination, idempotency, errors, OpenAPI, CORS, and no secret leakage.

### Frontend

Test components, route authorization, stale/cold-start/halt states, simulation labeling, accessibility, production build, SPA routing, CSP assumptions, and absence of forbidden secrets in bundles.

## 6. Property Invariants

1. Every ledger transaction balances.
2. An idempotent command or research cycle creates no duplicate side effect.
3. Only one process owns a logical cycle lease.
4. Filled quantity never exceeds risk approval.
5. Approved notional never exceeds policy.
6. Drawdown is consistent with equity high-water mark.
7. Monetary precision is preserved.
8. Reconstructed portfolio equals reconciled state.
9. Invalid or stale AI output cannot create an approved order.
10. A halt prevents new entries.
11. Browser roles cannot mutate server-only financial tables.
12. Restore preserves migration revision and ledger reconciliation.

## 7. Migration, RLS, and Database Tests

CI must verify:

- upgrade from empty database to head;
- deterministic seed application;
- one expected migration head;
- applied migrations remain unchanged;
- constraints and indexes exist;
- RLS deny-by-default behavior;
- owner, operator, viewer, unauthenticated, and server access matrices;
- read-only views expose only approved fields;
- database leases reject overlap;
- schema drift fails CI.

## 8. External Provider Policy

### Gemini

Normal CI uses the deterministic fake provider. Protected manual smoke tests may use a dedicated key with strict request/token budgets and must not run for untrusted fork code.

### Binance

Normal CI uses fixtures. A bounded scheduled or manual public REST smoke test may verify server time, symbol metadata, and a small finalized-candle request. No private key is permitted in MVP.

### Free Cloud Providers

Cloudflare, Render, and Supabase integration assumptions are validated through builds, health checks, staging/demo smoke tests, and documented contracts. Tests must account for cold starts, pauses, and best-effort scheduling.

## 9. Required End-to-End Scenarios

1. Local login through Supabase Auth.
2. Valid candles to immutable snapshot and features.
3. Fake Gemini valid report to strategy and risk.
4. Invalid Gemini report to safe fallback or HOLD.
5. ENTER to approval to paper order, fill, ledger, and reconciliation.
6. Risk rejection with no order.
7. Duplicate research cycle with no duplicate state.
8. Stale market data blocking entry.
9. Ledger mismatch causing halt.
10. Backtest with cash and buy-and-hold benchmarks.
11. Owner can control experiment; viewer cannot.
12. UI displays complete decision lineage and simulation status.
13. Export and restore preserve integrity.
14. Render cold start does not stop scheduled research.

## 10. Coverage Policy

- at least 90% branch coverage for risk, execution, portfolio, and accounting;
- at least 85% branch coverage for other core backend domains;
- every public API operation has an automated contract or E2E test;
- every stable error code has a test;
- every critical RLS and authorization rule has a test;
- every critical safety invariant has a test or verified scan.

Coverage does not replace meaningful failure and invariant testing.

## 11. CI Workflows

The project should maintain:

- quality checks;
- local Supabase migration and integration tests;
- frontend tests and production build;
- security scans;
- documentation consistency checks;
- optional provider smoke checks;
- hourly research cycle;
- demo deployment;
- future staging deployment;
- future protected production deployment.

Normal pull requests must not access production data or paid-provider credentials.

## 12. Reliability and Recovery Tests

Test interrupted cycles, duplicate workflow delivery, GitHub scheduling delay, Render cold start, Supabase outage, Gemini quota exhaustion, Binance timeout, partial transaction failure, export/restore, projection rebuild, and halt behavior.

A backup process is not accepted until a restore and ledger reconciliation have succeeded.

## 13. Security Tooling

Required checks include Ruff, MyPy strict, Pytest, Bandit, Semgrep, dependency review, secret scanning, frontend dependency audit, bundle secret inspection, Trivy where artifacts or containers exist, and SBOM generation before production research promotion.

## 14. Test Data

Use synthetic users, explicit UTC timestamps, deterministic seeds, versioned market fixtures, malicious prompt fixtures, decimal boundary values, and known ledger examples. Never use production secrets or personal data.

## 15. Flaky Test Policy

Flaky tests are defects. Do not blindly rerun until green. Quarantine requires an issue, owner, reason, and expiry. Remove time dependence through fake clocks, randomness through seeds, provider dependence through fakes, and race masking through proper synchronization.

## 16. Promotion Gates

### Local Completion

Clean checkout, bootstrap, migrations, seed, unit/integration/contract/E2E tests, quality checks, and no secret requirement.

### Cloud Demo

Auth, RLS, public URLs, fake-provider demo, protected real-provider configuration, simulation labels, and reset/export procedures.

### Formal Paper Experiment

All P0 safety tests, idempotency, data freshness, Gemini degradation, risk halts, ledger reconstruction, restore evidence, and frozen configuration.

### Staging and Production Research

Separate environments, migration rehearsal, protected CI/CD, production-like E2E, load/failure testing, managed backups, measured SLOs, security/privacy review, and manual approval.

See `TEST_ENVIRONMENTS.md` for the full gates.

## 17. Pull Request Evidence

Each implementation PR reports tests added, commands executed, result summary, coverage impact, security scan result, migration result, untested risks, environment impact, and documentation updates.

## 18. Related Documents

- `/AGENTS.md`
- `LOCAL_DEVELOPMENT.md`
- `TEST_ENVIRONMENTS.md`
- `PRODUCTION_DEVELOPMENT.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `SECURITY.md`
- `/LOCAL_AND_PRODUCTION_TASKS.md`
