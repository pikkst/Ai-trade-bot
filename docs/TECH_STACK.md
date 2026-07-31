# Technology Stack

Last reviewed: 2026-07-31

## Decision Status

This document defines the default MVP stack. Alternatives require an Architecture Decision Record before adoption.

## Backend

- Python 3.12 baseline
- FastAPI for HTTP APIs
- Pydantic v2 and `pydantic-settings` for boundary validation and configuration
- SQLAlchemy 2 for persistence
- Alembic for additive database migrations
- Uvicorn for local serving
- Pytest and Hypothesis for testing
- Ruff for formatting and linting
- MyPy strict mode for static typing

## Database and Background Jobs

- PostgreSQL as the authoritative system of record
- Redis for queues, locks, caching, and ephemeral coordination
- ARQ as the MVP async job runner
- Polars for new analytical data pipelines
- Pandas only where a required library lacks a practical Polars integration

## Exchange Integration

- Binance Spot native REST API for metadata, backfill, reconciliation, and request-response operations
- Binance Spot WebSocket Streams for near-real-time public market data
- CCXT may be used only behind an adapter for research or future multi-exchange support; it is not the source of truth for Binance filters, precision, signatures, or rate-limit behavior

## AI

- Google Gemini API is the authoritative cloud AI provider for version 1
- Official Google Gen AI Python SDK (`google-genai`)
- Project-owned provider-independent `LLMProvider` protocol
- Gemini structured output with JSON Schema or Pydantic where supported
- Deterministic fake provider for CI and unit tests
- Versioned prompts, schemas, models, safety settings, and evaluation datasets
- Explicit request, token, and cost budgets

OpenAI is not part of the version 1 implementation plan. Ollama or vLLM may be added later through an ADR without changing domain contracts.

Models must be configured and pinned for each experiment rather than hardcoded into domain logic. Preview models must not be used for a production-facing deployment unless their current service status and terms explicitly permit production use.

## Frontend

- React
- TypeScript strict mode
- Vite
- TanStack Query for server state
- React Router
- Zod for client boundary validation where generated OpenAPI types are insufficient
- A charting library selected through an ADR before implementation

## Infrastructure and Operations

- Docker Compose for local and initial sandbox environments
- Prometheus for metrics
- Grafana for dashboards and alert visualization
- OpenTelemetry-compatible tracing when distributed debugging becomes necessary
- GitHub Actions for CI
- Trivy for container and filesystem scanning

## Security and Quality

- Bandit
- Semgrep
- Dependency review and automated update tooling
- Secret scanning
- SBOM generation before sandbox release
- Pinned container image versions and dependency lock files

## Versioning Policy

Exact dependency versions belong in lock files and build manifests. Every release must record:

- Python runtime version
- Node.js runtime version
- locked Python dependencies
- locked frontend dependencies
- container image digests
- database migration revision
- strategy and risk-policy versions
- Gemini model, prompt, schema, and safety-setting versions

## Selection Principles

The stack prioritizes deterministic behavior, strong typing, auditability, local development, reproducibility, replaceable infrastructure adapters, and low operational complexity for the first version.