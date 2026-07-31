# Free Cloud Requirements Addendum

Last reviewed: 2026-07-31
Status: Authoritative addendum to `PRODUCT_REQUIREMENTS.md` for the first 30-day experiment

Where this addendum conflicts with deployment, scheduling, ingestion, or hosted-observability assumptions in the base PRD, this addendum controls for the free-cloud MVP.

## Deployment Requirements

- FCR-001: The formal experiment must run without the owner's local computer.
- FCR-002: The selected MVP infrastructure must require no recurring monthly payment to start the experiment.
- FCR-003: The application must not automatically upgrade to paid usage.
- FCR-004: The UI and documentation must disclose that free services provide no SLA.
- FCR-005: A dedicated Supabase project must be used; unrelated project databases must not be reused.
- FCR-006: FastAPI must be deployable to Render Free and remain stateless outside PostgreSQL.
- FCR-007: The React/Vite frontend must be deployable to Cloudflare Pages.

## Scheduling Requirements

- FCR-SCH-001: GitHub Actions must execute a one-shot research cycle approximately hourly.
- FCR-SCH-002: Scheduled work must not depend on Render being awake.
- FCR-SCH-003: A database lock or lease must prevent overlapping cycles.
- FCR-SCH-004: Every cycle must have a stable idempotency key.
- FCR-SCH-005: Schedule delays and missed runs must be recorded.
- FCR-SCH-006: The system must never invent or backdate simulated trades for a missed cycle.

## Market Data Requirements

- FCR-MD-001: The free-cloud MVP uses Binance Spot REST and finalized candles.
- FCR-MD-002: Every cycle performs continuity and freshness checks.
- FCR-MD-003: Gaps are repaired through bounded REST backfill.
- FCR-MD-004: Persistent WebSocket ingestion is not required for the first experiment.

## Database and Auth Requirements

- FCR-DB-001: Supabase-managed PostgreSQL is authoritative.
- FCR-DB-002: Supabase Auth provides identity.
- FCR-DB-003: RLS is enabled on all Data API-visible objects.
- FCR-DB-004: Browser writes to financial and control tables are prohibited.
- FCR-DB-005: Only approved read views may be queried directly by the frontend.
- FCR-DB-006: Migrations rebuild a fresh database deterministically.
- FCR-DB-007: Export and restore procedures must be demonstrated before experiment start.

## Observability Requirements

- FCR-OBS-001: Every cycle persists status, duration, error, data freshness, and decision references.
- FCR-OBS-002: The frontend displays last successful cycle, freshness, Gemini status, halt state, and reconciliation state.
- FCR-OBS-003: GitHub Actions, Render, and Supabase logs are operational sources, not the sole audit record.
- FCR-OBS-004: Hosted Prometheus and Grafana are not required for the free-cloud experiment.
- FCR-OBS-005: Integrity failures remain durably visible until reviewed.

## Free-Tier Failure Requirements

- FCR-FAIL-001: Render cold start must not stop scheduled execution.
- FCR-FAIL-002: Supabase unavailability must prevent side effects.
- FCR-FAIL-003: Binance stale/unavailable data must block entries.
- FCR-FAIL-004: Gemini quota or outage must use deterministic fallback or HOLD.
- FCR-FAIL-005: Local or ephemeral filesystem loss must not lose authoritative state.
- FCR-FAIL-006: Reconciliation mismatch must halt the experiment.

## Acceptance Gate

The free-cloud MVP is ready for the 30-day experiment only when:

- public HTTPS frontend and API URLs exist;
- the scheduled CLI completes while the local computer is off;
- migrations and RLS tests pass;
- duplicate cycle execution cannot duplicate a side effect;
- Render cold start is handled;
- export and restore are demonstrated;
- the EUR 0 Gemini cost budget is enforced;
- live/private Binance execution remains disabled.

## Related Documents

- `PRODUCT_REQUIREMENTS.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `../CLOUD_MVP_TASKS.md`
