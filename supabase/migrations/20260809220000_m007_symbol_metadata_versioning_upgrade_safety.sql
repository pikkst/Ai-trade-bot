-- M007 symbol-metadata versioning upgrade safety.
-- Stage raw_metadata_hash to nullable, backfill, add last_verified_at,
-- resolve pre-existing multiple effective rows, then enforce NOT NULL
-- and exactly-one-current for populated pre-M007 deployments.

-- 1. Allow backfill of raw_metadata_hash for pre-M007 rows.
alter table public.exchange_symbol_versions
    alter column raw_metadata_hash drop not null;

-- 2. Deterministically backfill raw_metadata_hash for existing rows.
-- Pre-M007 rows lack raw exchangeInfo evidence; fall back to the stored
-- normalized metadata_hash so the column is non-null and auditable.
update public.exchange_symbol_versions
set raw_metadata_hash = metadata_hash
where raw_metadata_hash is null;

-- 3. Add last_verified_at to track freshness of unchanged refreshes.
alter table public.exchange_symbol_versions
    add column if not exists last_verified_at timestamptz;

-- 4. Seed last_verified_at from retrieved_at for existing rows so they
-- do not immediately appear stale.
update public.exchange_symbol_versions
set last_verified_at = retrieved_at
where last_verified_at is null;

-- 5. Resolve pre-existing multiple effective rows per (exchange_id, native_symbol).
-- Mark all but the latest effective_at row as superseded so the later
-- exactly-one-current partial unique index can be enforced.
with ranked as (
    select id, exchange_id, native_symbol,
           row_number() over (
               partition by exchange_id, native_symbol
               order by effective_at desc
           ) as rn
    from public.exchange_symbol_versions
    where superseded_by is null
)
update public.exchange_symbol_versions sv
set superseded_by = (
    select id from ranked r
    where r.exchange_id = sv.exchange_id
      and r.native_symbol = sv.native_symbol
      and r.rn = 1
)
from ranked r2
where sv.id = r2.id
  and r2.rn > 1;

-- 6. Enforce NOT NULL now that every row has raw source evidence.
alter table public.exchange_symbol_versions
    alter column raw_metadata_hash set not null;

-- 7. Enforce exactly one current version per exchange+symbol pair.
create unique index if not exists exchange_symbol_versions_current_idx
    on public.exchange_symbol_versions (exchange_id, native_symbol)
    where superseded_by is null;
