# Sprint 16 Tasks — Data Lifecycle, Dataset Registry, Quality, Retention, Archival, Export, Deletion, Anonymization, and Reproducibility Preservation Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a server-authoritative data-governance workspace that registers immutable dataset versions, validates quality and lineage, tracks downstream dependencies, applies retention and evidence holds, verifies archive restore, plans bounded deletion and anonymization, separates account data from immutable evidence, and preserves reproducibility manifests without silently rewriting, exposing, publishing, or deleting integrity-critical data.

## Authoritative References

- `docs/DATA_LIFECYCLE_DATASET_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/MARKET_DATA.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/MARKET_EVIDENCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/GEMINI_ANALYSIS_VALIDATION_WORKSPACE_IMPLEMENTATION.md`
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`
- `docs/BACKTEST_EXPERIMENT_COMPARISON_WORKSPACE_IMPLEMENTATION.md`
- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `docs/AUTH_CONFIGURATION_SECURITY_RELEASE_WORKSPACE_IMPLEMENTATION.md`
- `docs/PERFORMANCE_RESILIENCE_CAPACITY_FINOPS_WORKSPACE_IMPLEMENTATION.md`
- `docs/DEVELOPER_PORTAL_DOCUMENTATION_TRACEABILITY_WORKSPACE_IMPLEMENTATION.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `AGENTS.md`

## S16.1 Define Versioned Data-Governance Schemas

### Objective

Create explicit contracts for dataset identity, versions, classification, manifests, schemas, provenance, transformations, lineage, quality, dependencies, retention, holds, archives, deletion, anonymization, reproducibility, access, diagnostics, permissions, and links.

### Work

- define `DatasetGovernanceReadModel` and nested schemas;
- define reproducibility-manifest and deletion-plan models;
- define lifecycle, quality, archive, deletion, anonymization, access, and verification states;
- define hashes, record counts, byte sizes, periods, source quality, and limitations;
- publish schemas in OpenAPI;
- generate frontend types.

### Acceptance Criteria

- every data-governance state is machine-readable;
- destructive eligibility is server-provided;
- schemas contain no secret storage URLs;
- compatibility and nullability are versioned;
- contract tests pass.

## S16.2 Implement Dataset Registry Endpoint

### Objective

Expose bounded, filterable dataset history across authorized workspaces and environments.

### Work

- implement dataset list endpoint;
- support filters for type, classification, workspace, environment, lifecycle, quality, retention, hold, archive, access, source, schema, and date;
- use cursor pagination and safe sort options;
- include current version, manifest, dependency, and blocker summaries;
- enforce authorization and RLS;
- add safe telemetry.

### Acceptance Criteria

- unauthorized dataset existence is not leaked;
- archived, invalidated, superseded, and deleted tombstones remain discoverable by authorized roles;
- filters are bounded;
- pagination is deterministic;
- API tests pass.

## S16.3 Implement Dataset Detail Endpoint

### Objective

Return the complete dataset-governance projection.

### Work

- implement dataset and version detail projections;
- return identity, classification, manifest, quality, lineage, dependencies, retention, holds, archive, deletion, anonymization, reproducibility, access, diagnostics, limitations, permissions, and links;
- classify missing required evidence;
- enforce role-specific redaction;
- map safe errors.

### Acceptance Criteria

- identical persisted evidence produces the same response;
- missing quality or lineage fails closed;
- secret storage details are absent;
- command permissions are server-authoritative;
- integration tests pass.

## S16.4 Implement Data-Governance Routes

### Objective

Add dataset, version, lineage, quality, retention, archive, export, deletion, anonymization, hold, cleanup, reproducibility, and access routes.

### Work

- implement the approved canonical route family;
- add product-shell navigation and cross-links;
- preserve filters in URL state;
- add route-level error boundaries;
- separate evidence routes from destructive commands;
- enforce authorization at route and API layers.

### Acceptance Criteria

- routes are directly addressable and keyboard reachable;
- destructive controls appear only with server permission;
- invalid IDs fail safely;
- refresh preserves stable read state;
- route tests pass.

## S16.5 Implement Dataset Identity and Safety Header

### Objective

Present classification, environment, quality, retention, hold, access, archive, and lifecycle state before storage metrics.

### Work

- render dataset/version IDs, type, workspace, environment, owner, schema, manifest hash, period, record count, lifecycle, quality, retention, hold, archive, public/private, and incident state;
- apply canonical status priority;
- expose local time and UTC;
- preserve critical state on mobile;
- link evidence.

### Acceptance Criteria

- invalid, quarantined, held, or deletion-blocked state cannot appear ordinary;
- hashes and versions are inspectable;
- storage savings never dominate integrity state;
- public/private classification is explicit;
- accessibility tests pass.

## S16.6 Implement Canonical Dataset-Type Registry

### Objective

Define approved types for market, AI, strategy, risk, execution, ledger, portfolio, backtest, experiment, audit, operations, security, test, documentation, account, and public-demo evidence.

### Work

- assign stable type codes;
- map each type to schema, classification, owner, quality rules, retention profile, access profile, and lineage expectations;
- detect unknown types;
- preserve deprecation;
- link developer catalogs.

### Acceptance Criteria

- every dataset maps to one registered type;
- secret material cannot be a normal type;
- type changes require versioning;
- deprecated types remain readable;
- registry tests pass.

## S16.7 Implement Data Classification Registry

### Objective

Apply public, internal, restricted operational, restricted financial, restricted security, personal, secret, and prohibited-persistence classifications.

### Work

- define classification codes and rules;
- map dataset types and fields;
- define access, export, retention, anonymization, and publication impacts;
- detect secret or prohibited content;
- create incidents for violations;
- preserve review evidence.

### Acceptance Criteria

- secret material cannot be listed as healthy data;
- classification impacts are enforced server-side;
- public status requires separate approval;
- violations fail closed;
- classification tests pass.

## S16.8 Implement Immutable Dataset Versions

### Objective

Persist parentage, schema, sources, transformation, configuration, manifests, hashes, counts, size, range, job, quality, approval, retention, and access.

### Work

- implement version storage and unique constraints;
- calculate deterministic content hashes;
- prevent update/delete after use;
- create successor versions for changes;
- link invalidation and supersession;
- add audit events.

### Acceptance Criteria

- used versions are immutable;
- identical ordered content produces the same hash;
- changed content produces a new version;
- parent and successor relationships are complete;
- property tests pass.

## S16.9 Implement Dataset Lifecycle State Machine

### Objective

Govern registering, ingesting, validating, quarantined, approved, active, frozen, correction, invalidated, superseded, archived, and deleted states.

### Work

- define valid transitions and actors;
- require expected version, reason, evidence, and audit;
- enforce downstream-use restrictions;
- preserve transition history;
- reject ambiguous or repeated transitions idempotently.

### Acceptance Criteria

- invalid transitions fail deterministically;
- quarantined and invalidated versions cannot become normal inputs;
- historical transitions are immutable;
- repeated commands do not duplicate transitions;
- state-machine tests pass.

## S16.10 Implement Record Manifest Generation

### Objective

Create ordered partition/object manifests and aggregate integrity hashes.

### Work

- define record identity and ordering by type;
- record partitions, time range, count, bytes, schema, hashes, serialization, compression, encryption metadata, storage tier, source, and verification;
- support large datasets without loading all data in memory;
- prohibit signed URLs and credentials;
- generate verification tools.

### Acceptance Criteria

- aggregate hashes are deterministic;
- counts reconcile with partitions;
- secret storage details are absent;
- verification detects corruption;
- manifest tests pass.

## S16.11 Implement Schema and Serialization Registry

### Objective

Version fields, types, units, nullability, constraints, decimal, timezone, ordering, compatibility, and migration guidance.

### Work

- connect OpenAPI/JSON Schema, Python, TypeScript, and storage representations;
- calculate schema hashes;
- define compatibility rules;
- detect drift;
- link tests and transformations;
- preserve deprecations.

### Acceptance Criteria

- schema drift cannot hide inside a dataset label;
- decimals and timestamps remain canonical;
- breaking changes require new versions;
- generated types match schemas;
- schema tests pass.

## S16.12 Implement Source Provenance Registry

### Objective

Trace provider, adapter, request/job, timestamps, records, server time, code, dependencies, migrations, actor, correlations, and hashes.

### Work

- persist bounded source references;
- support Binance, Supabase, Gemini, imports, workflows, and generated sources;
- preserve provider clock evidence where relevant;
- redact private request details;
- validate source completeness;
- link incidents.

### Acceptance Criteria

- every dataset version has source provenance;
- missing required source evidence is critical;
- provider and application timestamps remain distinct;
- secrets are absent;
- provenance tests pass.

## S16.13 Implement Transformation Registry

### Objective

Record exact inputs, outputs, code, configuration, determinism, seeds, environment, quality, warnings, and hashes.

### Work

- define transformation IDs and versions;
- support ingestion, snapshot, features, validation, benchmark, export, archive, and anonymization transformations;
- distinguish probabilistic Gemini provider output from validated project data;
- persist run evidence;
- enforce immutable outputs.

### Acceptance Criteria

- each derived dataset lists exact input versions;
- deterministic transforms reproduce hashes;
- probabilistic steps expose limitations;
- output quality is linked;
- transformation tests pass.

## S16.14 Implement Dataset Lineage Graph and Table

### Objective

Expose source, validation, transformation, snapshot, feature, analysis, decision, execution, accounting, benchmark, invalidation, archive, and export relationships.

### Work

- define typed relationship codes;
- render graph and ordered table alternatives;
- preserve version, direction, timestamp, status, and authorization;
- detect cycles and missing required relationships;
- support resource-centered traversal;
- link product lineage navigator.

### Acceptance Criteria

- one report can be traced to source data and transformations;
- unauthorized nodes do not leak existence;
- missing required lineage is critical;
- graphs have accessible alternatives;
- lineage tests pass.

## S16.15 Implement Data Quality Rule Registry

### Objective

Version quality conditions, tolerance, severity, failure, quarantine, tests, and ownership.

### Work

- define stable rule IDs;
- group rules by dataset type;
- connect validator implementation and tests;
- support activation and deprecation;
- prevent rule changes from rewriting old outcomes;
- expose definitions.

### Acceptance Criteria

- every approved dataset type has required rules;
- validator changes create a new version;
- critical failures have deterministic behavior;
- rules link to tests;
- registry tests pass.

## S16.16 Implement Market Data Quality Rules

### Objective

Validate prices, OHLC, volume, close time, intervals, symbols, finalization, uniqueness, ordering, gaps, clock drift, precision, and hashes.

### Work

- implement property and integration validators;
- use exchange server time;
- reject unrecognized metadata versions;
- persist gap and correction evidence;
- block stale or unfinalized inputs;
- expose failed records safely.

### Acceptance Criteria

- invalid candles never feed normal workflows;
- duplicates and ordering errors are deterministic;
- gap detection and repair are traceable;
- precision remains decimal-safe;
- quality tests pass.

## S16.17 Implement Derived Data Quality Rules

### Objective

Validate snapshots, features, Gemini evidence, strategy/risk inputs, accounting, benchmarks, and hashes.

### Work

- verify exact input references;
- validate warm-up, null/finite values, alignment, formulas, no look-ahead, schema, grounding, input completeness, ledger/reconciliation, and period compatibility;
- persist warnings and failures;
- link downstream invalidation;
- add deterministic fixtures.

### Acceptance Criteria

- future-data dependency fails validation;
- ungrounded Gemini evidence is rejected;
- unreconciled financial data is not approved;
- benchmark mismatch is visible;
- tests pass.

## S16.18 Implement Quality Run Endpoint and Workspace

### Objective

Expose rule-set, checks, counts, mode, failures, quarantine, approval, artifacts, and limitations.

### Work

- implement quality-run list and detail projections;
- support sample and full-scan modes;
- render rule outcomes and safe failed-record references;
- calculate final quality state server-side;
- link dataset lifecycle and incidents;
- add export.

### Acceptance Criteria

- missing checks cannot yield approved state;
- sample mode is explicit;
- critical failures trigger quarantine;
- results are revision-linked;
- API and accessibility tests pass.

## S16.19 Implement Quarantine Workflow

### Objective

Restrict invalid or suspicious data and track remediation.

### Work

- persist quarantine ID, scope, reasons, detection, source, affected resources, access, owner, decision, state, audit, and incident;
- block normal downstream consumption;
- support correction, rejection, or approved-with-limitations outcomes;
- preserve original evidence;
- add authorization tests.

### Acceptance Criteria

- quarantined data cannot feed strategy, risk, execution, reporting, or benchmark paths;
- remediation is explicit;
- original evidence is immutable;
- unauthorized access fails closed;
- workflow tests pass.

## S16.20 Implement Source Correction Detection and Propagation

### Objective

Preserve originals while versioning corrections and marking dependent artifacts.

### Work

- detect changed finalized records;
- create correction evidence and new source version;
- query dependency registry;
- invalidate or supersede snapshots, features, reports, decisions, backtests, and summaries according to policy;
- preserve financial and audit history;
- create incident where material.

### Acceptance Criteria

- original records are never overwritten;
- affected dependencies are complete;
- financial history is not recalculated silently;
- recomputation is explicit and versioned;
- propagation tests pass.

## S16.21 Implement Dependency Registry

### Objective

Track exact source/target versions, relationship, criticality, retention, deletion, and invalidation impact.

### Work

- persist dependency edges;
- enforce unique and required relationships;
- calculate downstream dependency closure server-side;
- detect missing, stale, or circular edges;
- link traceability and reproducibility;
- expose filters.

### Acceptance Criteria

- unknown dependency state blocks deletion;
- required missing relationships are critical;
- closure is deterministic;
- authorization is enforced;
- property tests pass.

## S16.22 Implement Dataset Promotion Workflow

### Objective

Approve validated versions for normal research use without affecting frozen experiments silently.

### Work

- require manifest, schema, quality, lineage, privacy, retention, access, environment, secret scan, and approval evidence;
- implement idempotent, expected-version transition;
- preserve limitations;
- block active-experiment replacement;
- audit promotion.

### Acceptance Criteria

- incomplete datasets cannot be promoted;
- approved version is immutable;
- active experiments retain frozen inputs;
- secret/prohibited data blocks promotion;
- workflow tests pass.

## S16.23 Implement Public Dataset Promotion Gate

### Objective

Require classification, privacy, license, delay/aggregation, security, documentation, and reproducibility evidence.

### Work

- define public-promotion checks;
- scan personal and secret content;
- verify provider redistribution terms;
- require public schema, limitations, and owner approval;
- create immutable published version;
- prohibit direct internal-to-public transition.

### Acceptance Criteria

- internal accessibility never implies public status;
- failed privacy or license review blocks publication;
- published version is immutable;
- public exports are minimized;
- security tests pass.

## S16.24 Implement Retention Policy Registry

### Objective

Version active, archive, deletion, cleanup, hold, lineage, personal-data, incident, and review rules.

### Work

- define stable policy IDs;
- map data classes, dataset types, environments, periods, schedules, holds, constraints, owner, approval, dates, and limitations;
- preserve historical application;
- prevent implicit default deletion;
- expose review status.

### Acceptance Criteria

- every dataset has an applied policy or explicit blocker;
- policy changes do not rewrite old cleanup evidence;
- actual periods come from configuration;
- overdue reviews are visible;
- registry tests pass.

## S16.25 Implement Evidence Hold Registry and Commands

### Objective

Prevent archive or deletion while experiments, incidents, audits, releases, corrections, privacy reviews, or reproducibility require evidence.

### Work

- implement hold create, review, extend, and release workflows;
- require authorized role, reason, scope, start, review, expiry/indefinite state, affected policies, release conditions, and audit;
- calculate effective holds server-side;
- preserve expired and released history;
- prohibit silent override.

### Acceptance Criteria

- active hold blocks destructive action;
- release requires documented conditions;
- duplicate commands are idempotent;
- expired state is explicit;
- hold tests pass.

## S16.26 Implement Cleanup Dry-Run Engine

### Objective

Preview candidates, exclusions, dependencies, actions, records, bytes, and blockers before execution.

### Work

- evaluate policy and current time;
- query holds and dependencies;
- classify archive, anonymize, delete, skip, and fail candidates;
- calculate expected counts and bytes;
- persist immutable dry-run snapshot and hash;
- expose safe preview.

### Acceptance Criteria

- destructive cleanup requires a completed dry run;
- candidates are bounded and reproducible;
- active holds and unknown dependencies are excluded;
- preview contains no sensitive payloads;
- reference tests pass.

## S16.27 Implement Cleanup Execution Workflow

### Objective

Execute approved archive, anonymization, and deletion actions idempotently and audibly.

### Work

- require owner authorization, recent authentication, idempotency, expected version, exact dry-run hash, approvals, confirmation, and stop conditions;
- process bounded batches;
- persist counts, bytes, failures, skips, integrity checks, audit, and outcome;
- prevent arbitrary targets;
- support safe retry.

### Acceptance Criteria

- stale dry-run plans cannot execute;
- repeated commands do not duplicate actions;
- failures preserve partial evidence and stop rules;
- integrity is checked after execution;
- workflow tests pass.

## S16.28 Implement Archive Registry and Tiering

### Objective

Track active, warm, cold, offline, and tombstone tiers with integrity and access semantics.

### Work

- define archive ID, source/target tiers, manifest, hash, compression, encryption metadata, access, timestamp, restore runbook, retention, hold, cost, verification, and audit;
- preserve dataset identity;
- prohibit secret URLs;
- support filters and status;
- link FinOps evidence.

### Acceptance Criteria

- archival never changes dataset identity;
- integrity hash is preserved;
- access is authorization-controlled;
- restore procedure is present;
- registry tests pass.

## S16.29 Implement Archive Restore Verification

### Objective

Prove archived evidence is recoverable in an isolated environment.

### Work

- restore manifest and data into approved target;
- verify records, bytes, hashes, schema, migrations, quality, lineage, and financial reconciliation;
- persist timing, outcome, failures, and limitations;
- preserve source archive;
- link runbook and release gates.

### Acceptance Criteria

- archive readiness requires successful restore;
- restore never targets production research directly;
- financial evidence reconciles;
- failed restores remain critical;
- tests pass.

## S16.30 Implement Deletion Eligibility Engine

### Objective

Determine whether a bounded target is deletable, archivable, anonymizable, or prohibited.

### Work

- evaluate classification, retention, holds, dependencies, reproducibility, integrity evidence, account separation, provider/license, archive, approvals, and environment;
- return blockers and alternatives;
- version rules;
- fail closed on unknown state;
- expose evidence.

### Acceptance Criteria

- unknown dependencies block deletion;
- prohibited financial/audit categories remain protected;
- alternatives are explicit;
- result is deterministic;
- reference tests pass.

## S16.31 Implement Deletion Plan and Preview

### Objective

Create immutable bounded plans with dependencies, blockers, archive, anonymization, counts, bytes, approvals, and stop conditions.

### Work

- implement plan creation and read model;
- calculate exact plan hash;
- require dry run;
- display rollback limitations;
- preserve rejected and expired plans;
- link policy and audit.

### Acceptance Criteria

- arbitrary table/path input is impossible;
- plan target is immutable;
- counts and dependencies are inspectable;
- changed evidence invalidates the plan;
- plan tests pass.

## S16.32 Implement Guarded Deletion Command

### Objective

Execute only an approved immutable plan under strict authorization.

### Work

- require owner, recent auth, idempotency, expected version, plan hash, completed dry run, no blockers/holds, archive/restore prerequisites, confirmation, bounded execution, and audit;
- reject stale plans;
- process deterministic batches;
- stop on integrity failure;
- create execution evidence.

### Acceptance Criteria

- protected evidence cannot be deleted;
- duplicate requests are idempotent;
- stale or altered plans fail;
- browser cannot provide arbitrary targets;
- security tests pass.

## S16.33 Implement Deletion Tombstones and Proof

### Objective

Preserve non-sensitive identity, policy, counts, hashes, actor, reason, and surviving-dependency evidence.

### Work

- generate tombstone and proof after execution;
- store original IDs, schema/manifest hashes, counts, timestamp, policy, actor, proof hash, redirects, and visibility;
- avoid deleted payload retention;
- verify post-delete dependencies and RLS;
- support authorized export.

### Acceptance Criteria

- deletion is auditable without retaining deleted sensitive data;
- tombstones cannot be rewritten;
- proof hashes verify;
- dangling dependencies are detected;
- tests pass.

## S16.34 Implement Anonymization Plan and Validation

### Objective

Apply removal, tokenization, pseudonymization, generalization, aggregation, noise, or suppression with re-identification review.

### Work

- define source, purpose, fields, technique, key boundary, utility, risk method, preview, approvals, output, and limitations;
- validate direct/quasi-identifiers, rare groups, linkage, free text, timestamps, reversible tokens, and public suitability;
- create a new output dataset version;
- preserve source access restrictions;
- avoid false anonymization claims.

### Acceptance Criteria

- pseudonymization remains labeled reversible where applicable;
- high re-identification risk blocks public promotion;
- validation is versioned;
- output lineage is complete;
- privacy tests pass.

## S16.35 Implement Account Data Separation

### Objective

Allow mutable profile correction or closure without rewriting immutable operational evidence.

### Work

- use stable bounded actor references;
- separate profile display fields from audit/approval records;
- remove deleted profile data from search, notifications, support packages, and caches;
- restrict re-identification access;
- define account export and closure effects;
- test required-history preservation.

### Acceptance Criteria

- account closure does not erase financial/audit integrity;
- mutable profile data can be corrected according to policy;
- stale profile data is purged from derived user-facing stores;
- access is minimized;
- tests pass.

## S16.36 Implement Reproducibility Manifest Registry

### Objective

Preserve every dataset, schema, configuration, code, dependency, migration, provider, seed, model, policy, and expected hash needed for research reproduction.

### Work

- implement manifest list/detail;
- support backtest, experiment, report, release, and evaluation targets;
- calculate manifest hash;
- map retention requirements;
- detect missing resources;
- preserve immutable versions.

### Acceptance Criteria

- every final research report maps to a manifest;
- required dataset versions are exact;
- code and dependency identities are present;
- missing inputs make the manifest incomplete;
- registry tests pass.

## S16.37 Implement Reproducibility Verification

### Objective

Verify manifests, hashes, schemas, code, dependencies, migrations, configurations, events, outputs, and archived restores.

### Work

- implement verified, limited, mismatch, incomplete, and unavailable outcomes;
- compare partition and aggregate hashes;
- validate compatibility and expected outputs;
- link repeated runs and restore evidence;
- expose machine-readable differences;
- preserve original evidence.

### Acceptance Criteria

- approximate display cannot hide mismatch;
- verified requires all mandatory checks;
- limitations are explicit;
- archived data must restore and verify;
- reproducibility tests pass.

## S16.38 Implement Dataset Access Assurance

### Objective

Expose classification, permissions, RLS/storage policies, purpose, export, public, recent-auth, review, and findings.

### Work

- define canonical permission codes;
- verify workspace/environment isolation;
- test dataset reads, exports, archives, deletion, and public access;
- detect RLS/storage mismatch;
- minimize details by role;
- link governance assurance.

### Acceptance Criteria

- access does not imply deletion or publication;
- unauthorized datasets do not leak existence;
- policy mismatch is critical;
- direct storage access is prohibited for browsers;
- tests pass.

## S16.39 Implement Environment Data-Boundary Verification

### Objective

Ensure CI, public demo, local, experiment, staging, and production research use approved data classes.

### Work

- verify synthetic/public fixtures in CI;
- verify public/sample/delayed data in demo;
- prevent production credentials/personal data in local and staging;
- require manifest and approval for cross-environment copies;
- scan copied content;
- preserve audit evidence.

### Acceptance Criteria

- production data does not enter CI;
- cross-environment copies are traceable;
- secrets never become dataset content;
- violations create incidents;
- boundary tests pass.

## S16.40 Implement Provider Request Data-Minimization Assurance

### Objective

Verify Gemini and other provider requests use approved minimum structured evidence and bounded retention.

### Work

- map request fields to purpose and schema;
- scan for credentials, personal data, raw logs, and unrestricted rows;
- verify provider terms and regional readiness;
- persist request hash and source references;
- verify raw-response retention policy;
- link analyses and incidents.

### Acceptance Criteria

- prohibited fields block provider request;
- only approved evidence is sent;
- raw payload retention is bounded;
- secrets are never transmitted;
- privacy tests pass.

## S16.41 Implement Test and Fixture Dataset Governance

### Objective

Ensure tests use synthetic or public-approved deterministic data.

### Work

- register fixture IDs, schemas, hashes, source, size, provider class, retention, and update policy;
- scan for personal, production, financial, and secret payloads;
- validate quality;
- link tests and revisions;
- preserve deprecated fixtures.

### Acceptance Criteria

- ordinary CI uses no production data;
- fixtures are deterministic and bounded;
- secret scans pass;
- provider classification is explicit;
- tests pass.

## S16.42 Implement Data Drift Detection

### Objective

Detect schema, distribution, missingness, metadata, feature, provider, quality, label, retention, and access-policy drift.

### Work

- define baseline, current window, method, sample, severity, limitation, and review;
- return insufficient data safely;
- link affected datasets and configurations;
- create notices or incidents by policy;
- preserve historical drift evidence.

### Acceptance Criteria

- methods are versioned;
- insufficient samples do not create confident drift;
- critical schema/access drift blocks use;
- findings link to evidence;
- drift tests pass.

## S16.43 Implement Data Incident Workflow

### Objective

Handle corrections, contamination, missing lineage, prohibited data, leakage, restore, deletion, reproducibility, and quality-bypass incidents.

### Work

- define categories and severity;
- link datasets, downstream resources, containment, invalidation, correction, recovery, holds, and audit;
- preserve unresolved incidents;
- block promotion and deletion where applicable;
- link runbooks.

### Acceptance Criteria

- incidents cannot be removed to clean reports;
- affected dependencies are traceable;
- containment state is explicit;
- resolution requires verification;
- integration tests pass.

## S16.44 Implement Authorized Data Export and Integrity Package

### Objective

Generate manifests, quality, lineage, retention, hold, archive, reproducibility, deletion, anonymization, account, and public packages.

### Work

- generate server-side;
- include schema/generation versions, identity, hashes, source, period, counts, classification, quality, lineage, retention, holds, access, limitations, and authorization context;
- include package manifest, file list, compression/encryption metadata, purpose, expiry, verification, and restore test;
- enforce role-specific minimization;
- prohibit secret URLs.

### Acceptance Criteria

- exports identify exact dataset version;
- critical quality and hold state cannot be omitted;
- packages verify by hash;
- private data is minimized;
- export tests pass.

## S16.45 Implement Safe External Data Import Boundary

### Objective

Quarantine and validate approved bounded external imports before use.

### Work

- require type, schema, size/range bounds, source/license, malware/content scan, secret/personal scan, classification, manifest, hashes, quality, environment, and approval;
- prohibit arbitrary storage path or SQL imports;
- preserve import job and audit;
- create quarantined version first;
- link incidents.

### Acceptance Criteria

- external data cannot enter normal workflows before approval;
- unsafe or oversized imports fail;
- source and license metadata are present;
- secrets and malware are blocked;
- security tests pass.

## S16.46 Add Explicit State Handling

### Objective

Define safe rendering for every lifecycle, quality, retention, archive, deletion, anonymization, reproducibility, and access state.

### Work

- implement loading, empty, registering, ingesting, validating, quarantined, approved, limited, active, frozen, correction, invalidated, superseded, archive pending/archived, restore running/failed, retention due, hold, cleanup dry run/failed, deletion blocked/pending/completed, anonymization pending/failed, reproducibility verified/mismatch, lineage incomplete, quality unavailable, schema mismatch, denied, unavailable, and export failure states;
- define bounded retries;
- distinguish missing evidence from healthy;
- label cached evidence by version.

### Acceptance Criteria

- missing quality or lineage never appears approved;
- destructive conflicts preserve server state;
- stale evidence is explicit;
- unauthorized state reveals no dataset existence;
- state-matrix tests pass.

## S16.47 Add Responsive and Accessibility Verification

### Objective

Ensure manifests, lineage, quality, dependencies, plans, previews, and confirmations are usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom;
- test headings, landmarks, tables, trees, lineage alternatives, diffs, previews, confirmations, filters, focus, announcements, definitions, and copy controls;
- verify reduced motion and contrast;
- test long hashes, schema IDs, partitions, policies, and reason codes;
- record screen-reader spot checks.

### Acceptance Criteria

- graphs have equivalent table/text views;
- destructive confirmations are fully accessible;
- no state relies only on color;
- context survives narrow layouts;
- no critical automated violation remains;
- manual evidence is recorded.

## S16.48 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make immutable versions, quality, lineage, holds, archive restore, deletion safety, anonymization honesty, access, and reproducibility release-blocking.

### Work

- add contract, registry, version, manifest, schema, provenance, transformation, lineage, quality, quarantine, correction, dependency, promotion, retention, hold, cleanup, archive, restore, eligibility, deletion, tombstone, anonymization, account, reproducibility, access, environment, provider, fixture, drift, incident, import, route, E2E, accessibility, visual, export, authorization, and RLS tests;
- add secret, signed-URL, arbitrary-target, SQL, storage, public-leak, prohibited-delete, false-anonymization, production-data, and live-trading checks;
- instrument safe lifecycle and outcome metrics;
- test prohibited telemetry fields;
- link critical failures to release gates.

### Acceptance Criteria

- invalid/quarantined data cannot feed normal workflows;
- held or integrity-critical evidence cannot be deleted;
- no browser or AI path gains arbitrary SQL/storage, quality-bypass, publication, deletion, provider, private exchange, testnet, or live-trading authority;
- telemetry contains no prohibited fields;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Contracts and registry | Dataset, type, classification, version, manifest, schema, lifecycle, access, permission, and API tests |
| Provenance and lineage | Source, transformation, dependencies, graph/table, correction propagation, invalidation, reproducibility, and traceability tests |
| Quality | Market, derived, rule registry, full/sample runs, quarantine, promotion, stale, schema, no-look-ahead, grounding, ledger, and benchmark tests |
| Lifecycle | Retention, holds, cleanup dry-run/execution, archive tiers, restore, incident, and audit tests |
| Deletion and privacy | Eligibility, prohibited categories, plans, recent auth, idempotency, confirmation, tombstone, proof, anonymization, account separation, public promotion, and import tests |
| Reproducibility | Manifests, dataset/partition hashes, schemas, code, dependencies, migrations, configurations, seeds, provider evidence, outputs, and restore tests |
| Security and accessibility | RLS, storage policies, environment boundaries, provider minimization, fixture scans, exports, keyboard, lineage alternatives, zoom, confirmations, and telemetry tests |

## Sprint Exit Gate

Sprint 16 is complete only when:

- S16.1 through S16.48 are implemented and verified;
- every dataset has immutable identity, version, schema, manifest, hash, classification, quality, retention, access, and lineage evidence;
- used versions cannot be mutated;
- provenance includes exact source, transformation, code, configuration, dependency, migration, job, and input versions;
- quality rules are versioned and invalid, stale, contaminated, ungrounded, unreconciled, or lineage-incomplete data fails closed;
- source corrections preserve originals and propagate invalidation without rewriting financial history;
- retention, holds, cleanup, archive, deletion, and anonymization decisions are server-authoritative and audited;
- archive readiness requires isolated restore, quality, lineage, and financial reconciliation;
- unknown dependencies or active holds block deletion;
- required financial, risk, ledger, reconciliation, experiment, audit, incident, security, and release evidence cannot be silently deleted;
- deletion requires immutable plan, dry run, recent authentication, idempotency, expected version, approval, bounded execution, tombstone, and proof;
- pseudonymization is never misrepresented as anonymization;
- account profile data remains separable from immutable actor and audit references;
- reproducibility manifests preserve exact datasets, schemas, configurations, code, dependencies, migrations, provider evidence, seeds, policies, and expected hashes;
- public promotion and external imports require separate privacy, license, quality, security, and approval gates;
- no browser or AI arbitrary SQL/storage, signed-URL, quality-bypass, publication, deletion, import, private exchange, testnet, or live-trading authority exists;
- accessibility, responsive, security, privacy, contract, registry, quality, lineage, retention, archive, deletion, anonymization, reproducibility, access, import, E2E, export, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 17 defines and implements the Research Review, Strategy Lifecycle, Evidence Scoring, Decision Governance, and Promotion Workspace.
