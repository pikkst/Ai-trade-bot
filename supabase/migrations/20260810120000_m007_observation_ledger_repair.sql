-- M007 observation-ledger repair and provenance hardening.
-- Forward migration from the 20260809220000 state to the current shape:
--  - add source_evidence_state provenance to exchange_symbol_versions
--  - add request_key (deterministic idempotency), disposition, and nullable
--    symbol_version_id to symbol_metadata_observations
--  - populate deterministic request_key for existing observation rows
--  - enforce observation-to-version identity at the DB boundary.

-- ============================================================================
-- 1. Provenance on exchange_symbol_versions.
-- ============================================================================

-- 1a. Add source_evidence_state if missing.
alter table public.exchange_symbol_versions
    add column if not exists source_evidence_state text not null default 'observed'
        check (source_evidence_state in ('observed', 'legacy_unavailable'));

-- 1b. Detect fabricated legacy evidence injected by the restored
--     20260809000000 migration. That migration copied metadata_hash into
--     raw_metadata_hash and effective_at into retrieved_at for pre-M007 rows
--     that had no genuine source observation. Those fabricated values are not
--     real evidence, so we mark the rows legacy_unavailable. The
--     source_evidence_state flag is the authoritative signal - downstream
--     code must ignore raw_metadata_hash/retrieved_at for legacy rows.
update public.exchange_symbol_versions
set source_evidence_state = 'legacy_unavailable'
where source_evidence_state = 'observed'
  and raw_metadata_hash = metadata_hash
  and retrieved_at = effective_at;

-- Also mark any row that still has no raw evidence after the fabric check.
update public.exchange_symbol_versions
set source_evidence_state = 'legacy_unavailable'
where source_evidence_state = 'observed'
  and raw_metadata_hash is null;

-- 1c. Strong evidence invariants apply only to observed rows.
alter table public.exchange_symbol_versions
    drop constraint if exists exchange_symbol_versions_observed_evidence_check;

alter table public.exchange_symbol_versions
    add constraint exchange_symbol_versions_observed_evidence_check
    check (
        source_evidence_state = 'legacy_unavailable'
        or (raw_metadata_hash is not null and retrieved_at is not null)
    );

-- ============================================================================
-- 2. Extend symbol_metadata_observations.
-- ============================================================================

-- 2a. State-aware request_key column.
alter table public.symbol_metadata_observations
    add column if not exists request_key text;

-- Drop the inline unique constraint from 46ded15 if it exists, so we can
-- recreate it with a known name below.
alter table public.symbol_metadata_observations
    drop constraint if exists symbol_metadata_observations_request_key_key;

-- 2b. State-aware disposition column and CHECK.
--     If the column already exists with the old two-value CHECK, drop that
--     CHECK and add the new three-value CHECK.
alter table public.symbol_metadata_observations
    add column if not exists disposition text not null default 'verified';

alter table public.symbol_metadata_observations
    drop constraint if exists symbol_metadata_observations_disposition_check;

alter table public.symbol_metadata_observations
    add constraint symbol_metadata_observations_disposition_check
    check (disposition in ('verified', 'stale_conflict', 'equal_timestamp_conflict'));

-- 2c. Ensure symbol_version_id is nullable.
alter table public.symbol_metadata_observations
    alter column symbol_version_id drop not null;

-- 2d. Backfill exchange_id for existing observation rows if missing.
update public.symbol_metadata_observations o
set exchange_id = v.exchange_id
from public.exchange_symbol_versions v
where v.id = o.symbol_version_id
  and o.exchange_id is null;

-- 2e. Backfill deterministic request_key for existing observation rows.
--     Use full timestamp precision (microseconds) so distinct observations
--     in the same second do not collide. For actual evidence duplicates
--     (same request, same hash, same retrieved_at to microsecond precision),
--     one row keeps the canonical key and the others receive a deterministic
--     suffix so every row remains unique without deleting audit history.
create or replace function public.jsonb_sort_keys(val jsonb)
returns jsonb
language sql
immutable
as $$
select case
    when val is null then null
    when jsonb_typeof(val) = 'object' then (
        select jsonb_object_agg(key, public.jsonb_sort_keys(value))
        from (
            select key, value
            from jsonb_each(val)
            order by key
        ) sorted
    )
    when jsonb_typeof(val) = 'array' then (
        select jsonb_agg(public.jsonb_sort_keys(elem))
        from jsonb_array_elements(val) as elem
    )
    else val
end;
$$;

create or replace function public.compute_metadata_request_key(
    p_exchange_id uuid,
    p_native_symbol text,
    p_raw_metadata_hash text,
    p_retrieved_at timestamptz,
    p_request_evidence jsonb
) returns text
language sql
immutable
as $$
select encode(
    digest(
        convert_to(
            jsonb_build_object(
                'exchange_id', p_exchange_id::text,
                'raw_metadata_hash', p_raw_metadata_hash,
                'request', public.jsonb_sort_keys(p_request_evidence),
                'retrieved_at', regexp_replace(replace(p_retrieved_at::text, ' ', 'T'), '([+-])(\d{2})(\d{2})$', '\1\2:\3'),
                'symbol', upper(p_native_symbol)
            )::text,
            'UTF8'
        ),
        'sha256'
    ),
    'hex'
);
$$;

with base_keys as (
    select
        o.id,
        public.compute_metadata_request_key(
            o.exchange_id,
            o.native_symbol,
            o.raw_metadata_hash,
            o.retrieved_at,
            o.request_evidence
        ) as canonical_key
    from public.symbol_metadata_observations o
    where o.request_key is null
),
collision_groups as (
    select
        id,
        canonical_key,
        count(*) over (partition by canonical_key) as group_size,
        row_number() over (partition by canonical_key order by id) as rn
    from base_keys
)
update public.symbol_metadata_observations o
set request_key = case
    when cg.group_size = 1 then cg.canonical_key
    when cg.rn = 1 then cg.canonical_key
    else cg.canonical_key || '-' || o.id::text
end
from collision_groups cg
where o.id = cg.id;

-- 2f. Enforce NOT NULL and uniqueness on request_key.
alter table public.symbol_metadata_observations
    alter column request_key set not null;

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.symbol_metadata_observations'::regclass
          and conname = 'symbol_metadata_observations_request_key_key'
    ) then
        alter table public.symbol_metadata_observations
            add constraint symbol_metadata_observations_request_key_key unique (request_key);
    end if;
end;
$$;

-- 2g. Verified and equal_timestamp_conflict observations must reference a version
--     stale_conflict observations may have a NULL resolved version.
alter table public.symbol_metadata_observations
    drop constraint if exists symbol_metadata_observations_verified_has_version_check;

alter table public.symbol_metadata_observations
    add constraint symbol_metadata_observations_verified_has_version_check
    check (
        disposition = 'stale_conflict'
        or symbol_version_id is not null
    );

-- ============================================================================
-- 3. Enforce observation-to-version identity at the DB boundary.
-- ============================================================================

-- equal_timestamp_conflict observations document a deliberate hash mismatch
-- with the linked version, so we exempt only the metadata_hash equality
-- check for that disposition - exchange_id and native_symbol must still match.
create or replace function public.validate_observation_version_identity()
returns trigger as $$
begin
    if NEW.symbol_version_id is not null then
        if not exists (
            select 1
            from public.exchange_symbol_versions v
            where v.id = NEW.symbol_version_id
              and v.exchange_id = NEW.exchange_id
              and v.native_symbol = NEW.native_symbol
        ) then
            raise exception using
                message = 'symbol_metadata_observations references version ' || NEW.symbol_version_id || ' with mismatched identity (exchange_id/native_symbol)';
        end if;
        if NEW.disposition <> 'equal_timestamp_conflict' then
            if not exists (
                select 1
                from public.exchange_symbol_versions v
                where v.id = NEW.symbol_version_id
                  and v.metadata_hash = NEW.metadata_hash
            ) then
                raise exception using
                    message = 'symbol_metadata_observations references version ' || NEW.symbol_version_id || ' with mismatched metadata_hash';
            end if;
        end if;
    end if;
    return NEW;
end;
$$ language plpgsql;

drop trigger if exists symbol_metadata_observations_version_identity_trg on public.symbol_metadata_observations;

create trigger symbol_metadata_observations_version_identity_trg
    before insert or update on public.symbol_metadata_observations
    for each row execute function public.validate_observation_version_identity();
