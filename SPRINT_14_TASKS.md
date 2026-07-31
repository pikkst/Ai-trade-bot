# Sprint 14 Tasks — Developer Portal, API Explorer, Documentation System, Test Evidence, Runbook Library, and Implementation Traceability Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement an authenticated engineering-evidence portal and approved public documentation subset that connects authoritative documents, requirements, sprint tasks, ADRs, APIs, schemas, errors, events, permissions, metrics, source files, migrations, tests, invariants, runbooks, release artifacts, and deployment verification while detecting stale, conflicting, incomplete, drifted, or unsafe evidence in CI.

## Authoritative References

- `docs/DEVELOPER_PORTAL_DOCUMENTATION_TRACEABILITY_WORKSPACE_IMPLEMENTATION.md`
- `AGENTS.md`
- `docs/TESTING.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/ARCHITECTURE.md`
- `docs/LOCAL_DEVELOPMENT.md`
- `docs/TEST_ENVIRONMENTS.md`
- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/DEPLOYMENT.md`
- `docs/SECURITY.md`
- `docs/OBSERVABILITY.md`
- `docs/NAMING_CONVENTIONS.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- all sprint task files and workspace implementation specifications

## S14.1 Define Versioned Developer Portal Schemas

### Objective

Create explicit contracts for repository revision, documentation catalog, API catalog, traceability, tests, runbooks, ADRs, documentation health, blockers, permissions, diagnostics, and links.

### Work

- define `DeveloperPortalReadModel` and nested schemas;
- define traceability-item and documentation-health models;
- define catalogs for documents, requirements, tasks, ADRs, operations, schemas, errors, events, permissions, metrics, tests, invariants, runbooks, commands, and releases;
- define freshness, conflict, drift, gap, flake, and review states;
- publish schemas in OpenAPI;
- generate frontend types.

### Acceptance Criteria

- every engineering-evidence state is machine-readable;
- repository revision is present in every aggregate;
- public/private visibility is explicit;
- blockers and compatibility rules are versioned;
- contract tests pass.

## S14.2 Implement Repository Revision Endpoint

### Objective

Expose the exact repository, build, API, migration, dependency, and documentation revision.

### Work

- return repository ID, branch, commit SHA, timestamp, docs build, OpenAPI hash, migration head, dependency lock hashes, client/backend build versions, environment, publication time, and authorized links;
- verify values during build and deployment;
- classify mismatches and unavailable evidence;
- cache immutably by revision;
- avoid private repository leakage in public output.

### Acceptance Criteria

- every portal page can identify its revision;
- hashes map to generated artifacts;
- mismatches fail documentation or release gates;
- public output is minimized;
- integration tests pass.

## S14.3 Define Documentation Metadata and Registry

### Objective

Give every authoritative document stable identity, ownership, version, review, and supersession evidence.

### Work

- define document IDs, paths, title, category, authority, status, version, owner, reviewers, review dates, supersession, relations, visibility, language, hash, and freshness;
- create a registry or machine-readable index;
- map existing files before requiring front matter;
- detect duplicate IDs and paths;
- preserve archived documents.

### Acceptance Criteria

- path is not the only identity;
- duplicate IDs fail CI;
- every authoritative document has an owner and review date;
- supersession is explicit;
- registry tests pass.

## S14.4 Implement Documentation Authority and Conflict Rules

### Objective

Resolve conflicting instructions according to explicit precedence.

### Work

- encode authority levels from safety and AGENTS through historical guidance;
- detect product-scope, live-trading, role, API, risk, accounting, environment, provider, terminology, task, and release-gate conflicts;
- persist documents, fields, severity, precedence, owner, and resolution;
- block silent newest-file selection;
- expose conflict history.

### Acceptance Criteria

- every conflict names authoritative precedence;
- critical scope or safety conflicts block CI;
- resolved conflicts retain history;
- no document is chosen by timestamp alone;
- conflict tests pass.

## S14.5 Implement Documentation Freshness Engine

### Objective

Detect technical staleness using dependency evidence rather than modification time alone.

### Work

- track references to APIs, schemas, configuration defaults, migrations, source, commands, providers, deployments, and review dates;
- mark documents stale when dependencies change;
- distinguish stale, review due, superseded, conflict, and unavailable;
- record cause and affected sections;
- support owner acknowledgement and remediation tracking.

### Acceptance Criteria

- recently edited but outdated documents remain stale;
- each stale state has a reason and dependency;
- critical stale documents block applicable releases;
- remediation does not erase history;
- freshness tests pass.

## S14.6 Implement Link, Anchor, and Canonical-ID Validation

### Objective

Verify every repository and catalog reference.

### Work

- validate relative links, anchors, document IDs, requirements, tasks, ADRs, operations, schemas, errors, reasons, tests, runbooks, source paths, migrations, releases, and approved external links;
- skip or protect authenticated/private external links;
- classify broken, redirected, ambiguous, and forbidden links;
- provide source locations;
- integrate with CI.

### Acceptance Criteria

- broken authoritative links fail CI;
- private URLs are not exposed in public artifacts;
- ambiguous references require stable IDs;
- external checks are bounded and safe;
- link tests pass.

## S14.7 Implement Documentation Front-Matter Migration

### Objective

Introduce machine-readable metadata without breaking existing authoritative content.

### Work

- define front-matter schema;
- inventory current documents;
- create migration phases and compatibility fallback;
- add validation and autofix only for safe metadata;
- preserve document bodies and Git history;
- document rollback.

### Acceptance Criteria

- no content is lost;
- existing docs remain readable during migration;
- invalid metadata fails with precise errors;
- safe automation never changes authority silently;
- migration tests pass.

## S14.8 Implement Documentation Catalog and Navigation

### Objective

Expose categorized, searchable, authorization-aware documentation.

### Work

- implement catalog list and detail endpoints;
- group by product, architecture, domain, operations, security, design, contributor, generated, and historical categories;
- expose status, authority, version, owner, review, freshness, relations, and visibility;
- support filters and cursor pagination;
- add hierarchical navigation and breadcrumbs.

### Acceptance Criteria

- authoritative and historical content are distinguishable;
- unauthorized documents do not leak existence;
- stale and superseded state is visible;
- deep links are stable;
- API and navigation tests pass.

## S14.9 Implement Documentation Build Pipeline

### Objective

Produce immutable public and authenticated documentation artifacts.

### Work

- read Markdown and generated catalogs;
- validate metadata, IDs, links, terminology, and conflicts;
- render diagrams safely;
- sanitize HTML;
- build search indexes;
- include revision and hashes;
- separate public/authenticated output;
- fail on critical drift or conflicts;
- publish immutable artifacts.

### Acceptance Criteria

- build output maps to exact source revision;
- public and authenticated content are separated;
- unsafe HTML is removed;
- critical errors stop publication;
- build tests pass.

## S14.10 Implement Generated Artifact Manifest

### Objective

Track source, generator, command, hash, and drift for every generated reference.

### Work

- register OpenAPI docs, TypeScript types, backend schemas, database diagrams, migration manifest, permission matrix, code catalogs, glossary, task index, test inventory, SBOM, and release manifests;
- persist source revision, generator version, command, output hash, and status;
- detect uncommitted or stale generation;
- expose remediation commands;
- integrate with CI.

### Acceptance Criteria

- generated files cannot drift silently;
- every artifact identifies generator and source;
- stale output blocks applicable builds;
- remediation commands are repository-owned;
- generation tests pass.

## S14.11 Implement OpenAPI Catalog and Explorer

### Objective

Expose every API operation with complete contract and implementation evidence.

### Work

- parse authoritative OpenAPI;
- render version, hash, operation ID, method, path, purpose, Auth, permissions, request/response schemas, errors, idempotency, expected version, rate limits, pagination, examples, tests, source, environment, deprecation, and compatibility;
- validate operation IDs and tags;
- link related tasks and requirements;
- support search and filters.

### Acceptance Criteria

- every public operation has a stable operation ID;
- permissions and errors are complete;
- undocumented operations fail CI;
- examples use synthetic values;
- explorer tests pass.

## S14.12 Implement Safe API Example Registry

### Objective

Keep API examples versioned, executable against fakes, and free of secrets.

### Work

- define example identity, operation, purpose, environment, synthetic headers/parameters/body, expected response/errors, permission, idempotency, fixture, version, and hash;
- validate examples against schemas;
- run examples against fake or isolated environments;
- scan for credentials and personal data;
- preserve failed example runs.

### Acceptance Criteria

- examples validate automatically;
- no production data or secret appears;
- failures remain visible;
- every state-changing example documents idempotency and concurrency;
- example tests pass.

## S14.13 Implement API Explorer Execution Guard

### Objective

Allow only approved interactive requests in isolated environments.

### Work

- restrict environment and host allowlist;
- require authentication and operation permission;
- default to static examples;
- require normal confirmation, idempotency, expected version, and audit for approved commands;
- redact headers and responses;
- prohibit production-research mutations by default;
- add rate limits.

### Acceptance Criteria

- arbitrary hosts and operations are impossible;
- secret headers are never displayed;
- privileged requests use normal command gates;
- public docs cannot execute requests;
- security tests pass.

## S14.14 Implement Schema Catalog

### Objective

Connect project-owned schemas to Python, TypeScript, APIs, events, and tests.

### Work

- render schema ID/version/hash, JSON/OpenAPI reference, Python and TypeScript types, fields, formats, units, nullability, enums, ranges, examples, compatibility, source, tests, dependents, and deprecation;
- verify decimal and timestamp rules;
- reject provider SDK types as public contracts;
- add schema diffs;
- support search.

### Acceptance Criteria

- every public schema maps to project-owned types;
- breaking changes are classified;
- generated types match source schema;
- units and nullability are explicit;
- schema tests pass.

## S14.15 Implement Error and Reason-Code Catalog

### Objective

Document every stable public and domain code.

### Work

- render code, category, severity, HTTP status, safe meaning, retry eligibility, actionability, affected operations/domains, audit, telemetry, localization, tests, introduced/deprecated versions;
- extract or register codes from source;
- compare with API and frontend content registries;
- detect unknown runtime codes;
- preserve deprecations.

### Acceptance Criteria

- every public error code is documented and tested;
- severity and retry behavior are unambiguous;
- frontend localization coverage is complete;
- unknown codes fail CI or safe fallback policy;
- catalog tests pass.

## S14.16 Implement Event Catalog

### Objective

Document domain, outbox, audit, and lifecycle event contracts.

### Work

- render event type, schema, producer, consumers, payload, ordering, idempotency, transaction/outbox, retry, dead-letter, privacy, telemetry, source, tests, and compatibility;
- validate emitted events against schemas;
- detect unregistered producers or consumers;
- link lineage workspaces;
- classify deferred event infrastructure.

### Acceptance Criteria

- emitted events are schema-valid;
- ordering and retry semantics are explicit;
- private data classification is present;
- unregistered event changes fail CI;
- event tests pass.

## S14.17 Implement Permission Catalog

### Objective

Document every permission across routes, handlers, roles, RLS, commands, and tests.

### Work

- render code, description, role defaults, scope, application rule, RLS policy, recent-auth requirement, route/command mappings, denied audit, tests, and versions;
- compare with governance permission registry;
- detect unused and undocumented permissions;
- expose public-safe subsets;
- support diff and traceability.

### Acceptance Criteria

- every protected route and command maps to a permission;
- RLS and application references are present;
- undocumented permission changes block release;
- role defaults do not override effective checks;
- permission tests pass.

## S14.18 Implement Metric Catalog

### Objective

Document safe observability metrics and prevent cardinality or privacy regressions.

### Work

- render metric name, type, unit, description, source, labels, cardinality, privacy, environments, alert/SLO, retention, tests, and versions;
- scan instrumentation against registry;
- detect secret or unbounded-label patterns;
- link dashboards and runbooks;
- preserve deprecation.

### Acceptance Criteria

- every production metric is registered;
- high-cardinality labels fail review;
- sensitive metrics are blocked;
- units and alert links are explicit;
- metric tests pass.

## S14.19 Implement Requirement Registry

### Objective

Give product, security, privacy, architecture, accessibility, and operational requirements stable identity.

### Work

- extract or register requirement ID, source, text hash, category, priority, owner, status, acceptance evidence, supersession, and links;
- detect duplicates and missing IDs;
- preserve historical text hashes;
- link tasks, tests, documentation, and releases;
- support search and filters.

### Acceptance Criteria

- every material implementation task maps to requirements;
- changed requirement text is visible;
- supersession does not erase history;
- missing critical IDs fail CI;
- registry tests pass.

## S14.20 Implement Sprint Task Registry

### Objective

Track every task from specification through verified completion evidence.

### Work

- parse stable sprint task IDs, source, title, objective, work, acceptance hashes, dependencies, owner, status, implementation, tests, docs, commits, follow-ups, and limitations;
- validate duplicate IDs and references;
- distinguish documentation-created from implementation-complete;
- preserve verification commits;
- expose filters and progress.

### Acceptance Criteria

- task completion is never inferred from commit message alone;
- acceptance criteria remain traceable by hash;
- missing evidence produces partial state;
- dependencies are explicit;
- task tests pass.

## S14.21 Implement Source and Symbol Evidence Registry

### Objective

Connect implementation files and symbols to contracts and tests.

### Work

- register source path, symbol/range where available, revision, owner, generated/handwritten class, API/schema/migration/task/requirement/test/ADR links, classifications, and verification time;
- use repository parsers where practical;
- minimize private source in public output;
- detect orphan implementation;
- preserve renamed-path lineage.

### Acceptance Criteria

- material source maps to at least one requirement or task;
- generated and handwritten code remain distinct;
- public output exposes no private source;
- orphan changes become gaps;
- registry tests pass.

## S14.22 Implement Migration Traceability Registry

### Objective

Prove every migration is immutable, motivated, tested, rehearsed, and deployed intentionally.

### Work

- render revision, hash, parent, commit, purpose, affected database objects, stage, tasks, requirements, tests, rehearsal, deployment, applied environments, drift, and recovery notes;
- detect changed applied migrations;
- link RLS and schema catalogs;
- validate one head;
- expose environment status.

### Acceptance Criteria

- modified applied migration is critical;
- each migration maps to a task and tests;
- rehearsal and environment application are visible;
- drift blocks release;
- migration tests pass.

## S14.23 Implement Traceability Graph and Matrix

### Objective

Connect requirements through deployment verification.

### Work

- model typed relationships among requirements, tasks, ADRs, APIs, schemas, events, permissions, source, migrations, tests, docs, releases, and deployments;
- render graph and table alternatives;
- support resource-centered views;
- preserve direction and status;
- enforce authorization;
- export bounded evidence.

### Acceptance Criteria

- every material behavior has an evidence chain or explicit gap;
- graphs have accessible text alternatives;
- unauthorized nodes do not leak existence;
- cycles and conflicting links are detected;
- traceability tests pass.

## S14.24 Implement Traceability Gap Detection

### Objective

Find missing requirements, tasks, implementation, contracts, migrations, tests, docs, runbooks, and release evidence.

### Work

- detect all gap categories defined by specification;
- assign severity based on domain and release target;
- persist affected items, evidence, owner, remediation, and state;
- prevent coverage-only closure;
- integrate critical gaps into release gates.

### Acceptance Criteria

- critical invariants without tests are blockers;
- public API without schema/error/tests is blocked;
- gaps remain until evidence is verified;
- false-positive resolution is audited;
- gap tests pass.

## S14.25 Implement ADR Registry and Lifecycle

### Objective

Track architecture decisions, alternatives, consequences, and supersession.

### Work

- define ADR metadata and templates;
- implement proposed, review, accepted, rejected, superseded, deprecated, and archived states;
- require security, privacy, financial, operational, migration, component, task, and test impact;
- preserve accepted ADR immutability;
- link dependent docs and code.

### Acceptance Criteria

- production architecture changes require an ADR;
- accepted ADR changes create amendment or successor;
- alternatives and consequences are present;
- supersession is explicit;
- ADR tests pass.

## S14.26 Implement Architecture Dependency Graph

### Objective

Expose active and deferred component relationships and contract ownership.

### Work

- model domains, services, adapters, database, providers, deployments, schemas, events, ADRs, tasks, and tests;
- render direction, owner, environment, optional/deferred state, and status;
- detect forbidden domain imports and activated-deferred components;
- provide accessible table alternative;
- link source evidence.

### Acceptance Criteria

- dependency direction matches architecture rules;
- deferred Redis/ARQ/WebSocket cannot appear active without ADR;
- forbidden boundary violations are findings;
- diagram is revision-linked;
- architecture tests pass.

## S14.27 Implement Test Inventory

### Objective

Catalog test identity, type, environment, coverage, fixtures, provider policy, timeout, flake state, and last result.

### Work

- extract test file/name and stable ID where practical;
- classify unit, property, integration, contract, E2E, security, accessibility, performance, recovery, and smoke;
- link requirements, tasks, invariants, APIs, schemas, migrations, and source;
- record fake/fixture/smoke provider class;
- preserve last verified revision.

### Acceptance Criteria

- every critical invariant maps to tests;
- paid or external calls are classified;
- test environment is explicit;
- stale test inventory is detected;
- inventory tests pass.

## S14.28 Implement Test Run Evidence Ingestion

### Objective

Persist normalized CI and local verification evidence.

### Work

- ingest workflow/job, revision, environment, command, tool versions, timing, counts, coverage, artifacts, redacted failures, retries, outcome, and PR/release links;
- validate artifact hashes;
- distinguish rerun and retry;
- preserve failed runs;
- expose safe filters.

### Acceptance Criteria

- failed runs remain discoverable;
- blind rerun cannot replace original evidence;
- counts reconcile with artifacts;
- sensitive payloads are redacted;
- ingestion tests pass.

## S14.29 Implement Invariant Registry and Coverage

### Objective

Track financial, safety, authorization, recovery, and live-trading-disabled invariants.

### Work

- register invariant ID, definition, domain, severity, proof strategy, tests, scans, runtime checks, environments, last verification, and gaps;
- seed mandatory invariants from AGENTS and TESTING;
- render property and integration evidence;
- block critical uncovered invariants;
- preserve version changes.

### Acceptance Criteria

- all mandatory invariants are registered;
- each has executable or explicit verification evidence;
- coverage metrics cannot substitute for invariant proof;
- failed invariant tests are critical;
- registry tests pass.

## S14.30 Implement Coverage Evidence View

### Objective

Present coverage with domain thresholds and limitations.

### Work

- ingest branch, statement, function, line, changed-lines, uncovered critical files, exclusions, test-type contribution, and trends;
- apply domain-specific thresholds;
- require rationale for exclusions;
- link uncovered code to tasks and invariants;
- avoid coverage-as-correctness framing.

### Acceptance Criteria

- risk/execution/portfolio/accounting thresholds are enforced;
- critical uncovered files are visible;
- exclusions are reviewed;
- coverage failure cannot be hidden by aggregate percentage;
- coverage tests pass.

## S14.31 Implement Flaky Test Registry and Expiry

### Objective

Treat flakiness as a tracked defect rather than rerun policy.

### Work

- store test, issue, owner, pattern, environment, reason, compensating coverage, start, expiry, remediation, last fail/success, and state;
- detect repeated reruns and intermittent failures;
- expire quarantines automatically by policy state;
- block promotion when expired or critical;
- preserve history.

### Acceptance Criteria

- quarantine requires issue, owner, and expiry;
- expired quarantine is a blocker;
- blind rerun-until-green is detected;
- critical tests cannot remain silently quarantined;
- flake tests pass.

## S14.32 Implement External Provider Test Policy View

### Objective

Make fake, fixture, local, public smoke, paid smoke, and prohibited calls explicit.

### Work

- classify every Binance, Gemini, Supabase, Render, and Cloudflare test;
- render credential, budget, fork, data, and environment restrictions;
- verify normal CI uses fakes and fixtures;
- protect smoke workflows;
- detect untrusted-fork secret access.

### Acceptance Criteria

- normal PRs require no paid credentials;
- private Binance is prohibited;
- smoke tests are bounded and protected;
- provider classification maps to test inventory;
- policy tests pass.

## S14.33 Implement Pull Request Evidence Package

### Objective

Standardize implementation review evidence.

### Work

- generate change, task, requirement, ADR, file, migration, API/schema/error/event/permission/metric, tests, commands, results, coverage, scans, migration/RLS, accessibility, visual, environment, docs, changelog, risk, follow-up, release, and rollback sections;
- derive safe evidence from CI and repository metadata;
- allow explicit reviewer notes;
- preserve immutable package hash;
- link release candidates.

### Acceptance Criteria

- every implementation PR has task and test evidence;
- untested risks are explicit;
- package does not expose secrets;
- generated content is reviewable and not self-approving;
- package tests pass.

## S14.34 Implement Runbook Registry

### Objective

Catalog triggers, prerequisites, steps, validation, stop conditions, and ownership for operational recovery.

### Work

- define runbook ID, trigger, symptoms, scope, severity, role, recent auth, prerequisites, safety/halts, tools, steps, evidence, validation, rollback/stop, secret notes, relations, owner, version, review dates;
- migrate existing runbook content;
- detect duplicate or missing triggers;
- support search and filters;
- link incidents and alerts.

### Acceptance Criteria

- every critical alert has a runbook;
- role and environment are explicit;
- secret handling is documented safely;
- stale critical runbooks block promotion;
- registry tests pass.

## S14.35 Implement Runbook Testing and Drill Evidence

### Objective

Verify runbooks through syntax, dry-run, helper, failure, redaction, recovery, and review tests.

### Work

- validate links and metadata;
- run isolated dry-runs where practical;
- test helper scripts and stop conditions;
- record restore/recovery drills;
- verify redaction;
- persist execution evidence and failures;
- schedule review reminders.

### Acceptance Criteria

- runbook existence alone is insufficient;
- failed drills remain visible;
- critical runbooks have recent evidence;
- commands are safe and repository-owned;
- drill tests pass.

## S14.36 Implement Guarded Runbook Execution Boundary

### Objective

Prevent the portal from becoming an arbitrary shell or SQL console.

### Work

- keep runbooks read-only by default;
- allow only explicit helpers in isolated environments;
- require role, recent auth, target, confirmation, idempotency, concurrency, secret-safe inputs, audit, validation, and stop conditions;
- prohibit arbitrary shell, SQL, provider, and exchange commands;
- preserve failed attempts.

### Acceptance Criteria

- arbitrary execution is impossible;
- every helper maps to a reviewed script and runbook version;
- production-research actions remain separately gated;
- execution evidence is complete;
- security tests pass.

## S14.37 Implement Contributor Getting Started

### Objective

Provide reproducible no-paid-secret setup on Windows 11 and Unix-like systems.

### Work

- document prerequisites, clone, bootstrap, templates, local Supabase/Auth, backend/frontend, fake providers, seed, one-shot cycle, tests, lint, type, formatting, scans, builds, docs, reset, cleanup, common failures, and contribution workflow;
- use repository scripts;
- provide PowerShell and shell commands where needed;
- test clean setup environments;
- link task selection and AGENTS.

### Acceptance Criteria

- ordinary setup requires no paid provider key;
- commands work from documented directories;
- Windows 11 and Unix-like flows are verified;
- reset returns deterministic local state;
- setup tests pass.

## S14.38 Implement Command Catalog

### Objective

Document repository commands, side effects, platforms, failures, and cleanup.

### Work

- register command ID, purpose, platforms, prerequisites, directory, environment, secret needs, side effects, expected output, failures, cleanup, source script, tests, and version;
- validate referenced scripts;
- detect duplicated hidden CI logic;
- link getting-started and runbooks;
- preserve deprecated commands.

### Acceptance Criteria

- commands call repository-owned scripts where practical;
- secret requirements are explicit and minimal;
- destructive side effects require warning and isolation;
- missing scripts fail docs checks;
- command tests pass.

## S14.39 Implement Public Documentation Boundary

### Objective

Publish approved product, architecture, methodology, API, setup, Trust, and disclosure content safely.

### Work

- define public visibility policy;
- generate separate public artifact and search index;
- exclude private incidents, findings, environments, source, audits, financial evidence, and privileged runbooks;
- scan public output for secrets and private identifiers;
- link public source revision and limitations.

### Acceptance Criteria

- public docs reveal no private operational evidence;
- authenticated pages are not indexed publicly;
- public API examples are safe;
- disclosure contact is present;
- boundary tests pass.

## S14.40 Implement Documentation Search

### Objective

Search canonical documentation and engineering evidence within authorization boundaries.

### Work

- index titles, headings, IDs, requirements, tasks, ADRs, APIs, schemas, errors, events, permissions, metrics, invariants, tests, runbooks, commands, and approved symbols;
- support category, status, owner, environment, version, and freshness filters;
- enforce authorization before indexing/results;
- sanitize queries;
- provide accessible result grouping.

### Acceptance Criteria

- private content does not influence public results or counts;
- exact canonical IDs resolve;
- search index identifies revision;
- query injection is inert;
- search tests pass.

## S14.41 Implement Changelog and Compatibility Registry

### Objective

Connect material changes, deprecations, migration notes, and release evidence.

### Work

- record version/date, tasks, requirements, user-visible behavior, API/schema compatibility, migration, security/privacy, operations, deprecations, limitations, upgrade, rollback, and release links;
- define compatibility and deprecation lifecycle;
- validate generated release notes against evidence;
- require review before publication;
- preserve history.

### Acceptance Criteria

- breaking changes have migration guidance;
- deprecation has replacement and removal gate;
- release notes map to exact artifacts;
- generated notes cannot self-approve;
- compatibility tests pass.

## S14.42 Implement Authorized Evidence Export

### Objective

Export bounded traceability, test, runbook, documentation-health, and release packages.

### Work

- support document catalog, API/schema catalogs, traceability, ADRs, test evidence, invariant coverage, runbook evidence, docs health, PR evidence, and release manifests;
- generate server-side;
- include revision, hashes, blockers, gaps, limitations, and authorization context;
- redact source and operational details by role;
- preserve integrity manifest.

### Acceptance Criteria

- exports identify exact revision;
- critical gaps cannot be omitted;
- secrets, production data, and private failure payloads are absent;
- public and private export policies differ explicitly;
- export tests pass.

## S14.43 Add Explicit State Handling

### Objective

Define safe rendering for every documentation, generation, traceability, test, and runbook state.

### Work

- implement loading, empty, authoritative, stale, conflicting, superseded, generated, generation failed, broken link, invalid metadata, OpenAPI/schema drift, migration modified, requirement/task/implementation/test gaps, invariant uncovered, runbook stale/failed, test passed/failed/partial, flake expired, provider unavailable, unauthorized, not found, backend unavailable, schema mismatch, and export failure;
- define bounded retries;
- distinguish integrity failures from no content;
- label cached artifacts by revision.

### Acceptance Criteria

- critical evidence failure never appears empty or healthy;
- stale artifacts identify source revision;
- retries do not hide deterministic failures;
- unauthorized state reveals no private content;
- state-matrix tests pass.

## S14.44 Add Responsive and Accessibility Verification

### Objective

Ensure dense engineering evidence remains usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom;
- test navigation, trees, code, schemas, API examples, tables, graphs, diagrams, filters, search, copy controls, headings, landmarks, focus, and announcements;
- provide text alternatives for diagrams;
- verify reduced motion and contrast;
- test long paths, commands, hashes, and symbols.

### Acceptance Criteria

- all evidence is keyboard reachable;
- diagrams have equivalent text or table views;
- code blocks do not break page reflow;
- no meaning relies only on color or hover;
- no critical automated violation remains;
- manual evidence is recorded.

## S14.45 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make documentation integrity, generated drift, traceability, test evidence, runbook safety, public/private boundaries, and no-arbitrary-execution release-blocking.

### Work

- add contract, metadata, authority, freshness, conflict, link, build, generation, API, schema, error, event, permission, metric, requirement, task, source, migration, traceability, ADR, test, invariant, coverage, flake, provider, PR evidence, runbook, setup, command, public docs, search, changelog, route, E2E, accessibility, visual, authorization, and export tests;
- add secret, private-data, source-leak, unsafe-example, arbitrary-host, arbitrary-command, raw-failure, and sanitization checks;
- verify normal CI requires no paid credentials and cannot edit applied migrations or trigger live trading;
- instrument safe docs build, gaps, drift, test, runbook, search, and export metrics;
- test prohibited telemetry fields.

### Acceptance Criteria

- critical docs, generated, migration, traceability, invariant, and runbook failures block release;
- unauthorized public output contains no private evidence;
- no portal, browser, API explorer, runbook, command, or AI path gains arbitrary code, SQL, workflow, provider, exchange, migration-edit, secret, or live-trading authority;
- telemetry contains no prohibited fields;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Documentation | Stable IDs, metadata, authority, ownership, review, freshness, supersession, conflicts, links, terminology, public/private, and build tests |
| Generated artifacts | OpenAPI, types, schema, database, migration, permission, code, glossary, task, test, SBOM, manifest, hash, and drift tests |
| API and catalogs | Operations, Auth, permissions, schemas, errors, idempotency, examples, events, metrics, compatibility, and executable-fake tests |
| Traceability | Requirement, task, ADR, API, schema, migration, source, test, invariant, docs, release, deployment, gap, and export tests |
| Test evidence | Inventory, types, environments, provider policy, run parsing, counts, artifacts, coverage, invariants, flakes, retries, and release links |
| Runbooks | Registry, triggers, roles, prerequisites, steps, validation, stop conditions, redaction, dry runs, helpers, drills, review, and execution guards |
| Contributor experience | Clean bootstrap, local Supabase/Auth, fake providers, seed, cycle, commands, reset, Windows 11, Unix-like, no-paid-secret, and common-failure tests |
| Accessibility and security | Keyboard, code, diagrams, search, zoom, public/private separation, authorization, sanitization, no arbitrary execution, secret scan, and telemetry tests |

## Sprint Exit Gate

Sprint 14 is complete only when:

- S14.1 through S14.45 are implemented and verified;
- every portal page identifies repository and documentation revision;
- documents have stable identity, authority, ownership, version, review, supersession, and freshness evidence;
- links, IDs, terminology, conflicts, and generated artifacts are verified in CI;
- OpenAPI, schemas, errors, events, permissions, metrics, requirements, tasks, ADRs, tests, invariants, runbooks, and commands have versioned catalogs;
- traceability connects requirements through tasks, design, code, migrations, tests, docs, release, and deployment;
- modified applied migrations, uncovered critical invariants, undocumented public errors, stale critical runbooks, and critical traceability gaps block release;
- test evidence preserves revision, environment, command, tool versions, counts, coverage, failures, artifacts, reruns, and provider policy;
- flaky tests require issue, owner, expiry, and remediation;
- runbook execution remains allowlisted, isolated, role-controlled, idempotent, audited, and non-arbitrary;
- contributor setup works with fake providers and no paid secrets on Windows 11 and Unix-like systems;
- public docs are separately built and contain no private operational evidence;
- no developer portal, API explorer, runbook, command, browser, or AI path gains arbitrary source mutation, shell, SQL, workflow, provider, exchange, migration-edit, secret, private credential, testnet, or live-trading authority;
- accessibility, responsive, security, privacy, documentation, generation, API, traceability, test, invariant, runbook, setup, command, E2E, export, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 15 defines and implements the Performance, Resilience, Capacity, SLO, Cost, Quota, and FinOps Evidence Workspace.
