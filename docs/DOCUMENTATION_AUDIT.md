# Documentation Audit

Last reviewed: 2026-07-31

## Audit Result

The repository now contains the major specification categories required to begin MVP implementation. The README inventory uses exact repository paths, Google Gemini API is the authoritative version 1 cloud AI provider, and `TASKS.md` contains independently executable work items with acceptance criteria and definitions of done.

## Coverage Matrix

| Area | Authoritative document | Status |
|---|---|---|
| Product scope and requirements | `docs/PRODUCT_REQUIREMENTS.md` | Baseline complete; exact implemented acceptance evidence evolves with code |
| System architecture | `docs/ARCHITECTURE.md` | Baseline complete |
| AI coding instructions | `AGENTS.md` | Complete initial version |
| Runtime analytical agents | `docs/AGENTS.md` | Baseline complete |
| Backend rules | `docs/BACKEND.md` | Baseline complete |
| REST API | `docs/API_SPECIFICATION.md` | Resource baseline complete; exact generated schemas are implementation outputs |
| Database | `docs/DATABASE_SCHEMA.md` | Entity baseline complete; exact columns and migrations are implementation outputs |
| Market data | `docs/MARKET_DATA.md` | Baseline complete |
| Binance | `docs/BINANCE_INTEGRATION.md` | Updated baseline complete |
| AI architecture | `docs/AI_ARCHITECTURE.md` | Gemini-aligned baseline complete |
| Gemini provider | `docs/GEMINI_INTEGRATION.md` | Authoritative version 1 provider specification complete |
| Prompt design | `docs/AI_PROMPTS.md` | Baseline complete; exact prompt assets belong in `ai/` during implementation |
| Strategy | `docs/STRATEGY_ENGINE.md` | Baseline complete |
| Risk | `docs/RISK_ENGINE.md` | Baseline complete |
| Paper execution | `docs/PAPER_TRADING.md` | Baseline complete |
| Portfolio ledger | `docs/PORTFOLIO_ENGINE.md` | Baseline complete |
| Backtesting | `docs/BACKTEST_ENGINE.md` | Baseline complete |
| Security | `docs/SECURITY.md` | Baseline complete |
| Testing | `docs/TESTING.md` | Baseline complete |
| Observability | `docs/OBSERVABILITY.md` | Baseline complete |
| Deployment | `docs/DEPLOYMENT.md` | Baseline complete |
| Technology choices | `docs/TECH_STACK.md` | Definitive MVP choices recorded |
| Implementation backlog | `TASKS.md` | Detailed MVP task cards complete for the first implementation sequence |
| Product roadmap | `ROADMAP.md` | Baseline complete |

## Important Distinction

- `/AGENTS.md` contains mandatory rules for AI coding tools and contributors.
- `/docs/AGENTS.md` describes runtime analytical agents inside the product.

These files have different responsibilities and must not be merged.

## Current External API Guidance

- Binance Spot REST and WebSocket interfaces are the primary exchange integration surface.
- Internal paper trading is completed and evaluated before exchange testnet or demo execution is considered.
- Google Gemini API is the required cloud LLM provider for version 1.
- Use the official Google Gen AI SDK and structured output with project-owned JSON Schema or Pydantic models where supported.
- Model, prompt, schema, safety-setting, and experiment versions must be recorded.
- Gemini requests must retain request metadata, latency, token usage, retry history, safety outcome, and estimated cost.
- Normal CI must use a deterministic fake provider and must not require a paid Gemini call.
- Function calling, code execution, Google Search grounding, exchange tools, and database mutation tools are disabled for the initial technical-analysis flow.
- Current Gemini terms, model status, region availability, paid-service requirements, and data-handling behavior must be reviewed before any production-facing release.

## Missing Detail That Must Be Produced with Implementation

These items cannot be finalized honestly before the corresponding code exists. `TASKS.md` requires them to be produced in the same pull request as implementation:

1. Exact Python and JavaScript dependency locks.
2. Complete generated OpenAPI request and response schemas.
3. Column-level SQL definitions and Alembic migration history.
4. Exchange filter and precision examples captured from current Binance responses.
5. Exact indicator and fill-model formulas with verified fixtures.
6. Exact Prometheus metric names, alert rules, and Grafana provisioning files.
7. Environment-specific deployment manifests and image digests.
8. Measured performance, recovery-time, and recovery-point evidence.
9. Gemini evaluation datasets, baseline reports, and regression thresholds.
10. Final legal and regulatory assessment before offering the system to third parties.

## Consistency Rules

- The MVP is paper-trading only.
- Gemini has no direct execution authority.
- Every strategy intent passes through deterministic risk validation.
- Monetary calculations use decimal arithmetic.
- All state-changing commands are idempotent.
- The append-only ledger is the portfolio source of truth.
- Reconciliation mismatch halts the affected portfolio or workspace.
- Fees and slippage are mandatory in simulations.
- Backtests prohibit look-ahead.
- Live trading requires a separate owner-approved milestone, security review, and readiness gate.

## README Inventory Audit

The README documentation table must:

1. use exact repository paths;
2. list only files that exist;
3. distinguish specifications from generated implementation artifacts;
4. include every new authoritative document;
5. remove or update renamed and deleted documents in the same pull request.

## Task Quality Audit

Every new task must include:

- task ID and title;
- priority;
- description;
- user story;
- objective acceptance criteria;
- definition of done;
- explicit dependencies;
- authoritative references;
- notes where parallelism or special constraints matter.

A one-line checklist item is not sufficient for implementation work.

## Audit Procedure for Future Changes

1. Verify every README link resolves to an existing file.
2. Verify terminology against product requirements and architecture.
3. Verify coding-agent boundaries against `/AGENTS.md`.
4. Verify every API resource has a domain owner and persistence plan.
5. Verify every strategy path has risk, execution, ledger, audit, and test coverage.
6. Verify environment variables are documented without secrets.
7. Verify no document enables prohibited MVP scope.
8. Verify Binance and Gemini guidance against official current documentation.
9. Verify every task uses the required detailed structure.
10. Record material changes in `CHANGELOG.md`.

## Conclusion

The documentation is now coherent enough to begin task-by-task MVP implementation. It remains a living specification: generated API contracts, migrations, dependency locks, dashboards, evaluation reports, and measured operational evidence must remain synchronized with code.