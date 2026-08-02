-- Local Supabase cluster-role bootstrap for development and CI only.
--
-- The Supabase CLI applies this file to the local stack before migrations.
-- Normal `supabase db push` does not deploy it. Never use `--include-roles`
-- against a hosted, staging, or production project.

do $$
begin
    if not exists (select 1 from pg_roles where rolname = 'app_workflow') then
        create role app_workflow nologin noinherit;
    end if;
    if not exists (select 1 from pg_roles where rolname = 'app_migration') then
        create role app_migration nologin noinherit bypassrls;
    end if;
    if not exists (select 1 from pg_roles where rolname = 'app_runtime') then
        create role app_runtime
            login
            password 'app-runtime-local-only'
            nosuperuser
            nocreatedb
            nocreaterole
            noinherit
            nobypassrls;
    end if;
end
$$;

alter role app_workflow nologin noinherit nobypassrls;
alter role app_migration nologin noinherit bypassrls;
alter role app_runtime
    login
    password 'app-runtime-local-only'
    noinherit;

grant anon, authenticated to app_runtime;
do $$
begin
    if pg_has_role('app_runtime', 'service_role', 'member') then
        revoke service_role from app_runtime;
    end if;
    if pg_has_role('app_runtime', 'app_workflow', 'member') then
        revoke app_workflow from app_runtime;
    end if;
    if pg_has_role('app_runtime', 'app_migration', 'member') then
        revoke app_migration from app_runtime;
    end if;
end
$$;
grant app_workflow, app_migration to postgres;
