# Portfolio Engine

Last reviewed: 2026-07-31
Status: Authoritative MVP portfolio and accounting specification

## 1. Purpose

The portfolio engine tracks simulated financial state through an append-only double-entry ledger. The ledger is the source of truth; balances, positions, P&L, exposure, and drawdown are rebuildable projections.

## 2. Accounting Principles

- Decimal arithmetic only.
- Explicit asset and currency on every amount.
- Every financial transaction balances.
- Ledger entries are append-only.
- Corrections use reversing and replacement transactions, never row mutation.
- Fills and ledger postings are atomic.
- Projections are rebuildable from the ledger and immutable source events.
- Reconciliation mismatch activates a halt.

## 3. Accounts

A practical chart of accounts may include:

- available cash by currency;
- reserved cash by currency;
- asset inventory by asset;
- reserved asset by asset;
- fee expense by asset/currency;
- realized trading gain/loss;
- simulation equity adjustment only when explicitly required by accounting model.

Exact account codes are versioned and documented with implementation.

## 4. Ledger Transaction Model

Each business event creates one balanced transaction containing two or more entries.

Required fields:

- portfolio;
- transaction ID;
- ordered ledger sequence;
- account code;
- asset/currency;
- debit or credit amount;
- business reference type and ID;
- effective time;
- creation time;
- correlation and job IDs;
- transaction description/reason code.

For each transaction and asset/currency accounting unit, total debits must equal total credits according to the chosen ledger convention.

## 5. Portfolio State

Tracked values:

- available cash;
- reserved cash;
- available asset quantity;
- reserved asset quantity;
- position quantity;
- cost basis;
- average cost;
- realized P&L;
- unrealized P&L;
- cumulative fees;
- market value;
- equity;
- gross exposure;
- net exposure;
- high-water mark;
- daily reference equity;
- daily and total drawdown;
- current state version;
- halt status.

## 6. Cash Reservation

Before an approved buy order becomes open, the engine reserves sufficient quote currency for:

- approved notional;
- estimated fee;
- conservative slippage/spread buffer where needed.

Reservation is idempotent and references the order. Fill processing consumes reservation; cancellation releases unused reservation.

## 7. Asset Reservation

Before a sell/exit order becomes open, the engine reserves the approved asset quantity. Reserved quantity cannot be used by another order.

Short selling is prohibited, so available plus reserved asset cannot become negative.

## 8. Fill Accounting

A buy fill must account for:

- quote cash consumed;
- base asset acquired;
- fee amount and fee asset;
- release/adjustment of reservation;
- position cost basis.

A sell fill must account for:

- base asset disposed;
- quote cash received;
- fee;
- reservation release;
- realized P&L based on the configured cost-basis method.

The MVP cost-basis method must be explicitly selected and versioned. Weighted average cost is the default design candidate; changing it requires an ADR and new accounting version.

## 9. Cost Basis

If weighted average cost is selected:

```text
new_average_cost =
(previous_quantity * previous_average_cost + acquired_cost_including_policy_defined_fees)
/ new_quantity
```

The treatment of fees in cost basis must be explicit and tested. Selling does not retroactively change the average cost of remaining units except according to the chosen accounting policy.

## 10. Realized P&L

For a sell under weighted-average accounting:

```text
realized_pnl = net_sale_proceeds - disposed_quantity * average_cost
```

Net proceeds and fee treatment follow the accounting policy version.

## 11. Unrealized P&L and Valuation

Unrealized P&L uses a timestamped validated mark price:

```text
unrealized_pnl = position_market_value - remaining_cost_basis
```

Valuation metadata includes:

- price source;
- symbol;
- timestamp;
- freshness status;
- snapshot/ticker reference.

Stale price produces explicit stale valuation. It must not silently appear current.

## 12. Equity and Exposure

Baseline definitions:

```text
equity = available_cash + reserved_cash + market_value_of_assets
```

Exposure calculations must avoid double counting reserved assets and orders.

Gross exposure is the absolute market value of open asset positions divided by equity. The MVP is long only, so net and gross exposure may be equal, but both definitions remain explicit.

## 13. Drawdown

### High-Water Mark

Maximum reconciled equity observed during the experiment under the selected valuation policy.

### Total Drawdown

```text
(high_water_mark - current_equity) / high_water_mark
```

### Daily Drawdown

```text
(daily_reference_equity - current_equity) / daily_reference_equity
```

Daily reset time is explicit UTC configuration. Division-by-zero and missing valuation conditions fail safely.

## 14. Projection State Versions

After every committed financial event, generate or update a state version containing:

- last applied ledger sequence;
- balances;
- positions;
- P&L;
- fees;
- equity and exposure;
- drawdown;
- valuation reference;
- state hash.

Risk evaluations reference an immutable portfolio-state version to avoid race ambiguity.

## 15. Reconciliation

Reconciliation compares:

- ledger-derived balances;
- persisted balance projections;
- fills and order totals;
- reservations;
- positions and cost basis;
- fee totals;
- state version and ledger sequence.

Outcomes:

- matched;
- mismatch with classified reason;
- unable to reconcile due to missing/corrupted data.

Any unresolved mismatch creates a critical audit event and halt.

## 16. Rebuild

A complete rebuild must be possible from:

- initial portfolio funding transaction;
- immutable orders and fills;
- append-only ledger entries;
- accounting-policy version;
- validated valuation inputs for historical snapshots where required.

Rebuild does not overwrite evidence. It creates a new projection version and comparison result.

## 17. Concurrency

- use optimistic locking/state versions or appropriate row locks for financial commands;
- order/fill commands must verify expected portfolio state;
- ledger sequence allocation is transaction-safe;
- concurrent duplicate fills resolve through unique constraints and idempotency;
- no network call occurs inside the portfolio transaction.

## 18. Invariants

1. No negative available or reserved balance unless explicitly allowed by a future accounting model.
2. No short asset quantity.
3. Each ledger transaction balances.
4. Ledger sequence is unique and monotonic per portfolio.
5. Filled quantity does not exceed approved order quantity.
6. Reservation cannot exceed owned/available amount.
7. Projection ledger sequence cannot exceed persisted ledger.
8. Rebuilt and persisted state hashes match after reconciliation.
9. Financial values respect configured precision.
10. A halted portfolio cannot accept a new entry order.

## 19. Initial Funding

Creating the EUR 20 research portfolio posts an explicit initial funding transaction. It is not inserted as a mutable balance field without ledger evidence.

## 20. Fees

Fees are explicit ledger events and included in:

- cumulative fees;
- cash/asset balances;
- realized P&L or cost basis according to policy;
- equity;
- reports and benchmarks.

## 21. Reporting

Portfolio reports distinguish:

- deposited virtual capital;
- current equity;
- realized and unrealized P&L;
- gross/net return;
- fees and simulated slippage;
- exposure and drawdown;
- stale valuation status;
- halted state;
- simulation limitations.

## 22. Tests

Required tests:

- initial funding;
- buy reservation, fill, and release;
- sell reservation, fill, and release;
- partial fills;
- cancellation;
- fees in quote and base asset;
- weighted-average cost reference cases;
- realized/unrealized P&L;
- equity and exposure;
- daily and total drawdown;
- decimal rounding;
- duplicate command replay;
- concurrent state conflict;
- transaction rollback;
- projection rebuild;
- reconciliation mismatch and halt;
- no negative or short balance.

Property tests verify conservation and reconstruction across generated sequences of valid events.

## 23. Metrics

- equity, P&L, fees, exposure, and drawdown;
- ledger posting count/failure;
- projection rebuild duration;
- reconciliation outcome/duration;
- balance invariant failure;
- active halt;
- stale valuation.

## 24. Related Documents

- `PAPER_TRADING.md`
- `RISK_ENGINE.md`
- `DATABASE_SCHEMA.md`
- `BACKTEST_ENGINE.md`
- `TESTING.md`
- `OBSERVABILITY.md`
