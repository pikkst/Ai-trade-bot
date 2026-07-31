# Changelog

All notable project changes are documented here.

## Unreleased

### Free Cloud MVP Architecture — 2026-07-31

#### Added

- `docs/FREE_CLOUD_ARCHITECTURE.md` as the authoritative zero-cost deployment profile.
- `CLOUD_MVP_TASKS.md` with detailed Supabase, GitHub Actions, Render, Cloudflare Pages, RLS, backup, and experiment-start tasks.
- Supabase/Auth, external scheduler, research-cycle lock, and free-tier feature flags in `.env.example`.

#### Changed

- The first 30-day experiment now uses Cloudflare Pages, Render Free, a dedicated Supabase Free project, GitHub Actions, Gemini free allowance, and Binance Spot REST.
- Runtime execution now uses a one-shot idempotent research-cycle CLI instead of a mandatory persistent queue worker.
- PostgreSQL advisory locking/database leases replace Redis locking for the free-cloud profile.
- Binance REST finalized-candle polling replaces mandatory persistent WebSocket ingestion for MVP.
- Hosted Prometheus and Grafana are deferred; free-tier observability uses structured logs and persistent cycle/audit/freshness/halt/reconciliation records.
- Render hosts only FastAPI; scheduled execution remains independent of Render cold starts and idle spin-down.
- README, architecture, backend, deployment, technology stack, ADRs, roadmap, and environment configuration were aligned with the free-cloud profile.

#### Fixed

- Removed the requirement for Redis and ARQ from the initial cloud deployment.
- Removed the requirement for a continuously running scheduler/worker and local computer.
- Clarified that the existing Eventnexus Supabase project must not be reused.
- Clarified browser Data API restrictions and deny-by-default RLS requirements.
- Clarified that free tiers provide no production SLA and may sleep, pause, throttle, restart, delay work, or change quotas.

### Documentation Audit and Specification Expansion — 2026-07-31

#### Added

- Root `AGENTS.md` for coding agents and contributors.
- `docs/GEMINI_INTEGRATION.md` for Google Gemini API.
- `docs/DOCUMENTATION_AUDIT.md` for consistency and coverage.
- Detailed requirements, architecture, API, database, AI, market, strategy, risk, execution, accounting, testing, security, observability, deployment, roadmap, ADR, and task specifications.

#### Changed

- Google Gemini API is the required V1 cloud AI provider.
- Runtime AI remains advisory.
- `TASKS.md` uses independently implementable task cards.
- Live trading and private Binance execution remain outside MVP.

## 0.1.0 — Documentation Baseline

- Added initial vision, architecture, backend, API, database, AI, trading, security, testing, deployment, observability, roadmap, and task documentation.
