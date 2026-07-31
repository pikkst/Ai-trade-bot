# Sprint 20 Tasks — Documentation Synchronization and Canonical Implementation Backlog

Last reviewed: 2026-08-01  
Status: Completed and verified  
Implementation status: Documentation governance complete; product implementation starts at `M001`

## Sprint Goal

Replace conflicting task-order assumptions with one canonical dependency graph, integrate all existing detailed workstreams into `TASKS.md`, align contributor entry points, and leave the repository ready for a developer or coding agent to implement Master Task 1 through the production-research completion gate.

## Authoritative References

- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASKS.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `README.md`
- `ROADMAP.md`
- `docs/LOCAL_DEVELOPMENT.md`
- `docs/TEST_ENVIRONMENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/BACKEND.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/DOCUMENTATION_AUDIT.md`
- `CHANGELOG.md`
- all detailed task catalogs and workspace implementation specifications

## [x] S20.1 Audit Task Sources and Architecture Assumptions

Completed:

- compared the former `TASKS.md`, `CLOUD_MVP_TASKS.md`, `LOCAL_AND_PRODUCTION_TASKS.md`, `UX_DESIGN_TASKS.md`, and Sprint 3–19 task files;
- identified mandatory Redis, ARQ, persistent-worker, WebSocket, Prometheus, and Grafana assumptions in the former root backlog;
- identified the conflict with the authoritative one-shot free-cloud architecture;
- identified multiple apparent task entry points and local/cloud dependency cycles;
- mapped every Sprint 3–19 workstream into the new master sequence;
- recorded the correction in `docs/DOCUMENTATION_AUDIT.md`.

Acceptance verified:

- infrastructure conflicts are explicit;
- local/cloud dependency cycles are removed from canonical ordering;
- the paper-only runtime profile is explicit;
- no detailed catalog was deleted.

## [x] S20.2 Define Canonical Execution Governance

Completed:

- created `docs/IMPLEMENTATION_EXECUTION_PLAN.md`;
- defined instruction precedence, task authority, stages, status, evidence, parallel-work rules, and project completion;
- established `TASKS.md` as the only implementation-order authority;
- established detailed catalogs as acceptance-criteria sources only through mapped master tasks;
- added Sprint 20 to the governance catalog.

Acceptance verified:

- one unambiguous task authority exists;
- conflicts use documented precedence;
- deferred systems require measured need and an ADR;
- production-research completion is defined without live trading.

## [x] S20.3 Replace the Root Task Backlog

Completed:

- replaced the legacy root backlog with Master Tasks `M001–M036`;
- defined hard dependencies, outcomes, detailed sources, verification, and completion gates;
- ordered repository/local foundations before domains;
- ordered domains before API and UI workspaces;
- ordered full local/CI verification and restore before cloud deployment;
- ordered the controlled experiment before evidence hardening and staging;
- integrated Sprint 3–19 detailed catalogs;
- deferred Redis, ARQ, persistent workers, WebSocket ingestion, hosted Prometheus/Grafana, Binance test/private credentials, and live trading.

Acceptance verified:

- the developer starts with `M001`;
- cloud deployment begins only at `M028` after `M026–M027`;
- every mandatory master task has a completion gate;
- the project ends at verified production research `M036`.

## [x] S20.4 Align Contributor and Product Entry Points

Completed:

- updated `AGENTS.md`;
- updated `CONTRIBUTING.md`;
- updated README;
- updated ROADMAP;
- updated `docs/LOCAL_DEVELOPMENT.md`;
- updated `docs/TEST_ENVIRONMENTS.md`;
- updated the documentation audit and changelog.

Acceptance verified:

- all active contributor entry points start with `M001`;
- README, ROADMAP, AGENTS, CONTRIBUTING, local development, test environments, and the audit use the same stages;
- official product identity and paper-only scope remain intact;
- supplemental catalogs do not override `TASKS.md`.

## [x] S20.5 Correct Supplemental Dependency Guidance

Completed:

- documented that local Supabase does not depend on a cloud project;
- made deterministic fakes and local tests precede protected provider/cloud workflows;
- placed export/restore/security gates before the formal experiment;
- placed cloud provisioning and deployment at `M028`;
- classified queue, persistent stream, hosted metrics, test/private exchange, and live execution as deferred;
- preserved historical detailed cards while removing their authority over canonical order.

Acceptance verified:

- no canonical dependency cycle remains;
- normal local development requires no cloud or paid provider;
- restore proof precedes experiment start;
- a historical task card cannot activate deferred infrastructure.

## [x] S20.6 Add Documentation Consistency Rules

Completed:

- defined `VERIFIED` as the only complete master-task state;
- required implementation commits, tests, scans, hashes, environment impact, documentation, limitations, and follow-ups as evidence;
- required affected task, specification, OpenAPI/schema, database, runbook, observability, README/ROADMAP, and changelog synchronization;
- required CI checks for links, IDs, task format, conflicts, deprecated architecture terms, and generated drift;
- documented that documentation creation, a passing score, coverage, or a demo cannot auto-complete or approve implementation.

Acceptance verified:

- generated contract drift is a gate;
- material conflicts must be surfaced;
- historical task cards remain traceable;
- implementation and documentation completion are distinct.

## [x] S20.7 Verify Synchronization Commits

Verified GitHub commits:

- `a952f8f3636abae96cd10135463f61adc35609fd` — created implementation execution plan;
- `2020ede10ce097d4c3b0fcd836bb0ff3b5a3d25c` — created Sprint 20 task catalog;
- `64d1b08e579499f3bc6833428172ca318de3dc49` — replaced root `TASKS.md` with M001–M036;
- `10c5f252277e08f7d69d2657e85e057a68288b4d` — aligned `AGENTS.md`;
- `8de1c738454e8381e971e09c0da9e7e6f62a2f59` — aligned README;
- `47efdaae7d50b4ece42b6e5b1f08748d89474eb2` — mapped ROADMAP to master tasks;
- `f7ee54fc28e42b52297d1ed267c91caafc5b55ca` — added Sprint 20 to task governance;
- `602cbe95bfa84166331061063d0395308ac52963` — updated documentation audit;
- `ffdb786bc225510a2bfbb95ee35dcd3f1e495cf9` — updated changelog;
- `97551969ce4f4958a932f0e6283c8e842315e464` — aligned CONTRIBUTING;
- `1c67e7ffc205a25d4f733534fa4195c45a706546` — aligned local development;
- `b06ebbb5f7088732f85d6e5b787bca1f22bb1390` — aligned test environments.

Verification performed:

- each listed commit was fetched from GitHub after creation;
- updated files were fetched from `main`;
- `TASKS.md` begins with `M001` and ends with `M036`;
- active runtime uses one-shot execution and Binance REST;
- local development does not require a cloud project;
- cloud deployment follows local/CI and restore gates;
- no Sprint 20 document authorizes live trading, private Binance execution, leverage, derivatives, shorting, custody, or withdrawals.

## Sprint 20 Definition of Done

- [x] `docs/IMPLEMENTATION_EXECUTION_PLAN.md` exists and is authoritative;
- [x] `TASKS.md` is the canonical sequential implementation plan;
- [x] all detailed task catalogs are mapped without becoming competing schedules;
- [x] the active free-cloud MVP uses a one-shot CLI and finalized REST data;
- [x] Redis, ARQ, persistent workers, WebSocket ingestion, hosted Prometheus/Grafana, Binance test trading, private Binance, and live trading are deferred;
- [x] contributor entry points use the same `M001` first task;
- [x] no canonical dependency cycle remains;
- [x] synchronization changes are committed and fetched from GitHub;
- [x] implementation-dependent artifacts are assigned to `M001–M036` rather than misreported as completed.

## Developer Handoff

The next project action is not to create another documentation-only implementation sprint.

The developer or coding agent should:

```text
1. Open AGENTS.md
2. Open docs/IMPLEMENTATION_EXECUTION_PLAN.md
3. Open TASKS.md
4. Select M001
5. Implement and verify M001
6. Continue only when dependencies are VERIFIED
```

Sprint 20 completion means the documentation is synchronized. It does not mark any product implementation Master Task as complete.
