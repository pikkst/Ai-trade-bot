# Market Data and Feature Evidence

Last reviewed: 2026-08-01  
Status: Authoritative M007–M008 market-data, quality, snapshot, dataset, and feature-input contract

## 1. Active Scope

The active M007 profile uses Binance Spot public REST for:

- exchange server time;
- exchange/symbol metadata;
- finalized OHLCV candles;
- bounded checkpointed historical backfill;
- idempotent gap detection and repair;
- optional public ticker diagnostics where explicitly useful.

Only finalized, quality-approved, fresh persisted evidence may enter normal snapshots, features, Gemini analysis, strategy, risk, paper execution, backtests, or research review.

Out of active M007 scope:

- private Binance credentials or order endpoints;
- persistent WebSocket ingestion;
- order book, aggregate trades, funding, open interest, derivatives, on-chain, news, social, or alternative data;
- cross-exchange aggregation;
- live-trading or exchange-reconciliation data.

A new source or persistent stream requires product requirements, source/licensing/terms review, schema and quality policy, M030 capacity/reliability evidence, M034 change governance, ADR, migration/rollback, security/privacy review, tests, staged paper verification, and owner approval.

## 2. Master-Task Ownership

| Capability | Master Tasks |
|---|---|
| provider protocol and deterministic fake | M006 |
| REST metadata/candles, quality, repair, corrections | M007 |
| immutable snapshots and deterministic features | M008 |
| API and Market Evidence workspace | M014, M017 |
| integrated/recovery tests | M026–M027 |
| cloud cycle and experiment | M028–M029 |
| performance, dataset lifecycle, research, and changes | M030–M034 |

## 3. Canonical Identity and Values

Internal symbol format: `BASE/QUOTE`, for example `BTC/EUR`.

Persist separately:

- provider/exchange code;
- exchange-native symbol;
- normalized base and quote assets;
- effective symbol-metadata version.

Candle identity:

- exchange;
- exchange-native symbol/effective symbol version;
- interval;
- exchange-provided open time.

Rules:

- timestamps are timezone-aware UTC;
- price, quantity, volume, and notional values use decimal representation;
- provider response order is not trusted until validated;
- local wall clock is not provider server time;
- current provider limits and retry guidance come from timestamped approved evidence rather than frozen prose constants.

## 4. Symbol Metadata Versions

Persist immutable effective versions containing:

- base/quote asset;
- trading/data status;
- price and quantity precision;
- tick size and step size;
- minimum/maximum quantity where supplied;
- minimum notional where supplied;
- supported public data capabilities;
- raw metadata hash and approved normalized hash;
- retrieval/effective timestamps;
- source request and provider version evidence;
- supersession/correction relationship.

Exchange metadata is authoritative for provider constraints. CCXT defaults or hidden application constants are not.

A metadata change invalidates or limits dependent configuration, risk, execution, backtest, or report evidence according to explicit compatibility rules.

## 5. Candle Contract

Required fields:

- symbol-metadata version;
- interval;
- open time and close time;
- open, high, low, close;
- base volume;
- quote volume when available;
- trade count when available;
- finalized flag;
- source ingestion/page reference;
- provider timestamps where available;
- canonical content hash.

Finalized candles are immutable in ordinary paths.

## 6. Validation Rules

A candle is invalid when any applicable invariant fails:

- all required prices are positive;
- `high >= open`, `high >= close`, and `high >= low`;
- `low <= open`, `low <= close`, and `low <= high`;
- volume and trade counts are non-negative;
- close time is after open time;
- interval boundaries and duration are valid;
- symbol and interval are allowed by exact configuration;
- sequence is ordered;
- identity is not duplicated inconsistently;
- finalization matches provider semantics;
- normalized decimals satisfy configured/source precision policy;
- payload size and schema are bounded;
- content hash is deterministic.

Invalid provider data is never coerced into valid evidence silently.

## 7. Quality State

Canonical quality outcomes include:

- `approved`;
- `incomplete`;
- `stale`;
- `duplicate_consistent`;
- `duplicate_conflict`;
- `invalid_value`;
- `invalid_interval`;
- `out_of_order`;
- `gap_detected`;
- `gap_repair_pending`;
- `provider_unavailable`;
- `rate_limited`;
- `clock_drift_exceeded`;
- `correction_pending`;
- `quarantined`;
- `invalidated`.

Only the exact approved/fresh states permitted by the frozen workflow policy may enter actionable paths.

Missing evidence must not appear as an empty successful dataset.

## 8. Time and Freshness

Freshness evaluation references:

- trusted application UTC clock abstraction;
- Binance server time;
- expected interval boundary and close time;
- latest persisted finalized candle;
- ingestion completion time;
- workflow purpose and tolerance-policy version;
- intended and actual cycle time.

Rules:

- excessive provider/local clock skew blocks affected processing;
- a delayed cycle evaluates the latest actual eligible finalized event;
- a missed cycle is recorded and never reconstructed as an imagined trade;
- freshness is calculated server-side and persisted with policy/version evidence;
- frontend calculations are presentation-only;
- stale or unavailable source data blocks new entry intent according to risk/configuration policy.

## 9. REST Ingestion

Every REST ingestion/backfill is:

- bounded by provider, market, interval, start, end, and configured maximum range;
- chunked according to current approved provider evidence;
- rate-limit aware;
- timeout/cancellation aware;
- checkpointed and restart-safe;
- protected from overlapping duplicate work;
- idempotent by page/range/content identity;
- observable by request, page, count, duration, retry, and safe error;
- independent of Render availability and local persistent disk.

A page is normalized, validated, and committed through an application-owned transaction. Duplicate consistent records do not create new rows. Duplicate conflicts create quality/correction evidence.

No network request occurs inside the persistence transaction.

## 10. Gap Detection and Repair

Expected candle boundaries are derived from:

- interval semantics;
- requested/available range;
- provider server time;
- finalization policy;
- existing approved sequence;
- market/calendar policy where future adapters require it.

A gap produces:

- explicit range and expected identities;
- detection policy/version;
- severity and downstream impact;
- repair job/checkpoint;
- provider request evidence;
- repaired/unresolved outcome;
- snapshot/dataset invalidation or block.

Repair uses bounded REST pages and the same validation/idempotency rules. The application never interpolates or invents OHLCV values for actionable evidence.

## 11. Corrections and Invalidations

When finalized source evidence changes:

1. preserve the original candle and source lineage;
2. create a quality/correction event;
3. persist replacement version/evidence;
4. identify dependent snapshots, features, AI reports, decisions, orders/fills, backtests, datasets, research reviews, and reports;
5. mark derived resources invalid, limited, or superseded according to versioned policy;
6. rebuild/re-run only through explicit commands or workflows;
7. preserve historical decisions and financial evidence as originally made;
8. record audit and incident/change references where material.

Corrections never rewrite prior decision, order, fill, ledger, or approval evidence.

## 12. Immutable Market Snapshots

A snapshot contains:

- workspace and environment;
- exchange/symbol metadata version;
- interval and analysis timestamp;
- exact ordered candle IDs/versions;
- first/last event time and count;
- quality and freshness outcome/version;
- data source and ingestion lineage;
- snapshot schema/serialization version;
- canonical snapshot hash;
- creator/cycle/backtest/job/correlation references;
- invalidation/supersession state;
- limitations.

Constraints:

- identical canonical membership and metadata produce the same hash;
- a snapshot never changes after creation;
- invalidated snapshots remain readable for audit;
- every feature, AI request, strategy/risk evaluation, paper decision, or backtest references an exact snapshot/dataset identity.

## 13. Historical Dataset Versions

Backtests, AI evaluations, and research reviews use immutable dataset versions containing:

- dataset class and purpose;
- market, interval, requested and actual range;
- exact source partitions/candles and metadata versions;
- finalized/quality/gap/correction state;
- schema/manifest version;
- canonical manifest and content hashes;
- creation/approval owner and timestamps;
- retention, hold, archive, restore, and invalidation state;
- source-to-derived lineage;
- limitations and excluded data.

Train/design, validation, final untouched test, and walk-forward windows are explicit resources/relationships. Reuse or contamination must be visible.

## 14. Feature Input Contract

M008 feature calculations receive only:

- exact immutable snapshot/dataset reference;
- feature-set version/configuration hash;
- required history and warm-up policy;
- typed decimal/boolean/string input values;
- clock/replay context;
- deterministic seed only if an approved feature requires one;
- workspace and purpose scope.

Features do not call live providers or read hidden mutable state.

## 15. Feature Output Contract

Feature calculation evidence includes:

- calculation ID and idempotency key;
- source snapshot/dataset hash;
- feature-set/version/configuration hash;
- status and required-history/warm-up result;
- typed values and explicit units;
- input/output hashes;
- start/end/duration;
- warnings, missing values, null reasons, or safe error;
- cycle/backtest/evaluation references.

Identical inputs, code version, configuration, clock/replay context, and seed produce identical outputs and hashes.

## 16. Required Baseline Features

The baseline may include versioned:

- simple and logarithmic returns;
- SMA and EMA;
- RSI;
- ATR;
- rolling volatility;
- volume-relative features;
- trend/regime evidence;
- data-quality/freshness-derived guards.

Exact formulas, periods, annualization, warm-up, null behavior, decimal precision, and edge cases are documented in source/tests and registered by version. No hidden default influences a running experiment.

## 17. Feature Failure Behavior

Explicit states include:

- insufficient history;
- missing required source value;
- invalid source quality/freshness;
- unsupported interval/market;
- division by zero/undefined statistic;
- incompatible metadata/configuration;
- invalid decimal/domain range;
- deterministic calculation failure;
- cancelled/timed out.

Undefined values use explicit null plus reason. They are never replaced with misleading zero or fabricated data.

## 18. Idempotency and Concurrency

Stable identities are required for:

- symbol metadata refresh;
- REST page/range ingestion;
- gap detection/repair;
- candle validation/correction;
- snapshot creation;
- dataset manifest creation;
- feature calculation.

Duplicate delivery returns existing resources or deterministic conflicts. Locks/leases prevent overlapping logical cycle work, while database constraints protect canonical identities.

## 19. Security and Privacy

- public market data requests contain no credentials;
- provider URLs, query parameters, and responses are bounded/validated;
- logs omit unrestricted provider payloads and unbounded IDs;
- raw transport payload retention is minimized and versioned;
- provider terms, regions, limits, and use restrictions are reviewed before deployment;
- source/licensing restrictions flow to dataset/publication/export policy;
- browser access uses approved read models and RLS;
- direct browser market-data mutation is prohibited.

## 20. Observability

Durable/operational evidence includes:

- provider/server-time outcomes and skew;
- request/page latency, status, retry, rate-limit, and safe error;
- inserted, duplicate, invalid, corrected, quarantined counts;
- latest finalized candle and ingestion lag;
- gap detection/repair duration/outcome;
- snapshot creation/rejection/hash;
- feature duration/status/warm-up/null reasons/hash;
- stale-data blocks and affected cycle/decision;
- correction/invalidation propagation;
- dataset manifest/quality/archive/restore outcomes.

Metrics use bounded labels. Profit is not a market-data or feature SLI.

## 21. Testing

Required tests include:

- reference metadata/candle parsing;
- decimal and OHLC invariants;
- duplicate consistent/conflict behavior;
- ordering and interval boundaries;
- gaps and bounded repair;
- provider timeout, cancellation, rate limit, malformed/partial response;
- clock skew/freshness;
- idempotent page/cycle replay;
- immutable correction and dependent invalidation;
- snapshot/dataset hash determinism;
- feature formula reference cases and properties;
- warm-up/insufficient history/null/undefined behavior;
- no look-ahead and replay clock isolation;
- stale/invalid evidence blocks actionable downstream work;
- RLS/read-only exposure;
- export/archive/restore preserves hashes and lineage.

Normal CI uses fixtures/fakes. Protected public REST smoke tests are bounded and never use private credentials.

## 22. Deferred Persistent Streaming

Persistent WebSocket ingestion is not part of M007 acceptance.

If later activated, it must:

- preserve REST as gap-repair and canonical continuity mechanism;
- model subscription/session/heartbeat/reconnect state;
- handle partial-to-final transition, duplicates, ordering, and provider outages;
- not treat an open connection as complete data;
- use durable checkpointing and bounded resource behavior;
- pass M030 capacity/reliability evidence and M034 approval;
- include migration, rollback, cost, security/privacy, and staged paper verification.

## 23. Completion Gate

M007–M008 are verified only when:

- public REST and fake provider contracts pass;
- metadata/candles/gaps/corrections/snapshots/features are deterministic and idempotent;
- invalid/stale evidence fails closed;
- provider retries/limits are bounded;
- exact lineage and hashes exist;
- no WebSocket, private exchange, or live execution dependency exists;
- API/schema/docs/tests and task evidence are synchronized;
- final commits are fetched and inspected.

## 24. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `BINANCE_INTEGRATION.md`
- `DATABASE_SCHEMA.md`
- `API_SPECIFICATION.md`
- `DATA_LIFECYCLE_DATASET_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
- `OBSERVABILITY.md`
- `TESTING.md`
