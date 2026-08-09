-- M007 symbol-metadata persistence and versioning.
-- Additive migration:
--  - add superseded_by predecessor linkage to exchange_symbol_versions so
--    immutable version history is navigable;
--  - add max_quantity and max_notional so the full provider metadata can be
--    version-controlled;
--  - add raw_metadata_hash and retrieved_at so the authoritative source
--    observation is reproducible.

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
    add column if not exists raw_metadata_hash text
        check (length(raw_metadata_hash) = 64);

alter table public.exchange_symbol_versions
    add column if not exists retrieved_at timestamptz;
