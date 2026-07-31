# Backend

Last reviewed: 2026-07-31
Status: Authoritative backend specification for the free-cloud MVP

## Purpose

The Python 3.12 modular monolith provides FastAPI HTTP APIs and a one-shot research-cycle CLI. Both entry points reuse the same application and domain services.

## Package Structure

```text
backend/app/
├── main.py
├── api/
├── cli/
│   └── run_research_cycle.py
├── core/
├── domains/
│   ├── identity/
│   ├── configuration/
│   ├── market_data/
│   ├── features/
│   ├── ai_analysis/
│   ├── strategy/
│   ├── risk/
│   ├── execution/
│   ├── portfolio/
│   ├── backtesting/
│   ├── audit/
│   └── reporting/
└── infrastructure/
    ├── persistence/supabase_postgres/
    ├── auth/supabase/
    ├── exchange/binance/
    ├── ai/gemini/
    └── observability/
```

Domain code does not import FastAPI, SQLAlchemy ORM models, Supabase SDK types, Binance provider types, or Gemini SDK types.

## Runtime Entry Points

### FastAPI

Runs on Render and provides authenticated reads plus explicit commands. It does not run the hourly scheduler or a persistent worker.

### Research-Cycle CLI

Runs from GitHub Actions. It acquires a PostgreSQL lock/lease and executes one complete idempotent cycle. The CLI must operate without Redis, ARQ, WebSocket, Render availability, or persistent local storage.

## Configuration

Typed Pydantic settings cover application, Supabase/PostgreSQL, Auth, Binance REST, Gemini, strategy, risk, paper execution, external scheduling, CORS, and observability.

`REDIS_ENABLED`, `ARQ_ENABLED`, `WEBSOCKET_INGESTION_ENABLED`, `LIVE_TRADING_ENABLED`, and `PRIVATE_BINANCE_API_ENABLED` default to false.

## Persistence and Auth

- Supabase-managed PostgreSQL is authoritative.
- SQLAlchemy 2 and Alembic manage application persistence.
- Supabase Auth supplies identity.
- FastAPI validates identity and applies owner/operator/viewer authorization.
- RLS provides a second deny-by-default database boundary.
- Browser writes to financial tables are prohibited.

## Commands and Transactions

- commands carry actor, correlation ID, and idempotency key;
- network calls occur outside database transactions;
- fill, order transition, ledger entries, and audit/outbox state commit atomically;
- retries never duplicate a financial side effect;
- PostgreSQL advisory locks or leases coordinate scheduled cycles.

## Binance Adapter

The MVP adapter uses public REST for server time, exchange metadata, finalized candles, and gap repair. WebSocket behavior is not required for the first experiment.

## Gemini Adapter

The official `google-genai` SDK is isolated behind `LLMProvider`. The adapter maps timeout, authentication, rate-limit, safety-block, refusal, empty response, provider failure, and invalid-schema outcomes to project-owned types.

No Gemini tool may mutate state or execute orders.

## Error Model

Stable codes include validation, authentication, authorization, conflict, idempotency conflict, stale data, data quality failure, provider failures, AI safety/output failures, budget exhaustion, strategy/risk rejection, trading halt, reconciliation failure, and internal error.

## Logging

Use structured JSON logs with correlation ID, environment, cycle ID, request ID, entity identifiers, duration, outcome, and stable error code. Redact credentials, tokens, signatures, database URLs, and prompt bodies.

## Testing

- pure domain unit tests;
- PostgreSQL and migration integration tests;
- Supabase JWT/RLS authorization tests;
- fake and recorded Binance/Gemini contract tests;
- property tests for ledger, precision, risk, and idempotency;
- end-to-end one-shot cycle tests;
- duplicate workflow, restart, stale data, quota, and reconciliation failure tests.

Normal CI must not require production Supabase, paid Gemini, or private Binance access.

## Deferred Backend Infrastructure

Redis, ARQ, persistent worker processes, and WebSocket consumers are deferred. They require measured need and an accepted ADR. Domain services and job commands must remain reusable if they are introduced later.

## Prohibited Patterns

- business logic in routes or CLI argument parsing;
- direct browser writes to ledger/fill/risk/audit tables;
- local filesystem as authoritative state;
- binary float for money;
- network calls inside transactions;
- mutable ledger rows;
- unbounded retries;
- strategy-to-order bypass;
- risk/reconciliation bypass flags;
- editing an applied migration.

## Related Documents

- `ARCHITECTURE.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `DATABASE_SCHEMA.md`
- `SECURITY.md`
- `../CLOUD_MVP_TASKS.md`
