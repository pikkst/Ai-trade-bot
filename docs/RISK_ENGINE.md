# Risk Engine

The deterministic risk engine is non-bypassable.

## Outcomes
Approve, approve with reduced size, reject, halt portfolio, halt workspace.

## Policies
Position limit, exposure limit, order notional, daily drawdown, total drawdown, consecutive losses, cooldown, stale-data rejection, volatility guard, minimum notional, open-order limit, duplicate protection, and global kill switch.

## EUR 20 Research Profile
Maximum position 25%; maximum order EUR 5 equivalent; risk budget 1%; daily drawdown halt 5%; total drawdown halt 15%; one open order; no leverage; no shorting.

Fail closed on reconciliation mismatch, stale data, invalid precision, missing fees, risk exceptions, transaction failure, or corrupted version references.
