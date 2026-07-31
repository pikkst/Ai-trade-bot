# AGENTS.md

## Purpose

This is the authoritative implementation guide for AI coding agents and human contributors.

The project is a cloud-hosted cryptocurrency research, backtesting, paper-trading, and Gemini-assisted decision-support platform. The MVP and production research service never execute live trades.

## Instruction Precedence

1. Security, financial integrity, privacy, and fail-closed requirements
2. This file
3. `docs/PRODUCT_REQUIREMENTS.md`
4. `docs/ARCHITECTURE.md`, environment architecture documents, and accepted ADRs
5. Domain specifications
6. The selected detailed task file
7. Existing implementation conventions

Material conflicts must be corrected in documentation before implementation.

## Task Sources

- `TASKS.md` — shared domain implementation
- `CLOUD_MVP_TASKS.md` — free cloud demo and experiment deployment
- `LOCAL_AND_PRODUCTION_TASKS.md` — local development, test automation, staging, production research, and post-launch work

Select one focused task from the correct task source and read all references before editing code.

## Mandatory Rules

1. Do not implement live trading, private Binance execution, leverage, margin, futures, shorting, withdrawals, or custody.
2. Gemini is advisory and cannot bypass deterministic strategy, risk, execution, accounting, or reconciliation.
3. Risk and integrity failures fail closed.
4. Use `Decimal` for all financial values.
5. Use timezone-aware UTC timestamps.
6. External side effects, scheduled cycles, migrations, and financial commands must be idempotent or safely single-execution.
7. Every decision and scheduled cycle must be reproducible and auditable.
8. Never commit or expose secrets, production data, personal data, or provider credentials.
9. Never weaken tests, RLS, authorization, typing, validation, risk, accounting, backup, or recovery controls to make CI pass.
10. Do not claim profitability, production availability, or recovery capability without measured evidence.
11. Do not treat a free-tier service as a guaranteed production dependency.
12. Do not copy production data into local or test environments without an approved anonymization process.

## Environment Rules

### Local

- Use Supabase CLI/local PostgreSQL and Auth.
- Use fake Binance and Gemini providers by default.
- Do not require paid credentials for normal development or tests.
- Support Windows 11 and a Unix-like environment where practical.
- Use deterministic seed data and isolated test data.

### CI

- Use ephemeral or resettable test infrastructure.
- Never access production Supabase, paid Gemini, or private Binance credentials in ordinary pull requests.
- Reuse repository commands rather than duplicating hidden CI-only behavior.
- Verify migrations, RLS, Auth, financial invariants, frontend bundle safety, and documentation consistency.

### Free Cloud Demo and Paper Experiment

- Use Cloudflare Pages, Render Free, dedicated Supabase Free, GitHub Actions, Binance Spot REST, and bounded Gemini usage.
- The existing Eventnexus Supabase project must not be reused.
- Redis, ARQ, persistent WebSocket, hosted Prometheus/Grafana, and private Binance APIs are deferred.
- Render cold start must not stop the scheduled research cycle.
- GitHub Actions schedule delay is expected and must never cause fabricated trades.

### Staging and Production Research

- Use separate database, Auth, Gemini credentials, domains, secrets, and deployment environments.
- Production artifacts must be validated in staging.
- Production deployment requires protected environments and manual approval.
- Migrations run once through a controlled step.
- Backup and restore evidence, measured SLOs, incident routing, security review, and privacy review are required.
- A production research service still uses simulated trading only.

## Repository Boundaries

```text
backend/         FastAPI, one-shot CLI, domains, persistence, provider adapters
frontend/        React and TypeScript interface
ai/              prompts, schemas, evaluations, fixtures
supabase/        config, migrations, RLS, database functions, seed data
infrastructure/  CI, deployment, local tooling, environment definitions
tests/           unit, property, integration, contract, E2E, recovery tests
docs/            specifications and runbooks
```

## Backend Rules

- Use a modular monolith.
- FastAPI and the research-cycle CLI reuse application/domain services.
- Domain code does not import FastAPI, SQLAlchemy ORM models, Supabase SDK types, Binance types, or Gemini SDK types.
- The CLI runs without Redis, ARQ, WebSocket, Render availability, or persistent local disk in the active MVP profile.
- Use PostgreSQL advisory locks or durable leases to prevent overlapping research cycles.
- Do not perform network calls inside database transactions.
- Fill, order transition, ledger posting, and audit/outbox state commit atomically.
- Production architecture changes require an ADR and migration plan.

## Supabase and Database Rules

- Supabase-managed PostgreSQL is authoritative for the cloud MVP.
- Supabase Auth supplies identity; FastAPI enforces application roles.
- Enable RLS on every Data API-visible table or view.
- Browser access is deny-by-default.
- Browser writes to ledger, fills, risk decisions, AI runs, audit events, and experiment-control tables are prohibited.
- Frontend may receive only public URL and publishable-key values.
- Service-role key, direct database credentials, Gemini key, and future Binance secrets remain server/workflow-only.
- Migrations are version-controlled and additive. Never edit an applied migration.
- Local and cloud filesystems are disposable and never authoritative.
- Backup is not accepted until restore and ledger reconciliation succeed.

## Research-Cycle Rules

The one-shot cycle must acquire a database lock/lease, fetch and validate finalized Binance REST data, repair gaps, create immutable snapshot/features, invoke Gemini within budget, validate output, evaluate strategy/risk, simulate approved paper actions, atomically post ledger state, reconcile, persist results, and release the lease.

Retries must never duplicate financial side effects. Decisions use actual finalized market data, not the intended cron timestamp.

## Gemini Rules

- Use the official `google-genai` SDK behind `LLMProvider`.
- Use project-owned structured schemas.
- Handle authentication, 429, 5xx, timeout, safety block, refusal, empty output, and invalid schema explicitly.
- Normal CI uses a fake provider.
- No function calling, search grounding, code execution, database mutation, or order tools.
- Gemini quota exhaustion degrades to deterministic fallback or HOLD.
- Production model, prompt, schema, safety settings, usage, and costs are versioned and monitored.

## Strategy, Risk, and Accounting Rules

- Strategies emit intents; they do not place orders or decide final size.
- Every actionable intent passes deterministic risk.
- The append-only double-entry ledger is the financial source of truth.
- Projections must reconcile with the ledger.
- Reconciliation mismatch halts the experiment or production research workspace.
- Paper execution includes fees, spread, slippage, precision, minimum notional, partial fills, and conservative ambiguity handling.

## Frontend Rules

- TypeScript strict mode.
- Server state uses TanStack Query.
- Local, demo, paper, staging, production research, stale, cold-start, paused, and halted states must be unmistakable.
- Never present AI confidence as probability of profit.
- Built assets must contain no server secret.
- React Router fallback, CSP, CORS, HTTPS, accessibility, and environment-variable allowlists are tested.

## Testing Requirements

- unit and property tests for calculations, state machines, ledger, precision, risk, and idempotency;
- local Supabase migration, constraint, Auth, and RLS tests;
- Binance/Gemini contract tests using fakes or controlled fixtures;
- frontend component, accessibility, build, and E2E tests;
- one-shot cycle, paper execution, halt, reconciliation, export, and restore drills;
- duplicate workflow, scheduling delay, cold-start, quota, stale-data, database outage, and recovery tests;
- staging validation before production research promotion.

See `docs/LOCAL_DEVELOPMENT.md`, `docs/TEST_ENVIRONMENTS.md`, and `docs/PRODUCTION_DEVELOPMENT.md`.

## Task Workflow

Before coding:

1. select one task;
2. verify dependencies;
3. read all references;
4. inspect existing code, migrations, tests, and generated artifacts;
5. define failure cases and evidence.

Before completion:

1. run format, lint, type, tests, migrations, builds, security scans, and applicable recovery checks;
2. verify no secret or production data in source, logs, artifacts, fixtures, or frontend bundle;
3. verify idempotency, monetary precision, RLS, risk, reconciliation, and environment separation;
4. update docs and changelog;
5. satisfy every acceptance criterion and Definition of Done item.

## Prohibited Without Explicit Owner Approval

- live or private exchange execution;
- weakening RLS, risk limits, halts, ledger, backup, or recovery design;
- reusing the Eventnexus database;
- enabling paid usage automatically;
- introducing Redis/ARQ/WebSocket as mandatory MVP infrastructure;
- exposing service-role or provider secrets;
- allowing Gemini side-effect tools;
- editing applied migrations;
- bypassing staging for production research releases;
- disabling security or test gates;
- representing demo success as live-trading approval.
