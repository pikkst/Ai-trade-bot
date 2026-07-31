# Market Data

Last reviewed: 2026-07-31
Status: Authoritative MVP market-data specification

## 1. Scope

The MVP uses Binance Spot public market data. Required data:

- exchange server time;
- exchange and symbol metadata;
- finalized OHLCV candles;
- public ticker where operationally useful;
- public WebSocket candle updates.

Order-book, aggregate trades, funding, open interest, derivatives, on-chain, news, and social data are outside the initial MVP unless added through a new specification and tasks.

## 2. Canonical Models

Internal symbols use `BASE/QUOTE`, for example `BTC/EUR`. The exchange-native symbol is retained separately.

All timestamps are timezone-aware UTC. Candle identity is:

- exchange;
- exchange-native symbol;
- interval;
- exchange-provided open time.

Financial values use decimal representation.

## 3. Symbol Metadata

Persist effective versions of:

- base and quote assets;
- trading status;
- price and quantity precision;
- tick size;
- step size;
- minimum and maximum quantity;
- minimum notional where supplied;
- supported order types where relevant to future phases;
- raw metadata hash;
- retrieval and effective timestamps.

Exchange metadata is authoritative for exchange constraints, not CCXT defaults or hardcoded values.

## 4. Candle Model

Required fields:

- open time;
- close time;
- open, high, low, close;
- base volume;
- quote volume when available;
- trade count when available;
- finalized flag;
- source request/session reference;
- content hash.

Only finalized candles may be consumed by normal feature, Gemini, strategy, risk, and backtest workflows.

## 5. Validation Rules

A candle is invalid when any required condition fails:

- prices are positive;
- high is greater than or equal to open, close, and low;
- low is less than or equal to open, close, and high;
- volume is non-negative;
- close time is after open time;
- interval boundaries are valid;
- symbol and interval are recognized;
- sequence is not duplicated or out of order;
- finalization state matches exchange semantics.

## 6. Quality Status

Quality status should distinguish:

- `approved`;
- `incomplete`;
- `stale`;
- `duplicate_detected`;
- `invalid_value`;
- `out_of_order`;
- `gap_detected`;
- `provider_unavailable`;
- `correction_pending`.

Downstream analysis requires `approved` and fresh status.

## 7. Freshness

Freshness tolerance is configured by interval and workflow.

The system compares:

- local UTC clock;
- Binance server time;
- expected candle close time;
- latest persisted finalized candle;
- ingestion completion time.

Excessive clock drift or stale data blocks new analysis and entries.

## 8. REST Backfill

Backfill must be:

- bounded by explicit symbol, interval, start, and end;
- chunked according to current provider limits;
- rate-limit aware;
- idempotent;
- checkpointed;
- restartable;
- observable;
- protected against overlapping duplicate jobs.

A page is persisted only after validation. Duplicate records do not create duplicate rows. Partial progress is preserved for safe retry.

## 9. WebSocket Ingestion

WebSocket handling must include:

- explicit subscription state;
- heartbeat or liveness monitoring where supported;
- bounded reconnect with jitter;
- session and message metrics;
- duplicate event handling;
- out-of-order event handling;
- transition from partial to finalized candle;
- gap detection after reconnect;
- REST repair before downstream approval.

WebSocket data is not assumed complete merely because the connection is open.

## 10. Corrections

Finalized candles are immutable in ordinary paths.

When source correction is detected:

1. create a data-quality event;
2. persist replacement/version evidence;
3. identify dependent snapshots, features, analyses, backtests, and reports;
4. mark affected derived artifacts invalid or superseded according to policy;
5. never silently rewrite historical lineage.

## 11. Market Snapshots

An immutable snapshot contains:

- workspace;
- exchange and symbol;
- interval;
- analysis timestamp;
- exact ordered candle IDs;
- first and last candle time;
- candle count;
- data-quality state;
- freshness result;
- snapshot hash;
- creation job and correlation IDs.

Every feature calculation, Gemini request, strategy evaluation, and backtest references an exact snapshot or immutable historical dataset hash.

## 12. Idempotency

Deterministic keys are required for:

- metadata refresh;
- REST page ingestion;
- candle upsert/validation;
- gap-repair job;
- snapshot creation.

Duplicate delivery must not duplicate candles, snapshots, or quality events.

## 13. Rate Limits and Failure Handling

Current provider quotas and limits must be obtained from official Binance responses/documentation and adapter metadata, not frozen prose values.

Behavior:

- honor retry guidance when present;
- use bounded exponential backoff with jitter;
- avoid reconnect storms;
- separate market-data queues from Gemini/backtest work;
- preserve checkpoints;
- mark data stale when recovery exceeds tolerance;
- block downstream entry decisions until repaired.

## 14. Retention

Validated candles and snapshot lineage are retained indefinitely for project reproducibility unless a later legal/operational policy changes this. Raw transport payload retention should be bounded and configurable.

## 15. Metrics

Required categories:

- latest finalized candle time;
- ingestion lag;
- candles inserted;
- duplicates;
- gaps;
- invalid records;
- stale status;
- REST request outcomes;
- WebSocket connection and reconnects;
- backfill duration and checkpoints;
- snapshot creation and rejection.

## 16. Tests

Required tests:

- reference candle parsing;
- OHLC invariant failures;
- duplicates and ordering;
- gap detection and repair;
- partial/final candle transitions;
- reconnect behavior;
- idempotent backfill replay;
- rate-limit and timeout handling;
- clock drift;
- immutable correction flow;
- snapshot hash determinism;
- stale data blocks downstream processing.

## 17. Related Documents

- `BINANCE_INTEGRATION.md`
- `ARCHITECTURE.md`
- `DATABASE_SCHEMA.md`
- `BACKEND.md`
- `TESTING.md`
- `OBSERVABILITY.md`
