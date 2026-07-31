# Technology Stack

Last reviewed: 2026-07-31
Status: Authoritative technology selection for the first cloud experiment

## Application

- Python 3.12
- FastAPI, Pydantic v2, SQLAlchemy 2, Alembic
- Polars for analytical calculations
- React, TypeScript strict mode, Vite, TanStack Query, React Router
- Google Gemini API through the official `google-genai` SDK
- Binance Spot public REST API

## Free Cloud Deployment Profile

- Supabase Free: managed PostgreSQL and Auth
- Render Free Web Service: FastAPI HTTP backend
- Cloudflare Pages Free: static React frontend
- GitHub Actions: CI and approximately hourly research-cycle scheduling
- GitHub artifacts and database records: experiment reports and diagnostics

The 30-day MVP does not require a paid service or a continuously running local computer.

## Deliberately Deferred Infrastructure

The first free-cloud deployment does not require Redis, ARQ, persistent WebSocket ingestion, hosted Prometheus, hosted Grafana, Kubernetes, or private Binance APIs.

These components may be introduced later only after measured need and an accepted ADR. Existing domain contracts must remain compatible with a future queue or persistent worker.

## Data and Scheduling

PostgreSQL is the authoritative source of truth. A one-shot research-cycle CLI is scheduled through GitHub Actions and uses a PostgreSQL advisory lock or database lease for concurrency control and idempotency.

Hourly finalized-candle ingestion uses Binance REST. WebSocket ingestion is a later optimization, not an MVP requirement.

## Authentication and Browser Access

Supabase Auth supplies user identity. FastAPI performs server-side authorization for commands. Browser Data API access is deny-by-default and limited to approved RLS-protected read views.

Frontend bundles may contain only the Supabase URL, publishable key, and public API URL. Service-role, database, Gemini, JWT-signing, and future exchange secrets remain server-side.

## AI

- Gemini is advisory only.
- Structured output uses project-owned Pydantic/JSON Schema contracts.
- CI uses a deterministic fake provider.
- The experiment has explicit request, token, and EUR cost budgets.
- Default monthly Gemini cost budget for the free experiment is EUR 0.

## Quality and Security

- Pytest and Hypothesis
- Ruff and MyPy strict
- Bandit, Semgrep, dependency review, secret scanning, and Trivy
- committed dependency lock files
- generated OpenAPI and migration validation
- RLS authorization tests

## Free-Tier Caveat

Free tiers are best-effort. They may sleep, pause, throttle, restart, delay scheduled work, or change limits. The system must degrade safely and must not claim production availability or an SLA.

Current provider quotas and terms are checked before deployment and experiment start; prose documentation is not a quota source of truth.

## Related Documents

- `FREE_CLOUD_ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `ARCHITECTURE.md`
- `GEMINI_INTEGRATION.md`
- `../CLOUD_MVP_TASKS.md`
