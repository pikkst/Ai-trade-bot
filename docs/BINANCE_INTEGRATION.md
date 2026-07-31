# Binance Integration

Last reviewed: 2026-07-31

## MVP Scope

The MVP uses Binance Spot public market data only. Private account access and exchange-side order placement are not required for the first paper-trading release.

## Official Interfaces

- Spot REST API for exchange information, symbol filters, historical candles, ticker snapshots, server time, and later reconciliation operations
- Spot WebSocket Streams for near-real-time public market data
- Testnet or demo environments only after internal paper trading is stable

The implementation must follow current official Binance Spot documentation. Do not assume that endpoints, filters, rate limits, authentication methods, or test-environment behavior remain unchanged.

## Adapter Contract

The Binance adapter provides:

- Exchange server time and measured clock drift
- Symbol metadata
- Base and quote asset
- Trading status
- Price precision and tick size
- Quantity precision and step size
- Minimum and maximum quantity
- Minimum notional and other applicable filters
- Historical finalized candles
- Near-real-time public streams
- Ticker data
- Rate-limit state
- Provider health

All exchange-native values must be retained alongside normalized domain values.

## Data Ingestion Rules

1. Load and cache exchange metadata with an explicit refresh policy.
2. Validate symbols before scheduling ingestion.
3. Backfill candles with bounded chronological requests.
4. Store only validated records.
5. Treat finalized candles as immutable.
6. Detect gaps after WebSocket disconnects.
7. Repair gaps through REST before resuming dependent analysis.
8. Compare local time with exchange server time.
9. Respect response rate-limit information and exponential backoff.
10. Record provider request IDs or equivalent correlation data where available.

## WebSocket Reliability

- Connections must reconnect with jittered backoff.
- Reconnection must not create duplicate consumers.
- Every reconnect triggers continuity verification.
- Events must be deduplicated by exchange identity and event time.
- Stale streams must be detected independently of TCP connection state.
- Strategies must not consume unverified gaps.

## Private API Progression

1. Public data only
2. Internal paper trading
3. Binance testnet or demo, where the required Spot features are supported
4. Restricted real API key without withdrawal permission
5. Tiny live allocation only after explicit owner approval, security review, reconciliation testing, and operational readiness review

Test environments do not perfectly reproduce production liquidity, spread, fills, filters, or operational failure modes. Sandbox success is necessary but not sufficient for live approval.

## Credential Security

Private credentials, when introduced later, must be:

- Created per environment
- Restricted to the minimum required permissions
- Created without withdrawal permission
- Encrypted at rest
- Loaded from a secret manager or protected environment
- Never logged or included in AI prompts
- Rotatable without code changes
- IP restricted where practical
- Monitored for authentication failures and unexpected usage

The implementation should support the strongest authentication mechanism that is operationally appropriate and officially supported for the selected interface. Authentication choice must be documented in an ADR before private API access is enabled.

## Order and Balance Reconciliation

Future sandbox or live execution must reconcile:

- Submitted client order IDs
- Exchange order IDs
- Order status
- Executed quantity
- Average price
- Fees and fee asset
- Open orders
- Available and locked balances
- Local ledger entries

Any unresolved mismatch triggers a portfolio or workspace halt. Automatic retries must use stable client order IDs and idempotency controls to avoid duplicate orders.

## Prohibited Assumptions

- Do not infer precision from displayed decimal places.
- Do not hardcode minimum notional or lot size.
- Do not assume WebSocket delivery is complete.
- Do not assume testnet liquidity models production.
- Do not use a generic library as the source of truth for Binance filters or signing rules.
- Do not enable withdrawals.
- Do not let AI generate or sign exchange requests.