# AI Trade Bot

AI Trade Bot is a documentation-first cryptocurrency research, backtesting, paper-trading, and AI decision-support platform.

The MVP collects Binance Spot market data, calculates deterministic indicators, uses Google Gemini API to generate structured analytical reports, validates recommendations through deterministic strategy and risk rules, and executes only simulated paper trades.

## MVP Scope

Included:

- Binance Spot public market data
- Historical and near-real-time OHLCV ingestion
- Data-quality checks and immutable market snapshots
- Deterministic technical indicators
- Google Gemini API structured market analysis
- Deterministic strategy evaluation
- Non-bypassable risk controls
- Paper-trading balances, orders, fills, fees, slippage, and reconciliation
- Backtesting and cash/buy-and-hold benchmarks
- Audit logs and decision lineage
- Docker-based local development
- Prometheus metrics and Grafana dashboards

Excluded from the MVP:

- live trading;
- leverage, margin, futures, and shorting;
- custody and withdrawals;
- high-frequency trading;
- autonomous AI execution authority;
- guaranteed-return or profitability claims.

## Core Safety Flow

```text
Binance market data
  -> data validation
  -> deterministic features
  -> Gemini structured analysis
  -> schema and evidence validation
  -> deterministic strategy
  -> deterministic risk engine
  -> paper execution
  -> ledger reconciliation
  -> audit and reporting
```

Gemini is an advisory analytical component. It cannot create orders, select credentials, resize positions, alter risk policies, enable live trading, or bypass validation.

## Initial Validation Experiment

The first controlled experiment uses a virtual EUR 20 balance for 30 days.

- Primary pair: BTC/EUR
- Optional observation pairs: ETH/EUR and SOL/EUR
- Maximum position: 25% of portfolio equity
- Maximum daily drawdown: 5%
- Maximum total drawdown: 15%
- One open order maximum
- No leverage or shorting
- Fees and slippage included
- Benchmarks: cash and buy-and-hold
- Human review enabled

## Authoritative Technology Stack

- Python 3.12
- FastAPI, Pydantic v2, SQLAlchemy 2, Alembic
- PostgreSQL
- Redis and ARQ
- Polars
- Binance native Spot REST and WebSocket APIs
- Google Gemini API through the official `google-genai` Python SDK
- Gemini structured output with project-owned JSON Schema or Pydantic models
- Deterministic fake AI provider for tests
- React, TypeScript, Vite, and TanStack Query
- Docker Compose
- Prometheus and Grafana
- Pytest, Hypothesis, Ruff, MyPy, Bandit, Semgrep, and Trivy

Exact dependency versions must be pinned in lock files and validated by CI.

## Repository Structure

```text
.
├── AGENTS.md
├── README.md
├── TASKS.md
├── ROADMAP.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
├── .env.example
├── docs/
├── backend/
├── frontend/
├── ai/
├── infrastructure/
└── tests/
```

## AI Coding Agents

All coding agents and contributors must follow [`AGENTS.md`](AGENTS.md). It defines mandatory architecture, security, testing, documentation, financial-calculation, Gemini-integration, and definition-of-done rules.

[`docs/AGENTS.md`](docs/AGENTS.md) is different: it describes runtime analytical agents inside the application.

## Actual Documentation Inventory

The following table lists the Markdown specification files that currently exist in the repository. The file path is authoritative.

| Exact file | Current responsibility |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Mandatory instructions for AI coding agents and human contributors |
| [`TASKS.md`](TASKS.md) | Implementable MVP work items with user story, acceptance criteria, and definition of done |
| [`ROADMAP.md`](ROADMAP.md) | Product phases from documentation through controlled sandbox and later live evaluation |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution and pull-request workflow |
| [`CHANGELOG.md`](CHANGELOG.md) | Material documentation and implementation changes |
| [`docs/DOCUMENTATION_AUDIT.md`](docs/DOCUMENTATION_AUDIT.md) | Documentation coverage, known gaps, and audit procedure |
| [`docs/PRODUCT_REQUIREMENTS.md`](docs/PRODUCT_REQUIREMENTS.md) | MVP goals, exclusions, functional requirements, non-functional requirements, and completion criteria |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Modular-monolith architecture, domains, components, consistency, and failure policy |
| [`docs/BACKEND.md`](docs/BACKEND.md) | Backend package boundaries, configuration, errors, and quality rules |
| [`docs/API_SPECIFICATION.md`](docs/API_SPECIFICATION.md) | Planned `/api/v1` resources, authentication, idempotency, errors, and versioning |
| [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) | Planned tables, constraints, indexes, ledger rules, and retention |
| [`docs/AI_ARCHITECTURE.md`](docs/AI_ARCHITECTURE.md) | Provider boundary, Gemini analysis flow, validation, failures, evaluations, and invariants |
| [`docs/GEMINI_INTEGRATION.md`](docs/GEMINI_INTEGRATION.md) | Authoritative Gemini SDK, authentication, structured output, budgets, safety, retries, tests, and observability specification |
| [`docs/AGENTS.md`](docs/AGENTS.md) | Runtime analytical-agent roles and contracts |
| [`docs/AI_PROMPTS.md`](docs/AI_PROMPTS.md) | Prompt principles, templates, and output-schema rules |
| [`docs/MARKET_DATA.md`](docs/MARKET_DATA.md) | Binance market-data normalization, validation, freshness, and backfill |
| [`docs/BINANCE_INTEGRATION.md`](docs/BINANCE_INTEGRATION.md) | Binance adapter, rate limits, WebSocket recovery, testnet progression, and reconciliation |
| [`docs/STRATEGY_ENGINE.md`](docs/STRATEGY_ENGINE.md) | Deterministic strategy contract, intents, lifecycle, and baseline strategy |
| [`docs/RISK_ENGINE.md`](docs/RISK_ENGINE.md) | Mandatory risk decisions, limits, EUR 20 profile, halt conditions, and fail-closed behavior |
| [`docs/PAPER_TRADING.md`](docs/PAPER_TRADING.md) | Simulated order lifecycle, fill assumptions, fees, slippage, and idempotency |
| [`docs/PORTFOLIO_ENGINE.md`](docs/PORTFOLIO_ENGINE.md) | Append-only ledger, balances, positions, P&L, equity, and reconciliation |
| [`docs/BACKTEST_ENGINE.md`](docs/BACKTEST_ENGINE.md) | Historical event replay, look-ahead prevention, benchmarks, metrics, and reproducibility |
| [`docs/SECURITY.md`](docs/SECURITY.md) | Threats, secrets, authorization, scanning, credential restrictions, and incident response |
| [`docs/TESTING.md`](docs/TESTING.md) | Unit, integration, contract, end-to-end, property, failure, and release-gate testing |
| [`docs/OBSERVABILITY.md`](docs/OBSERVABILITY.md) | Structured logs, Prometheus metrics, dashboards, alerts, and runbook expectations |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Local, CI, sandbox, and future production deployment boundaries |
| [`docs/TECH_STACK.md`](docs/TECH_STACK.md) | Definitive MVP technologies and decision policy |
| [`docs/ADR.md`](docs/ADR.md) | Accepted architecture decisions and rationale |

Empty source directories and `.gitkeep` files are placeholders; their existence does not mean the corresponding implementation is complete.

## Engineering Principles

- Documentation before implementation
- Deterministic controls around probabilistic AI
- Reproducibility before optimization
- `Decimal` arithmetic for monetary values
- Timezone-aware UTC timestamps
- Idempotent external side effects
- Safe defaults and explicit feature flags
- Complete auditability
- No secrets in source control or logs
- No profitability claims without statistically valid evidence

## Documentation Status

The specification set is sufficient to begin the first implementation tasks, but it is not a substitute for generated implementation artifacts. Exact dependency locks, OpenAPI schemas, database migrations, metric names, Grafana JSON, measured performance results, and operational recovery targets must be created and updated in the same pull requests as their implementations.

## Disclaimer

This project is for research and engineering experimentation. It does not provide financial advice and does not guarantee profitability. Cryptocurrency markets are volatile and may cause complete loss of capital.
