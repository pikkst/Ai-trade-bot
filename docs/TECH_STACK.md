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

Python 3.12 is selected as the compatibility baseline. Newer runtimes may be added to CI after all critical dependencies are verified, but production must use a pinned and tested runtime.

## Database and Background Jobs

- PostgreSQL as the authoritative system of record
- Redis for queues, locks, caching, and ephemeral coordination
- ARQ as the MVP async job runner
- Polars for new analytical data pipelines
- Pandas only where a required library lacks a practical Polars integration

The previous open choices of “Celery or ARQ” and “Pandas or Polars” are resolved for the MVP. ARQ and Polars minimize initial operational and dependency complexity. A move to Celery requires evidence that ARQ no longer meets reliability or scheduling requirements.

## Exchange Integration

- Binance Spot native REST API for metadata, backfill, reconciliation, and request-response operations
- Binance Spot WebSocket Streams for near-real-time public market data
- CCXT may be used only behind an adapter for research or future multi-exchange support; it is not the source of truth for Binance filters, precision, signatures, or rate-limit behavior

## AI

- Provider-independent `LLMProvider` protocol
- OpenAI Responses API for new OpenAI integration work
- Strict JSON Schema Structured Outputs where supported
- Ollama for simple local development
- vLLM for future higher-throughput local serving
- Fake deterministic provider for CI and tests
- Versioned prompts, schemas, models, and evaluation datasets

Models must be configured and pinned rather than hardcoded into domain logic.

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

Exact dependency versions belong in lock files and build manifests, not in prose documentation. Every release must record:

- Python runtime version
- Node.js runtime version
- Locked Python dependencies
- Locked frontend dependencies
- Container image digests
- Database migration revision
- Strategy, risk-policy, prompt, and AI schema versions

## Selection Principles

The stack prioritizes deterministic behavior, strong typing, auditability, local development, reproducibility, replaceable provider adapters, and low operational complexity for the first version.