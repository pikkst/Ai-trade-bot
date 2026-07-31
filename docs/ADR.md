# Architecture Decision Records

Last reviewed: 2026-07-31
Status: Accepted baseline decisions

## ADR Format

Each decision records context, decision, consequences, alternatives, and change conditions. New material architectural choices require a new ADR rather than silent documentation edits.

---

## ADR-001 — Use a Modular Monolith

**Status:** Accepted

### Context

The MVP requires strong transaction boundaries, rapid local development, and multiple domains, but does not yet have measured scale or team boundaries that justify microservices.

### Decision

Use a Python modular monolith with separate API, worker, and scheduler processes sharing domain and application packages.

### Consequences

- simpler deployment and debugging;
- strong portfolio transaction boundaries;
- domain boundaries remain explicit;
- modules may be extracted later based on measured need;
- direct cross-domain table mutation is prohibited.

### Reconsider When

Independent scaling, ownership, availability, or deployment requirements clearly exceed modular-monolith capabilities.

---

## ADR-002 — PostgreSQL Is the System of Record

**Status:** Accepted

### Context

The platform needs transactional accounting, constraints, versioned records, auditability, and reproducible queries.

### Decision

Use PostgreSQL as the authoritative store. Redis is only for queues, locks, cache, and ephemeral coordination.

### Consequences

- ledger and financial state remain durable;
- Redis loss does not destroy authoritative state;
- migrations and backups are operationally important;
- queue handlers must be idempotent.

---

## ADR-003 — Google Gemini Is Advisory Only

**Status:** Accepted

### Context

LLM output is probabilistic, may be incorrect, may be blocked, and can change with model behavior.

### Decision

Google Gemini produces structured analytical reports only. Deterministic strategy, risk, execution, and reconciliation remain authoritative.

### Consequences

- Gemini receives no order, exchange, shell, database mutation, or risk-policy tools;
- invalid output degrades to deterministic fallback or HOLD;
- every report is independently validated;
- Gemini confidence is not probability of profit.

---

## ADR-004 — Use Google Gemini API as the Required Cloud AI Provider for V1

**Status:** Accepted

### Context

The project owner selected Google Gemini API for the initial cloud AI integration.

### Decision

Use the official `google-genai` Python SDK behind a project-owned `LLMProvider` protocol. Use a deterministic fake provider in CI.

### Consequences

- Gemini SDK objects are isolated in infrastructure code;
- model identifier and quotas are configuration;
- prompts, schemas, model settings, usage, and costs are versioned;
- OpenAI is not part of the V1 implementation plan;
- local or alternative providers require a future ADR.

---

## ADR-005 — Paper Trading Before Any Private Exchange API

**Status:** Accepted

### Context

Private exchange integration introduces credential, duplicate-order, reconciliation, and financial-loss risks.

### Decision

Complete public market data, internal paper trading, backtesting, and the controlled 30-day experiment before designing Binance private API access.

### Consequences

- no private Binance credential in MVP;
- Binance test environment is a later gated phase;
- paper execution must model costs and limitations honestly;
- sandbox success will not automatically approve live trading.

---

## ADR-006 — Use an Append-Only Double-Entry Ledger

**Status:** Accepted

### Context

Mutable balance fields alone are difficult to audit and reconcile.

### Decision

Use an append-only double-entry ledger as the financial source of truth. Positions and balances are rebuildable projections.

### Consequences

- corrections use reversal/replacement transactions;
- fill and ledger posting are atomic;
- reconciliation can detect divergence;
- accounting logic requires strong property tests.

---

## ADR-007 — No Live Trading in MVP

**Status:** Accepted

### Context

The first objective is validating engineering, analysis, risk, and accounting, not risking capital.

### Decision

Do not implement or enable live trading, leverage, margin, futures, shorting, withdrawals, or custody in MVP.

### Consequences

- `LIVE_TRADING_ENABLED` remains false and has no active execution path;
- documentation and UI must label all trading as simulated;
- future live work requires a separate owner-approved milestone, legal review, security review, and implementation specification.

---

## ADR-008 — Use Python 3.12, FastAPI, PostgreSQL, Redis, and ARQ

**Status:** Accepted

### Context

The MVP needs strong typing, asynchronous I/O, mature database tooling, background jobs, and low operational complexity.

### Decision

Use Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL, Redis, and ARQ.

### Consequences

- dependency versions are pinned in lock files;
- MyPy strict and Ruff are mandatory;
- ARQ remains replaceable if measured reliability or scheduling needs justify a change;
- moving to Celery or another queue requires an ADR.

---

## ADR-009 — Use Polars for New Analytical Pipelines

**Status:** Accepted

### Context

The project needs efficient typed data-frame operations while minimizing unnecessary dependency complexity.

### Decision

Use Polars for new analytical pipelines. Pandas may be isolated at third-party boundaries where required.

### Consequences

- domain contracts do not expose data-frame types;
- calculations require deterministic reference tests;
- introducing Pandas broadly requires justification.

---

## ADR-010 — Use Native Binance Spot Interfaces for Binance-Specific Behavior

**Status:** Accepted

### Context

Generic exchange libraries may obscure current Binance filters, precision, rate limits, and signing behavior.

### Decision

Use Binance Spot native REST and WebSocket interfaces through a project-owned adapter. CCXT may be used later for research or multi-exchange support, but is not authoritative for Binance-specific rules.

### Consequences

- exchange metadata and current official documentation are authoritative;
- adapter contract tests are required;
- private API signing is deferred.

---

## ADR-011 — Use Finalized Candles for MVP Decisions

**Status:** Accepted

### Context

Partial candles can change before close and create replay ambiguity.

### Decision

Normal feature, Gemini, strategy, and backtest workflows consume only finalized candles.

### Consequences

- lower-frequency decision latency;
- stronger reproducibility;
- WebSocket partial candles may be stored as ephemeral state but are not approved decision input;
- any future partial-candle strategy requires a new ADR and risk analysis.

---

## ADR-012 — Use Shared Contracts for Backtesting and Paper Trading

**Status:** Accepted

### Context

Separate backtest and runtime logic creates unrealistic results and divergence.

### Decision

Backtesting and paper trading reuse strategy, risk, execution, and portfolio contracts.

### Consequences

- execution timing and cost models remain explicit;
- no-look-ahead remains mandatory;
- improvements benefit both environments;
- backtest performance cannot use shortcuts unavailable to paper trading.

---

## ADR-013 — Use Immutable Versioned Experiment Configuration

**Status:** Accepted

### Context

Changing model, prompt, strategy, risk, or execution assumptions during an experiment destroys interpretability.

### Decision

Freeze a canonical hashed configuration before an experiment starts.

### Consequences

- active experiments retain all referenced versions;
- changes require a new configuration and normally a new experiment;
- reports can reproduce exact assumptions.

---

## ADR-014 — Fail Closed on Integrity and Risk Uncertainty

**Status:** Accepted

### Context

Guessing during data, risk, precision, or accounting failure may create invalid simulated financial state and would be unsafe in later environments.

### Decision

Reject or halt on stale data, missing policy, unsupported precision, missing cost model, database failure, reconciliation mismatch, and risk exceptions.

### Consequences

- some opportunities are intentionally missed;
- operators receive explicit alerts and reason codes;
- safe degradation is prioritized over continuous activity.

---

## ADR-015 — Do Not Call Live Gemini During Standard Historical Replay

**Status:** Accepted

### Context

Live model calls during every historical step are expensive and not reliably reproducible.

### Decision

Standard backtests either disable AI or use immutable precomputed validated Gemini reports tied to exact snapshots and versions.

### Consequences

- deterministic backtests remain reproducible;
- sampled live-model historical research is treated as a separate experiment;
- reports disclose whether AI was disabled, precomputed, or separately sampled.

## Decision Change Process

To supersede a decision:

1. create a new ADR;
2. reference the superseded ADR;
3. describe migration and compatibility;
4. update related requirements, architecture, tasks, and tests;
5. obtain explicit owner approval for changes involving Gemini provider, private exchange access, live trading, risk weakening, or ledger architecture.
