# Implementation Execution Plan and Documentation Synchronization

Last reviewed: 2026-08-01  
Status: Authoritative implementation-order and task-governance specification

## 1. Purpose

This document defines the single executable path for building The Daily Roast AI from an empty implementation repository to a verified production-grade research service.

The repository contains detailed domain specifications, UX workstreams, cloud tasks, local/production tasks, and Sprint 3–21 task catalogs. Those files remain authoritative for detailed acceptance criteria, but they do not independently define execution order. `TASKS.md` is the only canonical implementation sequence.

`docs/TASK_CATALOG_INDEX.md` maps detailed IDs and catalogs to Master Tasks and classifies work as mandatory, conditional, deferred, superseded, future assessment, or documentation complete.

## 2. Problems Corrected by Sprints 20 and 21

The previous task system contained valid detailed work but exposed conflicting implementation assumptions:

- the former `TASKS.md` treated Redis, ARQ, persistent workers, WebSocket ingestion, Prometheus, and Grafana as MVP P0 requirements;
- the active architecture deliberately defers those systems until measured need and approved change governance;
- local, cloud, UX, and Sprint task files could be read as parallel entry points;
- some supplemental dependencies were cyclic or environment-specific;
- Sprint 3–19 workspace tasks were not integrated into the root implementation sequence;
- the previous documentation audit claimed consistency while the root backlog still contained superseded architecture;
- testing, deployment, free-cloud, staging, and production documents described compatible concepts but did not consistently map them to one stable task lifecycle.

Sprint 20 established M001–M036 and synchronized primary entry points. Sprint 21 added the task catalog index and aligned testing, deployment, free-cloud, staging, and production-research gates.

## 3. Canonical Authority

Implementation precedence is:

1. security, privacy, financial-integrity, and fail-closed requirements;
2. `AGENTS.md`;
3. `docs/PRODUCT_REQUIREMENTS.md`;
4. accepted architecture documents and ADRs;
5. domain and workspace implementation specifications;
6. `TASKS.md` for execution order and dependency gates;
7. detailed task cards referenced by the selected Master Task and mapped in `docs/TASK_CATALOG_INDEX.md`;
8. existing implementation conventions.

When a supplemental task file conflicts with `TASKS.md`:

- the Master Task dependency and active architecture win;
- compatible acceptance criteria are retained;
- incompatible assumptions are marked deferred or superseded in the task catalog index;
- the conflict is corrected rather than implemented silently.

## 4. Active MVP Runtime Profile

The active implementation profile is:

- Python 3.12 modular monolith;
- FastAPI read/command API;
- one-shot research-cycle CLI;
- React, TypeScript, and Vite frontend;
- Supabase PostgreSQL and Auth;
- Binance Spot public REST using finalized candles;
- Google Gemini through the official `google-genai` SDK;
- GitHub Actions as a best-effort external scheduler;
- Cloudflare Pages frontend and Render Free API for the first demo;
- PostgreSQL locks or durable leases and deterministic idempotency;
- append-only double-entry ledger and mandatory reconciliation;
- paper trading only.

The following are deferred and must not be introduced as mandatory M001–M036 dependencies:

- Redis;
- ARQ or another persistent queue;
- persistent worker processes;
- Binance WebSocket ingestion;
- hosted Prometheus or Grafana;
- Kubernetes;
- automatic paid infrastructure or scaling;
- private Binance credentials;
- Binance test trading;
- live trading.

A deferred component requires measured need, M034 change governance, an ADR, migration and rollback plans, updated tasks, security/privacy review, tests, cost/capacity evidence, staged paper verification, and owner approval. Exchange credential or live-capital work additionally requires a separate future milestone.

## 5. Task Model

Each Master Task in `TASKS.md` contains:

- stable `Mxxx` ID;
- implementation outcome;
- required detailed workstreams;
- hard dependencies;
- required verification;
- completion gate;
- deferred or prohibited scope.

A Master Task is complete only when:

- all mandatory and applicable conditional detailed cards are implemented;
- deferred/superseded/future-assessment cards remain excluded unless separately activated;
- acceptance and failure cases are integrated;
- required security, privacy, accessibility, recovery, financial-integrity, and documentation evidence exists;
- the final commit or pull request is fetched and inspected;
- `TASKS.md` records verification evidence.

Only `VERIFIED` is complete.

## 6. Detailed Task Sources

### Core and environment catalogs

- `TASKS.md` — canonical Master Task sequence;
- `docs/TASK_CATALOG_INDEX.md` — detailed mapping and classification;
- `UX_DESIGN_TASKS.md` — UX/design acceptance detail;
- `CLOUD_MVP_TASKS.md` — free-cloud deployment and experiment detail;
- `LOCAL_AND_PRODUCTION_TASKS.md` — local, testing, staging, production-research, and post-launch detail.

### Workspace and governance catalogs

- `SPRINT_3_TASKS.md` — frontend application shell;
- `SPRINT_4_TASKS.md` — accessible component library;
- `SPRINT_5_TASKS.md` — Today’s Roast dashboard;
- `SPRINT_6_TASKS.md` — Market Evidence;
- `SPRINT_7_TASKS.md` — Strategy and Risk;
- `SPRINT_8_TASKS.md` — Portfolio, Execution, Ledger, and Reconciliation;
- `SPRINT_9_TASKS.md` — Backtests, Benchmarks, Reproducibility, and Comparison;
- `SPRINT_10_TASKS.md` — Experiment Operations and Audit;
- `SPRINT_11_TASKS.md` — Gemini Analysis and Validation;
- `SPRINT_12_TASKS.md` — Auth, Governance, Security, Privacy, and Release;
- `SPRINT_13_TASKS.md` — Product Shell, Onboarding, Search, Notifications, Trust Center, and i18n;
- `SPRINT_14_TASKS.md` — Developer Portal, Documentation Health, and Traceability;
- `SPRINT_15_TASKS.md` — Performance, Resilience, Capacity, SLOs, Quotas, and FinOps;
- `SPRINT_16_TASKS.md` — Data Lifecycle and Dataset Governance;
- `SPRINT_17_TASKS.md` — Research Review and Strategy Lifecycle;
- `SPRINT_18_TASKS.md` — Incident Response, Postmortems, and Learning;
- `SPRINT_19_TASKS.md` — Governed Behavior Changes and Staged Rollout;
- `SPRINT_20_TASKS.md` — Canonical Implementation Backlog Synchronization;
- `SPRINT_21_TASKS.md` — Task Catalog and Lifecycle Cross-Reference Synchronization.

Sprint numbers identify documentation workstreams. They do not grant permission to implement a workstream before its Master Task dependencies.

## 7. Implementation Stages

### Stage A — Repository and Local Foundation

**M001–M006**

Build the repository skeleton, locked toolchains, shared commands, local Supabase, migrations, Auth/RLS, frontend foundation, provider contracts, and deterministic fakes.

No cloud project or paid provider is required.

### Stage B — Core Research Domains

**M007–M013**

Implement finalized market data, quality controls, immutable snapshots, deterministic features, Gemini validation, strategy, risk, paper execution, ledger, reconciliation, one-shot orchestration, and backtesting.

### Stage C — API and Product Experience

**M014–M025**

Implement versioned APIs, authorization, application shell, accessible components, evidence workspaces, experiment/governance UI, onboarding/search/Trust/i18n, and developer traceability.

### Stage D — Verification and Local Completion

**M026–M027**

Complete integrated deterministic tests, RLS/Auth/security/accessibility/documentation checks, export, isolated restore, recovery drills, ledger rebuild, and reconciliation.

Cloud deployment must not compensate for missing local verification.

### Stage E — Free-Cloud Deployment and Controlled Experiment

**M028–M029**

Provision isolated cloud services, deploy API/frontend, schedule the one-shot cycle, verify cold-start and free-tier behavior, repeat export/restore, pass preflight, freeze configuration, and run the 30-day virtual EUR 20 experiment.

### Stage F — Evidence Hardening and Governance

**M030–M034**

Complete measured reliability/FinOps, dataset governance, research review, incident learning, and change-management controls.

### Stage G — Staging and Production Research

**M035–M036**

Make an explicit post-experiment decision, validate immutable artifacts in isolated staging, then launch and operate an authenticated paper-research service. Live trading remains disabled.

## 8. Dependency Rules

- local Supabase does not depend on a cloud project;
- deterministic fakes precede protected provider and cloud workflows;
- domain contracts precede consuming APIs and UI workspaces;
- ledger and reconciliation precede final portfolio and experiment status;
- the one-shot CLI precedes scheduled cloud execution;
- M026 and M027 precede M028;
- M028 precedes M029;
- current export/restore evidence precedes experiment start and production promotion;
- measured evidence precedes SLO, cost, capacity, or scaling claims;
- M030–M034 precede staging approval;
- strategy promotion requires untouched-test, robustness, reproducibility, paper observation, and owner review;
- behavior activation applies only to future configurations and never mutates a running experiment;
- production research still uses simulated execution.

## 9. Parallel Work

Tasks may run in parallel only when:

- all hard dependencies are verified;
- shared schemas/contracts are stable for the work period;
- migrations do not conflict;
- each workstream has isolated ownership;
- integration order is documented;
- no workstream weakens Auth, RLS, risk, ledger, reconciliation, privacy, or recovery controls.

The Master Task remains incomplete until parallel work is integrated and verified together.

## 10. Status and Evidence

Allowed Master Task states:

- `NOT_STARTED`;
- `IN_PROGRESS`;
- `BLOCKED`;
- `IMPLEMENTED_NOT_VERIFIED`;
- `VERIFIED`;
- `DEFERRED`;
- `NOT_APPLICABLE_WITH_APPROVAL`.

Completion evidence includes as applicable:

- Master Task and detailed task IDs;
- source, migration, generated, and documentation changes;
- commands executed and results;
- coverage and invariant evidence;
- security, privacy, accessibility, and recovery evidence;
- environment and compatibility impact;
- artifact, schema, OpenAPI, dependency, configuration, and behavior-set hashes;
- unresolved risks, exceptions, limitations, and follow-up IDs;
- commit or pull-request reference.

## 11. Completion Definition

The project reaches the production-research milestone only when:

- every mandatory Master Task M001–M036 is `VERIFIED`;
- the formal paper experiment and post-experiment decision are complete;
- no unresolved critical financial-integrity, security, privacy, migration, Auth, or RLS finding remains;
- backup/export and restore evidence is current;
- the ledger reconstructs and reconciles;
- documentation and generated artifacts match the deployed revision;
- production research is explicitly paper-only;
- live trading and private Binance access remain absent.

## 12. Documentation Synchronization Rule

Every implementation change updates all affected contracts in the same pull request or commit set:

- `TASKS.md` status and evidence;
- `docs/TASK_CATALOG_INDEX.md` when mappings/classification change;
- relevant domain or workspace specification;
- OpenAPI/schema/error/event/permission catalogs after implementation;
- database schema and migration manifest;
- tests, runbooks, observability, security, privacy, and operations documentation when affected;
- README or ROADMAP when entry points or phase gates change;
- changelog for material behavior.

## 13. Related Documents

- `TASKS.md`
- `TASK_CATALOG_INDEX.md`
- `SPRINT_20_TASKS.md`
- `SPRINT_21_TASKS.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `README.md`
- `ROADMAP.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `PRODUCT_REQUIREMENTS.md`
- `TESTING.md`
- `TEST_ENVIRONMENTS.md`
- `DEPLOYMENT.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `PRODUCTION_DEVELOPMENT.md`
- `SECURITY.md`
- `DOCUMENTATION_AUDIT.md`
