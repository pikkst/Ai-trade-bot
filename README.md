# AI Trade Bot

AI Trade Bot is a documentation-first cryptocurrency research, backtesting, paper-trading, and AI decision-support platform.

The MVP collects Binance Spot public market data, calculates deterministic indicators, uses Google Gemini API to generate structured analytical reports, validates recommendations through deterministic strategy and risk rules, and executes only simulated paper trades.

> **Current status:** documentation and implementation specification. Source-code directories are placeholders until their corresponding `TASKS.md` items are completed and verified.

## MVP Scope

Included:

- Binance Spot public market data;
- historical and near-real-time finalized OHLCV ingestion;
- data-quality checks, gap repair, and immutable market snapshots;
- deterministic technical indicators;
- Google Gemini API structured market analysis;
- deterministic strategy evaluation;
- non-bypassable deterministic risk controls;
- paper-trading balances, orders, fills, fees, spread, slippage, and reconciliation;
- append-only double-entry portfolio ledger;
- reproducible backtesting and cash/buy-and-hold benchmarks;
- audit logs and complete decision lineage;
- Docker-based local and persistent research environments;
- Prometheus metrics, Grafana dashboards, alerts, and runbooks.

Excluded from the MVP:

- live trading and private Binance order placement;
- leverage, margin, futures, options, and shorting;
- custody and withdrawals;
- high-frequency trading, market making, and arbitrage;
- autonomous AI execution authority;
- self-modifying prompts, strategies, or risk policies;
- public multi-tenant SaaS and billing;
- guaranteed-return or profitability claims.

## Core Safety Flow

```text
Binance public market data
  -> data validation and freshness policy
  -> immutable market snapshot
  -> deterministic versioned features
  -> Gemini structured analysis
  -> schema, evidence, safety, and policy validation
  -> deterministic strategy intent
  -> deterministic non-bypassable risk engine
  -> paper execution model
  -> append-only ledger and reconciliation
  -> audit, metrics, and reporting
```

Gemini is an advisory analytical component. It cannot create orders, select credentials, resize final positions, alter strategy or risk policy, enable live trading, mutate the database, or bypass validation.

## Initial Validation Experiment

The first controlled experiment uses a virtual EUR 20 balance for 30 calendar days.

- Primary pair: BTC/EUR
- Optional observation-only pairs: ETH/EUR and SOL/EUR
- Maximum position: 25% of reconciled portfolio equity
- Maximum single order: EUR 5 equivalent
- Maximum daily drawdown: 5%
- Maximum total drawdown: 15%
- One open order maximum
- No leverage or shorting
- Fees, spread, slippage, precision, and minimum-notional checks included
- Benchmarks: cash and buy-and-hold
- Frozen versioned experiment configuration
- Human owner review enabled

Profit is not an MVP acceptance criterion. The experiment validates system correctness, safety, data quality, AI handling, decision lineage, accounting, and operational reliability.

## Authoritative Technology Stack

- Python 3.12
- FastAPI, Pydantic v2, SQLAlchemy 2, Alembic
- PostgreSQL
- Redis and ARQ
- Polars
- Binance native Spot REST and WebSocket APIs
- Google Gemini API through the official `google-genai` Python SDK
- Gemini structured output with project-owned JSON Schema or Pydantic models
- Deterministic fake AI provider for normal CI and tests
- React, TypeScript, Vite, and TanStack Query
- Docker Compose
- Prometheus and Grafana
- Pytest, Hypothesis, Ruff, MyPy, Bandit, Semgrep, and Trivy

Exact dependency versions belong in committed lock files and release manifests. Gemini model identifiers and active quotas are configuration recorded per experiment; they are not hardcoded assumptions in domain logic.

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

Empty source directories and `.gitkeep` files are placeholders. Their existence does not mean the corresponding implementation is complete.

## Documentation Precedence

When documents conflict, use this order:

1. security, financial-integrity, and fail-closed requirements;
2. [`AGENTS.md`](AGENTS.md);
3. [`docs/PRODUCT_REQUIREMENTS.md`](docs/PRODUCT_REQUIREMENTS.md);
4. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and accepted ADRs;
5. domain-specific specifications under `docs/`;
6. [`TASKS.md`](TASKS.md);
7. local implementation conventions.

Material conflicts must be documented and corrected. They must not be silently resolved in code.

## AI Coding Agents

All coding agents and contributors must follow [`AGENTS.md`](AGENTS.md) before changing code. It defines mandatory architecture, security, testing, documentation, financial-calculation, Gemini-integration, and Definition of Done rules.

[`docs/AGENTS.md`](docs/AGENTS.md) is different: it describes runtime analytical agents inside the application.

## Actual Documentation Inventory

The following table lists the authoritative Markdown specification files that currently exist in the repository. Exact file paths are authoritative.

| Exact file | Responsibility |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Mandatory instructions for AI coding agents and human contributors |
| [`TASKS.md`](TASKS.md) | Independently implementable work items with user story, acceptance criteria, Definition of Done, dependencies, and references |
| [`ROADMAP.md`](ROADMAP.md) | Gated product phases from documentation through the paper experiment and future Binance test-environment assessment |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Branch, implementation, test, review, and pull-request workflow |
| [`CHANGELOG.md`](CHANGELOG.md) | Material documentation and implementation changes |
| [`docs/DOCUMENTATION_AUDIT.md`](docs/DOCUMENTATION_AUDIT.md) | Coverage, consistency findings, known implementation-dependent artifacts, and audit procedure |
| [`docs/PRODUCT_REQUIREMENTS.md`](docs/PRODUCT_REQUIREMENTS.md) | Vision, users, scope, functional and non-functional requirements, experiment rules, success metrics, and MVP completion criteria |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System context, containers, domains, flows, state machines, transactions, idempotency, deployment, and failure behavior |
| [`docs/BACKEND.md`](docs/BACKEND.md) | Backend layers, package boundaries, configuration, persistence, jobs, provider adapters, errors, tests, and prohibited patterns |
| [`docs/API_SPECIFICATION.md`](docs/API_SPECIFICATION.md) | Planned `/api/v1` resources, roles, payload conventions, idempotency, errors, jobs, and OpenAPI verification |
| [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) | Logical entities, ownership, fields, constraints, indexes, retention, ledger rules, and migration policy |
| [`docs/AI_ARCHITECTURE.md`](docs/AI_ARCHITECTURE.md) | AI provider boundary, Gemini analysis flow, output validation, failures, evaluation, and invariants |
| [`docs/GEMINI_INTEGRATION.md`](docs/GEMINI_INTEGRATION.md) | Authoritative Gemini SDK, authentication, structured output, budgets, safety, retry, test, and observability specification |
| [`docs/AGENTS.md`](docs/AGENTS.md) | Runtime analytical-agent roles, contracts, orchestration, versioning, evaluation, and restrictions |
| [`docs/AI_PROMPTS.md`](docs/AI_PROMPTS.md) | Prompt layers, templates, evidence envelope, injection defense, output contract, versioning, and evaluation |
| [`docs/MARKET_DATA.md`](docs/MARKET_DATA.md) | Binance market-data models, normalization, validation, freshness, backfill, WebSocket recovery, correction, and snapshots |
| [`docs/BINANCE_INTEGRATION.md`](docs/BINANCE_INTEGRATION.md) | Binance interfaces, adapter, rate-limit handling, WebSocket continuity, future private-API progression, and reconciliation |
| [`docs/STRATEGY_ENGINE.md`](docs/STRATEGY_ENGINE.md) | Deterministic strategy inputs, intents, Gemini relationship, baseline strategies, lifecycle, and anti-overfitting rules |
| [`docs/RISK_ENGINE.md`](docs/RISK_ENGINE.md) | Non-bypassable policies, sizing boundaries, EUR 20 profile, drawdown, halts, reason codes, and fail-closed behavior |
| [`docs/PAPER_TRADING.md`](docs/PAPER_TRADING.md) | Simulated order lifecycle, execution-model versions, market/limit fills, fees, slippage, precision, idempotency, and limitations |
| [`docs/PORTFOLIO_ENGINE.md`](docs/PORTFOLIO_ENGINE.md) | Double-entry ledger, reservations, cost basis, P&L, equity, drawdown, projections, and reconciliation |
| [`docs/BACKTEST_ENGINE.md`](docs/BACKTEST_ENGINE.md) | Historical replay, no-look-ahead, Gemini modes, execution timing, benchmarks, metrics, reproducibility, and anti-overfitting |
| [`docs/SECURITY.md`](docs/SECURITY.md) | Threat model, secrets, authentication, Gemini safety, financial controls, supply chain, incident response, and release gates |
| [`docs/TESTING.md`](docs/TESTING.md) | Test pyramid, domain matrix, property invariants, provider policy, E2E, resilience, performance, coverage, and release gates |
| [`docs/OBSERVABILITY.md`](docs/OBSERVABILITY.md) | Logs, correlation, metrics, dashboards, alerts, health, runbooks, retention, and testing |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Local, CI, persistent sandbox, service topology, migrations, backups, rollback, promotion gates, and release artifacts |
| [`docs/TECH_STACK.md`](docs/TECH_STACK.md) | Definitive MVP technologies, provider and exchange selections, quality tooling, and versioning policy |
| [`docs/ADR.md`](docs/ADR.md) | Accepted architecture decisions, consequences, and reconsideration conditions |

## Implementation Entry Point

Implementation begins with `T1.1` in [`TASKS.md`](TASKS.md).

For each task:

1. read `/AGENTS.md` and all task references;
2. verify dependencies;
3. satisfy every acceptance criterion;
4. add tests and operational evidence;
5. update affected documents and changelog;
6. complete the Definition of Done;
7. mark the task complete only after verification.

## Engineering Principles

- Documentation before implementation
- Deterministic controls around probabilistic AI
- Reproducibility before optimization
- `Decimal` arithmetic for monetary values
- Timezone-aware UTC timestamps
- Idempotent external side effects
- Safe defaults and explicit feature flags
- Complete auditability and decision lineage
- PostgreSQL as system of record; Redis is ephemeral
- Append-only ledger as financial source of truth
- No secrets in source control, logs, metrics, or prompts
- No profitability claims without statistically valid evidence
- Fail closed when data, policy, precision, accounting, or integrity is uncertain

## Documentation and Implementation Status

The design specification is complete enough to begin task-by-task MVP implementation. It intentionally does not pretend that generated implementation artifacts already exist.

The following must be created and maintained with code:

- dependency lock files;
- generated OpenAPI schemas and endpoint inventory;
- Alembic migrations and exact SQL schema;
- exact implemented indicator and fill formulas with fixtures;
- Prometheus metric names, alert rules, and Grafana provisioning files;
- Gemini evaluation datasets and baseline reports;
- container image digests and SBOMs;
- measured performance, restore, RPO, and RTO evidence.

See [`docs/DOCUMENTATION_AUDIT.md`](docs/DOCUMENTATION_AUDIT.md) for the latest audit.

## Disclaimer

This project is for research and engineering experimentation. It does not provide financial advice and does not guarantee profitability. Cryptocurrency markets are volatile and may cause complete loss of capital.
