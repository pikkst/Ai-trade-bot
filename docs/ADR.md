# Architecture Decision Records

Last reviewed: 2026-07-31
Status: Accepted baseline decisions

## ADR-001 — Modular Monolith

**Status:** Accepted

Use a Python modular monolith with shared domain/application packages and separate FastAPI and CLI entry points. Extract services only after measured need.

## ADR-002 — Supabase-Managed PostgreSQL Is the System of Record

**Status:** Accepted; supersedes the deployment assumptions in the former PostgreSQL/Redis decision.

Use a dedicated Supabase Free project for PostgreSQL and Auth during the first cloud experiment. PostgreSQL remains authoritative for financial, decision, audit, and scheduling state. Local filesystems and external schedulers are not authoritative.

## ADR-003 — Google Gemini Is Advisory Only

**Status:** Accepted

Gemini produces structured analysis. It cannot execute orders, size final positions, mutate state, access credentials, or change strategy/risk policy.

## ADR-004 — Google Gemini API Is the Required V1 Cloud AI Provider

**Status:** Accepted

Use the official `google-genai` SDK behind a project-owned `LLMProvider`. Normal CI uses a deterministic fake provider. Model, prompt, schema, safety configuration, usage, and cost are versioned.

## ADR-005 — Paper Trading Before Private Exchange Access

**Status:** Accepted

No private Binance key is used in MVP. Binance test/private APIs are a later gated milestone.

## ADR-006 — Append-Only Double-Entry Ledger

**Status:** Accepted

The ledger is the financial source of truth. Balances and positions are rebuildable projections. Corrections use reversal/replacement transactions.

## ADR-007 — No Live Trading in MVP

**Status:** Accepted

Live trading, leverage, margin, futures, shorting, custody, and withdrawals remain disabled.

## ADR-008 — Use a One-Shot Research-Cycle CLI and GitHub Actions Scheduler

**Status:** Accepted; supersedes the former requirement to use Redis and ARQ in the first deployment.

### Context

The first experiment must run in the cloud without a local computer and without required monthly infrastructure spending. An hourly finalized-candle strategy does not require a continuously running queue worker.

### Decision

Use a one-shot Python CLI scheduled approximately hourly by GitHub Actions. Use PostgreSQL advisory locks or a persistent lease plus idempotency keys to prevent overlap and duplicate side effects.

### Consequences

- Redis and ARQ are not MVP dependencies;
- GitHub schedule timing is best-effort and may be delayed;
- execution is unsuitable for high-frequency trading;
- the CLI must be restart-safe and stateless outside PostgreSQL;
- future queue infrastructure requires a new ADR based on measured need.

## ADR-009 — Use Polars for Analytical Pipelines

**Status:** Accepted

Use Polars for new calculations. Domain contracts do not expose dataframe types.

## ADR-010 — Use Binance Spot REST for the Free-Cloud MVP

**Status:** Accepted; narrows the former native REST/WebSocket decision.

Use native Binance Spot REST for server time, exchange metadata, finalized candles, and gap repair. Persistent WebSocket ingestion is deferred because the experiment runs approximately hourly.

## ADR-011 — Use Finalized Candles

**Status:** Accepted

Feature, Gemini, strategy, risk, and backtest decisions consume only finalized candles.

## ADR-012 — Share Contracts Across Backtesting and Paper Trading

**Status:** Accepted

Backtests and paper trading reuse strategy, risk, execution, and portfolio contracts.

## ADR-013 — Immutable Versioned Experiment Configuration

**Status:** Accepted

Freeze model, prompt, schema, data, strategy, risk, execution, and infrastructure profile versions before experiment start.

## ADR-014 — Fail Closed

**Status:** Accepted

Reject or halt on stale data, missing policy, unsupported precision, missing cost model, database failure, duplicate ambiguity, or reconciliation mismatch.

## ADR-015 — No Live Gemini Calls During Standard Historical Replay

**Status:** Accepted

Backtests disable AI or use immutable precomputed validated reports.

## ADR-016 — Use Cloudflare Pages, Render Free, and Supabase Free

**Status:** Accepted for the first 30-day experiment

### Decision

- Cloudflare Pages hosts the static frontend.
- Render Free hosts FastAPI.
- A dedicated Supabase Free project hosts PostgreSQL and Auth.
- GitHub Actions schedules research cycles.

### Consequences

- free services may sleep, pause, restart, throttle, or change limits;
- no production SLA is claimed;
- Render cold starts do not affect scheduled cycles;
- authoritative state cannot live on Render local disk;
- the unrelated Eventnexus Supabase project must not be reused;
- migration, RLS, export, and restore procedures are mandatory.

## ADR-017 — Defer Hosted Prometheus and Grafana

**Status:** Accepted for the free-cloud experiment

Use structured logs and persistent cycle/audit/freshness/halt/reconciliation records plus GitHub Actions, Render, and Supabase operational logs. Hosted Prometheus/Grafana may be added later when cost or operational needs justify them.

## Decision Change Process

To supersede a decision:

1. create a new ADR;
2. identify the superseded decision;
3. document migration and compatibility;
4. update requirements, architecture, deployment, tasks, and tests;
5. obtain explicit owner approval for provider changes, private exchange access, live trading, risk weakening, or ledger changes.
