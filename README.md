# AI Trade Bot

AI Trade Bot is a documentation-first cryptocurrency research, paper-trading, backtesting, and AI decision-support platform.

The first version is intentionally designed for safe experimentation. It ingests crypto market data, calculates deterministic indicators, asks AI models to produce structured analysis, validates all recommendations through deterministic strategy and risk rules, and executes only simulated paper trades.

## Current Scope

The MVP includes:

- Binance Spot public market data
- Historical and near-real-time OHLCV ingestion
- Technical indicators and market-regime analysis
- Structured AI market reports
- Deterministic strategy evaluation
- Non-bypassable risk controls
- Paper-trading wallet, orders, fills, fees, and slippage
- Backtesting and benchmark comparison
- Audit logs and decision lineage
- Docker-based local development
- Prometheus metrics and Grafana dashboards

Live trading, leverage, futures, margin, custody, and automated withdrawals are explicitly excluded from the MVP.

## Core Safety Flow

```text
Market data
  -> data validation
  -> deterministic feature calculation
  -> AI analysis
  -> schema validation
  -> deterministic strategy engine
  -> deterministic risk engine
  -> paper execution
  -> reconciliation
  -> audit and reporting
```

AI is advisory. It never bypasses the strategy engine, risk engine, or execution controls.

## Initial Validation Experiment

The first controlled experiment uses a virtual balance equivalent to EUR 20 for 30 days.

- Primary pair: BTC/EUR
- Optional observation pairs: ETH/EUR and SOL/EUR
- Maximum position: 25% of portfolio equity
- Maximum risk budget per decision: 1% of equity
- Maximum daily drawdown: 5%
- Maximum total drawdown: 15%
- Trading fees and slippage included
- Benchmarks: cash and buy-and-hold
- Human approval enabled during initial validation

## Technology Stack

- Python 3.12
- FastAPI
- PostgreSQL
- Redis and ARQ
- SQLAlchemy 2 and Alembic
- Pydantic 2
- Polars
- Binance native Spot REST and WebSocket interfaces
- OpenAI Responses API through a provider abstraction
- Optional local LLM through Ollama or vLLM
- React and TypeScript
- Docker Compose
- Prometheus and Grafana
- Pytest, Ruff, MyPy, Bandit, Semgrep, and Trivy

Exact versions must be pinned in lock files and validated by CI.

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

All AI coding tools and contributors must read and follow [AGENTS.md](AGENTS.md) before changing code. It defines safety boundaries, architecture rules, testing requirements, documentation duties, and the definition of done.

The similarly named [`docs/AGENTS.md`](docs/AGENTS.md) describes runtime analytical agents inside the product; it is not the coding-agent instruction file.

## Documentation Index

| Document | Purpose |
|---|---|
| [AI Coding Agent Rules](AGENTS.md) | Mandatory implementation rules for AI coding tools and contributors |
| [Documentation Audit](docs/DOCUMENTATION_AUDIT.md) | Coverage matrix, known gaps, and future audit procedure |
| [Product Requirements](docs/PRODUCT_REQUIREMENTS.md) | Goals, scope, users, requirements, acceptance criteria |
| [Architecture](docs/ARCHITECTURE.md) | Components, flows, and failure behavior |
| [Backend](docs/BACKEND.md) | Backend package design and engineering rules |
| [API Specification](docs/API_SPECIFICATION.md) | REST resources, payloads, errors, and versioning |
| [Database Schema](docs/DATABASE_SCHEMA.md) | Entities, constraints, indexes, and retention |
| [AI Architecture](docs/AI_ARCHITECTURE.md) | AI boundaries, providers, and structured outputs |
| [Runtime AI Agents](docs/AGENTS.md) | Product agent responsibilities and contracts |
| [AI Prompts](docs/AI_PROMPTS.md) | Prompt templates and output schemas |
| [Market Data](docs/MARKET_DATA.md) | Data normalization, quality, and freshness |
| [Binance Integration](docs/BINANCE_INTEGRATION.md) | Exchange adapter and sandbox progression |
| [Paper Trading](docs/PAPER_TRADING.md) | Simulated execution model |
| [Backtest Engine](docs/BACKTEST_ENGINE.md) | Historical simulation and reproducibility |
| [Strategy Engine](docs/STRATEGY_ENGINE.md) | Strategy lifecycle and decisions |
| [Risk Engine](docs/RISK_ENGINE.md) | Hard limits and kill-switch behavior |
| [Portfolio Engine](docs/PORTFOLIO_ENGINE.md) | Ledger, balances, positions, and P&L |
| [Security](docs/SECURITY.md) | Threat model, secrets, access control, and audit |
| [Testing](docs/TESTING.md) | Test strategy and release gates |
| [Observability](docs/OBSERVABILITY.md) | Logs, metrics, dashboards, and alerts |
| [Deployment](docs/DEPLOYMENT.md) | Local, sandbox, and production environments |
| [Technology Stack](docs/TECH_STACK.md) | Selected technologies and rationale |
| [Architecture Decisions](docs/ADR.md) | Initial architectural decisions |
| [Implementation Tasks](TASKS.md) | Ordered MVP backlog |
| [Roadmap](ROADMAP.md) | Product evolution plan |

## Engineering Principles

- Documentation before implementation
- Deterministic controls around probabilistic models
- Reproducibility before optimization
- Decimal arithmetic for monetary values
- UTC timestamps everywhere
- Idempotent external side effects
- Safe defaults and explicit feature flags
- Complete auditability
- No secrets in source control or logs
- No profitability claims without statistically valid evidence

## Documentation Status

The document set is structurally complete for beginning MVP implementation. Exact dependency pins, generated OpenAPI schemas, column-level migrations, dashboard definitions, and measured operational targets must be added and maintained together with the implementation. See the [documentation audit](docs/DOCUMENTATION_AUDIT.md).

## Disclaimer

This project is for research and engineering experimentation. It does not provide financial advice and does not guarantee profitability. Cryptocurrency markets are volatile and may cause complete loss of capital.
