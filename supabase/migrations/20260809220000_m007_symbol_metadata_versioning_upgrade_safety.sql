-- M007 symbol-metadata freshness evidence and raw observation persistence.
-- Upgrade-safe for populated deployments
--  - add last_verified_at so unchanged refreshes advance a dedicated
--    verification timestamp without mutating immutable version evidence
--  - add an immutable raw-observation ledger with a deterministic request
--    identity (idempotency), a verification disposition, and bounded
--    request/provider-version evidence so each observation is traceable to
--    the exact source request that produced it

-- 1. Add last_verified_at (nullable) so unchanged refreshes can advance
--    freshness evidence without mutating retrieved_at/effective_at.
alter table public.exchange_symbol_versions
    add column if not exists last_verified_at timestamptz;

-- 2. Seed existing rows from retrieval time only when observed evidence
--    exists (legacy_unavailable rows remain NULL and therefore stale)
update public.exchange_symbol_versions
set last_verified_at = retrieved_at
where last_verified_at is null
  and retrieved_at is not null;

-- 3. Immutable raw observation ledger. Each observation carries a
--    deterministic request_key (logical request/attempt identity + source
--    hash + retrieval identity) so exact replay or duplicate delivery is a
--    no-op, a disposition ('verified' | 'stale_conflict'), a nullable
--    resolved symbol version, and bounded canonical request evidence.
create table if not exists public.symbol_metadata_observations (
    id uuid primary key default extensions.gen_random_uuid(),
    request_key text not null unique,
    symbol_version_id uuid
        references public.exchange_symbol_versions(id) on delete restrict,
    exchange_id uuid not null references public.exchanges(id) on delete restrict,
    native_symbol text not null,
    disposition text not null default 'verified'
        check (disposition in ('verified', 'stale_conflict')),
    metadata_hash text not null check (length(metadata_hash) = 64),
    raw_metadata_hash text not null check (length(raw_metadata_hash) = 64),
    retrieved_at timestamptz not null,
    observed_at timestamptz not null default timezone('utc', now()),
    request_evidence jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default timezone('utc', now()),
    constraint symbol_metadata_observations_verified_version_check
        check (
            disposition = 'stale_conflict'
            or symbol_version_id is not null
        )
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
