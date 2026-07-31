# Technology Stack

Last reviewed: 2026-08-01  
Status: Authoritative technology selection mapped to `M001–M036`

## 1. Selection Principles

Technology is selected to support:

- deterministic local development and CI;
- project-owned domain boundaries;
- strict typing and schema generation;
- append-only accounting and relational integrity;
- safe cloud operation without a local computer;
- bounded provider use and graceful degradation;
- Windows 11 plus one Unix-like development path;
- evidence-based evolution rather than speculative infrastructure.

A library, hosted service, or runtime is not active merely because it appears in a future specification. `TASKS.md` and `docs/TASK_CATALOG_INDEX.md` define when it may be implemented.

## 2. Required Application Stack

### Backend — M001–M013, M014

- Python 3.12;
- FastAPI;
- Pydantic v2 and Pydantic Settings;
- SQLAlchemy 2;
- Alembic and/or Supabase migration tooling under one immutable migration policy;
- PostgreSQL driver selected and locked during M002;
- Polars for approved analytical calculations;
- Python `Decimal` for financial values;
- project-owned protocols for exchange, AI, persistence, clock, IDs, scheduling, export, and observability.

### Frontend — M004, M015–M025

- React;
- TypeScript strict mode;
- Vite;
- React Router;
- TanStack Query;
- project-selected component/test/accessibility tooling locked in M004;
- generated project-owned API types where practical;
- versioned design tokens and localization keys.

### Data and Auth — M003

- Supabase PostgreSQL;
- Supabase Auth;
- PostgreSQL Row Level Security;
- additive immutable migrations;
- deterministic seed and local reset workflows.

### Market and AI Providers — M006–M009

- Binance Spot public REST;
- Google Gemini API through the official `google-genai` SDK;
- deterministic fake Binance and Gemini providers for normal tests;
- no private Binance SDK/order endpoint in M001–M036.

## 3. Required Development and Quality Tooling

Selected and locked during M001–M002:

- committed Python and Node lock files;
- Ruff;
- MyPy strict;
- Pytest;
- Hypothesis;
- frontend lint, type, unit, accessibility, visual, E2E, and production-build tools;
- Bandit;
- Semgrep;
- dependency review/audit tooling;
- secret scanning;
- Trivy for filesystem/container artifacts when applicable;
- SBOM generation before production-research promotion;
- documentation link, ID, task, OpenAPI, schema, and generated-artifact checks.

Third-party GitHub Actions, images, and tool versions are pinned. Repository commands are reused by local development and CI.

## 4. Local Development Profile — M001–M006

- local Supabase CLI/PostgreSQL/Auth;
- fake providers by default;
- no cloud Supabase project required;
- no paid provider required;
- stable cross-platform command runner;
- Docker Desktop/Compose only where required by local Supabase or selected tooling;
- Windows PowerShell and Unix-like command documentation.

## 5. Free-Cloud Deployment Profile — M028

- Supabase Free: managed PostgreSQL and Auth;
- Render Free Web Service: FastAPI reads and explicit commands;
- Cloudflare Pages Free: static React/Vite frontend;
- GitHub Actions: CI and best-effort one-shot cycle schedule;
- GitHub artifacts or approved storage plus PostgreSQL records for diagnostics/exports where appropriate;
- Binance Spot public REST;
- bounded Gemini use.

M026 and M027 must be verified before M028. The first cloud profile does not require a paid service or continuously running local computer.

## 6. Controlled Experiment Profile — M029

The formal experiment uses the M028 stack plus:

- exact frozen configuration and behavior-set hashes;
- persistent cycle/stage/audit/incident/reconciliation records;
- current export and restore evidence;
- explicit request/token/cost budgets;
- owner-approved preflight and lifecycle controls;
- cash and buy-and-hold benchmarks.

## 7. Staging and Production Research — M035–M036

Technology selections are based on measured M030 evidence and M034 change governance.

Possible production choices include:

- upgraded Supabase or another managed PostgreSQL profile;
- connection pooling appropriate to measured load;
- persistent worker/queue if measured cycle/backtest needs justify it;
- managed object storage for exports/reports/backups;
- managed logs, metrics, tracing, incident routing, and status infrastructure;
- paid always-on API hosting;
- automated encrypted backups and recovery features.

Production research remains paper-only.

## 8. Required Runtime Components

Active in M001–M036:

- FastAPI;
- one-shot research-cycle CLI;
- React frontend;
- PostgreSQL/Auth;
- Binance public REST;
- Gemini advisory adapter and fake provider;
- database lock/lease;
- append-only ledger and reconciliation;
- structured logs and persistent operational evidence;
- GitHub Actions external scheduling for the initial cloud profile.

## 9. Deferred Runtime Components

Not mandatory unless M030 evidence and M034 approval activate them:

- Redis;
- ARQ or another durable queue;
- persistent workers;
- Binance WebSocket ingestion;
- hosted Prometheus/Grafana;
- OpenTelemetry collector/backend;
- Kubernetes;
- paid/high-availability infrastructure;
- automatic scaling.

Domain and application commands must remain reusable if a future adapter is added.

## 10. Future-Assessment Technology

Outside M001–M036:

- private Binance credentials or order APIs;
- Binance test execution;
- live-capital execution;
- custody/withdrawal infrastructure;
- leverage, margin, derivatives, options, or shorting infrastructure.

These require a separate approved milestone in addition to ordinary M034 governance.

## 11. Data and Scheduling

PostgreSQL is authoritative.

The initial schedule uses:

- one-shot CLI;
- GitHub Actions best-effort occurrence;
- PostgreSQL advisory lock or durable lease;
- deterministic idempotency;
- Binance REST finalized-candle polling;
- bounded checkpointed gap repair.

A delayed schedule uses actual eligible market data. A missed cycle does not create imagined trades.

## 12. Authentication and Browser Access

- Supabase Auth supplies identity;
- FastAPI/application services enforce command authorization;
- RLS provides a second deny-by-default boundary;
- browser access is limited to Auth and approved read views/APIs;
- browser direct writes to critical financial/control tables are prohibited;
- no unrelated custom password or JWT signing subsystem is part of the active profile;
- frontend bundles contain only explicitly allowlisted public values.

## 13. AI Technology Rules

- Gemini is advisory only;
- structured output uses project-owned Pydantic/JSON Schema contracts;
- provider SDK types remain in infrastructure;
- normal CI uses deterministic fakes;
- prompt, schema, safety, validation, fallback, usage, and cost are versioned;
- no Gemini execution, shell, database, exchange, search, or code tools are enabled;
- default formal-experiment Gemini monthly cost budget is EUR 0 unless explicitly approved;
- provider/model changes use M034 governance.

## 14. Supply Chain and Generated Contracts

Implementation must produce and verify:

- dependency lock hashes;
- pinned tool/action/image versions;
- deterministic OpenAPI;
- generated frontend types;
- migration manifest and head;
- schema/error/event/permission/metric catalogs as their Master Tasks are implemented;
- SBOM and release provenance before production research;
- generated-artifact drift detection.

Provider SDK types must not become public project contracts.

## 15. Free-Tier and Provider Caveats

Free services may:

- sleep or pause;
- restart;
- throttle;
- delay scheduled work;
- change quotas, terms, retention, or availability.

The system must degrade safely and never claim an SLA for the free profile.

Current provider quotas, pricing, terms, and model status are verified from approved current evidence before deployment and experiment start. Prose documentation is not the source of truth for a numeric quota.

No plan is purchased, upgraded, or scaled automatically.

## 16. Technology Change Gate

A material technology change requires:

- M034 change proposal;
- complete before/after behavior-set and dependency impact;
- ADR;
- compatibility and migration plan;
- security/privacy/data/accessibility review as applicable;
- cost, quota, and capacity evidence;
- tests and resilience/recovery evidence;
- staged paper verification and stop conditions;
- rollback or forward-fix plan;
- owner approval.

## 17. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `GEMINI_INTEGRATION.md`
- `TESTING.md`
- `SECURITY.md`
