# Sprint 22 Tasks — Runtime Architecture, Configuration, and Observability Contract Synchronization

Last reviewed: 2026-08-01  
Status: Documentation synchronization in progress

## Sprint Goal

Synchronize the active runtime architecture, backend boundaries, technology stack, environment-variable inventory, observability model, and Master Task ownership so a developer implementing M001–M013 and M028–M030 receives one consistent paper-only runtime contract.

## Authoritative References

- `TASKS.md`
- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`
- `docs/TASK_CATALOG_INDEX.md`
- `docs/ARCHITECTURE.md`
- `docs/BACKEND.md`
- `docs/TECH_STACK.md`
- `docs/OBSERVABILITY.md`
- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/FREE_CLOUD_REQUIREMENTS.md`
- `.env.example`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `AGENTS.md`

## S22.1 Align Architecture with Master Tasks

### Work

- map architectural foundations to M001–M006;
- map domains and orchestration to M007–M013;
- map cloud runtime to M028–M029 and measured evolution to M030/M034;
- distinguish authoritative runtime components from deferred options;
- add cycle completeness, incident, behavior-set, and no-auto-spend boundaries.

### Acceptance Criteria

- one-shot CLI and REST are the active MVP runtime;
- Render is not the scheduler;
- M026–M027 precede cloud deployment;
- running experiments remain frozen;
- no deferred component becomes mandatory through architecture prose.

## S22.2 Align Backend Contract

### Work

- map backend packages and services to Master Tasks;
- define command, transaction, lock, idempotency, audit/outbox, and reconciliation boundaries;
- distinguish Supabase Auth validation from application authorization;
- define deterministic cycle completeness and safe recovery;
- classify queue/worker/WebSocket infrastructure as deferred change-governed work.

### Acceptance Criteria

- domain code has project-owned boundaries;
- no network call occurs inside financial transactions;
- successful process exit is insufficient without required cycle stages;
- no direct browser critical-table write exists;
- no strategy, AI, or API bypasses risk/accounting.

## S22.3 Align Technology Stack

### Work

- map technology adoption to M001–M006 and environment promotion gates;
- distinguish required, optional, deferred, and future-assessment technology;
- require lock files, pinned actions/images, generated contracts, and Windows support;
- preserve free-tier caveats and no-auto-upgrade behavior.

### Acceptance Criteria

- required stack matches TASKS and architecture;
- provider/SDK boundaries are explicit;
- deferred infrastructure requires M034 and ADR;
- no provider quota is treated as a constant.

## S22.4 Align Environment Variable Inventory

### Work

- make `.env.example` a safe variable inventory rather than an executable secret file;
- remove conflicting custom JWT/password configuration from the Supabase Auth profile;
- distinguish public, server, workflow, bootstrap-default, and immutable experiment configuration;
- require startup rejection of unsafe flags and public-bundle allowlisting;
- add no-auto-spend, private-exchange, and behavior-freeze comments.

### Acceptance Criteria

- no real or usable secret appears;
- Supabase Auth remains authoritative;
- environment defaults cannot mutate a running experiment;
- frontend-public variables are explicit;
- every prohibited execution flag defaults false.

## S22.5 Align Observability Contract

### Work

- map foundational logging/health to M005, cycle evidence to M012/M022/M029, and measured SLI/SLO/FinOps to M030;
- add cycle stages, completeness, incident, export/restore, release, and audit evidence;
- distinguish logs from durable evidence;
- preserve bounded labels and redaction;
- keep hosted metrics deferred unless M034 activates them.

### Acceptance Criteria

- observability proves safety and completeness rather than only process uptime;
- intended/actual schedule, lock/idempotency, ledger/reconciliation, and fallback are visible;
- incident and blocker state persists;
- profit is not an operational metric or SLO;
- no hosted stack is falsely marked complete.

## S22.6 Verify Runtime Contract Synchronization

### Work

- fetch every Sprint 22 commit;
- fetch synchronized files from `main`;
- compare runtime components, flags, and task ownership;
- verify paper-only and deferred boundaries;
- update audit/changelog and complete the Sprint file.

### Acceptance Criteria

- all commits are retrievable;
- architecture, backend, tech stack, env inventory, and observability agree;
- no unsafe Auth, provider, scheduling, or execution ambiguity remains;
- implementation handoff still starts at M001.

## Sprint 22 Definition of Done

- architecture, backend, technology, configuration, and observability contracts are synchronized;
- active/deferred/future components are explicitly classified;
- every runtime area maps to Master Tasks;
- `.env.example` contains safe placeholders and safe defaults only;
- changes are committed and verified from GitHub;
- product implementation remains not started.
