# Roadmap

Last reviewed: 2026-07-31
Status: Gated product evolution plan

## Principles

Safety gates are more important than dates. Gemini remains advisory. Live trading is not part of MVP. Free-cloud services are experimental and do not provide an SLA. Production development means a production-grade research service, not automatic real-money execution.

## Phase 0 — Documentation and Governance

Complete requirements, architecture, Gemini, risk, accounting, security, testing, deployment, coding-agent rules, detailed tasks, and audit.

**Exit:** documents are coherent and implementation may begin without hidden architecture decisions.

## Phase 1 — Local Engineering Foundation

Implement:

- Python 3.12 backend and frontend foundations;
- locked dependencies and cross-platform bootstrap;
- local Supabase/PostgreSQL and Auth;
- migrations, deterministic seed data, and RLS tests;
- fake Binance and Gemini providers;
- stable local command runner;
- one-shot research-cycle CLI;
- structured logs and correlation IDs.

Use `T1.1`, `T1.2`, and `L1.1-L1.4`.

**Exit:** a clean checkout becomes a working local environment without paid credentials, migrations apply from zero, and the fake-provider flow is reproducible on Windows and CI.

## Phase 2 — Automated Test and Quality Foundation

Implement:

- unit and property tests;
- Supabase migration, constraint, Auth, and RLS integration tests;
- provider contract tests;
- frontend component, accessibility, and browser E2E tests;
- security scanning;
- documentation and generated-artifact checks;
- export and restore tests.

Use `L2.1-L2.6`.

**Exit:** core financial invariants, authorization, RLS, idempotency, recovery, and critical E2E flows pass automatically.

## Phase 3 — Free Cloud Foundation

Follow `C1-C7`:

- dedicated Supabase Free project;
- migrations, Auth, RLS, and read views;
- one-shot research-cycle CLI;
- scheduled GitHub Actions workflow;
- Render Free FastAPI deployment;
- Cloudflare Pages frontend deployment;
- free-tier logs, cycle status, export, and restore procedure.

**Exit:** the platform runs without a local computer, has public HTTPS frontend/API URLs, and has proven duplicate protection and restore.

## Phase 4 — Market and Feature Core

Implement Binance Spot REST metadata and finalized candle backfill, data quality, immutable snapshots, and versioned features.

Persistent WebSocket ingestion is deferred.

**Exit:** complete hourly data can be reproduced and stale or missing data blocks entries.

## Phase 5 — Gemini Analysis

Implement provider protocol, fake provider, official Gemini adapter, structured report schema, validation, budgets, and evaluation suite.

**Exit:** invalid, blocked, unavailable, or quota-exhausted Gemini calls degrade safely; normal CI uses no paid call.

## Phase 6 — Strategy, Risk, Portfolio, and Paper Execution

Implement HOLD baseline, BTC/EUR trend baseline, risk policy, append-only ledger, reconciliation, market/limit paper orders, fees, spread, slippage, precision, and minimum-notional rules.

**Exit:** no duplicate side effects, all actionable intents pass risk, and accounting property tests pass.

## Phase 7 — Backtesting, API, and UI Completion

Implement reproducible backtesting, benchmarks, reports, FastAPI resources, Supabase Auth authorization, and primary frontend views.

**Exit:** OpenAPI, API tests, UI states, RLS, accessibility, and audit lineage pass.

## Phase 8 — Cloud Demo

Deploy a public testable demonstration using synthetic or clearly labeled sample data.

**Exit:** auth, API, frontend, fake-provider demo, protected real Gemini configuration, simulation labeling, cold-start behavior, reset, export, and restore are verified.

## Phase 9 — Controlled 30-Day Free-Cloud Experiment

Follow `C8`.

Configuration:

- virtual EUR 20;
- BTC/EUR and 1h finalized candles;
- approximately hourly GitHub Actions cycle;
- maximum position 25%;
- maximum order EUR 5;
- daily/total drawdown halts 5%/15%;
- one open order;
- no leverage or shorting;
- Gemini cost budget EUR 0 by default;
- cash and buy-and-hold benchmarks.

**Exit:** complete report, no unresolved reconciliation mismatch, no duplicate financial side effect, and no manual database repair. Profit is not an exit criterion.

## Phase 10 — Post-Experiment Review

Review reliability, data completeness, AI validity, incidents, free-tier behavior, costs, security findings, and user experience.

**Exit:** explicit decision to stop, repeat, improve the demo, or begin staging/production research development.

## Phase 11 — Staging Environment

Use `P1.1` and related tasks to create an isolated production-like environment with separate database, Auth, Gemini key, deployment credentials, synthetic data, migration rehearsal, E2E, load, and failure testing.

**Exit:** production artifacts deploy unchanged to staging and all release-candidate checks pass.

## Phase 12 — Production Research Readiness

Complete:

- protected CI/CD and manual approvals;
- hardened Auth and role controls;
- managed backups, restore, RPO, and RTO;
- centralized observability and measured SLOs;
- security and privacy review;
- cost and quota planning;
- incident response and runbooks.

Use `P1.2-P1.6`.

**Exit:** production research launch gate in `docs/PRODUCTION_DEVELOPMENT.md` is satisfied. Live trading remains disabled.

## Phase 13 — Production Research Service

Launch an authenticated production-grade service for market research, Gemini-assisted analysis, backtesting, audit history, and paper portfolios only.

Use `P1.7`.

**Exit:** stable operation, post-launch review, measured reliability and cost evidence.

## Phase 14 — Reliability and Capacity Evolution

Use `P2.1` to decide from measured need whether to introduce:

- paid always-on API or worker hosting;
- Redis/ARQ or another durable queue;
- persistent Binance WebSocket ingestion;
- managed observability;
- upgraded database and backup capabilities;
- stronger availability architecture.

Every material change requires an ADR.

## Phase 15 — Binance Test Environment

Only after explicit owner approval and a separate private-credential, reconciliation, security, and operational design. No live capital.

## Phase 16 — Real-Capital Assessment

Not approved by this roadmap. Requires separate legal, security, accounting, operational, exchange-eligibility, and loss-limit review plus explicit owner approval.

## Future Productization

Possible later scope includes multi-user tenancy, additional exchanges, billing, optional local models, stronger analytics, and compliance controls. Public SaaS requires separate product, privacy, support, and operational planning.

## Task Sources

- `TASKS.md` — shared domain implementation
- `CLOUD_MVP_TASKS.md` — free cloud deployment
- `LOCAL_AND_PRODUCTION_TASKS.md` — local development, test automation, staging, production research, and post-launch work
