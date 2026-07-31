# Sprint 12 Tasks — Authentication, Workspace Administration, Configuration Governance, Security, Privacy, and Release Readiness Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a server-authoritative governance workspace that exposes authenticated identity, workspace membership, effective permissions, RBAC and RLS assurance, immutable configuration lifecycle, environment and secret posture, migration readiness, security and privacy evidence, backup and restore validation, and auditable release promotion gates without exposing secrets, bypassing domain controls, mutating immutable evidence, or enabling live trading.

## Authoritative References

- `docs/AUTH_CONFIGURATION_SECURITY_RELEASE_WORKSPACE_IMPLEMENTATION.md`
- `docs/SECURITY.md`
- `docs/DEPLOYMENT.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/API_SPECIFICATION.md`
- `docs/FREE_CLOUD_ARCHITECTURE.md`
- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/TEST_ENVIRONMENTS.md`
- `docs/OBSERVABILITY.md`
- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `docs/GEMINI_ANALYSIS_VALIDATION_WORKSPACE_IMPLEMENTATION.md`
- `CLOUD_MVP_TASKS.md`
- `LOCAL_AND_PRODUCTION_TASKS.md`
- `AGENTS.md`

## S12.1 Define Versioned Governance Workspace Schemas

### Objective

Create explicit contracts for account security, workspace administration, authorization assurance, RLS assurance, configuration governance, environment boundaries, secret posture, migrations, security, privacy, backups, release readiness, blockers, permissions, and links.

### Work

- define `GovernanceWorkspaceReadModel` and nested schemas;
- define release-candidate and authorization-assurance models;
- define account, membership, permission, configuration, secret, migration, finding, exception, privacy, backup, release, deployment, and rollback states;
- define redaction, compatibility, stale, unavailable, blocker, conflict, and approval rules;
- publish schemas in OpenAPI;
- generate frontend types where practical.

### Acceptance Criteria

- every governance state is machine-readable;
- effective permissions are server-provided;
- secret schemas contain no value fields;
- blocker and approval invalidation rules are explicit;
- contract tests pass.

## S12.2 Implement Account and Session Endpoint

### Objective

Expose authenticated identity and session security without exposing tokens.

### Work

- implement or extend `GET /api/v1/auth/me`;
- return user identity, provider, authentication time, issued and expiry time, recent-auth status, account state, memberships, security-event summary, and allowed session commands;
- classify expiring, expired, disabled, locked, revoked, invalid, and provider-unavailable states;
- enforce minimization and redaction;
- add safe telemetry.

### Acceptance Criteria

- tokens, cookies, signatures, password data, and recovery secrets are absent;
- session expiry is authoritative;
- unauthenticated and unavailable states fail closed;
- memberships are workspace-scoped;
- authentication tests pass.

## S12.3 Implement Sign-In, Sign-Out, and Session Security UX

### Objective

Provide secure authentication state and recovery messaging.

### Work

- integrate approved Supabase Auth flow;
- use generic authentication errors and rate-limit feedback;
- prevent account enumeration;
- implement secure sign-out and server/provider session revocation where supported;
- prompt for recent authentication before sensitive owner commands;
- handle expiry without losing unsent non-sensitive UI state.

### Acceptance Criteria

- credentials are handled only by approved flows;
- invalid or revoked sessions cannot access protected data;
- sign-out clears local authentication state safely;
- sensitive commands require recent authentication when configured;
- E2E and accessibility tests pass.

## S12.4 Implement Workspace List and Detail Endpoints

### Objective

Expose authorized workspace identity, status, owners, active configuration, experiments, memberships, and blockers.

### Work

- implement workspace list and detail projections;
- return ID, name, base currency, status, owners, timestamps, active configuration, experiment and portfolio summaries, role counts, retention profile, and blockers;
- use cursor pagination and approved filters;
- enforce RLS and application authorization;
- map safe errors.

### Acceptance Criteria

- users see only authorized workspaces;
- owner, experiment, and halt semantics remain distinct;
- blocker summaries are complete;
- archived workspaces remain auditable;
- integration tests pass.

## S12.5 Implement Workspace Administration Routes

### Objective

Add account, workspace, members, access-review, configuration, governance, and release routes.

### Work

- implement the approved canonical route family;
- add global navigation and role-aware route guards;
- preserve approved filters in URL state;
- add route-level error boundaries;
- visually separate evidence from privileged commands;
- hide no permission through frontend-only logic.

### Acceptance Criteria

- routes are directly addressable and keyboard reachable;
- server permissions determine command availability;
- invalid IDs and filters fail safely;
- refresh preserves stable read state;
- route tests pass.

## S12.6 Implement Membership and Role Read Models

### Objective

Expose complete membership, role, grant, revocation, and effective-permission evidence.

### Work

- render membership ID, workspace, user, role, state, grant source, reason, timestamps, expiry, recent-auth requirement, audit, and permission version;
- render service, migration, workflow, and read-only identities separately;
- preserve owner-count invariant state;
- support bounded filters;
- minimize identity exposure by role.

### Acceptance Criteria

- role labels do not substitute for effective permissions;
- system identities remain distinguishable from people;
- inactive and revoked memberships remain auditable;
- owner invariant is visible;
- component tests pass.

## S12.7 Implement Invitation Command and Lifecycle

### Objective

Invite workspace members safely without exposing invitation tokens.

### Work

- implement `POST /api/v1/workspaces/{workspace_id}/invitations`;
- require owner role, recent authentication when configured, idempotency, expected workspace version, target verification, role, reason, rate limit, and audit;
- persist pending, accepted, declined, revoked, and expired states;
- store tokens only in protected form;
- omit tokens from list APIs.

### Acceptance Criteria

- duplicate invitations are handled deterministically;
- tokens are never exposed after issuance;
- invitations expire and revoke correctly;
- unauthorized invitations fail closed;
- integration and abuse tests pass.

## S12.8 Implement Role Change and Membership Revocation Commands

### Objective

Change or revoke access with version guards and owner invariants.

### Work

- implement explicit role-change and revoke commands;
- require owner authorization, recent authentication, idempotency, expected version, reason, target checks, and confirmation for privilege increase or owner removal;
- ensure at least one owner remains;
- invalidate affected sessions or claims according to policy;
- persist audit events.

### Acceptance Criteria

- silent escalation is impossible;
- stale commands return safe conflicts;
- last owner cannot be removed;
- duplicate requests do not duplicate transitions;
- authorization and concurrency tests pass.

## S12.9 Implement Effective Permission Registry and View

### Objective

Expose canonical permissions and their application and database sources.

### Work

- define permission codes for reads and privileged commands;
- render role source, workspace scope, application-rule version, RLS-policy version, allow/deny, reason, verification time, and limitations;
- map routes and handlers to permissions;
- detect undocumented permissions;
- provide accessible matrix and narrow-layout views.

### Acceptance Criteria

- every protected route maps to a permission;
- browser does not infer permission from role alone;
- undocumented commands fail CI;
- mismatches are explicit;
- contract and component tests pass.

## S12.10 Implement Access Review Workspace

### Objective

Support periodic owner review of human and service access.

### Work

- render current members, stale memberships, privileged identities, recent changes, denied attempts, findings, owner invariant, last review, next due, reviewer, and remediation;
- implement review-record creation with owner authorization and audit;
- link findings to explicit remediation commands;
- preserve prior reviews;
- avoid automatic revocation.

### Acceptance Criteria

- review evidence is immutable;
- overdue reviews are visible;
- findings link to affected identities;
- no access changes occur implicitly;
- review tests pass.

## S12.11 Implement Application RBAC Assurance

### Objective

Verify handler-level authorization and endpoint inventory.

### Work

- evaluate route, command, workspace, role, resource, recent-auth, idempotency, expected-version, and denied-audit checks;
- map checks to code revision and test evidence;
- expose verified, mismatch, incomplete, or unavailable outcome;
- detect dependency-only authorization gaps;
- add CI endpoint inventory checks.

### Acceptance Criteria

- handler authorization is independently verified;
- route dependencies alone do not satisfy assurance;
- every mismatch has evidence and severity;
- missing verification fails closed for release;
- assurance tests pass.

## S12.12 Implement RLS Assurance and Matrix

### Objective

Verify deny-by-default database isolation across all relevant identities.

### Work

- verify RLS enabled on every Data API-visible table;
- test anonymous, viewer, operator, owner, service, migration, workflow, and read-only identities;
- test workspace isolation and approved read-only views;
- test direct-write denial for critical financial and control tables;
- verify claim mapping and policy migration versions;
- persist assurance result.

### Acceptance Criteria

- browser identities cannot write critical tables directly;
- workspace isolation is proven;
- service and migration roles remain scoped and separated;
- missing or mismatched RLS is critical;
- RLS tests pass.

## S12.13 Implement Authorization Mismatch Detection

### Objective

Detect disagreement between application authorization and RLS.

### Work

- detect API-allow/RLS-deny, API-deny/RLS-allow, role mapping, scope, stale claims, direct-write, service overreach, migration runtime, undocumented endpoint, and missing-audit mismatches;
- persist severity, evidence, environment, affected resource, incident, and remediation;
- show critical mismatches first;
- link to code and migration revision where safe;
- add regression fixtures.

### Acceptance Criteria

- mismatches cannot appear as verified;
- API-deny/RLS-allow is treated as security exposure;
- affected resources are traceable;
- critical mismatches block release;
- detection tests pass.

## S12.14 Implement Immutable Configuration List and Detail Endpoints

### Objective

Expose canonical workspace configuration versions and dependencies.

### Work

- return ID, version, canonical JSON, hash, domain references, creator, lifecycle, evaluation, approval, activation, archive, and dependent experiment, backtest, report, and release references;
- redact prohibited fields;
- support filters and cursor pagination;
- enforce authorization and RLS;
- validate canonical hashes.

### Acceptance Criteria

- used configurations are immutable;
- dependencies are complete;
- canonical JSON contains no secret values;
- hashes are deterministic;
- API tests pass.

## S12.15 Implement Configuration Lifecycle Commands

### Objective

Create, validate, approve, activate, supersede, and archive configuration versions safely.

### Work

- implement draft creation and explicit lifecycle commands;
- require owner role, recent authentication for approval/activation, idempotency, expected version, validation, compatibility, domain reviews, AI evaluation where applicable, and audit;
- prohibit editing after use;
- activate only for future eligible resources;
- preserve active experiment freezes.

### Acceptance Criteria

- invalid or incomplete configurations cannot be approved;
- behavior changes require versioned evidence;
- running experiments do not silently change;
- repeated commands are idempotent;
- state-machine tests pass.

## S12.16 Implement Configuration Diff and Dependency View

### Objective

Explain material changes and affected future resources.

### Work

- render field-level old/new values, category, materiality, compatibility, required evaluation, risk review, execution review, privacy impact, migration impact, and dependent resources;
- keep secret fields redacted or represented by metadata state only;
- distinguish unchanged values;
- support accessible tabular and narrative summaries;
- link approvals and tests.

### Acceptance Criteria

- every material change has governance requirements;
- secret values never appear in diffs;
- incompatible changes are explicit;
- active experiment impact is never implied silently;
- diff tests pass.

## S12.17 Implement Environment Boundary View

### Objective

Verify local, CI, demo, experiment, staging, and production-research isolation.

### Work

- render purpose, database/Auth isolation, Gemini project separation, domains, CORS, deployment source, data classification, live-trading-disabled state, private-credential prohibition, verification time, blockers, and limitations;
- detect cross-environment reuse;
- link deployments and secrets metadata;
- expose stale verification;
- prohibit secret display.

### Acceptance Criteria

- each environment is clearly labeled;
- production data and credentials are absent from CI;
- unsafe cross-environment reuse is critical;
- live trading remains disabled everywhere in scope;
- environment tests pass.

## S12.18 Implement Secret Inventory Metadata Endpoint and View

### Objective

Expose secret posture without exposing secret values.

### Work

- return canonical metadata name, purpose, environment, storage provider, owner service, presence, creation, rotation, due date, scope, exposure, verification, and public-build prohibition state;
- apply role-specific minimization;
- omit hashes and retrieval links;
- support safe filters;
- instrument state counts only.

### Acceptance Criteria

- no endpoint contains secret values or usable hashes;
- missing and overdue states are explicit;
- public frontend secret prohibition is verifiable;
- unauthorized inventory access fails closed;
- privacy and security tests pass.

## S12.19 Implement Secret Scanning and Exposure Workflow

### Objective

Detect source, log, prompt, response, telemetry, and artifact secret exposure.

### Work

- ingest approved secret-scan evidence;
- classify healthy, missing, overdue, suspected, confirmed, mis-scoped, source, log, and frontend-artifact states;
- create incident and blocker for suspected or confirmed exposure;
- link rotation evidence;
- preserve scan and finding history.

### Acceptance Criteria

- exposure cannot be dismissed as a warning-only state;
- raw secret values are redacted from findings;
- false-positive resolution is audited;
- confirmed exposure blocks release;
- security tests pass.

## S12.20 Implement Secret Rotation Evidence

### Objective

Record rotation, revocation, verification, and dependent-service recovery without values.

### Work

- render trigger, incident, actor, timing, old credential revocation, new credential verification, service restart/deployment, smoke tests, audit, and limitations;
- require authorized workflow references;
- preserve failed attempts;
- verify stale credential rejection where testable;
- close blocker only after validation.

### Acceptance Criteria

- no old or new value is displayed;
- revocation and verification are separate checks;
- failed rotation remains visible;
- dependent services are tested;
- rotation tests pass.

## S12.21 Implement Migration Readiness Endpoint and Workspace

### Objective

Expose revision, drift, rehearsal, compatibility, backup, and approval evidence.

### Work

- render migration set, commit, target, current and expected revision, pending list, applied immutability, drift, reset, upgrade, rehearsal, compatibility, expand/migrate/contract stage, lock classification, recovery strategy, backup, approval, and audit;
- support environment filters;
- link RLS checks;
- classify destructive and unrehearsed changes;
- add deterministic migration manifests.

### Acceptance Criteria

- applied migrations are never edited;
- drift and rehearsal failure block release;
- RLS changes are verified;
- rollback is not promised when unsafe;
- migration tests pass.

## S12.22 Implement Security Finding Registry

### Objective

Persist and expose findings from scans, tests, and manual reviews.

### Work

- implement finding list and detail projections;
- return source, category, severity, status, affected artifact, safe description, detection, evidence, owner, remediation, due date, verification, exception, and incident;
- preserve closed and rejected findings;
- support bounded filters;
- sanitize sensitive evidence.

### Acceptance Criteria

- findings cannot be deleted to clean a release;
- severity and status are server-defined;
- verification evidence is required for closure;
- critical and high findings are prominent;
- registry tests pass.

## S12.23 Implement Security Scan and Supply-Chain Evidence

### Objective

Expose secret, dependency, static, container, SBOM, action-pinning, and branch-protection checks.

### Work

- integrate evidence from dependency review, Python and frontend scanners, Bandit, Semgrep, Trivy, SBOM, container checks, action pinning, and branch protection;
- render tool version, target, timestamp, outcome, finding counts, limitations, and artifact hashes;
- distinguish unavailable from passing;
- link release gates;
- avoid raw exploit details in broad roles.

### Acceptance Criteria

- missing tools are not represented as pass;
- evidence maps to exact artifacts;
- critical findings block eligible promotions;
- SBOM hash is preserved;
- integration tests pass.

## S12.24 Implement Time-Limited Security Exceptions

### Objective

Govern approved high-severity exceptions with compensating controls and expiry.

### Work

- implement exception read and owner-approval workflow;
- require finding, rationale, compensating controls, scope, start, expiry, review cadence, remediation owner, evidence, and audit;
- prohibit critical exceptions under baseline policy;
- mark expired exceptions as blockers;
- preserve terminal history.

### Acceptance Criteria

- critical findings cannot be waived;
- high exceptions expire automatically by policy state;
- changed scope invalidates approval;
- compensating controls are testable;
- exception tests pass.

## S12.25 Implement Privacy Data Inventory

### Objective

Document processed data classes, purposes, providers, retention, deletion, export, sensitivity, and environments.

### Work

- define identity, audit, configuration, market, Gemini, logs, incidents, exports, and backup classes;
- render purpose, policy or review status, source, recipient/provider, retention, deletion, export, sensitivity, and environment;
- link minimization and provider-term evidence;
- preserve historical versions;
- label legal review status without legal conclusions.

### Acceptance Criteria

- every persisted data class has an inventory entry;
- unknown purpose or retention is a blocker for public promotion;
- legal certification is not implied;
- role-sensitive details are minimized;
- privacy tests pass.

## S12.26 Implement Data Minimization and Retention Workspace

### Objective

Verify collection, prompts, logs, telemetry, raw payloads, exports, and cleanup behavior.

### Work

- render minimization checks and retention policies;
- expose data class, period, environment override, policy, archive, deletion/anonymization, hold, lineage constraints, cleanup runs, next due, and verification;
- detect cleanup failures and orphaned lineage;
- protect required audit and financial history;
- link incidents and findings.

### Acceptance Criteria

- secrets and unnecessary personal data remain excluded from Gemini and telemetry;
- cleanup cannot break required lineage;
- overdue cleanup is visible;
- raw provider retention is bounded;
- retention tests pass.

## S12.27 Implement Provider Terms and Regional Readiness View

### Objective

Track service-tier, data-handling, regional, EEA, retention, and review evidence.

### Work

- render provider, tier, review date, data-handling class, regional eligibility, EEA requirements, retention assumptions, hosting notes, production-use approval, owner/legal-review status, next due, and limitations;
- mark stale or unknown evidence;
- link target release;
- avoid legal claims;
- preserve review history.

### Acceptance Criteria

- stale terms evidence blocks public or production-research promotion according to policy;
- selected tier and environment are explicit;
- legal review status is visible;
- no unsupported compliance claim appears;
- readiness tests pass.

## S12.28 Implement Account Data Request Boundary

### Objective

Define auditable account access, profile correction, export, closure, and deletion/restriction workflows for future public use.

### Work

- model request identity, verification, scope, retention constraints, immutable audit evidence, mutable profile actions, required-history exceptions, completion, and communication;
- expose read-only status in Sprint 12 unless approved command workflows exist;
- preserve financial and audit integrity;
- enforce authorization and privacy;
- add test fixtures.

### Acceptance Criteria

- account closure does not silently delete required evidence;
- identity verification is mandatory;
- constraints are explicit;
- no legal promise exceeds documented policy;
- workflow tests pass.

## S12.29 Implement Backup and Restore Readiness Workspace

### Objective

Expose environment-specific backup, export, encryption, retention, restore, integrity, reconciliation, RPO, and RTO evidence.

### Work

- render mechanism, cadence, retention, last success, next due, failures, artifact hash, restore target, restore test, migration revision, data integrity, ledger reconciliation, measured recovery values, and limitations;
- distinguish free-cloud logical export from managed production backup;
- require isolated restore;
- link incidents and release gates;
- detect overdue evidence.

### Acceptance Criteria

- backup is not ready without successful restore;
- restore verifies ledger reconciliation;
- RPO/RTO are measured rather than invented;
- failed and overdue states block applicable promotions;
- recovery tests pass.

## S12.30 Implement Release Candidate Registry

### Objective

Create immutable release identities tied to exact source and artifacts.

### Work

- implement release list and detail projections;
- return source branch, commit, target, version, creator, backend and frontend digests, lock hashes, migrations, OpenAPI hash, SBOM, compatibility, release notes, live-trading assertion, and status;
- support bounded filters;
- preserve failed and rejected releases;
- verify artifact immutability.

### Acceptance Criteria

- approved releases cannot change artifacts;
- source-to-artifact provenance is complete;
- live-trading-disabled state is explicit;
- failed releases remain discoverable;
- API tests pass.

## S12.31 Implement Release Provenance and Artifact Verification

### Objective

Prove release artifacts originate from reviewed source and protected CI.

### Work

- render commit, branch protection, reviews, CI run, build identity, commands, lock hashes, base-image digest, artifact hashes, OpenAPI, docs, SBOM, attestation, and source verification;
- verify digests at deployment;
- classify missing or mismatched provenance;
- link findings;
- avoid internal secret paths.

### Acceptance Criteria

- every artifact maps to exact source;
- digest mismatch is critical;
- missing SBOM or required review blocks promotion;
- provenance is immutable;
- supply-chain tests pass.

## S12.32 Implement Release Gate Engine and Workspace

### Objective

Evaluate all technical, safety, privacy, recovery, and approval gates server-side.

### Work

- implement gates for source, tests, migration, RLS, Auth, authorization, secrets, static analysis, dependencies, containers, AI safety, market data, strategy, risk, execution, ledger, reconciliation, accessibility, docs, OpenAPI, backup, restore, incident, rollback, privacy, terms, environment isolation, live-trading-disabled, and manual approval;
- return version, evidence, outcome, severity, timestamp, and blockers;
- freeze gate snapshot for approval;
- support target-specific profiles.

### Acceptance Criteria

- readiness is deterministic for the same evidence;
- missing required evidence fails closed;
- critical blockers cannot be dismissed;
- target profiles are versioned;
- gate tests pass.

## S12.33 Implement Promotion Profile Views

### Objective

Explain Local→Demo, Demo→Experiment, Experiment→Staging, and Staging→Production Research requirements.

### Work

- render profile version, source, target, required gates, evidence, blockers, approvals, and limitations;
- show current progress without implying approval;
- prohibit Binance test or live progression within Sprint 12;
- link related experiments and releases;
- preserve prior profile decisions.

### Acceptance Criteria

- each promotion path has explicit requirements;
- production research remains paper-only;
- missing gates remain visible;
- future Binance environments require a separate specification;
- profile tests pass.

## S12.34 Implement Release Approval Workflow

### Objective

Record owner decisions against an immutable gate snapshot.

### Work

- implement approve, reject, and request-changes commands;
- require eligible role, recent authentication, idempotency, expected release version, gate snapshot hash, blocker validation, reason, and audit;
- invalidate approval when artifacts, migrations, configuration, or gates change;
- preserve every decision;
- prohibit automatic approval.

### Acceptance Criteria

- approval applies only to exact evidence snapshot;
- stale approval cannot deploy changed artifacts;
- blocked releases cannot be approved contrary to policy;
- repeated commands are idempotent;
- approval tests pass.

## S12.35 Implement Deployment Evidence View

### Objective

Present controlled deployment, migration, health, Auth, RLS, smoke, reconciliation, and audit evidence.

### Work

- render deployment ID, release, target, workflow/platform run, actor, timing, digests, migration, health, Auth, RLS, API, frontend, reconciliation, live-trading-disabled checks, outcome, safe error, rollback, and audit;
- verify deployed digests match approval;
- distinguish Render cold start from deployment failure;
- preserve failed attempts;
- avoid unsafe one-click bypass.

### Acceptance Criteria

- deployment evidence maps to approved release;
- digest or migration mismatch fails deployment;
- failed attempts remain visible;
- no secret environment values appear;
- deployment tests pass.

## S12.36 Implement Rollback Readiness and Post-Release Verification

### Objective

Expose safe rollback or forward-fix strategy and verify deployed state.

### Work

- render compatible artifact, migration strategy, backup prerequisite, configuration plan, frontend rollback, halt behavior, runbook, rehearsal, timestamp, and limitations;
- run post-release digest, migration, health, Auth, RLS, CORS, asset-secret, market, provider, paper-mode, ledger, reconciliation, logs, and rollback-window checks;
- trigger failed, halt, rollback, or forward-fix state on critical failure;
- preserve evidence.

### Acceptance Criteria

- unsafe database rollback is not promised;
- post-release checks are complete and auditable;
- live trading remains disabled;
- failed critical checks trigger policy action;
- rollback and verification tests pass.

## S12.37 Implement Governance Blocker and Audit Timeline

### Objective

Unify blocker, finding, incident, approval, and transition lineage.

### Work

- render blocker identity, category, severity, scope, environment, affected resource, reason, evidence, owner, due date, incident/finding, and state;
- link immutable events for authentication, memberships, reviews, configurations, secrets, migrations, findings, privacy, backups, releases, approvals, deployments, rollbacks, and verification;
- preserve deterministic ordering and filters;
- prohibit critical dismissal;
- enforce role-based detail minimization.

### Acceptance Criteria

- every blocker is traceable to evidence;
- critical blockers remain visible;
- audit events are append-only;
- unauthorized detail is absent;
- timeline tests pass.

## S12.38 Implement Authorized Governance and Release Export

### Objective

Generate redacted, provenance-preserving governance packages.

### Work

- support access, authorization, RLS, configuration, environment, secret metadata, migration, findings, exceptions, privacy, retention, terms, backup, restore, release, gates, approval, deployment, rollback, and verification exports;
- generate server-side;
- include schema, identities, timestamps, hashes, blockers, approvals, audit, and limitations;
- enforce authorization and redaction;
- exclude secrets and unsafe vulnerability details.

### Acceptance Criteria

- exports preserve critical blockers;
- no secret values or invitation tokens appear;
- provenance and approval snapshots are complete;
- role restrictions are enforced;
- export tests pass.

## S12.39 Add Explicit State Handling

### Objective

Define safe rendering for every account, access, configuration, security, privacy, backup, and release state.

### Work

- implement loading, unauthenticated, expiring, recent-auth, disabled, no workspace, invitation, role change, verified, authorization mismatch, RLS mismatch, configuration states, secret states, migration states, finding and exception states, privacy stale, backup overdue, restore failure, release draft/blocked/ready/approved/deploying/deployed/failed/rolled-back, verification failure, schema mismatch, unauthorized, not found, backend unavailable, command conflict, and export failure;
- define bounded retry behavior;
- prevent infinite retries;
- label cached data stale.

### Acceptance Criteria

- critical states never render as ready or empty;
- loading fabricates no permissions or readiness;
- conflicts show current server evidence;
- stale cached data is explicit;
- state-matrix tests pass.

## S12.40 Add Responsive and Accessibility Verification

### Objective

Ensure governance evidence and privileged confirmations remain usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom layouts;
- test headings, landmarks, focus, keyboard operation, permission matrices, tables, diffs, timelines, confirmation dialogs, definitions, announcements, and copy controls;
- verify reduced motion and contrast;
- test long IDs, hashes, artifact digests, policies, findings, and reason codes;
- record screen-reader spot checks.

### Acceptance Criteria

- no critical evidence is hover-only;
- no state relies only on color;
- privileged confirmations are fully accessible;
- tables and diffs retain context at narrow widths;
- no critical automated violation remains;
- manual evidence is recorded.

## S12.41 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make authentication, authorization, RLS, immutable configuration, secret safety, migration readiness, privacy evidence, restore validation, and release approval release-blocking.

### Work

- add contract, Auth, session, membership, permission, RBAC, RLS, mismatch, configuration, environment, secret, rotation, migration, finding, exception, privacy, retention, provider-term, backup, restore, release, provenance, gate, approval, deployment, rollback, verification, route, E2E, accessibility, visual, export, and audit tests;
- add CSRF, rate-limit, expected-version, session-revocation, secret, log-redaction, hostile-content, unsafe-command, and artifact-tamper tests;
- verify browser users cannot access service-role or migration credentials or write critical tables;
- instrument safe account, access, denied, RLS, configuration, secret, migration, finding, exception, privacy, backup, restore, gate, approval, deployment, rollback, verification, conflict, and export metrics;
- test prohibited telemetry fields.

### Acceptance Criteria

- unauthorized and stale commands fail closed;
- critical secrets, RLS, migration, finding, restore, and release failures block promotion;
- no browser or AI path gains SQL, secret, service-role, deployment-bypass, live-trading, or critical-waiver authority;
- immutable evidence remains append-only;
- telemetry contains no prohibited fields;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Authentication | Provider flow, generic errors, expiry, revocation, recent authentication, disabled account, sign-out, rate limit, and no-enumeration tests |
| Authorization | Role matrix, handler checks, effective permissions, owner invariant, idempotency, expected versions, denied audit, and endpoint inventory tests |
| RLS | Anonymous, viewer, operator, owner, service, migration, workflow, workspace isolation, direct-write denial, claim mapping, and mismatch tests |
| Configuration | Canonical hash, lifecycle, validation, evaluation, approval, activation, immutability, dependency, freeze, supersession, and archive tests |
| Secrets | Inventory metadata, no-value schemas, source/log/prompt/response/artifact scans, exposure, rotation, revocation, and smoke tests |
| Migrations | Clean reset, upgrade, drift, applied immutability, data changes, RLS, compatibility, rehearsal, backup, and failure tests |
| Security and privacy | Findings, scans, SBOM, exceptions, critical-waiver prohibition, data inventory, minimization, retention, cleanup, terms, regional, and export tests |
| Recovery | Backup, encryption metadata, cadence, artifact hash, isolated restore, migration revision, integrity, reconciliation, RPO/RTO, and failure tests |
| Release | Provenance, digests, reviews, CI, OpenAPI, SBOM, gates, profiles, approval invalidation, deployment, smoke, rollback, and verification tests |
| Accessibility | Keyboard, matrices, tables, diffs, timelines, confirmations, definitions, zoom, reflow, contrast, and manual review |

## Sprint Exit Gate

Sprint 12 is complete only when:

- S12.1 through S12.41 are implemented and verified;
- account, session, workspace, membership, role, and effective permissions are server-authoritative;
- application RBAC and RLS are independently verified and any mismatch fails closed;
- membership changes preserve owner invariants and immutable audit evidence;
- used configuration versions are immutable and active experiments remain frozen;
- secret APIs expose metadata only, and exposure or overdue rotation blocks release;
- applied migrations remain immutable and drift, rehearsal, compatibility, backup, and RLS gates pass;
- findings and exceptions remain discoverable, critical findings cannot be waived, and high exceptions expire;
- privacy inventory, minimization, retention, cleanup, provider terms, and regional readiness are explicit without claiming legal certification;
- backup readiness requires isolated restore and ledger reconciliation;
- release candidates preserve source, artifact, dependency, migration, OpenAPI, SBOM, gate, approval, deployment, rollback, and post-release evidence;
- approvals are tied to immutable gate snapshots and invalidated by changes;
- every environment preserves paper-only and live-trading-disabled boundaries;
- no browser or AI secret display, SQL, service-role, migration-role, silent escalation, automatic approval, finding suppression, unsafe deploy bypass, private exchange order, testnet, or live-trading authority exists;
- accessibility, responsive, security, privacy, contract, authentication, authorization, RLS, configuration, secret, migration, finding, exception, retention, backup, restore, release, E2E, export, audit, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 13 defines and implements the Product Shell, Onboarding, Help, Trust Center, Global Search, Notifications, Internationalization, and Cross-Workspace Experience.
