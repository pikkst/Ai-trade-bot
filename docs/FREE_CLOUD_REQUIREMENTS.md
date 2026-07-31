# Free Cloud Requirements Addendum

Last reviewed: 2026-08-01  
Status: Authoritative addendum for `M028` free-cloud deployment and `M029` controlled paper experiment

## 1. Authority and Entry Boundary

This addendum refines `PRODUCT_REQUIREMENTS.md` for the first free-cloud demonstration and formal 30-day paper experiment.

`TASKS.md` remains the only implementation-order authority.

- M001–M027 must be verified before M028 cloud deployment.
- M028 must be verified before M029 experiment preflight and start.
- Local Supabase, normal CI, deterministic fakes, export, and restore do not depend on a cloud project.
- Cloud tasks are not the repository implementation entry point.

Where this addendum conflicts with older deployment, scheduling, ingestion, or hosted-observability assumptions for the free-cloud profile, this addendum and `FREE_CLOUD_ARCHITECTURE.md` control.

## 2. M028 Deployment Requirements

- FCR-DEP-001: The deployed demo must run without the owner’s local computer.
- FCR-DEP-002: The selected initial infrastructure must require no recurring monthly payment to begin the experiment.
- FCR-DEP-003: The system must not automatically upgrade a plan, purchase resources, scale infrastructure, or increase a provider budget.
- FCR-DEP-004: The UI, Trust Center, and documentation must disclose that free services provide no SLA.
- FCR-DEP-005: A dedicated Supabase project must be used; the Eventnexus or any unrelated database project must not be reused.
- FCR-DEP-006: FastAPI must deploy to Render Free and remain stateless outside authoritative managed storage.
- FCR-DEP-007: The React/Vite frontend must deploy to Cloudflare Pages using an explicit public-variable allowlist.
- FCR-DEP-008: Deployment artifacts must map to a verified source revision, dependency lock set, migration head, and generated contract hashes.
- FCR-DEP-009: HTTPS, approved domains, CORS, CSP, SPA fallback, Auth redirects, environment labels, and client-bundle secret absence must be verified.
- FCR-DEP-010: Render must host reads and explicit commands only; it must not become the authoritative scheduler or start a duplicate worker.

## 3. Scheduling Requirements

- FCR-SCH-001: GitHub Actions must execute a one-shot research cycle approximately hourly using a best-effort schedule.
- FCR-SCH-002: Scheduled work must not depend on Render being awake or on the owner’s computer.
- FCR-SCH-003: Workflow concurrency plus a PostgreSQL lock or durable lease must prevent overlapping side effects.
- FCR-SCH-004: Every logical occurrence must have a stable idempotency key and a canonical cycle identity.
- FCR-SCH-005: Intended time, actual start, completion time, delay, missed occurrence, workflow run, and attempt identifiers must be persisted when available.
- FCR-SCH-006: Schedule delays and missed runs must be recorded and surfaced.
- FCR-SCH-007: The system must never invent, backdate, or reconstruct simulated trades for a missed cycle.
- FCR-SCH-008: A delayed cycle must use actual eligible finalized market data, not the intended cron timestamp.
- FCR-SCH-009: Lock rejection, duplicate delivery, timeout, cancellation, partial failure, and recovery must be machine-readable.
- FCR-SCH-010: Successful workflow process exit alone must not mark a financial cycle complete; required stages, ledger posting, and reconciliation must complete.

## 4. Market Data Requirements

- FCR-MD-001: The active free-cloud MVP uses Binance Spot public REST and finalized candles.
- FCR-MD-002: Every cycle performs server-time, continuity, finalization, quality, ordering, and freshness checks.
- FCR-MD-003: Gaps are repaired through bounded, checkpointed, idempotent REST backfill.
- FCR-MD-004: Persistent WebSocket ingestion is not required for M028 or M029.
- FCR-MD-005: Stale, invalid, incomplete, gapped, or provider-unavailable evidence must block new entry actions according to the frozen policy.
- FCR-MD-006: Finalized source corrections must create explicit quality, replacement, invalidation, and downstream lineage evidence rather than silently rewriting history.
- FCR-MD-007: Provider limits and retry guidance must be obtained from current approved evidence rather than hard-coded prose values.

## 5. Database, Auth, and RLS Requirements

- FCR-DB-001: Supabase-managed PostgreSQL is authoritative for the cloud profile.
- FCR-DB-002: Supabase Auth provides identity; FastAPI enforces application authorization.
- FCR-DB-003: RLS must be enabled on all Data API-visible objects and deny access by default.
- FCR-DB-004: Browser writes to financial, AI, audit, experiment-control, governance, incident, release, and access-control tables are prohibited.
- FCR-DB-005: Only approved RLS-protected read views or FastAPI resources may be queried by the frontend.
- FCR-DB-006: Committed immutable migrations must rebuild a fresh database deterministically and reach one expected head.
- FCR-DB-007: Service-role and direct database credentials must remain server/workflow-only.
- FCR-DB-008: Application, workflow/service, read-only, and migration identities must remain scoped and separated.
- FCR-DB-009: Workspace isolation and browser direct-write denial must be tested in local CI and against the cloud profile before acceptance.
- FCR-DB-010: Database unavailability, migration mismatch, or RLS assurance failure must fail closed.

## 6. Export, Restore, and Recovery Requirements

- FCR-REC-001: M027 must demonstrate logical export and isolated restore before M028 is accepted.
- FCR-REC-002: Export and restore evidence must be current before M029 preflight and experiment start.
- FCR-REC-003: An export must record environment, source revision, migration head, configuration scope, timestamp, hash, and protected storage reference.
- FCR-REC-004: A restore must run in an isolated local or separate project environment.
- FCR-REC-005: Restore verification must include migration state, required evidence hashes, portfolio rebuild, append-only ledger preservation, and reconciliation.
- FCR-REC-006: A provider backup claim must not be accepted solely from provider configuration or documentation; successful restore evidence is required.
- FCR-REC-007: Export, backup, restore, or reconciliation failure must block experiment start or continuation according to policy.
- FCR-REC-008: Recovery must never fabricate missing market events, AI reports, decisions, orders, fills, ledger entries, or audit evidence.

## 7. Gemini and Budget Requirements

- FCR-AI-001: Gemini remains optional advisory evidence and cannot execute commands or mutate state.
- FCR-AI-002: Gemini receives only approved minimum structured evidence and no secrets, personal data, credentials, or unrelated private content.
- FCR-AI-003: Provider success and application validation acceptance must remain separate.
- FCR-AI-004: Malformed, stale, unsupported, injected, refused, safety-blocked, empty, or otherwise invalid output must be rejected.
- FCR-AI-005: Timeout, rate limit, outage, invalid output, or exhausted budget must use the frozen deterministic fallback or HOLD policy.
- FCR-AI-006: Gemini request, token, and cost budgets must be enforced before each request.
- FCR-AI-007: The first formal experiment defaults to a Gemini monthly cost budget of EUR 0 unless an explicit versioned owner-approved configuration changes it.
- FCR-AI-008: The platform must not automatically enable paid Gemini use or upgrade a provider plan.
- FCR-AI-009: Prompt, schema, safety, validation, provider configuration, attempts, usage, cost estimate, and fallback lineage must be persisted.

## 8. Paper Execution and Financial Integrity Requirements

- FCR-FIN-001: Every actionable strategy intent must pass deterministic risk.
- FCR-FIN-002: One approved risk evaluation may create at most one paper order.
- FCR-FIN-003: Fees, spread, slippage, precision, minimum notional, partial fills, cancellation, and conservative timing must remain enabled through immutable execution-model versions.
- FCR-FIN-004: Order transition, fill, ledger, audit/outbox, and projection effects must commit atomically.
- FCR-FIN-005: The append-only double-entry ledger is the financial source of truth.
- FCR-FIN-006: Portfolio state must rebuild and reconcile to the ledger.
- FCR-FIN-007: Reconciliation or financial-integrity mismatch must create a critical event and halt new entry activity.
- FCR-FIN-008: Every displayed order, fill, balance, P&L value, return, and benchmark result must be labeled simulated.
- FCR-FIN-009: Live/private exchange execution, leverage, margin, futures, options, shorting, custody, and withdrawals remain prohibited.

## 9. Observability Requirements

- FCR-OBS-001: Every cycle must persist occurrence identity, intended/actual timing, status, duration, safe error, data freshness, lock/idempotency, and domain-stage references.
- FCR-OBS-002: The frontend must display the latest attempted and successful cycle, next expected estimate, freshness, Gemini/fallback/budget, risk halt, reconciliation, dependency, incident, and environment state.
- FCR-OBS-003: GitHub Actions, Render, and Supabase logs are operational sources but never the sole audit record.
- FCR-OBS-004: Hosted Prometheus and Grafana are not required for M028 or M029 and must not be represented as completed.
- FCR-OBS-005: Integrity failures remain durably visible until reviewed and resolved through the incident process.
- FCR-OBS-006: Critical state must outrank positive performance in APIs, UI, notifications, and reports.
- FCR-OBS-007: Logs, metrics, traces, responses, exports, and artifacts must redact secrets and avoid unbounded sensitive labels.
- FCR-OBS-008: Free-tier cold start, pause, quota, schedule-delay, and retention limitations must be documented in the experiment report.

## 10. Free-Tier Failure Requirements

- FCR-FAIL-001: Render cold start or sleep must not stop scheduled execution.
- FCR-FAIL-002: Supabase unavailability or pause must prevent side effects and create visible operational evidence.
- FCR-FAIL-003: Binance stale or unavailable data must block entries.
- FCR-FAIL-004: Gemini quota or outage must use deterministic fallback or HOLD.
- FCR-FAIL-005: Local or ephemeral filesystem loss must not lose authoritative state.
- FCR-FAIL-006: Reconciliation mismatch must halt the experiment.
- FCR-FAIL-007: Secret exposure or authentication/RLS mismatch must create a release/experiment blocker and incident.
- FCR-FAIL-008: Lost or changed free quota must degrade safely and must not trigger automatic purchase or scale.
- FCR-FAIL-009: Missing evidence must never appear as healthy, empty success, or completed financial work.
- FCR-FAIL-010: An automatic safety halt must not resume automatically without the required review and command gates.

## 11. M028 Acceptance Gate

The free-cloud deployment is ready when:

- M001–M027 required work is verified;
- public HTTPS frontend and API URLs exist;
- dedicated Supabase, migrations, Auth, RLS, and workspace isolation are verified;
- the scheduled/manual CLI completes while the owner’s computer is off;
- duplicate or overlapping execution cannot duplicate side effects;
- Render cold start is handled and does not control the schedule;
- Cloudflare build, routing, CSP, CORS, Auth redirect, and secret allowlist checks pass;
- export and isolated restore remain valid;
- deployment revision, migration head, artifact hashes, limitations, and service boundaries are recorded;
- no live/private Binance execution capability exists.

M028 completion does not start the formal experiment automatically.

## 12. M029 Preflight and Experiment Gate

The controlled experiment may start only when:

- M028 is verified;
- current export and restore evidence exists;
- exact configuration and behavior-set hashes are frozen;
- virtual funding and initial portfolio reconciliation are verified;
- Binance public REST and finalized-candle freshness checks pass;
- Gemini mode, fallback, request/token/cost budgets, and secret configuration are valid;
- deterministic strategy, risk, execution, ledger, reconciliation, locks, and idempotency checks pass;
- GitHub workflow, Render API, Cloudflare frontend, Auth, RLS, incident controls, runbooks, and observability checks pass;
- no active halt or unresolved critical incident exists;
- live trading and private exchange credentials are absent;
- owner approval is recorded.

## 13. M029 Completion Gate

The experiment is verified only when:

- it reaches a documented terminal state after 30 calendar days or an approved early halt;
- all expected, attempted, successful, delayed, missed, duplicate, failed, recovered, and invalidated cycle evidence is preserved;
- no duplicate financial side effect occurred;
- final portfolio and ledger reconcile;
- incidents, halts, provider/free-tier limitations, and missing cycles are reported;
- final export and restore evidence is current;
- cash and buy-and-hold benchmarks are included using comparable assumptions;
- final report and owner closure decision exist;
- profit, outperformance, or Gemini confidence is not used as completion proof.

## 14. Promotion Boundary

M029 does not authorize staging or production directly.

Required next sequence:

- M030 performance, resilience, SLO, quota, cost, and capacity evidence;
- M031 data lifecycle and dataset governance;
- M032 research review and strategy lifecycle;
- M033 incident response and learning;
- M034 governed behavior changes and staged paper rollout;
- M035 post-experiment decision and isolated staging;
- M036 production research.

## 15. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `PRODUCT_REQUIREMENTS.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `TEST_ENVIRONMENTS.md`
- `SECURITY.md`
- `OBSERVABILITY.md`
- `../CLOUD_MVP_TASKS.md`
