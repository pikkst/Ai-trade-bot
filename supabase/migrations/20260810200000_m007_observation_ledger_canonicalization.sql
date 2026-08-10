-- M007 observation-ledger repair and provenance hardening.
-- Forward migration from the 20260810120000 state to the current shape:
--  - canonicalize existing request_keys to the DB function algorithm;
--  - neutralize synthetic freshness evidence for legacy_unavailable rows;
--  - enforce observation-to-version identity at the DB boundary.

-- ============================================================================
-- 1. Canonicalize existing request_keys.
-- ============================================================================

-- Recursive JSON key sorter for canonical request evidence serialization.
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

-- Canonical request key computation. This is the single source of truth
-- for both migration backfill and runtime inserts.
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

-- Recompute ALL existing request_keys into the canonical form. Rows that
-- already have the canonical key keep it, rows with the legacy Python key
-- get the new canonical key. For actual evidence collisions (same request,
-- same hash, same retrieved_at to microsecond precision), one row keeps the
-- canonical key and the others receive a deterministic suffix so every row
-- remains unique without deleting audit history
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

-- State-aware request_key UNIQUE constraint.
alter table public.symbol_metadata_observations
    drop constraint if exists symbol_metadata_observations_request_key_key;

alter table public.symbol_metadata_observations
    add constraint symbol_metadata_observations_request_key_key unique (request_key);

-- ============================================================================
-- 2. Neutralize synthetic freshness evidence for legacy rows.
-- ============================================================================

-- Detect fabricated legacy evidence injected by the restored
-- 20260809000000 migration. That migration copied metadata_hash into
-- raw_metadata_hash and effective_at into retrieved_at for pre-M007 rows
-- that had no genuine source observation. Those fabricated values are not
-- real evidence, so we mark the rows legacy_unavailable.
update public.exchange_symbol_versions
set source_evidence_state = 'legacy_unavailable'
where source_evidence_state = 'observed'
  and raw_metadata_hash = metadata_hash
  and retrieved_at = effective_at;

-- Also mark any row that still has no raw evidence.
update public.exchange_symbol_versions
set source_evidence_state = 'legacy_unavailable'
where source_evidence_state = 'observed'
  and raw_metadata_hash is null;

-- The restored 20260809000000 migration fabricated raw_metadata_hash and
-- retrieved_at for pre-M007 rows, 092200 then seeded last_verified_at from
-- those synthetic timestamps. Flipping source_evidence_state alone is not
-- enough - the runtime freshness gate uses last_verified_at or retrieved_at
-- for the 24h TTL. Clear the synthetic verification timestamp so legacy
-- rows cannot masquerade as recently observed.
update public.exchange_symbol_versions
set last_verified_at = null
where source_evidence_state = 'legacy_unavailable'
  and last_verified_at = retrieved_at;

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
