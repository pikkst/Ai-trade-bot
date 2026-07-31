# Risk Engine

Last reviewed: 2026-07-31
Status: Authoritative MVP risk specification

## 1. Purpose

The risk engine is the non-bypassable deterministic safety boundary between strategy intent and paper execution.

It decides whether an intent is approved, reduced, rejected, or causes a halt. Google Gemini has no authority over the risk decision.

## 2. Inputs

Every risk evaluation references:

- immutable strategy evaluation;
- active risk-policy version;
- immutable market snapshot and freshness result;
- portfolio-state version;
- open orders;
- current and proposed exposure;
- execution-model version;
- exchange symbol precision and minimum-notional metadata;
- experiment configuration;
- evaluation timestamp and correlation ID.

Missing, stale, or inconsistent input fails closed.

## 3. Outcomes

- `APPROVE`: intent is permitted without modification.
- `APPROVE_REDUCED`: permitted with lower quantity/notional.
- `REJECT`: no order may be created.
- `HALT_PORTFOLIO`: block new paper entries for one portfolio.
- `HALT_WORKSPACE`: block new paper entries across the workspace.

Every outcome includes stable reason codes and a policy version.

## 4. Evaluation Order

Recommended deterministic order:

1. workspace and experiment state;
2. active halt check;
3. input version and ownership validation;
4. market-data quality and freshness;
5. strategy intent validity;
6. symbol and direction permissions;
7. precision and minimum-notional constraints;
8. duplicate and open-order checks;
9. portfolio balance and reserved funds;
10. position and gross-exposure limits;
11. order-notional and risk-budget limits;
12. volatility guard;
13. consecutive-loss cooldown;
14. daily and total drawdown limits;
15. execution-model availability;
16. final approved quantity and notional.

A critical failure stops further approval and may halt.

## 5. Required Policies

### Position Limit

Maximum value of one position as a percentage of reconciled portfolio equity.

### Gross Exposure Limit

Maximum total open long exposure as a percentage of equity.

### Order Notional Limit

Maximum notional for a single approved paper order.

### Risk Budget

A conservative per-decision budget. The initial MVP does not depend on AI-calculated stop-loss risk. The exact calculation must be explicit and versioned before use.

### Drawdown Limits

Daily drawdown and total drawdown are measured from explicitly defined equity reference points. Threshold breach activates halt.

### Volatility Guard

Reject or reduce entries when approved deterministic volatility features exceed configured boundaries.

### Consecutive-Loss Cooldown

After a configured number of realized losing trades, block new entries for a configured duration or until owner review.

### Stale-Data Rejection

No entry approval when snapshot freshness or quality fails policy.

### Open-Order Limit

Restrict simultaneous open orders per portfolio and symbol.

### Duplicate Protection

The same strategy intent and portfolio state cannot create multiple approvals or orders.

### Precision and Minimum Notional

Approved values must satisfy current persisted Binance symbol filters used by the paper model.

### Kill Switch

Owner or automatic safety rules can halt portfolio or workspace. No undocumented bypass is permitted.

## 6. EUR 20 Research Profile

Initial frozen profile:

- starting virtual capital: EUR 20;
- primary symbol: BTC/EUR;
- long only;
- no leverage;
- maximum position: 25% of equity;
- maximum order: EUR 5 equivalent;
- maximum gross exposure: 25% unless separately approved;
- daily drawdown halt: 5%;
- total drawdown halt: 15%;
- one open order maximum;
- stale data: reject;
- missing fee/slippage model: reject;
- unresolved reconciliation mismatch: halt;
- human/owner oversight enabled.

The risk-budget percentage must not conflict with the EUR 5 order and 25% position limits. The strictest applicable limit wins.

## 7. Sizing

The risk engine receives a strategy exposure request and computes an approved upper bound.

Approved quantity must consider:

- reconciled available cash;
- current position;
- requested target exposure;
- maximum position and gross exposure;
- maximum order notional;
- symbol step size and minimum quantity;
- minimum notional;
- estimated fee and slippage reserve;
- configured safety buffer.

Rounding is conservative and uses decimal arithmetic. Rounding must never increase risk above the approved boundary.

## 8. Drawdown Definitions

### Daily Drawdown

Difference between current reconciled equity and the configured daily reference equity, divided by reference equity.

The daily reference and reset time must be explicit UTC configuration.

### Total Drawdown

Difference between current equity and the experiment high-water mark, divided by high-water mark.

Drawdown calculations include realized/unrealized P&L and fees according to the portfolio specification.

## 9. Halt Semantics

A halt:

- blocks new ENTER intents immediately;
- may allow safe cancellation or EXIT/REDUCE according to explicit policy;
- records source, reason, actor, time, and affected scope;
- emits critical metrics and audit events;
- cannot be silently cleared;
- requires owner review before any resume path;
- creates a new state transition rather than deleting history.

For MVP, an unresolved ledger mismatch or corrupted version reference causes a workspace or portfolio halt.

## 10. Fail-Closed Conditions

Reject or halt on:

- risk-engine exception;
- missing or invalid policy version;
- stale or invalid market data;
- portfolio-state version conflict;
- reconciliation mismatch;
- insufficient cash;
- invalid precision;
- missing minimum-notional metadata;
- missing fee, spread, or slippage model;
- duplicate intent/order relation;
- database transaction failure;
- unsupported direction, leverage, or symbol;
- experiment not in Running state;
- active halt;
- corrupted lineage reference.

## 11. Versioning

A new immutable risk-policy version is required for any change to:

- limit values;
- calculation formulas;
- drawdown reference rules;
- rounding or buffers;
- volatility thresholds;
- cooldown behavior;
- halt behavior;
- allowed symbols/directions;
- reason-code semantics.

Active experiments keep their frozen version.

## 12. Reason Codes

Examples:

- `approved_within_limits`;
- `position_limit_exceeded`;
- `gross_exposure_exceeded`;
- `order_notional_exceeded`;
- `insufficient_available_cash`;
- `minimum_notional_not_met`;
- `invalid_precision`;
- `stale_market_data`;
- `volatility_guard_triggered`;
- `cooldown_active`;
- `daily_drawdown_limit_reached`;
- `total_drawdown_limit_reached`;
- `open_order_limit_reached`;
- `duplicate_intent`;
- `reconciliation_failed`;
- `trading_halted`;
- `execution_model_missing`;
- `unsupported_direction`.

## 13. Persistence

Risk evaluations are immutable. Persist:

- input references and state versions;
- policy version and configuration hash;
- individual rule results;
- original requested amount;
- approved amount if any;
- outcome and reason codes;
- evaluation hash;
- timing and correlation metadata.

## 14. Tests

Required tests:

- each policy boundary below, equal, and above threshold;
- combined limits select the strictest result;
- conservative precision rounding;
- insufficient cash including fee reserve;
- stale/invalid data;
- duplicate evaluation and order prevention;
- active halt;
- daily and total drawdown;
- cooldown;
- missing configuration;
- exception fail-closed behavior;
- concurrent portfolio-state conflict;
- Gemini output cannot bypass risk;
- no leverage or shorting;
- halt persists across restart.

Property tests verify approved exposure never exceeds configured constraints.

## 15. Metrics and Alerts

Metrics:

- evaluations by outcome;
- rejection reasons;
- reduced approvals;
- active halts;
- drawdown and threshold proximity;
- cooldown activations;
- evaluation errors and duration.

Critical alerts:

- reconciliation halt;
- drawdown halt;
- risk-engine internal failure;
- corrupted policy or state reference;
- attempted bypass or unsupported direction.

## 16. Related Documents

- `STRATEGY_ENGINE.md`
- `PORTFOLIO_ENGINE.md`
- `PAPER_TRADING.md`
- `DATABASE_SCHEMA.md`
- `SECURITY.md`
- `TESTING.md`
- `OBSERVABILITY.md`
