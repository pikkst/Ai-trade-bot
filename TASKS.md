# The Daily Roast AI — Canonical Implementation Tasks

Last reviewed: 2026-08-01  
Status: Authoritative master implementation sequence  
Execution authority: this file defines order and hard dependencies

## 1. Start Here

A developer or coding agent starts with **Master Task 1 (`M001`)** and proceeds in dependency order until **Master Task 36 (`M036`)** is verified.

Detailed files such as `UX_DESIGN_TASKS.md`, `CLOUD_MVP_TASKS.md`, `LOCAL_AND_PRODUCTION_TASKS.md`, and `SPRINT_3_TASKS.md` through `SPRINT_19_TASKS.md` contain deeper acceptance criteria. They do not override the order or hard dependencies in this file.

Read before implementation:

1. `AGENTS.md`;
2. `docs/IMPLEMENTATION_EXECUTION_PLAN.md`;
3. the selected master task below;
4. every specification and detailed task file referenced by that master task;
5. the existing implementation, tests, migrations, and generated artifacts.

## 2. Active Architecture

The MVP uses:

- Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, and Alembic;
- a one-shot research-cycle CLI;
- React, TypeScript, Vite, and TanStack Query;
- Supabase PostgreSQL and Auth;
- Binance Spot public REST with finalized candles;
- Google Gemini through the official `google-genai` SDK;
- GitHub Actions best-effort scheduling;
- Cloudflare Pages and Render Free for the first cloud demo;
- append-only accounting, deterministic risk, idempotency, and mandatory reconciliation;
- paper trading only.

Deferred unless an accepted ADR and measured need activate them:

- Redis and ARQ;
- persistent workers;
- Binance WebSocket ingestion;
- hosted Prometheus and Grafana;
- Kubernetes;
- Binance test/private credentials;
- live trading.

## 3. Status Model

- `[ ] NOT_STARTED`
- `[~] IN_PROGRESS`
- `[!] BLOCKED`
- `[i] IMPLEMENTED_NOT_VERIFIED`
- `[x] VERIFIED`
- `[-] DEFERRED`
- `[n/a] NOT_APPLICABLE_WITH_APPROVAL`

Only `[x] VERIFIED` is complete.

Every completed task records:

- implementation commit or pull request;
- changed source and migration paths;
- commands and tests executed;
- coverage, invariant, security, accessibility, and recovery evidence as applicable;
- generated artifact hashes;
- documentation changes;
- known limitations and follow-up IDs.

## 4. Master Sequence Overview

| ID | Outcome | Hard dependencies |
|---|---|---|
| M001 | Repository scaffold and shared command entry point | None |
| M002 | Locked toolchains and baseline CI | M001 |
| M003 | Local Supabase, migrations, Auth, and RLS foundation | M001, M002 |
| M004 | Frontend foundation and versioned design tokens | M001, M002 |
| M005 | Typed settings, logging, errors, transactions, and idempotency | M002, M003 |
| M006 | Project-owned provider contracts and deterministic fakes | M001, M002 |
| M007 | Binance REST market-data ingestion and quality controls | M003, M005, M006 |
| M008 | Immutable snapshots and deterministic feature engineering | M007 |
| M009 | Gemini adapter, prompts, schemas, validation, and budgets | M005, M006, M008 |
| M010 | Deterministic strategy and risk domains | M008, M009 |
| M011 | Paper execution, portfolio ledger, and reconciliation | M003, M005, M010 |
| M012 | Idempotent one-shot research-cycle CLI | M007–M011 |
| M013 | Reproducible backtest and benchmark engine | M007–M011 |
| M014 | Authenticated API, OpenAPI, commands, and read models | M003, M005, M008–M013 |
| M015 | Accessible frontend shell and component system | M004, M014 |
| M016 | Today’s Roast dashboard | M012, M014, M015 |
| M017 | Market Evidence workspace | M008, M014, M015 |
| M018 | Gemini Analysis and Validation workspace | M009, M014, M015 |
| M019 | Strategy and Risk workspace | M010, M014, M015 |
| M020 | Portfolio, Execution, Ledger, and Reconciliation workspace | M011, M014, M015 |
| M021 | Backtest, Benchmark, and Comparison workspace | M013, M014, M015 |
| M022 | Experiment Operations, Cycle, Incident, and Audit workspace | M012, M014, M015, M020 |
| M023 | Auth, Governance, Security, Privacy, and Release workspace | M003, M014, M015, M022 |
| M024 | Product shell, onboarding, search, notifications, Trust Center, and i18n | M016–M023 |
| M025 | Developer portal, documentation health, and traceability | M002, M014, M024 |
| M026 | Full automated verification and deterministic local demo | M001–M025 |
| M027 | Export, restore, recovery, and security release gate | M011, M012, M026 |
| M028 | Free-cloud infrastructure and deployments | M012, M014, M024, M026, M027 |
| M029 | Cloud observability, preflight, and 30-day paper experiment | M028 |
| M030 | Performance, resilience, SLO, quota, cost, and FinOps evidence | M029 |
| M031 | Data lifecycle and dataset governance | M007–M013, M029 |
| M032 | Research review and strategy lifecycle governance | M013, M029–M031 |
| M033 | Incident response, postmortem, and corrective-action system | M029, M030 |
| M034 | Change management and staged paper rollout | M023, M025, M030–M033 |
| M035 | Post-experiment decision and staging readiness | M029–M034 |
| M036 | Production research launch and continuous operations | M035 |

---

# Stage A — Repository and Local Foundation

## [x] Master Task 1 — M001 Repository Scaffold and Shared Commands

### Outcome

Create the minimal backend/frontend repository structure and one cross-platform command entry point without requiring cloud or paid-provider credentials.

### Required Work

- initialize `backend/`, `frontend/`, `supabase/`, `tests/`, `infrastructure/`, and generated-artifact directories;
- create a minimal importable FastAPI application and React/Vite application;
- create stable repository commands for bootstrap, format, lint, type-check, test, local services, API, frontend, and research cycle;
- support Windows PowerShell and one Unix-like shell;
- create safe environment examples and ignore local secrets;
- document clean checkout bootstrap.

### Detailed Sources

- legacy `T1.1` and relevant `T1.2` content from the prior `TASKS.md` history;
- `LOCAL_AND_PRODUCTION_TASKS.md`: `L1.1`, `L1.3`;
- `docs/LOCAL_DEVELOPMENT.md`;
- `docs/ARCHITECTURE.md`;
- `docs/BACKEND.md`;
- `docs/TECH_STACK.md`.

### Verification

- clean import/build smoke tests;
- command help and failure codes;
- no database, Gemini, Binance, or cloud credential required;
- README repository structure matches implementation.

### Completion Gate

A clean checkout can bootstrap the empty application skeleton with one documented command.

### Verification Evidence

- PR #1 was merged to `main` as `ff92f73`; its current head passed all eight repository CI jobs.
- The merged scaffold, shared commands, Windows/Unix bootstrap paths, safe environment examples, backend smoke tests, frontend tests/build, and documentation checks were fetched and inspected before dependency advancement.
- Cloud/database/provider credentials and live trading are not required by the scaffold.

## [x] Master Task 2 — M002 Locked Toolchains and Baseline CI

### Outcome

Establish reproducible Python and Node dependency installation plus baseline quality/security CI.

### Required Work

- configure locked Python and frontend dependencies;
- configure Ruff, MyPy strict, Pytest, Hypothesis, Bandit, frontend lint/type/test/build tools;
- create shared quality commands reused by CI;
- add GitHub Actions for format, lint, type, unit tests, secret scanning, dependency review, and documentation links;
- pin third-party actions and container/tool versions;
- ensure normal CI uses no production data or paid provider.

### Detailed Sources

- legacy `T1.2`, `T1.4`;
- `LOCAL_AND_PRODUCTION_TASKS.md`: `L2.1`, `L2.5` foundations;
- `docs/TESTING.md`;
- `docs/SECURITY.md`;
- `CONTRIBUTING.md`.

### Verification

- install from lock files on clean CI;
- deliberate lint/test/link failure is detected and reverted;
- no secrets in caches, logs, or artifacts.

### Completion Gate

Every pull request runs a deterministic baseline quality pipeline using repository-owned commands.

### Implementation Evidence

- Selected detailed cards: `L1.3` command extensions, `L2.1` baseline tooling/coverage, and `L2.5` documentation consistency.
- Toolchains and locks: `.python-version`, `.nvmrc`, `backend/requirements.txt`, and `frontend/package-lock.json`.
- Shared commands: `Makefile` and `tasks.ps1` expose `quality`, `lock-check`, `security-test`, `frontend-audit`, and `docs-check` with non-zero failure propagation.
- CI/security: immutable action SHAs, fixed runner/tool selectors, read-only default permissions, Ruff, MyPy strict, Pytest/Hypothesis/coverage, Bandit, dependency audits/review, Gitleaks, frontend test/build, and deterministic documentation checks.
- Environment: normal CI explicitly uses the fake AI provider and disables Gemini, paid-provider usage, private Binance access, and live trading; no cache or artifact upload is configured.
- Local verification: Python 3.12.12 locked install; Ruff format/lint; MyPy strict; 13 Pytest/Hypothesis tests with 90.91% branch coverage; Bandit; locked `pip-audit`; frontend format/lint/type/test/build; zero-finding `npm audit`; documentation consistency; workflow YAML/pin scan; and Gitleaks 8.30.1 over 245 commits with no leaks.
- Failure proof: temporary lint, test, and broken-link probes returned non-zero status and were removed; the permanent regression tests retain broken-link, malformed-task, and command failure-propagation coverage.
- PR #2 was merged to `main` as `242ff72`; the Windows Hypothesis timing regression was corrected separately in PR #4 and merged as `369f71b` after all repository CI jobs passed.
- The merged commits were fetched and inspected; the local Windows `quality` gate passed with backend/frontend tests, lint, type checks, build, and documentation checks.
- Deferred to mapped later tasks: database/Auth/RLS integration (`M003`/`M026`), frontend accessibility/E2E and bundle inspection (`M015`/`M024`/`M026`), provider contracts (`M006`), and release-stage Semgrep/Trivy/SBOM/provenance gates (`M026`/`M027`/`M036`).

## [i] Master Task 3 — M003 Local Supabase, Migrations, Auth, and RLS Foundation

### Outcome

Provide a resettable local PostgreSQL/Auth environment that mirrors the cloud security model without depending on a cloud project.

### Required Work

- create `supabase/config.toml` and deterministic seed data;
- configure SQLAlchemy 2 sessions and Alembic/Supabase migrations;
- create foundational identity, workspace, configuration, audit, and domain tables in additive migrations;
- implement Supabase Auth subject mapping and owner/operator/viewer roles;
- enable deny-by-default RLS on every Data API-visible object;
- prohibit browser writes to financial/control tables;
- add approved read-only views;
- provide local reset/start/stop/migrate/seed commands.

### Detailed Sources

- legacy `T2.3`;
- `LOCAL_AND_PRODUCTION_TASKS.md`: `L1.2`, `L2.2`;
- `CLOUD_MVP_TASKS.md`: `C2` contract, excluding cloud provisioning;
- `docs/DATABASE_SCHEMA.md`;
- `docs/SECURITY.md`;
- `docs/API_SPECIFICATION.md`.

### Verification

- upgrade from empty database to one migration head;
- deterministic reset/seed;
- RLS matrix for anonymous, viewer, operator, owner, workflow/service, and migration roles;
- transaction commit/rollback and workspace isolation tests;
- no cloud credential required.

### Completion Gate

Local database, Auth, migrations, RLS, and seed workflows are reproducible in local development and CI.

### Implementation Evidence

- PR #3 implemented the M003 foundation but was merged into the stale M002 feature branch instead of `main`; this corrective integration branch isolates the M003 diff against current `main`.
- PR #7 review identified that local administrator membership must not be embedded in the deployable migration chain. The correction moves cluster-role bootstrap to local-only `supabase/roles.sql`, removes the unmerged membership migration, and gives request-facing code a dedicated least-privilege `app_runtime` login.
- Alembic verifies durable trusted-role attributes and rejects browser/runtime membership without hard-coding a valid deployment principal list.
- M003 is `IMPLEMENTED_NOT_VERIFIED` while the corrected clean reset, runtime-denial tests, quality gate, and PR checks are pending.

## [ ] Master Task 4 — M004 Frontend Foundation and Design Tokens

### Outcome

Create a strict, accessible, token-driven frontend foundation before product screens.

### Required Work

- configure React, TypeScript strict, Vite, React Router, TanStack Query, testing, accessibility, and production builds;
- implement versioned color, typography, spacing, radius, motion, chart, and status tokens;
- support light, dark, and system modes;
- establish localization-ready content keys and financial formatting utilities;
- prevent server-secret environment variables from entering the build.

### Detailed Sources

- `UX_DESIGN_TASKS.md`: `UX1`, relevant `UX9` foundations;
- `docs/DESIGN_SYSTEM.md`;
- `docs/UI_UX_GUIDELINES.md`;
- `docs/BRAND_GUIDELINES.md`;
- `docs/NAMING_CONVENTIONS.md`.

### Verification

- frontend lint, type, unit, accessibility, and build pass;
- contrast and reduced-motion tests;
- bundle secret scan;
- official product identity is used.

### Completion Gate

The frontend can render a tested token reference page in all supported themes with no domain screen yet required.

## [ ] Master Task 5 — M005 Typed Settings, Logging, Errors, Transactions, and Idempotency

### Outcome

Create the safe application infrastructure used by every domain and command.

### Required Work

- implement typed Pydantic settings and safe environment profiles;
- hard-disable live/private trading capabilities in the MVP model;
- implement structured logging, redaction, correlation IDs, request/job/cycle IDs;
- define stable application/domain errors and safe API envelopes;
- define transaction helpers and prohibit network calls inside transactions;
- implement idempotency records/keys and optimistic concurrency primitives;
- implement liveness/readiness foundations.

### Detailed Sources

- legacy `T2.1`, `T2.2`, transaction/idempotency portions of `T2.3`;
- `docs/BACKEND.md`;
- `docs/API_SPECIFICATION.md`;
- `docs/OBSERVABILITY.md`;
- `docs/SECURITY.md`.

### Verification

- invalid/unsafe configuration rejects startup without leaking secrets;
- log redaction and context propagation tests;
- idempotent duplicate-command tests;
- transaction rollback and safe error mapping tests.

### Completion Gate

All later services can depend on one typed, observable, transaction-safe, idempotent application foundation.

## [ ] Master Task 6 — M006 Provider Contracts and Deterministic Fakes

### Outcome

Define project-owned exchange, AI, clock, and scheduling protocols plus deterministic failure-injection fakes.

### Required Work

- define Binance market-data protocol and project-owned models/errors;
- define `LLMProvider` and project-owned request/response/usage/safety models;
- define injectable clock, ID, and scheduler context boundaries;
- implement deterministic fake Binance and Gemini scenarios;
- version fixtures and scenario configuration;
- prevent SDK types from leaking into domain code.

### Detailed Sources

- legacy `T3.1`, `T5.1`;
- `LOCAL_AND_PRODUCTION_TASKS.md`: `L1.4`;
- `docs/BINANCE_INTEGRATION.md`;
- `docs/AI_ARCHITECTURE.md`;
- `docs/GEMINI_INTEGRATION.md`.

### Verification

- protocol and serialization tests;
- fake success, timeout, rate-limit, malformed, refusal, safety, stale, and gap scenarios;
- deterministic repeated runs;
- no network call in normal unit tests.

### Completion Gate

Core domains can be implemented and tested against stable project-owned interfaces without live providers.

---

# Stage B — Core Research Domains

## [ ] Master Task 7 — M007 Binance REST Market Data and Quality

### Outcome

Persist reproducible finalized Binance Spot metadata and candles with complete quality evidence and gap repair.

### Required Work

- implement public REST server time, exchange metadata, symbols, and finalized candle retrieval;
- support BTC/EUR as primary and approved observation symbols;
- preserve Decimal values and UTC timestamps;
- implement bounded, checkpointed, idempotent backfill and hourly incremental fetch;
- detect invalid OHLC, duplicates, out-of-order rows, gaps, stale data, and clock drift;
- create append-only quality/correction events;
- block downstream use until approved and fresh.

### Detailed Sources

- legacy `T3.2`, `T3.3`; `T3.4` WebSocket scope is deferred;
- `docs/MARKET_DATA.md`;
- `docs/BINANCE_INTEGRATION.md`;
- `docs/DATA_LIFECYCLE_DATASET_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md` relevant foundations.

### Verification

- fixtures plus optional protected public REST smoke;
- pagination, 429, timeout, restart, duplicate, gap, correction, and stale tests;
- no private Binance credential;
- same input produces same persisted identities/hashes.

### Completion Gate

A requested finalized candle range can be loaded, validated, repaired, and approved reproducibly using REST only.

## [ ] Master Task 8 — M008 Immutable Snapshots and Deterministic Features

### Outcome

Create immutable snapshot and feature evidence that every later analysis can reproduce.

### Required Work

- implement ordered snapshot membership, hashes, quality/freshness state, and lineage;
- implement versioned returns, SMA, EMA, RSI, ATR, volatility, and volume features;
- define warm-up and insufficient-history behavior;
- use Decimal or documented precision rules;
- persist calculation input/output hashes and typed values;
- prohibit look-ahead and mutable historical replacements.

### Detailed Sources

- legacy Epic 4 tasks;
- `docs/MARKET_DATA.md`;
- `docs/FEATURE_ENGINEERING.md` if present;
- `docs/DATABASE_SCHEMA.md`;
- `SPRINT_6_TASKS.md` source-read requirements.

### Verification

- reference calculations and boundary cases;
- deterministic hashes;
- no-look-ahead and finalized-data assertions;
- stale/invalid snapshot rejection;
- correction invalidation lineage.

### Completion Gate

Identical approved candles and feature versions produce identical immutable snapshot and feature outputs.

## [ ] Master Task 9 — M009 Gemini Adapter, Prompts, Schemas, Validation, and Budgets

### Outcome

Produce optional evidence-grounded Gemini reports that remain advisory and fail closed.

### Required Work

- implement the official `google-genai` adapter behind `LLMProvider`;
- implement immutable provider/model, prompt, report schema, safety, validation, and budget versions;
- send minimum structured snapshot/feature evidence only;
- enforce structured output and independent application validation;
- verify evidence references and unsupported claims;
- cover prompt injection, false certainty, stale sources, refusal, safety block, empty, malformed, timeout, 429, and provider errors;
- enforce request/token/cost budgets before calls;
- persist usage, attempts, validation, fallback, and report lineage;
- implement deterministic fallback/HOLD.

### Detailed Sources

- legacy Epic 5 tasks;
- `SPRINT_11_TASKS.md` backend/data tasks;
- `docs/GEMINI_INTEGRATION.md`;
- `docs/AI_ARCHITECTURE.md`;
- `docs/AI_PROMPTS.md`.

### Verification

- deterministic fake-provider suite;
- schema, grounding, unsupported-claim, injection, retry, budget, and fallback tests;
- protected real-provider smoke excluded from normal CI;
- no tools, secrets, position sizing, or execution authority.

### Completion Gate

Only an accepted, grounded, versioned report can become optional strategy evidence; all other outcomes degrade safely.

## [ ] Master Task 10 — M010 Deterministic Strategy and Risk

### Outcome

Convert immutable evidence into deterministic intents and non-bypassable risk outcomes.

### Required Work

- implement HOLD smoke strategy and explainable BTC/EUR trend baseline;
- implement immutable strategy versions, configurations, reason codes, and evaluation hashes;
- define required/optional/ignored Gemini evidence policy;
- implement risk policy versions and checks for position, notional, exposure, stale data, volatility, cooldown, open orders, duplicates, precision, minimum notional, daily/total drawdown, and halts;
- support approve, reduce, reject, halt portfolio, and halt workspace;
- prevent strategy from creating orders or selecting final size;
- fail closed on missing policy or integrity evidence.

### Detailed Sources

- legacy Epic 6 tasks;
- `SPRINT_7_TASKS.md` domain/API tasks;
- `docs/STRATEGY_ENGINE.md`;
- `docs/RISK_ENGINE.md`;
- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- deterministic repeated evaluations;
- all action/outcome and boundary tests;
- stale, missing, contradictory, provider-outage, drawdown, duplicate, and halt cases;
- property tests for sizing and limits;
- no direct order side effect.

### Completion Gate

Every non-HOLD intent has one deterministic risk result and no path can bypass it.

## [ ] Master Task 11 — M011 Paper Execution, Portfolio Ledger, and Reconciliation

### Outcome

Simulate approved orders with realistic costs and maintain an append-only accounting source of truth.

### Required Work

- implement paper portfolios, virtual funding, state versions, balances, reservations, and positions;
- implement market/limit orders, lifecycle transitions, partial fills, cancellation, precision, minimum notional, time in force, conservative timing, spread, slippage, and fees;
- enforce one approved risk evaluation to at most one order;
- atomically commit fill, order transition, balanced ledger, audit/outbox, and projection effects;
- implement cost basis, realized/unrealized P&L, equity, exposure, and drawdown projections;
- implement deterministic rebuild and reconciliation;
- halt on mismatch or missing required financial evidence;
- use Decimal for all financial values.

### Detailed Sources

- legacy Epic 7 tasks;
- `SPRINT_8_TASKS.md` domain/API tasks;
- `docs/PAPER_TRADING.md`;
- `docs/PORTFOLIO_ENGINE.md`;
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- order-state and timing tests;
- duplicate/restart/idempotency tests;
- ledger balance and conservation properties;
- reservation/release, fees, P&L, precision, partial-fill, and cancellation cases;
- reconstruction equals reconciled state;
- mismatch triggers halt.

### Completion Gate

Every simulated financial effect is atomic, append-only, reconstructable, and reconciled to the ledger.

## [ ] Master Task 12 — M012 Idempotent One-Shot Research-Cycle CLI

### Outcome

Execute one complete restart-safe research cycle without Redis, ARQ, a persistent worker, WebSocket, Render availability, or local persistent disk.

### Required Work

- implement a documented CLI entry point;
- acquire PostgreSQL advisory lock or durable lease;
- derive stable occurrence/cycle key from experiment and intended occurrence;
- fetch actual eligible finalized candles, repair gaps, snapshot, features, optional Gemini, strategy, risk, paper execution, ledger, reconciliation, cycle status, and audit;
- return existing side effects on retry;
- record intended/actual time, workflow metadata, stage results, and failures;
- exit non-zero on integrity failure;
- always release or expire lock safely.

### Detailed Sources

- `CLOUD_MVP_TASKS.md`: `C3`;
- `SPRINT_10_TASKS.md` cycle/lock/idempotency tasks;
- `docs/ARCHITECTURE.md`;
- `docs/FREE_CLOUD_ARCHITECTURE.md`;
- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- complete fake-provider cycle;
- duplicate dispatch, overlap, interruption, timeout, stale data, Gemini degradation, risk rejection, order/fill, reconciliation mismatch, and restart tests;
- no duplicate financial side effect;
- no dependency on Render or local files.

### Completion Gate

One command can safely execute, retry, inspect, and reconcile a complete logical cycle.

## [ ] Master Task 13 — M013 Reproducible Backtest and Benchmark Engine

### Outcome

Replay historical finalized data through the same strategy, risk, execution, and accounting contracts.

### Required Work

- implement immutable run configuration, queue/job state, cancellation, timeout, event loop, and reports;
- enforce no look-ahead and next-event execution timing;
- support disabled/precomputed Gemini modes; no silent live calls;
- require fees, spread, slippage, precision, partial fills, ledger, and reconciliation;
- calculate versioned metrics with explicit null/insufficient-sample behavior;
- include cash and buy-and-hold benchmarks;
- preserve train/validation/untouched-test and walk-forward metadata;
- store code, dependency, migration, data, strategy, risk, execution, accounting, and seed provenance;
- preserve failed/rejected variants.

### Detailed Sources

- legacy Epic 8 tasks;
- `SPRINT_9_TASKS.md` engine/API tasks;
- `docs/BACKTEST_ENGINE.md`;
- `docs/BACKTEST_EXPERIMENT_COMPARISON_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- deterministic repeat and report hash;
- no-look-ahead assertions;
- benchmark and metric reference fixtures;
- zero denominator/insufficient sample behavior;
- ledger/reconciliation and failure-stop tests;
- cancellation, timeout, resource-bound tests.

### Completion Gate

A complete run is reproducible from its manifest and cannot appear final when incomplete or unreconciled.

---

# Stage C — API and Product Experience

## [ ] Master Task 14 — M014 Authenticated API, OpenAPI, Commands, and Read Models

### Outcome

Expose all implemented domains through versioned, authorized, bounded, documented APIs.

### Required Work

- implement `/api/v1`, health, Auth/session, workspace, configuration, market, features, analyses, strategy, risk, portfolio, orders, ledger, reconciliation, backtest, experiment, cycle, audit, job, search, and export resources as dependencies allow;
- implement owner/operator/viewer permissions in handlers and RLS;
- require idempotency and expected-version guards for commands;
- serialize Decimal as strings and timestamps as UTC RFC 3339;
- implement pagination, filter allowlists, rate-limit classes, safe errors, correlation IDs, and redaction;
- generate deterministic OpenAPI and frontend types;
- prevent undocumented endpoints.

### Detailed Sources

- `docs/API_SPECIFICATION.md`;
- `docs/DATABASE_SCHEMA.md`;
- API portions of `SPRINT_5_TASKS.md` through `SPRINT_19_TASKS.md`;
- `SPRINT_12_TASKS.md` authorization tasks;
- `SPRINT_14_TASKS.md` API catalog tasks.

### Verification

- every operation has contract/integration/E2E coverage;
- authorization/RLS matrix;
- invalid IDs, filters, concurrency, idempotency, rate limit, and redaction tests;
- OpenAPI/type generation drift check;
- no arbitrary prompt or database endpoint.

### Completion Gate

Every implemented domain operation has one documented project-owned API contract and enforced permission.

## [ ] Master Task 15 — M015 Accessible Frontend Shell and Component System

### Outcome

Build the shared application shell and safety-oriented component library consumed by all workspaces.

### Required Work

- implement responsive authenticated shell, route guards, navigation, breadcrumbs, mode/environment status, account menu, error boundaries, loading, empty, stale, partial, unauthorized, and degraded states;
- implement accessible buttons, forms, overlays, tabs, tables, timelines, alerts, status badges, charts with text alternatives, data formatting, and critical safety components;
- use generated API types and TanStack Query;
- support keyboard, screen reader, zoom/reflow, reduced motion, light/dark/system;
- preserve simulation, freshness, reconciliation, halt, and critical incident state at narrow viewports.

### Detailed Sources

- `UX_DESIGN_TASKS.md`: `UX2`–`UX4`, `UX9`, `UX10` as applicable;
- `SPRINT_3_TASKS.md`;
- `SPRINT_4_TASKS.md`;
- `docs/FRONTEND_APPLICATION_SHELL.md`;
- `docs/CORE_COMPONENT_LIBRARY_IMPLEMENTATION.md`.

### Verification

- component, accessibility, responsive, visual-regression, route, and bundle-secret tests;
- no frontend-only authorization;
- no critical state hidden by layout or color-only presentation.

### Completion Gate

All later screens can be composed from tested canonical components and one consistent application shell.

## [ ] Master Task 16 — M016 Today’s Roast Dashboard

### Outcome

Provide an evidence-first summary of the latest or selected completed research cycle.

### Required Work

Complete mandatory cards in `SPRINT_5_TASKS.md`, including read model, endpoint, route, freshness/simulation/halt header, market regime, evidence, Gemini state, strategy/risk, portfolio/reconciliation, cycle status, lineage, errors, export, accessibility, and observability.

### Detailed Sources

- `SPRINT_5_TASKS.md`;
- `docs/TODAYS_ROAST_DASHBOARD_IMPLEMENTATION.md`.

### Verification

- loading/empty/stale/partial/failed/halted/reconciliation states;
- no positive metric outranks critical safety state;
- direct links to complete lineage;
- responsive/accessibility/E2E tests.

### Completion Gate

A user can understand current evidence and safety state before interpreting performance.

## [ ] Master Task 17 — M017 Market Evidence Workspace

### Outcome

Expose candles, snapshots, features, quality, freshness, corrections, and lineage without client-side authority.

### Required Work

Complete mandatory cards in `SPRINT_6_TASKS.md` after M007–M008 and M014 exist.

### Detailed Sources

- `SPRINT_6_TASKS.md`;
- `docs/MARKET_EVIDENCE_WORKSPACE_IMPLEMENTATION.md`;
- `docs/MARKET_DATA.md`.

### Verification

- exact Decimal/UTC display;
- quality, gap, stale, corrected, superseded, and unavailable states;
- accessible chart/table alternatives;
- pagination/filter/security tests.

### Completion Gate

Every displayed market interpretation can trace to exact approved source evidence.

## [ ] Master Task 18 — M018 Gemini Analysis and Validation Workspace

### Outcome

Expose provider attempts, versioned request evidence, validation gates, grounded report, safety, fallback, usage, and budget.

### Required Work

Complete mandatory cards in `SPRINT_11_TASKS.md` after M009 and M014 exist.

### Detailed Sources

- `SPRINT_11_TASKS.md`;
- `docs/GEMINI_ANALYSIS_VALIDATION_WORKSPACE_IMPLEMENTATION.md`;
- `docs/GEMINI_INTEGRATION.md`.

### Verification

- provider success distinct from validation acceptance;
- rejected/blocked/stale/unsafe output never appears validated;
- confidence never presented as profit probability;
- secret/raw-content redaction and prompt-injection rendering tests.

### Completion Gate

The user can inspect why an AI report was accepted or rejected without granting it execution authority.

## [ ] Master Task 19 — M019 Strategy and Risk Workspace

### Outcome

Explain deterministic intent, optional AI evidence, every risk rule, final approval/rejection/halt, and immutable lineage.

### Required Work

Complete mandatory cards in `SPRINT_7_TASKS.md` after M010 and M014 exist.

### Detailed Sources

- `SPRINT_7_TASKS.md`;
- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`;
- `docs/STRATEGY_ENGINE.md`;
- `docs/RISK_ENGINE.md`.

### Verification

- intent versus risk result versus order remain distinct;
- all limits, units, versions, reasons, and state references visible;
- no browser sizing or bypass;
- accessible rule matrices/timelines and security tests.

### Completion Gate

Every actionable or rejected decision is understandable and traceable to deterministic rules.

## [ ] Master Task 20 — M020 Portfolio, Execution, Ledger, and Reconciliation Workspace

### Outcome

Expose the simulated financial state and immutable accounting evidence.

### Required Work

Complete mandatory cards in `SPRINT_8_TASKS.md` after M011 and M014 exist.

### Detailed Sources

- `SPRINT_8_TASKS.md`;
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- requested/approved/ordered/filled/ledger values remain distinct;
- available/reserved balances, cost basis, P&L, fees, exposure, and drawdown use server values;
- balanced transaction, correction, rebuild, and reconciliation evidence;
- mismatch/halt state dominates performance;
- no ledger edit or live-order control.

### Completion Gate

The user can reconstruct every simulated financial effect from order approval through reconciliation.

## [ ] Master Task 21 — M021 Backtest, Benchmark, and Comparison Workspace

### Outcome

Present immutable configuration, methodology, results, benchmarks, robustness, reproducibility, and comparison evidence.

### Required Work

Complete mandatory cards in `SPRINT_9_TASKS.md` after M013–M015 exist.

### Detailed Sources

- `SPRINT_9_TASKS.md`;
- `docs/BACKTEST_EXPERIMENT_COMPARISON_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- incomplete/failed/unreconciled/non-reproducible results cannot appear final;
- metric definitions, null reasons, costs, dataset splits, variants, and benchmark assumptions visible;
- accessible series and full-resolution exports;
- comparison compatibility tests.

### Completion Gate

A reviewer can reproduce and critique a result without interpreting it as future-performance proof.

## [ ] Master Task 22 — M022 Experiment Operations, Cycle, Incident, and Audit Workspace

### Outcome

Operate and investigate the controlled paper experiment with immutable evidence.

### Required Work

Complete mandatory cards in `SPRINT_10_TASKS.md`, including frozen configuration, preflight, lifecycle commands, schedule/delay, lock/idempotency, cycle lineage, dependencies, incidents, recovery, exports, audit, and report readiness.

### Detailed Sources

- `SPRINT_10_TASKS.md`;
- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`;
- `CLOUD_MVP_TASKS.md` operational contracts.

### Verification

- owner-only, recent-authenticated, idempotent, expected-version commands;
- no generic clear-halt or automatic unsafe resume;
- successful process exit is not enough for complete cycle;
- duplicate/lock/missed/delayed/recovered states;
- full audit history.

### Completion Gate

The experiment can be preflighted, started, paused, halted, investigated, exported, and reported without hidden mutation.

## [ ] Master Task 23 — M023 Auth, Governance, Security, Privacy, and Release Workspace

### Outcome

Govern access, immutable configurations, environments, secrets metadata, migrations, findings, privacy, backups, and releases.

### Required Work

Complete mandatory cards in `SPRINT_12_TASKS.md` after M003, M014, M015, and M022 exist.

### Detailed Sources

- `SPRINT_12_TASKS.md`;
- `docs/AUTH_CONFIGURATION_SECURITY_RELEASE_WORKSPACE_IMPLEMENTATION.md`;
- `docs/SECURITY.md`;
- `docs/DEPLOYMENT.md`.

### Verification

- session/member/permission/RLS assurance;
- no secret values or usable hashes in UI/API;
- immutable configuration lifecycle and dependency diff;
- migration drift/rehearsal/rollback gates;
- security/privacy exception expiry;
- backup means tested restore;
- release cannot authorize live trading.

### Completion Gate

No privileged change or release proceeds without server-provided permission, evidence, approval, and audit.

## [ ] Master Task 24 — M024 Product Shell, Onboarding, Search, Notifications, Trust Center, and i18n

### Outcome

Turn the workspaces into one coherent bilingual research product.

### Required Work

Complete mandatory cards in `SPRINT_13_TASKS.md` and remaining applicable `UX_DESIGN_TASKS.md` cards.

### Detailed Sources

- `SPRINT_13_TASKS.md`;
- `docs/PRODUCT_SHELL_ONBOARDING_TRUST_I18N_WORKSPACE_IMPLEMENTATION.md`;
- `UX_DESIGN_TASKS.md`: remaining product/landing/visual tasks.

### Verification

- global safety hierarchy and authorized navigation/search;
- role-aware onboarding and material acknowledgements;
- privacy-minimized notifications;
- English/Estonian semantic parity for safety and financial terms;
- Trust Center and public-demo separation;
- no command-palette bypass or arbitrary financial language.

### Completion Gate

Users can navigate, search, learn, and interpret evidence consistently in English or Estonian without losing safety context.

## [ ] Master Task 25 — M025 Developer Portal, Documentation Health, and Traceability

### Outcome

Make requirements, tasks, ADRs, APIs, schemas, migrations, source, tests, scans, runbooks, artifacts, and releases traceable.

### Required Work

Complete mandatory cards in `SPRINT_14_TASKS.md`.

### Detailed Sources

- `SPRINT_14_TASKS.md`;
- `docs/DEVELOPER_PORTAL_DOCUMENTATION_TRACEABILITY_WORKSPACE_IMPLEMENTATION.md`;
- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`.

### Verification

- documentation IDs/owners/review dates and conflict/freshness checks;
- OpenAPI/schema/error/event/permission/metric catalogs;
- master task to implementation/test/release evidence;
- runbook registry and drill evidence;
- generated artifact drift and edited-applied-migration detection;
- public/private documentation separation.

### Completion Gate

A reviewer can prove what implements and tests every material requirement at one exact revision.

---

# Stage D — Verification and Local Completion

## [ ] Master Task 26 — M026 Full Automated Verification and Deterministic Local Demo

### Outcome

Prove the integrated product locally and in CI before cloud provisioning.

### Required Work

- complete `LOCAL_AND_PRODUCTION_TASKS.md` `L1.5` and `L2.1`–`L2.5` without cloud-only cycles;
- build deterministic end-to-end demo seed;
- run unit, property, migration, RLS, Auth, integration, provider contract, API contract, component, accessibility, visual, E2E, documentation, security, and build tests;
- enforce coverage and stable-error-code requirements;
- verify no production data, paid calls, or secrets;
- verify every master task M001–M025 has implementation evidence or approved not-applicable state.

### Verification

- clean checkout bootstrap and local reset/demo;
- complete ENTER→risk→paper order→fill→ledger→reconcile flow;
- rejected, stale, invalid AI, duplicate, halt, and mismatch flows;
- generated artifacts current;
- all mandatory CI checks green.

### Completion Gate

A clean local/CI environment demonstrates the full paper-research product deterministically without cloud or paid credentials.

## [ ] Master Task 27 — M027 Export, Restore, Recovery, and Security Release Gate

### Outcome

Prove recoverability and security before any formal cloud experiment.

### Required Work

- implement logical export and isolated restore commands;
- verify migration revision, hashes, ledger rebuild, reconciliation, Auth/data handling, and no source-control backup artifacts;
- execute database outage, partial transaction, duplicate cycle, stale data, Gemini quota, provider timeout, and halt recovery drills;
- complete secret, dependency, static, container/filesystem, frontend-bundle, Auth/RLS, and financial-integrity scans;
- create and verify required runbooks;
- resolve critical/high findings or record approved time-limited exceptions where policy permits.

### Detailed Sources

- `LOCAL_AND_PRODUCTION_TASKS.md`: `L2.6`;
- `docs/TESTING.md`;
- `docs/SECURITY.md`;
- `docs/DEPLOYMENT.md`;
- `SPRINT_18_TASKS.md` runbook prerequisites.

### Completion Gate

An isolated restore succeeds and reconciles, and no unresolved release-blocking security or integrity finding remains.

---

# Stage E — Free-Cloud Demo and Controlled Experiment

## [ ] Master Task 28 — M028 Free-Cloud Infrastructure and Deployments

### Outcome

Deploy the verified paper-research product without requiring the owner’s local computer.

### Required Work

- complete `CLOUD_MVP_TASKS.md` `C1`–`C6` in canonical dependency order;
- create a dedicated Supabase project, never reuse Eventnexus;
- apply migrations/RLS through controlled workflows;
- configure GitHub Actions scheduled and manual one-shot cycle with concurrency and timeout;
- deploy FastAPI to Render and frontend to Cloudflare Pages;
- configure approved domains, HTTPS, CORS, CSP, Auth redirects, and environment separation;
- use secrets/variables with least privilege;
- verify Render cold start does not control scheduled cycles;
- keep local filesystem non-authoritative.

### Verification

- public HTTPS smoke tests;
- Auth/RLS/API/frontend checks;
- scheduled/manual cycle with duplicate protection;
- frontend bundle secret scan;
- deployment revision and migration evidence;
- no paid auto-upgrade or live/private exchange capability.

### Completion Gate

The demo is accessible from the cloud and scheduled research continues independently of Render sleep and the local computer.

## [ ] Master Task 29 — M029 Cloud Observability, Preflight, and 30-Day Paper Experiment

### Outcome

Run and close the controlled virtual EUR 20 experiment with complete evidence.

### Required Work

- complete `CLOUD_MVP_TASKS.md` `C7` and `C8`;
- persist cycle status, freshness, Gemini, risk, halt, reconciliation, dependency, incident, export, and audit evidence;
- execute and record cloud export/restore drill;
- pass exact configuration-hash preflight;
- freeze BTC/EUR 1h, EUR 20, 25% position, EUR 5 order, 5% daily and 15% total drawdown, one open order, no leverage/shorting, EUR 0 Gemini budget default, cash/buy-and-hold benchmarks;
- obtain owner approval;
- start, monitor, pause/halt when required, complete, export, and report the 30-day or approved early-stop experiment;
- do not fabricate missed-cycle trades.

### Verification

- first scheduled cycle and ongoing status;
- no duplicate financial side effect;
- no unresolved reconciliation mismatch;
- all incidents and free-tier limitations documented;
- final export/report and owner closure decision.

### Completion Gate

The experiment has an auditable terminal state and final report; profit is not a completion criterion.

---

# Stage F — Research Review and Product Hardening

## [ ] Master Task 30 — M030 Performance, Resilience, SLO, Quota, Cost, and FinOps Evidence

### Outcome

Measure actual reliability, capacity, provider limits, costs, and scale triggers without inventing guarantees.

### Required Work

Complete mandatory cards in `SPRINT_15_TASKS.md` using measured experiment/deployment evidence.

### Detailed Sources

- `SPRINT_15_TASKS.md`;
- `docs/PERFORMANCE_RESILIENCE_CAPACITY_FINOPS_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- versioned SLI/SLO/error-budget definitions;
- API/cold-start/frontend/cycle/stage/database/backtest/provider measurements;
- measured/provider-reported/estimated/billed evidence classification;
- quotas, budgets, anomalies, forecasts, resilience tests, and no-auto-upgrade rules;
- profit is not an SLO.

### Completion Gate

Every reliability or cost claim identifies its source, window, revision, sample adequacy, and limitation.

## [ ] Master Task 31 — M031 Data Lifecycle and Dataset Governance

### Outcome

Govern datasets, lineage, quality, retention, holds, archives, deletion/anonymization, and reproducibility.

### Required Work

Complete mandatory cards in `SPRINT_16_TASKS.md`.

### Detailed Sources

- `SPRINT_16_TASKS.md`;
- `docs/DATA_LIFECYCLE_DATASET_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- immutable dataset/version registry and manifests;
- quality gates and quarantine;
- complete source→derived lineage and correction propagation;
- retention/hold/cleanup, archive/restore, deletion/anonymization boundaries;
- protected financial/audit evidence cannot be silently removed;
- reproducibility after archive/restore.

### Completion Gate

Every research result references governed data whose quality, lineage, retention, and availability are explicit.

## [ ] Master Task 32 — M032 Research Review and Strategy Lifecycle Governance

### Outcome

Make strategy promotion a human-controlled evidence decision rather than a performance score.

### Required Work

Complete mandatory cards in `SPRINT_17_TASKS.md`.

### Detailed Sources

- `SPRINT_17_TASKS.md`;
- `docs/RESEARCH_REVIEW_STRATEGY_LIFECYCLE_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- hypothesis/test-plan registry and immutable evidence snapshot;
- train/validation/untouched-test integrity;
- variants, robustness, walk-forward, reproducibility, benchmark, cost, risk, paper observation, accounting, incident, and operational evidence;
- reviewer conflicts and owner decision;
- promotion only to future paper configurations;
- rollback, deprecation, retirement, and archive.

### Completion Gate

No strategy advances solely because it was profitable, and active experiments remain frozen.

## [ ] Master Task 33 — M033 Incident Response, Postmortem, and Corrective Actions

### Outcome

Operationalize alert-to-learning workflows that distinguish containment, restoration, integrity verification, and resolution.

### Required Work

Complete mandatory cards in `SPRINT_18_TASKS.md`.

### Detailed Sources

- `SPRINT_18_TASKS.md`;
- `docs/INCIDENT_RESPONSE_POSTMORTEM_LEARNING_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- alert registry/routing/deduplication/acknowledgement;
- incident lifecycle, roles, timelines, evidence preservation, communications, containment, recovery, and financial-integrity checks;
- blameless postmortem and causal/contributing-factor analysis;
- corrective actions have owners, dates, tests, verification, and effectiveness review;
- no automatic unsafe resume.

### Completion Gate

An incident cannot close before required service, security, data, ledger, reconciliation, communication, and follow-up gates are evidenced.

## [ ] Master Task 34 — M034 Change Management and Staged Paper Rollout

### Outcome

Govern every material model, prompt, data, feature, strategy, risk, execution, accounting, migration, security, UX, cost, or infrastructure behavior change.

### Required Work

Complete mandatory cards in `SPRINT_19_TASKS.md`.

### Detailed Sources

- `SPRINT_19_TASKS.md`;
- `docs/CHANGE_MANAGEMENT_ROLLOUT_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`.

### Verification

- immutable proposals and complete before/after behavior-set hashes;
- risk classification, dependency impact, compatibility, evidence plan/completeness, reviewers/conflicts, immutable approval snapshot;
- staged local/CI/demo/staging/bounded paper canary and stop conditions;
- activation only for future paper configurations;
- rollback/forward-fix, freeze, emergency expiry, deprecation, support window, usage, and removal gates;
- no AI/browser/CI score can approve or activate;
- no auto-spend or live/private exchange path.

### Completion Gate

Material behavior cannot drift or activate without complete evidence, human approval, staged verification, and safe rollback.

---

# Stage G — Staging and Production Research

## [ ] Master Task 35 — M035 Post-Experiment Decision and Staging Readiness

### Outcome

Turn experiment evidence into an explicit stop/repeat/improve/staging decision and, when approved, build isolated staging.

### Required Work

- complete formal post-experiment review using M030–M034 evidence;
- record owner decision, rationale, limitations, and follow-up tasks;
- when staging is approved, complete `LOCAL_AND_PRODUCTION_TASKS.md` `P1.1` and staging portions of `P1.2`;
- use separate database, Auth, Gemini credentials, domains, secrets, and synthetic data;
- deploy immutable production artifacts unchanged;
- rehearse migrations, rollback/forward fix, restore, load/failure, E2E, accessibility, security, privacy, content, and operational checks;
- keep live trading disabled.

### Completion Gate

A release candidate passes isolated production-like staging with complete evidence and explicit owner approval to proceed.

## [ ] Master Task 36 — M036 Production Research Launch and Continuous Operations

### Outcome

Launch and operate a production-grade authenticated research and paper-trading service without authorizing real-money execution.

### Required Work

- complete remaining applicable `LOCAL_AND_PRODUCTION_TASKS.md` production and post-launch tasks;
- use protected CI/CD, manual approval, immutable artifacts, one controlled migration step, smoke/reconciliation verification, and rollback readiness;
- harden session/recovery/MFA decisions, RLS, secrets, backups, restore, privacy, incident routing, SLOs, cost budgets, support, status, and runbooks;
- publish data policies, disclaimers, Trust Center, release notes, and operational ownership;
- measure reliability, capacity, cost, and user comprehension;
- perform periodic access, security, privacy, recovery, model/prompt, strategy, and documentation reviews;
- process all material changes through M034;
- preserve paper-only and live-trading-disabled configuration.

### Completion Gate

The production research service operates with current release, security, privacy, backup/restore, reconciliation, incident, SLO, cost, documentation, and support evidence. Private Binance and live trading remain separate unapproved future assessments.

---

# 5. Global Completion Gate

The project reaches the documented production-research completion milestone only when:

- M001–M036 are `[x] VERIFIED`, except explicitly approved deferred/not-applicable scope;
- no unresolved critical security, privacy, RLS, migration, financial-integrity, ledger, or reconciliation issue exists;
- all deployed artifacts map to one source revision and migration head;
- backup has been restored and reconciled;
- the 30-day paper experiment and post-experiment decision are complete;
- user-facing content clearly states simulation, uncertainty, and limitations;
- Gemini remains advisory;
- strategy and risk remain deterministic and non-bypassable;
- no private Binance credential, live order path, leverage, margin, futures, shorting, withdrawal, or custody capability exists.

# 6. Developer Handoff Checklist

Before starting a master task:

1. confirm all hard dependencies are `[x] VERIFIED`;
2. claim one master task and the exact detailed cards being implemented;
3. read all references and inspect current code/migrations/tests;
4. define failure cases, invariants, security/privacy impact, and evidence;
5. avoid unrelated architecture changes.

Before marking it verified:

1. satisfy every mandatory detailed acceptance criterion;
2. run relevant repository commands and record results;
3. update task status/evidence and affected documentation;
4. verify no secrets, production data, unsafe floats, bypasses, or undocumented endpoints;
5. fetch the commit/PR and confirm the intended files and tests;
6. leave explicit follow-up IDs for anything deferred.
