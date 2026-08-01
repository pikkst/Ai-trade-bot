-- Allow the local PostgreSQL administrator to exercise the trusted role matrix.
-- Application/browser roles remain unable to assume either privileged role.

begin;

grant app_workflow, app_migration to postgres;

commit;
