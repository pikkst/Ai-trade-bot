# Portfolio Engine

The portfolio uses an append-only double-entry ledger.

## Tracked Values
Available cash, reserved cash, asset quantity, average cost, realized P&L, unrealized P&L, equity, exposure, fees, and drawdown.

## Rules
Use Decimal arithmetic, explicit currencies, exchange precision normalization, and invariant checks after every transaction.

Derived balances and positions must match ledger reconstruction. Any mismatch activates a halt and creates a critical alert. Mark-to-market valuation uses timestamped validated prices and reports stale valuation explicitly.
