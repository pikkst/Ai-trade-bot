# AGENTS.md

Last reviewed: 2026-08-01  
Status: Authoritative implementation guide for AI coding agents and human contributors

## 1. Purpose

This file governs implementation work for **The Daily Roast AI**, an evidence-driven market-intelligence, backtesting, paper-trading, and Gemini-assisted decision-support platform.

The MVP, cloud demo, controlled experiment, staging environment, and production research service remain paper-only. This repository does not authorize live trading, private Binance execution, withdrawals, custody, leverage, margin, futures, options, or short selling.

## 2. Instruction Precedence

1. security, privacy, financial-integrity, and fail-closed requirements;
2. this file;
3. `docs/PRODUCT_REQUIREMENTS.md`;
4. accepted architecture documents and ADRs;
5. domain and workspace implementation specifications;
6. `TASKS.md` for implementation order and hard dependencies;
7. the detailed task cards referenced by the selected Master Task and mapped in `docs/TASK_CATALOG_INDEX.md`;
8. existing implementation conventions.

A material conflict must be corrected in documentation before implementation. Do not choose whichever file is newest, shortest, or easiest.

## 3. Canonical Task Workflow

`TASKS.md` is the only execution-order authority.

- Start with Master Task 1 (`M001`).
- Select one Master Task whose hard dependencies are `[x] VERIFIED`.
- Open `docs/TASK_CATALOG_INDEX.md` and select the exact mandatory and applicable conditional detailed cards.
- Treat deferred, superseded, and future-assessment cards according to the index.
- Do not begin a later workspace sprint because its documentation exists.
- A detailed task file provides acceptance criteria but does not override `TASKS.md` dependencies.
- Documentation creation is not implementation completion.
- Only `[x] VERIFIED` is complete.

Detailed task catalogs include:

- `UX_DESIGN_TASKS.md`;
- `CLOUD_MVP_TASKS.md`;
- `LOCAL_AND_PRODUCTION_TASKS.md`;
- `SPRINT_3_TASKS.md` through `SPRINT_21_TASKS.md`.

Read these before starting implementation:

1. `docs/IMPLEMENTATION_EXECUTION_PLAN.md`;
2. `TASKS.md`;
3. `docs/TASK_CATALOG_INDEX.md`;
4. every specification referenced by the selected Master Task and detailed cards.

## 4. Official Product Identity

- Product name: **The Daily Roast AI**
- Tagline: **Evidence-Driven Market Intelligence**
- Product domain: `thedailyroast.online`
- Application: `app.thedailyroast.online`
- API: `api.thedailyroast.online`
- Documentation: `docs.thedailyroast.online`
- Status: `status.thedailyroast.online`

`Ai-trade-bot` is a technical repository identifier only. User-facing copy must use the official product name.

## 5. Brand and Communication Rules

All user-facing output must:

- put evidence before claims;
- label simulation and paper execution explicitly;
- expose uncertainty, freshness, risk, reconciliation, limitations, and provenance;
- distinguish Gemini interpretation from deterministic strategy and risk;
- describe AI confidence as analytical confidence, never probability of profit;
- avoid guaranteed-return, urgency, fear-of-missing-out, casino, moon, rocket, or get-rich-quick language;
- avoid financial advice or personal suitability claims;
- preserve equivalent safety meaning in English and Estonian.

## 6. Active MVP Architecture

The active implementation profile uses:

- Python 3.12 modular monolith;
- FastAPI API and one-shot research-cycle CLI sharing application/domain services;
- React, TypeScript, Vite, React Router, and TanStack Query;
- Supabase PostgreSQL and Auth;
- SQLAlchemy 2 and additive Alembic/Supabase migrations;
- Binance Spot public REST and finalized candles;
- Google Gemini through the official `google-genai` SDK;
- GitHub Actions best-effort scheduling;
- Cloudflare Pages and Render Free for the first cloud demo;
- PostgreSQL advisory locks or durable leases;
- append-only double-entry ledger and mandatory reconciliation.

Deferred unless measured need, M034 change governance, ADR, migration/rollback, tests, security/privacy review, cost/capacity evidence, staged paper verification, and owner approval exist:

- Redis and ARQ;
- persistent workers;
- Binance WebSocket ingestion;
- hosted Prometheus and Grafana;
- Kubernetes;
- paid/high-availability infrastructure;
- automatic plan purchase or scaling;
- Binance test/private credentials;
- live trading.

Do not implement a deferred component merely because an old task card mentions it. Exchange credential or live-capital work additionally requires a separate future milestone outside M001–M036.

## 7. Repository Boundaries

```text
backend/         FastAPI, CLI, application/domain services, provider adapters
frontend/        React/TypeScript product and public demo
ai/              prompts, schemas, evaluations, and fixtures
supabase/        local config, migrations, RLS, functions, and seed data
infrastructure/  CI, deployment, scripts, and environment definitions
tests/           unit, property, integration, contract, E2E, security, recovery
docs/            product, architecture, domain, UX, operations, and governance
```

Domain code must not import FastAPI, SQLAlchemy ORM models, Supabase SDK types, Binance SDK types, or Gemini SDK types.

## 8. Mandatory Safety Invariants

1. Gemini never executes trades or mutates state.
2. Strategies emit intents and never create orders.
3. Every non-HOLD intent passes deterministic risk.
4. Missing or invalid risk configuration fails closed.
5. The append-only ledger is the financial source of truth.
6. Fills and accounting effects commit atomically.
7. Portfolio projections reconcile to the ledger.
8. A reconciliation mismatch halts new entry activity.
9. All financial values use decimal arithmetic and explicit currency/asset units.
10. All timestamps are timezone-aware UTC internally.
11. External side effects are idempotent or safely single-execution.
12. Network calls do not occur inside database transactions.
13. Finalized decision inputs and used configuration versions are immutable.
14. Browser roles cannot write directly to critical financial/control tables.
15. No secret appears in source, fixtures, frontend bundles, prompts, responses, logs, metrics, traces, screenshots, or artifacts.
16. A running experiment keeps its frozen behavior-set hash.
17. No automatic test score, AI output, browser control, or CI result can approve a strategy, release, or behavior activation.
18. Live trading remains disabled.

## 9. Backend Rules

- Use a modular monolith.
- FastAPI and the research-cycle CLI reuse the same application/domain services.
- Route handlers and CLI parsing contain no domain logic.
- Use Pydantic v2 project-owned request/response models.
- Use SQLAlchemy 2 transaction boundaries owned by application services.
- Use stable domain errors and safe API envelopes.
- Require idempotency keys for repeatable side-effect commands.
- Use optimistic concurrency or expected-version guards for privileged state changes.
- Persist actor, correlation ID, reason, outcome, and evidence for material commands.
- Map provider errors to project-owned types.
- Keep local/runtime filesystems disposable and non-authoritative.

## 10. Supabase and Database Rules

- Local development uses Supabase CLI/PostgreSQL/Auth without needing a cloud project.
- Cloud environments use separate projects and credentials.
- Applied migrations are immutable; create new migrations for every change.
- CI upgrades a clean database to one expected migration head.
- RLS is enabled on every Data API-visible object.
- Browser access is deny-by-default.
- Approved browser reads use documented views or APIs.
- Browser writes to ledger, fills, risk decisions, AI runs, audit events, experiments, releases, incidents, or security-control records are prohibited.
- Service-role, workflow, read-only, and migration credentials are scoped, separated, and server/workflow-only.
- A backup is not accepted until restore, migration verification, ledger rebuild, and reconciliation succeed.

## 11. Research-Cycle Rules

One logical cycle must:

1. load the frozen experiment configuration;
2. acquire a PostgreSQL lock or durable lease;
3. record intended and actual timing;
4. fetch actual eligible finalized Binance REST data;
5. validate quality, freshness, ordering, and gaps;
6. create an immutable snapshot;
7. calculate versioned deterministic features;
8. reserve/check Gemini budget and optionally request structured analysis;
9. validate grounding, schema, safety, certainty, and source validity;
10. evaluate deterministic strategy;
11. evaluate deterministic risk;
12. simulate approved paper execution;
13. atomically post order/fill/ledger/audit/outbox effects;
14. rebuild or update the portfolio projection;
15. reconcile;
16. persist complete cycle and audit evidence;
17. release or safely expire the lock.

Retries must return existing results or deterministic conflicts and must never duplicate a financial side effect. Delayed or missed schedules never create imagined trades.

## 12. Gemini Rules

- Use `google-genai` only inside the Gemini infrastructure adapter.
- Use project-owned structured schemas.
- Send only minimum required structured market evidence.
- Never send credentials, tokens, personal data, database URLs, unrelated content, or private provider payloads.
- Separate trusted instructions from untrusted evidence.
- Disable execution, shell, database, exchange, search, and code tools for the MVP analysis flow.
- Handle authentication, timeout, cancellation, 429, 5xx, refusal, safety block, empty response, malformed output, invalid schema, unsupported claims, false certainty, injection, stale source, and budget exhaustion explicitly.
- Provider success is not validation acceptance.
- Invalid or unavailable AI evidence degrades to deterministic fallback or HOLD.
- Normal CI uses deterministic fake providers.
- Model, provider, prompt, schema, safety, validation, fallback, usage, and budget behavior are versioned.

## 13. Strategy, Risk, Execution, and Accounting Rules

- Deterministic inputs and versions produce deterministic outputs and hashes.
- Shorting, leverage, margin, futures, options, custody, and withdrawals are prohibited.
- Position size and order notional are bounded by deterministic risk.
- Execution models include fees, spread, slippage, precision, minimum notional, partial fills, cancellation, time in force, and conservative event timing.
- One approved risk evaluation creates at most one paper order.
- Filled quantity never exceeds approved quantity.
- Ledger transactions balance and remain append-only.
- Corrections use reversal/replacement evidence rather than mutation.
- Reconciliation failure blocks final performance and experiment completion.

## 14. Frontend and Accessibility Rules

- TypeScript strict mode is mandatory.
- Consume project-owned generated API types where available.
- Use TanStack Query for server state.
- Use versioned design tokens and canonical components.
- Preserve environment, simulation, freshness, halt, reconciliation, incident, and critical blocker state globally.
- Never rely on color alone.
- Primary workflows support keyboard, screen readers, 200% zoom/reflow, reduced motion, and mobile layouts.
- Charts require text or tabular alternatives.
- Frontend calculations are presentation-only; authoritative financial, risk, freshness, reconciliation, permission, SLO, cost, or compatibility results come from the server.
- No secret-bearing environment variable may enter a client bundle.

## 15. Environment Rules

### Local

- no paid provider or cloud credential required;
- deterministic fakes by default;
- resettable Supabase/PostgreSQL/Auth;
- Windows 11 and one Unix-like path documented;
- synthetic fixtures only.

### CI

- ephemeral or resettable infrastructure;
- fake providers by default;
- no production data, secrets, paid Gemini, or private Binance access;
- reuse repository commands;
- verify migrations, RLS, Auth, financial invariants, builds, security, accessibility, documentation, and generated artifacts.

### Free-Cloud Demo — M028

- dedicated Supabase project;
- Cloudflare Pages, Render Free, GitHub Actions, Binance REST, and bounded Gemini;
- Render is not the scheduler;
- GitHub schedule is best effort;
- free-tier limits are not SLA claims;
- no persistent worker, Redis, ARQ, WebSocket requirement, hosted Prometheus/Grafana, or private Binance.

### Controlled Paper Experiment — M029

- exact frozen configuration and behavior-set hashes;
- current export/restore evidence;
- preflight and owner approval;
- complete cycles, incidents, halts, ledger, reconciliation, and final report;
- no fabricated missed-cycle trades;
- profit is not completion evidence.

### Staging and Production Research — M035/M036

- separate database, Auth, Gemini credentials, domains, secrets, storage, monitoring, and deployment credentials;
- production artifacts validated unchanged in staging;
- protected environments and manual approval;
- controlled migration step;
- tested backup/restore, measured SLOs, incident routing, security/privacy review, cost planning, and rollback readiness;
- paper-only and live-trading-disabled.

## 16. Testing Requirements

Use the layers required by the selected Master Task:

- unit tests;
- property tests;
- migration, constraint, RLS, Auth, transaction, and lease integration tests;
- provider contract tests using fakes/fixtures;
- API contract tests;
- frontend component, accessibility, visual, build, and E2E tests;
- idempotency, restart, concurrency, and duplicate-delivery tests;
- ledger, reconstruction, reconciliation, and halt tests;
- export, restore, rollback, resilience, and incident drills;
- security/privacy scans and secret/bundle inspection;
- documentation, task, link, OpenAPI, schema, and generated-artifact checks.

Flaky tests are defects. A quarantine requires an issue, owner, reason, and expiry.

## 17. Work Procedure

Before editing:

1. confirm the selected `Mxxx` task;
2. confirm all hard dependencies are verified;
3. use `docs/TASK_CATALOG_INDEX.md` to select detailed cards;
4. inspect relevant code, tests, migrations, schemas, and generated artifacts;
5. list invariants, failure cases, security/privacy impact, environment impact, and verification commands;
6. avoid unrelated scope.

During implementation:

- keep changes focused;
- add tests before or with behavior;
- use project-owned types at boundaries;
- preserve backward compatibility or document migration;
- update documentation and generated artifacts in the same change;
- do not weaken controls to make tests pass.

Before marking verified:

1. satisfy every mandatory and applicable conditional acceptance criterion;
2. run and record relevant commands;
3. verify financial precision, idempotency, RLS, Auth, redaction, risk, ledger, reconciliation, and environment separation;
4. update `TASKS.md` status/evidence;
5. update affected specifications, API/schema/database docs, runbooks, changelog, and release evidence;
6. inspect the final diff and commit;
7. fetch the commit or pull request and verify intended files and test evidence;
8. record limitations and follow-up IDs.

## 18. Prohibited Without a Separate Approved Milestone

- live or private exchange execution;
- Binance test-environment activation;
- leverage, margin, derivatives, options, shorting, custody, or withdrawals;
- weakening RLS, Auth, risk, ledger, reconciliation, backup, recovery, or release gates;
- reusing the Eventnexus Supabase project;
- enabling paid usage automatically;
- adding mandatory Redis/ARQ/WebSocket/hosted metrics without measured need, M034 governance, and ADR;
- exposing service-role, database, Gemini, signing, or exchange secrets;
- allowing Gemini side-effect tools;
- editing applied migrations;
- bypassing staging for production research;
- automatic release, strategy, prompt, model, or configuration activation;
- representing demo or paper performance as live-readiness or profit proof;
- changing official product identity or using hype/guarantee language without approved brand governance.
