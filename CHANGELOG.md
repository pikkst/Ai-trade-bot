# Changelog

All notable project changes are documented here.

## Unreleased

### Documentation Audit and Specification Expansion — 2026-07-31

#### Added

- Root `AGENTS.md` as the authoritative implementation guide for AI coding agents and human contributors.
- `docs/GEMINI_INTEGRATION.md` as the provider-specific Google Gemini API specification.
- `docs/DOCUMENTATION_AUDIT.md` for coverage, consistency rules, known implementation-dependent details, and future audit procedure.
- Detailed product requirements with requirement identifiers, user journeys, non-functional requirements, experiment definition, success metrics, and MVP Definition of Done.
- Expanded C4-style architecture, decision flow, state machines, transaction boundaries, data ownership, idempotency, deployment topology, and failure policy.
- Detailed backend package, layering, configuration, dependency-injection, persistence, queue, Gemini, Binance, error, logging, authentication, testing, and prohibited-pattern rules.
- Detailed REST API contract covering workspaces, configuration versions, market data, features, Gemini analysis, strategy, risk, portfolios, orders, backtests, experiments, audit, jobs, errors, pagination, idempotency, and OpenAPI verification.
- Detailed logical database schema covering identity, configuration, market data, features, Gemini analysis, strategy, risk, execution, portfolio, backtesting, experiments, audit, outbox, retention, indexes, and migration rules.
- Expanded runtime AI-agent responsibilities, prompt contracts, prompt-injection protections, versioning, evaluation, fallback, and audit requirements.
- Expanded market-data, strategy, risk, paper-execution, portfolio-accounting, and backtesting specifications.
- Expanded security threat model, secrets lifecycle, provider safety, financial controls, supply-chain controls, incident response, recovery, privacy, and release gates.
- Expanded testing strategy with domain matrices, property invariants, provider policies, E2E flows, resilience, performance, security tooling, coverage, and release gates.
- Expanded observability specification with structured events, metric categories, dashboards, alert severity, runbooks, and health behavior.
- Expanded deployment specification with environment separation, service topology, migration workflow, backups, rollback, promotion gates, resource management, and release artifacts.
- Expanded roadmap with gated phases from documentation through paper experiment and future Binance test-environment assessment.
- Expanded architecture decision records for Gemini, paper-first progression, ledger, stack, Binance native interfaces, finalized candles, shared contracts, configuration freezing, and fail-closed behavior.
- Expanded contribution workflow and pull-request requirements.

#### Changed

- Google Gemini API is now the required cloud AI provider for version 1.
- OpenAI is removed from the version 1 implementation plan.
- The official `google-genai` SDK is required behind a project-owned provider protocol.
- Runtime AI remains advisory and cannot bypass deterministic strategy, risk, execution, or reconciliation.
- README documentation inventory was aligned with real repository files.
- `TASKS.md` was converted from a shallow checklist into independently implementable task cards with description, user story, acceptance criteria, Definition of Done, dependencies, references, and notes.
- Python stack choices were resolved to ARQ and Polars for the MVP.
- Live trading, private Binance order placement, leverage, futures, margin, shorting, withdrawals, and custody remain outside MVP scope.
- Active Gemini quotas and rate limits are treated as environment/project configuration observed from Google AI Studio rather than hardcoded documentation values.
- Standard backtests no longer call live Gemini by default; they disable AI or use immutable precomputed validated reports.

#### Fixed

- Removed provider ambiguity between OpenAI, Gemini, and local models in MVP documentation.
- Removed ambiguity between root `/AGENTS.md` coding-agent rules and `docs/AGENTS.md` runtime-agent design.
- Fixed conflicts between strategy sizing, risk sizing, and order creation authority.
- Fixed unclear source-of-truth rules by making PostgreSQL authoritative and Redis ephemeral.
- Fixed accounting ambiguity by defining the append-only double-entry ledger as the financial source of truth.
- Fixed simulation ambiguity by requiring explicit fee, spread, slippage, precision, minimum-notional, partial-fill, and intrabar rules.
- Fixed experiment mutability by requiring frozen versioned configuration.
- Fixed failure ambiguity by defining fail-closed and halt behavior for stale data, provider failure, missing policy, precision failure, database failure, and reconciliation mismatch.
- Fixed audit gaps by requiring complete lineage from market snapshot and Gemini request to strategy, risk, order, fill, ledger, and report.

## 0.1.0 — Documentation Baseline

- Added initial product vision and MVP boundaries.
- Added initial architecture, backend, API, and database summaries.
- Added initial AI, agents, and prompt summaries.
- Added initial market data and Binance integration design.
- Added initial strategy, risk, portfolio, paper trading, and backtesting design.
- Added initial security, testing, deployment, observability, and technology documentation.
- Added initial implementation roadmap and task backlog.
