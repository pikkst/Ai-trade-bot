# Backend

Last reviewed: 2026-07-31
Status: Authoritative backend implementation specification

## 1. Purpose

The backend provides the HTTP API, application use cases, background jobs, persistence, Binance public market-data adapters, Google Gemini integration, deterministic strategy and risk engines, paper execution, portfolio accounting, backtesting, audit, and operational interfaces.

The MVP backend is a Python 3.12 modular monolith. The architecture must preserve domain boundaries and make external providers replaceable without leaking SDK-specific objects into business logic.

## 2. Package Structure

```text
backend/
├── pyproject.toml
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── dependencies/
│   │   ├── middleware/
│   │   ├── schemas/
│   │   └── v1/
│   ├── core/
│   │   ├── config.py
│   │   ├── errors.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   ├── clock.py
│   │   └── ids.py
│   ├── domains/
│   │   ├── identity/
│   │   ├── configuration/
│   │   ├── market_data/
│   │   ├── features/
│   │   ├── ai_analysis/
│   │   ├── strategy/
│   │   ├── risk/
│   │   ├── execution/
│   │   ├── portfolio/
│   │   ├── backtesting/
│   │   ├── audit/
│   │   └── reporting/
│   ├── infrastructure/
│   │   ├── persistence/
│   │   ├── queue/
│   │   ├── exchange/binance/
│   │   ├── ai/gemini/
│   │   └── observability/
│   └── workers/
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    └── e2e/
```

## 3. Layering

### 3.1 Domain Layer

Contains entities, value objects, domain services, policies, state machines, and project-owned protocols. It must not import FastAPI, SQLAlchemy ORM, Redis, Binance SDKs, Gemini SDKs, or HTTP clients.

### 3.2 Application Layer

Coordinates use cases, permissions, idempotency, transaction boundaries, repositories, domain services, and event publication. Application handlers receive typed commands or queries and return project-owned result models.

### 3.3 Infrastructure Layer

Implements persistence repositories, Redis/ARQ queues, Binance clients, Gemini clients, clocks, ID generators, and metrics exporters.

### 3.4 API Layer

Maps HTTP requests to application commands and queries. Route handlers must remain thin: authenticate, authorize, validate, invoke, and map the result.

## 4. Domain Module Template

Each substantial domain should use a consistent internal structure:

```text
domain_name/
├── entities.py
├── value_objects.py
├── enums.py
├── commands.py
├── queries.py
├── services.py
├── policies.py
├── protocols.py
├── events.py
├── exceptions.py
└── handlers.py
```

Files should only be added when useful; empty ceremonial modules are discouraged.

## 5. Type and Value Rules

- All production functions and methods require complete type annotations.
- MyPy strict mode applies to application packages.
- `Any` is isolated at third-party boundaries and converted immediately.
- Monetary amounts, prices, quantities, fees, and P&L use `Decimal`.
- Currency and asset symbols are explicit value objects or validated strings.
- Timestamps are timezone-aware UTC.
- Durations use `timedelta` or explicitly named integer units.
- Finite states use enums or literal types.
- IDs use UUID unless a documented external identifier is required.
- Domain objects must not silently coerce invalid values.

## 6. Configuration

Use Pydantic Settings with nested, typed configuration groups:

- application;
- HTTP server;
- PostgreSQL;
- Redis and ARQ;
- Binance public data;
- Google Gemini;
- AI budgets;
- strategy;
- risk;
- paper execution;
- authentication;
- observability;
- feature flags.

Startup validation must reject:

- missing mandatory settings;
- malformed database or Redis URLs;
- unsafe production defaults;
- negative budgets or limits;
- unsupported model configuration;
- live-trading activation in MVP;
- incompatible risk settings;
- missing JWT secret outside test mode.

Secrets must use secret-aware types and redacted representations.

## 7. Dependency Injection

Use explicit dependency injection through constructors and FastAPI dependency factories. Required protocols include:

- `Clock`;
- `IdGenerator`;
- `UnitOfWork`;
- repositories per domain;
- `ExchangeMarketDataProvider`;
- `LLMProvider`;
- `JobQueue`;
- `EventPublisher`;
- `MetricsRecorder`.

Domain and application tests must substitute deterministic fakes without monkey-patching global SDK clients.

## 8. Commands, Queries, and Transactions

Commands mutate state; queries read state.

Rules:

- every command has an actor and correlation ID;
- commands that may repeat have an idempotency key;
- transaction boundaries belong to application command handlers;
- network calls never occur inside database transactions;
- immutable external results are fetched before the transaction and persisted inside a short transaction;
- reliable post-commit work uses a transactional outbox where necessary;
- query handlers do not mutate domain state.

## 9. Persistence

Use SQLAlchemy 2 with explicit mappings and repository implementations.

- ORM models are infrastructure objects, not domain entities.
- API schemas are not ORM models.
- migrations are additive and immutable after application.
- repositories expose domain-oriented operations rather than generic CRUD.
- list queries require pagination and deterministic ordering.
- N+1 query behavior must be tested for common read paths.
- database constraints enforce invariants where practical.

## 10. Redis and ARQ

Redis is used for queues, locks, short-lived cache, and ephemeral coordination. It is not the source of truth for financial or decision state.

ARQ job requirements:

- typed payload schema;
- deterministic job ID;
- maximum retry count;
- exponential backoff with jitter where appropriate;
- explicit timeout;
- structured start, success, retry, and terminal-failure logs;
- metrics for duration and outcome;
- idempotent handler behavior;
- no paid Gemini calls in normal CI.

## 11. Google Gemini Adapter

The Gemini implementation lives under `infrastructure/ai/gemini/` and uses the official Google Gen AI SDK.

It must:

- implement the project-owned `LLMProvider` protocol;
- accept project-owned typed requests;
- configure model, timeout, retry, temperature, and output limit from settings;
- request structured output where supported;
- map provider results into project-owned raw response, usage, status, and error types;
- distinguish authentication failure, quota/rate limit, timeout, server failure, safety block, refusal, empty response, and invalid schema;
- expose no SDK object outside the adapter;
- never receive execution tools or secrets.

Active rate limits must be treated as configuration observed from Google AI Studio rather than hardcoded assumptions. Retry behavior must be bounded and must not bypass daily or monthly budgets.

## 12. Binance Adapter

The Binance adapter is responsible for:

- server time;
- exchange information and symbol filters;
- historical finalized candles;
- current ticker where required;
- public WebSocket streams;
- rate-limit metadata and errors;
- reconnect and gap-repair support.

The adapter returns normalized project-owned models while retaining exchange-native identifiers and raw metadata needed for audit.

## 13. Error Model

All expected failures map to typed application errors with stable codes.

Minimum error codes:

- `validation_error`;
- `authentication_error`;
- `authorization_error`;
- `not_found`;
- `conflict`;
- `idempotency_conflict`;
- `stale_data`;
- `data_quality_failed`;
- `provider_authentication_failed`;
- `provider_rate_limited`;
- `provider_unavailable`;
- `provider_timeout`;
- `ai_safety_blocked`;
- `ai_output_invalid`;
- `budget_exhausted`;
- `strategy_rejected`;
- `risk_rejected`;
- `trading_halted`;
- `reconciliation_failed`;
- `internal_error`.

Unexpected exceptions are logged with correlation ID and mapped to a generic response. Stack traces, secrets, SQL, and provider payloads must not be returned to clients.

## 14. Logging

Use structured JSON logs.

Standard fields:

- timestamp;
- level;
- service;
- environment;
- event;
- correlation ID;
- request ID;
- actor ID where safe;
- workspace ID;
- job ID;
- entity type and ID;
- outcome;
- duration;
- stable error code.

Authorization headers, cookies, API keys, JWTs, signatures, database URLs, and raw sensitive payloads must be redacted.

## 15. Authentication and Authorization

- Authentication is server-side.
- Passwords use Argon2id when local password authentication is implemented.
- Access tokens are short-lived.
- Refresh-token storage and rotation must be explicitly designed before implementation.
- Roles are owner, operator, and viewer.
- Application handlers enforce permissions; UI visibility is not authorization.
- Audit events record privileged actions.

## 16. API Conventions

- Base path: `/api/v1`.
- JSON request and response bodies.
- RFC 3339 UTC timestamps.
- Decimal financial values serialized as strings.
- Cursor pagination preferred for large time-ordered collections.
- State-changing commands use `Idempotency-Key` where duplication is possible.
- Error responses include stable code, message, correlation ID, and optional safe details.
- OpenAPI output is generated and checked into CI validation.

## 17. Background Workflows

Required workflows include:

- symbol metadata refresh;
- candle backfill;
- WebSocket gap repair;
- snapshot creation;
- feature calculation;
- Gemini analysis;
- strategy evaluation;
- risk evaluation;
- paper-order evaluation and fills;
- reconciliation;
- backtest execution;
- experiment report generation;
- retention cleanup.

Every workflow must define retries, timeout, idempotency, terminal failure, metrics, and alert behavior.

## 18. Testing Requirements

- unit tests for pure calculations and state machines;
- integration tests with real PostgreSQL and Redis containers;
- migration upgrade tests from an empty database;
- contract tests for Binance and Gemini adapters using recorded or fake responses;
- property-based tests for decimal arithmetic, risk invariants, and ledger balance;
- end-to-end tests for analysis-to-paper-fill and halt flows;
- failure tests for duplicate, restart, stale data, provider errors, and reconciliation mismatch.

## 19. Quality Gates

A backend change is not complete until:

- Ruff formatting and linting pass;
- MyPy strict passes;
- Pytest passes;
- migration validation passes;
- Bandit and Semgrep pass according to policy;
- no secret is detected;
- documentation is current;
- public behavior has tests;
- no risk, ledger, or AI safety invariant is weakened.

## 20. Prohibited Patterns

- business logic in route handlers;
- ORM objects returned directly from API routes;
- generic repository abstractions that hide required domain semantics;
- binary floating-point for financial values;
- naive datetimes;
- network calls inside transactions;
- mutable ledger rows;
- broad exception swallowing;
- unbounded retries;
- hardcoded Gemini model or credentials;
- Gemini function tools with side effects;
- direct strategy-to-order calls;
- bypass flags for risk or reconciliation;
- editing an applied migration.

## 21. Related Documents

- `/AGENTS.md`
- `PRODUCT_REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `API_SPECIFICATION.md`
- `DATABASE_SCHEMA.md`
- `GEMINI_INTEGRATION.md`
- `SECURITY.md`
- `TESTING.md`
- `OBSERVABILITY.md`
