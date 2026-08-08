-- M007 evidence idempotency and durable resume evidence.
-- Additive migration:
--  - market_data_ingestions.page_hashes: ordered page-content hashes persisted
--    atomically with each page checkpoint so a restarted run can reproduce the
--    final ingestion content hash from committed evidence.
--  - unique market_snapshots.snapshot_hash: identical canonical snapshot input
--    resolves to the same persisted identity (idempotent replay).

alter table public.market_data_ingestions
    add column if not exists page_hashes text;

comment on column public.market_data_ingestions.page_hashes is
    'Ordered JSON array of deterministic per-page content hashes committed with the checkpoint.';

drop index if exists public.market_snapshots_hash_idx;

create unique index if not exists market_snapshots_hash_uniq
    on public.market_snapshots (snapshot_hash);
