# Task Catalog Index

Last reviewed: 2026-08-01  
Status: Authoritative mapping from detailed task catalogs to `TASKS.md` Master Tasks

## 1. Purpose

This index preserves the repository’s detailed UX, cloud, local/production, runtime-contract, and Sprint task cards while removing ambiguity about implementation order.

`TASKS.md` is the only execution-order and hard-dependency authority. A detailed task ID is selected only after its mapped Master Task is eligible to start.

## 2. Task Status Vocabulary

Detailed task mappings use:

- **Mandatory** — required to verify the mapped Master Task unless explicitly approved as not applicable;
- **Conditional** — required when the selected feature, environment, or risk profile uses it;
- **Deferred** — excluded from the active MVP; requires measured need, ADR, updated task mapping, tests, and owner approval;
- **Superseded** — the original implementation assumption is replaced by the active architecture, but compatible acceptance criteria may be retained;
- **Future assessment** — outside M001–M036 and requires a separate approved milestone;
- **Documentation complete** — specification exists, but product implementation remains not started until its Master Task is selected and verified.

## 3. Conflict Resolution

When a detailed task’s dependency, priority, configuration, or architecture conflicts with `TASKS.md`:

1. keep compatible acceptance criteria;
2. use the Master Task dependency and active architecture;
3. mark the incompatible implementation assumption superseded, deferred, or future assessment;
4. update the detailed catalog during implementation if the conflict affects developer execution;
5. never implement the old assumption silently.

Examples:

- Redis/ARQ worker orchestration is superseded for the MVP by the one-shot CLI and PostgreSQL lock/lease model;
- persistent WebSocket ingestion is deferred; finalized REST ingestion is mandatory;
- local Supabase work is M003 and does not depend on cloud project creation;
- hosted Prometheus/Grafana is deferred; durable cycle/audit/incident/reconciliation evidence is mandatory;
- environment variables provide wiring/bootstrap defaults and cannot mutate a running experiment;
- private Binance, Binance test execution, and live trading are future assessments.

## 4. Root and Documentation-Governance Catalogs

| Catalog | Master mapping | Classification | Notes |
|---|---|---|---|
| `TASKS.md` | M001–M036 | Mandatory authority | Defines order, dependencies, gates, and completion |
| `docs/IMPLEMENTATION_EXECUTION_PLAN.md` | M001–M036 | Mandatory governance | Defines task model and evidence |
| `docs/TASK_CATALOG_INDEX.md` | M001–M036 | Mandatory mapping | Maps detailed IDs and classifies scope |
| `AGENTS.md` | all tasks | Mandatory governance | Contributor safety and implementation rules |
| `CONTRIBUTING.md` | all tasks | Mandatory workflow | Branch, PR, review, and verification evidence |
| `SPRINT_20_TASKS.md` | documentation governance | Documentation complete | Created canonical implementation sequence |
| `SPRINT_21_TASKS.md` | documentation governance | Documentation complete | Aligned detailed catalogs and environment lifecycle |
| `SPRINT_22_TASKS.md` | documentation governance | In progress | Aligns runtime architecture, configuration, and observability |

## 5. Legacy Root Backlog Mapping

The former root `T*` tasks remain only in Git history and Master Task reference notes.

| Legacy area | Master Task | Classification |
|---|---|---|
| backend scaffold and package layout | M001 | Mandatory |
| dependency locking and quality tools | M002 | Mandatory |
| local Docker stack requiring Redis/worker/Prometheus/Grafana | M001–M003 | Superseded; only active local Supabase/application needs remain |
| GitHub quality workflow | M002 | Mandatory |
| settings, errors, logging, transactions, idempotency | M005 | Mandatory |
| database/migration/Auth/RLS baseline | M003 | Mandatory |
| Binance provider protocol | M006 | Mandatory |
| Binance REST metadata/candle ingestion | M007 | Mandatory |
| Binance WebSocket ingestion | future change through M034 | Deferred |
| snapshots and features | M008 | Mandatory |
| Gemini provider, schema, validation, and budget | M009 | Mandatory |
| deterministic strategy and risk | M010 | Mandatory |
| paper execution, ledger, portfolio, reconciliation | M011 | Mandatory |
| one-shot orchestration | M012 | Mandatory |
| backtesting and benchmarks | M013 | Mandatory |
| Redis/ARQ worker orchestration | future change through M034 | Deferred |
| hosted Prometheus/Grafana/OpenTelemetry backend | future change through M034 | Deferred |

## 6. Runtime Contract Mapping

| Contract | Master Tasks | Classification |
|---|---|---|
| `docs/ARCHITECTURE.md` | M001–M036 | Mandatory architecture |
| `docs/BACKEND.md` | M001–M014, M022–M036 | Mandatory backend boundary |
| `docs/TECH_STACK.md` | M001–M036 | Mandatory technology classification |
| `.env.example` | M001, M003–M005, M007–M012, M027–M031 | Mandatory safe variable inventory |
| `docs/OBSERVABILITY.md` | M005, M012, M014, M022, M026–M030, M033–M036 | Mandatory operations evidence |

Sprint 22 synchronizes these contracts. It does not implement their runtime components.

## 7. UX Design Catalog Mapping

| Detailed area | Master Task | Classification |
|---|---|---|
| UX foundations, product identity, design tokens | M004 | Mandatory |
| application shell and responsive navigation | M015 | Mandatory |
| core accessible components and financial formatting | M015 | Mandatory |
| Today’s Roast design and state matrix | M016 | Mandatory |
| market evidence and chart/table experience | M017 | Mandatory |
| Gemini analysis presentation | M018 | Mandatory |
| strategy/risk decision lineage | M019 | Mandatory |
| portfolio, orders, fills, ledger, reconciliation | M020 | Mandatory |
| backtest reporting and comparison | M021 | Mandatory |
| experiment operations, incidents, audit | M022 | Mandatory |
| governance, Auth, privacy, release views | M023 | Mandatory |
| onboarding, search, notifications, Trust Center, i18n | M024 | Mandatory |
| public demo/landing work | M024 and M028 | Conditional |
| visual regression, usability, accessibility completion | M026 | Mandatory |

`UX_DESIGN_TASKS.md` does not authorize frontend work before M004/M014/M015 dependencies.

## 8. Cloud MVP Catalog Mapping

| Detailed ID | Master Task | Classification | Canonical dependency note |
|---|---|---|---|
| C1 dedicated Supabase cloud project | M028 | Mandatory | follows M026–M027; not required locally |
| C2 cloud migrations, Auth, RLS | M028 | Mandatory | local foundation comes from M003 |
| C3 one-shot research-cycle CLI | M012 | Mandatory | implemented and verified locally first |
| C4 scheduled GitHub Actions cycle | M028 | Mandatory | depends on M012 and M027 |
| C5 Render FastAPI deployment | M028 | Mandatory | Render is API-only, not scheduler |
| C6 Cloudflare Pages deployment | M028 | Mandatory | consumes verified M014/M024 builds |
| C7 free-tier observability and backup procedure | M029 | Mandatory | restore foundation comes from M027 |
| C8 preflight and formal experiment start | M029 | Mandatory | requires M028 and exact frozen configuration |

Cloud rules:

- schedules are best effort;
- delayed/missed cycles use actual eligible data and never create imagined trades;
- no provider plan is automatically upgraded;
- Eventnexus Supabase is not reused;
- no local computer is required for scheduled operation;
- no private Binance or live execution exists.

## 9. Local and Production Catalog Mapping

### Local and CI cards

| Detailed ID | Master Task | Classification |
|---|---|---|
| L1.1 repository/bootstrap workflow | M001 | Mandatory |
| L1.2 local Supabase/PostgreSQL/Auth | M003 | Mandatory; cloud-independent |
| L1.3 stable cross-platform commands | M001/M002 | Mandatory |
| L1.4 deterministic provider fakes | M006 | Mandatory |
| L1.5 deterministic local demo | M026 | Mandatory |
| L2.1 unit/property tests | M002/M026 | Mandatory |
| L2.2 migration/constraint/Auth/RLS tests | M003/M026 | Mandatory |
| L2.3 provider/API contract tests | M006/M014/M026 | Mandatory |
| L2.4 frontend/accessibility/E2E tests | M015/M024/M026 | Mandatory |
| L2.5 security/documentation/generated checks | M002/M025/M026 | Mandatory |
| L2.6 export/restore/recovery gate | M027 | Mandatory |

### Staging and production cards

| Detailed area | Master Task | Classification |
|---|---|---|
| post-experiment owner decision | M035 | Mandatory |
| isolated staging foundation | M035 | Conditional on advancement decision |
| production-like migration/restore/E2E/load/failure validation | M035 | Mandatory for advancement |
| protected production-research release | M036 | Mandatory |
| production Auth/RLS/secrets/privacy/incident/SLO/cost hardening | M036 | Mandatory |
| post-launch operation and reviews | M036 | Mandatory continuous work |
| Redis/ARQ/persistent workers/WebSocket/managed observability upgrades | M034 then M036 | Conditional, measured need only |
| Binance test/private credential profile | separate future milestone | Future assessment |
| live-capital execution | separate future milestone | Future assessment |

## 10. Sprint Workspace Mapping

| Catalog | Master Task | Implementation status |
|---|---|---|
| `SPRINT_3_TASKS.md` — frontend application shell | M015 | Not started until dependencies verified |
| `SPRINT_4_TASKS.md` — core components | M015 | Not started until dependencies verified |
| `SPRINT_5_TASKS.md` — Today’s Roast | M016 | Not started |
| `SPRINT_6_TASKS.md` — Market Evidence | M017 | Not started |
| `SPRINT_7_TASKS.md` — Strategy and Risk | M010/M014/M019 | Not started |
| `SPRINT_8_TASKS.md` — Portfolio/Execution/Ledger/Reconciliation | M011/M014/M020 | Not started |
| `SPRINT_9_TASKS.md` — Backtest/Benchmark/Comparison | M013/M014/M021 | Not started |
| `SPRINT_10_TASKS.md` — Experiment Operations/Audit | M012/M014/M022 | Not started |
| `SPRINT_11_TASKS.md` — Gemini Analysis/Validation | M009/M014/M018 | Not started |
| `SPRINT_12_TASKS.md` — Auth/Governance/Security/Privacy/Release | M003/M014/M023 | Not started |
| `SPRINT_13_TASKS.md` — Product Shell/Onboarding/Search/Trust/i18n | M024 | Not started |
| `SPRINT_14_TASKS.md` — Developer Portal/Traceability | M025 | Not started |
| `SPRINT_15_TASKS.md` — Performance/Resilience/SLO/FinOps | M030 | Requires completed experiment evidence |
| `SPRINT_16_TASKS.md` — Data Lifecycle/Dataset Governance | M031 | Requires data domains and experiment evidence |
| `SPRINT_17_TASKS.md` — Research Review/Strategy Lifecycle | M032 | Requires M013 and M029–M031 |
| `SPRINT_18_TASKS.md` — Incident Response/Learning | M033 | Requires operational evidence |
| `SPRINT_19_TASKS.md` — Change Management/Staged Rollout | M034 | Requires governance/evidence foundations |
| `SPRINT_20_TASKS.md` — Canonical backlog synchronization | documentation governance | Completed and verified |
| `SPRINT_21_TASKS.md` — Catalog/lifecycle synchronization | documentation governance | Completed and verified |
| `SPRINT_22_TASKS.md` — Runtime contract synchronization | documentation governance | In progress |

A Sprint file’s `Ready for implementation` wording means its acceptance contract is drafted. It does not mean its Master Task dependencies are satisfied.

## 11. Environment Lifecycle Mapping

```text
M001–M006   Local foundation
M007–M025   Domains, API, UI, and governance
M026        Integrated local/CI verification
M027        Export, restore, recovery, security gate
M028        Free-cloud infrastructure and deployment
M029        Controlled paper experiment
M030–M034   Evidence hardening and governance
M035        Post-experiment decision and staging
M036        Production research
Future      Binance test/private credentials or live-capital assessment
```

No stage can be skipped because performance appears favorable.

## 12. Deferred Components

Excluded from mandatory M001–M036 implementation unless a later approved change activates them:

- Redis;
- ARQ;
- persistent worker platform;
- Binance WebSocket ingestion;
- hosted Prometheus/Grafana/OpenTelemetry backend;
- Kubernetes;
- automatic paid-plan purchase or scaling;
- private Binance credentials;
- Binance test orders;
- live trading;
- leverage, margin, futures, options, shorting, custody, or withdrawals.

Activation requires M034 proposal, behavior diff, impact, security/privacy, migration, cost/capacity, testing, staged paper verification, rollback, and owner approval. Exchange credential or live-capital changes additionally require a separate milestone.

## 13. Developer Selection Procedure

1. Open `TASKS.md`.
2. Select the earliest eligible Master Task.
3. Verify every hard dependency is `VERIFIED`.
4. Open this index and identify mapped detailed catalogs.
5. Select exact mandatory and applicable conditional cards.
6. Treat deferred, superseded, and future-assessment assumptions as excluded.
7. Implement, test, document, and record evidence.
8. Mark the Master Task `VERIFIED` only after all required evidence exists.

## 14. Completion Rule

Detailed-card completion is necessary but insufficient. A Master Task is complete only when:

- all mandatory cards are implemented or approved not applicable;
- integrated acceptance and failure cases pass;
- required security, privacy, accessibility, recovery, and financial invariants pass;
- documentation and generated artifacts are synchronized;
- the final commit or pull request is fetched and inspected;
- `TASKS.md` contains verification evidence.
