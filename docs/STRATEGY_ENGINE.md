# Strategy Engine

Strategies are deterministic, versioned, and testable.

## Intents
HOLD, ENTER, EXIT, REDUCE.

## Output
Intent, symbol, direction, target exposure request, evidence references, invalidation condition, and strategy version.

## Lifecycle
Draft, unit tested, backtested, out-of-sample validated, observation mode, paper trading, sandbox candidate, approved or archived.

Initial baseline: conservative BTC/EUR trend strategy without leverage or short selling. Parameters must be configuration, not hidden code.
