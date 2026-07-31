# Roadmap

Last reviewed: 2026-07-31
Status: Gated product evolution plan

## Principles

Safety gates are more important than dates. Gemini remains advisory. Live trading is not part of MVP. Free-cloud services are experimental and do not provide an SLA.

## Phase 0 — Documentation and Governance

Complete requirements, architecture, Gemini, risk, accounting, security, testing, deployment, coding-agent rules, detailed tasks, and audit.

**Exit:** documents are coherent and implementation may begin without hidden architecture decisions.

## Phase 1 — Shared Engineering Foundation

Implement Python 3.12 backend structure, FastAPI, typed settings, SQLAlchemy/Alembic, tests, security checks, structured logs, and deterministic fakes.

**Exit:** `T1.1` and `T1.2` plus required foundation tasks pass.

## Phase 2 — Free Cloud Foundation

Follow `C1` through `C7` in `CLOUD_MVP_TASKS.md`:

- dedicated Supabase Free project;
- migrations, Auth, RLS, and read views;
- one-shot research-cycle CLI;
- scheduled GitHub Actions workflow;
- Render Free FastAPI deployment;
- Cloudflare Pages frontend deployment;
- free-tier logs, cycle status, export, and restore procedure.

**Exit:** the platform runs without a local computer, has public HTTPS frontend/API URLs, and has proven duplicate protection and restore.

## Phase 3 — Market and Feature Core

Implement Binance Spot REST metadata and finalized candle backfill, data quality, immutable snapshots, and versioned features.

Persistent WebSocket ingestion is deferred.

**Exit:** complete hourly data can be reproduced; stale or missing data blocks entries.

## Phase 4 — Gemini Analysis

Implement provider protocol, fake provider, official Gemini adapter, structured report schema, validation, budgets, and evaluation suite.

**Exit:** invalid, blocked, unavailable, or quota-exhausted Gemini calls degrade safely; normal CI uses no paid call.

## Phase 5 — Strategy, Risk, Portfolio, and Paper Execution

Implement HOLD baseline, BTC/EUR trend baseline, risk policy, append-only ledger, reconciliation, market/limit paper orders, fees, spread, slippage, precision, and minimum-notional rules.

**Exit:** no duplicate side effects, all actionable intents pass risk, and accounting property tests pass.

## Phase 6 — Backtesting and API/UI Completion

Implement reproducible backtesting, benchmarks, reports, FastAPI resources, Supabase Auth authorization, and the primary frontend views.

**Exit:** OpenAPI, API tests, UI states, RLS, and audit lineage pass.

## Phase 7 — Controlled 30-Day Free-Cloud Experiment

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

## Phase 8 — Reliability Upgrade Assessment

After the experiment, decide whether free-tier limitations justify:

- paid always-on API/worker hosting;
- Redis/ARQ or another durable queue;
- persistent Binance WebSocket ingestion;
- hosted Prometheus/Grafana;
- managed backups and higher availability.

Every addition requires measured evidence and an ADR.

## Phase 9 — Binance Test Environment

Only after explicit owner approval and a separate credential/security design. No live capital.

## Phase 10 — Real-Capital Assessment

Not approved by this roadmap. Requires legal, security, accounting, operational, and loss-limit review plus explicit owner approval.

## Future Productization

Possible later scope includes multi-user tenancy, additional exchanges, billing, optional local models, stronger analytics, and compliance controls. Public SaaS requires separate planning.
