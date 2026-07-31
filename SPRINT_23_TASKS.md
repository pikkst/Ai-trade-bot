# Sprint 23 Tasks — Product, Security, API, and Database Contract Synchronization

Last reviewed: 2026-08-01  
Status: Documentation synchronization in progress

## Sprint Goal

Synchronize product requirements, security controls, API contracts, database schema, retention, and Master Task ownership so implementation from M003 through M036 uses one Supabase Auth/RLS model, one command-gate model, one append-only evidence model, and one paper-only product boundary.

## Authoritative References

- `TASKS.md`
- `docs/IMPLEMENTATION_EXECUTION_PLAN.md`
- `docs/TASK_CATALOG_INDEX.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/SECURITY.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/ARCHITECTURE.md`
- `docs/BACKEND.md`
- `docs/GEMINI_INTEGRATION.md`
- `docs/OBSERVABILITY.md`
- `docs/TESTING.md`
- `.env.example`

## S23.1 Synchronize Product Requirements

### Work

- map functional and non-functional requirement groups to Master Tasks;
- clarify Supabase Auth, RLS, immutable behavior sets, cycle completeness, incidents, data governance, research review, and change management;
- distinguish MVP, production-research, deferred architecture, and future exchange assessments;
- align success metrics and the controlled experiment with evidence rather than profit.

### Acceptance Criteria

- every material requirement has a stable ID and Master Task owner;
- production research remains paper-only;
- process uptime cannot substitute for financial completeness;
- no deferred infrastructure or live path becomes a product requirement.

## S23.2 Synchronize Security Contract

### Work

- map security controls and release gates to M003, M005, M009–M012, M014, M023, M027–M036;
- align Supabase Auth, application authorization, recent authentication, RLS, service/workflow/migration roles, secrets, supply chain, AI, financial integrity, incident response, recovery, and change governance;
- remove custom password/JWT assumptions from the active profile;
- define no-auto-spend and no-live-execution startup/release assertions.

### Acceptance Criteria

- Auth/RLS boundaries match architecture/backend/env inventory;
- security failures fail closed and create durable evidence;
- no secret-bearing field or provider tool is authorized;
- critical findings and unsafe flags block experiment/release.

## S23.3 Synchronize API Contract

### Work

- map API resources and commands to Master Tasks and permission/recent-auth/idempotency/expected-version gates;
- add missing experiment-cycle, incident, data-governance, research-review, performance/FinOps, change-management, release, shell/search/notification, and developer-evidence resources;
- distinguish reads, asynchronous jobs, and commands;
- preserve stable error, Decimal, UTC, pagination, redaction, and OpenAPI rules.

### Acceptance Criteria

- every material command has explicit authorization, idempotency, concurrency, reason, audit, and safe-error behavior;
- browser direct writes cannot replace commands;
- no arbitrary prompt, SQL, environment, workflow, or live-execution API exists;
- generated OpenAPI remains the executable source after implementation.

## S23.4 Synchronize Database Schema

### Work

- map tables to domains and Master Tasks;
- add missing research-cycle stages, idempotency, reservations, state transitions, incidents/postmortems/actions, datasets/lineage/retention/holds, research reviews/approvals, behavior sets/changes/rollouts, releases/deployments, permissions/RLS assurance, notifications/preferences, documentation/test evidence, SLO/cost/quota/capacity, export/restore, and status records;
- define append-only versus mutable projections;
- align Decimal, UTC, constraints, indexes, RLS, retention, deletion/anonymization, and correction behavior.

### Acceptance Criteria

- every authoritative resource has a persistence/source-of-truth contract;
- append-only financial/audit/approval evidence cannot be mutated or deleted through ordinary paths;
- browser-visible objects have RLS and approved fields;
- retention and deletion cannot break financial, audit, incident, legal-hold, or reproducibility lineage.

## S23.5 Verify Cross-Contract Consistency

### Work

- compare product requirements, security, API, and schema against architecture, backend, env inventory, observability, testing, and detailed workspaces;
- verify terms, roles, statuses, error semantics, behavior-set freeze, cycle completeness, and paper-only boundaries;
- update task catalog, audit, changelog, and Sprint status;
- fetch every commit.

### Acceptance Criteria

- no Auth, RLS, command, schema, retention, or product-scope conflict remains;
- all synchronized files map to Master Tasks;
- all commits are retrievable;
- product implementation still starts at M001.

## Sprint 23 Definition of Done

- product, security, API, and database contracts are synchronized;
- new governance/operations resources are included without granting automatic authority;
- task/audit/changelog evidence is current;
- changes are committed and verified;
- product implementation remains not started.
