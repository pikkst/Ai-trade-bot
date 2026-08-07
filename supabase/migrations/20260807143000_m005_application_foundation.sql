-- M005 typed application foundation: durable idempotency records.
-- Browser roles have no direct access; application/workflow services own writes.

create table if not exists public.idempotency_records (
    id uuid primary key default extensions.gen_random_uuid(),
    workspace_id uuid not null references public.workspaces(id) on delete cascade,
    scope text not null check (length(scope) between 1 and 100),
    idempotency_key text not null check (length(idempotency_key) between 1 and 200),
    request_hash text not null check (length(request_hash) = 64),
    response_status integer check (response_status between 100 and 599),
    response_body jsonb,
    created_at timestamptz not null default timezone('utc', now()),
    completed_at timestamptz,
    unique (workspace_id, scope, idempotency_key),
    constraint idempotency_completion_consistency check (
        (completed_at is null and response_status is null and response_body is null)
        or
        (completed_at is not null and response_status is not null and response_body is not null)
    )
);

create index if not exists idempotency_records_workspace_created_idx
    on public.idempotency_records (workspace_id, created_at desc);

alter table public.idempotency_records enable row level security;
alter table public.idempotency_records force row level security;

create policy workflow_idempotency_all on public.idempotency_records
    for all to app_workflow using (true) with check (true);

revoke all on public.idempotency_records from public, anon, authenticated;
grant select, insert, update on public.idempotency_records to app_workflow;
grant all privileges on public.idempotency_records to app_migration;

comment on table public.idempotency_records is
    'M005 durable command idempotency evidence. Browser roles have no access.';
