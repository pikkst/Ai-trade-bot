# The Daily Roast AI

> **Evidence-Driven Market Intelligence**

The Daily Roast AI is a documentation-first market research, backtesting, paper-trading, and Gemini-assisted decision-support platform.

It helps users inspect market evidence, compare deterministic and AI-assisted analysis, test strategies, simulate decisions with realistic costs, understand risk, and trace every conclusion to its source.

> **Current status:** implementation-ready specification. Start with Master Task 1 (`M001`) in [`TASKS.md`](TASKS.md).

## Product Identity

- **Official name:** The Daily Roast AI
- **Tagline:** Evidence-Driven Market Intelligence
- **Product:** `thedailyroast.online`
- **Application:** `app.thedailyroast.online`
- **API:** `api.thedailyroast.online`
- **Documentation:** `docs.thedailyroast.online`
- **Status:** `status.thedailyroast.online`

`Ai-trade-bot` is a technical repository identifier only. User-facing content must use **The Daily Roast AI**.

## Product Promise

The Daily Roast AI does not promise profit or certainty. It promises:

- transparent evidence;
- explicit uncertainty;
- deterministic strategy and risk boundaries;
- realistic paper execution;
- append-only accounting;
- reproducible research;
- complete decision lineage;
- human control over material changes.

## Implementation Entry Point

There is one implementation sequence:

1. read [`AGENTS.md`](AGENTS.md);
2. read [`docs/IMPLEMENTATION_EXECUTION_PLAN.md`](docs/IMPLEMENTATION_EXECUTION_PLAN.md);
3. open [`TASKS.md`](TASKS.md);
4. begin with **Master Task 1 (`M001`)**;
5. complete hard dependencies and detailed acceptance cards before moving forward;
6. continue through **Master Task 36 (`M036`)** for the production-research completion milestone.

`TASKS.md` defines order and hard dependencies. Supplemental files provide detailed acceptance criteria:

- [`UX_DESIGN_TASKS.md`](UX_DESIGN_TASKS.md);
- [`CLOUD_MVP_TASKS.md`](CLOUD_MVP_TASKS.md);
- [`LOCAL_AND_PRODUCTION_TASKS.md`](LOCAL_AND_PRODUCTION_TASKS.md);
- `SPRINT_3_TASKS.md` through `SPRINT_20_TASKS.md`.

Do not select a supplemental task as an independent entry point when its master-task dependencies are incomplete.

## Active MVP Architecture

```text
Browser
  -> Cloudflare Pages React application
  -> Render FastAPI for authenticated reads and explicit commands
  -> Supabase PostgreSQL and Auth

GitHub Actions best-effort schedule
  -> one-shot Python research-cycle CLI
  -> Binance Spot public REST finalized candles
  -> optional bounded Gemini analysis
  -> deterministic strategy and risk
  -> paper execution
  -> append-only ledger
  -> reconciliation and audit
```

### Required technology

- Python 3.12;
- FastAPI, Pydantic v2, SQLAlchemy 2, Alembic;
- Supabase PostgreSQL and Auth;
- React, TypeScript, Vite, React Router, TanStack Query;
- Binance Spot public REST;
- Google Gemini using the official `google-genai` SDK;
- GitHub Actions, Cloudflare Pages, and Render Free for the initial cloud profile;
- Pytest, Hypothesis, Ruff, MyPy, Bandit, Semgrep, Trivy, frontend tests, accessibility, and E2E tooling.

### Deferred infrastructure

The following are not mandatory MVP dependencies:

- Redis;
- ARQ or another persistent queue;
- persistent worker services;
- Binance WebSocket ingestion;
- hosted Prometheus or Grafana;
- Kubernetes;
- paid high-availability infrastructure.

They require measured need, an accepted ADR, migration and rollback plans, tests, cost review, and owner approval.

## Core Safety Flow

```text
finalized market data
  -> data-quality validation
  -> immutable snapshot
  -> deterministic features
  -> optional validated Gemini report
  -> deterministic strategy intent
  -> deterministic risk outcome
  -> simulated order and fill
  -> append-only double-entry ledger
  -> reconciled portfolio state
  -> immutable audit and report evidence
```

Gemini cannot:

- access credentials;
- mutate the database;
- execute code or shell commands;
- choose final position size;
- create orders;
- bypass risk;
- change a running experiment;
- approve a release or strategy;
- enable live trading.

## MVP Scope

Included:

- finalized Binance Spot OHLCV through REST polling;
- data quality, gap repair, immutable snapshots, and versioned features;
- schema-valid, evidence-grounded Gemini advisory reports;
- deterministic strategy and non-bypassable risk;
- paper orders, partial fills, fees, spread, slippage, precision, and minimum-notional behavior;
- append-only ledger, portfolio projections, rebuild, and reconciliation;
- reproducible backtests with cash and buy-and-hold benchmarks;
- authenticated evidence workspaces and bilingual product shell;
- controlled cloud scheduling and a 30-day virtual EUR 20 paper experiment;
- documentation, security, recovery, incident, data, performance, research-review, and change-management governance;
- staging and production-grade research-service development.

Excluded:

- live trading or private Binance order placement;
- Binance test trading without a separate future milestone;
- leverage, margin, futures, options, short selling, custody, and withdrawals;
- HFT, market making, and arbitrage;
- autonomous AI execution or self-modification;
- guaranteed profitability;
- public SLA claims for free-tier services;
- public billing or multi-tenant SaaS in the first milestone.

## Initial Controlled Experiment

- virtual capital: EUR 20;
- primary market: BTC/EUR;
- finalized candle interval: 1 hour;
- best-effort cycle cadence: approximately hourly;
- maximum position: 25% of reconciled equity;
- maximum order: EUR 5 equivalent;
- maximum daily drawdown: 5%;
- maximum total drawdown: 15%;
- maximum open orders: one;
- no leverage or shorting;
- Gemini monthly cost budget: EUR 0 by default;
- benchmarks: cash and buy-and-hold;
- duration: 30 calendar days or an approved early halt.

Profit is not an acceptance criterion. The experiment measures correctness, safety, completeness, reliability, cost, user comprehension, AI handling, auditability, and accounting integrity.

## Development Lifecycle

```text
M001–M006   Repository and local foundation
M007–M013   Core research domains
M014–M025   API, workspaces, product shell, and developer evidence
M026–M027   Full local/CI verification, export, restore, and security gate
M028–M029   Free-cloud demo and controlled paper experiment
M030–M034   Performance, data, research, incident, and change governance
M035        Post-experiment decision and staging readiness
M036        Production research launch and continuous operations
```

Production research means production-quality research and paper trading. It does not authorize real-money execution.

## Authoritative Documentation

### Governance and entry points

| File | Responsibility |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Mandatory implementation and safety rules |
| [`TASKS.md`](TASKS.md) | Canonical Master Task 1–36 sequence |
| [`docs/IMPLEMENTATION_EXECUTION_PLAN.md`](docs/IMPLEMENTATION_EXECUTION_PLAN.md) | Task authority, stages, dependencies, evidence, and completion |
| [`SPRINT_20_TASKS.md`](SPRINT_20_TASKS.md) | Documentation synchronization sprint |
| [`ROADMAP.md`](ROADMAP.md) | Product phase gates mapped to master tasks |
| [`docs/DOCUMENTATION_AUDIT.md`](docs/DOCUMENTATION_AUDIT.md) | Current repository-wide consistency findings |

### Product, architecture, and domain contracts

| File | Responsibility |
|---|---|
| [`docs/PRODUCT_REQUIREMENTS.md`](docs/PRODUCT_REQUIREMENTS.md) | Product and experiment requirements |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Active runtime and domain architecture |
| [`docs/BACKEND.md`](docs/BACKEND.md) | Backend boundaries and one-shot execution |
| [`docs/API_SPECIFICATION.md`](docs/API_SPECIFICATION.md) | API resources, commands, errors, and OpenAPI |
| [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) | PostgreSQL entities, constraints, ledger, and retention |
| [`docs/MARKET_DATA.md`](docs/MARKET_DATA.md) | Finalized market-data and quality contracts |
| [`docs/GEMINI_INTEGRATION.md`](docs/GEMINI_INTEGRATION.md) | Gemini adapter, structured output, budgets, and safety |
| [`docs/STRATEGY_ENGINE.md`](docs/STRATEGY_ENGINE.md) | Deterministic strategy contract |
| [`docs/RISK_ENGINE.md`](docs/RISK_ENGINE.md) | Risk rules and halt behavior |
| [`docs/PAPER_TRADING.md`](docs/PAPER_TRADING.md) | Simulated execution model |
| [`docs/PORTFOLIO_ENGINE.md`](docs/PORTFOLIO_ENGINE.md) | Ledger, portfolio projections, and reconciliation |
| [`docs/BACKTEST_ENGINE.md`](docs/BACKTEST_ENGINE.md) | Historical replay and reproducibility |
| [`docs/SECURITY.md`](docs/SECURITY.md) | Threat model, secrets, Auth/RLS, and gates |
| [`docs/TESTING.md`](docs/TESTING.md) | Test strategy and promotion evidence |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Environment deployment and promotion |

### Detailed implementation workstreams

- `UX_DESIGN_TASKS.md`;
- `CLOUD_MVP_TASKS.md`;
- `LOCAL_AND_PRODUCTION_TASKS.md`;
- `SPRINT_3_TASKS.md` through `SPRINT_20_TASKS.md`;
- their corresponding `docs/*_IMPLEMENTATION.md` workspace specifications.

## Engineering Principles

- evidence over hype;
- safety before automation;
- deterministic controls around probabilistic AI;
- PostgreSQL and the append-only ledger as sources of truth;
- Decimal monetary arithmetic and UTC timestamps;
- idempotent side effects and immutable used versions;
- deny-by-default browser access;
- no secrets in source, prompts, logs, telemetry, screenshots, or bundles;
- safe degradation during free-tier/provider failures;
- tested restore before backup claims;
- human approval for material research, release, and behavior changes;
- no profitability, uptime, recovery, or capacity claim without evidence.

## Disclaimer

The Daily Roast AI is a research and engineering project. It does not provide financial advice, execute live trades, or guarantee profitability. Financial and cryptocurrency markets can cause complete loss of capital.
