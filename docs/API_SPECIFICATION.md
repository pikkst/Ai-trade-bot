# API Specification

Base path: `/api/v1`; JSON; Bearer JWT; `Idempotency-Key` for commands.

## Endpoints
- `GET /health/live`
- `GET /health/ready`
- `POST /workspaces`
- `GET /workspaces/{id}`
- `PATCH /workspaces/{id}`
- `GET /market/symbols`
- `GET /market/candles`
- `GET /market/snapshots/{id}`
- `POST /analysis`
- `GET /analysis/{id}`
- `POST /strategy-evaluations`
- `GET /strategy-evaluations/{id}`
- `GET /risk/policies`
- `POST /risk/evaluations`
- `POST /paper-portfolios`
- `GET /paper-portfolios/{id}`
- `POST /paper-orders`
- `GET /paper-orders/{id}`
- `POST /paper-orders/{id}/cancel`
- `POST /paper-portfolios/{id}/halt`
- `POST /backtests`
- `GET /backtests/{id}`
- `GET /backtests/{id}/report`
- `GET /audit/events`

Breaking changes require a new API version. Persisted asynchronous payloads include explicit schema versions.
