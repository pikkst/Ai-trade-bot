# Authentication, Workspace Administration, Configuration Governance, Security, Privacy, and Release Readiness Workspace Implementation Specification

Last reviewed: 2026-07-31  
Status: Sprint 12 authoritative administration, governance, and release-readiness workspace specification

## 1. Purpose

This document defines the implementation contract for the Authentication, Workspace Administration, Configuration Governance, Security, Privacy, and Release Readiness Workspace of The Daily Roast AI.

The workspace explains who is authenticated, which workspace and role grants apply, whether application authorization and PostgreSQL Row Level Security agree, which immutable configuration versions are active or frozen, whether environment secrets and deployment boundaries are healthy without exposing secret values, which security and privacy findings remain unresolved, whether migrations, backups, restore, observability, and operational runbooks are ready, and whether a release or environment promotion satisfies every required gate.

The workspace is governance-first. It must not become a generic superuser console that bypasses domain controls, mutates immutable financial evidence, exposes secrets, silently changes active experiments, or authorizes live trading.

## 2. Scope

Sprint 12 covers:

- authentication session, identity, recent-authentication, and sign-out state;
- workspace list, detail, membership, role, invitation, and access-review evidence;
- owner, operator, viewer, service, migration, workflow, and read-only authority boundaries;
- application RBAC and Supabase/PostgreSQL RLS verification;
- immutable workspace configuration versions and activation lineage;
- environment and deployment-boundary status;
- secret inventory metadata, rotation state, and exposure incidents without secret values;
- migration revision, drift, rehearsal, compatibility, and rollback readiness;
- security findings, exceptions, dependency and container scan evidence;
- privacy, retention, deletion, export, provider-term, and data-minimization evidence;
- backup, export, restore, RPO/RTO evidence by environment;
- release candidate identity, artifacts, SBOM, provenance, approvals, gates, deployment, smoke, rollback, and post-release verification;
- local, CI, demo, paper experiment, staging, and production-research promotion gates;
- immutable owner approvals and audit lineage;
- responsive, accessible, secure, observable, and testable presentation.

Sprint 12 does not implement:

- live trading or private Binance execution;
- a browser database console;
- arbitrary SQL;
- arbitrary environment-variable editing;
- secret-value display, copy, download, or browser storage;
- direct mutation of ledger, audit, fills, decisions, reports, or completed experiments;
- silent role escalation;
- automatic release approval;
- automatic waiver of critical findings;
- production deployment from an unreviewed browser action;
- automatic resume after security, integrity, or reconciliation halt;
- legal conclusions or compliance certification.

## 3. User Outcomes

A user should be able to answer:

1. Who am I authenticated as, and when does the session expire?
2. Which workspaces can I access and with which effective role?
3. Which permissions come from application RBAC, RLS, service roles, or workflow identities?
4. Do API authorization tests and database RLS verification agree?
5. Which memberships, invitations, access changes, and denied attempts occurred?
6. Which configuration version is active, frozen, archived, or awaiting approval?
7. Which experiments, backtests, reports, and deployments reference a configuration version?
8. Are any secrets missing, stale, exposed, due for rotation, or incorrectly present in public assets?
9. Which migration revision is deployed, pending, drifted, rehearsed, or incompatible?
10. Which security findings and time-limited exceptions remain open?
11. Which personal or sensitive data classes are processed, retained, exported, or deleted?
12. Are Gemini terms, regional eligibility, privacy review, and retention assumptions current for the target environment?
13. Are backup and restore evidence sufficient for the environment?
14. Which immutable artifact, commit, dependency lock, migration set, frontend build, and SBOM form the release candidate?
15. Did required tests, scans, approvals, migration rehearsal, smoke tests, reconciliation, and rollback checks pass?
16. Which release blocker prevents promotion?
17. Who approved or rejected the release, when, and why?
18. Does the target environment still explicitly prohibit live trading?

## 4. Canonical Routes

```text
/account
/account/security
/workspaces
/workspaces/:workspaceId
/workspaces/:workspaceId/members
/workspaces/:workspaceId/access-review
/workspaces/:workspaceId/configurations
/workspaces/:workspaceId/configurations/:configurationId
/governance/authorization
/governance/rls
/governance/secrets
/governance/migrations
/governance/security
/governance/privacy
/governance/backups
/releases
/releases/:releaseId
/releases/:releaseId/gates
/releases/:releaseId/deployment
/releases/:releaseId/rollback
/releases/:releaseId/audit
```

The workspace must link to experiments, cycles, portfolio, Gemini analyses, strategy and risk, backtests, incidents, audit, deployment evidence, and release artifacts.

State-changing routes must be distinct from read-only evidence routes and available only when server-provided permissions allow them.

## 5. Information Architecture

The governance landing page is ordered as follows:

1. authenticated identity, environment, effective role, and session state;
2. critical access, secret, migration, security, privacy, backup, or release blockers;
3. workspace and membership summary;
4. RBAC and RLS verification;
5. active and frozen configuration versions;
6. environment and secret metadata;
7. migration and schema readiness;
8. security findings and exceptions;
9. privacy, retention, and provider-term state;
10. backup, export, and restore evidence;
11. release candidates and promotion gates;
12. approvals, deployment, rollback, and audit lineage.

A critical security finding, secret exposure, RLS mismatch, migration drift, failed restore, expired exception, or live-trading configuration must visually dominate release-readiness summaries.

## 6. Recommended Read Models

Recommended governance contract:

```ts
interface GovernanceWorkspaceReadModel {
  schemaVersion: string;
  account: AccountSecuritySummary;
  workspace: WorkspaceAdministrationSummary;
  authorization: AuthorizationAssuranceSummary;
  rls: RlsAssuranceSummary;
  configurations: ConfigurationGovernanceSummary;
  environment: EnvironmentBoundarySummary;
  secrets: SecretPostureSummary;
  migrations: MigrationReadinessSummary;
  security: SecurityPostureSummary;
  privacy: PrivacyReadinessSummary;
  backups: BackupRestoreReadinessSummary;
  release: ReleaseReadinessSummary | null;
  blockers: GovernanceBlocker[];
  diagnostics: DiagnosticSummary[];
  permissions: GovernanceCommandPermissions;
  links: GovernanceResourceLinks;
}
```

Recommended release contract:

```ts
interface ReleaseCandidateReadModel {
  schemaVersion: string;
  release: ReleaseIdentity;
  target: ReleaseTargetSummary;
  artifacts: ReleaseArtifactSummary[];
  provenance: ReleaseProvenanceSummary;
  migrations: ReleaseMigrationSummary;
  gates: ReleaseGateResult[];
  findings: ReleaseFindingSummary[];
  approvals: ReleaseApprovalSummary[];
  deployment: DeploymentExecutionSummary | null;
  smokeTests: ReleaseSmokeTestSummary[];
  rollback: RollbackReadinessSummary;
  postRelease: PostReleaseVerificationSummary | null;
  outcome: "draft" | "blocked" | "ready" | "approved" | "deploying" | "deployed" | "failed" | "rolled_back" | "rejected";
  blockers: GovernanceBlocker[];
  diagnostics: DiagnosticSummary[];
  links: ReleaseResourceLinks;
}
```

Recommended authorization assurance contract:

```ts
interface AuthorizationAssuranceReadModel {
  schemaVersion: string;
  workspaceId: string;
  roleMatrixVersion: string;
  applicationChecks: AuthorizationCheckResult[];
  rlsChecks: AuthorizationCheckResult[];
  effectivePermissions: EffectivePermissionSummary[];
  mismatches: AuthorizationMismatch[];
  deniedAttemptSummary: DeniedAttemptSummary;
  outcome: "verified" | "mismatch" | "incomplete" | "unavailable";
  verifiedAt: string;
}
```

The frontend must not calculate effective permissions, release readiness, RLS assurance, secret health, migration compatibility, vulnerability severity, exception validity, privacy readiness, or deployment authority.

## 7. Account and Session Contract

Required fields:

- authenticated user ID;
- normalized login or email according to policy;
- display name;
- authentication provider;
- authentication time;
- session issued and expiry timestamps;
- recent-authentication status;
- multi-factor state when implemented;
- account active, disabled, locked, or recovery state;
- effective workspace memberships;
- last security event summary;
- sign-out and session-revocation permissions;
- safe device or session metadata where approved.

Tokens, cookies, signatures, password hashes, recovery secrets, and provider credentials must never be exposed.

## 8. Authentication States

Supported states include:

- unauthenticated;
- authenticating;
- authenticated;
- session expiring;
- session expired;
- recent authentication required;
- account disabled;
- account locked;
- recovery pending;
- provider unavailable;
- token invalid;
- token revoked;
- authorization unavailable.

The UI must fail closed when session or authorization evidence is unavailable.

## 9. Sign-In and Sign-Out Boundary

Authentication uses the approved Supabase Auth or future versioned provider integration.

Requirements:

- no password handling outside approved provider or server flow;
- HTTPS outside local development;
- generic authentication errors;
- rate limits and abuse controls;
- no account enumeration;
- short-lived access tokens;
- explicit session expiry behavior;
- secure sign-out and session revocation;
- audit of privileged denied attempts;
- recent authentication for sensitive owner commands where required.

Sprint 12 does not introduce an unreviewed refresh-token design.

## 10. Workspace Identity

Required fields:

- immutable workspace ID;
- name;
- base currency;
- status;
- owner references;
- creation and archive timestamps;
- active configuration reference;
- active experiment and portfolio summaries;
- membership count by role;
- security and release blockers;
- data-retention profile;
- environment references where applicable.

Workspace status must not override experiment or portfolio halt semantics.

## 11. Membership and Role Contract

Roles:

- `owner`;
- `operator`;
- `viewer`.

System identities may include:

- trusted service role;
- migration role;
- scheduled workflow identity;
- read-only operational identity.

Required membership fields:

- membership ID;
- workspace and user references;
- role;
- status;
- granted by;
- grant reason;
- created, accepted, changed, revoked, and expiry timestamps where applicable;
- recent-authentication requirement;
- audit references;
- effective permission version.

At least one owner must remain according to application policy.

## 12. Effective Permission Contract

Every effective permission must identify:

- canonical permission code;
- role source;
- workspace scope;
- application authorization rule version;
- database RLS policy version where applicable;
- command or resource scope;
- allow or deny outcome;
- reason code;
- verification timestamp;
- limitation or conflict.

The UI must not infer permissions from role labels alone.

## 13. Membership Commands

Approved commands may include:

```http
POST /api/v1/workspaces/{workspace_id}/invitations
POST /api/v1/workspaces/{workspace_id}/members/{membership_id}/role-changes
POST /api/v1/workspaces/{workspace_id}/members/{membership_id}/revoke
```

Every command requires:

- owner authorization;
- recent authentication where policy requires;
- idempotency key;
- expected workspace or membership version;
- target identity verification;
- explicit role and scope;
- reason code;
- confirmation for privilege increases or owner removal;
- invariant check that at least one owner remains;
- immutable audit event.

Direct browser writes to membership tables are prohibited.

## 14. Invitation Contract

Required invitation fields:

- invitation ID;
- workspace;
- target address or identity reference;
- proposed role;
- inviter;
- created and expiry timestamps;
- accepted, declined, revoked, or expired state;
- one-time token stored only in protected form;
- audit references;
- rate-limit and abuse state.

Invitation tokens must never be returned in administrative list APIs after issuance.

## 15. Access Review

The access-review workspace must expose:

- current members and roles;
- inactive or stale memberships;
- privileged service identities;
- recent role changes;
- recent denied attempts;
- unresolved access findings;
- owner-count invariant;
- last review and next due date;
- reviewer and approval references;
- remediation state.

A review must not silently revoke access without an explicit audited command.

## 16. Application RBAC Assurance

RBAC verification includes:

- route and command permission matrix;
- handler-level authorization checks;
- workspace ownership checks;
- role and resource-scope checks;
- recent-authentication checks;
- idempotency and expected-version checks for privileged commands;
- denied-attempt audit behavior;
- generated endpoint inventory;
- test coverage and last verified revision.

A route dependency alone is not sufficient evidence if handler authorization is missing.

## 17. Row Level Security Assurance

RLS verification includes:

- RLS enabled on every Data API-visible table;
- deny-by-default behavior;
- approved read-only views;
- anonymous access tests;
- viewer, operator, owner, service-role, and migration-role tests;
- workspace isolation;
- direct insert, update, and delete denial for ledger, fills, risk decisions, AI runs, audit events, and experiment-control records;
- policy version and migration reference;
- Supabase Auth claim mapping;
- mismatch and drift detection.

An RLS mismatch is a critical release blocker.

## 18. Authorization Mismatch Contract

Mismatch categories include:

- API allows while RLS denies;
- API denies while RLS allows;
- role mapping inconsistency;
- missing workspace scope;
- stale claim mapping;
- browser direct-write exposure;
- service-role overreach;
- migration role available to runtime;
- undocumented endpoint;
- missing denied-attempt audit.

Every mismatch requires severity, evidence, affected resource, environment, detection time, incident reference, and remediation status.

## 19. Configuration Version Contract

Required configuration fields:

- immutable configuration ID;
- workspace;
- semantic or monotonic version;
- canonical JSON;
- configuration hash;
- allowed markets and intervals;
- feature, Gemini, prompt, schema, strategy, risk, execution, accounting, benchmark, budget, retention, and schedule references;
- creator;
- creation time;
- lifecycle state;
- evaluation and approval references;
- activation and archive timestamps;
- dependent experiments, backtests, reports, and releases.

Used configuration versions are immutable.

## 20. Configuration Lifecycle

Supported states include:

- draft;
- validating;
- rejected;
- ready for approval;
- approved;
- active;
- frozen by experiment;
- superseded;
- archived.

Every transition records actor, reason, expected version, validation, approval, audit, and dependent-resource checks.

An active experiment must not silently inherit a superseding configuration.

## 21. Configuration Governance Commands

Approved commands may include create draft, validate, submit for approval, approve, activate for future use, supersede, and archive.

Requirements:

- owner authorization;
- recent authentication for approval and activation;
- idempotency;
- expected version;
- full schema validation;
- compatibility checks;
- no secret values in canonical JSON;
- evaluation evidence for AI behavior changes;
- risk and execution review for financial-policy changes;
- audit events;
- no mutation after use.

Sprint 12 does not permit changing a running experiment’s frozen configuration.

## 22. Environment Boundary Contract

Supported environments include:

- local;
- CI;
- free cloud demo;
- paper experiment;
- staging;
- production research.

Required fields:

- environment ID and type;
- purpose;
- database and Auth isolation state;
- Gemini project/key separation state;
- domains and CORS profile;
- deployment source;
- live-trading-disabled state;
- private-exchange-credential prohibition state;
- data classification;
- last verification timestamp;
- blockers and limitations.

Cross-environment secret or database reuse is a critical finding unless explicitly approved by policy.

## 23. Secret Inventory Metadata

The workspace may expose only metadata:

- canonical secret name;
- purpose;
- environment;
- storage provider;
- owning service;
- present or missing state;
- created and last rotated timestamp;
- rotation policy and due date;
- access scope;
- exposure or incident state;
- last verification;
- public-build prohibition status.

Secret values, hashes usable for guessing, connection strings, and retrieval links are prohibited.

## 24. Secret Posture States

Supported states include:

- healthy;
- missing;
- due for rotation;
- overdue;
- suspected exposure;
- confirmed exposure;
- rotation in progress;
- revoked;
- mis-scoped;
- found in source;
- found in logs;
- found in frontend artifact;
- verification unavailable.

Suspected or confirmed exposure requires incident and rotation evidence.

## 25. Secret Rotation Evidence

Required rotation fields:

- secret metadata reference;
- trigger;
- incident reference;
- actor;
- start and completion timestamps;
- old credential revocation confirmation;
- new credential verification;
- dependent service restart or deployment;
- smoke-test outcome;
- audit references;
- unresolved limitations.

The workspace never displays old or new values.

## 26. Migration Readiness Contract

Required migration fields:

- migration set or revision;
- source commit;
- target environment;
- current deployed revision;
- expected revision;
- pending migration list;
- immutable applied-history status;
- drift outcome;
- clean-reset outcome;
- forward-apply outcome;
- rehearsal environment and timestamp;
- compatibility window;
- expand-migrate-contract stage where applicable;
- estimated lock or downtime classification;
- rollback or forward-fix strategy;
- backup prerequisite;
- approval and audit references.

Applied migrations must not be edited.

## 27. Migration Gates

Release-blocking migration gates include:

- deterministic migration ordering;
- clean database application;
- existing-schema upgrade;
- drift detection;
- RLS and Auth policy verification;
- constraint and index verification;
- data migration test;
- staging rehearsal for production research;
- application backward or forward compatibility;
- backup and restore prerequisite;
- no destructive change without approved strategy;
- no automatic cloud database deployment before migration CI is approved.

## 28. Security Finding Contract

Required fields:

- finding ID;
- source tool or review;
- category;
- severity;
- status;
- affected artifact, dependency, image, route, configuration, or environment;
- safe description;
- detection timestamp;
- evidence reference;
- owner;
- remediation plan;
- due date;
- verification evidence;
- exception reference;
- incident reference where applicable.

Findings must not be deleted to make a release appear clean.

## 29. Security Evidence Sources

Approved sources may include:

- secret scanning;
- dependency review;
- Python vulnerability scanning;
- frontend vulnerability scanning;
- Bandit;
- Semgrep;
- Trivy filesystem and container scanning;
- SBOM analysis;
- container configuration checks;
- branch-protection verification;
- authentication, authorization, RLS, prompt-injection, ledger, reconciliation, and halt tests;
- manual threat-model review;
- penetration or external review when approved.

Tool absence must be shown as unavailable, not passing.

## 30. Security Exception Contract

A high-severity exception requires:

- immutable exception ID;
- finding reference;
- owner approval;
- business and technical rationale;
- compensating controls;
- scope;
- start and expiry timestamps;
- review cadence;
- remediation owner;
- evidence;
- terminal state.

Critical findings cannot be waived for sandbox or production-research promotion under the baseline policy.

Expired exceptions are release blockers.

## 31. Privacy Data Inventory

The workspace must identify approved data classes such as:

- account identity and membership data;
- audit actor identifiers;
- workspace configuration;
- market and research data;
- Gemini request metadata and validated reports;
- operational logs and diagnostics;
- security incidents;
- exports and backups.

For each class, expose purpose, lawful or policy basis status where documented, source, recipients or providers, retention, deletion behavior, export behavior, sensitivity, and environment scope.

This engineering view does not provide legal certification.

## 32. Data Minimization and Purpose Checks

Required checks include:

- only required identity data is collected;
- Gemini receives minimum structured market evidence;
- secrets and personal data are excluded from prompts;
- logs avoid credentials and unnecessary identifiers;
- telemetry uses bounded safe fields;
- raw provider payload retention is limited;
- exports preserve authorization and minimization;
- public demo uses synthetic or clearly labeled sample data where required;
- production-research user data requires approved review.

## 33. Retention Contract

Retention evidence includes:

- data class;
- default period;
- environment override;
- policy version;
- creation basis;
- archival behavior;
- deletion or anonymization process;
- legal or incident hold state where approved;
- dependent lineage constraints;
- last cleanup run;
- next expected cleanup;
- cleanup verification.

Retention cleanup must not break required financial, decision, experiment, or audit lineage.

## 34. Data Subject and Account Requests

When public user accounts are supported, approved workflows may include access, correction of mutable profile data, export, account closure, and deletion or restriction according to policy.

Requirements:

- identity verification;
- scoped request;
- immutable request record;
- legal or retention constraints;
- separation of mutable profile data from required audit evidence;
- completion evidence;
- safe communication;
- no deletion of records required for integrity without approved policy.

Sprint 12 documents the workflow boundary and does not provide legal advice.

## 35. Provider Terms and Regional Readiness

Required evidence may include:

- provider and service tier;
- current terms review date;
- data-handling classification;
- regional eligibility;
- EEA requirements;
- retention assumptions;
- subprocessors or hosting-region notes where documented;
- production-use approval;
- owner and legal-review status;
- next review due date.

Unknown or stale terms evidence blocks public or production-research promotion according to policy.

## 36. Backup and Restore Readiness

Required fields:

- environment;
- backup or export mechanism;
- encryption status;
- cadence;
- retention;
- last success;
- next expected run;
- failure state;
- artifact integrity hash;
- restore target;
- last restore test;
- migration revision;
- data integrity and ledger reconciliation result;
- measured RPO and RTO where applicable;
- limitations.

A backup is not accepted until restore succeeds.

## 37. Release Candidate Identity

Required fields:

- immutable release ID;
- source branch and commit SHA;
- target environment;
- version or release label;
- creation time;
- creator;
- backend artifact reference and digest;
- frontend artifact reference and digest;
- dependency lock hashes;
- migration set;
- OpenAPI hash;
- SBOM reference and hash;
- configuration compatibility range;
- release-notes reference;
- live-trading-disabled assertion;
- status.

Artifacts are immutable after approval.

## 38. Release Provenance

Required provenance includes:

- Git commit;
- protected-branch state;
- required review results;
- CI workflow and run IDs;
- build environment identity;
- build command and version;
- dependency lock hashes;
- container base image digest where applicable;
- generated artifact hashes;
- OpenAPI and documentation checks;
- SBOM;
- signing or attestation status when implemented;
- source-to-artifact verification.

## 39. Release Gate Categories

Release gates include:

- source and branch protection;
- tests and coverage policy;
- migration and RLS;
- Auth and authorization;
- secret scan;
- static analysis;
- dependency and container vulnerabilities;
- AI validation and prompt-injection safety;
- market data and freshness behavior;
- strategy and risk invariants;
- paper execution and ledger conservation;
- reconciliation and halt enforcement;
- accessibility and visual review;
- documentation and OpenAPI consistency;
- backup and restore;
- incident and rollback readiness;
- privacy and provider terms;
- environment isolation;
- live-trading-disabled verification;
- manual approval.

Every gate exposes version, evidence, outcome, severity, timestamp, and blocker state.

## 40. Promotion Profiles

### Local to Demo

Requires clean bootstrap, migrations, seed, fake-provider cycle, tests, no secrets, and public-build scan.

### Demo to Paper Experiment

Requires dedicated Supabase, Auth, RLS, idempotency, risk, ledger, reconciliation, freshness, observability, export, restore, frozen configuration, and preflight.

### Paper Experiment to Staging

Requires completed post-experiment review, explicit owner decision, release candidate, isolated staging, synthetic data, migration rehearsal, and security/privacy readiness.

### Staging to Production Research

Requires protected CI/CD, managed backup, measured reliability evidence, security and privacy review, incident readiness, manual approval, and authenticated research-only scope.

### Production Research to Binance Test Environment

Out of Sprint 12 scope and requires a separate future specification and approval.

## 41. Release Approval Contract

Required approval fields:

- approval ID;
- release candidate;
- target environment;
- approver;
- approver role;
- recent-authentication evidence;
- gate snapshot hash;
- blockers at decision time;
- decision: approved, rejected, or changes requested;
- reason;
- timestamp;
- expiry or invalidation rule;
- audit reference.

Approval is invalidated by artifact, migration, configuration, or gate changes.

## 42. Deployment Execution Evidence

Required fields:

- deployment ID;
- release candidate;
- target environment;
- workflow or platform run;
- start and finish timestamps;
- actor or automation identity;
- artifact digests;
- migration execution reference;
- health and readiness checks;
- authentication smoke test;
- RLS smoke test;
- API and frontend smoke tests;
- reconciliation and live-trading-disabled checks;
- outcome;
- safe error code;
- rollback reference;
- audit event.

Sprint 12 may present approved deployment evidence but must not expose an unsafe one-click production deployment bypass.

## 43. Rollback Readiness

Required evidence:

- rollback-compatible application artifact;
- migration compatibility strategy;
- database backup or restore prerequisite;
- configuration rollback or supersession plan;
- frontend rollback plan;
- domain halt behavior;
- owner and operator runbook;
- rehearsal result;
- last verified timestamp;
- limitations.

A database rollback must not be assumed safe when migrations are not reversible.

Forward-fix or restore may be the approved strategy.

## 44. Post-Release Verification

Required checks include:

- deployed artifact digests match approval;
- migration revision matches expectation;
- `/health/live` and `/health/ready`;
- Auth sign-in and identity;
- authorization and RLS smoke tests;
- CORS and public frontend configuration;
- no secrets in assets;
- market-data read;
- fake or approved provider smoke test;
- paper mode and live-trading disabled;
- ledger and reconciliation sanity;
- logs and alerts available;
- rollback window and owner acknowledgement.

A failed critical check triggers halt, rollback, or failed release outcome.

## 45. Governance Blocker Contract

Every blocker includes:

- blocker ID;
- category;
- severity;
- scope;
- environment;
- affected workspace, configuration, release, or resource;
- canonical reason code;
- safe explanation;
- evidence;
- owner;
- due date;
- incident or finding reference;
- terminal state.

Critical blockers cannot be hidden or dismissed in the UI.

## 46. Audit and Approval Lineage

The workspace must link immutable events for:

- sign-in and privileged denial;
- membership invitation, role change, and revocation;
- access review;
- configuration creation, validation, approval, activation, supersession, and archive;
- secret exposure and rotation;
- migration rehearsal and execution;
- security finding and exception;
- privacy and retention review;
- backup and restore;
- release creation, gate evaluation, approval, deployment, failure, rollback, and verification.

## 47. Filtering and History

Approved filters may include:

- workspace;
- user and role;
- membership state;
- permission code;
- authorization or RLS outcome;
- configuration lifecycle;
- environment;
- secret posture;
- migration state;
- finding severity and status;
- exception state;
- privacy review status;
- backup or restore outcome;
- release target and state;
- gate outcome;
- approval actor;
- date range;
- correlation ID where authorized.

Filters must be server-approved, authorization-aware, URL-stable where appropriate, and cursor-paginated.

## 48. Export Contract

Authorized exports may include:

- membership and access-review report;
- authorization and RLS assurance report;
- configuration package;
- environment-boundary report;
- secret-posture metadata report;
- migration readiness report;
- security findings and exception report;
- privacy, retention, and provider-term report;
- backup and restore readiness report;
- release candidate, gates, approval, deployment, rollback, and post-release package.

Every export includes schema and generation versions, workspace or release identity, evidence timestamps, blockers, limitations, hashes, approvals, audit references, and authorization context without secrets.

## 49. Page-State Matrix

Explicit states include:

- loading;
- unauthenticated;
- authenticated;
- session expiring;
- recent authentication required;
- account disabled;
- no workspaces;
- no members;
- invitation pending;
- role change pending;
- access verified;
- authorization mismatch;
- RLS mismatch;
- configuration draft;
- configuration rejected;
- approved;
- active;
- frozen;
- superseded;
- secret healthy;
- secret missing;
- rotation due;
- exposure suspected;
- migration current;
- migration pending;
- drift detected;
- rehearsal failed;
- finding open;
- exception expiring;
- privacy review stale;
- backup overdue;
- restore failed;
- release draft;
- release blocked;
- release ready;
- release approved;
- deploying;
- deployed;
- failed;
- rolled back;
- post-release verification failed;
- schema mismatch;
- unauthorized;
- not found;
- backend unavailable;
- command conflict;
- export unavailable.

Critical states must not render as ordinary empty or ready states.

## 50. Responsive Behavior

Requirements:

- identity, environment, effective role, and critical blockers remain first;
- membership and permission matrices provide narrow-layout alternatives;
- configuration diffs retain field, old, new, status, and evidence context;
- secret views display metadata only;
- migration and release gates retain outcome, revision, evidence, and blocker context;
- long IDs, hashes, artifact digests, policy names, and reason codes wrap or copy safely;
- state-changing controls remain separated from evidence;
- no critical content is hover-only;
- dense tables preserve headers and context.

## 51. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- keyboard-accessible filters, tables, disclosures, diffs, timelines, and confirmation dialogs;
- semantic tables with captions and headers;
- accessible definitions for role, permission, RLS, secret, migration, finding, exception, privacy, backup, and release states;
- visible focus;
- status announcements for material asynchronous changes;
- no reliance on color alone;
- reflow at 200% and relevant cases at 400% zoom;
- reduced-motion support;
- screen-reader-readable dates, durations, versions, hashes, severities, and outcomes;
- safe copy controls without exposing secrets.

## 52. Security and Authority Boundaries

The workspace must not:

- expose secret values, tokens, cookies, credentials, private keys, connection strings, or invitation tokens;
- allow arbitrary SQL, shell, workflow, deployment, or environment commands;
- trust browser-calculated permissions, readiness, severity, or approval;
- mutate immutable configuration, migration, audit, financial, experiment, or release evidence;
- grant owner role without authorization, recent authentication, invariant checks, and audit;
- allow runtime use of migration credentials;
- allow browser use of service-role credentials;
- suppress critical findings or expired exceptions;
- approve or deploy changed artifacts under an old approval;
- enable live trading or private Binance credentials;
- expose stack traces, SQL, internal paths, or unrestricted provider payloads.

## 53. Privacy and Data Minimization

The workspace must minimize:

- personal identity display;
- session and device metadata;
- invitation target exposure;
- audit detail outside authorized roles;
- secret inventory information;
- provider-term and incident details;
- raw vulnerability evidence where disclosure increases risk;
- export contents.

Public or shared views must not expose workspace membership or security posture without explicit authorization.

## 54. Observability

Safe telemetry may include:

- authentication outcomes and rate-limit events;
- session expiry and revocation counts;
- membership and role-change outcomes;
- denied authorization attempts by safe category;
- RBAC and RLS verification outcome;
- configuration lifecycle transitions;
- secret posture states without values;
- migration drift and rehearsal outcome;
- findings and exceptions by severity and status;
- privacy and retention review state;
- backup and restore outcomes;
- release gates, approvals, deployments, rollbacks, and smoke-test outcomes;
- command conflicts;
- approved correlation IDs;
- client build version.

Telemetry must not include credentials, tokens, full identities, secret names when unsafe, raw vulnerability payloads, or unrestricted audit details.

## 55. Testing Strategy

### Contract Tests

Validate schemas, enums, timestamps, roles, permission codes, states, severity, hashes, redaction, links, nullability, and compatibility.

### Authentication Tests

Validate login, generic failure, expiry, invalid signature, revocation, disabled account, rate limits, recent authentication, sign-out, and no enumeration.

### Authorization Tests

Validate owner, operator, viewer, service, migration, workflow, and read-only matrices at handler and database layers.

### RLS Tests

Validate anonymous denial, workspace isolation, approved reads, direct-write denial, claim mapping, service-role scope, and API/RLS mismatch fixtures.

### Membership Tests

Validate invitation, expiry, acceptance, role change, owner invariant, revocation, idempotency, expected version, confirmation, and audit.

### Configuration Tests

Validate schema, hash, immutability, lifecycle, evaluation gates, approval, activation, dependency checks, frozen experiments, supersession, and archive.

### Secret Tests

Validate source, log, artifact, frontend, prompt, response, and telemetry scanning; missing, due, exposure, rotation, revocation, and no-value APIs.

### Migration Tests

Validate clean reset, upgrade, drift, applied immutability, RLS, data migrations, compatibility, rehearsal, backup prerequisite, and failure behavior.

### Security and Privacy Tests

Validate finding ingestion, severity, exception expiry, critical-waiver prohibition, data inventory, minimization, retention, cleanup, provider-term freshness, and authorized exports.

### Backup and Restore Tests

Validate cadence, encryption metadata, artifact hashes, isolated restore, migration revision, data integrity, ledger reconciliation, measured recovery evidence, and visible failure.

### Release Tests

Validate artifact provenance, digests, locks, SBOM, gates, approval invalidation, deployment evidence, smoke tests, rollback readiness, post-release checks, and live-trading-disabled assertion.

### Accessibility Tests

Validate keyboard flow, headings, tables, matrices, diffs, confirmations, definitions, focus, announcements, copy controls, zoom, reflow, and contrast.

### Visual Regression

Capture unauthenticated, session-expiry, membership, RLS mismatch, configuration states, secret exposure, migration drift, findings, expired exceptions, privacy stale, restore failure, release blocked, approved, deploying, failed, rolled-back, and verification-failure states.

### Export Tests

Validate authorization, redaction, provenance, blockers, approvals, hashes, limitations, and prohibited-field absence.

## 56. Acceptance Criteria

Sprint 12 documentation is accepted when:

1. account, session, workspace, membership, role, and effective-permission evidence is explicit;
2. application RBAC and database RLS are independently verified and mismatches fail closed;
3. membership and role changes are owner-authorized, idempotent, version-guarded, invariant-checked, and audited;
4. used configuration versions are immutable and active experiments remain frozen;
5. secret inventory exposes metadata only and exposure or overdue rotation creates blockers;
6. applied migrations remain immutable and drift, rehearsal, compatibility, backup, and RLS gates are explicit;
7. security findings and exceptions remain discoverable, with no critical waiver and time-limited high exceptions;
8. privacy, minimization, retention, provider terms, and regional readiness are evidence-backed and explicitly non-legal certification;
9. backup readiness requires successful isolated restore and reconciliation;
10. release candidates identify immutable artifacts, provenance, migrations, OpenAPI, SBOM, gates, approvals, deployment, smoke tests, rollback, and verification;
11. approvals are invalidated by artifact or gate changes;
12. every environment preserves live-trading-disabled and private-exchange-credential prohibition state;
13. no secret display, arbitrary SQL, browser service role, silent escalation, automatic approval, critical-finding suppression, or unsafe deploy bypass is introduced;
14. security, privacy, accessibility, observability, authentication, authorization, RLS, migration, backup, and release tests are explicit.

## 57. Definition of Done

The Sprint 12 specification is complete when:

- this document is committed;
- `SPRINT_12_TASKS.md` is committed;
- terminology matches security, deployment, database, API, cloud MVP, experiments, audit, Gemini, portfolio, testing, and production-development documents;
- all account, session, membership, permission, RLS, configuration, environment, secret, migration, finding, exception, privacy, retention, provider, backup, release, approval, deployment, rollback, accessibility, and authority states are explicit;
- both commits are fetched and verified.

## 58. Next Sprint Boundary

Sprint 13 defines the **Product Shell, Onboarding, Help, Trust Center, Global Search, Notifications, Internationalization, and Cross-Workspace Experience**, including route discovery, first-run setup, simulation education, contextual definitions, user-facing status notices, saved views, accessible global navigation, Estonian and English content governance, support and incident communication, and coherent cross-resource lineage without adding financial or operational authority.
