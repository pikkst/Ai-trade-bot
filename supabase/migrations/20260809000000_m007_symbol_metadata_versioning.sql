-- M007 symbol-metadata persistence and versioning.
-- Additive migration:
--  - add superseded_by predecessor linkage to exchange_symbol_versions so
--    immutable version history is navigable;
--  - add max_quantity and max_notional so the full provider metadata can be
--    version-controlled.

alter table public.exchange_symbol_versions
    add column if not exists superseded_by uuid
        references public.exchange_symbol_versions(id) on delete restrict;

create index if not exists exchange_symbol_versions_superseded_by_idx
    on public.exchange_symbol_versions (superseded_by);

alter table public.exchange_symbol_versions
    add column if not exists max_quantity numeric(38, 18) check (max_quantity >= 0);

alter table public.exchange_symbol_versions
    add column if not exists max_notional numeric(38, 18) check (max_notional >= 0);
