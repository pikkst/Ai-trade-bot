# Backend

Last reviewed: 2026-08-01  
Status: Authoritative backend contract mapped to `M001–M036`

## 1. Purpose

The Python 3.12 modular monolith provides:

- a stateless FastAPI read/command API;
- an idempotent one-shot research-cycle CLI;
- reusable application/domain services;
- project-owned provider and persistence boundaries;
- append-only financial and audit evidence;
- deterministic paper-research behavior.

The backend does not authorize private Binance access, Binance test orders, live trading, leverage, margin, derivatives, shorting, custody, or withdrawals.

## 2. Master-Task Mapping

| Backend area | Master Tasks |
|---|---|
| scaffold, toolchains, database/Auth, core infrastructure, fakes | M001–M006 |
| market, features, AI, strategy/risk, execution/accounting, cycle, backtest | M007–M013 |
| API and read/command models | M014 |
| experiment, governance, product, and developer aggregates | M016–M025 |
| integrated verification/recovery | M026–M027 |
| cloud cycle and experiment operation | M028–M029 |
| operations/data/research/incident/change domains | M030–M034 |
| staging and production research | M035–M036 |

## 3. Package Structure

```text
backend/app/
├── main.py
├── api/
│   ├── dependencies/
│   ├── middleware/
│   ├── routes/
│   └── schemas/
├── cli/
│   └── run_research_cycle.py
├── core/
│   ├── settings/
│   ├── errors/
│   ├── logging/
│   ├── security/
│   ├── time/
│   └── ids/
├── application/
│   ├── commands/
│   ├── queries/
│   ├── transactions/
│   ├── authorization/
│   ├── idempotency/
│   └── outbox/
├── domains/
│   ├── identity/
│   ├── workspaces/
│   ├── configuration/
│   ├── market_data/
│   ├── features/
│   ├── ai_analysis/
│   ├── strategy/
│   ├── risk/
│   ├── execution/
│   ├── portfolio/
│   ├── backtesting/
│   ├── experiments/
│   ├── research_cycles/
│   ├── data_governance/
│   ├── research_review/
│   ├── incidents/
│   ├── changes/
│   ├── releases/
│   ├── audit/
│   └── reporting/
└── infrastructure/
    ├── persistence/postgres/
    ├── auth/supabase/
    ├── exchange/binance/
    ├── ai/gemini/
    ├── scheduling/external/
    ├── exports/
    └── observability/
```

Domain code does not import FastAPI, SQLAlchemy ORM models, Supabase SDK types, Binance provider/SDK types, Gemini SDK types, or frontend contracts.

## 4. Runtime Entry Points

### FastAPI

FastAPI runs on Render or the selected environment and provides:

- authenticated, authorized reads;
- explicit project-owned commands;
- stable `/api/v1` contracts;
- liveness and readiness;
- safe errors and correlation IDs.

It does not:

- own the hourly schedule;
- start a persistent worker;
- store authoritative local files;
- bypass application authorization or RLS;
- expose arbitrary SQL, prompts, environment editing, or provider tools.

### Research-Cycle CLI

The CLI runs locally, in CI, and through GitHub Actions. It must operate without Redis, ARQ, WebSocket ingestion, Render availability, or persistent local storage.

A logical cycle is complete only after required market, feature, optional AI/fallback, strategy, risk, execution, accounting, projection, reconciliation, audit, and cycle-closure stages have persisted successfully.

A zero process exit code alone is not financial completion.

## 5. Configuration

Typed Pydantic settings cover:

- application identity, environment, URLs, logging, and correlation;
- PostgreSQL/Supabase/Auth connectivity;
- Binance public REST transport;
- Gemini transport and budget bootstrap;
- external scheduling and cycle timeout;
- CORS/CSP/public-origin allowlists;
- feature flags and explicitly prohibited capabilities;
- operational export, retention, and observability adapters.

Environment variables provide deployment wiring and safe bootstrap defaults. Immutable workspace/experiment behavior belongs in versioned database configuration and behavior sets.

A running experiment never changes because an environment default changes.

Startup must reject unsafe combinations, including any attempt to enable live/private execution within M001–M036.

## 6. Authentication and Authorization

- Supabase Auth establishes identity.
- The backend verifies issuer, audience, signature/JWKS, expiry, and required claims.
- Application handlers enforce owner/operator/viewer, workspace scope, resource scope, recent authentication, expected version, and command permission.
- RLS is a second deny-by-default database boundary.
- Browser visibility never substitutes for server authorization.
- Denied privileged attempts create safe audit evidence.
- Application, workflow/service, read-only, and migration identities remain separated.

The active profile does not use an unrelated custom password or JWT-signing subsystem.

## 7. Persistence and Migrations

- PostgreSQL is authoritative.
- SQLAlchemy 2 implements repositories and transaction boundaries.
- Alembic/Supabase migrations are additive and immutable after application.
- CI verifies empty-database upgrade, one expected head, drift, constraints, indexes, and RLS.
- local/cloud filesystems are disposable.
- authoritative generated reports or exports use approved PostgreSQL, storage, or artifact locations.
- backup claims require tested isolated restore, migration verification, ledger rebuild, and reconciliation.

## 8. Application Commands

Every material command carries or resolves:

- authenticated actor and effective permission;
- workspace/resource scope;
- correlation/request ID;
- idempotency key where repetition could duplicate effects;
- expected aggregate/version where concurrent mutation matters;
- canonical reason code;
- recent-authentication evidence where required;
- immutable audit result.

Duplicate commands return the prior canonical result or a deterministic conflict.

## 9. Transactions and External Calls

- network/provider calls occur outside financial database transactions;
- provider responses are validated before authoritative use;
- order transition, fill, reservations, ledger entries, state version, audit, and outbox effects commit atomically;
- a partial financial write rolls back;
- post-commit publication uses outbox semantics where reliability matters;
- retries are outcome-aware and bounded;
- dead-letter behavior, when required by a future queue, must preserve authoritative state and evidence.

## 10. Locks, Leases, and Idempotency

The one-shot cycle uses a PostgreSQL advisory lock or durable lease.

Required behavior:

- stable lock/occurrence key;
- one eligible owner;
- bounded acquisition/expiry;
- explicit acquired/rejected/expired/released state;
- safe recovery after interruption;
- no duplicate market, AI, decision, order, fill, ledger, audit, or report side effect;
- canonical link between duplicate attempts and the original cycle.

## 11. Binance Adapter

The M007 adapter uses public REST for:

- server time;
- exchange and symbol metadata;
- finalized candles;
- checkpointed bounded gap repair.

It maps authentication-independent transport, timeout, rate-limit, malformed response, stale data, metadata, and data-quality failures to project-owned types.

It never uses private credentials or order endpoints.

Persistent WebSocket ingestion is deferred.

## 12. Gemini Adapter

The official `google-genai` SDK is isolated behind `LLMProvider`.

The adapter records/maps:

- configured provider/model and adapter versions;
- logical request and attempt IDs;
- timeout, cancellation, authentication, rate limit, transient/permanent failure;
- refusal, safety block, empty candidate, malformed output, invalid schema;
- usage, latency, retry, and cost estimate;
- provider-returned metadata safe for storage.

Application validation separately verifies schema, evidence references, unsupported claims, false certainty, prompt injection, source freshness/quality, and policy.

No Gemini tool may mutate state, execute code, place orders, size positions, alter risk/configuration, or approve lifecycle changes.

## 13. Market, Feature, Strategy, and Risk Services

- market services persist only validated finalized data and append-only corrections;
- snapshots preserve exact ordered source identities and hashes;
- feature calculations are versioned, deterministic, and no-look-ahead;
- strategy services emit immutable HOLD/ENTER/EXIT/REDUCE intents;
- risk services approve, reduce, reject, halt portfolio, or halt workspace;
- missing, stale, invalid, or incompatible evidence fails closed;
- strategy and AI cannot create an order or select final risk size.

## 14. Execution, Ledger, and Reconciliation Services

- one approved risk evaluation creates at most one paper order;
- execution uses versioned timing, fee, spread, slippage, precision, minimum-notional, partial-fill, cancellation, and time-in-force rules;
- all monetary values use Decimal and explicit units;
- ledger rows are append-only and transaction-balanced;
- corrections use reversal/replacement transactions;
- positions and portfolio summaries are rebuildable projections;
- reconciliation compares ledger-derived and persisted state;
- mismatch creates a critical event and halt.

## 15. Backtest Services

Backtests reuse domain contracts and:

- operate on immutable finalized datasets;
- enforce no look-ahead and next-event timing;
- include costs and required benchmarks;
- use disabled or exact precomputed Gemini evidence by default;
- preserve code/data/configuration/dependency/migration/seed provenance;
- report incomplete, failed, cancelled, or unreconciled outcomes explicitly;
- never directly promote a strategy.

## 16. Experiment and Operations Services

Experiment services manage immutable lifecycle transitions:

- draft;
- preflight;
- ready;
- running;
- paused;
- halted;
- completing;
- completed/failed/archived.

Start requires exact configuration-hash preflight, owner approval, reconciled initial portfolio, export/restore evidence, no active critical incident/halt, and live/private execution disabled.

Resume never clears unresolved risk, reconciliation, integrity, security, or incident blockers automatically.

## 17. Incident, Governance, and Change Services

- incidents distinguish alert acknowledgement, containment, service restoration, financial-integrity verification, and resolution;
- governance services manage memberships, permissions, RLS assurance, configurations, findings, exceptions, migrations, privacy, backups, releases, and approvals;
- research review services preserve hypotheses, variants, untouched tests, robustness, paper observation, reviewer conflicts, and owner decisions;
- change services preserve immutable before/after behavior sets, impact, compatibility, evidence, approvals, staged paper canaries, stop conditions, rollback, emergency expiry, and deprecation;
- no automated score, AI output, CI result, or browser action can approve or activate behavior.

## 18. API Error Model

Stable error categories include:

- validation and semantic validation;
- unauthenticated, unauthorized, recent-auth required;
- resource absent/not visible;
- idempotency or expected-version conflict;
- stale/invalid/incomplete data;
- provider/transport/budget/AI safety/output/grounding failure;
- strategy/risk rejection and halt;
- execution/accounting/reconciliation/integrity failure;
- migration/RLS/security/privacy/release blocker;
- quota/capacity/timeout/dependency unavailable;
- safe internal error.

Responses contain stable code, safe message, correlation ID, and bounded safe details. They never contain stack traces, SQL, secrets, credentials, unrestricted prompts, or raw provider payloads.

## 19. Logging and Durable Evidence

Structured logs use bounded fields such as:

- timestamp, level, service, environment, revision;
- correlation/request/cycle/experiment IDs;
- safe entity type/ID where approved;
- operation/stage, outcome, duration, stable error code.

Never log secrets, tokens, cookies, authorization headers, database URLs, raw prompt bodies, unrestricted provider responses, or private identifiers as unbounded metric labels.

Logs are diagnostic sources. Durable business/audit/cycle/incident/reconciliation evidence lives in PostgreSQL.

## 20. Testing

Required layers follow the selected Master Task:

- pure unit and property tests;
- PostgreSQL/migration/constraint/transaction tests;
- Supabase Auth and RLS tests;
- fake/fixture provider contract tests;
- API contract and generated-type tests;
- cycle duplicate/restart/timeout/stale/fallback/reconciliation tests;
- ledger reconstruction and restore tests;
- security/privacy/accessibility/E2E tests where affected;
- incident/change/release state-machine tests.

Normal CI requires no production Supabase, paid Gemini, cloud project, or private Binance access.

## 21. Deferred Backend Infrastructure

Redis, ARQ, persistent worker processes, WebSocket consumers, managed tracing/metrics, and paid/high-availability runtime changes are deferred.

Activation requires:

- measured M030 need;
- M034 change governance;
- accepted ADR;
- migration and compatibility plan;
- security/privacy and data review;
- cost/capacity evidence;
- test and recovery evidence;
- staged paper verification;
- rollback/forward-fix plan;
- owner approval.

## 22. Prohibited Patterns

- business logic in routes or CLI parsing;
- provider SDK types in domain or API contracts;
- direct browser writes to critical tables;
- custom Auth configuration that conflicts with Supabase Auth;
- local filesystem as authoritative state;
- binary float for money;
- network calls inside financial transactions;
- mutable ledger/audit/used configuration evidence;
- unbounded retries;
- strategy-to-order or AI-to-order bypass;
- risk, halt, reconciliation, Auth, RLS, release, or incident bypass flags;
- arbitrary browser environment/database/prompt consoles;
- editing an applied migration;
- automatic provider purchase/scaling;
- automatic strategy, release, or behavior activation;
- private/live exchange execution.

## 23. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `ARCHITECTURE.md`
- `TECH_STACK.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `DATABASE_SCHEMA.md`
- `API_SPECIFICATION.md`
- `SECURITY.md`
- `OBSERVABILITY.md`
