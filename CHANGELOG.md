# Changelog

All notable project changes are documented here.

## Unreleased

### Sprint 21 — Task Catalog and Lifecycle Synchronization — 2026-08-01

#### Added

- `docs/TASK_CATALOG_INDEX.md` mapping legacy `T*`, UX, cloud, local/production, and Sprint 3–21 task IDs to M001–M036.
- `SPRINT_21_TASKS.md` documenting residual task-catalog and environment-lifecycle synchronization.
- Explicit classifications for mandatory, conditional, deferred, superseded, future-assessment, and documentation-complete work.

#### Changed

- Mapped `docs/TESTING.md` and `docs/TEST_ENVIRONMENTS.md` to Master Task promotion gates.
- Mapped `docs/DEPLOYMENT.md` to M026–M036, including M027 restore/security prerequisites for M028.
- Mapped `docs/FREE_CLOUD_ARCHITECTURE.md` and `docs/FREE_CLOUD_REQUIREMENTS.md` to M028 deployment and M029 controlled experiment.
- Mapped `docs/PRODUCTION_DEVELOPMENT.md` to M030–M036, with M035 staging and M036 production research.
- Updated README, AGENTS, ROADMAP, and the implementation execution plan to require the task catalog index when selecting detailed cards.
- Updated the documentation audit with Sprint 21 mappings, environment gates, and verified commits.

#### Fixed

- Removed residual ambiguity between a detailed file marked “Ready for implementation” and an eligible Master Task.
- Removed cloud tasks as a possible repository entry point; local/CI implementation and restore proof precede cloud provisioning.
- Standardized the lifecycle as M026 local verification, M027 recovery/security, M028 cloud deployment, M029 experiment, M030–M034 hardening/governance, M035 staging, and M036 production research.
- Classified historical Redis/ARQ, persistent-worker, WebSocket, and hosted-metrics tasks as deferred rather than mandatory.
- Preserved Binance test/private credentials and live-capital execution as separate future assessments.

#### Safety

- Preserved paper-only execution, deterministic non-bypassable risk, append-only accounting, mandatory reconciliation, no-auto-spend, environment isolation, and no private/live exchange path.

### Sprint 20 — Canonical Implementation Plan — 2026-08-01

#### Added

- `docs/IMPLEMENTATION_EXECUTION_PLAN.md` defining the sole implementation-order authority, execution stages, dependency rules, task status model, verification evidence, and project completion gate.
- `SPRINT_20_TASKS.md` documenting the repository-wide synchronization sprint.
- A canonical Master Task sequence from `M001` through `M036` covering repository foundation, domains, API/UI workspaces, verification, cloud deployment, the controlled experiment, governance, staging, and production research.

#### Changed

- Replaced the legacy root backlog with an authoritative `TASKS.md` master plan.
- Updated `AGENTS.md` so coding agents begin at `M001` and use detailed task catalogs only through mapped Master Tasks.
- Updated README to expose one implementation entry point and the active paper-only architecture.
- Updated ROADMAP so every implementation phase maps to Master Tasks rather than forming a competing backlog.
- Updated `docs/DOCUMENTATION_AUDIT.md` to correct the prior incomplete consistency conclusion and record verified synchronization evidence.
- Updated `docs/IMPLEMENTATION_EXECUTION_PLAN.md` to include Sprint 20 and the final M001–M036 task model.

#### Fixed

- Removed Redis, ARQ, persistent workers, Binance WebSocket ingestion, Prometheus, and Grafana from mandatory MVP task dependencies.
- Removed the conflict between the active one-shot free-cloud architecture and the former root task backlog.
- Removed ambiguous parallel task entry points across root, cloud, local/production, UX, and Sprint task files.
- Removed canonical local-to-cloud dependency cycles; local Supabase development no longer depends on creating a cloud project.
- Integrated Sprint 3–19 workspace catalogs into the root implementation sequence.
- Established that only `VERIFIED` implementation evidence marks a Master Task complete; documentation creation alone is not completion.

#### Safety

- Preserved paper-only execution, deterministic non-bypassable risk, append-only accounting, mandatory reconciliation, environment isolation, no-auto-spend, no private Binance credentials, and no live-trading authority.

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
- README presents the repository as an evidence-driven market-intelligence platform rather than a generic trading bot.
- Product requirements include brand, content, trust, provenance, simulation-labeling, and future multi-market requirements.
- `AGENTS.md` requires brand-safe user-facing copy, approved naming, and explicit review of risk, uncertainty, freshness, and simulation labels.
- Roadmap includes brand governance, public custom-domain launch, product-interface modules, post-experiment product review, and future multi-market research expansion.

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

- Removed ambiguity about how development continues after the free-cloud example.
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

- The first 30-day experiment uses Cloudflare Pages, Render Free, a dedicated Supabase Free project, GitHub Actions, Gemini bounded allowance, and Binance Spot REST.
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
- Live trading and private Binance execution remain outside MVP.

## 0.1.0 — Documentation Baseline

- Added initial vision, architecture, backend, API, database, AI, trading, security, testing, deployment, observability, roadmap, and task documentation.
