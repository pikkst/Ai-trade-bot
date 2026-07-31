# Changelog

All notable project changes are documented here.

## Unreleased

### The Daily Roast AI Brand Foundation — 2026-07-31

#### Added

- `docs/BRAND_GUIDELINES.md` defining the official product identity, positioning, voice, visual direction, financial-claim restrictions, and domain strategy.
- `docs/PRODUCT_VISION.md` defining the long-term evidence-driven market-intelligence product vision and future multi-market direction.
- `docs/MISSION_AND_VALUES.md` defining mission, values, behavioral commitments, and decision tests.
- `docs/DESIGN_PRINCIPLES.md` defining trust, accessibility, evidence, uncertainty, risk, simulation, and interface principles.
- `docs/NAMING_CONVENTIONS.md` defining product, code, API, database, event, environment, and documentation naming rules.
- `docs/BRAND_FOUNDATION_AUDIT.md` documenting Sprint 1 consistency findings and remaining migration work.

#### Changed

- The official product name is now **The Daily Roast AI**.
- The official tagline is **Evidence-Driven Market Intelligence**.
- `thedailyroast.online` is the primary product domain, with approved `app`, `api`, `docs`, `status`, and future `admin` subdomains.
- README now presents the repository as an evidence-driven market-intelligence platform rather than a generic trading bot.
- Product requirements now include brand, content, trust, provenance, simulation-labeling, and future multi-market requirements.
- `AGENTS.md` now requires brand-safe user-facing copy, approved naming, and explicit review of risk, uncertainty, freshness, and simulation labels.
- Roadmap now includes brand governance, public custom-domain launch, product-interface modules, post-experiment product review, and future multi-market research expansion.

#### Fixed

- Removed the legacy product title `AI Trade Bot` from the primary README and product requirements.
- Clarified that `Ai-trade-bot` is only a technical repository identifier.
- Added explicit prohibition of guaranteed-return, deceptive urgency, fear-of-missing-out, and hype-driven financial language.
- Added a clear distinction between analytical confidence and probability of profit.

### Local Development, Testing, and Production Development — 2026-07-31

#### Added

- `docs/LOCAL_DEVELOPMENT.md` with local tools, Supabase CLI workflow, environment profiles, stable commands, seed data, debugging, Windows support, and local Definition of Done.
- `docs/TEST_ENVIRONMENTS.md` with environment matrix, test pyramid, fixtures, CI workflows, provider policy, recovery tests, and promotion gates.
- `docs/PRODUCTION_DEVELOPMENT.md` with staging, production research, CI/CD, security, privacy, backup, SLO, cost, incident, and launch requirements.
- `LOCAL_AND_PRODUCTION_TASKS.md` with independently implementable local, test, staging, production research, and post-launch task cards.

#### Changed

- README describes the complete lifecycle from local development through production research.
- `AGENTS.md` defines environment-specific rules for local, CI, demo, paper, staging, and production research.
- `docs/TESTING.md` uses local Supabase, fake providers, one-shot research cycles, RLS tests, frontend tests, and recovery gates.
- `docs/DEPLOYMENT.md` defines local, CI, demo, paper, staging, and production research promotion paths.
- `ROADMAP.md` includes local foundation, automated testing, cloud demo, post-experiment review, staging, production readiness, production research launch, and measured reliability evolution.
- Production development is explicitly defined as production-quality research and paper trading, not automatic live trading.

#### Fixed

- Removed ambiguity about how development continues after the free cloud example.
- Removed ambiguity between local database/Auth testing and cloud deployment.
- Added explicit Windows 11 local-development requirements.
- Added required migration, RLS, frontend-secret, export, restore, staging, and protected production deployment tests.
- Added a clear separation between demo, formal paper experiment, staging, production research, Binance sandbox, and live-trading assessment.

### Free Cloud MVP Architecture — 2026-07-31

#### Added

- `docs/FREE_CLOUD_ARCHITECTURE.md` as the authoritative zero-cost deployment profile.
- `docs/FREE_CLOUD_REQUIREMENTS.md` as the free-cloud PRD refinement.
- `CLOUD_MVP_TASKS.md` with detailed Supabase, GitHub Actions, Render, Cloudflare Pages, RLS, backup, and experiment-start tasks.
- Supabase/Auth, external scheduler, research-cycle lock, and free-tier feature flags in `.env.example`.

#### Changed

- The first 30-day experiment uses Cloudflare Pages, Render Free, a dedicated Supabase Free project, GitHub Actions, Gemini free allowance, and Binance Spot REST.
- Runtime execution uses a one-shot idempotent research-cycle CLI instead of a mandatory persistent queue worker.
- PostgreSQL advisory locking or durable database leases replace Redis locking for the free-cloud profile.
- Binance REST finalized-candle polling replaces mandatory persistent WebSocket ingestion for MVP.
- Hosted Prometheus and Grafana are deferred; free-tier observability uses structured logs and persistent cycle, audit, freshness, halt, and reconciliation records.

#### Fixed

- Removed Redis and ARQ as initial cloud requirements.
- Removed the requirement for a continuously running local computer.
- Clarified that the existing Eventnexus Supabase project must not be reused.
- Clarified browser Data API restrictions and deny-by-default RLS.
- Clarified that free tiers provide no production SLA.

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
