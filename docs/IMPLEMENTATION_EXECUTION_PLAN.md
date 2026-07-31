# Implementation Execution Plan and Documentation Synchronization

Last reviewed: 2026-08-01  
Status: Authoritative implementation-order and task-governance specification

## 1. Purpose

This document defines the single executable path for building The Daily Roast AI from an empty implementation repository to a verified production-grade research service.

The repository contains detailed domain specifications, UX workstreams, Sprint 3–19 workspace task files, cloud tasks, and local/production tasks. Those files remain authoritative for detailed acceptance criteria, but they do not independently define execution order. `TASKS.md` is the only canonical implementation sequence.

## 2. Problem Being Corrected

The previous task system contained valid detailed work but exposed several conflicting execution assumptions:

- `TASKS.md` still treated Redis, ARQ, persistent workers, WebSocket ingestion, Prometheus, and Grafana as MVP P0 requirements;
- the active architecture deliberately defers those systems until measured need and an accepted ADR;
- local, cloud, UX, and sprint task files could be read as parallel entry points;
- some supplemental dependencies were cyclic or environment-specific;
- Sprint 3–19 workspace tasks were not integrated into the root implementation sequence;
- the documentation audit claimed consistency while the root task backlog still contained superseded architecture.

This plan replaces those conflicting schedule assumptions without deleting the detailed specifications.

## 3. Canonical Authority

Implementation precedence is:

1. security, privacy, financial-integrity, and fail-closed requirements;
2. `AGENTS.md`;
3. `docs/PRODUCT_REQUIREMENTS.md`;
4. accepted architecture and ADRs;
5. domain and workspace implementation specifications;
6. `TASKS.md` for execution order and dependency gates;
7. detailed task cards referenced by the selected master task;
8. existing code conventions.

When a supplemental task file conflicts with `TASKS.md`, the dependency and scope in `TASKS.md` win. The conflict must be corrected during the selected task rather than silently implemented.

## 4. Active MVP Runtime Profile

The active implementation profile is:

- Python 3.12 modular monolith;
- FastAPI read/command API;
- one-shot research-cycle CLI;
- React, TypeScript, Vite frontend;
- Supabase PostgreSQL and Auth;
- Binance Spot public REST using finalized candles;
- Google Gemini through the official `google-genai` SDK;
- GitHub Actions as a best-effort external scheduler;
- Cloudflare Pages frontend and Render Free API for the first demo;
- database locks or leases and deterministic idempotency;
- append-only ledger and mandatory reconciliation;
- paper trading only.

The following are deferred and must not be introduced as mandatory MVP dependencies:

- Redis;
- ARQ or another persistent queue;
- persistent worker processes;
- Binance WebSocket ingestion;
- hosted Prometheus or Grafana;
- Kubernetes;
- private Binance credentials;
- Binance test trading;
- live trading.

A deferred component requires measured need, an ADR, a migration plan, updated tasks, tests, cost review, and owner approval.

## 5. Task Model

Each master task in `TASKS.md` contains:

- stable master ID;
- implementation outcome;
- required detailed workstreams;
- hard dependencies;
- required verification;
- completion gate;
- deferred or prohibited scope.

A master task is complete only when every referenced mandatory detailed card and acceptance criterion is implemented or explicitly marked not applicable with an approved reason.

## 6. Detailed Task Sources

### Core and environment catalogs

- `TASKS.md` — canonical master sequence;
- `UX_DESIGN_TASKS.md` — early UX/design implementation detail;
- `CLOUD_MVP_TASKS.md` — free-cloud deployment and experiment detail;
- `LOCAL_AND_PRODUCTION_TASKS.md` — local, testing, staging, and production-research detail.

### Workspace sprint catalogs

- `SPRINT_3_TASKS.md` — frontend application shell;
- `SPRINT_4_TASKS.md` — accessible component library;
- `SPRINT_5_TASKS.md` — Today’s Roast dashboard;
- `SPRINT_6_TASKS.md` — market evidence workspace;
- `SPRINT_7_TASKS.md` — strategy and risk workspace;
- `SPRINT_8_TASKS.md` — portfolio, execution, ledger, and reconciliation;
- `SPRINT_9_TASKS.md` — backtests, benchmarks, reproducibility, and comparison;
- `SPRINT_10_TASKS.md` — experiment operations and audit;
- `SPRINT_11_TASKS.md` — Gemini analysis and validation;
- `SPRINT_12_TASKS.md` — Auth, governance, security, privacy, and release readiness;
- `SPRINT_13_TASKS.md` — product shell, onboarding, search, notifications, Trust Center, and i18n;
- `SPRINT_14_TASKS.md` — developer portal, documentation health, and traceability;
- `SPRINT_15_TASKS.md` — performance, resilience, capacity, SLOs, quotas, and FinOps;
- `SPRINT_16_TASKS.md` — data lifecycle and dataset governance;
- `SPRINT_17_TASKS.md` — research review and strategy lifecycle;
- `SPRINT_18_TASKS.md` — incident response, postmortems, and learning;
- `SPRINT_19_TASKS.md` — governed behavior changes and staged rollout.

Sprint numbers are documentation-workstream identifiers, not permission to implement them before their master-task dependencies.

## 7. Implementation Stages

### Stage A — Repository and Local Foundation

Build the repository skeleton, locked toolchains, shared command runner, local Supabase stack, migrations, Auth/RLS baseline, frontend foundation, provider protocols, and deterministic fakes.

No cloud project or paid provider is required.

### Stage B — Core Research Domains

Implement finalized market data, quality controls, immutable snapshots, deterministic features, Gemini validation, strategy, risk, paper execution, ledger, reconciliation, and the one-shot research cycle.

### Stage C — API and Product Experience

Implement versioned read models and commands, OpenAPI, authorization, the application shell, accessible components, Today’s Roast, market evidence, Gemini, decisions/risk, portfolio, backtests, experiments, and audit views.

### Stage D — Verification and Local Completion

Complete property, integration, RLS, contract, E2E, accessibility, security, documentation, export, restore, recovery, and reproducibility gates.

A cloud deployment must not compensate for missing local verification.

### Stage E — Free-Cloud Demo and Controlled Experiment

Provision the dedicated Supabase project, deploy API/frontend, schedule the one-shot cycle, validate cold-start and free-tier behavior, perform export/restore, pass preflight, freeze configuration, and run the 30-day virtual EUR 20 experiment.

### Stage F — Research Review and Product Hardening

Complete experiment review, dataset governance, performance/FinOps evidence, incident controls, developer traceability, strategy lifecycle review, and change-management controls.

### Stage G — Staging and Production Research

Deploy immutable artifacts to isolated staging, rehearse migrations, pass production-readiness gates, then launch an authenticated paper-research service. Live trading remains disabled.

## 8. Dependency Rules

- local Supabase does not depend on a cloud Supabase project;
- provider fakes precede normal provider integration tests;
- domain contracts precede UI workspaces that consume them;
- ledger and reconciliation precede final portfolio and experiment status;
- the one-shot CLI precedes scheduled cloud execution;
- local and CI gates precede the formal cloud experiment;
- restore evidence precedes experiment start and production promotion;
- performance, SLO, cost, and capacity claims require measured evidence;
- strategy promotion requires backtest, untouched-test, robustness, reproducibility, paper observation, and owner review;
- behavior activation applies only to future configurations and never mutates a running experiment.

## 9. Parallel Work

Tasks may run in parallel only when:

- all hard dependencies are complete;
- shared schemas and contracts are frozen for the work period;
- migrations do not conflict;
- each task has isolated ownership;
- integration order is documented;
- no parallel task can weaken risk, RLS, ledger, or reconciliation controls.

The master task remains incomplete until parallel work is integrated and verified together.

## 10. Status and Evidence

Allowed master-task states:

- `NOT_STARTED`;
- `IN_PROGRESS`;
- `BLOCKED`;
- `IMPLEMENTED`;
- `VERIFIED`;
- `DEFERRED`;
- `NOT_APPLICABLE`.

Only `VERIFIED` is complete.

Completion evidence includes:

- changed files and migration revisions;
- commands executed;
- tests and scan results;
- coverage and invariant evidence where required;
- generated artifact hashes;
- security/privacy impact;
- environment impact;
- documentation updates;
- unresolved risks and follow-up references;
- commit SHA.

## 11. Completion Definition

The project is complete for the production-research milestone only when:

- every mandatory master task is `VERIFIED`;
- the formal paper experiment and post-experiment review are complete;
- no unresolved critical financial-integrity, security, privacy, migration, or RLS finding remains;
- backup and restore evidence is current;
- the ledger reconstructs and reconciles;
- documentation and generated artifacts match the deployed revision;
- production research is explicitly paper-only;
- live trading and private Binance access remain absent.

## 12. Documentation Synchronization Rule

Every implementation change must update all affected contracts in the same pull request or commit set:

- `TASKS.md` status/evidence;
- relevant domain or workspace specification;
- OpenAPI/schema catalogs after implementation;
- database schema and migration manifest;
- runbooks and observability where behavior changes;
- README or ROADMAP only when entry points or phase gates change;
- changelog for material behavior.

## 13. Related Documents

- `TASKS.md`
- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/BACKEND.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/TESTING.md`
- `docs/SECURITY.md`
- `docs/DOCUMENTATION_AUDIT.md`
