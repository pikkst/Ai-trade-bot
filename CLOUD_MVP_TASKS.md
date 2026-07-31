# Free Cloud MVP Tasks

Last reviewed: 2026-07-31
Status: Active infrastructure task sequence for the first 30-day experiment

This file supplements `TASKS.md`. For the free-cloud profile, these tasks replace the initial deployment assumptions that require Redis, ARQ, a persistent WebSocket worker, or hosted Prometheus/Grafana.

---

## [ ] C1 — Create a Dedicated Supabase Free Project

**Priority:** P0

### Description

Create a Supabase project dedicated to `pikkst/Ai-trade-bot` and document its non-secret identifiers and environment boundaries.

### User Story

As the project owner, I want an isolated managed PostgreSQL and Auth project, so that the trading experiment does not share data, credentials, migrations, or failure risk with another application.

### Acceptance Criteria

- A new Supabase project exists for AI Trade Bot.
- The project is not the existing Eventnexus project.
- The selected region and project reference are documented without exposing secrets.
- Database password, service-role key, JWT signing material, and connection strings are stored only in protected secret stores.
- `supabase/config.toml` is committed.
- `supabase/migrations/` exists.
- Production auto-deploy is disabled until migration CI is implemented.
- Free-tier limitations, inactivity pausing, and missing automatic-backup guarantees are acknowledged.

### Definition of Done

- Project isolation is verified.
- Local Supabase CLI can link to the project without committing credentials.
- A connectivity smoke test succeeds.
- `docs/FREE_CLOUD_ARCHITECTURE.md` and `.env.example` remain synchronized.

### Dependencies

- T1.1
- T1.2

### References

- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/SECURITY.md`

---

## [ ] C2 — Implement Supabase Migrations, Auth, and RLS Baseline

**Priority:** P0

### Description

Create the initial database migration, Supabase Auth integration, role mapping, and deny-by-default Row Level Security policies.

### User Story

As the portfolio owner, I want database access controlled at both API and database layers, so that browser credentials cannot mutate critical financial state.

### Acceptance Criteria

- Initial migrations create the approved foundational tables.
- Every Data API-visible table has RLS enabled.
- Browser roles cannot insert, update, or delete ledger entries, fills, risk decisions, AI runs, audit events, or experiment-control records.
- Owner, operator, and viewer identities map to documented application permissions.
- Approved read-only views exist for portfolio, analysis, experiment, and backtest summaries.
- Service-role usage is isolated to trusted server or workflow code.
- Migration reset from an empty local database succeeds.
- Authorization tests prove deny-by-default behavior.

### Definition of Done

- Migrations are committed.
- RLS tests pass for anonymous, viewer, operator, owner, and service roles.
- Generated schema documentation is updated.
- No secret appears in SQL or fixtures.

### Dependencies

- C1
- T2.3

### References

- `docs/DATABASE_SCHEMA.md`
- `docs/SECURITY.md`
- `docs/API_SPECIFICATION.md`

---

## [ ] C3 — Implement the Idempotent Research-Cycle CLI

**Priority:** P0

### Description

Implement a one-shot Python command that executes one complete hourly market-analysis and paper-trading cycle without requiring Redis or a continuously running worker.

### User Story

As the experiment operator, I want a restart-safe one-shot workflow, so that GitHub Actions can run the platform independently of my local computer.

### Acceptance Criteria

- Command is runnable as `python -m app.cli.run_research_cycle` or an equivalent documented entry point.
- A PostgreSQL advisory lock or database lease prevents overlapping cycles.
- The command fetches finalized Binance REST candles and repairs gaps.
- It creates a snapshot, features, optional Gemini analysis, strategy intent, risk result, paper execution, ledger entries, reconciliation, and audit records.
- A stable cycle key makes retries idempotent.
- Missing or stale data blocks entries.
- Gemini quota or provider failure follows deterministic fallback/HOLD policy.
- Integrity failure exits non-zero.
- The command does not require Redis, ARQ, WebSocket, Render, or a local filesystem.

### Definition of Done

- Unit, integration, duplicate-run, timeout, and restart tests pass.
- A complete fake-provider cycle runs in CI.
- A controlled real-provider smoke cycle is documented.
- Cycle status is queryable through the API.

### Dependencies

- C2
- T3.3
- T4.2
- T5.4
- T6.3
- T7.2

### References

- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/ARCHITECTURE.md`
- `docs/OBSERVABILITY.md`

---

## [ ] C4 — Add the Scheduled GitHub Actions Research Workflow

**Priority:** P0

### Description

Create a scheduled and manually dispatchable GitHub Actions workflow that runs the research-cycle CLI approximately once per hour.

### User Story

As the project owner, I want cloud scheduling through GitHub Actions, so that the 30-day experiment runs while my computer is off.

### Acceptance Criteria

- Workflow supports `schedule` and `workflow_dispatch`.
- Cron uses a non-zero minute offset.
- Workflow concurrency prevents overlapping environment cycles.
- Job timeout is configured.
- Python and dependencies are installed from the lock file.
- Supabase, Gemini, and configuration values come from GitHub Actions secrets or variables.
- Workflow permissions use least privilege.
- Secret values and prompt bodies are not logged.
- Failed runs preserve a concise diagnostic artifact or audit record.
- Normal pull-request CI does not call paid Gemini or production databases.

### Definition of Done

- Manual run succeeds against the research environment.
- Duplicate dispatch test does not duplicate a financial side effect.
- Scheduled run appears in Actions history.
- Failure and recovery procedure is documented.

### Dependencies

- C3
- T1.4

### References

- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`

### Notes

GitHub schedules are best-effort and may be delayed. This architecture is intentionally unsuitable for high-frequency or exact-second execution.

---

## [ ] C5 — Deploy FastAPI to Render Free

**Priority:** P0

### Description

Deploy the FastAPI application as a Render Free Web Service for authenticated reads and explicit commands.

### User Story

As a user, I want a public HTTPS API, so that the frontend can access the experiment without a local backend.

### Acceptance Criteria

- Render is connected to the GitHub repository.
- The service builds from a committed lock file or Dockerfile.
- Uvicorn binds to `0.0.0.0` and the platform-provided `PORT`.
- `/health/live` and `/health/ready` are configured.
- Secrets exist only in Render environment configuration.
- Local disk is not used for authoritative state.
- CORS allows only approved frontend origins.
- Cold-start behavior is visible in the UI and does not affect the GitHub Actions research cycle.
- The API does not start a duplicate scheduler or persistent worker.

### Definition of Done

- Public HTTPS API URL is documented as an environment value.
- Authentication and authorization smoke tests pass.
- Cold-start and restart tests preserve all authoritative state.
- Render free-tier limitations are documented.

### Dependencies

- C2
- T9.1
- T10.1

### References

- `docs/DEPLOYMENT.md`
- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/API_SPECIFICATION.md`

---

## [ ] C6 — Deploy the React Frontend to Cloudflare Pages

**Priority:** P1

### Description

Deploy the React/Vite application to Cloudflare Pages and connect it to Render and Supabase Auth.

### User Story

As the project owner, I want a public web interface, so that I can inspect and control the paper experiment from any device.

### Acceptance Criteria

- Cloudflare Pages is connected to the GitHub repository.
- Build root, build command, and output directory are documented.
- Frontend uses only `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, and the publishable Supabase key.
- No service-role, database, Gemini, JWT signing, or future Binance secret is present in the build.
- React Router refresh and fallback work.
- Authentication state works with Supabase Auth.
- Simulation mode, stale data, paused/halted state, and Render cold start are clearly shown.
- CSP, HTTPS, CORS, and error handling are tested.

### Definition of Done

- Public HTTPS frontend URL exists.
- A user can sign in and view authorized experiment data.
- Secret-scanning the built assets finds no server secret.
- Desktop and mobile smoke tests pass.

### Dependencies

- C5
- T11.1

### References

- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/API_SPECIFICATION.md`

---

## [ ] C7 — Implement Free-Tier Observability and Backup Procedures

**Priority:** P0

### Description

Implement database-backed cycle status, structured logs, GitHub/Render/Supabase operational review, and manual export/restore procedures without hosting Prometheus or Grafana.

### User Story

As the operator, I want sufficient visibility and recoverability on free services, so that failures do not silently invalidate the experiment.

### Acceptance Criteria

- Every research cycle stores start, finish, result, duration, error code, and correlation ID.
- Critical halt and reconciliation events are persisted.
- Render, GitHub Actions, and Supabase logs are documented as operational sources.
- The UI shows last successful cycle, data freshness, Gemini status, risk halt, and reconciliation status.
- A database export procedure is documented and tested.
- A restore into a separate test project or local Supabase instance is demonstrated.
- Formal experiment exports occur before start and at a documented cadence.
- Monitoring gaps are included in the final experiment report.

### Definition of Done

- Failure drill and restore drill pass.
- Runbooks are committed.
- Hosted Prometheus/Grafana tasks are explicitly deferred, not falsely marked complete.

### Dependencies

- C4
- C5

### References

- `docs/OBSERVABILITY.md`
- `docs/DEPLOYMENT.md`
- `docs/FREE_CLOUD_ARCHITECTURE.md`

---

## [ ] C8 — Run the Free-Cloud Preflight and Start the 30-Day Experiment

**Priority:** P0

### Description

Verify all free-cloud services, freeze the experiment configuration, and start the controlled EUR 20 virtual paper experiment.

### User Story

As the project owner, I want a documented preflight gate, so that the formal experiment starts only when cloud execution, safety, and recovery are proven.

### Acceptance Criteria

- Frontend, API, database, Auth, scheduled workflow, Binance REST, and Gemini allowance are checked.
- No local computer is required for scheduled cycles.
- Risk profile matches the approved EUR 20 configuration.
- Gemini monthly cost budget is EUR 0 unless explicitly changed.
- Live trading and private Binance access remain disabled.
- Migrations, RLS, idempotency, reconciliation, halt controls, export, and restore checks pass.
- Experiment configuration is immutable after start.
- Start time, planned end time, versions, service limitations, and owner approval are recorded.

### Definition of Done

- Preflight report is committed or stored as an auditable artifact.
- Experiment state is `RUNNING`.
- First scheduled cycle completes successfully.
- The public UI reports current experiment and freshness status.

### Dependencies

- C1 through C7
- T12.1

### References

- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/RISK_ENGINE.md`
- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `ROADMAP.md`
