# Sprint 21 Tasks — Task Catalog Mapping and Lifecycle Cross-Reference Synchronization

Last reviewed: 2026-08-01  
Status: Documentation synchronization in progress  
Scope: residual task-catalog and lifecycle cross-reference alignment

## Sprint Goal

Make every detailed task catalog and environment lifecycle document unambiguously subordinate to the `TASKS.md` Master Task sequence, provide a stable mapping from legacy and sprint task IDs to M001–M036, and align testing, deployment, free-cloud, staging, and production-research gates without changing the active paper-only architecture.

## Authoritative References

- `TASKS.md`
- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`
- `docs/DOCUMENTATION_AUDIT.md`
- `UX_DESIGN_TASKS.md`
- `CLOUD_MVP_TASKS.md`
- `LOCAL_AND_PRODUCTION_TASKS.md`
- `SPRINT_3_TASKS.md` through `SPRINT_20_TASKS.md`
- `docs/TESTING.md`
- `docs/TEST_ENVIRONMENTS.md`
- `docs/DEPLOYMENT.md`
- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `AGENTS.md`

## S21.1 Create the Task Catalog Index

### Work

- create `docs/TASK_CATALOG_INDEX.md`;
- map UX, cloud, local/production, and Sprint 3–20 catalogs to Master Tasks;
- classify detailed IDs as mandatory, conditional, deferred, superseded, or future-assessment work;
- define how conflicting dependencies are resolved;
- preserve historical task identity without granting independent ordering authority.

### Acceptance Criteria

- every active detailed task catalog has a Master Task mapping;
- local, cloud, staging, and production work are separated;
- WebSocket, Redis/ARQ, hosted metrics, Binance test/private access, and live trading remain deferred;
- detailed acceptance criteria remain traceable.

## S21.2 Align Testing Documentation

### Work

- update `docs/TESTING.md` with Master Task gates and evidence status;
- align its environment and promotion references with `docs/TEST_ENVIRONMENTS.md`;
- require Master Task plus detailed-card IDs in test and PR evidence;
- preserve deterministic fake-provider and recovery requirements.

### Acceptance Criteria

- test stages map to M001–M036;
- no cloud or paid provider is required for normal CI;
- production-research testing remains paper-only;
- documentation creation cannot satisfy test completion.

## S21.3 Align Deployment Documentation

### Work

- map local, demo, experiment, staging, and production-research deployment gates to M tasks;
- make M026–M027 prerequisites for M028 explicit;
- make M029 prerequisites for evidence hardening and staging explicit;
- preserve separate future Binance test and live-capital assessments.

### Acceptance Criteria

- no deployment phase bypasses local verification or restore proof;
- Render remains API-only and not the scheduler;
- free tiers are not SLA claims;
- live trading is not a deployment target.

## S21.4 Align Production Development Documentation

### Work

- map staging to M035 and production research to M036;
- map performance/data/research/incident/change governance to M030–M034;
- require immutable artifact, migration, restore, security/privacy, SLO, cost, and incident evidence;
- preserve explicit separation from Binance test and live trading.

### Acceptance Criteria

- production research means production-quality paper research;
- no favorable result can skip staging or approvals;
- ongoing material changes use M034 governance;
- future exchange credential work requires a separate milestone.

## S21.5 Align Free-Cloud Documentation

### Work

- map free-cloud foundation to M028 and controlled experiment to M029;
- state that local Supabase and normal CI precede cloud provisioning;
- preserve one-shot CLI, REST data, database locks, and safe degradation;
- align export/restore and preflight prerequisites.

### Acceptance Criteria

- cloud tasks are not the repository entry point;
- no local computer is required for scheduled cycles;
- missing or delayed cycles never create imagined trades;
- no auto-upgrade or private exchange path exists.

## S21.6 Verify Task and Lifecycle Cross-References

### Work

- fetch every Sprint 21 commit;
- fetch synchronized documents from `main`;
- verify M001–M036 mappings and phase gates;
- verify official product identity and paper-only boundaries;
- record residual implementation-dependent artifacts.

### Acceptance Criteria

- all commits are retrievable;
- catalog mappings contain no canonical cycle;
- environment documents use the same M task gates;
- no Sprint 21 document authorizes deferred or live execution.

## Sprint 21 Definition of Done

- `docs/TASK_CATALOG_INDEX.md` exists;
- testing, deployment, free-cloud, and production-development documents use the Master Task lifecycle;
- detailed task IDs remain usable as acceptance references but cannot override `TASKS.md`;
- all changes are committed and verified from GitHub;
- implementation still starts with M001.
