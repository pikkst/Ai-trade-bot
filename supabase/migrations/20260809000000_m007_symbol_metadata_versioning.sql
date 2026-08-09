-- M007 symbol-metadata persistence and versioning.
-- Additive migration:
--  - add max_quantity and max_notional to exchange_symbol_versions so the
--    full provider metadata can be version-controlled;
--  - add metadata_version to track the current effective version per symbol.

alter table public.exchange_symbol_versions
    add column if not exists max_quantity numeric(38, 18) check (max_quantity >= 0);

alter table public.exchange_symbol_versions
    add column if not exists max_notional numeric(38, 18) check (max_notional >= 0);
