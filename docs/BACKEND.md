# Backend

## Structure
```text
backend/app/
├── api/
├── core/
├── domains/
├── infrastructure/
├── workers/
└── main.py
```

## Rules
Domain modules do not import FastAPI. Services depend on protocols. ORM entities are not API models. Money uses Decimal. Time is UTC. Commands require idempotency keys. Transaction boundaries belong to command handlers.

## Configuration
Pydantic settings validate application, database, Redis, exchange, AI, risk, observability, and security configuration.

## Error Codes
`validation_error`, `authentication_error`, `authorization_error`, `not_found`, `conflict`, `stale_data`, `provider_unavailable`, `ai_output_invalid`, `risk_rejected`, `trading_halted`, `internal_error`.

## Quality
Ruff, MyPy strict, Pytest, no broad exception swallowing, no secrets in exceptions.
