# M003 Implementation Notes

Status: Implemented; review correction verification in progress

PR #3 implemented the local Supabase, migration, Auth mapping, and row-level-security foundation but was merged into the M002 feature branch after M002 had already reached `main`. The corrective integration branch carries only the M003 delta onto current `main`.

PR #7 review found that an administrator membership intended only for local verification had been placed in the deployable migration chain. The correction removes that migration and uses the Supabase CLI's local-only `supabase/roles.sql` bootstrap instead. Normal `supabase db push` does not include cluster roles; hosted environments must provision named workflow and migration principals separately and must never use `--include-roles` with this local bootstrap.

The request-facing default uses a dedicated `app_runtime` login that can assume only `anon` and `authenticated`. Trusted workflow and migration roles require separate connections. The implementation remains local-first, deterministic, deny-by-default, and usable without cloud credentials; verification is rerun after this correction.
