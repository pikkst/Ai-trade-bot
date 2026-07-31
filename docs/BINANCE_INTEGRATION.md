# Binance Integration

MVP uses public Spot data only.

## Adapter
Symbol metadata, candles, ticker, server time, health, and rate-limit state.

## Progression
1. Public data
2. Internal paper trading
3. Binance testnet or demo where supported
4. Restricted real key without withdrawal permission
5. Tiny live allocation only after explicit approval

Private keys must be encrypted, environment-separated, IP restricted where possible, rotatable, and never logged.

Future sandbox execution must reconcile local orders, fills, balances, and open orders with exchange state. Any mismatch triggers a halt.
