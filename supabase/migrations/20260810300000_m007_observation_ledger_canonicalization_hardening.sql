-- M007 observation-ledger canonicalization hardening.
-- Forward migration from the 20260810200000 state to the hardened shape:
--  - update canonical request_key function to timezone-independent format;
--  - normalize disposition CHECK to three-value contract;
--  - enforce request_key NOT NULL;
--  - add verified_has_version CHECK;
--  - recompute request_keys with new canonical function.

-- ============================================================================
-- 1. Update canonical request_key function to timezone-independent format.
-- ============================================================================

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
                'retrieved_at', to_char(p_retrieved_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US'),
                'symbol', upper(p_native_symbol)
            )::text,
            'UTF8'
        ),
        'sha256'
    ),
    'hex'
);
$$;

-- Recompute ALL existing request_keys into the new timezone-independent form.
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

-- ============================================================================
-- 2. Normalize disposition CHECK and observation invariants.
-- ============================================================================

-- Drop any existing disposition CHECK (old two-value or new three-value)
-- and recreate the canonical three-value contract.
alter table public.symbol_metadata_observations
    drop constraint if exists symbol_metadata_observations_disposition_check;

alter table public.symbol_metadata_observations
    add constraint symbol_metadata_observations_disposition_check
    check (disposition in ('verified', 'stale_conflict', 'equal_timestamp_conflict'));

-- Verified and equal_timestamp_conflict observations must reference a version;
-- stale_conflict observations may have a NULL resolved version.
alter table public.symbol_metadata_observations
    drop constraint if exists symbol_metadata_observations_verified_has_version_check;

alter table public.symbol_metadata_observations
    add constraint symbol_metadata_observations_verified_has_version_check
    check (
        disposition = 'stale_conflict'
        or symbol_version_id is not null
    );

-- ============================================================================
-- 3. Enforce request_key NOT NULL.
-- ============================================================================

alter table public.symbol_metadata_observations
    alter column request_key set not null;
