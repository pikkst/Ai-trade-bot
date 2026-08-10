-- M007 observation-ledger repair and provenance hardening.
-- Forward migration from the 20260809220000 state to the current shape:
--  - add source_evidence_state provenance to exchange_symbol_versions;
--  - add request_key (deterministic idempotency), disposition, and nullable
--    symbol_version_id to symbol_metadata_observations;
--  - populate deterministic request_key for existing observation rows;
--  - enforce observation-to-version identity at the DB boundary.

-- 1. Provenance on exchange_symbol_versions.
alter table public.exchange_symbol_versions
    add column if not exists source_evidence_state text not null default 'observed'
        check (source_evidence_state in ('observed', 'legacy_unavailable'));

-- Defensive: mark any row without raw evidence as legacy_unavailable.
update public.exchange_symbol_versions
set source_evidence_state = 'legacy_unavailable'
where raw_metadata_hash is null;

-- Strong evidence invariants apply only to observed rows.
alter table public.exchange_symbol_versions
    drop constraint if exists exchange_symbol_versions_observed_evidence_check;

alter table public.exchange_symbol_versions
    add constraint exchange_symbol_versions_observed_evidence_check
    check (
        source_evidence_state = 'legacy_unavailable'
        or (raw_metadata_hash is not null and retrieved_at is not null)
    );

-- 2. Extend symbol_metadata_observations.
alter table public.symbol_metadata_observations
    add column if not exists request_key text;

alter table public.symbol_metadata_observations
    add column if not exists disposition text not null default 'verified'
        check (disposition in ('verified', 'stale_conflict', 'equal_timestamp_conflict'));

-- Make symbol_version_id nullable so stale/conflict observations can be
-- stored without a resolved version.
alter table public.symbol_metadata_observations
    alter column symbol_version_id drop not null;

-- Backfill exchange_id for existing observation rows if missing.
update public.symbol_metadata_observations o
set exchange_id = v.exchange_id
from public.exchange_symbol_versions v
where v.id = o.symbol_version_id
  and o.exchange_id is null;

-- Backfill deterministic request_key for existing observation rows.
update public.symbol_metadata_observations
set request_key = encode(
    digest(
        convert_to(
            coalesce(request_evidence::text, '{}') || '|' || coalesce(native_symbol, '') || '|' || coalesce(raw_metadata_hash, '') || '|' || coalesce(to_char(retrieved_at, 'YYYY-MM-DDTHH24:MI:SSZ'), ''),
        'UTF8'
    ),
    'sha256'
),
'hex'
)
where request_key is null;

-- Enforce NOT NULL and uniqueness on request_key.
alter table public.symbol_metadata_observations
    alter column request_key set not null;

alter table public.symbol_metadata_observations
    add constraint symbol_metadata_observations_request_key_key unique (request_key);

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

-- 3. Enforce observation-to-version identity at the DB boundary.
-- equal_timestamp_conflict observations document a hash mismatch with the
-- linked version, so they are exempt from the hash-match check.
create or replace function public.validate_observation_version_identity()
returns trigger as $$
begin
    if NEW.symbol_version_id is not null then
        if NEW.disposition = 'equal_timestamp_conflict' then
            return NEW;
        end if;
        if not exists (
            select 1
            from public.exchange_symbol_versions v
            where v.id = NEW.symbol_version_id
              and v.exchange_id = NEW.exchange_id
              and v.native_symbol = NEW.native_symbol
              and v.metadata_hash = NEW.metadata_hash
        ) then
            raise exception using
                message = 'symbol_metadata_observations references version ' || NEW.symbol_version_id || ' with mismatched identity (exchange_id/native_symbol/metadata_hash)';
        end if;
    end if;
    return NEW;
end;
$$ language plpgsql;

drop trigger if exists symbol_metadata_observations_version_identity_trg on public.symbol_metadata_observations;

create trigger symbol_metadata_observations_version_identity_trg
    before insert or update on public.symbol_metadata_observations
    for each row execute function public.validate_observation_version_identity();
