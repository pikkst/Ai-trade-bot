# Documentation Audit

Last reviewed: 2026-07-31
Audit scope: root documentation, all `docs/` specifications, `.env.example`, and cloud task governance
Status: Completed for the free-cloud pre-implementation baseline

## Executive Result

The documentation has been updated from a persistent Redis/ARQ/WebSocket sandbox design to a zero-required-cost cloud experiment profile.

The current authoritative MVP consistently defines:

- Cloudflare Pages for the static frontend;
- Render Free for FastAPI;
- a dedicated Supabase Free project for PostgreSQL and Auth;
- GitHub Actions for approximately hourly one-shot research cycles;
- Binance Spot REST and finalized candles;
- Google Gemini API as advisory AI with EUR 0 monthly cost budget by default;
- PostgreSQL locking/idempotency instead of mandatory Redis/ARQ;
- structured logs and persistent cycle/audit status instead of required hosted Prometheus/Grafana;
- paper trading only and no private Binance credentials.

## New Authoritative Files

- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `CLOUD_MVP_TASKS.md`

`CLOUD_MVP_TASKS.md` supersedes initial infrastructure task assumptions that require Redis, ARQ, persistent WebSocket ingestion, or hosted Prometheus/Grafana. Shared domain tasks in `TASKS.md` remain applicable.

## Corrected Contradictions

### Queue and Scheduler

Earlier documents treated Redis and ARQ as mandatory MVP infrastructure. They are now deferred. The free-cloud profile uses a one-shot CLI, GitHub Actions, and a PostgreSQL advisory lock or lease.

### Market Ingestion

Earlier architecture required REST plus a persistent WebSocket consumer. The hourly experiment now uses finalized REST candles and gap repair. WebSocket ingestion is a future optimization.

### Monitoring

Earlier documents required hosted Prometheus/Grafana before the experiment. The free profile uses provider logs, health endpoints, durable cycle/audit/freshness/halt/reconciliation records, and frontend status. Prometheus/Grafana are deferred.

### Database and Auth

The first experiment now uses a dedicated Supabase project. The existing Eventnexus project must not be reused. RLS is deny-by-default and browser writes to financial/control tables are prohibited.

### Backend Availability

Render cold starts or idle spin-down no longer threaten scheduled execution because GitHub Actions runs the research CLI independently.

## Free-Tier Risk Controls

- no SLA or production claim;
- no automatic paid upgrade;
- provider limits are checked at deployment time;
- delayed/missed cycles are recorded and never fabricated;
- stale data blocks entries;
- Gemini failure/quota exhaustion degrades safely;
- local and Render filesystems are not authoritative;
- database export and restore drills are required.

## Documentation Coverage

| Area | Authoritative document | Status |
|---|---|---|
| Product and experiment | `PRODUCT_REQUIREMENTS.md` | Baseline complete |
| Cloud topology | `FREE_CLOUD_ARCHITECTURE.md` | Complete |
| Runtime architecture | `ARCHITECTURE.md` | Free-cloud aligned |
| Technology stack | `TECH_STACK.md` | Free-cloud aligned |
| Deployment | `DEPLOYMENT.md` | Free-cloud aligned |
| Coding-agent rules | `/AGENTS.md` | Free-cloud aligned |
| Cloud tasks | `/CLOUD_MVP_TASKS.md` | Detailed active sequence |
| Shared domain tasks | `/TASKS.md` | Applicable with cloud overrides |
| Backend | `BACKEND.md` | One-shot CLI/FastAPI aligned |
| Observability | `OBSERVABILITY.md` | Free-tier profile complete |
| ADRs | `ADR.md` | Superseding decisions recorded |
| Environment example | `/.env.example` | Free-cloud variables aligned |

## Known Implementation-Dependent Artifacts

These are not yet complete because code does not exist:

- Supabase project and non-secret project identifiers;
- `supabase/config.toml` and migrations;
- exact RLS SQL and authorization tests;
- dependency locks;
- GitHub Actions workflow YAML;
- Render and Cloudflare deployment configuration;
- generated OpenAPI;
- exact SQL schema and migration history;
- database export/restore evidence;
- experiment preflight report;
- public frontend/API URLs.

Each is required by `CLOUD_MVP_TASKS.md` and must be created with implementation.

## Audit Rules for Future Changes

1. Verify README links and inventory.
2. Verify active tasks against accepted ADRs.
3. Search for Redis/ARQ/WebSocket/Prometheus/Grafana references and ensure they are clearly marked deferred where applicable.
4. Verify no document permits reuse of the Eventnexus Supabase project.
5. Verify RLS and browser-write restrictions remain consistent.
6. Verify free-tier limitations and safe degradation remain documented.
7. Verify all financial side effects remain idempotent and risk-gated.
8. Verify Gemini remains advisory and within configured cost budgets.
9. Update changelog for material architecture changes.

## Conclusion

The documentation is coherent for starting the free-cloud MVP. Begin with `T1.1`, `T1.2`, then follow `C1` through `C8` together with the referenced shared domain tasks.
