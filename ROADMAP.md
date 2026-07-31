# The Daily Roast AI Roadmap

Last reviewed: 2026-07-31  
Status: Gated product and engineering evolution plan

## Roadmap Principles

- Evidence and safety gates are more important than dates.
- The Daily Roast AI is a market-intelligence product, not merely a trading bot.
- Cryptocurrency is the first supported market, not the permanent limit of the product.
- Gemini remains advisory.
- Production development means a production-grade research service, not automatic real-money execution.
- Live trading is not authorized by this roadmap.
- Every phase must preserve explainability, reproducibility, auditability, and deterministic risk controls.

## Phase 0 — Documentation, Brand, and Governance

Complete:

- product vision, mission, values, brand, design, and naming foundations;
- requirements, architecture, Gemini, market data, strategy, risk, accounting, security, testing, deployment, and operations specifications;
- coding-agent rules and detailed task cards;
- documentation, brand, naming, and cross-reference audits.

**Exit:** the repository consistently uses **The Daily Roast AI**, the README inventory matches real files, and implementation can begin without hidden product or architecture decisions.

## Phase 1 — Local Engineering Foundation

Implement:

- Python 3.12 backend and React/TypeScript frontend foundations;
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
- frontend component, accessibility, copy, and browser E2E tests;
- security scanning;
- documentation, brand, naming, and generated-artifact checks;
- export and restore tests.

Use `L2.1-L2.6`.

**Exit:** financial invariants, authorization, RLS, idempotency, recovery, critical E2E flows, and user-facing trust requirements pass automatically.

## Phase 3 — Free Cloud Foundation

Follow `C1-C7`:

- dedicated Supabase Free project;
- migrations, Auth, RLS, and read views;
- one-shot research-cycle CLI;
- scheduled GitHub Actions workflow;
- Render Free FastAPI deployment;
- Cloudflare Pages frontend deployment;
- `thedailyroast.online` custom-domain integration;
- free-tier logs, cycle status, export, and restore procedure.

**Exit:** The Daily Roast AI runs without a local computer, has public HTTPS frontend and API URLs, and has proven duplicate protection and restore.

## Phase 4 — Market and Feature Core

Implement Binance Spot REST metadata, finalized candle backfill, data quality, immutable snapshots, and versioned features.

Persistent WebSocket ingestion is deferred.

**Exit:** complete hourly data can be reproduced, provenance is visible, and stale or missing data blocks entries.

## Phase 5 — Gemini Research Intelligence

Implement:

- provider protocol and deterministic fake;
- official Gemini adapter;
- structured report schema;
- prompt and schema versioning;
- evidence-reference validation;
- usage and budget controls;
- evaluation suite;
- brand-safe, non-promotional user summaries.

**Exit:** invalid, blocked, unavailable, or quota-exhausted Gemini calls degrade safely; normal CI uses no paid call; generated content follows brand and financial-claim rules.

## Phase 6 — Strategy, Risk, Portfolio, and Paper Execution

Implement HOLD baseline, BTC/EUR trend baseline, risk policy, append-only ledger, reconciliation, market and limit paper orders, fees, spread, slippage, precision, and minimum-notional rules.

**Exit:** no duplicate side effects, all actionable intents pass deterministic risk, accounting property tests pass, and every displayed action is explicitly simulated.

## Phase 7 — Backtesting, API, and Product Interface

Implement reproducible backtesting, benchmarks, reports, FastAPI resources, Supabase Auth authorization, and primary product views:

- Today's Roast;
- market evidence and regime;
- Gemini analysis;
- strategy and risk lineage;
- paper portfolio;
- backtest reports;
- experiment status;
- audit timeline.

**Exit:** OpenAPI, API tests, UI states, RLS, accessibility, naming, and audit lineage pass.

## Phase 8 — Public Cloud Demo

Deploy a testable branded demonstration at `thedailyroast.online` or `app.thedailyroast.online` using synthetic or clearly labeled sample data.

**Exit:** branding, auth, API, frontend, fake-provider demo, protected Gemini configuration, simulation labeling, cold-start behavior, reset, export, and restore are verified.

## Phase 9 — Controlled 30-Day Free-Cloud Experiment

Follow `C8`.

Configuration:

- virtual EUR 20;
- BTC/EUR and 1h finalized candles;
- approximately hourly GitHub Actions cycle;
- maximum position 25%;
- maximum order EUR 5;
- daily and total drawdown halts 5% and 15%;
- one open order;
- no leverage or shorting;
- Gemini cost budget EUR 0 by default;
- cash and buy-and-hold benchmarks.

**Exit:** complete report, no unresolved reconciliation mismatch, no duplicate financial side effect, no manual database repair, and complete decision lineage. Profit is not an exit criterion.

## Phase 10 — Post-Experiment Product Review

Review:

- reliability and data completeness;
- Gemini validity and usefulness;
- user comprehension and trust;
- incidents and free-tier behavior;
- costs and quotas;
- security findings;
- interface and brand consistency;
- value of evidence, scenario, and paper-trading workflows.

**Exit:** explicit decision to stop, repeat, improve the demo, or begin staging and production research development.

## Phase 11 — Staging Environment

Create an isolated production-like environment with separate database, Auth, Gemini key, domains, deployment credentials, synthetic data, migration rehearsal, E2E, load, failure, and content validation.

**Exit:** production artifacts deploy unchanged to staging and all release-candidate checks pass.

## Phase 12 — Production Research Readiness

Complete:

- protected CI/CD and manual approvals;
- hardened Auth and role controls;
- managed backups, restore, RPO, and RTO;
- centralized observability and measured SLOs;
- security, privacy, legal, and content review;
- cost and quota planning;
- incident response and runbooks;
- brand and domain launch verification.

**Exit:** the production research launch gate in `docs/PRODUCTION_DEVELOPMENT.md` is satisfied. Live trading remains disabled.

## Phase 13 — Production Research Service

Launch an authenticated production-grade service for market research, Gemini-assisted analysis, backtesting, audit history, and paper portfolios.

**Exit:** stable operation, measured reliability and cost evidence, support process, and post-launch review.

## Phase 14 — Multi-Market Research Expansion

After the cryptocurrency research architecture is proven, evaluate additional market-data adapters for:

- equities;
- ETFs;
- foreign exchange;
- commodities;
- macroeconomic indicators.

Requirements:

- adapter-specific licensing and terms review;
- distinct market-session and corporate-action models;
- no reuse of crypto assumptions where they do not apply;
- consistent evidence, provenance, risk, and simulation contracts.

**Exit:** an approved ADR and product requirements exist for each added market class.

## Phase 15 — Reliability and Capacity Evolution

Use measured evidence to decide whether to introduce:

- paid always-on API or worker hosting;
- Redis/ARQ or another durable queue;
- persistent exchange streams;
- managed observability;
- upgraded database and backup capabilities;
- stronger availability architecture.

Every material change requires an ADR.

## Phase 16 — Binance Test Environment

Only after explicit owner approval and a separate private-credential, reconciliation, security, and operational design. No live capital.

## Phase 17 — Real-Capital Assessment

Not approved by this roadmap. Requires separate legal, security, accounting, operational, exchange-eligibility, tax, and loss-limit review plus explicit owner approval.

## Future Product Family

Potential modules, subject to evidence and separate requirements:

- The Daily Roast AI Markets;
- The Daily Roast AI Research;
- The Daily Roast AI Portfolio;
- The Daily Roast AI Strategies;
- The Daily Roast AI Backtests;
- The Daily Roast AI Alerts;
- The Daily Roast AI Labs;
- The Daily Roast AI Enterprise.

Sub-brands are not approved automatically. They must follow `docs/BRAND_GUIDELINES.md` and `docs/NAMING_CONVENTIONS.md`.

## Task Sources

- `TASKS.md` — shared domain implementation
- `CLOUD_MVP_TASKS.md` — free cloud deployment
- `LOCAL_AND_PRODUCTION_TASKS.md` — local development, test automation, staging, production research, and post-launch work
