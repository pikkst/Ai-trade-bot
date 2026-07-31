# Sprint 21 Tasks — Task Catalog Mapping and Lifecycle Cross-Reference Synchronization

Last reviewed: 2026-08-01  
Status: Completed and verified  
Scope: detailed task-catalog and environment-lifecycle alignment

## Sprint Goal

Make every detailed task catalog and environment lifecycle document unambiguously subordinate to the `TASKS.md` Master Task sequence, provide a stable mapping from legacy and Sprint task IDs to M001–M036, and align testing, deployment, free-cloud, staging, and production-research gates without changing the active paper-only architecture.

## Authoritative References

- `TASKS.md`
- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`
- `docs/TASK_CATALOG_INDEX.md`
- `docs/DOCUMENTATION_AUDIT.md`
- `UX_DESIGN_TASKS.md`
- `CLOUD_MVP_TASKS.md`
- `LOCAL_AND_PRODUCTION_TASKS.md`
- `SPRINT_3_TASKS.md` through `SPRINT_21_TASKS.md`
- `docs/TESTING.md`
- `docs/TEST_ENVIRONMENTS.md`
- `docs/DEPLOYMENT.md`
- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/FREE_CLOUD_REQUIREMENTS.md`
- `AGENTS.md`
- `README.md`
- `ROADMAP.md`

## [x] S21.1 Create the Task Catalog Index

Completed:

- created `docs/TASK_CATALOG_INDEX.md`;
- mapped legacy `T*`, UX, C1–C8 cloud, local/CI, staging/production, and Sprint 3–21 task areas to Master Tasks;
- classified work as mandatory, conditional, deferred, superseded, future assessment, or documentation complete;
- defined conflict-resolution rules;
- preserved historical task identity without granting independent ordering authority.

Acceptance verified:

- every active detailed catalog has a Master Task mapping;
- local, cloud, staging, and production work are separated;
- Redis/ARQ, persistent workers, WebSocket ingestion, hosted metrics, Binance test/private access, and live trading remain deferred or future assessment;
- detailed acceptance criteria remain traceable.

## [x] S21.2 Align Testing Documentation

Completed:

- mapped `docs/TESTING.md` to M001–M036 gates;
- aligned deterministic test layers and promotion gates with `docs/TEST_ENVIRONMENTS.md`;
- required Master Task and detailed-card IDs in implementation evidence;
- preserved fake-provider defaults, recovery, accessibility, security/privacy, and financial-invariant tests.

Acceptance verified:

- normal CI requires no cloud or paid provider;
- test stages map to the Master Task lifecycle;
- production-research testing remains paper-only;
- documentation creation, coverage, or a score cannot satisfy implementation completion.

## [x] S21.3 Align Deployment Documentation

Completed:

- mapped local/CI verification to M026;
- mapped export/restore/recovery/security prerequisites to M027;
- mapped free-cloud deployment to M028;
- mapped the controlled experiment to M029;
- mapped staging to M035 and production research to M036;
- preserved separate future Binance test/private and live-capital assessments.

Acceptance verified:

- no deployment phase bypasses local verification or restore proof;
- Render remains an API host rather than the scheduler;
- free tiers remain best effort and not SLA claims;
- live trading is not a deployment target.

## [x] S21.4 Align Production Development Documentation

Completed:

- mapped performance/data/research/incident/change governance to M030–M034;
- mapped post-experiment decision and isolated staging to M035;
- mapped protected production research to M036;
- required immutable artifact, migration, restore, security/privacy, SLO, cost, incident, support, and rollback evidence;
- required material post-launch changes to use M034 governance.

Acceptance verified:

- production research means production-quality paper research;
- favorable performance cannot skip staging or approvals;
- future exchange-credential work requires a separate milestone;
- no current production task creates a live-order path.

## [x] S21.5 Align Free-Cloud Documentation

Completed:

- mapped free-cloud deployment requirements to M028;
- mapped experiment requirements to M029;
- stated that M001–M027 precede cloud provisioning;
- preserved one-shot CLI, REST data, locks/leases, deterministic idempotency, safe degradation, and no imagined trades;
- aligned export/restore, preflight, budget, financial-integrity, observability, and experiment-closure gates.

Acceptance verified:

- cloud tasks are not the repository entry point;
- no local computer is required for scheduled cycles;
- missing or delayed cycles never create imagined trades;
- no automatic provider upgrade, purchase, scaling, private exchange, or live-execution path exists.

## [x] S21.6 Verify Task and Lifecycle Cross-References

Verified GitHub commits:

- `7a64dbefbecc4620299e172df13158f7c789f740` — Sprint 21 task catalog;
- `8e456bc66c8bc711ce694c3c40f62a325596fc0e` — task catalog index;
- `8a76c2697a4b10b45db007ab57f7444fcb8304b3` — testing strategy mapping;
- `40939947897b860878db5d66d9e5e88614f80f67` — deployment lifecycle mapping;
- `65ef0b84ab9d811d5fa850fb224ad1b61e109831` — production-development mapping;
- `9f4153107ab03b6e3738bf988bae60f48401b66c` — free-cloud architecture mapping;
- `36b6a6d609d6552d2cda2c26f0cc83d8e2ed4666` — free-cloud requirements mapping;
- `0da734ad071a2d08463a4615f3060fd87ae2a925` — README task-index entry;
- `e9d96d6fa143158251a0853776bc4feb3e45b7c7` — AGENTS task-index workflow;
- `1f4ff767c99e153bef2e7395ee3cb7b9992a6764` — ROADMAP catalog mapping;
- `a2af5936eb283822ef44e139e093508d4ed0add3` — implementation governance mapping;
- `6b2d83720f82ec54e3ecb7e7b5369162c14ad011` — documentation audit;
- `aaa08a1453ccc32d3811438ddb464cd900b48a2f` — changelog.

Verification performed:

- every listed commit was fetched from GitHub after creation;
- synchronized documents were fetched from `main`;
- task selection starts with M001 and uses the task catalog index;
- M026–M029 and M030–M036 lifecycle gates agree across testing, deployment, free-cloud, production-development, ROADMAP, README, AGENTS, and audit documents;
- no canonical dependency cycle remains;
- no Sprint 21 document authorizes deferred infrastructure, private Binance execution, Binance test orders, leverage, derivatives, shorting, custody, withdrawals, or live trading.

## Sprint 21 Definition of Done

- [x] `docs/TASK_CATALOG_INDEX.md` exists;
- [x] testing, deployment, free-cloud, and production-development documents use the Master Task lifecycle;
- [x] detailed task IDs remain usable as acceptance references but cannot override `TASKS.md`;
- [x] README, AGENTS, ROADMAP, execution governance, audit, and changelog include the catalog index;
- [x] all Sprint 21 content commits were fetched and verified;
- [x] implementation still starts with M001;
- [x] product implementation remains not started and no documentation-only task is misreported as product completion.

## Developer Handoff

```text
1. Read AGENTS.md
2. Read docs/IMPLEMENTATION_EXECUTION_PLAN.md
3. Open TASKS.md and select M001
4. Use docs/TASK_CATALOG_INDEX.md to select detailed cards
5. Implement and verify M001 before dependent work
```
