# Documentation Audit

Last reviewed: 2026-08-01  
Audit scope: governance entry points, active architecture, environment lifecycle, task catalogs, Sprint 3–21 workstreams, and implementation handoff  
Status: Sprint 20–21 synchronization complete; product implementation remains not started

## 1. Executive Result

The repository now defines one canonical implementation path:

```text
M001–M006   Repository and local foundation
M007–M013   Core research domains
M014–M025   API, product workspaces, governance, and developer evidence
M026–M027   Integrated local/CI verification, export, restore, recovery, and security gate
M028        Free-cloud deployment
M029        Controlled 30-day paper experiment
M030–M034   Performance, data, research, incident, and change governance
M035        Post-experiment decision and staging readiness
M036        Production research launch and continuous operations
```

`TASKS.md` is the sole authority for execution order and hard dependencies. `docs/TASK_CATALOG_INDEX.md` maps detailed IDs and catalogs to Master Tasks and classifies work as mandatory, conditional, deferred, superseded, future assessment, or documentation complete.

The product remains an evidence-driven research, backtesting, and paper-trading platform. No current document authorizes private Binance execution, Binance test orders, live capital, leverage, margin, derivatives, shorting, custody, or withdrawals.

## 2. Correction to the 2026-07-31 Audit

The earlier audit stated that documentation was fully coherent for implementation. That conclusion was incomplete.

The active architecture already specified a free-cloud one-shot model, while the former root backlog still contained mandatory work for:

- Redis;
- ARQ;
- persistent workers;
- Binance WebSocket ingestion;
- Prometheus;
- Grafana;
- a Docker Compose topology built around those services.

The old task system also allowed root, cloud, local/production, UX, and Sprint files to appear as competing entry points and included environment-dependent or cyclic relationships such as local Supabase guidance depending on cloud provisioning.

Sprint 20 corrected the canonical backlog and contributor entry points. Sprint 21 corrected residual task-catalog and environment-lifecycle cross-references.

## 3. Canonical Authority

Implementation precedence is consistently defined as:

1. security, privacy, financial-integrity, and fail-closed requirements;
2. `AGENTS.md`;
3. `docs/PRODUCT_REQUIREMENTS.md`;
4. accepted architecture documents and ADRs;
5. domain and workspace implementation specifications;
6. `TASKS.md` for order and hard dependencies;
7. detailed task cards mapped by `docs/TASK_CATALOG_INDEX.md`;
8. existing implementation conventions.

Material conflicts must be corrected. Contributors must not choose a document based on recency, convenience, or shorter scope.

## 4. Authoritative Entry Points

| File | Authority |
|---|---|
| `/AGENTS.md` | Mandatory contributor and coding-agent rules |
| `/TASKS.md` | Canonical M001–M036 sequence |
| `/docs/IMPLEMENTATION_EXECUTION_PLAN.md` | Task governance, stages, status, evidence, and completion |
| `/docs/TASK_CATALOG_INDEX.md` | Detailed task mapping and classification |
| `/CONTRIBUTING.md` | Branch, PR, review, and verification workflow |
| `/README.md` | Product orientation and implementation entry point |
| `/ROADMAP.md` | Phase outcomes mapped to Master Tasks; not a backlog |
| `/SPRINT_20_TASKS.md` | Canonical-backlog synchronization evidence |
| `/SPRINT_21_TASKS.md` | Catalog and lifecycle synchronization evidence |

All entry points instruct the developer to begin with `M001`.

## 5. Detailed Task Catalog Policy

Detailed acceptance catalogs include:

- `UX_DESIGN_TASKS.md`;
- `CLOUD_MVP_TASKS.md`;
- `LOCAL_AND_PRODUCTION_TASKS.md`;
- `SPRINT_3_TASKS.md` through `SPRINT_21_TASKS.md`.

Rules:

- detailed files do not define independent implementation order;
- a “Ready for implementation” status means the acceptance contract is drafted, not that dependencies are verified;
- mandatory and conditional cards are selected through the mapped Master Task;
- deferred, superseded, and future-assessment cards remain excluded unless separately activated;
- documentation sprint completion does not complete a product Master Task;
- only a Master Task marked `VERIFIED` with implementation evidence is complete.

## 6. Active Runtime Profile

The active profile is consistent across README, AGENTS, TASKS, ROADMAP, architecture, backend, testing, deployment, free-cloud, and production-development documents:

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

The following are excluded from mandatory M001–M036 implementation:

- Redis and ARQ;
- persistent workers;
- Binance WebSocket ingestion;
- hosted Prometheus and Grafana;
- Kubernetes;
- automatic paid infrastructure or scaling;
- Binance test/private credentials;
- live trading.

Activation requires measured need, M034 change governance, ADR, updated requirements/tasks, migration and rollback, security/privacy review, tests, cost/capacity evidence, staged paper verification, and owner approval. Exchange credential or real-capital work additionally requires a separate future milestone.

## 8. Dependency Audit

Resolved canonical rules include:

- local Supabase/PostgreSQL/Auth does not depend on a cloud project;
- local bootstrap and deterministic fakes precede protected provider and cloud workflows;
- domain contracts precede consuming APIs and UI workspaces;
- ledger and reconciliation precede final portfolio and experiment status;
- the one-shot CLI precedes scheduled cloud execution;
- M026 and M027 precede M028;
- M028 precedes M029;
- current export and tested restore precede experiment start and production promotion;
- measured evidence precedes SLO, capacity, cost, or scaling claims;
- M030–M034 precede staging approval;
- untouched-test, robustness, reproducibility, paper observation, and owner review precede strategy promotion;
- behavior changes apply only to future configurations and never mutate a running experiment.

No canonical dependency cycle remains.

## 9. Task Catalog Coverage

| Catalog area | Master mapping |
|---|---|
| legacy repository/tooling tasks | M001–M006 |
| market, AI, strategy, risk, execution, portfolio, cycle, backtest | M007–M013 |
| API and authorization | M014 |
| frontend shell/component tasks | M004, M015 |
| Today’s Roast and evidence workspaces | M016–M022 |
| Auth/governance/release | M023 |
| product shell/onboarding/search/Trust/i18n | M024 |
| developer portal/documentation traceability | M025 |
| integrated verification and recovery | M026–M027 |
| cloud tasks C1–C6 | M028 |
| cloud tasks C7–C8 | M029 |
| performance/data/research/incident/change workspaces | M030–M034 |
| local/staging/production task catalog | M001–M006, M026–M027, M035–M036 |
| Sprint 20–21 synchronization | documentation governance complete |

Every active detailed catalog has a Master Task mapping in `docs/TASK_CATALOG_INDEX.md`.

## 10. Environment Lifecycle

The synchronized environment path is:

```text
Local implementation
  -> Integrated local/CI verification
  -> Export/restore/recovery/security gate
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
- explicit simulation and paper labels;
- analytical confidence distinct from probability of profit;
- deterministic strategy and risk around probabilistic AI;
- Decimal financial arithmetic and UTC timestamps;
- immutable used inputs, configurations, and behavior sets;
- idempotent side effects;
- deny-by-default browser access;
- no secrets in source, prompts, bundles, logs, metrics, screenshots, or artifacts;
- append-only ledger and reconciliation;
- tested restore before backup claims;
- human approval for material research, release, and behavior changes;
- no guaranteed-return, urgency, or financial-advice language;
- no automatic purchase, scaling, release, strategy promotion, or behavior activation.

## 12. Sprint 20 Changes

Added:

- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`;
- `SPRINT_20_TASKS.md`.

Materially synchronized:

- `TASKS.md`;
- `AGENTS.md`;
- `CONTRIBUTING.md`;
- `README.md`;
- `ROADMAP.md`;
- `docs/LOCAL_DEVELOPMENT.md`;
- `docs/TEST_ENVIRONMENTS.md`;
- this audit;
- `CHANGELOG.md`.

## 13. Sprint 21 Changes

Added:

- `docs/TASK_CATALOG_INDEX.md`;
- `SPRINT_21_TASKS.md`.

Materially synchronized:

- `docs/TESTING.md`;
- `docs/DEPLOYMENT.md`;
- `docs/PRODUCTION_DEVELOPMENT.md`;
- `docs/FREE_CLOUD_ARCHITECTURE.md`;
- `docs/FREE_CLOUD_REQUIREMENTS.md`;
- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`;
- `AGENTS.md`;
- `README.md`;
- `ROADMAP.md`;
- this audit;
- `CHANGELOG.md`.

## 14. Verified Sprint 20 Commits

- `a952f8f3636abae96cd10135463f61adc35609fd` — implementation execution plan;
- `2020ede10ce097d4c3b0fcd836bb0ff3b5a3d25c` — Sprint 20 catalog;
- `64d1b08e579499f3bc6833428172ca318de3dc49` — canonical `TASKS.md`;
- `10c5f252277e08f7d69d2657e85e057a68288b4d` — AGENTS alignment;
- `8de1c738454e8381e971e09c0da9e7e6f62a2f59` — README entry point;
- `47efdaae7d50b4ece42b6e5b1f08748d89474eb2` — ROADMAP mapping;
- `f7ee54fc28e42b52297d1ed267c91caafc5b55ca` — execution-plan update;
- `602cbe95bfa84166331061063d0395308ac52963` — audit correction;
- `ffdb786bc225510a2bfbb95ee35dcd3f1e495cf9` — changelog;
- `97551969ce4f4958a932f0e6283c8e842315e464` — CONTRIBUTING alignment;
- `1c67e7ffc205a25d4f733534fa4195c45a706546` — local-development alignment;
- `b06ebbb5f7088732f85d6e5b787bca1f22bb1390` — test-environment alignment;
- `8eb075ec64853d1f1648f574bfc931164d42a6f9` — Sprint 20 completion.

## 15. Verified Sprint 21 Commits

- `7a64dbefbecc4620299e172df13158f7c789f740` — Sprint 21 catalog;
- `8e456bc66c8bc711ce694c3c40f62a325596fc0e` — task catalog index;
- `8a76c2697a4b10b45db007ab57f7444fcb8304b3` — testing strategy mapping;
- `40939947897b860878db5d66d9e5e88614f80f67` — deployment lifecycle mapping;
- `65ef0b84ab9d811d5fa850fb224ad1b61e109831` — production-development mapping;
- `9f4153107ab03b6e3738bf988bae60f48401b66c` — free-cloud architecture mapping;
- `36b6a6d609d6552d2cda2c26f0cc83d8e2ed4666` — free-cloud requirements mapping;
- `0da734ad071a2d08463a4615f3060fd87ae2a925` — README catalog entry;
- `e9d96d6fa143158251a0853776bc4feb3e45b7c7` — AGENTS catalog entry;
- `1f4ff767c99e153bef2e7395ee3cb7b9992a6764` — ROADMAP catalog mapping;
- `a2af5936eb283822ef44e139e093508d4ed0add3` — execution-governance mapping.

Each listed commit was fetched from GitHub after creation.

## 16. Implementation-Dependent Artifacts

The following remain intentionally absent or incomplete until their mapped Master Tasks are implemented:

- backend and frontend source;
- dependency lock files and stable commands;
- Supabase config, migrations, RLS, functions, and seed data;
- GitHub Actions workflows;
- generated OpenAPI and frontend types;
- API, schema, error, event, permission, metric, migration, and test catalogs;
- automated documentation-health output;
- real cloud identifiers and public deployment URLs;
- provider smoke evidence;
- experiment, incident, performance, cost, data, and research-review evidence;
- export, backup, restore, and recovery artifacts;
- staging and production infrastructure selections;
- measured SLO, RPO, RTO, capacity, and cost results;
- security, privacy, accessibility, and operational review results.

These are M001–M036 implementation deliverables, not unresolved documentation decisions.

## 17. Rules for Future Changes

1. Start work through one `TASKS.md` Master Task.
2. Verify hard dependencies before editing.
3. Use `docs/TASK_CATALOG_INDEX.md` to select detailed cards.
4. Update task status and evidence with implementation.
5. Update affected specifications, generated contracts, database docs, tests, runbooks, and changelog in the same change.
6. Detect broken links, unknown IDs, conflicting scope, deprecated architecture terms, and generated drift in CI.
7. Never edit an applied migration.
8. Never represent documentation, coverage, a score, or a demo as implementation approval.
9. Preserve environment and credential isolation.
10. Keep Gemini advisory and all execution paper-only.
11. Treat restore, reconciliation, security, privacy, and incident evidence as promotion gates.
12. Process material behavior changes through M034.

## 18. Conclusion

The repository is documentation-ready for implementation from `M001` through `M036`.

The first developer action is:

```text
Open AGENTS.md
Open docs/IMPLEMENTATION_EXECUTION_PLAN.md
Open TASKS.md and select M001
Use docs/TASK_CATALOG_INDEX.md to select detailed cards
Implement and verify M001 before dependent work
```

No remaining task-order or environment-lifecycle conflict requires a developer to choose between competing MVP architectures or task entry points.
