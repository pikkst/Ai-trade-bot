# Deployment

Last reviewed: 2026-07-31
Status: Authoritative MVP deployment specification

## 1. Deployment Principles

- Environment isolation is mandatory.
- Infrastructure is reproducible and version-controlled.
- Secrets are injected at runtime.
- PostgreSQL is the authoritative state store.
- Redis is ephemeral and rebuildable.
- Migrations run as a controlled release step.
- Health checks gate traffic and workers.
- Rollback and restore procedures are documented and tested.
- Live trading remains disabled in every MVP environment.

## 2. Environments

### 2.1 Local Development

Purpose: development and deterministic testing.

Components:

- API;
- worker;
- scheduler;
- PostgreSQL;
- Redis;
- Prometheus;
- Grafana;
- React frontend;
- fake Gemini provider by default;
- optional real Gemini provider only through an explicit local override and personal development key.

Requirements:

- Docker Compose startup;
- safe placeholder secrets;
- public Binance data or fixtures;
- no private exchange credentials;
- development data volume clearly separated from other environments.

### 2.2 CI

Purpose: automated validation.

Components:

- ephemeral PostgreSQL and Redis;
- fake Binance and Gemini providers;
- backend and frontend build/test environments;
- security scanners;
- optional scheduled public-provider contract jobs with dedicated limits.

CI must not require a paid Gemini request for ordinary pull requests.

### 2.3 Persistent Research Sandbox

Purpose: continuous market-data ingestion, real Gemini analysis, paper trading, backtesting, dashboards, and the 30-day EUR 20 virtual experiment.

Requirements:

- dedicated Gemini project and API key;
- persistent PostgreSQL storage;
- encrypted backups;
- full metrics, dashboards, alerts, and runbooks;
- authenticated access;
- no public PostgreSQL or Redis exposure;
- no private Binance key;
- live trading disabled;
- owner-approved frozen experiment configuration.

### 2.4 Binance Test Environment

Purpose: future validation of private order lifecycle only after internal paper trading passes all gates.

This is a separate milestone, not part of the first MVP release. It requires restricted environment-specific credentials, reconciliation, credential rotation, and a separate owner approval.

### 2.5 Future Production

Not defined by the MVP. Before public SaaS or live trading, complete dedicated architecture, security, legal, privacy, operational, and financial-risk reviews.

## 3. Runtime Services

### `frontend`

Serves the React application or static build through a reverse proxy.

### `api`

Runs FastAPI/Uvicorn. Handles HTTP reads and commands. It does not run long backfills or backtests synchronously.

### `worker`

Runs ARQ jobs for market data, Gemini analysis, strategy/risk workflow, paper execution, reconciliation, backtesting, and reports.

### `scheduler`

Creates deterministic scheduled jobs. Only one active scheduler leader may create a given job occurrence.

### `postgres`

Authoritative relational database and ledger store.

### `redis`

Queue, locks, cache, and coordination. Not authoritative.

### `prometheus`

Scrapes application and infrastructure metrics.

### `grafana`

Displays dashboards and alert state.

### `reverse-proxy`

Optional in local development; required when exposing sandbox through HTTPS.

## 4. Network Architecture

- Only frontend/reverse proxy and approved API ports are externally reachable.
- PostgreSQL, Redis, workers, scheduler, Prometheus, and Grafana are private unless access is explicitly protected.
- Outbound access is limited to required Binance public and Google Gemini endpoints where practical.
- Environment networks and credentials are isolated.
- TLS is mandatory outside localhost.

## 5. Container Requirements

- pinned base-image versions or digests;
- minimal images;
- multi-stage builds;
- non-root runtime user where supported;
- read-only root filesystem where practical;
- explicit health checks;
- resource requests/limits where platform supports them;
- no secret baked into image layers;
- SBOM and Trivy scan before sandbox promotion;
- graceful shutdown for API and workers.

## 6. Configuration and Secrets

Configuration is supplied through environment variables or an approved secret manager.

Required separation:

- database credentials;
- Redis credentials;
- JWT signing secret;
- Gemini API key and project;
- environment name;
- AI budgets;
- risk limits;
- feature flags.

`GEMINI_MODEL` is configuration and must be recorded with experiment versions. Active Gemini quotas are observed from Google AI Studio and must not be assumed from static prose.

## 7. Database Migrations

Release procedure:

1. verify backup or snapshot;
2. verify current migration revision;
3. run migration validation;
4. stop incompatible workers if required;
5. apply new Alembic migrations once;
6. verify expected head revision;
7. run readiness and smoke checks;
8. resume workers.

Migrations must not run concurrently from every application replica.

## 8. Deployment Workflow

1. Build immutable artifacts.
2. Generate SBOM.
3. Run lint, types, tests, migrations, and security scans.
4. Record commit SHA, lock files, image digests, and migration revision.
5. Review release notes and rollback plan.
6. Back up database.
7. Deploy database migration job.
8. Deploy API, worker, scheduler, and frontend.
9. Verify liveness/readiness.
10. Run smoke and reconciliation checks.
11. Verify dashboards and alerts.
12. Mark release complete or execute rollback.

## 9. Rollback

Application rollback uses the previous immutable image when schema compatibility allows it.

Database rollback must not assume destructive downgrade support. Prefer forward fixes. If integrity is threatened, halt side effects, restore from a verified backup, reconcile ledger state, and document the incident.

Every release must state whether application rollback is compatible with the new migration.

## 10. Backups and Restore

Before the persistent sandbox is accepted:

- automated PostgreSQL backups are configured;
- backup encryption is enabled;
- retention is documented;
- at least one restore test has completed;
- restored migration revision is verified;
- ledger reconstruction and reconciliation pass;
- restore steps are in a runbook.

Redis backup is not relied upon for authoritative recovery.

## 11. High Availability

The initial research sandbox may use single instances, provided limitations are documented and backups are tested.

Future high availability may include managed PostgreSQL, multiple API and worker replicas, scheduler leader election, and redundant monitoring. Do not add complexity before measured need.

## 12. Resource Management

- backtests use dedicated queue and concurrency limit;
- Gemini jobs respect request, token, and cost budgets;
- market-data jobs have separate rate-limit-aware queue;
- worker memory limits protect the host;
- large exports stream or use generated artifacts rather than loading entirely in memory;
- resource exhaustion creates alerts and safe job failure.

## 13. Health and Smoke Tests

Post-deployment checks:

- liveness and readiness;
- database and migration revision;
- Redis and queue operation;
- fake or controlled Gemini adapter check without exposing key;
- Binance public server-time and bounded candle request;
- create/read a non-financial diagnostic job;
- metrics scrape;
- dashboard data;
- paper portfolio read and reconciliation;
- live-trading flag remains false.

## 14. Monitoring and Alerts

Sandbox deployment requires the dashboards and critical alerts from `OBSERVABILITY.md`, including database failure, stale market data, Gemini authentication/rate-limit issues, AI budget, risk halt, queue backlog, and reconciliation mismatch.

## 15. Promotion Gates

### Local to Persistent Sandbox

- P0 foundation, market-data, Gemini, strategy, risk, execution, accounting, security, and observability tasks complete;
- tests and scans pass;
- secrets isolated;
- backup and restore tested;
- no critical/high unresolved security issue without explicit exception;
- paper-trading smoke test passes.

### Persistent Sandbox to Binance Test Environment

- 30-day paper experiment completed or safely halted with report;
- zero unresolved reconciliation mismatch;
- zero duplicate financial side effect;
- decision lineage complete;
- risk and halt controls proven;
- separate private-API design and security review approved;
- owner explicitly approves progression.

## 16. Disaster and Incident Behavior

- integrity uncertainty: halt immediately;
- database unavailable: readiness fails and side effects stop;
- Redis unavailable: scheduling stops; authoritative state remains in PostgreSQL;
- Gemini unavailable: deterministic analysis or HOLD;
- Binance public data unavailable: stale-data policy blocks new decisions;
- monitoring unavailable: do not start a new formal experiment until restored.

## 17. Release Artifacts

Each release records:

- semantic release/version tag;
- Git commit SHA;
- Python and Node versions;
- dependency lock hashes;
- container image digests;
- SBOM;
- migration revision;
- prompt, Gemini schema, strategy, risk, feature-set, and execution-model versions;
- release notes;
- rollback compatibility;
- known issues.

## 18. Related Documents

- `ARCHITECTURE.md`
- `TECH_STACK.md`
- `SECURITY.md`
- `TESTING.md`
- `OBSERVABILITY.md`
- `GEMINI_INTEGRATION.md`
- `ROADMAP.md`
