-- Complete the workflow/service/migration role verification matrix.

begin;

create policy workflow_audit_read on public.audit_events
    for select to app_workflow
    using (true);

grant usage on schema private to service_role;
grant execute on function private.current_app_user_id() to service_role;
grant execute on function private.has_workspace_role(uuid, text[]) to service_role;

commit;
