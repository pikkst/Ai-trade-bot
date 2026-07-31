# Observability

Last reviewed: 2026-07-31
Status: Authoritative MVP observability specification

## 1. Objectives

Observability must make it possible to answer:

- Is the platform healthy and ready?
- Is market data complete and fresh?
- Are Gemini requests succeeding, valid, within budget, and properly rejected when unsafe?
- Are strategy and risk decisions behaving as configured?
- Are paper orders, fills, and ledger entries consistent?
- Can every important action be traced end to end?
- Is the 30-day experiment operating safely?

## 2. Signals

The MVP uses:

- structured JSON logs;
- Prometheus metrics;
- Grafana dashboards;
- immutable audit events;
- health endpoints;
- alert rules and runbooks;
- optional OpenTelemetry-compatible tracing after instrumentation value is demonstrated.

Audit events and operational logs are different. Audit events are durable business evidence. Logs are operational diagnostics.

## 3. Correlation and Traceability

The following identifiers must propagate where relevant:

- correlation ID;
- HTTP request ID;
- background job ID;
- workspace ID;
- experiment ID;
- market snapshot ID;
- analysis ID;
- strategy evaluation ID;
- risk evaluation ID;
- order ID;
- fill ID;
- portfolio ID;
- backtest ID.

Identifiers may appear in structured logs, but must not be used as unbounded Prometheus labels.

## 4. Logging Standard

Required fields:

```json
{
  "timestamp": "2026-07-31T12:00:00Z",
  "level": "INFO",
  "service": "worker",
  "environment": "sandbox",
  "event": "ai_analysis_completed",
  "correlation_id": "uuid",
  "workspace_id": "uuid",
  "job_id": "uuid",
  "entity_type": "ai_analysis",
  "entity_id": "uuid",
  "outcome": "success",
  "duration_ms": 842,
  "error_code": null
}
```

Never log secrets, API keys, JWTs, cookies, signatures, database credentials, unrestricted prompts, or raw sensitive provider responses.

## 5. Log Events

At minimum, emit stable event names for:

- application startup and shutdown;
- configuration validation failure;
- migration state check;
- authentication success/failure;
- authorization denial;
- market ingestion start/success/retry/failure;
- WebSocket connect/disconnect/reconnect;
- data gap detected/repaired;
- snapshot creation/rejection;
- feature calculation completion/failure;
- Gemini request start/retry/completion/failure;
- Gemini schema validation and safety rejection;
- AI budget reservation/commit/rejection;
- strategy intent creation;
- risk approval/reduction/rejection/halt;
- paper order transitions;
- paper fill creation;
- ledger transaction posting;
- reconciliation success/mismatch;
- backtest start/progress/completion/failure;
- experiment transition;
- alert activation and resolution.

## 6. Metric Naming

Use a stable project prefix such as `ai_trade_bot_`. Exact names must be implemented and checked into `docs/metrics.md` by the corresponding task.

Counter suffix: `_total`.

Duration metrics: seconds.

Sizes and values include explicit units.

Labels must be bounded, such as environment, service, provider, model category, symbol from an approved bounded list, interval, status, outcome, reason code, and job type.

## 7. Core Metrics

### Application and API

- request count by method, route template, and status;
- request duration histogram;
- active requests;
- error count by stable code;
- authentication and authorization failures;
- process CPU and memory;
- application build and migration revision info.

### PostgreSQL and Redis

- database pool utilization;
- query duration for selected operations;
- transaction failures and deadlocks;
- Redis connectivity;
- queue depth;
- oldest queued job age;
- job retries and terminal failures;
- worker concurrency utilization.

### Market Data

- last finalized candle timestamp;
- ingestion lag seconds;
- candles ingested;
- duplicate candles;
- missing intervals;
- stale snapshots;
- quality events by type and severity;
- WebSocket reconnects;
- backfill duration and failed pages.

### Google Gemini

- requests by outcome;
- request duration;
- retries;
- 429 and 5xx responses;
- authentication failures;
- safety blocks;
- refusals;
- empty responses;
- schema validation failures;
- unsupported-claim failures;
- input and output usage;
- estimated cost;
- daily/monthly budget utilization;
- valid-report rate.

Model identifiers must be normalized to a bounded configured set before use as labels.

### Strategy and Risk

- intents by action;
- evaluations by strategy version;
- risk outcomes;
- risk rejection reason codes;
- active portfolio/workspace halts;
- cooldown activations;
- drawdown threshold proximity.

### Paper Execution and Portfolio

- orders by state and type;
- fills and partial fills;
- cancellations and rejections;
- simulated fees and slippage;
- portfolio equity;
- realized/unrealized P&L;
- exposure;
- drawdown;
- reconciliation duration;
- reconciliation mismatches;
- ledger posting failures.

Financial gauges must be clearly labeled as paper/simulated and must avoid high-cardinality portfolio labels in shared Prometheus environments.

### Backtesting and Experiments

- backtest runs by outcome;
- backtest duration;
- replay events processed;
- experiment state;
- experiment uptime;
- experiment safety events;
- report generation success/failure.

## 8. Dashboards

### Platform Health

API health, worker health, scheduler health, PostgreSQL, Redis, CPU, memory, queue depth, and errors.

### Market Data Quality

Ingestion lag, latest candles, gaps, duplicates, stale data, reconnects, and backfill status.

### Gemini Operations

Requests, latency, status, schema success, safety blocks, retries, usage, cost, and budget utilization.

### Strategy and Risk

Intents, risk outcomes, rejection reasons, halts, cooldowns, and drawdown thresholds.

### Paper Portfolio

Equity, cash, exposure, P&L, fees, drawdown, orders, fills, and reconciliation state.

### 30-Day Experiment

Experiment state, elapsed days, data completeness, AI validity, decisions, safety events, portfolio metrics, and benchmark comparison.

Dashboard definitions must be version-controlled before sandbox promotion.

## 9. Alert Severity

### Critical

Immediate attention:

- reconciliation mismatch;
- ledger posting failure after fill;
- database unavailable;
- migration revision mismatch;
- repeated duplicate side-effect attempt;
- global or drawdown halt;
- secret/credential authentication failure in a configured environment;
- experiment state corruption.

### Warning

Prompt investigation:

- market data stale;
- ingestion lag above threshold;
- queue age/depth above threshold;
- Gemini schema failure spike;
- Gemini 429/5xx spike;
- AI budget above warning threshold;
- repeated WebSocket reconnect;
- elevated API error rate;
- backtest or report failure.

### Informational

- experiment started, paused, completed, or archived;
- configuration version activated;
- scheduled report completed.

## 10. Alert Design

Every alert must define:

- condition;
- duration/for clause;
- severity;
- affected component;
- user impact;
- safe first checks;
- automatic mitigation if any;
- escalation owner;
- runbook link;
- resolution condition.

Alerts should avoid flapping and duplicate notifications. Critical integrity alerts remain active until explicitly resolved.

## 11. Runbooks

Required runbooks before the 30-day experiment:

- PostgreSQL unavailable;
- Redis/queue unavailable;
- Binance market data stale;
- WebSocket reconnect storm;
- Gemini rate limited or unavailable;
- Gemini key authentication failure;
- AI budget exhausted;
- risk halt;
- ledger reconciliation mismatch;
- duplicate order/fill suspicion;
- experiment halt and evidence collection;
- backup restoration.

## 12. Health Endpoints

`/health/live` checks process responsiveness only.

`/health/ready` checks mandatory dependencies and migration state. It must fail for PostgreSQL unavailability or incompatible schema. Redis readiness depends on the process role.

Provider outages should not necessarily make the read API unready, but must make AI-dependent operations unavailable with a clear safe status.

## 13. SLO Design

Initial SLOs are design targets and must be replaced by measured values:

- API availability for read operations;
- market-data freshness;
- successful scheduled-job completion;
- analysis schema-valid rate;
- zero unresolved ledger reconciliation mismatch;
- zero duplicate financial side effect.

Profit and market performance are not operational SLOs.

## 14. Retention

- operational logs: default 30 days;
- Prometheus metrics: deployment-dependent, documented before sandbox;
- audit events: at least one year;
- critical incident evidence: preserved according to incident policy;
- raw Gemini responses: according to database retention policy.

## 15. Testing

Tests must verify:

- required fields exist in key logs;
- secrets are redacted;
- metric labels are bounded;
- job outcomes update metrics;
- Gemini failure paths emit distinct metrics;
- reconciliation mismatch emits alerting signal;
- dashboards load from version-controlled definitions;
- alert rules and runbook links are valid.

## 16. Related Documents

- `ARCHITECTURE.md`
- `BACKEND.md`
- `GEMINI_INTEGRATION.md`
- `SECURITY.md`
- `TESTING.md`
- `DEPLOYMENT.md`
