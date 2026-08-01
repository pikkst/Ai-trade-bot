# M003 Implementation Notes

Status: In progress

This branch implements the local Supabase, migration, Auth mapping, and row-level-security foundation. It is intentionally stacked on M002 until PR #2 is merged.

The implementation must remain local-first, deterministic, deny-by-default, and usable without cloud credentials.
