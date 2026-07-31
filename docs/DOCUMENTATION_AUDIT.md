# Documentation Audit

Last reviewed: 2026-08-01  
Audit scope: root governance files, all active architecture and environment profiles, detailed task catalogs, Sprint 3–20 workspaces, and implementation entry points  
Status: Sprint 20 synchronization completed; implementation evidence remains future work

## 1. Executive Result

The repository now defines one canonical implementation path:

```text
M001–M006   Repository and local foundation
M007–M013   Core research domains
M014–M025   API, product workspaces, governance, and developer evidence
M026–M027   Integrated local/CI verification, export, restore, and security gate
M028–M029   Free-cloud demo and controlled 30-day paper experiment
M030–M034   Performance, data, research, incident, and change governance
M035        Post-experiment decision and staging readiness
M036        Production research launch and continuous operations
```

`TASKS.md` is the sole authority for execution order and hard dependencies. Detailed task catalogs remain authoritative for their acceptance criteria only when selected through a mapped master task.

The product remains an evidence-driven research, backtesting, and paper-trading platform. No current document authorizes private Binance execution, Binance test trading, or live capital.

## 2. Correction to the Previous Audit

The 2026-07-31 audit stated that the documentation was fully coherent for implementation. That conclusion was incomplete.

The active architecture documents already specified a free-cloud one-shot execution model, but the former root `TASKS.md` still contained mandatory P0 work for:

- Redis;
- ARQ;
- persistent workers;
- Binance WebSocket ingestion;
- Prometheus;
- Grafana;
- a Docker Compose topology built around those services.

Those tasks conflicted with:

- `docs/ARCHITECTURE.md`;
- `docs/BACKEND.md`;
- `docs/FREE_CLOUD_ARCHITECTURE.md`;
- `docs/DEPLOYMENT.md`;
- `docs/OBSERVABILITY.md`;
- `CLOUD_MVP_TASKS.md`.

The old task system also allowed multiple apparent entry points and included environment-dependent or cyclic relationships, such as local Supabase guidance depending on cloud provisioning.

Sprint 20 corrected these issues rather than preserving the previous audit conclusion.

## 3. Canonical Authority

Implementation precedence is now consistently defined as:

1. security, privacy, financial-integrity, and fail-closed requirements;
2. `AGENTS.md`;
3. `docs/PRODUCT_REQUIREMENTS.md`;
4. accepted architecture documents and ADRs;
5. domain and workspace implementation specifications;
6. `TASKS.md` for execution order and hard dependencies;
7. detailed task cards referenced by the selected master task;
8. existing implementation conventions.

Material conflicts must be corrected. A contributor must not silently choose the newest, shortest, or most convenient document.

## 4. Authoritative Entry Points

| File | Authority |
|---|---|
| `/AGENTS.md` | Mandatory contributor and coding-agent rules |
| `/TASKS.md` | Canonical Master Task M001–M036 sequence |
| `/docs/IMPLEMENTATION_EXECUTION_PLAN.md` | Task governance, stages, status, evidence, and completion |
| `/README.md` | Product orientation and implementation entry point |
| `/ROADMAP.md` | Phase outcomes mapped to master tasks; not a competing backlog |
| `/SPRINT_20_TASKS.md` | Synchronization sprint evidence |

All entry points now instruct the developer to begin with `M001`.

## 5. Detailed Task Catalog Policy

The following files contain detailed acceptance criteria but do not define independent implementation order:

- `UX_DESIGN_TASKS.md`;
- `CLOUD_MVP_TASKS.md`;
- `LOCAL_AND_PRODUCTION_TASKS.md`;
- `SPRINT_3_TASKS.md` through `SPRINT_20_TASKS.md`.

Their work is mapped into `TASKS.md` Master Tasks.

Documentation sprint completion does not imply that its implementation tasks are complete. Only a master task marked `VERIFIED` with implementation and verification evidence is complete.

## 6. Active Runtime Profile

The active MVP profile is consistent across README, AGENTS, TASKS, ROADMAP, architecture, backend, deployment, and free-cloud documents:

- Python 3.12 modular monolith;
- stateless FastAPI read/command API;
- one-shot research-cycle CLI;
- React/TypeScript/Vite frontend;
- Supabase PostgreSQL and Auth;
- Binance Spot public REST using finalized candles;
- Google Gemini using the official `google-genai` SDK;
- GitHub Actions best-effort scheduling;
- Cloudflare Pages and Render Free for the initial cloud demo;
- PostgreSQL advisory lock or durable lease;
- deterministic idempotency;
- append-only double-entry ledger;
- mandatory reconciliation;
- paper trading only.

## 7. Deferred Architecture

The following are explicitly deferred from mandatory MVP implementation:

- Redis and ARQ;
- persistent workers;
- Binance WebSocket ingestion;
- hosted Prometheus and Grafana;
- Kubernetes;
- paid/high-availability infrastructure;
- Binance test/private credentials;
- live trading.

Activation requires measured need, an ADR, updated requirements and tasks, migration and rollback plans, security/privacy review, tests, cost/capacity evidence, staged verification, and owner approval.

## 8. Dependency Audit

Resolved canonical dependency rules include:

- local Supabase/PostgreSQL/Auth does not depend on a cloud project;
- local bootstrap and deterministic fakes precede protected provider and cloud workflows;
- domain contracts precede consuming UI workspaces;
- ledger and reconciliation precede final portfolio and experiment status;
- the one-shot CLI precedes scheduled cloud execution;
- integrated local/CI verification precedes cloud deployment;
- export and tested restore precede the formal experiment;
- measured evidence precedes SLO, capacity, cost, and scaling claims;
- backtest, untouched-test, robustness, reproducibility, paper observation, and owner review precede strategy promotion;
- behavior changes apply only to future configurations and never mutate a running experiment.

No canonical dependency cycle remains in `TASKS.md`.

## 9. Workspace Coverage

| Master area | Detailed source |
|---|---|
| Frontend shell | `SPRINT_3_TASKS.md` |
| Component library | `SPRINT_4_TASKS.md` |
| Today’s Roast | `SPRINT_5_TASKS.md` |
| Market Evidence | `SPRINT_6_TASKS.md` |
| Strategy and Risk | `SPRINT_7_TASKS.md` |
| Portfolio, Execution, Ledger, Reconciliation | `SPRINT_8_TASKS.md` |
| Backtests and Comparison | `SPRINT_9_TASKS.md` |
| Experiment Operations and Audit | `SPRINT_10_TASKS.md` |
| Gemini Analysis and Validation | `SPRINT_11_TASKS.md` |
| Auth, Governance, Security, Privacy, Release | `SPRINT_12_TASKS.md` |
| Product Shell, Onboarding, Search, Trust, i18n | `SPRINT_13_TASKS.md` |
| Developer Portal and Traceability | `SPRINT_14_TASKS.md` |
| Performance, Resilience, SLO, FinOps | `SPRINT_15_TASKS.md` |
| Data Lifecycle and Dataset Governance | `SPRINT_16_TASKS.md` |
| Research Review and Strategy Lifecycle | `SPRINT_17_TASKS.md` |
| Incident Response and Learning | `SPRINT_18_TASKS.md` |
| Change Management and Staged Rollout | `SPRINT_19_TASKS.md` |
| Documentation Synchronization | `SPRINT_20_TASKS.md` |

Every workstream is represented by one or more master tasks in `TASKS.md`.

## 10. Environment Lifecycle

The synchronized environment path is:

```text
Local
  -> CI and integrated local verification
  -> Free-cloud demo
  -> Controlled paper experiment
  -> Evidence hardening and post-experiment review
  -> Isolated staging
  -> Production research service
  -> Separate future Binance test assessment
  -> Separate future real-capital assessment
```

Production research still uses simulated execution. No phase can be skipped because of favorable performance.

## 11. Safety and Product Consistency

The synchronized documents consistently require:

- official name **The Daily Roast AI**;
- tagline **Evidence-Driven Market Intelligence**;
- evidence over hype;
- simulation and paper labels;
- analytical confidence distinct from probability of profit;
- deterministic strategy and risk around probabilistic AI;
- Decimal financial arithmetic and UTC timestamps;
- immutable used inputs and configuration versions;
- idempotent side effects;
- deny-by-default browser access;
- no secrets in source, prompts, bundles, logs, metrics, screenshots, or artifacts;
- append-only ledger and reconciliation;
- tested restore before backup claims;
- human approval for material research, release, and behavior changes;
- no guaranteed-return, urgency, or financial-advice language.

## 12. Sprint 20 Changes

Added:

- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`;
- `SPRINT_20_TASKS.md`.

Replaced or materially synchronized:

- `TASKS.md`;
- `AGENTS.md`;
- `README.md`;
- `ROADMAP.md`;
- this audit;
- `CHANGELOG.md`.

## 13. Verified Sprint 20 Commits

- `a952f8f3636abae96cd10135463f61adc35609fd` — implementation execution plan;
- `2020ede10ce097d4c3b0fcd836bb0ff3b5a3d25c` — Sprint 20 task catalog;
- `64d1b08e579499f3bc6833428172ca318de3dc49` — canonical `TASKS.md` backlog;
- `10c5f252277e08f7d69d2657e85e057a68288b4d` — `AGENTS.md` workflow alignment;
- `8de1c738454e8381e971e09c0da9e7e6f62a2f59` — README implementation entry point;
- `47efdaae7d50b4ece42b6e5b1f08748d89474eb2` — ROADMAP master-task mapping;
- `f7ee54fc28e42b52297d1ed267c91caafc5b55ca` — execution-plan catalog update.

Each listed commit was fetched from GitHub after creation.

## 14. Implementation-Dependent Artifacts

The following remain intentionally absent or incomplete until their mapped master tasks are implemented:

- backend and frontend source implementations;
- dependency lock files;
- stable command scripts;
- Supabase local config, migrations, RLS policies, functions, and seeds;
- exact GitHub Actions workflows;
- generated OpenAPI and frontend types;
- API, schema, error, event, permission, metric, and migration catalogs;
- automated documentation-health output;
- real cloud project identifiers and public deployment URLs;
- provider smoke evidence;
- experiment, incident, performance, cost, and strategy-review evidence;
- export, backup, restore, and recovery artifacts;
- staging and production infrastructure selections;
- measured SLO, RPO, RTO, capacity, and cost results;
- security, privacy, accessibility, and operational review results.

These are implementation deliverables assigned to M001–M036, not missing documentation decisions.

## 15. Rules for Future Changes

1. Start work through one `TASKS.md` master task.
2. Verify hard dependencies before editing.
3. Use detailed cards only through their mapped master task.
4. Update task status and evidence with implementation.
5. Update affected specifications, OpenAPI, schema/database docs, runbooks, and changelog in the same change.
6. Detect broken links, unknown IDs, deprecated architecture terms, and generated drift in CI.
7. Never edit an applied migration.
8. Never represent documentation creation, coverage percentage, or a passing score as implementation approval.
9. Preserve environment and credential isolation.
10. Keep Gemini advisory and all execution paper-only.
11. Treat restore, reconciliation, security, privacy, and incident evidence as promotion gates.
12. Process material behavior changes through governed staged rollout.

## 16. Conclusion

The repository is now documentation-ready for implementation from `M001` through `M036`.

The first developer action is:

```text
Open TASKS.md
Select M001
Read AGENTS.md and docs/IMPLEMENTATION_EXECUTION_PLAN.md
Implement and verify M001 before selecting dependent work
```

No remaining documentation conflict requires a developer to choose between competing MVP architectures or task entry points.
