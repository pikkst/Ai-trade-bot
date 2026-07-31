# Strategy Engine

Last reviewed: 2026-08-01  
Status: Authoritative deterministic strategy, evidence, lifecycle, and promotion contract for `M010`, `M019`, `M032`, and `M034`

## 1. Purpose

The strategy engine converts exact immutable research evidence into a typed advisory intent.

It is:

- deterministic for identical inputs, versions, code, clock/replay context, and seed;
- versioned and side-effect free;
- separate from deterministic risk and paper execution;
- auditable through exact evidence references and hashes;
- compatible with both paper cycles and backtests.

It does not:

- place or cancel orders;
- reserve cash/assets;
- write ledger entries;
- choose final position size;
- access credentials or providers;
- change risk, execution, accounting, experiments, releases, or configuration;
- approve itself;
- enable private Binance or live trading.

## 2. Master-Task Ownership

| Capability | Master Tasks |
|---|---|
| strategy domain and risk interaction | M010 |
| API and Strategy/Risk workspace | M014, M019 |
| cycle and backtest use | M012–M013 |
| integrated test evidence | M026 |
| formal paper observation | M029 |
| research review and lifecycle | M032 |
| behavior changes and staged rollout | M034 |

## 3. Immutable Input Contract

Every evaluation references:

- workspace and environment;
- exact immutable workspace configuration and behavior set;
- market snapshot/dataset identity and hash;
- quality/freshness outcome and policy version;
- feature calculation identity/hash/version;
- optional accepted validated Gemini report identity/hash/version;
- strategy version/configuration hash;
- exact portfolio-state version/hash where current exposure matters;
- evaluation/replay timestamp supplied by the application clock;
- code revision and relevant dependency/migration versions;
- cycle/backtest/research context;
- correlation/idempotency identity.

The strategy never reads hidden mutable database state, current wall clock, live provider data, environment defaults, or arbitrary frontend values.

Invalid, stale, incomplete, quarantined, invalidated, incompatible, or unauthorized input produces explicit rejection or HOLD according to the frozen strategy policy.

## 4. Intent Contract

Allowed actions:

- `HOLD` — no requested exposure change;
- `ENTER` — request new or increased approved long exposure;
- `EXIT` — request closure of existing long exposure;
- `REDUCE` — request lower existing long exposure.

Short selling is prohibited in M001–M036.

A strategy evaluation contains:

- immutable evaluation ID;
- action;
- normalized symbol;
- direction (`long` or none according to action);
- requested target exposure or requested notional boundary, not final size;
- deterministic reason codes;
- supporting and contradictory evidence references;
- blockers/missing information;
- invalidation condition;
- source and portfolio-state versions;
- strategy/configuration/behavior-set references;
- evaluation hash;
- creation timestamp and context references.

A strategy intent is not a risk approval, order, fill, or financial effect.

## 5. Determinism

For identical canonical inputs, strategy implementation/version, configuration, application clock/replay event, and explicit seed, output and evaluation hash are identical.

Prohibited nondeterminism:

- wall-clock reads inside pure logic;
- random values without an explicit persisted seed;
- live external calls;
- mutable global/process state;
- hidden database state;
- unversioned AI/provider requests;
- locale/display values;
- implicit defaults not represented in immutable configuration;
- unordered iteration that changes results;
- binary floating-point authoritative financial calculations.

Canonical serialization and hashing are versioned and property tested.

## 6. Gemini Relationship

Gemini is optional typed advisory evidence according to the strategy version’s explicit dependency policy:

- `required` — AI-dependent action is blocked/HOLD when no accepted compatible report exists;
- `optional` — deterministic strategy continues and records missing/invalid AI reason;
- `ignored` — Gemini is not an input.

Rules:

- provider success without accepted application validation is unavailable evidence;
- rejected, blocked, stale, unsupported, injected, invalid, or incompatible reports are unavailable;
- analytical confidence is not profit probability or position-size authority;
- AI cannot change formula, thresholds, feature requirements, exposure request logic, or fallback behavior;
- strategy must preserve contradictions and missing information where material;
- a provider outage cannot create a more permissive action;
- same behavior applies in cycle and exact precomputed backtest modes.

## 7. Strategy Version Contract

A version includes:

- stable strategy ID and semantic/monotonic version;
- implementation reference and code revision;
- canonical configuration/schema/hash;
- supported markets/intervals;
- required feature set/history;
- portfolio-state dependency;
- Gemini dependency policy;
- action and exposure-request rules;
- contradiction/blocker behavior;
- invalidation/exit logic;
- reason-code version;
- deterministic seed policy if applicable;
- lifecycle state;
- test/backtest/research/evaluation/approval references;
- activation/archive timestamps;
- limitations.

Used versions are immutable. A material rule/default/meaning change creates a new version and behavior set.

## 8. Initial Strategies

### 8.1 HOLD-Only Smoke Strategy

Purpose: validate orchestration, persistence, audit, API, and workspace behavior without exposure.

After validating inputs, always emits `HOLD` with stable reason `smoke_strategy_hold`.

It remains available as a safe deterministic fallback/test strategy.

### 8.2 BTC/EUR Trend Baseline

Purpose: provide a simple explainable baseline, not an optimized profit claim.

Candidate versioned evidence:

- short/long EMA relationship;
- price relative to trend EMA;
- RSI range;
- ATR/volatility guard;
- volume confirmation;
- data-quality/freshness guard;
- current reconciled exposure;
- optional accepted Gemini regime agreement/contradiction.

Exact periods, thresholds, warm-up, Decimal precision, reason-code semantics, entry/exit/reduce behavior, and requested-exposure boundary belong in immutable configuration and reference tests.

Baseline constraints:

- long-only;
- no leverage;
- no averaging down unless separately specified/reviewed;
- HOLD on insufficient, stale, invalid, contradictory, or incompatible evidence according to policy;
- explicit trend invalidation/exit;
- no hidden optimization or dynamic model-selected parameter.

## 9. Evaluation Sequence

1. verify actor/workspace/context eligibility;
2. load exact immutable behavior/configuration/strategy versions;
3. validate market snapshot/dataset quality, freshness, finalization, and compatibility;
4. validate feature calculation and required history;
5. validate exact portfolio-state version where required;
6. load optional AI report only according to explicit dependency policy;
7. evaluate pure deterministic rules;
8. resolve contradictions/blockers/fallback;
9. construct typed intent and stable reason codes;
10. canonicalize and calculate evaluation hash;
11. persist immutable strategy evaluation idempotently;
12. publish/return typed result;
13. submit non-HOLD intent to deterministic risk as a separate application step.

No network call occurs inside this evaluation.

## 10. Reason Codes

Reason codes are stable, machine-readable, versioned, localized outside the domain, and linked to evidence.

Baseline categories/examples:

- input: `insufficient_history`, `stale_market_data`, `invalid_market_data`, `feature_missing`, `portfolio_state_stale`, `configuration_incompatible`;
- trend: `trend_not_confirmed`, `trend_entry_confirmed`, `trend_invalidation`, `exit_condition_met`;
- volatility/volume: `volatility_too_high`, `volume_not_confirmed`;
- AI: `gemini_not_required`, `gemini_unavailable`, `gemini_report_invalid`, `gemini_agrees_bullish`, `gemini_contradicts_entry`;
- portfolio: `existing_position_hold`, `no_position_to_exit`, `target_exposure_reached`;
- safety/fallback: `strategy_policy_hold`, `unsupported_action`, `active_halt`.

Changing a code’s meaning requires versioning. Human messages do not replace canonical codes.

## 11. Failure Behavior

Explicit outcomes include:

- successful HOLD/non-HOLD intent;
- invalid input rejection;
- HOLD due to policy/blocker;
- configuration/version incompatibility;
- deterministic calculation error;
- duplicate/idempotent replay returning canonical result;
- cancelled/timed out application operation;
- persistence conflict before side effects.

A failure never creates an order or financial effect. Unknown/missing required evidence fails closed.

## 12. Risk Boundary

Every non-HOLD intent is evaluated by the exact deterministic risk policy against the exact portfolio state and market evidence.

Strategy requested exposure/notional is only an upper request boundary. Risk may:

- approve;
- approve a reduced boundary;
- reject;
- halt portfolio;
- halt workspace/experiment according to policy.

Strategy cannot:

- treat absence of risk as approval;
- consume a stale/different risk result;
- retry around a rejection;
- issue a direct order;
- weaken limit or halt rules.

## 13. Shared Paper and Backtest Contract

The same strategy implementation and project-owned input/output contracts are used in:

- one-shot paper research cycles;
- deterministic backtests;
- repeated-run reproducibility checks;
- research/evaluation datasets;
- bounded paper canaries.

Backtests provide a replay clock and only evidence available at each event. They do not call live providers or use future portfolio state.

Any unavoidable environment adapter difference is explicit, versioned, tested, and included in compatibility/limitations.

## 14. Lifecycle

Canonical states:

1. `draft`;
2. `unit_tested`;
3. `backtested`;
4. `out_of_sample_validated`;
5. `observation_mode`;
6. `paper_candidate`;
7. `active_paper`;
8. `rolled_back`;
9. `retired`;
10. `archived`.

No state authorizes private/test/live exchange execution.

Transitions are append-only and require actor/source, reason, evidence snapshot, expected version, and audit.

## 15. Research Review and Promotion

Before future active-paper use, M032 requires:

- explicit hypothesis and causal rationale;
- approved test plan created before final evidence;
- exact datasets and split-use declarations;
- no-look-ahead and leakage checks;
- cash and buy-and-hold benchmarks;
- fees/spread/slippage/precision/minimum-notional assumptions;
- all material selected, rejected, failed, cancelled, incomplete, and unfavorable variants;
- final untouched-test result uncontaminated by parameter selection;
- robustness and parameter sensitivity;
- walk-forward evidence where data permits;
- reproducibility verification;
- turnover, costs, drawdown, tail, halt, and failure evidence;
- risk/execution/accounting compatibility;
- bounded paper observation/canary with stop conditions;
- reviewer assignment/conflict disclosure;
- immutable approval snapshot and owner decision;
- rollback/retirement plan.

Profit or a score alone cannot approve a strategy.

## 16. Change Management

Changes to formula, feature/period/threshold, Gemini policy, action meaning, exposure request, invalidation/exit, supported market/interval, reason codes, fallback, serialization/hash, or dependencies require:

- new strategy/configuration/behavior-set versions;
- M034 proposal and risk classification;
- field-level and dependency diff;
- compatibility/migration review;
- pre-approved evidence plan;
- security/privacy/cost/accessibility review as applicable;
- staged paper rollout and stop conditions;
- immutable approval snapshot;
- rollback/forward-fix and deprecation evidence;
- activation only for future configurations.

Running experiments remain frozen. Tests, CI, AI, metrics, or browser state cannot auto-activate a strategy.

## 17. Observability and Audit

Persist/measure with bounded labels:

- evaluations by strategy/version/action/status;
- HOLD/rejection/blocker reason codes;
- input/evaluation hashes;
- source snapshot/features/AI/portfolio-state versions;
- duration and deterministic error;
- AI availability/agreement/contradiction when configured;
- downstream risk result and lineage, without conflating stages;
- cycle/backtest/research/canary context;
- lifecycle/review/approval/rollback references.

Do not use profit as strategy operational health. User-facing views preserve evidence, uncertainty, simulation, and risk authority.

## 18. Testing

Required tests:

- each action and policy-HOLD outcome;
- every threshold and Decimal boundary;
- insufficient history/missing feature/null input;
- stale/invalid/invalidated snapshot;
- portfolio-state exactness and staleness;
- AI required/optional/ignored, invalid, unavailable, contradictory;
- deterministic identical-input hash/output;
- explicit seed behavior if any;
- version/configuration isolation;
- no wall clock/provider/global mutable state;
- no order/ledger/side effect;
- no short/leverage/unsupported action;
- idempotent duplicate evaluation;
- shared paper/backtest reference fixtures;
- no-look-ahead and replay-clock isolation;
- reason-code registry/localization coverage;
- lifecycle/review/approval invalidation;
- behavior-set freeze/change rollout.

Property tests cover canonical hashing, ordering independence, Decimal boundaries, and action invariants.

## 19. Completion Gate

M010 strategy work is verified only when:

- strategy versions/configurations/reason codes are implemented and immutable;
- deterministic reference/property/failure tests pass;
- market/feature/AI/portfolio-state contracts are exact;
- no direct order or risk bypass exists;
- shared paper/backtest behavior is demonstrated;
- API/schema/workspace/audit/observability/docs are synchronized;
- final commit is fetched and inspected.

Promotion to active paper additionally requires M029 observation and M032/M034 evidence/approval.

## 20. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `MARKET_DATA.md`
- `AI_ARCHITECTURE.md`
- `GEMINI_INTEGRATION.md`
- `RISK_ENGINE.md`
- `PAPER_TRADING.md`
- `BACKTEST_ENGINE.md`
- `RESEARCH_REVIEW_STRATEGY_LIFECYCLE_WORKSPACE_IMPLEMENTATION.md`
- `CHANGE_MANAGEMENT_ROLLOUT_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
- `TESTING.md`
