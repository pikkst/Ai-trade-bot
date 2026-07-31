# Documentation Audit

Last reviewed: 2026-07-31
Audit scope: all root documentation, all Markdown files under `docs/`, `.env.example`, and task-governance rules
Status: Completed for the pre-implementation specification baseline

## 1. Executive Result

The repository documentation has been reviewed and corrected as a single system rather than as isolated files.

The current pre-implementation specification is internally coherent enough to begin task-by-task MVP development. It consistently defines:

- Google Gemini API as the required cloud AI provider for version 1;
- Binance Spot public market data as the MVP exchange-data source;
- deterministic strategy, risk, execution, and accounting boundaries;
- paper trading only for MVP;
- PostgreSQL as the authoritative system of record;
- Redis as ephemeral queue and coordination infrastructure;
- an append-only double-entry ledger as the financial source of truth;
- fail-closed behavior for stale data, invalid policy, precision, database, and reconciliation failures;
- complete lineage from source candles to analysis, intent, risk decision, order, fill, ledger, and report;
- detailed implementation tasks with acceptance criteria and Definition of Done.

No remaining OpenAI, Celery, Ollama, or vLLM implementation requirement was found in the current MVP documentation. Future alternative providers require a new ADR.

## 2. Files Audited

### Root

- `README.md`
- `AGENTS.md`
- `TASKS.md`
- `ROADMAP.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `.env.example`
- `LICENSE`

### Specifications

- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/BACKEND.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/AI_ARCHITECTURE.md`
- `docs/GEMINI_INTEGRATION.md`
- `docs/AGENTS.md`
- `docs/AI_PROMPTS.md`
- `docs/MARKET_DATA.md`
- `docs/BINANCE_INTEGRATION.md`
- `docs/STRATEGY_ENGINE.md`
- `docs/RISK_ENGINE.md`
- `docs/PAPER_TRADING.md`
- `docs/PORTFOLIO_ENGINE.md`
- `docs/BACKTEST_ENGINE.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `docs/OBSERVABILITY.md`
- `docs/DEPLOYMENT.md`
- `docs/TECH_STACK.md`
- `docs/ADR.md`
- `docs/DOCUMENTATION_AUDIT.md`

## 3. Major Findings and Corrections

### 3.1 AI Provider Ambiguity

**Finding:** Earlier documentation mixed generic providers and previous OpenAI assumptions.

**Correction:** Google Gemini API is now the only required cloud provider for V1. The official `google-genai` SDK is isolated behind the project-owned `LLMProvider` protocol. CI uses a deterministic fake provider.

### 3.2 Coding Agents vs Runtime Agents

**Finding:** Two files named `AGENTS.md` could be misunderstood.

**Correction:** Root `/AGENTS.md` is the mandatory coding-agent/contributor guide. `docs/AGENTS.md` is the runtime analytical-agent specification. README and both documents state this distinction.

### 3.3 Strategy, Risk, and Sizing Authority

**Finding:** Earlier summaries did not make authority boundaries sufficiently explicit.

**Correction:** Strategy emits typed intents only. Risk calculates the final approved upper bound. Gemini cannot size positions. Clients cannot submit arbitrary unapproved paper-order quantities.

### 3.4 Accounting Source of Truth

**Finding:** Mutable balances and portfolio projections could have been interpreted as authoritative.

**Correction:** The append-only double-entry ledger is authoritative. Balances, positions, P&L, equity, exposure, and drawdown are rebuildable projections. Reconciliation mismatch causes a halt.

### 3.5 Backtest AI Reproducibility

**Finding:** Live Gemini calls during historical replay would make standard backtests expensive and non-reproducible.

**Correction:** Standard backtests disable AI or use immutable precomputed validated Gemini reports tied to exact snapshots and versions. Sampled live-model historical research is a separate experiment.

### 3.6 Paper-Fill Ambiguity

**Finding:** A short fill description left timing, partial fills, precision, minimum notional, fees, and intrabar ambiguity underspecified.

**Correction:** Execution-model versions now define reference price, spread, slippage, fees, volume participation, partial fills, precision, filters, time in force, and conservative intrabar ordering.

### 3.7 Environment Configuration Gaps

**Finding:** `.env.example` did not represent the full planned typed settings surface.

**Correction:** Safe placeholder configuration now covers application, database, Redis/ARQ, authentication, Binance public data, Gemini, features, strategy, paper trading, risk, experiment, observability, retention, and prohibited feature flags.

### 3.8 Roadmap Scope Drift

**Finding:** Later live and productization phases could be read as automatically approved progression.

**Correction:** Every phase has explicit gates. Binance test-environment work and any real-capital assessment require new owner decisions, current provider capability checks, security review, and separate specifications.

### 3.9 API and Database Detail

**Finding:** Initial documents were endpoint/table lists rather than contracts.

**Correction:** API resources now include roles, idempotency, errors, async jobs, configuration versions, experiments, audit, OpenAPI checks, and security rules. The logical database schema now defines ownership, key fields, constraints, indexes, retention, and migration policy.

### 3.10 Task Granularity

**Finding:** The original task file was a shallow checklist.

**Correction:** `TASKS.md` now uses independently implementable task cards containing priority, description, user story, objective acceptance criteria, Definition of Done, dependencies, references, and notes where relevant.

## 4. Coverage Matrix

| Area | Authoritative document | Audit status |
|---|---|---|
| Product scope and requirements | `docs/PRODUCT_REQUIREMENTS.md` | Expanded and consistent |
| System architecture | `docs/ARCHITECTURE.md` | Expanded and consistent |
| Coding-agent instructions | `AGENTS.md` | Complete baseline |
| Runtime analytical agents | `docs/AGENTS.md` | Expanded and bounded |
| Backend implementation rules | `docs/BACKEND.md` | Expanded and consistent |
| REST API | `docs/API_SPECIFICATION.md` | Logical contract complete; generated schemas depend on code |
| Database | `docs/DATABASE_SCHEMA.md` | Logical schema complete; migrations depend on code |
| Market data | `docs/MARKET_DATA.md` | Expanded and consistent |
| Binance adapter | `docs/BINANCE_INTEGRATION.md` | Consistent with public-data MVP |
| AI architecture | `docs/AI_ARCHITECTURE.md` | Gemini aligned |
| Gemini provider | `docs/GEMINI_INTEGRATION.md` | Authoritative V1 provider specification |
| Prompt design | `docs/AI_PROMPTS.md` | Expanded and consistent |
| Strategy | `docs/STRATEGY_ENGINE.md` | Expanded and deterministic |
| Risk | `docs/RISK_ENGINE.md` | Expanded and fail closed |
| Paper execution | `docs/PAPER_TRADING.md` | Expanded and conservative |
| Portfolio accounting | `docs/PORTFOLIO_ENGINE.md` | Expanded with ledger and reconciliation |
| Backtesting | `docs/BACKTEST_ENGINE.md` | Expanded with AI/reproducibility rules |
| Security | `docs/SECURITY.md` | Expanded threat model and release gates |
| Testing | `docs/TESTING.md` | Expanded domain and failure matrix |
| Observability | `docs/OBSERVABILITY.md` | Expanded metrics, alerts, dashboards, runbooks |
| Deployment | `docs/DEPLOYMENT.md` | Expanded environments and promotion gates |
| Technology choices | `docs/TECH_STACK.md` | Definitive MVP choices |
| Decisions | `docs/ADR.md` | Expanded accepted decisions |
| Implementation backlog | `TASKS.md` | Detailed task-card baseline |
| Product roadmap | `ROADMAP.md` | Expanded gated phases |
| Contribution workflow | `CONTRIBUTING.md` | Expanded and aligned |
| Repository entry point | `README.md` | Inventory and precedence aligned |

## 5. Cross-Document Invariants Verified

The following statements are now consistent across the repository:

1. MVP uses paper trading only.
2. Private Binance account access is not required for MVP.
3. Google Gemini is advisory only.
4. Gemini cannot execute orders or modify strategy/risk policy.
5. Every actionable strategy intent passes deterministic risk evaluation.
6. Risk failures fail closed.
7. Monetary calculations use `Decimal`/PostgreSQL `numeric`.
8. All timestamps are timezone-aware UTC.
9. PostgreSQL is authoritative; Redis is ephemeral.
10. Ledger and audit evidence are append-only.
11. Every repeatable side effect is idempotent.
12. Finalized candles are normal decision inputs.
13. Fees and slippage are mandatory in simulation.
14. Backtests prohibit look-ahead.
15. Reconciliation mismatch halts activity.
16. Active experiments use frozen versioned configuration.
17. Profit is not an MVP acceptance criterion.
18. Live trading requires a separate future milestone and approval.

## 6. README Inventory Verification

The README inventory uses exact current paths and includes every authoritative Markdown document currently planned for the specification set.

No nonexistent document is intentionally presented as already implemented. Generated artifacts are clearly identified as future implementation outputs.

## 7. Task Structure Verification

The task-card standard is:

- unique task ID and title;
- priority;
- description;
- user story;
- acceptance criteria;
- Definition of Done;
- dependencies;
- authoritative references;
- notes when parallelism or special constraints apply.

A task must not be marked complete merely because code exists. Test, documentation, security, migration, metrics, and operational acceptance evidence must also pass where applicable.

## 8. Implementation-Dependent Artifacts

The following cannot truthfully exist as final artifacts until code is implemented. Their absence is not a documentation defect; their required creation is specified in `TASKS.md` and related documents:

1. exact Python and frontend dependency lock files;
2. generated OpenAPI document and route inventory;
3. actual Alembic migrations and database DDL;
4. exact implemented feature formulas and golden fixtures;
5. exact paper fill formulas and calibration evidence;
6. Prometheus metric names and alert-rule files;
7. Grafana dashboard provisioning JSON;
8. Gemini evaluation datasets and baseline results;
9. container image digests and SBOMs;
10. measured performance, restore, RPO, and RTO results;
11. current legal/regulatory assessment before third-party or real-money use.

These artifacts must remain synchronized with code and are release gates where specified.

## 9. Remaining Controlled Assumptions

The documents intentionally leave these as configurable or implementation-verified choices:

- exact stable Gemini model identifier;
- active Gemini project quota and pricing;
- exact dependency versions;
- final authentication refresh/session model;
- exact weighted-average cost fee treatment;
- exact indicator periods and thresholds for the baseline strategy;
- exact fee/spread/slippage calibration;
- exact infrastructure RPO/RTO;
- exact charting library.

Each has an explicit task, ADR requirement, configuration version, or implementation-time verification rule. None may be silently chosen in domain code.

## 10. Future Audit Procedure

For every material documentation or implementation change:

1. verify README links and inventory;
2. search for obsolete provider and technology names;
3. verify terminology against product requirements;
4. verify architecture and ADR consistency;
5. verify API resource ownership and persistence mapping;
6. verify every strategy path reaches risk, execution, ledger, audit, and tests;
7. verify `.env.example` matches typed settings without secrets;
8. verify Gemini guidance against current official Google documentation and project quota dashboard;
9. verify Binance behavior against current official Spot documentation;
10. verify new tasks follow the detailed task-card format;
11. update changelog and this audit date;
12. do not claim generated or measured artifacts exist before they do.

## 11. Final Audit Conclusion

The repository's documentation baseline is complete for beginning MVP implementation from `T1.1`.

“Complete” here means that the planned system, safety boundaries, interfaces, data ownership, development process, and task acceptance requirements are documented consistently. It does not falsely claim that code-generated schemas, migrations, dashboards, evaluation results, or measured operational evidence already exist.

The next valid action is implementation through `TASKS.md`, with documentation updated in the same pull requests as code.
