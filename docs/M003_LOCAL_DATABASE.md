# M003 Local Supabase, Auth, Migrations, and RLS

Last reviewed: 2026-08-01  
Status: Implementation and verification in progress

## Purpose

M003 provides a reproducible local PostgreSQL and Supabase Auth environment that mirrors the intended cloud authorization boundary without linking a cloud project or supplying cloud credentials.

Supabase SQL migrations are the executable schema and security source of truth. Alembic records an application compatibility head only after verifying that the expected Supabase relations, approved views, forced RLS settings, and workflow policies exist.

## Local endpoints

| Service | Local endpoint |
| --- | --- |
| Supabase API/Auth | `http://127.0.0.1:54321` |
| PostgreSQL | `127.0.0.1:54322` |
| Supabase Studio | `http://127.0.0.1:54323` |
| Inbucket | `http://127.0.0.1:54324` |

The default local SQLAlchemy URL is:

```text
postgresql+psycopg://postgres:postgres@127.0.0.1:54322/postgres
```

This value is local development infrastructure, not a production credential.

## Commands

Unix-like shells:

```bash
make local-up
make local-migrate
make local-reset
make local-seed
make alembic-upgrade
make database-test
make local-down
```

Windows PowerShell:

```powershell
.\tasks.ps1 local-up
.\tasks.ps1 local-migrate
.\tasks.ps1 local-reset
.\tasks.ps1 local-seed
.\tasks.ps1 alembic-upgrade
.\tasks.ps1 database-test
.\tasks.ps1 local-down
```

`local-reset` is destructive for the local database. It recreates the database, applies every Supabase migration, and applies the committed deterministic seed. `local-seed` deliberately performs the same clean reset so repeated seed verification cannot retain stale rows.

## Migration chain

Supabase migrations:

1. `20260801144500_m003_foundation.sql` — identity, workspace, membership, configuration, audit, market-data, and virtual-portfolio relations; private authorization helpers; forced RLS; initial policies and read views.
2. `20260801150000_m003_data_api_grants.sql` — RLS-backed browser reads, approved views, service/workflow grants, and explicit browser-write denial.
3. `20260801151000_m003_workflow_rls.sql` — workflow audit-read policy and service helper grants.
4. `20260801170000_m003_local_admin_role_membership.sql` — permits only the local PostgreSQL administrator to assume the trusted workflow and migration roles for verification.

Alembic compatibility head:

```text
20260801170000
```

Alembic stores its version table in the non-Data-API `private` schema. Alembic revisions do not re-run the Supabase DDL. They fail closed when the expected Supabase schema or security configuration is missing.

Applied Supabase SQL migrations are immutable. Corrections must be additive forward migrations.

## Foundational relations

The initial M003 schema contains:

- `users` — application identity mapped one-to-one to `auth.users.id` through `auth_subject`;
- `workspaces` — tenant and isolation boundary;
- `workspace_memberships` — active owner/operator/viewer grants;
- `workspace_config_versions` — versioned immutable-style workspace configuration records;
- `audit_events` — append-only safe audit evidence;
- `exchanges` and `exchange_symbol_versions` — versioned market metadata;
- `candles` — finalized deterministic market-data rows;
- `virtual_portfolios` — paper-only financial state.

All Data API-visible base tables have both RLS enabled and RLS forced.

## Auth and roles

Seeded local identities:

| Email | Workspace role |
| --- | --- |
| `owner@local.test` | owner |
| `operator@local.test` | operator |
| `viewer@local.test` | viewer |

Local-only password for all three identities:

```text
local-password-only
```

The application maps the Supabase Auth subject to `public.users.auth_subject`, then resolves an active, unexpired workspace membership. Unknown, disabled, revoked, expired, or cross-workspace subjects fail closed.

Database execution roles covered by the verification matrix:

- `anon` — no approved application-data read;
- `authenticated` viewer — workspace/config/market/portfolio reads, own profile and own membership, no audit read;
- `authenticated` operator — viewer reads plus workspace audit read;
- `authenticated` owner — operator reads plus all memberships in the workspace;
- `app_workflow` — policy-controlled service workflow access;
- `service_role` — trusted Supabase backend role;
- `app_migration` — local migration/verification role with RLS bypass.

The trusted application roles remain `NOLOGIN` and `NOINHERIT`. Only `app_migration` has `BYPASSRLS`, and only the local `postgres` administrator is granted membership in `app_workflow` and `app_migration`; browser and Data API roles cannot assume either role.

## Browser-write boundary

`anon` and `authenticated` receive no insert, update, delete, truncate, references, or trigger privileges on the foundational tables. This includes financial state, configuration, access control, audit evidence, market data, and identity mapping.

Owners and operators do not receive direct browser table writes. Approved changes must pass through server-side commands or trusted workflows that validate authorization, invariants, audit evidence, and transaction boundaries.

## Approved read-only views

- `current_user_profile`
- `workspace_overview`
- `current_workspace_memberships`
- `active_workspace_configuration`
- `workspace_audit_read`
- `market_candle_read`
- `portfolio_summary`

Views use `security_invoker = true`, so underlying table RLS remains authoritative. `active_workspace_configuration` exposes the version and hash but not raw configuration JSON.

## Deterministic seed

The seed uses stable UUIDs and fixed UTC timestamps. It creates:

- three local Auth identities and application users;
- one workspace with owner/operator/viewer memberships;
- one active configuration version with fake AI and live trading disabled;
- Binance/BTCEUR metadata;
- two finalized synthetic one-hour candles;
- one EUR 10,000 paper portfolio;
- one migration audit event.

The seed contains no production identifier, cloud project reference, private exchange key, Gemini key, or live-trading capability.

## SQLAlchemy transaction model

`backend/app/database.py` provides:

- a SQLAlchemy 2 engine and explicit session factory;
- one commit or rollback boundary per `transactional_session`;
- a FastAPI session dependency;
- transaction-local database role and JWT-claim context;
- a closed allowlist of permitted database roles.

Raised exceptions roll back the transaction and always close the session. Role context disappears when the transaction finishes.

## Verification

The local database CI job performs:

1. install the pinned Supabase CLI and locked Python dependencies;
2. start the local Supabase stack;
3. reset from an empty database and apply all migrations and seed data;
4. verify the Alembic compatibility head;
5. run migration-count and deterministic-seed assertions;
6. run anonymous/viewer/operator/owner/workflow/service/migration RLS checks;
7. prove browser financial writes are denied;
8. prove workspace isolation;
9. prove transaction commit and rollback behavior;
10. stop the local stack without retaining a backup.

Normal M003 verification requires no cloud credential and does not contact paid AI or private exchange APIs.

## Security limitations and follow-up

M003 is the authorization and persistence foundation. Later Master Tasks must add domain-specific tables and additive policies without weakening the browser-write boundary. Production credential lifecycle, MFA/recovery policy, application command endpoints, complete audit coverage, and deployment provisioning remain mapped to their later tasks.
