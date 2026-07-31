# Documentation Audit

Last reviewed: 2026-07-31

## Audit Result

The repository contains the correct major document categories for an MVP, but the initial files were concise design summaries rather than implementation-complete specifications. This audit defines the authoritative coverage map and the remaining documentation work.

## Coverage Matrix

| Area | Authoritative document | Status |
|---|---|---|
| Product scope and requirements | `PRODUCT_REQUIREMENTS.md` | Baseline complete; detailed acceptance criteria should evolve with implementation |
| System architecture | `ARCHITECTURE.md` | Baseline complete |
| AI coding instructions | `/AGENTS.md` | Complete initial version |
| Runtime AI agents | `AGENTS.md` | Baseline complete |
| Backend rules | `BACKEND.md` | Baseline complete |
| REST API | `API_SPECIFICATION.md` | Endpoint baseline complete; request/response schemas remain implementation tasks |
| Database | `DATABASE_SCHEMA.md` | Entity baseline complete; column-level schema remains implementation work |
| Market data | `MARKET_DATA.md` | Baseline complete |
| Binance | `BINANCE_INTEGRATION.md` | Updated baseline required and tracked below |
| AI providers and outputs | `AI_ARCHITECTURE.md` | Updated baseline required and tracked below |
| Prompt design | `AI_PROMPTS.md` | Baseline complete |
| Strategy | `STRATEGY_ENGINE.md` | Baseline complete |
| Risk | `RISK_ENGINE.md` | Baseline complete |
| Paper execution | `PAPER_TRADING.md` | Baseline complete |
| Portfolio ledger | `PORTFOLIO_ENGINE.md` | Baseline complete |
| Backtesting | `BACKTEST_ENGINE.md` | Baseline complete |
| Security | `SECURITY.md` | Baseline complete |
| Testing | `TESTING.md` | Baseline complete |
| Observability | `OBSERVABILITY.md` | Baseline complete |
| Deployment | `DEPLOYMENT.md` | Baseline complete |
| Technology choices | `TECH_STACK.md` | Must use definitive MVP choices |
| Implementation backlog | `/TASKS.md` | MVP baseline complete |
| Product roadmap | `/ROADMAP.md` | Baseline complete |

## Important Distinction

`/AGENTS.md` contains instructions for AI coding tools and contributors.

`/docs/AGENTS.md` describes runtime analytical agents that may exist inside the product. These files serve different purposes and must not be merged.

## Current External API Guidance

- Binance Spot REST and WebSocket interfaces are the primary exchange integration surface. The adapter must follow the official current Spot documentation and rate-limit metadata.
- Exchange testnet or demo environments are used only after internal paper trading is stable.
- The OpenAI adapter should use the Responses API for new integration work.
- Strict JSON Schema Structured Outputs should be preferred where supported.
- Model identifiers should be pinned for reproducible experiments.
- Provider request IDs, response IDs, model identifiers, token usage, latency, and cost estimates must be retained.
- OpenAI requests should use `store=false` unless a documented requirement explicitly needs provider-side storage.

## Missing Detail That Must Be Added During Implementation

The following content cannot be truthfully finalized before implementation decisions and schemas exist. Each item is already represented in `TASKS.md` and must be added in the same pull request as the implementation:

1. Exact Python and JavaScript dependency versions.
2. Complete OpenAPI request and response schemas.
3. Column-level SQL definitions and migration history.
4. Exchange filter and precision examples captured from current API responses.
5. Exact fill-model formulas and calibration evidence.
6. Exact Prometheus metric names and dashboard JSON.
7. Environment-specific deployment manifests.
8. Recovery-time and recovery-point objectives based on deployed infrastructure.
9. Measured performance targets and load-test results.
10. Final legal and regulatory assessment before offering the system to third parties.

## Consistency Rules

- The MVP is paper-trading only.
- No document may imply that an LLM has direct execution authority.
- Every strategy action passes through deterministic risk validation.
- Monetary calculations use decimal arithmetic.
- All state-changing commands are idempotent.
- The append-only ledger is the portfolio source of truth.
- Reconciliation mismatch halts trading.
- Fees and slippage are mandatory in simulations.
- Backtests prohibit look-ahead.
- Live trading requires a separate owner-approved milestone and security review.

## Audit Procedure for Future Changes

For every documentation review:

1. Verify all links from `README.md`.
2. Verify terminology against `PRODUCT_REQUIREMENTS.md`.
3. Verify architecture boundaries against `ARCHITECTURE.md` and `/AGENTS.md`.
4. Verify every API resource has a data owner and persistence model.
5. Verify every strategy path has risk, execution, ledger, audit, and test coverage.
6. Verify all environment variables are documented without containing secrets.
7. Verify no document enables prohibited MVP scope.
8. Verify external-provider instructions against official documentation.
9. Record the audit date and material changes in `CHANGELOG.md`.

## Conclusion

The documentation set is structurally complete for beginning implementation. It is not a frozen 100-percent implementation specification: exact schemas, dependency pins, generated API contracts, dashboards, and operational measurements must remain synchronized with the code as it is built. `/AGENTS.md` makes this synchronization mandatory for AI coding agents.