# Developer Portal, API Explorer, Documentation System, Test Evidence, Runbook Library, and Implementation Traceability Workspace Specification

Last reviewed: 2026-07-31  
Status: Sprint 14 authoritative developer experience and implementation-evidence specification

## 1. Purpose

This document defines the implementation contract for the Developer Portal, API Explorer, Documentation System, Test Evidence, Runbook Library, Architecture Decision Record, and Implementation Traceability Workspace of The Daily Roast AI.

The workspace makes the repository’s implementation contract inspectable and verifiable. It connects product requirements, domain specifications, sprint tasks, architecture decisions, OpenAPI operations, schemas, database migrations, source files, tests, security scans, runbooks, release gates, and deployed artifacts so contributors and reviewers can prove what changed, why it changed, how it is tested, and whether the documentation remains current.

The portal is an engineering evidence layer. It must not expose secrets, production data, private provider payloads, unsafe operational commands, or browser access to privileged infrastructure.

## 2. Scope

Sprint 14 covers:

- authenticated developer portal and approved public documentation subset;
- versioned documentation catalog and navigation;
- generated OpenAPI explorer with authenticated examples;
- schema, enum, error-code, event, reason-code, permission, metric, and status catalogs;
- task, requirement, ADR, source, migration, API, test, scan, artifact, and release traceability;
- documentation metadata, ownership, freshness, review, supersession, and broken-link detection;
- architecture decision record registry and dependency graph;
- test plan, test run, coverage, invariant, environment, flake, and evidence views;
- runbook library, prerequisites, dry-run, execution, validation, recovery, and review evidence;
- contributor onboarding, local setup, Windows 11 and Unix-like command guidance;
- generated-reference verification and drift detection;
- pull request evidence package and review checklist;
- changelog, release notes, migration notes, and compatibility records;
- searchable implementation glossary and code ownership;
- authorized diagnostic and evidence export;
- responsive, accessible, secure, observable, and testable presentation.

Sprint 14 does not implement:

- arbitrary code execution from the browser;
- arbitrary API requests against production research;
- secret-bearing example values;
- database consoles or raw SQL;
- direct workflow dispatch without an approved command specification;
- mutation of applied migrations;
- automatic acceptance of a task based only on coverage;
- AI-generated code changes without repository review and tests;
- exposure of private source repositories or proprietary provider payloads;
- live trading or private exchange execution.

## 3. User Outcomes

A contributor or reviewer should be able to answer:

1. Which document is authoritative for this behavior?
2. Which sprint task and acceptance criteria require the implementation?
3. Which product requirement and architecture decision justify it?
4. Which API operation, schema, error code, event, and permission define the public contract?
5. Which source files and migrations implement it?
6. Which unit, property, integration, contract, E2E, security, accessibility, recovery, and performance tests verify it?
7. Which invariants remain untested?
8. Which documentation pages are stale, superseded, conflicting, or missing review?
9. Which generated artifacts drift from source?
10. Which runbook applies to a failure, and what evidence proves it was executed successfully?
11. Which commands reproduce local setup and verification on Windows 11 and Unix-like systems?
12. Which external-provider calls are fake, protected smoke, or prohibited in normal CI?
13. Which release and deployment contain the implementation?
14. Which known limitations, exceptions, flaky tests, and follow-up tasks remain?
15. Can the evidence package be exported without secrets or production data?

## 4. Canonical Routes

```text
/developers
/developers/getting-started
/developers/architecture
/developers/adrs
/developers/adrs/:adrId
/developers/api
/developers/api/:operationId
/developers/schemas
/developers/schemas/:schemaId
/developers/errors
/developers/events
/developers/permissions
/developers/metrics
/developers/tasks
/developers/tasks/:taskId
/developers/requirements
/developers/traceability
/developers/tests
/developers/tests/runs/:testRunId
/developers/invariants
/developers/runbooks
/developers/runbooks/:runbookId
/developers/docs-health
/developers/releases/:releaseId/evidence
```

Public documentation routes must be a separately approved subset with no authenticated operational or repository-private content.

## 5. Information Architecture

The portal landing page is ordered as follows:

1. repository, branch, commit, environment, and documentation version;
2. critical documentation, generated-artifact, migration, test, scan, or traceability failures;
3. getting-started and contributor workflow;
4. architecture and ADRs;
5. API, schema, error, event, permission, and metric catalogs;
6. sprint tasks and requirement traceability;
7. test evidence and invariant coverage;
8. runbooks and recovery evidence;
9. documentation health, ownership, and freshness;
10. pull request, release, and deployment evidence.

A broken authoritative link, conflicting specification, missing critical test, generated OpenAPI drift, modified applied migration, failed security scan, or stale runbook must outrank ordinary documentation completeness metrics.

## 6. Recommended Read Models

Recommended portal contract:

```ts
interface DeveloperPortalReadModel {
  schemaVersion: string;
  repository: RepositoryRevisionSummary;
  documentation: DocumentationCatalogSummary;
  api: ApiCatalogSummary;
  traceability: TraceabilitySummary;
  tests: TestEvidenceSummary;
  runbooks: RunbookLibrarySummary;
  architecture: ArchitectureDecisionSummary;
  health: DocumentationHealthSummary;
  blockers: DeveloperEvidenceBlocker[];
  permissions: DeveloperPortalPermissions;
  diagnostics: DiagnosticSummary[];
  links: DeveloperPortalLinks;
}
```

Recommended traceability contract:

```ts
interface TraceabilityItemReadModel {
  schemaVersion: string;
  item: TraceabilityItemIdentity;
  requirements: RequirementReference[];
  tasks: TaskReference[];
  adrs: AdrReference[];
  apiOperations: ApiOperationReference[];
  schemas: SchemaReference[];
  migrations: MigrationReference[];
  sourceFiles: SourceFileReference[];
  tests: TestReference[];
  invariants: InvariantReference[];
  scans: ScanEvidenceReference[];
  documentation: DocumentationReference[];
  releases: ReleaseReference[];
  deployments: DeploymentReference[];
  gaps: TraceabilityGap[];
  outcome: "complete" | "partial" | "conflict" | "missing" | "unavailable";
}
```

Recommended documentation health contract:

```ts
interface DocumentationHealthReadModel {
  schemaVersion: string;
  revision: string;
  documents: DocumentationHealthItem[];
  brokenLinks: BrokenLinkSummary[];
  staleDocuments: StaleDocumentSummary[];
  conflicts: DocumentationConflictSummary[];
  generatedDrift: GeneratedArtifactDriftSummary[];
  terminologyFindings: TerminologyFindingSummary[];
  coverage: DocumentationCoverageSummary;
  outcome: "healthy" | "warning" | "blocked" | "unavailable";
}
```

The frontend must not infer test success, task completeness, traceability completeness, documentation freshness, API compatibility, migration immutability, or release readiness.

## 7. Repository Revision Identity

Required fields:

- repository canonical identifier;
- branch;
- commit SHA;
- commit timestamp;
- working or generated revision identifier;
- documentation build ID;
- API schema hash;
- migration head;
- dependency lock hashes;
- frontend and backend build versions;
- environment;
- publication timestamp;
- source and artifact links where authorized.

Every portal page must identify the revision it documents.

## 8. Documentation Catalog Contract

Required fields:

- immutable document ID;
- canonical path;
- title;
- category;
- authority level;
- status;
- version;
- source revision;
- owner;
- reviewers;
- last reviewed timestamp;
- next review due date;
- supersedes and superseded-by references;
- related requirements, tasks, ADRs, APIs, schemas, tests, and runbooks;
- publication visibility;
- language;
- hash;
- freshness outcome;
- limitations.

The path alone is not a stable document identity.

## 9. Documentation Authority Levels

Recommended levels:

1. mandatory safety and governance instructions;
2. agent and contributor instructions;
3. product requirements;
4. accepted architecture and ADRs;
5. domain specifications;
6. sprint implementation specifications;
7. task files;
8. operational runbooks;
9. generated API and schema references;
10. explanatory guides and examples;
11. historical or archived records.

Conflicts must be resolved according to documented precedence, not by choosing the newest file silently.

## 10. Document Lifecycle

Supported states include:

- draft;
- in review;
- authoritative;
- approved with limitations;
- stale;
- conflicting;
- superseded;
- archived;
- generated;
- generation failed;
- unavailable.

Every transition records actor, revision, reason, review evidence, timestamp, and audit reference.

## 11. Documentation Metadata Front Matter

Every authoritative or operational document should expose machine-readable metadata for:

- document ID;
- title;
- status;
- authority;
- owner;
- reviewers;
- version;
- last reviewed;
- next review;
- source revision;
- related task and requirement IDs;
- supersession;
- visibility;
- language.

A migration plan is required before introducing mandatory front matter to existing files.

## 12. Documentation Freshness

Freshness uses evidence, not file modification time alone.

Signals include:

- referenced API operation changed;
- referenced schema or enum changed;
- referenced configuration default changed;
- referenced migration changed;
- code ownership changed;
- test command changed;
- provider behavior or terms changed;
- deployment topology changed;
- document review due date passed;
- unresolved link or terminology failure;
- explicit supersession.

A recently touched but technically outdated document remains stale.

## 13. Documentation Conflict Detection

Conflict categories include:

- contradictory product scope;
- inconsistent live-trading boundary;
- conflicting role permissions;
- incompatible API paths or schemas;
- differing risk limits or accounting rules;
- mismatched environment topology;
- conflicting provider model or prompt behavior;
- inconsistent terminology or product identity;
- duplicate task ownership;
- contradictory release gates.

Every conflict requires documents, excerpts or structured fields, precedence, severity, owner, and resolution state.

## 14. Link and Reference Validation

Validation includes:

- relative repository links;
- anchors;
- document IDs;
- requirement IDs;
- task IDs;
- ADR IDs;
- API operation IDs;
- schema IDs;
- error and reason codes;
- test IDs;
- runbook IDs;
- source paths;
- migration revisions;
- release references;
- approved external links.

Private or authenticated external URLs must not be crawled or exposed in public output.

## 15. Generated Documentation Contract

Generated references may include:

- OpenAPI HTML or structured catalog;
- TypeScript client types;
- backend schema references;
- database schema diagrams;
- migration manifest;
- permission matrix;
- error and reason-code catalog;
- event catalog;
- metric catalog;
- glossary catalog;
- task index;
- test inventory;
- SBOM summary;
- release evidence manifest.

Generated artifacts must identify source revision, generator version, command, hash, and drift status.

## 16. API Explorer

The API explorer must expose:

- API version and OpenAPI hash;
- operation ID;
- method and path;
- purpose;
- authentication and permission requirements;
- request schema;
- response schemas;
- error codes;
- idempotency requirements;
- expected-version or concurrency requirements;
- rate-limit class;
- pagination;
- examples;
- related tasks, requirements, tests, and source files;
- environment availability;
- deprecation and compatibility state.

## 17. API Explorer Execution Boundary

Interactive requests may be allowed only in approved local, CI, demo, or isolated staging profiles.

Requirements:

- explicit environment;
- authenticated user permission;
- allowlisted operations;
- safe example payloads;
- no secret headers displayed;
- no arbitrary host;
- no private provider or exchange credentials;
- no production-research mutation by default;
- normal command confirmation and idempotency;
- response redaction;
- audit event.

Read-only static examples are the default.

## 18. API Example Contract

Examples include:

- example ID;
- operation ID;
- purpose;
- environment profile;
- request headers excluding secrets;
- path and query parameters;
- body using synthetic values;
- expected response;
- expected errors;
- permission context;
- idempotency and concurrency notes;
- source test or fixture;
- version and hash.

Examples must remain executable against fakes or isolated test infrastructure where practical.

## 19. Schema Catalog

The schema catalog includes:

- schema ID and version;
- JSON Schema or OpenAPI reference;
- TypeScript and Python type references;
- fields, types, formats, units, nullability, enums, ranges, lengths, and examples;
- decimal and timestamp rules;
- compatibility classification;
- source file;
- tests;
- dependent operations and events;
- deprecation state;
- generated hash.

Provider SDK types must not appear as public project contracts.

## 20. Error and Reason-Code Catalog

Every code includes:

- canonical code;
- category;
- severity;
- HTTP status where applicable;
- safe user-facing meaning;
- retry eligibility;
- actionability;
- affected operations or domains;
- audit behavior;
- telemetry behavior;
- localization key;
- tests;
- introduced and deprecated versions.

Unknown or undocumented public error codes fail documentation checks.

## 21. Event Catalog

Every domain or audit event includes:

- event type;
- schema version;
- producer;
- consumers;
- payload schema;
- ordering and idempotency rules;
- transaction or outbox behavior;
- retry and dead-letter behavior where applicable;
- privacy classification;
- telemetry classification;
- source and tests;
- compatibility state.

## 22. Permission Catalog

Every permission includes:

- canonical permission code;
- description;
- role defaults;
- resource scope;
- application authorization reference;
- RLS policy reference;
- recent-authentication requirement;
- command or route mappings;
- denied-audit behavior;
- tests;
- introduced and deprecated versions.

## 23. Metric Catalog

Every metric includes:

- canonical name;
- type;
- unit;
- description;
- source component;
- labels and cardinality constraints;
- privacy classification;
- collection environment;
- alert or SLO linkage;
- retention;
- tests;
- introduced and deprecated versions.

Metrics containing secrets or unbounded identifiers are prohibited.

## 24. Requirement Registry

Requirements may originate from:

- product requirements;
- security and privacy controls;
- architecture constraints;
- domain specifications;
- accessibility requirements;
- operational and release gates.

Each requirement includes stable ID, source document, text hash, category, priority, owner, status, acceptance evidence, supersession, and links.

## 25. Task Registry

Each task includes:

- stable sprint task ID;
- sprint and source file;
- title;
- objective;
- work summary;
- acceptance criteria hashes;
- dependencies;
- owner or assignee where applicable;
- status;
- source revision;
- implementation references;
- test and documentation evidence;
- completion and verification commits;
- follow-up tasks and limitations.

Task completion cannot be inferred only from a commit message.

## 26. Implementation Evidence Contract

Implementation references include:

- source path;
- symbol or code range where available;
- source revision;
- ownership;
- generated or handwritten classification;
- related APIs, schemas, migrations, tasks, requirements, tests, and ADRs;
- security or privacy classification;
- last verified timestamp.

The portal must not expose private source content to unauthorized users.

## 27. Migration Traceability

Every migration includes:

- revision or filename;
- immutable hash;
- parent revision;
- source commit;
- purpose;
- affected tables, policies, indexes, functions, and views;
- expand/migrate/contract stage;
- related requirements and tasks;
- tests;
- rehearsal and deployment references;
- applied environments;
- drift state;
- rollback or forward-fix notes.

Modification of an applied migration is a critical blocker.

## 28. Traceability Matrix

Minimum relationships:

```text
requirement
  -> sprint task
  -> ADR or design decision
  -> API/schema/event/permission contract
  -> source and migration
  -> unit/property/integration/contract/E2E/security/accessibility/recovery test
  -> documentation
  -> release artifact
  -> deployment verification
```

Every material behavior change must preserve a complete or explicitly limited chain.

## 29. Traceability Gap Categories

- requirement without task;
- task without implementation;
- implementation without requirement or task;
- API operation without schema or tests;
- schema without compatibility policy;
- migration without task or test;
- public error without catalog entry;
- critical invariant without test;
- runbook without trigger or validation;
- document without owner or review;
- release artifact without source provenance;
- deployed behavior without release evidence.

## 30. Architecture Decision Record Registry

Every ADR includes:

- stable ADR ID;
- title;
- status;
- context;
- decision;
- alternatives;
- consequences;
- security, privacy, financial, operational, and migration impact;
- affected components and documents;
- implementation tasks;
- tests;
- supersession relationships;
- approvers;
- decision and review dates.

## 31. ADR Lifecycle

Supported states:

- proposed;
- under review;
- accepted;
- rejected;
- superseded;
- deprecated;
- archived.

Accepted ADRs are immutable; changes create a new ADR or explicit amendment record.

## 32. Architecture Dependency Graph

The graph may include:

- domains;
- application services;
- adapters;
- database components;
- external providers;
- deployment services;
- schemas;
- events;
- ADRs;
- tasks and tests.

It must preserve direction, contract ownership, environment activation, optional/deferred state, and authorization.

## 33. Test Inventory

Every test includes:

- stable test ID where practical;
- file and test name;
- type: unit, property, integration, contract, E2E, security, accessibility, performance, recovery, or smoke;
- environment;
- related requirements, tasks, invariants, APIs, schemas, migrations, and source;
- fixtures and fake providers;
- external-call policy;
- timeout;
- flake state;
- last result and revision.

## 34. Test Run Evidence

Required fields:

- test-run ID;
- workflow and job;
- source revision;
- environment;
- command;
- tool versions;
- start, finish, and duration;
- test counts;
- pass, fail, skip, xfail, and error counts;
- coverage summary;
- artifact references;
- failure details with redaction;
- retry or rerun evidence;
- final outcome;
- release or pull request reference.

## 35. Invariant Registry

Critical invariants include:

- balanced ledger transactions;
- no duplicate financial side effects;
- one cycle lease owner;
- fill quantity within approved quantity;
- approved notional within policy;
- drawdown consistency;
- decimal precision;
- projection equals reconciled state;
- invalid AI cannot approve an order;
- halt prevents new entries;
- browser cannot mutate server-only tables;
- restore preserves migration and reconciliation;
- live trading remains disabled.

Each invariant maps to property, integration, or explicit verification evidence.

## 36. Coverage Evidence

Coverage views include:

- branch, statement, function, and line coverage where applicable;
- domain-specific thresholds;
- changed-lines coverage;
- uncovered critical files;
- excluded files and rationale;
- test-type contribution;
- trend by revision;
- limitations.

Coverage cannot substitute for invariant and failure-path testing.

## 37. Flaky Test Registry

Every quarantined test requires:

- test reference;
- issue;
- owner;
- observed failure pattern;
- environment;
- quarantine reason;
- compensating coverage;
- start and expiry date;
- remediation plan;
- last failure and success;
- terminal state.

Blind rerun-until-green behavior is prohibited.

## 38. External Provider Test Classification

Classifications:

- deterministic fake;
- fixture or recorded public structure;
- local simulator;
- protected public smoke;
- protected paid-provider smoke;
- prohibited in ordinary CI.

Every provider test must identify data, credential, budget, fork, and environment restrictions.

## 39. Pull Request Evidence Package

Required evidence:

- change summary;
- selected task IDs;
- requirements and ADRs;
- files and migrations changed;
- APIs, schemas, errors, events, permissions, and metrics changed;
- tests added or updated;
- commands executed;
- results and coverage impact;
- security and secret scans;
- migration and RLS results;
- accessibility and visual evidence;
- environment impact;
- documentation and changelog updates;
- untested risks and follow-up tasks;
- release and rollback considerations.

## 40. Runbook Registry

Every runbook includes:

- stable runbook ID;
- title;
- trigger and symptoms;
- scope and environment;
- severity;
- required role and recent authentication;
- prerequisites;
- safety and halt conditions;
- commands or tools;
- step sequence;
- expected evidence;
- validation checks;
- rollback or stop conditions;
- secret-handling notes;
- related incidents, services, alerts, tests, and ADRs;
- owner, version, last review, and next review.

## 41. Runbook Execution Boundary

The portal presents runbooks read-only by default.

Any executable helper requires:

- approved allowlisted operation;
- isolated environment;
- role authorization;
- recent authentication;
- explicit target;
- confirmation;
- idempotency and concurrency controls;
- no arbitrary shell or SQL;
- secret-safe input handling;
- audit event;
- validation and stop conditions.

## 42. Runbook Execution Evidence

Required fields:

- execution ID;
- runbook ID and version;
- trigger;
- incident or release reference;
- actor;
- environment and targets;
- start and finish timestamps;
- steps attempted;
- outcomes;
- redacted command references;
- evidence artifacts;
- validation checks;
- rollback or stop state;
- unresolved items;
- audit references.

Failed attempts remain visible.

## 43. Runbook Testing

Runbooks should have:

- syntax and link checks;
- prerequisite checks;
- isolated dry-run where practical;
- scripted helper tests;
- failure and stop-condition tests;
- secret-redaction tests;
- restore or recovery drills;
- periodic review evidence.

A stale or untested critical runbook blocks applicable promotion.

## 44. Contributor Getting Started

Required content:

- product and safety scope;
- repository structure;
- prerequisite versions;
- clone and bootstrap;
- environment-file template handling;
- local Supabase and Auth;
- backend and frontend startup;
- fake Binance and Gemini providers;
- seed data;
- one-shot research cycle;
- tests, lint, type, formatting, security scans, builds, and docs checks;
- reset and cleanup;
- common failures;
- Windows 11 and Unix-like commands;
- contribution workflow and task selection.

No paid credential should be required for ordinary setup.

## 45. Command Catalog

Every documented command includes:

- command ID;
- purpose;
- supported platforms;
- prerequisites;
- working directory;
- environment profile;
- secret requirements;
- side effects;
- expected output;
- failure modes;
- cleanup or rollback;
- source script;
- tests;
- version.

Commands should call repository scripts rather than duplicate hidden logic.

## 46. Documentation Build

The documentation build must:

- read repository Markdown and generated catalogs;
- validate front matter and IDs;
- resolve links and references;
- render Mermaid or diagrams safely;
- sanitize HTML;
- generate search index;
- generate API and schema references;
- include source revision and hashes;
- separate public and authenticated output;
- fail on critical conflicts or drift;
- produce an immutable artifact.

## 47. Public Documentation Boundary

Public documentation may include:

- product scope and brand;
- approved architecture overview;
- public API reference where intended;
- methodology;
- Trust Center;
- contributor setup for open-source portions;
- responsible disclosure.

It must exclude:

- secrets and secret metadata that increases risk;
- private incidents and findings;
- internal environment identifiers;
- private source or deployment details;
- unrestricted audit or financial evidence;
- privileged runbook commands;
- hidden provider or security configuration.

## 48. Documentation Search

Search supports:

- titles and headings;
- canonical IDs;
- requirements, tasks, ADRs, APIs, schemas, errors, events, permissions, metrics, invariants, tests, runbooks, and commands;
- approved source symbols where authorized;
- filters for category, status, owner, environment, version, and freshness.

Search must preserve authorization and avoid indexing secrets or private evidence.

## 49. Changelog and Release Notes

Every material change records:

- version or date;
- task and requirement references;
- user-visible behavior;
- API/schema compatibility;
- migration impact;
- security and privacy impact;
- operational impact;
- deprecations;
- known limitations;
- upgrade and rollback notes;
- release references.

Generated release notes must be reviewed before publication.

## 50. Compatibility and Deprecation

Required fields:

- affected contract;
- old and new versions;
- compatibility classification;
- deprecation announcement;
- replacement;
- migration guide;
- support window;
- telemetry and usage evidence where applicable;
- removal gate;
- owner and approval.

Breaking changes require versioning and explicit migration evidence.

## 51. Page-State Matrix

Explicit states include:

- loading;
- no documents;
- no results;
- document authoritative;
- stale;
- conflicting;
- superseded;
- generated;
- generation failed;
- broken link;
- invalid metadata;
- OpenAPI drift;
- schema drift;
- migration modified;
- requirement gap;
- task gap;
- implementation gap;
- test gap;
- invariant uncovered;
- runbook stale;
- runbook failed;
- test run passed;
- test run failed;
- test run partial;
- flaky quarantine expired;
- provider smoke unavailable;
- unauthorized;
- not found;
- backend unavailable;
- schema mismatch;
- export unavailable.

Critical evidence failures must not render as ordinary empty states.

## 52. Responsive Behavior

Requirements:

- repository revision and blockers remain visible;
- documentation navigation supports deep hierarchies on mobile;
- code, schema, API, traceability, and test tables provide narrow-layout alternatives;
- long paths, symbols, hashes, commands, and IDs wrap or copy safely;
- diagrams have text alternatives;
- API examples remain readable without horizontal page overflow;
- no critical evidence is hover-only;
- sticky navigation does not obscure anchors or focus.

## 53. Accessibility Requirements

The portal targets WCAG 2.2 AA where practical.

Required behavior:

- skip links, landmarks, headings, and consistent navigation;
- keyboard-accessible trees, tables, tabs, disclosures, API examples, search, diagrams, and filters;
- visible focus;
- semantic code and preformatted content;
- text alternatives for diagrams and traceability graphs;
- status announcements for build or test updates;
- no reliance on color alone;
- reflow at 200% and relevant 400% zoom;
- reduced motion;
- safe copy controls;
- language and code-language attributes.

## 54. Security and Authority Boundaries

The portal must not:

- expose secrets, tokens, cookies, connection strings, private keys, or invitation tokens;
- run arbitrary shell, SQL, workflow, provider, or exchange commands;
- permit unrestricted production API calls;
- expose private source content to unauthorized users;
- edit applied migrations;
- mark tasks complete from coverage alone;
- accept generated docs without source and drift checks;
- suppress failed tests, findings, stale runbooks, or traceability gaps;
- allow AI-generated changes to bypass code review;
- enable live trading or private exchange access.

## 55. Privacy and Data Minimization

The portal must minimize:

- contributor identities;
- pull request and commit metadata;
- test failure payloads;
- incident and runbook evidence;
- source paths and symbols in public output;
- support and diagnostic data;
- provider smoke metadata.

Production data and personal data are prohibited from fixtures, examples, and ordinary test evidence.

## 56. Observability

Safe telemetry may include:

- documentation build outcome and duration;
- broken links and invalid metadata counts;
- stale and conflicting document counts;
- generated drift counts;
- API/schema/error/event/permission/metric catalog coverage;
- traceability gap counts;
- test run and invariant coverage outcomes;
- flaky quarantine counts;
- runbook review and drill outcomes;
- search results by safe category;
- public/authenticated build status;
- export outcome;
- client and documentation build versions.

Telemetry must not include raw source content, secrets, test payloads, private search queries, or unrestricted failure output.

## 57. Testing Strategy

### Contract Tests

Validate document, API, schema, error, event, permission, metric, requirement, task, traceability, ADR, test, invariant, runbook, command, build, and export schemas.

### Documentation Tests

Validate front matter, IDs, links, anchors, precedence, freshness, conflicts, terminology, product identity, language, Mermaid, sanitization, and public/private boundaries.

### Generated Artifact Tests

Validate OpenAPI, type generation, migration manifest, permission matrix, catalogs, task index, test inventory, SBOM summary, hashes, source revision, and drift.

### API Explorer Tests

Validate operation inventory, schemas, permissions, errors, examples, synthetic values, environment restrictions, redaction, allowlists, and no unsafe execution.

### Traceability Tests

Validate requirement-to-task, task-to-source, source-to-test, migration, API, documentation, release, and deployment relationships; detect gaps and conflicts.

### Test Evidence Tests

Validate test-run parsing, commands, tool versions, counts, artifacts, coverage, failures, retries, flakes, provider classifications, and release linkage.

### Runbook Tests

Validate metadata, triggers, prerequisites, steps, stop conditions, validation, links, redaction, dry runs, helper scripts, drills, and review expiry.

### Contributor Setup Tests

Validate documented bootstrap, reset, fake-provider flow, one-shot cycle, test commands, Windows 11, and Unix-like commands in clean environments where practical.

### Accessibility Tests

Validate navigation, trees, code, API examples, tables, diagrams, search, focus, zoom, reflow, contrast, and screen-reader summaries.

### Security and Privacy Tests

Validate authorization, public/private separation, secret scanning, safe examples, test-data policy, source minimization, no arbitrary execution, sanitization, and export redaction.

### Visual Regression

Capture portal home, API operation, schema, task traceability, ADR, test run, invariant gap, runbook, stale document, conflict, generated drift, public docs, mobile, and error states.

## 58. Acceptance Criteria

Sprint 14 documentation is accepted when:

1. every portal page identifies repository and documentation revision;
2. authoritative documents have stable identity, ownership, version, review, supersession, and freshness evidence;
3. links, IDs, terminology, conflicts, and generated artifacts are validated in CI;
4. OpenAPI operations expose authentication, permissions, schemas, errors, idempotency, pagination, examples, tests, and compatibility;
5. schemas, errors, events, permissions, metrics, requirements, tasks, ADRs, tests, invariants, runbooks, and commands have versioned catalogs;
6. traceability connects requirements through tasks, design, code, migrations, tests, docs, release, and deployment;
7. modified applied migrations, uncovered critical invariants, undocumented public errors, and stale critical runbooks are release blockers;
8. test evidence preserves revision, environment, command, tool versions, counts, coverage, failures, artifacts, and retry behavior;
9. flaky tests require owner, issue, expiry, and remediation rather than blind reruns;
10. runbook execution remains allowlisted, role-controlled, idempotent, audited, and non-arbitrary;
11. contributor setup works with fake providers and no paid secrets on Windows 11 and Unix-like systems;
12. public docs are built separately and reveal no private operational evidence;
13. no arbitrary API, shell, SQL, workflow, provider, exchange, migration-edit, AI-bypass, secret, or live-trading authority is introduced;
14. security, privacy, accessibility, documentation, generation, traceability, test, runbook, setup, and export gates are explicit.

## 59. Definition of Done

The Sprint 14 specification is complete when:

- this document is committed;
- `SPRINT_14_TASKS.md` is committed;
- terminology matches AGENTS, product, architecture, API, database, testing, deployment, security, observability, all workspace specifications, and task files;
- all document, generated artifact, API, schema, catalog, requirement, task, traceability, ADR, test, invariant, runbook, command, setup, changelog, compatibility, responsive, accessibility, and authority states are explicit;
- both commits are fetched and verified.

## 60. Next Sprint Boundary

Sprint 15 defines the **Performance, Resilience, Capacity, SLO, Cost, Quota, and FinOps Evidence Workspace**, including measured API and cycle latency, backtest resource limits, provider quotas and budgets, free-tier constraints, cold starts, database capacity, resilience tests, SLI/SLO definitions, error budgets, capacity forecasts, cost attribution, and scale-trigger evidence without inventing guarantees or enabling unsafe automatic infrastructure changes.
