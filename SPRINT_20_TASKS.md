# Sprint 20 Tasks — Documentation Synchronization and Canonical Implementation Backlog

Last reviewed: 2026-08-01  
Status: Documentation synchronization sprint

## Sprint Goal

Replace conflicting task-order assumptions with one canonical dependency graph, integrate all existing detailed workstreams into `TASKS.md`, align contributor entry points, and leave the repository ready for a developer or coding agent to implement Task 1 through the production-research completion gate.

## Authoritative References

- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASKS.md`
- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/BACKEND.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/DOCUMENTATION_AUDIT.md`
- all detailed task catalogs and workspace implementation specifications

## S20.1 Audit Task Sources and Architecture Assumptions

### Work

- compare `TASKS.md`, `CLOUD_MVP_TASKS.md`, `LOCAL_AND_PRODUCTION_TASKS.md`, `UX_DESIGN_TASKS.md`, and Sprint 3–19 task files;
- identify active and superseded infrastructure assumptions;
- identify cyclic or environment-specific dependencies;
- identify workstreams missing from the root execution sequence;
- record authoritative precedence.

### Acceptance Criteria

- Redis/ARQ/WebSocket/Prometheus/Grafana conflicts are identified;
- local/cloud dependency cycles are identified;
- every Sprint 3–19 workstream is mapped;
- the active paper-only runtime profile is explicit.

## S20.2 Define Canonical Execution Governance

### Work

- create `docs/IMPLEMENTATION_EXECUTION_PLAN.md`;
- define task authority, stages, status model, evidence, parallel-work rules, and project completion;
- state that `TASKS.md` is the only execution-order authority;
- preserve detailed catalogs as acceptance-criteria sources.

### Acceptance Criteria

- one unambiguous task authority exists;
- conflicts are resolved by documented precedence;
- deferred systems require an ADR and measured need;
- project completion is defined without live trading.

## S20.3 Replace the Root Task Backlog

### Work

- replace legacy `TASKS.md` with a sequential master implementation plan;
- begin with repository/local foundations;
- integrate backend, frontend, market, Gemini, strategy, risk, execution, portfolio, backtesting, experiment, governance, UX, developer, operations, data, incident, and change-management work;
- end with verified production research and ongoing operations;
- map each master task to detailed task files and specifications.

### Acceptance Criteria

- the developer starts with Master Task 1;
- every mandatory task has hard dependencies and a completion gate;
- no task requires deferred infrastructure for the MVP;
- every detailed Sprint 3–19 catalog is represented;
- cloud deployment occurs only after local verification.

## S20.4 Align Contributor and Product Entry Points

### Work

- update `AGENTS.md` task-selection rules;
- update README implementation entry point and documentation inventory;
- update ROADMAP phase/task mappings;
- update documentation audit findings and implementation order;
- add a task-source index where useful.

### Acceptance Criteria

- no entry point tells contributors to select a conflicting task source;
- README, ROADMAP, AGENTS, and audit use the same first task and stages;
- official product identity and paper-only scope remain intact;
- detailed catalogs are described as subordinate to `TASKS.md` ordering.

## S20.5 Correct Supplemental Dependency Guidance

### Work

- document that local Supabase does not require a cloud project;
- document that local/CI recovery gates precede experiment start;
- prevent cloud tasks from becoming the local implementation entry point;
- mark queue, persistent stream, and hosted metrics tasks as deferred unless activated by ADR;
- preserve detailed cards while resolving schedule authority centrally.

### Acceptance Criteria

- no canonical dependency cycle remains;
- cloud provisioning is not required for normal local development;
- provider fakes and local tests precede protected provider/cloud workflows;
- restore proof precedes experiment start.

## S20.6 Add Documentation Consistency Rules

### Work

- require task status and evidence updates with implementation;
- require affected specs, OpenAPI, database docs, runbooks, and changelog updates;
- define CI checks for links, IDs, task structure, deprecated architecture terms, and generated drift;
- preserve historical task cards without treating documentation creation as implementation completion.

### Acceptance Criteria

- `VERIFIED` is the only complete task state;
- documentation creation cannot mark an implementation task complete;
- stale generated contracts fail the applicable gate;
- material conflicts are surfaced rather than silently resolved.

## S20.7 Verify Synchronization Commits

### Work

- fetch every Sprint 20 commit from GitHub;
- fetch updated files from `main`;
- verify task links and active architecture statements;
- verify no Sprint 20 document enables live trading or private Binance access;
- record residual implementation-dependent artifacts.

### Acceptance Criteria

- all Sprint 20 commits are retrievable;
- `TASKS.md` is readable from `main`;
- README, ROADMAP, AGENTS, and audit agree on execution order;
- residual work is implementation evidence, not unresolved documentation scope.

## Sprint 20 Definition of Done

- `docs/IMPLEMENTATION_EXECUTION_PLAN.md` exists and is authoritative;
- `TASKS.md` is the canonical sequential implementation plan;
- all detailed task catalogs are mapped without becoming competing schedules;
- the active free-cloud MVP uses one-shot execution and REST data;
- Redis, ARQ, persistent workers, WebSocket ingestion, hosted Prometheus/Grafana, Binance test trading, private Binance, and live trading are deferred;
- contributor entry points use the same Task 1;
- no canonical dependency cycle remains;
- changes are committed and fetched from GitHub for verification.
