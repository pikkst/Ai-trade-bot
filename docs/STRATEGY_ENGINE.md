# Strategy Engine

Last reviewed: 2026-07-31
Status: Authoritative MVP strategy specification

## 1. Purpose

The strategy engine converts immutable market evidence into a typed advisory intent. It is deterministic, versioned, side-effect free, and separate from risk and execution.

The strategy engine does not place orders, write ledger entries, choose credentials, enable live trading, or override a risk decision.

## 2. Inputs

Every evaluation references:

- workspace and experiment configuration version;
- immutable market snapshot;
- versioned feature calculation;
- optional validated Google Gemini report;
- strategy version and configuration hash;
- portfolio-state version where the strategy requires current exposure;
- evaluation timestamp and correlation ID.

Invalid, stale, incomplete, or unapproved inputs cause rejection or HOLD according to explicit policy.

## 3. Intent Model

Allowed actions:

- `HOLD`: no new exposure change;
- `ENTER`: request a new long exposure;
- `EXIT`: request closure of an existing long exposure;
- `REDUCE`: request lower existing exposure.

Short selling is prohibited in MVP.

A strategy intent contains:

- action;
- symbol;
- direction;
- requested target exposure or requested notional boundary;
- deterministic reason codes;
- evidence references;
- contradictions or blockers;
- invalidation condition;
- strategy version;
- configuration hash;
- referenced input versions;
- evaluation hash.

The requested amount is not final. The risk engine may reduce or reject it.

## 4. Determinism

For identical input references, code version, configuration, and clock value, the strategy must produce the same intent and evaluation hash.

Prohibited sources of nondeterminism:

- current wall-clock reads inside calculation logic;
- random values without an explicit seed;
- live external calls;
- mutable global state;
- hidden database state;
- unversioned Gemini requests;
- implicit configuration defaults that are not persisted.

## 5. Google Gemini Relationship

Gemini produces a validated advisory report. The strategy may use selected typed report fields as optional evidence.

Rules:

- a missing Gemini report must not crash the strategy;
- an invalid or rejected report is treated as unavailable;
- Gemini confidence is not probability of profit;
- Gemini cannot determine final position size;
- Gemini cannot change the strategy formula;
- a strategy version must state whether Gemini evidence is required, optional, or ignored;
- AI-dependent entry is blocked during provider outage unless the frozen strategy explicitly defines a safe deterministic alternative.

## 6. Initial Strategies

### 6.1 HOLD-Only Smoke Strategy

Purpose: validate orchestration without exposure.

Behavior: always emits HOLD with reason `smoke_strategy_hold` after validating inputs.

### 6.2 BTC/EUR Trend Baseline

Purpose: provide a simple, explainable baseline rather than an optimized profit claim.

Candidate inputs:

- long and short EMA relationship;
- price relative to long EMA;
- RSI range;
- volatility guard input;
- volume confirmation;
- optional validated Gemini regime agreement.

Exact periods, thresholds, and logic must be explicit configuration and covered by reference tests. They must not be selected by Gemini or hidden in code.

The baseline must support:

- entry only for long exposure;
- exit on explicit trend invalidation;
- HOLD under insufficient or contradictory evidence;
- no averaging down unless separately specified and approved;
- no leverage or shorting.

## 7. Evaluation Sequence

1. Validate referenced versions and workspace scope.
2. Validate market snapshot freshness and quality.
3. Validate feature availability.
4. Load strategy version and configuration.
5. Load optional validated Gemini report according to strategy policy.
6. Evaluate pure deterministic rules.
7. Construct typed intent and reason codes.
8. Calculate evaluation hash.
9. Persist immutable evaluation.
10. Submit non-HOLD intent to deterministic risk evaluation.

## 8. Reason Codes

Reason codes must be stable and machine-readable.

Examples:

- `insufficient_history`;
- `stale_market_data`;
- `feature_missing`;
- `trend_not_confirmed`;
- `trend_entry_confirmed`;
- `trend_invalidation`;
- `volatility_too_high`;
- `gemini_unavailable`;
- `gemini_report_invalid`;
- `gemini_agrees_bullish`;
- `gemini_contradicts_entry`;
- `existing_position_hold`;
- `exit_condition_met`.

Human-readable explanations are derived from reason codes and evidence.

## 9. Strategy Lifecycle

States:

1. Draft
2. Unit tested
3. Backtested
4. Out-of-sample validated
5. Observation mode
6. Paper-trading candidate
7. Active paper strategy
8. Sandbox candidate
9. Archived

A strategy cannot skip required gates. Live approval is not part of this lifecycle and requires a separate future milestone.

## 10. Promotion Criteria

Before active paper trading:

- complete unit and property tests;
- no look-ahead;
- reference calculations verified;
- backtest includes fees and slippage;
- cash and buy-and-hold benchmarks included;
- out-of-sample result reported;
- parameter selection documented;
- risk policy compatibility verified;
- failure behavior documented;
- owner approves frozen version.

Profit alone is not sufficient.

## 11. Versioning

A new strategy version is required for changes to:

- rules or formula;
- indicators or periods;
- thresholds;
- Gemini evidence policy;
- requested exposure logic;
- invalidation logic;
- supported symbols or intervals;
- reason-code semantics;
- fallback behavior.

Applied versions are immutable. Active experiments retain their frozen strategy version.

## 12. Configuration

Configuration must define:

- supported symbols;
- allowed intervals;
- required history length;
- indicator parameters;
- thresholds;
- exposure request boundary;
- Gemini dependency policy;
- contradictory-evidence behavior;
- cooldown-related signals if strategy-owned;
- explicit defaults.

Configuration is validated and hashed.

## 13. Tests

Required tests:

- each action outcome;
- boundary values for every threshold;
- insufficient history;
- missing feature;
- stale snapshot;
- invalid Gemini report;
- provider unavailable;
- contradictory Gemini evidence;
- identical-input determinism;
- version isolation;
- no side effects;
- no direct order creation;
- no short or leverage output;
- reference dataset expected intents.

## 14. Metrics and Audit

Record:

- evaluations by strategy version;
- intents by action;
- HOLD reason codes;
- Gemini agreement/disagreement when used;
- evaluation duration;
- rejection/error count;
- input and evaluation hashes.

Every intent must be traceable to exact snapshot, features, optional Gemini report, strategy version, and configuration.

## 15. Anti-Overfitting Rules

- Separate design, validation, and test periods.
- Record every parameter trial used for selection where practical.
- Avoid optimizing many parameters against a small dataset.
- Report sensitivity to reasonable parameter changes.
- Include turnover and cost impact.
- Preserve rejected strategy experiments rather than cherry-picking only winners.
- Do not promote based only on in-sample return.

## 16. Related Documents

- `PRODUCT_REQUIREMENTS.md`
- `AI_ARCHITECTURE.md`
- `GEMINI_INTEGRATION.md`
- `RISK_ENGINE.md`
- `BACKTEST_ENGINE.md`
- `PAPER_TRADING.md`
- `TESTING.md`
