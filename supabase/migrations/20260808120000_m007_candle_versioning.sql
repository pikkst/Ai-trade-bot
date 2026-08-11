-- M007 candle versioning for immutable corrections.
-- Additive migration: allows original + replacement candles to coexist at the
-- same (symbol_version_id, interval_code, open_time) while guaranteeing exactly
-- one active (non-superseded) finalized candle per open time.

alter table public.candles
    drop constraint if exists candles_symbol_version_id_interval_code_open_time_key;

alter table public.candles
    add column if not exists superseded_by uuid references public.candles(id) on delete restrict;

comment on column public.candles.superseded_by is
    'Set to the replacement candle id when this candle has been corrected; the original row remains immutable evidence.';

create unique index if not exists candles_active_open_time_idx
    on public.candles (symbol_version_id, interval_code, open_time)
    where superseded_by is null;
