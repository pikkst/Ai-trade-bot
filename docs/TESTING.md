# Testing

## Layers
Unit, integration, contract, end-to-end, and property-based tests.

## Critical Cases
Duplicate jobs, stale or missing candles, malformed AI output, provider timeout, position limit, drawdown halt, partial fills, fee rounding, restart recovery, ledger mismatch, and unauthorized commands.

## Release Gates
Ruff, MyPy strict, migration tests, unit and integration tests, no critical or high security findings, 85% core-domain coverage target, and a complete paper-trading smoke test.

Property-based tests must verify ledger conservation, non-negative balances, idempotency, and precision boundaries.
