# AGENTS.md

## Purpose

This is the authoritative implementation guide for AI coding agents and human contributors.

The project is a cloud-hosted cryptocurrency research, backtesting, paper-trading, and Gemini-assisted decision-support platform. The MVP never executes live trades.

## Instruction Precedence

1. Security, financial integrity, and fail-closed requirements
2. This file
3. `docs/PRODUCT_REQUIREMENTS.md`
4. `docs/ARCHITECTURE.md`, `docs/FREE_CLOUD_ARCHITECTURE.md`, and accepted ADRs
5. Domain specifications
6. `CLOUD_MVP_TASKS.md` for free-cloud deployment work
7. `TASKS.md` for shared domain work

Material conflicts must be corrected in documentation before implementation.

## Mandatory Rules

1. Select one focused task and read all references.
2. Do not implement live trading, private Binance execution, leverage, margin, futures, shorting, withdrawals, or custody.
3. Gemini is advisory and cannot bypass deterministic strategy, risk, execution, accounting, or reconciliation.
4. Risk and integrity failures fail closed.
5. Use `Decimal` for all financial values.
6. Use timezone-aware UTC timestamps.
7. External side effects are idempotent.
8. Every decision and scheduled cycle is reproducible and auditable.
9. Never commit or expose secrets.
10. Never weaken tests, RLS, authorization, typing, validation, risk, or accounting controls to make CI pass.
11. Do not claim profitability or production availability.

## Active Free-Cloud Profile

The first experiment uses:

- Cloudflare Pages for the frontend;
- Render Free for FastAPI;
- a dedicated Supabase Free project for PostgreSQL and Auth;
- GitHub Actions for approximately hourly scheduling;
- Binance Spot REST for finalized candles;
- Google Gemini API with EUR 0 monthly cost budget by default.

The existing Eventnexus Supabase project must not be reused.

Redis, ARQ, persistent WebSocket ingestion, hosted Prometheus/Grafana, Kubernetes, and private Binance APIs are deferred. Do not implement them as an MVP dependency unless a new accepted ADR explicitly supersedes the free-cloud profile.

## Repository Boundaries

```text
backend/         FastAPI, one-shot CLI, domains, persistence, provider adapters
frontend/        React and TypeScript interface
ai/              prompts, schemas, evaluations, fixtures
supabase/        config, migrations, RLS, database functions
infrastructure/  CI, deployment, optional local tooling
 tests/          unit, integration, contract, property, and E2E tests
 docs/           specifications and runbooks
```

## Backend Rules

- Use a modular monolith.
- FastAPI and the research-cycle CLI reuse application/domain services.
- Domain code does not import FastAPI, SQLAlchemy ORM models, Supabase SDK types, Binance types, or Gemini SDK types.
- The CLI must run without Redis, ARQ, WebSocket, Render availability, or persistent local disk.
- Use PostgreSQL advisory locks or leases to prevent overlapping research cycles.
- Do not perform network calls inside database transactions.
- Fill, order transition, ledger posting, and audit/outbox state commit atomically.

## Supabase and Database Rules

- Supabase-managed PostgreSQL is authoritative.
- Supabase Auth supplies identity; FastAPI enforces application roles.
- Enable RLS on every Data API-visible table or view.
- Browser access is deny-by-default.
- Browser writes to ledger, fills, risk decisions, AI runs, audit events, and experiment-control tables are prohibited.
- Frontend may receive only the Supabase URL and publishable key.
- Service-role key, direct database credentials, Gemini key, and future Binance secrets remain server/workflow-only.
- Migrations are version-controlled and additive. Never edit an applied migration.
- Local filesystems are disposable and never authoritative.

## Research-Cycle Rules

The scheduled one-shot cycle must:

1. acquire a database lock/lease;
2. fetch and validate finalized Binance REST data;
3. repair gaps;
4. create immutable snapshot and features;
5. invoke Gemini only within budget;
6. validate AI output;
7. evaluate strategy and risk;
8. simulate approved paper actions;
9. atomically post ledger state;
10. reconcile;
11. persist cycle and audit results;
12. release the lease.

Retries must never duplicate financial side effects. GitHub Actions schedule delay is expected; decisions use actual finalized market data, not the intended cron timestamp.

## Gemini Rules

- Use the official `google-genai` SDK behind `LLMProvider`.
- Use project-owned structured schemas.
- Handle authentication, 429, 5xx, timeout, safety block, refusal, empty output, and invalid schema explicitly.
- Normal CI uses a fake provider.
- No function calling, search grounding, code execution, database mutation, or order tools in MVP.
- Gemini quota exhaustion degrades to deterministic fallback or HOLD.

## Market Data Rules

- MVP uses Binance Spot public REST.
- Only finalized candles are decision inputs.
- Persist symbol filters and exact decimal constraints.
- Validate chronology, duplicates, gaps, OHLC relationships, volume, freshness, and server clock drift.
- WebSocket ingestion is deferred.

## Strategy, Risk, and Accounting Rules

- Strategies emit intents; they do not place orders or decide final size.
- Every actionable intent passes deterministic risk.
- The append-only double-entry ledger is the financial source of truth.
- Projections must reconcile with the ledger.
- Reconciliation mismatch halts the experiment.
- Paper execution includes fees, spread, slippage, precision, minimum notional, partial fills, and conservative ambiguity handling.

## Frontend Rules

- TypeScript strict mode.
- Server state uses TanStack Query.
- Simulation, stale data, cold start, paused, and halted states must be unmistakable.
- Never present AI confidence as probability of profit.
- Built assets must contain no server secret.
- React Router fallback, CSP, CORS, HTTPS, and accessibility are tested.

## Testing Requirements

- unit tests for calculations and state machines;
- PostgreSQL/migration integration tests;
- Supabase JWT and RLS tests;
- Binance/Gemini contract tests using fakes or recorded public fixtures;
- property tests for ledger, precision, risk, and idempotency;
- E2E tests for one-shot cycle, paper execution, auth, halt, and reconciliation;
- duplicate workflow, restart, cold-start, quota, stale-data, and restore drills.

Normal CI must not use production Supabase, paid Gemini, or private Binance credentials.

## Free-Tier Operational Rules

Free services may sleep, pause, restart, throttle, delay work, or change quota. Code must not assume exact scheduling or guaranteed availability.

- Render cold start must not affect scheduled research.
- Supabase unavailability produces safe failure.
- Missing scheduled cycles are recorded, never fabricated.
- Database exports and restore tests are mandatory before the formal experiment.
- Hosted Prometheus/Grafana are not required and must not be falsely marked complete.

## Task Workflow

Before coding:

1. select a task from `TASKS.md` or `CLOUD_MVP_TASKS.md`;
2. verify dependencies;
3. read all references;
4. define failure cases and evidence.

Before completion:

1. run format, lint, type, tests, migrations, builds, and security scans;
2. verify no secret in source, logs, artifacts, or frontend bundle;
3. verify idempotency, monetary precision, RLS, risk, and reconciliation;
4. update docs and changelog;
5. satisfy every acceptance criterion and Definition of Done item.

## Prohibited Without Explicit Owner Approval

- live or private exchange execution;
- weakening RLS, risk limits, halts, or ledger design;
- reusing the Eventnexus database;
- enabling paid usage automatically;
- introducing Redis/ARQ/WebSocket as mandatory MVP infrastructure;
- exposing service-role or provider secrets;
- allowing Gemini side-effect tools;
- editing applied migrations;
- disabling security or test gates.
