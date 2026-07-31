# Testing

Last reviewed: 2026-08-01  
Status: Authoritative test strategy mapped to `TASKS.md`

## 1. Objectives

Testing must prove deterministic behavior, financial conservation, safe degradation, authorization, RLS, idempotency, reproducibility, provider isolation, accessibility, recovery, and the separation between Gemini analysis and deterministic trading controls.

A passing happy path or coverage percentage is insufficient. Failure behavior, restart safety, schedule uncertainty, migration safety, restore, and incident recovery are first-class requirements.

`TASKS.md` defines when test work is required. `docs/TEST_ENVIRONMENTS.md` defines environment gates. This file defines the test strategy.

## 2. Master-Task Test Gates

| Master range | Required test outcome |
|---|---|
| M001–M006 | bootstrap, lock files, quality tools, local database/Auth/RLS, frontend foundation, fakes |
| M007–M013 | domain unit/property/integration/contract tests for market, AI, strategy, risk, execution, ledger, cycle, backtest |
| M014–M025 | API contracts, authorization/RLS, frontend components, accessibility, E2E, documentation/traceability |
| M026 | integrated deterministic local/CI product verification |
| M027 | export, restore, recovery, security, and release-blocking gate |
| M028 | cloud deployment, Auth, CORS/CSP, cold-start, scheduling, and secret isolation |
| M029 | controlled experiment preflight, operation, reconciliation, export, and report evidence |
| M030–M034 | performance, data, research, incident, and change-governance evidence |
| M035 | isolated staging migration, restore, load/failure, security/privacy, and release-candidate validation |
| M036 | protected production-research deployment and continuous verification |

A later gate cannot compensate for a missing earlier test gate.

## 3. Active Test Architecture

The active profile uses:

- local Supabase/PostgreSQL and Auth for integration and browser tests;
- deterministic fake Binance and Gemini providers for normal CI;
- a one-shot research-cycle CLI rather than Redis/ARQ workers;
- PostgreSQL locks or durable leases and deterministic idempotency;
- GitHub Actions as an external best-effort scheduler;
- optional protected public/provider smoke workflows;
- React/TypeScript component, accessibility, visual, and browser tests;
- repository-owned documentation and generated-artifact checks.

Redis, ARQ, persistent workers, Binance WebSocket ingestion, and hosted Prometheus/Grafana tests are deferred until an accepted change proposal and ADR activate those components.

## 4. Test Layers

### Unit Tests

Pure domain calculations, value objects, state machines, reason-code mapping, schema validation, compatibility, classification, and policy logic.

### Property-Based Tests

Use Hypothesis or an approved equivalent for Decimal values, ledger transactions, reservations, precision boundaries, drawdown, risk sizing, idempotency, canonical hashes, reconstruction, and state-machine invariants.

### Integration Tests

Use local Supabase/PostgreSQL for repositories, migrations, constraints, transactions, RLS, Auth, locks/leases, atomic ledger posting, projection rebuild, export, and restore validation.

### Contract Tests

Verify Binance, Gemini, Supabase/PostgREST, application OpenAPI, generated client types, Render startup, Cloudflare build, and GitHub scheduling assumptions against fakes, mocks, fixtures, recorded public structures, or protected smoke environments.

### End-to-End Tests

Exercise browser, FastAPI, local Auth, database, fake providers, strategy, risk, paper execution, ledger, reconciliation, audit, export, and complete cross-workspace lineage.

### Security and Privacy Tests

Cover authentication, recent authentication, authorization, RLS, workspace isolation, secrets, unsafe configuration, prompt injection, unsupported claims, data minimization, retention/deletion boundaries, dependency scans, frontend secret absence, and halt enforcement.

### Accessibility and Content Tests

Cover keyboard, screen readers, zoom/reflow, contrast, reduced motion, chart alternatives, focus, semantic status, English/Estonian safety parity, and prohibited financial claims.

### Performance and Resilience Tests

Measure cycle runtime, API reads, frontend budgets, backtest limits, duplicate-cycle behavior, cold starts, provider timeouts, database interruptions, export/restore, rollback, and incident recovery.

## 5. Determinism and Reproducibility

Identical inputs and versions must produce identical:

- snapshot and feature hashes;
- strategy intents;
- risk decisions;
- deterministic paper orders/fills;
- ledger entries and state hashes;
- portfolio projections;
- backtest events, metrics, and report hashes;
- logical research-cycle results;
- task-generated schema and documentation artifacts where applicable.

Gemini output is probabilistic. Deterministic tests validate project schemas, grounding, safety, retry, budget, fallback, and downstream isolation using immutable fixtures and a fake provider.

## 6. Core Domain Matrix

### Market Data

Test finalized-candle rules, invalid OHLC, negative volume, duplicates, ordering, gaps, stale data, REST retry, rate limit, immutable correction, snapshot hash stability, and missed-cycle recovery without fabricated trades.

### Features

Test returns, SMA, EMA, RSI, ATR, volatility, volume, warm-up, missing history, precision, deterministic hashes, and no look-ahead.

### Gemini

Test valid structured output, parsing/schema failure, unsupported evidence/claims, false certainty, authentication, 429, timeout, cancellation, 5xx, safety block, refusal, empty output, budget exhaustion, prompt injection, secret exclusion, retries, fallback, and fake-provider behavior.

### Strategy

Test HOLD, ENTER, EXIT, REDUCE, determinism, Gemini required/optional/ignored policies, stale input rejection, version isolation, and absence of direct side effects.

### Risk

Test position, order, exposure, drawdown, volatility, cooldown, duplicate, open-order, minimum-notional, precision, missing policy, stale data, exceptions, and halts.

### Paper Execution

Test market/limit orders, next-event activation, partial fills, cancellation, fee, spread, slippage, precision, conservative intrabar handling, restart, duplicate command, and approved-quantity limits.

### Portfolio and Ledger

Test double-entry balance, reservation/release, fees, cost basis, realized/unrealized P&L, equity, exposure, drawdown, sequence uniqueness, reversal/replacement, reconstruction, mismatch detection, and atomic commit.

### Backtesting

Test finalized data, no look-ahead, timing, cost models, benchmarks, deterministic replay, dataset splits, missing data, metrics, null reasons, variants, cancellation, timeout, and reproducibility metadata.

### API and Auth

Test Supabase identity/JWT handling, owner/operator/viewer roles, workspace isolation, recent authentication, validation, Decimal serialization, UTC timestamps, pagination, idempotency, expected-version conflicts, stable errors, OpenAPI, CORS, rate limits, and redaction.

### Frontend

Test components, route permission, stale/cold-start/halt/reconciliation states, simulation labels, accessibility, localization, production build, SPA routing, CSP assumptions, and forbidden-secret absence.

### Operations and Governance

Test experiment lifecycle, locks, cycle completeness, incidents, release gates, migration drift, restore evidence, SLO/error-budget calculations, data lifecycle, research approvals, and staged behavior changes.

## 7. Property Invariants

1. Every ledger transaction balances.
2. An idempotent command or cycle creates no duplicate side effect.
3. Only one process owns a logical cycle lease.
4. Filled quantity never exceeds approved quantity.
5. Approved notional never exceeds policy.
6. Drawdown is consistent with the equity high-water mark.
7. Monetary precision is preserved.
8. Reconstructed portfolio equals reconciled state.
9. Invalid, stale, rejected, or unavailable AI output cannot create an approved order.
10. A halt prevents new entries.
11. Browser roles cannot mutate server-only critical tables.
12. Restore preserves migration revision, evidence hashes, ledger reconstruction, and reconciliation.
13. A running experiment retains its frozen behavior-set hash.
14. No approval is valid after its immutable evidence snapshot materially changes.
15. No deferred or live-trading capability can be enabled through ordinary configuration.

## 8. Migration, RLS, and Database Tests

CI verifies:

- upgrade from empty database to one expected head;
- deterministic seed application;
- applied migrations remain unchanged;
- constraints and indexes exist;
- expand-migrate-contract behavior where applicable;
- RLS deny-by-default;
- anonymous, viewer, operator, owner, workflow/service, read-only, and migration-role matrices;
- workspace isolation and approved views;
- browser direct-write denial for critical tables;
- database locks reject overlap;
- transaction and outbox atomicity;
- schema and generated documentation drift;
- isolated restore and reconciliation.

## 9. External Provider Policy

### Gemini

Normal CI uses the deterministic fake. Protected smoke tests use a dedicated non-production key with strict request/token/cost budgets and never run for untrusted fork code.

### Binance

Normal CI uses fixtures. A bounded public REST smoke test may verify server time, symbol metadata, and finalized candles. Private credentials and order endpoints are prohibited.

### Free-Cloud Providers

Cloudflare, Render, Supabase, and GitHub assumptions are verified through builds, health checks, isolated smoke tests, provider snapshots, and documented contracts. Cold starts, pauses, throttling, quota changes, and best-effort scheduling are expected failure modes.

## 10. Required Integrated Scenarios

1. local login through Supabase Auth;
2. valid candles to immutable snapshot and features;
3. fake Gemini accepted report to strategy and risk;
4. invalid Gemini report to deterministic fallback or HOLD;
5. ENTER to approval to paper order, fill, ledger, projection, and reconciliation;
6. risk rejection with no order;
7. duplicate/overlapping cycle with no duplicate state;
8. stale market data blocking entry;
9. ledger/reconciliation mismatch causing halt;
10. backtest with cash and buy-and-hold benchmarks;
11. owner command allowed and viewer command denied;
12. complete UI decision lineage and simulation status;
13. export and restore preserving integrity;
14. Render cold start not stopping scheduled research;
15. experiment preflight/start/pause/halt/report lifecycle;
16. incident containment distinct from restoration and resolution;
17. behavior change requiring immutable approval and staged paper canary.

## 11. Coverage and Evidence Policy

- at least 90% branch coverage for risk, execution, portfolio, and accounting;
- at least 85% branch coverage for other core backend domains;
- every public API operation has a contract or E2E test;
- every stable public error/reason code has a test;
- every critical RLS and authorization rule has a test;
- every critical safety invariant has a test or verified scan;
- every primary frontend workflow has accessibility evidence;
- every Master Task records selected detailed IDs, commands, results, and limitations.

Coverage does not replace meaningful failure and invariant tests. Documentation creation or a passing score cannot mark a Master Task `VERIFIED`.

## 12. CI Workflow Classes

The project maintains repository-owned workflow classes for:

- quality checks;
- local Supabase migration/Auth/RLS/integration tests;
- frontend tests and production build;
- security/privacy/supply-chain scans;
- documentation, task, link, and generated-artifact consistency;
- optional protected provider smoke checks;
- hourly one-shot research cycle;
- free-cloud demo deployment;
- protected staging deployment;
- protected production-research deployment.

Normal pull requests never access production data, production credentials, paid-provider keys, or private Binance APIs.

## 13. Reliability and Recovery Tests

Test interrupted cycles, duplicate delivery, GitHub scheduling delay, Render cold start, Supabase outage/pause, Gemini quota exhaustion, Binance timeout, partial transaction failure, export/restore, projection rebuild, reconciliation halt, failed migration/deployment, secret rotation, incident response, and rollback/forward fix.

A backup process is not accepted until restore and ledger reconciliation succeed.

## 14. Security Tooling

Required checks include Ruff, MyPy strict, Pytest, Hypothesis, Bandit, Semgrep, dependency review, secret scanning, frontend dependency audit, client-bundle inspection, Trivy where artifacts/containers exist, and SBOM generation before production-research promotion.

Tools, actions, and images are pinned. Exceptions have owner, rationale, compensating controls, expiry, and verification.

## 15. Test Data

Use synthetic identities, explicit UTC timestamps, deterministic IDs/seeds, versioned market fixtures, malicious AI fixtures, Decimal boundaries, known ledger examples, and safe environment metadata.

Never use production secrets, production personal data, private provider payloads, or unrestricted prompt/response content.

## 16. Flaky Test Policy

Flaky tests are defects. Do not rerun blindly until green. Quarantine requires an issue, owner, reason, impact, and expiry. Remove time dependence through fake clocks, randomness through seeds, provider dependence through fakes, and race masking through correct synchronization.

## 17. Promotion Gates

### M026 Integrated Local Completion

Clean checkout, bootstrap, migrations, seed, all relevant deterministic test layers, generated artifacts, documentation, and no secret requirement.

### M027 Recovery and Security Gate

Isolated export/restore, ledger reconstruction/reconciliation, outage/retry/halt drills, security scans, and no unresolved release-blocking finding.

### M028 Free-Cloud Demo

Auth, RLS, public URLs, protected providers, simulation labels, cold-start behavior, schedule concurrency, secret isolation, and deployment smoke tests.

### M029 Formal Paper Experiment

All P0 safety tests, idempotency, freshness, Gemini degradation, risk halts, ledger reconstruction, restore evidence, frozen configuration, observability, incidents, and report closure.

### M030–M034 Evidence Hardening

Measured reliability/cost, governed datasets, research review, incident learning, and change-control verification.

### M035 Staging

Separate environment, immutable artifacts, migration rehearsal, production-like E2E/load/failure/security/privacy/accessibility/restore tests, and release-candidate approval.

### M036 Production Research

Protected deployment, controlled migration, post-deploy smoke/reconciliation, current backup/restore, measured SLO/capacity/cost, incident/support ownership, and live-trading-disabled confirmation.

## 18. Pull Request and Task Evidence

Each implementation change reports:

- Master Task and detailed task IDs;
- dependencies verified;
- tests added and commands executed;
- result and coverage summary;
- invariant/security/privacy/accessibility evidence;
- migration/RLS/Auth result;
- generated artifacts and hashes;
- environment impact;
- documentation/changelog updates;
- untested risks, exceptions, and follow-ups;
- commit or pull-request reference.

## 19. Related Documents

- `/AGENTS.md`
- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `LOCAL_DEVELOPMENT.md`
- `TEST_ENVIRONMENTS.md`
- `PRODUCTION_DEVELOPMENT.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `SECURITY.md`
- `/LOCAL_AND_PRODUCTION_TASKS.md`
