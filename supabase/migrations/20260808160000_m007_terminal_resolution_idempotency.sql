-- M007 append-only terminal-resolution idempotency (eighth-pass review).
-- Additive migration:
--  - add supersedes_event_id so terminal events carry a structured parent
--    identity instead of relying only on JSON details;
--  - add a unique partial index (supersedes_event_id, event_type) so the same
--    blocker cannot be superseded twice by the same terminal type, even across
--    concurrent sessions.

alter table public.data_quality_events
    add column if not exists supersedes_event_id uuid
    references public.data_quality_events(id) on delete restrict;

create unique index if not exists data_quality_events_terminal_unique
    on public.data_quality_events (supersedes_event_id, event_type)
    where supersedes_event_id is not null;
