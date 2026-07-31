# The Daily Roast AI — Naming Conventions

Last reviewed: 2026-07-31
Status: Authoritative naming specification

## 1. Purpose

This document defines naming rules for product language, repositories, code, APIs, database objects, configuration, environments, metrics, logs, documentation, and user-facing modules.

## 2. Product Name

Official product name:

> The Daily Roast AI

Approved short form:

> Daily Roast AI

Legacy technical references such as `Ai-trade-bot` may remain only where changing them would require a separate repository or infrastructure migration.

## 3. Product Descriptor

Primary descriptor:

> Evidence-Driven Market Intelligence Platform

Approved alternatives:

- AI-Assisted Market Research Platform
- Crypto Research and Paper-Trading Platform

## 4. Domain Names

- `thedailyroast.online` — landing page;
- `app.thedailyroast.online` — application;
- `api.thedailyroast.online` — backend API;
- `docs.thedailyroast.online` — documentation;
- `status.thedailyroast.online` — future status page;
- `admin.thedailyroast.online` — future restricted administration interface.

## 5. Environment Names

Use the following canonical environment identifiers:

- `local`
- `test`
- `ci`
- `demo`
- `paper`
- `staging`
- `production-research`
- `binance-sandbox`

Do not use `production` alone where it could be confused with live trading.

## 6. Execution Modes

Canonical values:

- `research`
- `paper`
- `sandbox`
- `live`

The `live` value is reserved and must remain disabled until separately approved.

## 7. User-Facing Module Names

Approved module names:

- Today's Roast
- Markets
- Research
- Portfolio
- Strategies
- Backtesting
- Paper Trading
- Reports
- Alerts
- Audit
- Settings
- Labs

Use title case in navigation and headings.

## 8. Backend Package Naming

Python packages, modules, functions, and variables use `snake_case`.

Classes and Pydantic models use `PascalCase`.

Constants use `UPPER_SNAKE_CASE`.

Examples:

```text
market_data
RiskEvaluation
run_research_cycle
MAX_RETRY_ATTEMPTS
```

## 9. Frontend Naming

React components use `PascalCase`.

Hooks use `useCamelCase`.

Variables and functions use `camelCase`.

Route segments use lowercase kebab-case.

Examples:

```text
MarketSummaryCard
usePortfolioStatus
analysisReport
/paper-portfolios/:portfolioId
```

## 10. API Naming

- Base path: `/api/v1`
- Resources use plural kebab-case nouns.
- Commands use explicit action subresources only where normal resource semantics are insufficient.
- Query parameters use `snake_case` unless generated client standards require otherwise.
- JSON properties use `snake_case` for backend consistency.

Examples:

```text
/api/v1/market-snapshots
/api/v1/paper-portfolios/{portfolio_id}/halt
/api/v1/research-cycles
```

## 11. Database Naming

PostgreSQL schemas, tables, columns, constraints, and indexes use lowercase `snake_case`.

Tables use plural nouns.

Primary keys use `id`.

Foreign keys use `<entity>_id`.

Timestamps use explicit suffixes:

- `created_at`
- `updated_at`
- `started_at`
- `completed_at`
- `occurred_at`

Examples:

```text
market_snapshots
risk_evaluations
paper_orders
portfolio_id
uq_candles_exchange_symbol_interval_open_time
idx_audit_events_occurred_at
```

## 12. Event Names

Domain and audit event names use lowercase `snake_case` past-tense or completed-state language.

Examples:

- `market_snapshot_created`
- `ai_analysis_rejected`
- `risk_evaluation_approved`
- `paper_order_filled`
- `portfolio_halted`
- `ledger_reconciliation_failed`

## 13. Error Codes

Error codes use lowercase `snake_case` and remain stable across API, logs, tests, and documentation.

Examples:

- `validation_error`
- `stale_data`
- `provider_rate_limited`
- `risk_rejected`
- `reconciliation_failed`

## 14. Metrics

Prometheus-style metrics use the prefix:

`daily_roast_ai_`

Counters end in `_total`.

Durations use seconds.

Examples:

- `daily_roast_ai_research_cycles_total`
- `daily_roast_ai_gemini_request_duration_seconds`
- `daily_roast_ai_reconciliation_failures_total`

## 15. Environment Variables

Environment variables use uppercase `UPPER_SNAKE_CASE` and a clear subsystem prefix.

Examples:

- `APP_ENV`
- `DATABASE_URL`
- `SUPABASE_URL`
- `GEMINI_API_KEY`
- `RISK_MAX_POSITION_PERCENT`
- `PAPER_INITIAL_CASH_EUR`

Public frontend variables must use the `VITE_` prefix.

## 16. Git Branches

Preferred branch patterns:

- `feat/<task-id>-short-description`
- `fix/<task-id>-short-description`
- `docs/<task-id>-short-description`
- `chore/<task-id>-short-description`

Examples:

- `docs/s1-brand-foundation`
- `feat/t3-2-binance-rest-adapter`
- `fix/t7-5-drawdown-halt`

## 17. Commit Messages

Use concise conventional-style prefixes:

- `feat:`
- `fix:`
- `docs:`
- `test:`
- `refactor:`
- `chore:`
- `security:`

Messages should describe the outcome, not the editing process.

## 18. Task IDs

Task IDs are immutable once published.

Current namespaces:

- `T` — shared implementation tasks;
- `C` — free-cloud MVP tasks;
- `L` — local development and test tasks;
- `P` — production research tasks;
- `S` — documentation sprint tasks.

## 19. Version Names

Use semantic versions for releases where practical.

Versioned domain artifacts must include explicit versions:

- prompt version;
- report schema version;
- feature-set version;
- strategy version;
- risk-policy version;
- execution-model version;
- experiment configuration version.

## 20. Financial Terms

Use precise terms:

- `paper_order`, not `trade`, when no fill exists;
- `paper_fill`, not `execution`, when simulated;
- `virtual_cash`, not `cash`, in user-facing simulation contexts;
- `simulated_pnl`, not `profit`, unless clearly qualified;
- `market_analysis`, not `prediction`, unless a forecast is explicitly defined.

## 21. AI Terms

Use:

- Gemini analysis;
- validated AI report;
- confidence score;
- evidence reference;
- contradiction;
- missing information;
- provider status.

Do not use:

- guaranteed prediction;
- AI certainty;
- winning signal;
- autonomous trader.

## 22. Documentation File Names

Authoritative Markdown specification files use uppercase snake case:

```text
BRAND_GUIDELINES.md
PRODUCT_VISION.md
MISSION_AND_VALUES.md
```

Generated documentation may use lowercase kebab-case when tool conventions require it.

## 23. Deprecated Names

The following names are deprecated for user-facing use:

- AI Trade Bot
- Crypto Bot
- Trading Bot
- AI Crypto Research Platform

Historical references may remain in changelogs or repository metadata until migrated.

## 24. Review Checklist

Before introducing a new name:

- confirm it does not conflict with an existing domain term;
- confirm casing and pluralization;
- confirm API and database implications;
- confirm user-facing clarity;
- confirm no implication of guaranteed performance or regulatory status;
- update this document when the name becomes canonical.

## 25. Related Documents

- `BRAND_GUIDELINES.md`
- `PRODUCT_VISION.md`
- `DESIGN_PRINCIPLES.md`
- `API_SPECIFICATION.md`
- `DATABASE_SCHEMA.md`
- `OBSERVABILITY.md`
- `../AGENTS.md`
