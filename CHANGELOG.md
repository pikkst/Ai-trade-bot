# Changelog

All notable project changes are documented here.

## Unreleased

### M007 — Binance REST Market-Data Ingestion and Quality Controls — 2026-08-08

#### Added

- Additive Supabase/Alembic migration `20260808150000_m007_quality_state_governance` adding the `clock_drift_recovered` terminal vocabulary and scoping authenticated snapshot reads to workspace membership.
- Additive Supabase/Alembic migration `20260808160000_m007_terminal_resolution_idempotency` adding the structured `supersedes_event_id` column and a partial unique index `(supersedes_event_id, event_type)` so a blocker can never be superseded twice by the same terminal type.

#### Fixed

- Incremental fetch ranges are now aligned to finalized interval boundaries using trusted exchange time: a 1h fetch at a non-hour wall clock never expects a not-yet-finalized candle, and the start is floored to an interval.
- `detect_gaps` now requires explicit `expected_start`/`expected_end` boundaries; completeness is never inferred from whatever data exists, so an empty requested range and a missing leading candle are reported as gaps.
- The advisory-lock identity now matches the database ingestion identity (exchange, symbol version, interval, requested range, ingestion type — not the caller delivery key), so two workers requesting the same canonical range/type with different idempotency keys contend on the same lock.
- Clock-drift failures are scoped to the attempted range, and a later healthy server-time check appends `clock_drift_recovered` terminal evidence so one transient drift incident cannot block future fresh snapshots forever.
- The ingestion content hash is now derived from canonical accepted-content pairs ordered by open time (not page segmentation or operational counters), so an interrupted+resumed run and an uninterrupted run over the same logical range produce the identical hash.
- Quality evidence resolution is now append-only: repairing a gap or applying a correction inserts a terminal `gap_repaired`/`correction_applied` event linked to the original range/candle instead of rewriting prior evidence, and effective snapshot-gate state is derived from the event chain.
- Retry/attempt metadata for provider page calls is captured in `try/finally`, so exhausted-timeout and rate-limit failures persist the real counters instead of pre-call values.
- Snapshot creation is atomic: `INSERT ... ON CONFLICT (snapshot_hash) DO NOTHING RETURNING` with a follow-up lookup removes the check-then-insert race, and membership inserts are idempotent.
- Bandit B608 suppression is localized to the audited parameterized SQL builders: precisely placed `# nosec B608` comments on the exact flagged lines, and the `_resolve_quality_events` query was refactored to `event_type = any(:event_types)` so no dynamic placeholder list is assembled at all.
- The incremental preflight server-time provider call now runs with no active SQLAlchemy transaction (the symbol-binding read is committed first), and its failure persists a durable FAILED ingestion attempt with the real request/retry counters; a successful preflight's telemetry is carried into the resulting ingestion.
- Backfill rejects zero-length and inverted ranges and normalizes non-aligned boundaries to interval-aligned UTC boundaries so the expected open-time sequence is deterministic.
- Terminal quality resolution is correlated to the exact blocker via the structured `supersedes_event_id` column with valid transitions enforced (gap→gap_repaired, drift→clock_drift_recovered, correction→correction_applied); a wrong-category terminal event can no longer clear an unrelated blocker.
- Invalid candle evidence is scoped to the exact failed open-time/range so one malformed historical candle cannot block unrelated future snapshots; a valid candle at the same open time appends terminal resolution.
- A same-page inconsistent duplicate now fails the ingestion closed (scoped error event + FAILED status) instead of completing successfully, and `duplicate_conflict` is an explicit snapshot-gate blocker.
- The canonical ingestion content hash is built only at the exact acceptance points (inserted row, consistent duplicate, applied correction), so rejected content can never participate in the content identity.
- The advisory-lock release unlocks only the exact ingestion key after rolling back the aborted transaction, never unrelated session-level locks on the same pooled connection.
- The aggregate gap-repair hash is derived from the ordered child ingestion content hashes plus stable range metadata, so identical repairs replay to the same hash and different repairs over the same range differ.

#### Safety

- Authenticated users may only read snapshots of workspaces they belong to; cross-workspace snapshot and membership rows are invisible, verified by a negative RLS test.
- `app_workflow` no longer holds UPDATE on `data_quality_events`, enforcing append-only quality evidence.

### M003 — Local Supabase, Auth, Migrations, and RLS — 2026-08-01

#### Added

- Additive Supabase/Alembic migration chain, deterministic local seed, SQLAlchemy transaction boundary, Auth subject mapping, and owner/operator/viewer authorization foundation.
- Forced-RLS browser read model, trusted workflow/migration roles, and migration, role-matrix, write-denial, workspace-isolation, and rollback verification.

#### Fixed

- Moved local administrator membership out of the deployable migration chain and into the Supabase CLI's local-only `roles.sql` bootstrap.
- Replaced the request-facing `postgres` default with a dedicated `app_runtime` login that may assume only browser-equivalent roles and cannot assume workflow, migration, or service roles.
- Made Alembic trusted-role verification reject prohibited runtime/browser members without hard-coding a deployment-specific administrator name.

#### Safety

- The foundation remains local-first and paper-only; browser identities cannot write financial, configuration, membership, audit, or market-data tables, and hosted environments must provision dedicated principals outside the migration chain.

### M002 — Locked Toolchains and Baseline CI — 2026-08-01

#### Added

- Exact Python, Node, and npm selectors plus reproducible Python/frontend lock installation.
- Repository-owned baseline quality, dependency-audit, and documentation consistency commands for PowerShell and Make.
- Pytest branch coverage enforcement and Hypothesis coverage for deterministic lock normalization.
- Pull-request secret scanning, dependency review, and local Markdown/task-card validation.

#### Changed

- Pinned every GitHub Action to an immutable commit and every CI runner/tool selector to a non-floating version.
- Made normal CI explicitly fake-provider, paid-provider-disabled, private-exchange-disabled, and live-trading-disabled.

#### Safety

- CI creates no caches or artifacts containing environment files, logs, scan output, provider data, or credentials.

### M001 Review Fixes — 2026-08-01

#### Changed

- Upgraded Vite and its React plugin to versions that clear the enforced frontend dependency audit.
- Removed the unused React Router wrapper from the single-screen M001 scaffold; routing remains scheduled for M004 and will require a non-vulnerable release.
- Added an explicit Windows-only `colorama==0.4.6` lock input and cross-platform lock normalization.

#### Fixed

- Restored the fail-closed `npm audit --audit-level=moderate` security gate with zero accepted exceptions.
- Added Linux and Windows lock-drift verification for the same deterministic Python lock.

### Sprint 22 — Runtime Contract Synchronization — 2026-08-01

#### Added

- `SPRINT_22_TASKS.md` covering architecture, backend, technology, configuration, and observability alignment.
- Complete M001–M036 runtime/domain ownership in `docs/ARCHITECTURE.md` and `docs/BACKEND.md`.
- Runtime contract mapping in `docs/TASK_CATALOG_INDEX.md`.
- Durable cycle-stage, incident, export/restore, reconciliation, SLI/SLO, quota, cost, and capacity evidence requirements in `docs/OBSERVABILITY.md`.

#### Changed

- Expanded the modular-monolith package map to include experiments, research cycles, data governance, research review, incidents, changes, releases, and reporting.
- Clarified that a successful process exit is not cycle completion without required stages, atomic financial evidence, audit closure, and reconciliation.
- Reclassified technology as required, deferred, or future assessment and tied material technology changes to M030 evidence and M034 governance.
- Reworked `.env.example` into a safe deployment/bootstrap inventory with Supabase Auth as the identity source and immutable experiment behavior stored in PostgreSQL.
- Updated README, AGENTS, ROADMAP, execution governance, and the task catalog to make Sprint references future-safe.

#### Fixed

- Removed custom JWT/password settings that conflicted with the active Supabase Auth profile.
- Removed ambiguity between environment wiring/defaults and immutable running-experiment configuration.
- Added explicit false defaults for Redis, ARQ, persistent workers, WebSocket ingestion, automatic scaling/plan upgrades, private/test/live exchange execution, leverage/derivatives/shorting/custody/withdrawals, AI side-effect tools, and automatic approval/activation.
- Clarified that logs and provider dashboards are not substitutes for durable cycle, financial, incident, approval, or audit evidence.
- Clarified that hosted Prometheus, Grafana, and OpenTelemetry backends remain deferred rather than assumed complete.

#### Safety

- Preserved one-shot REST execution, deterministic idempotency and risk, append-only accounting, mandatory reconciliation, behavior-set freeze, no-auto-spend, and paper-only operation.

### Sprint 21 — Task Catalog and Lifecycle Synchronization — 2026-08-01

#### Added

- `docs/TASK_CATALOG_INDEX.md` mapping legacy `T*`, UX, cloud, local/production, and Sprint task IDs to M001–M036.
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
- Detailed requirements, architecture, API, database, AI, trading, security, testing, deployment, observability, roadmap, ADR, and task specifications.

#### Changed

- Google Gemini API is the required V1 cloud AI provider.
- Runtime AI remains advisory.
- Live trading and private Binance execution remain outside MVP.

## 0.1.0 — Documentation Baseline

- Added initial vision, architecture, backend, API, database, AI, trading, security, testing, deployment, observability, roadmap, and task documentation.
