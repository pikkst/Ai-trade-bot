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
