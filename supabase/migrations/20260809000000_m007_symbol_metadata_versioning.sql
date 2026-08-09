-- M007 symbol-metadata persistence and versioning.
-- Upgrade-safe for populated pre-M007 deployments:
--  - stage nullable columns first;
--  - deterministically backfill source evidence and reconstruct the
--    immediate-successor supersession chain (lead window) without deleting
--    history;
--  - then enforce NOT NULL and exactly-one-current.

-- Stage nullable columns first so populated M003 rows never fail.
alter table public.exchange_symbol_versions
    add column if not exists superseded_by uuid
        references public.exchange_symbol_versions(id) on delete restrict;

create index if not exists exchange_symbol_versions_superseded_by_idx
    on public.exchange_symbol_versions (superseded_by);

alter table public.exchange_symbol_versions
    add column if not exists max_quantity numeric(38, 18) check (max_quantity >= 0);

alter table public.exchange_symbol_versions
    add column if not exists max_notional numeric(38, 18) check (max_notional >= 0);

alter table public.exchange_symbol_versions
    add column if not exists raw_metadata_hash text check (length(raw_metadata_hash) = 64);

alter table public.exchange_symbol_versions
    add column if not exists retrieved_at timestamptz;

-- Deterministically backfill source evidence for pre-M007 rows.
update public.exchange_symbol_versions
set raw_metadata_hash = metadata_hash
where raw_metadata_hash is null;

update public.exchange_symbol_versions
set retrieved_at = effective_at
where retrieved_at is null;

-- Reconstruct the immediate-successor supersession chain per exchange+symbol
-- so V1 -> V2 -> V3 -> NULL and effective intervals remain recoverable.
with chained as (
    select id,
           lead(id) over (
               partition by exchange_id, native_symbol
               order by effective_at, id
           ) as next_id
    from public.exchange_symbol_versions
    where superseded_by is null
)
update public.exchange_symbol_versions sv
set superseded_by = chained.next_id
from chained
where sv.id = chained.id
  and chained.next_id is not null;

-- Enforce NOT NULL now that every row has deterministic source evidence.
alter table public.exchange_symbol_versions
    alter column raw_metadata_hash set not null;

alter table public.exchange_symbol_versions
    alter column retrieved_at set not null;

-- Enforce exactly one current version per exchange+symbol pair.
create unique index if not exists exchange_symbol_versions_current_idx
    on public.exchange_symbol_versions (exchange_id, native_symbol)
    where superseded_by is null;
