# API Specification

Last reviewed: 2026-07-31
Status: Authoritative design contract; generated OpenAPI becomes executable source of truth after implementation

## 1. General Conventions

- Base path: `/api/v1`
- Content type: `application/json`
- Authentication: Bearer access token for protected endpoints
- Timestamps: RFC 3339, timezone-aware UTC
- Monetary and quantity values: decimal strings, never JSON floating-point values
- Request correlation: accept or generate `X-Correlation-ID`
- Idempotent commands: require `Idempotency-Key`
- List responses: paginated with deterministic ordering
- Breaking public changes: new API version or explicit migration plan

## 2. Roles

- `owner`: full workspace configuration, experiment start/halt, policy administration
- `operator`: run ingestion, analysis, backtests, and paper operations within approved policy
- `viewer`: read-only access

Authorization is enforced in application handlers, not only in route dependencies or the frontend.

## 3. Standard Error Envelope

```json
{
  "error": {
    "code": "risk_rejected",
    "message": "The requested action was rejected by the active risk policy.",
    "correlation_id": "7e470bf2-f3fc-4e62-95ce-7f6f79a82581",
    "details": {
      "reason_codes": ["position_limit_exceeded"]
    }
  }
}
```

Safe details may be included. Stack traces, SQL, credentials, secrets, raw authorization data, and unrestricted provider payloads must never be returned.

## 4. Pagination

Cursor response:

```json
{
  "items": [],
  "page": {
    "next_cursor": null,
    "has_more": false
  }
}
```

Default and maximum page sizes must be configured and documented in generated OpenAPI.

## 5. Health

### `GET /health/live`

Purpose: process liveness only.

Authentication: none.

Success: `200` when the process event loop can respond.

### `GET /health/ready`

Purpose: readiness for traffic and background work.

Checks:

- configuration validated;
- PostgreSQL reachable;
- required migration revision present;
- Redis reachable when mandatory for this process;
- service not in unrecoverable startup state.

Returns `503` with safe component statuses when not ready.

## 6. Authentication

### `POST /auth/login`

Accepts validated credentials and returns a short-lived access token. Exact refresh-token design must be implemented only after a dedicated security decision.

### `GET /auth/me`

Returns authenticated user identity and effective roles.

## 7. Workspaces

### `POST /workspaces`

Role: owner.

Idempotency: required.

Creates a research workspace with name, base currency, allowed symbols, default interval, and safe disabled feature flags.

### `GET /workspaces/{workspace_id}`

Role: viewer or higher.

Returns workspace metadata and active configuration-version references. Secret values are never returned.

### `PATCH /workspaces/{workspace_id}`

Role: owner.

Updates mutable metadata only. Versioned strategy, risk, Gemini, or experiment configuration changes use dedicated version resources rather than silent in-place mutation.

## 8. Configuration Versions

### `POST /workspaces/{workspace_id}/configurations`

Role: owner.

Idempotency: required.

Creates an immutable configuration version containing references to:

- allowed symbols and intervals;
- feature-set version;
- Gemini provider configuration without secret value;
- prompt and report-schema versions;
- strategy version;
- risk-policy version;
- paper execution model;
- AI budgets.

### `GET /workspaces/{workspace_id}/configurations/{version_id}`

Returns the immutable configuration and hash.

## 9. Market Data

### `GET /market/symbols`

Role: viewer or higher.

Filters: exchange, base asset, quote asset, active status.

Returns normalized and exchange-native symbol information, precision, lot-size, price, and minimum-notional filters.

### `GET /market/candles`

Role: viewer or higher.

Required query fields: exchange, symbol, interval, start, end.

Optional: page size and cursor.

Returns only validated persisted candles unless an explicit diagnostic flag is authorized.

### `POST /market/backfills`

Role: operator or owner.

Idempotency: required.

Creates an asynchronous bounded backfill job. Returns `202` with job resource location.

### `GET /market/backfills/{job_id}`

Returns progress, checkpoint, inserted count, duplicate count, quality failures, retry count, and terminal status.

### `POST /market/snapshots`

Role: operator or owner.

Idempotency: required.

Creates an immutable snapshot from finalized, quality-approved candles.

### `GET /market/snapshots/{snapshot_id}`

Returns snapshot metadata, candle references, quality state, freshness, and hash.

## 10. Feature Sets

### `POST /feature-calculations`

Role: operator or owner.

Idempotency: required.

Input references an immutable snapshot and feature-set version.

### `GET /feature-calculations/{calculation_id}`

Returns typed values, input/output hashes, version, status, and warnings.

## 11. Google Gemini Analysis

### `POST /analyses`

Role: operator or owner.

Idempotency: required.

Example request:

```json
{
  "workspace_id": "uuid",
  "market_snapshot_id": "uuid",
  "feature_calculation_id": "uuid",
  "prompt_version_id": "uuid",
  "report_schema_version": "1.0",
  "provider_configuration_version_id": "uuid"
}
```

The API does not accept a Gemini API key or arbitrary system prompt.

Returns `202` for asynchronous execution or the existing analysis for a duplicate idempotency key.

### `GET /analyses/{analysis_id}`

Returns:

- status;
- market and feature references;
- provider and configured model identifier;
- prompt and schema versions;
- validated report when available;
- validation result;
- safety/refusal status;
- request count, latency, usage, and cost estimate;
- no secret or unrestricted raw prompt.

### `POST /analyses/{analysis_id}/revalidate`

Role: operator or owner.

Revalidates stored raw output against a selected compatible schema/policy without making a new paid provider request. It must create a new immutable validation record.

## 12. Strategy Evaluations

### `POST /strategy-evaluations`

Role: operator or owner.

Idempotency: required.

Input references immutable market snapshot, feature calculation, optional validated AI report, strategy version, and portfolio-state version.

### `GET /strategy-evaluations/{evaluation_id}`

Returns HOLD, ENTER, EXIT, or REDUCE intent, evidence references, configuration hash, and deterministic reason codes.

## 13. Risk Policies and Evaluations

### `GET /risk/policies`

Role: viewer or higher.

Lists immutable policy versions and status.

### `POST /risk/policies`

Role: owner.

Creates a new immutable policy version. Existing active experiments continue using their frozen version.

### `POST /risk-evaluations`

Role: operator or owner.

Idempotency: required.

Input references strategy intent, portfolio-state version, market snapshot, and risk-policy version.

### `GET /risk-evaluations/{evaluation_id}`

Returns approve, approve-with-reduced-size, reject, halt-portfolio, or halt-workspace, with safe reason codes and approved notional where applicable.

## 14. Paper Portfolios

### `POST /paper-portfolios`

Role: owner.

Idempotency: required.

Creates a portfolio with base currency, starting virtual cash, execution-model version, and risk-policy reference.

### `GET /paper-portfolios/{portfolio_id}`

Role: viewer or higher.

Returns reconciled cash, reserved cash, positions, realized and unrealized P&L, equity, fees, exposure, drawdown, halt status, and state version.

### `GET /paper-portfolios/{portfolio_id}/ledger`

Returns paginated immutable ledger entries. Viewer or higher.

### `POST /paper-portfolios/{portfolio_id}/halt`

Role: owner; automated system halt may use internal application command.

Idempotency: required.

Requires reason and optional incident reference. Halting blocks new entries immediately.

### `POST /paper-portfolios/{portfolio_id}/reconcile`

Role: operator or owner.

Runs explicit reconciliation. A mismatch creates a critical event and halt.

## 15. Paper Orders

### `POST /paper-orders`

Role: operator or owner.

Idempotency: required.

The request must reference an approved risk evaluation. Clients may not submit arbitrary unvalidated order notional.

### `GET /paper-orders/{order_id}`

Returns order state, requested and approved values, fills, fees, and lineage references.

### `POST /paper-orders/{order_id}/cancel`

Role: operator or owner.

Idempotency: required.

Cancellation is valid only for cancellable states and returns the resulting order state.

## 16. Backtests

### `POST /backtests`

Role: operator or owner.

Idempotency: required.

Request fields include data range, symbol, interval, initial capital, strategy version, risk version, execution model, benchmark set, and reproducibility metadata.

Returns `202` with backtest ID.

### `GET /backtests/{backtest_id}`

Returns status, progress, warnings, failure code, and configuration summary.

### `GET /backtests/{backtest_id}/report`

Returns performance metrics, equity curve references, trade summary, fees, benchmarks, reproducibility metadata, and warnings.

### `GET /backtests/{backtest_id}/trades`

Returns paginated simulated trades and lineage.

## 17. Experiments

### `POST /experiments`

Role: owner.

Creates a draft experiment referencing a frozen workspace configuration and virtual starting balance.

### `POST /experiments/{experiment_id}/preflight`

Role: owner or operator.

Checks market data, migrations, services, budgets, strategy, risk, execution model, observability, and halt controls.

### `POST /experiments/{experiment_id}/start`

Role: owner.

Idempotency: required. Allowed only from Ready state.

### `POST /experiments/{experiment_id}/pause`

Role: owner.

### `POST /experiments/{experiment_id}/halt`

Role: owner; also available to internal safety controls.

### `GET /experiments/{experiment_id}`

Returns state, frozen configuration hash, timing, portfolio, safety events, and report status.

### `GET /experiments/{experiment_id}/report`

Returns final or current report with cash and buy-and-hold comparison.

## 18. Audit

### `GET /audit/events`

Role: viewer or higher; secret-bearing details remain restricted.

Filters:

- workspace;
- actor;
- entity type and ID;
- event type;
- outcome;
- error code;
- start and end time.

Audit records are immutable and paginated.

## 19. Jobs

### `GET /jobs/{job_id}`

Returns asynchronous job type, status, attempts, timestamps, progress, safe error code, and result-resource reference.

## 20. HTTP Status Guidance

- `200`: successful read or synchronous command
- `201`: resource created synchronously
- `202`: asynchronous command accepted
- `204`: successful command without body
- `400`: malformed request
- `401`: unauthenticated
- `403`: unauthorized
- `404`: resource absent or not visible
- `409`: state or idempotency conflict
- `422`: semantic validation failure
- `429`: application rate limit
- `503`: dependency unavailable or service not ready

Domain rejection such as risk rejection may return `409` or `422` according to the generated endpoint contract, but must always include a stable domain code.

## 21. OpenAPI and Contract Verification

Implementation requirements:

- generated OpenAPI must be deterministic;
- CI must detect uncommitted OpenAPI changes;
- examples must validate against schemas;
- frontend types should be generated from OpenAPI where practical;
- endpoint inventory must identify method, path, permission, idempotency, handler, and automated tests;
- undocumented endpoints fail CI;
- breaking schema differences require explicit approval.

## 22. Security Requirements

- never expose Gemini or future exchange credentials;
- arbitrary prompt submission is prohibited in MVP;
- validate UUID ownership and workspace scope;
- apply rate limits to authentication, analysis, backfill, and backtest creation;
- do not expose internal stack traces;
- log privileged commands and denied authorization attempts;
- use explicit confirmation for destructive or mode-changing actions in the UI.

## 23. Related Documents

- `PRODUCT_REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `DATABASE_SCHEMA.md`
- `GEMINI_INTEGRATION.md`
- `RISK_ENGINE.md`
- `PAPER_TRADING.md`
- `SECURITY.md`
