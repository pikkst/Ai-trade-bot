# Database Schema

Last reviewed: 2026-07-31
Status: Authoritative logical schema; Alembic migrations become executable source of truth after implementation

## 1. Global Rules

- PostgreSQL is the system of record.
- Primary keys use UUID.
- Timestamps use UTC `timestamptz`.
- Monetary, price, quantity, fee, and P&L fields use `numeric`; never `float` or `double precision`.
- Currency and asset identifiers are explicit.
- Ledger and audit rows are append-only.
- Foreign keys, unique constraints, check constraints, and indexes enforce invariants where practical.
- Applied migrations are immutable; schema evolution uses new additive Alembic migrations.
- Soft deletion is allowed only where historical references remain valid and the domain document explicitly permits it.

## 2. Common Columns

Mutable aggregate tables generally contain:

- `id uuid primary key`;
- `created_at timestamptz not null`;
- `updated_at timestamptz not null`;
- `version bigint not null` for optimistic concurrency where required.

Immutable records omit `updated_at` unless a separate processing-status projection is needed.

## 3. Identity and Workspace

### `users`

Purpose: authenticated human users.

Key fields: email/login, display name, password hash when local authentication exists, active status, created time.

Constraints: normalized login unique; password hash never exposed.

### `workspaces`

Purpose: top-level ownership and isolation boundary.

Key fields: name, base currency, status, owner reference.

Indexes: owner and status.

### `workspace_memberships`

Purpose: role assignment.

Fields: workspace, user, role (`owner`, `operator`, `viewer`).

Constraint: unique workspace/user pair; at least one owner must remain through application policy.

### `workspace_config_versions`

Purpose: immutable configuration used by backtests and experiments.

Fields include version number, canonical JSON, configuration hash, feature-set reference, Gemini configuration reference, prompt/schema references, strategy reference, risk-policy reference, execution-model reference, creator, and activation state.

Constraint: unique workspace/version and workspace/configuration hash.

## 4. Exchange and Market Data

### `exchanges`

Fields: code, display name, active status.

MVP includes Binance Spot.

### `exchange_symbols`

Fields: exchange, native symbol, normalized base/quote assets, status, price precision, quantity precision, tick size, step size, minimum quantity, minimum notional, metadata JSON, effective timestamps.

Constraint: unique exchange/native symbol/effective version.

### `candles`

Fields: exchange symbol, interval, open time, close time, open/high/low/close, base volume, quote volume when available, trade count when available, final flag, source ingestion ID, content hash.

Constraints:

- unique exchange symbol, interval, and open time;
- high >= open, close, low;
- low <= open, close, high;
- prices positive;
- volumes non-negative;
- close time after open time;
- only finalized candles may be referenced by normal snapshots.

Indexes: symbol/interval/open time and open-time ranges.

### `market_data_ingestions`

Purpose: track REST pages and WebSocket sessions.

Fields: provider request identifiers, range, checkpoint, status, counts, retries, timestamps, safe error code.

### `data_quality_events`

Fields: candle or range reference, event type, severity, details, detected time, resolution state, replacement reference when applicable.

Events are append-only.

### `market_snapshots`

Fields: workspace, exchange symbol, interval, analysis time, first/last candle, candle count, quality status, freshness, snapshot hash, creator/job reference.

### `market_snapshot_candles`

Join table preserving the exact ordered candle identities for reproducibility.

Constraint: unique snapshot/sequence and snapshot/candle.

## 5. Feature Engineering

### `feature_set_versions`

Fields: name, semantic version, implementation identifier, configuration JSON, configuration hash, status.

### `feature_calculations`

Fields: snapshot, feature-set version, status, input hash, output hash, start/end time, warnings, error code.

Constraint: unique snapshot/feature-set/configuration hash.

### `feature_values`

Fields: calculation, feature name, value type, numeric/string/boolean value, unit, sequence or timestamp when required.

Constraint: exactly one typed value representation is populated.

## 6. Google Gemini and AI Analysis

### `ai_provider_config_versions`

Fields: provider (`google_gemini` or `fake`), configured model identifier, timeout, retry policy, generation settings, budget references, configuration hash, status.

Secrets are not stored in this table.

### `ai_prompt_versions`

Fields: agent/purpose, version, system instruction, user template, template hash, status, creator.

Prompt records are immutable after use.

### `ai_report_schema_versions`

Fields: schema version, JSON Schema, schema hash, compatibility status.

### `ai_analysis_runs`

Fields: workspace, snapshot, feature calculation, provider config, prompt, schema, request ID, provider response ID when available, status, started/completed time, retry count, latency, input/output usage, cost estimate, safety status, refusal status, safe error code, raw-response retention reference.

Constraint: deterministic request/idempotency key unique within workspace.

### `ai_reports`

Fields: analysis run, validated structured report JSON, market regime, recommended action, confidence, validation status, validation-policy version.

Constraint: only validated reports may be consumed by strategy.

### `ai_report_validations`

Fields: run, schema version, validator version, outcome, errors, unsupported-claim result, created time.

Immutable; revalidation creates a new row.

### `ai_budget_usage`

Fields: workspace, provider config, budget period, request count, input/output usage, estimated cost, reservation and committed states.

Constraint: unique workspace/provider/period. Updates require transaction-safe reservation to prevent concurrent budget overruns.

## 7. Strategy and Risk

### `strategy_versions`

Fields: name, version, implementation reference, configuration JSON/hash, status, created time.

### `strategy_evaluations`

Fields: snapshot, feature calculation, optional validated AI report, strategy version, portfolio-state version, action, direction, requested exposure/notional, reason codes, evidence JSON, evaluation hash, created time.

Immutable and deterministic for identical referenced inputs.

### `risk_policy_versions`

Fields: workspace, version, limits and rule configuration JSON, configuration hash, active/archived status.

### `risk_evaluations`

Fields: strategy evaluation, policy version, portfolio-state version, outcome, approved quantity/notional when applicable, reason codes, rule results, created time.

Constraint: one canonical risk evaluation per unique intent/policy/portfolio-state combination unless explicitly re-evaluated against a new state.

### `trading_halts`

Fields: workspace, optional portfolio, scope, source (`manual`, `risk`, `reconciliation`, `integrity`), reason code, details, activated by/time, reviewed by/time, terminal state.

Halt history is immutable; review creates state-transition records rather than deleting evidence.

## 8. Paper Execution and Portfolio

### `paper_portfolios`

Fields: workspace, base currency, execution-model version, active risk-policy version, state, current state version, start time, halt reference.

### `paper_orders`

Fields: portfolio, approved risk evaluation, client/idempotency key, symbol, side, type, requested and approved quantity/notional, limit price, time in force, state, created time.

Constraints:

- unique portfolio/idempotency key;
- at most one order for one approved risk evaluation;
- positive quantity/notional;
- limit price required only for limit order;
- valid state transitions enforced by application and tested.

### `paper_fills`

Fields: order, fill sequence, quantity, reference price, fill price, fee amount/currency, slippage amount/model version, filled time.

Constraint: unique order/fill sequence; total filled quantity cannot exceed approved order quantity.

### `ledger_entries`

Fields: portfolio, transaction ID, sequence, account code, asset/currency, debit, credit, reference type/ID, effective time, created time.

Constraints:

- debit and credit non-negative;
- exactly one of debit or credit positive per row;
- transaction debits equal credits by application invariant and deferred verification;
- unique portfolio/sequence;
- entries never update or delete.

### `portfolio_state_versions`

Purpose: immutable reconciled projection snapshots.

Fields: portfolio, version, ledger sequence, cash, reserved cash, equity, realized/unrealized P&L, fees, exposure, drawdown, state hash, created time.

### `positions`

Current read projection keyed by portfolio and asset/symbol. It is rebuildable from ledger/fills and is not the financial source of truth.

### `reconciliation_runs`

Fields: portfolio, expected state hash, actual state hash, outcome, mismatch details, start/end time, halt reference.

## 9. Backtesting and Experiments

### `execution_model_versions`

Fields: fee, spread, slippage, precision, partial-fill, and intrabar assumptions plus configuration hash.

### `backtest_runs`

Fields: workspace, configuration, symbol/interval/range, initial capital, strategy, risk, execution model, status, progress, code commit, data hash, dependency manifest, random seed, start/end time, safe error code.

### `backtest_metrics`

Fields: run and named typed metrics including return, drawdown, volatility, Sharpe, Sortino, win rate, profit factor, exposure, turnover, fees, and trade count.

### `backtest_events`

Ordered replay events or references required for audit and reproducibility.

### `experiments`

Fields: workspace, frozen configuration, paper portfolio, name, state, planned/actual start/end, stop reason, final report reference.

### `experiment_state_transitions`

Immutable transitions with actor/source, from/to states, reason, and timestamp.

### `experiment_reports`

Stores report metadata, benchmark metrics, artifact locations, generation version, and hash.

## 10. Operations and Audit

### `audit_events`

Fields: workspace, actor type/ID, event type, entity type/ID, correlation/request/job IDs, outcome, safe details JSON, created time, integrity hash when implemented.

Append-only and indexed by workspace/time, entity, actor, and event type.

### `background_jobs`

Fields: queue job ID, type, idempotency key, workspace, status, attempts, max attempts, schedule/start/end times, progress, result resource, safe error code.

### `outbox_events`

Fields: aggregate reference, event type, schema version, payload, created time, published time, attempts, last safe error.

Used when reliable post-commit publication is required.

## 11. Delete and Retention Policy

Default design values, subject to legal and operational review:

- validated candles, snapshots, strategy/risk decisions, fills, and ledger: indefinite for project history;
- raw Gemini response payloads: 180 days by default, while validated structured reports and lineage remain;
- audit events: at least one year;
- operational application logs: 30 days;
- failed transient job payloads: 30–90 days depending on sensitivity;
- secrets: never stored in ordinary database tables.

Retention cleanup must be idempotent and must not break referenced lineage.

## 12. Index Requirements

At minimum:

- candles by symbol/interval/open time;
- snapshots by workspace/symbol/analysis time;
- analyses by workspace/status/created time;
- strategy and risk evaluations by referenced input IDs;
- orders by portfolio/state/created time;
- fills by order/sequence;
- ledger by portfolio/sequence and reference;
- audit by workspace/time and entity;
- jobs by status/scheduled time;
- experiments by workspace/state.

Indexes must be validated against real query plans before production.

## 13. Migration Rules

1. Generate a new Alembic migration for every schema change.
2. Never modify an already-applied migration.
3. Prefer backward-compatible expand/migrate/contract changes.
4. Test upgrade from an empty database and from the previous supported revision.
5. Data migrations must be bounded, restartable, and observable.
6. Destructive changes require backup, rollback plan, and explicit approval.
7. CI verifies one migration head unless a deliberate merge migration exists.

## 14. Schema-to-API Consistency

Every API resource in `API_SPECIFICATION.md` must map to an owning domain and persistence model or be explicitly computed. Secret-bearing internal fields must never appear in public response schemas.

## 15. Related Documents

- `ARCHITECTURE.md`
- `BACKEND.md`
- `API_SPECIFICATION.md`
- `GEMINI_INTEGRATION.md`
- `PORTFOLIO_ENGINE.md`
- `SECURITY.md`
- `TESTING.md`
