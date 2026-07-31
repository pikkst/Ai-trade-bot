# The Daily Roast AI Roadmap

Last reviewed: 2026-08-01  
Status: Gated product and engineering evolution plan mapped to `TASKS.md`

## Roadmap Rules

- `TASKS.md` is the only implementation-order authority.
- This roadmap describes outcomes and promotion gates, not an alternative backlog.
- Detailed task catalogs do not override Master Task dependencies.
- Evidence and safety gates are more important than dates.
- Gemini remains advisory.
- Production research remains paper-only.
- Live trading and private Binance execution are not authorized.
- No phase advances solely because a backtest or paper experiment was profitable.

## Phase 0 — Documentation Synchronization

**Master-plan status:** documentation complete; implementation not started.

Completed documentation outcomes:

- official product identity and brand foundation;
- product, architecture, domain, UX, security, testing, deployment, and operations specifications;
- Sprint 3–19 detailed workspace catalogs;
- Sprint 20 task-system synchronization;
- one canonical Master Task 1–36 sequence;
- active free-cloud architecture aligned around Supabase, REST, one-shot CLI, GitHub Actions, Render, and Cloudflare Pages;
- Redis, ARQ, persistent workers, WebSocket ingestion, hosted Prometheus/Grafana, private Binance, and live trading deferred.

**Exit:** contributors start from `M001` without hidden architectural or dependency decisions.

## Phase 1 — Repository and Local Foundation

**Tasks:** `M001–M006`

Deliver:

- backend/frontend repository scaffold;
- locked Python and Node toolchains;
- stable cross-platform commands;
- baseline CI and security checks;
- local Supabase/PostgreSQL/Auth;
- additive migrations, deterministic seed data, and RLS;
- frontend design tokens and test foundation;
- typed settings, logs, errors, transactions, idempotency;
- project-owned provider protocols and deterministic fakes.

**Exit:** a clean checkout becomes a working local foundation on Windows and CI without cloud or paid credentials.

## Phase 2 — Core Research Domains

**Tasks:** `M007–M013`

Deliver:

- Binance Spot public REST metadata and finalized candles;
- data-quality validation, continuity checks, gap repair, corrections, and freshness;
- immutable snapshots and deterministic features;
- Gemini adapter, prompts, schemas, grounding, safety, retries, fallback, and budgets;
- deterministic strategy and risk;
- paper execution, append-only ledger, portfolio projection, rebuild, and reconciliation;
- idempotent one-shot research cycle;
- reproducible backtests and required benchmarks.

**Exit:** the entire paper-research domain flow works deterministically against fake providers and approved fixtures.

## Phase 3 — API and Product Workspaces

**Tasks:** `M014–M025`

Deliver:

- authenticated, versioned `/api/v1` contracts and deterministic OpenAPI;
- owner/operator/viewer authorization and RLS assurance;
- accessible application shell and component system;
- Today’s Roast dashboard;
- Market Evidence workspace;
- Gemini Analysis and Validation workspace;
- Strategy and Risk workspace;
- Portfolio, Execution, Ledger, and Reconciliation workspace;
- Backtest, Benchmark, Reproducibility, and Comparison workspace;
- Experiment Operations, Cycle, Incident, and Audit workspace;
- Auth, Governance, Security, Privacy, and Release workspace;
- onboarding, search, notifications, Trust Center, English/Estonian localization;
- developer portal, documentation health, runbooks, and traceability.

**Exit:** users can inspect complete evidence and lineage through accessible, authorized, paper-only interfaces.

## Phase 4 — Local and CI Verification

**Tasks:** `M026–M027`

Deliver:

- deterministic full local demo;
- unit, property, migration, RLS, Auth, integration, provider contract, API contract, component, accessibility, visual, E2E, documentation, and security tests;
- no-secret and frontend-bundle checks;
- export, isolated restore, migration verification, ledger rebuild, and reconciliation;
- database/provider/interruption/duplicate/halt/recovery drills;
- release-blocking finding resolution and verified runbooks.

**Exit:** cloud deployment is unnecessary to prove correctness, security boundaries, and recoverability.

## Phase 5 — Free-Cloud Demo

**Task:** `M028`

Deliver:

- dedicated Supabase project separate from Eventnexus;
- controlled migrations, Auth, RLS, and read models;
- scheduled/manual GitHub Actions one-shot cycle;
- Render FastAPI deployment;
- Cloudflare Pages frontend deployment;
- HTTPS, domains, CORS, CSP, Auth redirects, environment separation, and secret isolation;
- public demo or approved authenticated paper environment;
- proof that Render cold start does not control the scheduled cycle.

**Exit:** The Daily Roast AI runs in the cloud without the owner’s computer and without mandatory paid infrastructure.

## Phase 6 — Controlled 30-Day Paper Experiment

**Task:** `M029`

Frozen baseline:

- virtual EUR 20;
- BTC/EUR;
- finalized 1-hour candles;
- approximately hourly best-effort cycles;
- maximum position 25%;
- maximum order EUR 5;
- daily drawdown halt 5%;
- total drawdown halt 15%;
- maximum one open order;
- no leverage or shorting;
- Gemini cost budget EUR 0 by default;
- cash and buy-and-hold benchmarks.

Deliver:

- cloud observability and cycle status;
- export/restore evidence;
- exact configuration-hash preflight;
- owner approval and immutable start evidence;
- monitoring, incidents, pauses/halts, reconciliation, audit, and final report;
- no fabricated missed-cycle trades or hidden manual database repair.

**Exit:** the experiment reaches an auditable terminal state. Profit is not an exit criterion.

## Phase 7 — Evidence Hardening and Governance

**Tasks:** `M030–M034`

Deliver:

- measured performance, resilience, SLO, error-budget, capacity, quota, cost, and FinOps evidence;
- dataset/version registry, quality gates, lineage, retention, holds, archive/restore, and deletion/anonymization controls;
- hypothesis, evidence snapshot, robustness, untouched-test, paper-observation, reviewer, approval, promotion, rollback, and strategy lifecycle controls;
- alert routing, incident lifecycle, integrity verification, postmortems, corrective actions, and effectiveness review;
- behavior-set change proposals, risk classification, compatibility, evaluation plans, immutable approvals, staged paper canaries, stop conditions, rollback, emergency expiry, and deprecation.

**Exit:** reliability, cost, data, strategy, incident, and behavior-change claims are governed by evidence and human approval.

## Phase 8 — Post-Experiment Decision and Staging

**Task:** `M035`

Deliver:

- explicit owner decision to stop, repeat, improve, or advance;
- complete review of reliability, data, AI validity, strategy evidence, user comprehension, incidents, security, privacy, recovery, costs, and limitations;
- isolated production-like staging when advancement is approved;
- separate database, Auth, Gemini credentials, domains, storage, and deployment credentials;
- immutable production artifacts deployed unchanged;
- migration rehearsal, rollback/forward-fix, restore, E2E, load, failure, accessibility, security, privacy, content, and operational gates.

**Exit:** one release candidate passes production-like staging with complete approval evidence.

## Phase 9 — Production Research Service

**Task:** `M036`

Deliver:

- protected CI/CD and manual approvals;
- controlled migration and immutable deployment evidence;
- hardened account/session/access controls;
- managed backups and tested restore;
- measured SLOs, incident routing, status communication, support, and runbooks;
- privacy and data policies;
- cost and capacity governance;
- periodic security, access, recovery, model/prompt, strategy, documentation, and change reviews;
- authenticated market research, backtests, audit history, and paper portfolios.

**Exit:** stable production-grade research and paper-trading operation with current evidence and live trading disabled.

## Phase 10 — Multi-Market Research Assessment

Not part of `M001–M036` unless separately approved.

Potential adapters:

- equities;
- ETFs;
- foreign exchange;
- commodities;
- macroeconomic indicators.

Each market requires separate product requirements, licensing/terms review, session/calendar models, corporate-action handling where applicable, risk assumptions, data-quality rules, ADR, tasks, and approval.

## Phase 11 — Reliability and Capacity Evolution

Future architecture changes use `M034` change governance and measured `M030` evidence.

Possible changes:

- paid always-on API or worker hosting;
- Redis/ARQ or another durable queue;
- persistent exchange streams;
- managed observability;
- upgraded PostgreSQL/backups;
- high-availability architecture.

Free tiers must never be represented as permanent production capacity.

## Phase 12 — Binance Test Environment Assessment

Not authorized by this roadmap.

Requires a separate milestone for:

- private test credentials;
- credential threat model;
- exchange order/reconciliation contracts;
- capital and loss limits even in test mode;
- incident and emergency disablement;
- independent security and accounting review;
- owner approval.

## Phase 13 — Real-Capital Assessment

Not authorized.

Requires separate legal, exchange-eligibility, tax, security, financial-risk, accounting, operational, loss-limit, independent-review, and owner-approval work. No current task or phase may silently create a live-order path.

## Task Source Policy

- [`TASKS.md`](TASKS.md) — canonical Master Task 1–36 sequence and dependencies;
- [`docs/IMPLEMENTATION_EXECUTION_PLAN.md`](docs/IMPLEMENTATION_EXECUTION_PLAN.md) — task governance and completion model;
- `UX_DESIGN_TASKS.md`, `CLOUD_MVP_TASKS.md`, `LOCAL_AND_PRODUCTION_TASKS.md`, and `SPRINT_3_TASKS.md` through `SPRINT_20_TASKS.md` — detailed acceptance catalogs used only through their mapped master tasks.
