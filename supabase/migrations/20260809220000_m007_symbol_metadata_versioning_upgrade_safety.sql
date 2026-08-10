-- M007 symbol-metadata freshness evidence and raw observation persistence.
-- Upgrade-safe for populated deployments:
--  - add last_verified_at so unchanged refreshes advance a dedicated
--    verification timestamp without mutating immutable version evidence;
--  - add an immutable raw-observation ledger so each authoritative source
--    observation (raw hash, retrieval time, provider evidence) is traceable
--    and freshness can be re-derived from observations.

-- 1. Add last_verified_at (nullable) so unchanged refreshes can advance
--    freshness evidence without mutating retrieved_at/effective_at.
alter table public.exchange_symbol_versions
    add column if not exists last_verified_at timestamptz;

-- 2. Seed existing rows so they do not immediately appear stale.
update public.exchange_symbol_versions
set last_verified_at = retrieved_at
where last_verified_at is null;

-- 3. Immutable raw observation ledger. Each refresh persists one bounded
--    observation row (raw hash, retrieval time, provider evidence) linked to
--    the symbol version it verified.
create table if not exists public.symbol_metadata_observations (
    id uuid primary key default extensions.gen_random_uuid(),
    symbol_version_id uuid not null
        references public.exchange_symbol_versions(id) on delete restrict,
    exchange_id uuid not null references public.exchanges(id) on delete restrict,
    native_symbol text not null,
    metadata_hash text not null check (length(metadata_hash) = 64),
    raw_metadata_hash text not null check (length(raw_metadata_hash) = 64),
    retrieved_at timestamptz not null,
    observed_at timestamptz not null default timezone('utc', now()),
    request_evidence jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default timezone('utc', now())
);

create index if not exists symbol_metadata_observations_version_time_idx
    on public.symbol_metadata_observations (symbol_version_id, observed_at);

alter table public.symbol_metadata_observations enable row level security;
alter table public.symbol_metadata_observations force row level security;

create policy workflow_metadata_observations_all on public.symbol_metadata_observations
    for all to app_workflow using (true) with check (true);

revoke all on public.symbol_metadata_observations from public, anon, authenticated;

grant select on public.symbol_metadata_observations to authenticated;
grant select, insert on public.symbol_metadata_observations to app_workflow;
grant all privileges on public.symbol_metadata_observations to app_migration;
grant all privileges on public.symbol_metadata_observations to service_role;
