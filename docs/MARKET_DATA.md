# Market Data

MVP uses Binance Spot public data.

## Rules
Internal symbols use `BASE/QUOTE`. All timestamps are UTC. Candle identity uses exchange open time.

## Validation
Positive prices, valid high/low relationships, non-negative volume, no duplicates, interval continuity, freshness tolerance.

Backfill is chunked, rate-limit aware, idempotent, and checkpointed. Corrections create data-quality events and may invalidate dependent snapshots.

Every feature set and decision references the exact candle range and snapshot hash.
