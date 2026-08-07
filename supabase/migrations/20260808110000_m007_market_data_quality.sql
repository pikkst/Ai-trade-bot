-- M007 Binance REST market-data ingestion and quality controls.
-- Additive migration for new market-data quality, correction, snapshot, and ingestion tables.

create table if not exists public.market_data_ingestions (
    id uuid primary key default extensions.gen_random_uuid(),
    exchange_id uuid not null references public.exchanges(id) on delete restrict,
    symbol_version_id uuid not null references public.exchange_symbol_versions(id) on delete restrict,
    ingestion_type text not null check (ingestion_type in ('backfill', 'incremental', 'gap_repair')),
    interval_code text not null,
    requested_start_time timestamptz not null,
    requested_end_time timestamptz not null,
    actual_start_time timestamptz,
    actual_end_time timestamptz,
    status text not null default 'pending' check (status in ('pending', 'running', 'completed', 'failed', 'cancelled')),
    inserted_count bigint not null default 0 check (inserted_count >= 0),
    duplicate_count bigint not null default 0 check (duplicate_count >= 0),
    invalid_count bigint not null default 0 check (invalid_count >= 0),
    corrected_count bigint not null default 0 check (corrected_count >= 0),
    gap_count bigint not null default 0 check (gap_count >= 0),
    retry_count integer not null default 0 check (retry_count >= 0),
    request_count integer not null default 0 check (request_count >= 0),
    provider_latency_ms integer,
    safe_error text,
    checkpoint timestamptz,
    idempotency_key text not null check (length(idempotency_key) between 1 and 200),
    content_hash text not null check (length(content_hash) = 64),
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),
    completed_at timestamptz,
    unique (exchange_id, symbol_version_id, interval_code, requested_start_time, requested_end_time, ingestion_type),
    unique (idempotency_key)
);

create table if not exists public.data_quality_events (
    id uuid primary key default extensions.gen_random_uuid(),
    exchange_id uuid not null references public.exchanges(id) on delete restrict,
    symbol_version_id uuid not null references public.exchange_symbol_versions(id) on delete restrict,
    interval_code text not null,
    event_type text not null check (event_type in (
        'invalid_value',
        'invalid_interval',
        'out_of_order',
        'duplicate_consistent',
        'duplicate_conflict',
        'gap_detected',
        'gap_repair_pending',
        'gap_repaired',
        'gap_unresolved',
        'stale_data',
        'clock_drift_exceeded',
        'correction_pending',
        'correction_applied',
        'quarantined',
        'invalidated',
        'approved',
        'incomplete'
    )),
    severity text not null default 'warning' check (severity in ('info', 'warning', 'error', 'critical')),
    affected_candle_id uuid references public.candles(id) on delete restrict,
    affected_range_start timestamptz,
    affected_range_end timestamptz,
    detection_policy_version text not null,
    details jsonb not null default '{}'::jsonb,
    resolution text,
    replacement_candle_id uuid references public.candles(id) on delete restrict,
    invalidated_candle_id uuid references public.candles(id) on delete restrict,
    ingestion_id uuid references public.market_data_ingestions(id) on delete set null,
    snapshot_id uuid,
    reviewer_user_id uuid references public.users(id) on delete set null,
    detected_at timestamptz not null default timezone('utc', now()),
    resolved_at timestamptz,
    created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.candle_corrections (
    id uuid primary key default extensions.gen_random_uuid(),
    exchange_id uuid not null references public.exchanges(id) on delete restrict,
    symbol_version_id uuid not null references public.exchange_symbol_versions(id) on delete restrict,
    interval_code text not null,
    open_time timestamptz not null,
    original_candle_id uuid not null references public.candles(id) on delete restrict,
    replacement_candle_id uuid not null references public.candles(id) on delete restrict,
    reason text not null,
    source_evidence jsonb not null default '{}'::jsonb,
    effective_at timestamptz not null default timezone('utc', now()),
    created_at timestamptz not null default timezone('utc', now()),
    unique (original_candle_id)
);

create table if not exists public.market_snapshots (
    id uuid primary key default extensions.gen_random_uuid(),
    workspace_id uuid not null references public.workspaces(id) on delete restrict,
    exchange_id uuid not null references public.exchanges(id) on delete restrict,
    symbol_version_id uuid not null references public.exchange_symbol_versions(id) on delete restrict,
    interval_code text not null,
    analysis_time timestamptz not null,
    first_event_time timestamptz not null,
    last_event_time timestamptz not null,
    candle_count bigint not null check (candle_count >= 0),
    quality_outcome text not null check (quality_outcome in ('approved', 'incomplete', 'stale', 'invalidated')),
    quality_policy_version text not null,
    freshness_outcome text not null check (freshness_outcome in ('fresh', 'stale', 'clock_drift_exceeded')),
    freshness_policy_version text not null,
    data_source text not null,
    ingestion_id uuid references public.market_data_ingestions(id) on delete set null,
    snapshot_hash text not null check (length(snapshot_hash) = 64),
    snapshot_schema_version text not null,
    state text not null default 'active' check (state in ('active', 'superseded', 'invalidated')),
    invalidation_reason text,
    predecessor_snapshot_id uuid references public.market_snapshots(id) on delete set null,
    creator_cycle_id text,
    creator_job_id text,
    created_at timestamptz not null default timezone('utc', now()),
    constraint snapshots_time_order check (last_event_time >= first_event_time)
);

create table if not exists public.market_snapshot_candles (
    id uuid primary key default extensions.gen_random_uuid(),
    snapshot_id uuid not null references public.market_snapshots(id) on delete cascade,
    candle_id uuid not null references public.candles(id) on delete restrict,
    sequence bigint not null,
    unique (snapshot_id, sequence),
    unique (snapshot_id, candle_id)
);

create index if not exists market_data_ingestions_exchange_symbol_idx
    on public.market_data_ingestions (exchange_id, symbol_version_id, interval_code, requested_start_time);
create index if not exists market_data_ingestions_status_idx
    on public.market_data_ingestions (status, created_at desc);
create index if not exists data_quality_events_symbol_time_idx
    on public.data_quality_events (symbol_version_id, interval_code, detected_at desc);
create index if not exists data_quality_events_ingestion_idx
    on public.data_quality_events (ingestion_id);
create index if not exists candle_corrections_open_time_idx
    on public.candle_corrections (symbol_version_id, interval_code, open_time);
create index if not exists market_snapshots_workspace_analysis_idx
    on public.market_snapshots (workspace_id, analysis_time desc);
create index if not exists market_snapshots_hash_idx
    on public.market_snapshots (snapshot_hash);
create index if not exists market_snapshot_candles_snapshot_seq_idx
    on public.market_snapshot_candles (snapshot_id, sequence);

alter table public.market_data_ingestions enable row level security;
alter table public.market_data_ingestions force row level security;
alter table public.data_quality_events enable row level security;
alter table public.data_quality_events force row level security;
alter table public.candle_corrections enable row level security;
alter table public.candle_corrections force row level security;
alter table public.market_snapshots enable row level security;
alter table public.market_snapshots force row level security;
alter table public.market_snapshot_candles enable row level security;
alter table public.market_snapshot_candles force row level security;

create policy workflow_ingestions_all on public.market_data_ingestions
    for all to app_workflow using (true) with check (true);
create policy workflow_quality_all on public.data_quality_events
    for all to app_workflow using (true) with check (true);
create policy workflow_corrections_all on public.candle_corrections
    for all to app_workflow using (true) with check (true);
create policy workflow_snapshots_all on public.market_snapshots
    for all to app_workflow using (true) with check (true);
create policy workflow_snapshot_candles_all on public.market_snapshot_candles
    for all to app_workflow using (true) with check (true);

revoke all on public.market_data_ingestions from public, anon, authenticated;
revoke all on public.data_quality_events from public, anon, authenticated;
revoke all on public.candle_corrections from public, anon, authenticated;
revoke all on public.market_snapshots from public, anon, authenticated;
revoke all on public.market_snapshot_candles from public, anon, authenticated;

grant usage on schema public to app_workflow, app_migration;
grant select, insert, update on public.market_data_ingestions to app_workflow;
grant select, insert on public.data_quality_events to app_workflow;
grant select, insert on public.candle_corrections to app_workflow;
grant select, insert, update on public.market_snapshots to app_workflow;
grant select, insert on public.market_snapshot_candles to app_workflow;
grant all privileges on all tables in schema public to app_migration;
grant all privileges on all sequences in schema public to app_migration;

create or replace view public.market_snapshot_read
with (security_invoker = true)
as
select snapshot.id,
       exchange.code as exchange_code,
       symbol.native_symbol,
       symbol.base_asset,
       symbol.quote_asset,
       snapshot.interval_code,
       snapshot.analysis_time,
       snapshot.first_event_time,
       snapshot.last_event_time,
       snapshot.candle_count,
       snapshot.quality_outcome,
       snapshot.quality_policy_version,
       snapshot.freshness_outcome,
       snapshot.freshness_policy_version,
       snapshot.data_source,
       snapshot.snapshot_hash,
       snapshot.snapshot_schema_version,
       snapshot.state,
       snapshot.invalidation_reason,
       snapshot.created_at
from public.market_snapshots snapshot
join public.exchange_symbol_versions symbol on symbol.id = snapshot.symbol_version_id
join public.exchanges exchange on exchange.id = snapshot.exchange_id
where snapshot.state = 'active'
  and snapshot.quality_outcome = 'approved'
  and snapshot.freshness_outcome = 'fresh';

create or replace view public.data_quality_event_read
with (security_invoker = true)
as
select event.id,
       exchange.code as exchange_code,
       symbol.native_symbol,
       symbol.base_asset,
       symbol.quote_asset,
       event.interval_code,
       event.event_type,
       event.severity,
       event.details,
       event.resolution,
       event.detected_at,
       event.resolved_at
from public.data_quality_events event
join public.exchange_symbol_versions symbol on symbol.id = event.symbol_version_id
join public.exchanges exchange on exchange.id = event.exchange_id;

grant select on public.market_snapshot_read to authenticated;
grant select on public.data_quality_event_read to authenticated;

comment on table public.market_data_ingestions is 'M007 bounded checkpointed REST ingestion evidence.';
comment on table public.data_quality_events is 'M007 append-only quality/correction events.';
comment on table public.candle_corrections is 'M007 immutable original/replacement candle evidence.';
comment on table public.market_snapshots is 'M007 immutable market snapshot metadata.';
comment on table public.market_snapshot_candles is 'M007 ordered snapshot candle membership.';
