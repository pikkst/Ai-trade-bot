# Observability

Last reviewed: 2026-07-31
Status: Authoritative observability profile for the free-cloud MVP

## Objectives

The operator must know whether scheduled cycles are running, data is fresh, Gemini is valid and within budget, risk controls are active, and paper accounting reconciles.

## MVP Signals

The free-cloud profile uses:

- structured JSON logs from FastAPI and the research-cycle CLI;
- GitHub Actions run history, logs, and diagnostic artifacts;
- Render service logs and health endpoints;
- Supabase database/Auth logs;
- persistent `research_cycles`, audit events, data-quality events, halts, and reconciliation records;
- frontend status views.

Hosted Prometheus and Grafana are deferred and must not be represented as completed MVP work.

## Persistent Cycle Status

Every scheduled cycle stores:

- cycle ID and stable occurrence key;
- environment and experiment ID;
- intended and actual start time;
- finish time and duration;
- GitHub run/attempt identifiers when available;
- status and stable error code;
- snapshot, analysis, strategy, risk, order, and reconciliation references;
- data freshness and Gemini outcome;
- whether the database lock was acquired;
- summary safe for display.

## Required UI Status

The frontend shows:

- current experiment state;
- last successful and last attempted cycle;
- next expected cycle as an estimate, not a guarantee;
- latest finalized candle and freshness;
- Gemini provider/budget status;
- risk halt and reconciliation status;
- Render API cold-start/loading state;
- explicit paper/simulation label.

## Logging

Required bounded fields include timestamp, level, service, environment, event, correlation ID, cycle ID, experiment ID, entity type/ID, outcome, duration, and stable error code.

Never log secrets, tokens, cookies, database URLs, authorization headers, raw prompt bodies, or unrestricted provider responses.

## Key Events

- cycle scheduled, started, lock acquired/rejected, completed, failed;
- candle fetch, gap detection/repair, stale-data rejection;
- Gemini request, retry, completion, quota, safety, schema, and provider failures;
- strategy intent and risk outcome;
- order/fill/ledger transitions;
- reconciliation success/mismatch;
- experiment state changes;
- database export and restore drill;
- API startup, readiness, authentication, and authorization failures.

## Critical Conditions

- reconciliation mismatch;
- ledger posting failure;
- database unavailable during a cycle;
- duplicate side-effect suspicion;
- experiment/risk halt;
- migration mismatch;
- repeated authentication or secret failure.

Critical integrity conditions remain visible until reviewed.

## Warning Conditions

- missed/delayed cycle;
- stale or incomplete market data;
- repeated GitHub workflow failure;
- Gemini quota, rate-limit, schema, or safety failure spike;
- API cold-start or error-rate issue;
- database nearing free-tier storage limit;
- Supabase inactivity/pause risk;
- export cadence missed.

## Health Endpoints

- `/health/live`: process responsiveness only;
- `/health/ready`: database, migration revision, required configuration, and Auth verification dependencies.

Render sleeping is not a paper-cycle failure because scheduling runs independently through GitHub Actions.

## Runbooks Required Before Experiment

- GitHub scheduled cycle failed or delayed;
- Supabase unavailable or paused;
- Render cold start or deploy failure;
- Binance data stale;
- Gemini unavailable/quota exhausted;
- risk halt;
- ledger reconciliation mismatch;
- duplicate workflow suspicion;
- database export and restore;
- experiment halt and evidence collection.

## Retention and Exports

Operational provider logs follow free-tier provider limits and are not the sole audit record. Durable audit/cycle records live in PostgreSQL. Export the database before experiment start and at a documented cadence.

## Future Metrics Stack

Prometheus, Grafana, alert rules, and OpenTelemetry remain documented future upgrades. Introduce them only after measured need and an ADR. When introduced, exact metric names and dashboard definitions must be version-controlled.

## Testing

Tests verify log fields/redaction, cycle status persistence, delayed/duplicate workflow behavior, frontend freshness calculations, critical event persistence, export/restore procedure, and bounded identifiers.

## Related Documents

- `FREE_CLOUD_ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `ARCHITECTURE.md`
- `SECURITY.md`
- `../CLOUD_MVP_TASKS.md`
