# Paper Trading

Supports market and limit buy/sell plus cancellation.

## Fill Model
Defines reference price, spread, slippage, fee, volume assumption, partial fills, and time in force.

Default: market fills at the next eligible candle open plus slippage; limit fills only when the candle range crosses the price; ambiguous intrabar events resolve conservatively; every fill includes fees.

One approved risk evaluation creates at most one order. Portfolio state is reconstructed from ledger entries after every fill cycle.

Paper fills cannot reproduce queue priority, latency, market impact, exchange outages, or emotional behavior. Reports must state these limitations.
