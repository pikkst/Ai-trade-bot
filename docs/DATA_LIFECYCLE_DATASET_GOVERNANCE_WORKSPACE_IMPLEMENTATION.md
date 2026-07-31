# Data Lifecycle, Dataset Registry, Quality, Retention, Archival, Export, Deletion, Anonymization, and Reproducibility Preservation Workspace Specification

Last reviewed: 2026-07-31  
Status: Sprint 16 authoritative data lifecycle and dataset-governance specification

## 1. Purpose

This document defines the implementation contract for the Data Lifecycle, Dataset Registry, Quality, Retention, Archival, Export, Deletion, Anonymization, and Reproducibility Preservation Workspace of The Daily Roast AI.

The workspace explains which immutable datasets exist, how they were created, which records and versions they contain, whether they passed quality gates, which analyses and experiments depend on them, how long each data class is retained, when evidence may be archived or deleted, which records must remain for accounting, audit, incident, or reproducibility purposes, and how exports and restoration preserve hashes, lineage, schemas, and limitations.

The workspace is integrity-first. It must not silently rewrite historical market data, break required financial or audit lineage, delete evidence needed to reproduce a report, mix personal-account data with public research datasets, or present archived or invalidated data as current approved evidence.

## 2. Scope

Sprint 16 covers:

- dataset registry, detail, version, lineage, quality, retention, archive, export, deletion, anonymization, and reproducibility routes;
- canonical dataset types and immutable dataset versions;
- record manifests, schema versions, content hashes, source references, and time ranges;
- raw, validated, derived, research, financial, audit, operational, personal, and public data classes;
- market-candle, symbol-metadata, snapshot, feature, Gemini-report, strategy, risk, order, fill, ledger, portfolio, backtest, experiment, incident, audit, observability, test, documentation, and release evidence lineage;
- quality rules, completeness, gap, duplicate, ordering, correction, drift, contamination, and validation evidence;
- dataset status, approval, invalidation, supersession, and promotion;
- retention policy versions, cleanup schedules, evidence holds, and legal/incident review status;
- archival tiers, restore verification, and access boundaries;
- deletion planning, dependency analysis, tombstones, deletion proof, and prohibited deletion categories;
- anonymization, pseudonymization, aggregation, and re-identification-risk evidence;
- account/profile data separation from immutable operational and financial evidence;
- reproducibility manifests for backtests, experiments, reports, and releases;
- authorized export packages and integrity verification;
- dataset access permissions, environment boundaries, and public/private classifications;
- responsive, accessible, secure, observable, and testable presentation.

Sprint 16 does not implement:

- silent destructive cleanup;
- deletion of ledger, fill, risk, audit, reconciliation, or release evidence required by integrity policy;
- mutation of applied migration history;
- automatic public publication of private datasets;
- arbitrary SQL or object-storage browser access;
- irreversible anonymization without preview, policy, and validation;
- legal determinations or compliance certification;
- unrestricted raw Gemini prompt or provider-response retention;
- training external models on private user or experiment data;
- live trading or private Binance execution.

## 3. User Outcomes

An owner, operator, engineer, reviewer, or authorized user should be able to answer:

1. Which dataset or evidence package am I viewing?
2. What is its immutable version, schema, hash, source, period, and record count?
3. Is it raw, validated, derived, financial, audit, operational, personal, public, or archived?
4. Which quality gates passed, failed, or remain unavailable?
5. Which source records and transformations produced it?
6. Which snapshots, features, Gemini reports, decisions, orders, fills, ledgers, portfolios, backtests, experiments, incidents, reports, and releases depend on it?
7. Was a source correction detected, and which derived artifacts became invalid or superseded?
8. Which retention policy applies, and when is review, archive, or cleanup due?
9. Is an evidence hold active because of an experiment, incident, security review, release, or reproducibility requirement?
10. Can the data be archived without breaking active workflows?
11. Can the data be deleted, anonymized, aggregated, or only access-restricted?
12. Which dependencies block deletion?
13. Which immutable tombstone and proof show what was deleted and why?
14. Does an export include schemas, hashes, lineage, quality, permissions, and limitations?
15. Can a backtest or experiment be reproduced from the retained manifest?
16. Which personal profile data can be changed or removed separately from required audit evidence?
17. Which data is permitted in public demo, CI fixtures, support packages, or provider requests?
18. Did archival, restore, cleanup, deletion, or anonymization complete safely?

## 4. Canonical Routes

```text
/data
/data/datasets
/data/datasets/:datasetId
/data/datasets/:datasetId/versions/:versionId
/data/datasets/:datasetId/lineage
/data/datasets/:datasetId/quality
/data/datasets/:datasetId/retention
/data/datasets/:datasetId/archive
/data/datasets/:datasetId/exports
/data/datasets/:datasetId/deletion
/data/datasets/:datasetId/anonymization
/data/retention-policies
/data/cleanup-runs
/data/evidence-holds
/data/reproducibility
/data/reproducibility/:manifestId
/data/access
```

The workspace must link to market evidence, Gemini analyses, decisions, portfolio, backtests, experiments, audit, governance, privacy, backups, developer traceability, releases, and incidents.

## 5. Information Architecture

The dataset detail page is ordered as follows:

1. data class, environment, approval, quality, retention, hold, and access state;
2. dataset identity, version, schema, hash, period, and record manifest;
3. source and transformation lineage;
4. quality checks and unresolved issues;
5. downstream dependencies and invalidation impact;
6. retention, archive, and evidence-hold policy;
7. export and reproducibility evidence;
8. anonymization or deletion eligibility;
9. cleanup, restore, incident, and audit history;
10. limitations and authorized commands.

Invalid, contaminated, unverified, held, deletion-blocked, or lineage-incomplete state must visually dominate ordinary record counts or storage savings.

## 6. Recommended Read Models

Recommended dataset contract:

```ts
interface DatasetGovernanceReadModel {
  schemaVersion: string;
  dataset: DatasetIdentity;
  version: DatasetVersionSummary;
  classification: DataClassificationSummary;
  manifest: DatasetManifestSummary;
  quality: DataQualitySummary;
  lineage: DatasetLineageSummary;
  dependencies: DatasetDependencySummary;
  retention: RetentionPolicyApplicationSummary;
  holds: EvidenceHoldSummary[];
  archive: ArchiveStateSummary;
  deletion: DeletionEligibilitySummary;
  anonymization: AnonymizationEligibilitySummary;
  reproducibility: ReproducibilityManifestReference[];
  access: DatasetAccessSummary;
  diagnostics: DiagnosticSummary[];
  limitations: LimitationSummary[];
  permissions: DatasetCommandPermissions;
  links: DatasetResourceLinks;
}
```

Recommended reproducibility contract:

```ts
interface ReproducibilityManifestReadModel {
  schemaVersion: string;
  manifest: ReproducibilityManifestIdentity;
  target: ReproducibleTargetReference;
  datasets: ReproducibilityDatasetReference[];
  schemas: VersionReference[];
  configurations: VersionReference[];
  code: CodeProvenanceSummary;
  dependencies: DependencyProvenanceSummary;
  migrations: MigrationReference[];
  providerEvidence: ProviderEvidenceReference[];
  randomSeeds: RandomSeedReference[];
  expectedHashes: ExpectedArtifactHash[];
  retentionRequirements: RetentionRequirementSummary[];
  verification: ReproducibilityVerificationSummary;
  limitations: LimitationSummary[];
}
```

Recommended deletion contract:

```ts
interface DataDeletionPlanReadModel {
  schemaVersion: string;
  plan: DataDeletionPlanIdentity;
  target: DataTargetReference;
  policy: RetentionPolicyReference;
  dependencies: DataDependencyCheck[];
  prohibitedReasons: DataDeletionBlocker[];
  archivePrerequisite: ArchivePrerequisiteSummary | null;
  anonymizationAlternative: AnonymizationAlternativeSummary | null;
  preview: DeletionPreviewSummary;
  approvals: ApprovalReference[];
  execution: DeletionExecutionSummary | null;
  proof: DeletionProofSummary | null;
}
```

The frontend must not calculate dataset approval, quality, dependency completeness, retention due dates, deletion eligibility, anonymization sufficiency, or reproducibility verification.

## 7. Dataset Identity

Required fields:

- immutable dataset ID;
- dataset type;
- workspace and environment scope;
- name and safe description;
- owner;
- current version reference;
- lifecycle state;
- data classification;
- source system or provider;
- creation timestamp;
- first and last effective timestamps;
- record count;
- schema version;
- manifest hash;
- quality state;
- retention policy;
- access profile;
- archive state;
- public/private status;
- active hold and incident references.

Dataset names must not contain secrets or unnecessary personal identifiers.

## 8. Dataset Types

Canonical types may include:

- exchange symbol metadata;
- finalized market candles;
- raw transport payload samples under bounded retention;
- market snapshots;
- deterministic feature sets;
- validated Gemini report datasets;
- strategy and risk evaluation datasets;
- paper orders, fills, and execution evidence;
- ledger and portfolio state evidence;
- backtest input, event, trade, and report datasets;
- experiment cycle and report datasets;
- audit and incident evidence;
- observability aggregates;
- security and release evidence;
- test fixtures and evaluation datasets;
- documentation and generated-reference artifacts;
- account profile and membership data;
- public demo datasets.

Each type requires a versioned schema and classification.

## 9. Data Classification

Required classifications:

- public;
- internal;
- restricted operational;
- restricted financial evidence;
- restricted security evidence;
- personal account data;
- secret or credential material;
- prohibited for persistence.

Secret or credential material must not become a normal dataset. Detection creates a security incident and remediation workflow.

## 10. Dataset Version Contract

Every version includes:

- immutable version ID;
- parent or predecessor version;
- schema version;
- source versions;
- transformation version;
- configuration hash;
- ordered record or partition manifest;
- content hash;
- record count;
- byte size;
- time range;
- creation job and revision;
- quality result;
- approval state;
- supersession and invalidation references;
- retention requirements;
- access classification.

Used dataset versions are immutable.

## 11. Dataset Lifecycle

Supported states include:

- registering;
- ingesting;
- validating;
- quarantined;
- approved;
- approved with limitations;
- active;
- frozen by reproducibility requirement;
- correction pending;
- invalidated;
- superseded;
- archived;
- deletion pending;
- deleted with tombstone;
- unavailable.

Every transition is versioned, authorized, and audited.

## 12. Record Manifest Contract

Required fields:

- manifest ID and version;
- partition or object references;
- ordered record identity strategy;
- first and last record timestamps;
- record count;
- byte size;
- schema version;
- partition hashes;
- aggregate content hash;
- compression and serialization;
- encryption state;
- storage tier;
- creation source;
- verification result.

Manifests must not expose secret storage URLs or credentials.

## 13. Schema and Serialization Contract

Required fields:

- schema ID and semantic version;
- field names, types, formats, units, nullability, enums, ranges, and constraints;
- serialization format and version;
- timezone and decimal rules;
- ordering and identity rules;
- compatibility classification;
- migration or transformation guidance;
- source and generated type references;
- tests and hash.

Schema drift must not be hidden inside a dataset label.

## 14. Source Provenance

Required provenance:

- provider or source system;
- adapter and configuration version;
- request, ingestion, import, or transformation job;
- source timestamps;
- source record IDs or bounded references;
- provider server time where relevant;
- input dataset versions;
- code commit;
- dependency and migration versions;
- actor or workflow identity;
- correlation IDs;
- source hashes;
- limitations.

## 15. Transformation Lineage

Each transformation records:

- transformation ID and version;
- input datasets and versions;
- output dataset and version;
- code revision;
- configuration;
- deterministic or probabilistic classification;
- random seed where applicable;
- execution environment;
- start and finish time;
- quality checks;
- warnings;
- output hash;
- audit evidence.

Probabilistic Gemini output is not treated as a deterministic data transformation until validated and persisted under the project schema.

## 16. Dataset Lineage Graph

Supported relationships:

- sourced from;
- validates;
- transforms into;
- snapshots;
- derives features from;
- analyzes;
- authorizes or informs;
- executes from;
- accounts for;
- benchmarks against;
- reproduces;
- invalidates;
- supersedes;
- archives;
- exports.

The graph must preserve direction, version, status, timestamp, and authorization. A text/table alternative is required.

## 17. Data Quality Rule Registry

Every rule includes:

- stable rule ID;
- dataset type;
- description;
- severity;
- validator version;
- input fields or relationships;
- expected condition;
- tolerance;
- failure code;
- quarantine or block behavior;
- tests;
- owner;
- activation and archive state.

## 18. Market Data Quality Rules

Required rules include:

- positive prices;
- OHLC invariants;
- non-negative volume;
- close after open;
- valid interval boundaries;
- recognized symbol and metadata version;
- finalized state;
- uniqueness;
- deterministic ordering;
- gap detection;
- provider timestamp and clock drift;
- precision and decimal validity;
- content-hash determinism.

Only approved, fresh, finalized data may feed normal downstream workflows.

## 19. Derived Data Quality Rules

Required checks may include:

- exact input snapshot reference;
- feature warm-up sufficiency;
- null and finite-value handling;
- formula and feature-set version;
- output length and alignment;
- deterministic hash;
- schema validation;
- no future-data dependency;
- report evidence grounding;
- strategy and risk input completeness;
- ledger and reconciliation consistency;
- benchmark period compatibility.

## 20. Quality Run Contract

Required fields:

- quality-run ID;
- dataset and version;
- rule-set version;
- source revision;
- start and finish;
- checks executed;
- pass, warning, failure, unavailable, and not-applicable counts;
- sample or full-scan mode;
- failed record references;
- quarantine result;
- approval outcome;
- artifacts;
- limitations.

## 21. Quality States

Supported states:

- approved;
- approved with warning;
- incomplete;
- stale;
- duplicate detected;
- invalid value;
- out of order;
- gap detected;
- provider unavailable;
- correction pending;
- contaminated;
- schema mismatch;
- lineage incomplete;
- quality unavailable.

Missing quality evidence must not appear approved.

## 22. Quarantine Contract

Quarantined data requires:

- quarantine ID;
- dataset/version or record scope;
- reason codes;
- detection time;
- source job;
- affected downstream resources;
- access restrictions;
- remediation owner;
- correction or rejection decision;
- terminal state;
- audit and incident references.

Quarantined data cannot feed normal strategy, risk, execution, reporting, or benchmark workflows.

## 23. Source Correction Contract

When a finalized source record changes:

1. detect and persist correction evidence;
2. preserve original record and hash;
3. create a new source version or replacement record;
4. identify all dependent datasets and artifacts;
5. mark affected snapshots, features, reports, decisions, backtests, and summaries invalid or superseded according to policy;
6. preserve financial and audit evidence without rewriting history;
7. require explicit recomputation or comparison;
8. record incident and audit evidence where material.

## 24. Dependency Registry

Every dependency includes:

- source and target dataset or resource;
- exact versions;
- relationship type;
- required or optional status;
- creation timestamp;
- consuming revision;
- retention impact;
- deletion impact;
- invalidation propagation policy;
- verification state.

Missing required dependencies are integrity failures.

## 25. Dataset Promotion

Promotion may move a dataset from quarantine or validation into approved research use.

Requirements:

- complete manifest and hashes;
- approved schema;
- passed quality rule set;
- complete lineage;
- privacy and access classification;
- retention policy;
- no secret or prohibited data;
- environment compatibility;
- owner approval where required;
- immutable transition and audit;
- no impact on frozen active experiments without explicit new version.

## 26. Public Dataset Promotion Boundary

Public promotion additionally requires:

- public classification;
- personal and secret-data scan;
- provider-license and redistribution review;
- aggregation or delay policy where needed;
- incident and security review;
- public schema and documentation;
- reproducibility and limitations;
- owner approval;
- immutable published version.

Public status is never inferred from internal accessibility.

## 27. Retention Policy Registry

Every policy includes:

- stable policy ID and version;
- data class and dataset types;
- environment;
- minimum and maximum retention;
- active, archive, and deletion stages;
- cleanup schedule;
- evidence-hold rules;
- lineage and reproducibility constraints;
- personal-data handling;
- incident and security overrides;
- owner and approval;
- activation, review, and archive dates;
- limitations.

## 28. Baseline Retention Principles

Baseline principles:

- validated candles and snapshot lineage are retained indefinitely for project reproducibility until an approved policy changes;
- raw transport payloads have bounded configurable retention;
- ledger, fills, risk decisions, reconciliations, experiment lifecycle, and audit evidence are retained according to financial-integrity and governance policy;
- raw Gemini prompts and provider responses are minimized and bounded;
- derived caches may be rebuilt and may have shorter retention when manifests remain;
- account profile data is separated from immutable audit references;
- test and observability data use bounded retention and synthetic inputs.

Actual policy values remain versioned configuration rather than assumptions in the UI.

## 29. Evidence Hold Contract

Hold triggers may include:

- active or reproducible experiment;
- backtest or report verification;
- unresolved data correction;
- security incident;
- privacy investigation;
- audit or release review;
- legal review where documented;
- failed reconciliation or restore;
- pending deletion appeal or validation.

Every hold includes scope, reason, owner, start, review, expiry or indefinite state, affected policies, release conditions, and audit evidence.

## 30. Cleanup Run Contract

Required fields:

- cleanup-run ID;
- policy version;
- environment;
- planned and actual start;
- candidates discovered;
- excluded by hold;
- archived;
- anonymized;
- deleted;
- failed;
- bytes reclaimed;
- dependency and integrity checks;
- dry-run or execute mode;
- approvals;
- error codes;
- audit and artifacts;
- terminal outcome.

Dry-run preview is required before destructive execution.

## 31. Archival Contract

Required fields:

- archive ID;
- dataset/version scope;
- source and target storage tier;
- manifest and hash;
- compression and encryption;
- access policy;
- archive timestamp;
- restore procedure and runbook;
- retention and hold state;
- cost class;
- verification;
- audit reference.

Archival must preserve immutable identity and reproducibility references.

## 32. Archive Tiers

Possible tiers:

- active database;
- active object storage;
- warm archive;
- cold archive;
- offline controlled export;
- tombstone-only record after approved deletion.

Each tier requires access, retrieval, integrity, cost, and recovery semantics.

## 33. Archive Restore Contract

Required evidence:

- restore-run ID;
- archive and manifest references;
- target isolated environment;
- start and finish;
- bytes and records restored;
- hash verification;
- schema and migration compatibility;
- quality rerun;
- lineage verification;
- reconciliation where financial evidence applies;
- outcome and limitations.

Archive readiness requires successful restore evidence.

## 34. Deletion Eligibility

Deletion evaluation checks:

- data classification;
- retention period;
- active evidence hold;
- dependency count and criticality;
- reproducibility manifest requirements;
- financial, audit, security, or release evidence status;
- account-data separation;
- provider or license constraints;
- archive prerequisite;
- anonymization alternative;
- approval requirements;
- policy and environment.

Unknown dependency state blocks deletion.

## 35. Prohibited Deletion Categories

Baseline prohibited categories include evidence required to preserve:

- balanced ledger and financial history;
- fills and paper-order lineage;
- deterministic risk approvals and rejections;
- reconciliation and correction history;
- experiment lifecycle, cycle validity, incidents, and halts;
- immutable audit events;
- release approvals and deployment evidence;
- security incident evidence under active policy;
- reproducibility manifests and required source hashes.

Policy may archive or restrict access, but must not silently erase required integrity evidence.

## 36. Deletion Plan Contract

Required fields:

- plan ID;
- target scope;
- policy;
- discovery snapshot;
- dependencies;
- blockers;
- archive prerequisite;
- anonymization alternative;
- dry-run preview;
- expected records and bytes;
- approvals;
- execution window;
- stop conditions;
- rollback limitations;
- audit reference.

## 37. Deletion Command Boundary

Deletion commands require:

- owner authorization;
- recent authentication;
- idempotency key;
- expected version;
- exact immutable plan hash;
- completed dry run;
- no active blockers or holds;
- required archive and restore verification;
- explicit confirmation;
- bounded target;
- audit event;
- no arbitrary table, SQL, or object-store input.

## 38. Deletion Execution and Proof

Required evidence:

- execution ID;
- plan reference and hash;
- actor;
- start and finish;
- target partitions or bounded resources;
- records and bytes deleted;
- failures and skipped items;
- post-delete dependency check;
- integrity and RLS verification;
- tombstone record;
- deletion-proof hash;
- audit and incident references;
- limitations.

Deletion proof records what was removed without retaining the deleted sensitive payload.

## 39. Tombstone Contract

A tombstone includes:

- original dataset or version ID;
- deletion-plan and execution references;
- data classification;
- high-level scope;
- schema and manifest hashes;
- record count and byte count;
- deletion timestamp;
- reason and policy;
- actor;
- proof hash;
- surviving dependencies and redirects;
- public/private visibility.

## 40. Anonymization Contract

Required fields:

- plan ID and version;
- source data class;
- target purpose;
- fields and relationships affected;
- technique: removal, tokenization, pseudonymization, generalization, aggregation, noise, or suppression;
- key-management boundary;
- utility requirements;
- re-identification-risk method;
- preview;
- validation;
- approvals;
- output dataset version;
- limitations.

Pseudonymization is not anonymization when re-linking remains possible.

## 41. Anonymization Validation

Required checks:

- direct identifier removal;
- quasi-identifier review;
- rare-category and small-group risk;
- cross-dataset linkage risk;
- free-text and log scanning;
- timestamp precision;
- location precision where applicable;
- reversible token access controls;
- utility and reproducibility impact;
- public-release suitability;
- reviewer and test evidence.

## 42. Account Data Separation

Mutable account/profile data must be separated from immutable evidence through stable internal references.

Requirements:

- profile display fields can be corrected or removed according to policy;
- audit and approval records preserve a bounded actor reference;
- account closure does not rewrite financial or security history;
- deleted profile data does not remain in search, notifications, support packages, or caches;
- re-identification access is restricted;
- exports distinguish profile data from immutable operational evidence.

## 43. Reproducibility Manifest

Required fields:

- immutable manifest ID;
- target type and ID;
- dataset versions and hashes;
- ordered record or partition manifests;
- schema versions;
- configuration versions and hashes;
- code commit;
- dependency lock hashes;
- migration revision;
- provider evidence versions;
- prompt and validation versions where applicable;
- random seeds;
- execution model and accounting policy;
- expected output hashes;
- retention requirements;
- verification and limitations.

## 44. Reproducibility Preservation Policy

A target remains reproducible only when:

- required dataset versions are retained or restorable;
- manifests and hashes verify;
- schemas and transformations remain available;
- code, dependencies, and migrations are identified;
- provider evidence is preserved at the approved abstraction level;
- random and timing policies are known;
- configuration is immutable;
- expected output or report hashes remain accessible;
- limitations are explicit.

## 45. Reproducibility Verification

Required comparisons:

- manifest completeness;
- dataset and partition hashes;
- schema compatibility;
- code/dependency/migration identity;
- configuration hashes;
- event ordering;
- expected outputs;
- report, ledger, state, and export hashes;
- archived restore integrity;
- missing external-provider dependencies.

Possible outcomes:

- verified;
- verified with limitations;
- mismatch;
- incomplete;
- unavailable.

## 46. Dataset Access Contract

Required fields:

- dataset and version;
- classification;
- workspace and environment scope;
- canonical permission codes;
- role defaults;
- RLS or storage-policy references;
- purpose restriction;
- provider-export restriction;
- public visibility;
- download/export permission;
- recent-authentication requirement;
- last review and findings.

Access permission does not imply deletion or publication permission.

## 47. Environment Data Boundaries

Required rules:

- CI uses synthetic or approved fixtures;
- public demo uses approved public/sample/delayed datasets;
- local development avoids production credentials and personal data;
- paper experiment uses dedicated project and frozen data lineage;
- staging uses synthetic or explicitly approved data;
- production research remains authenticated and paper-only;
- cross-environment copies require manifest, classification, approval, and audit;
- secrets are never copied as dataset content.

## 48. Provider Request Data Boundary

Gemini and other provider requests must use:

- minimum structured evidence;
- approved fields and schemas;
- no credentials or personal data;
- no unrestricted raw logs or database rows;
- versioned purpose and retention classification;
- provider terms and regional-readiness evidence;
- request hashes and source references;
- bounded raw-response retention.

## 49. Test and Fixture Data Governance

Requirements:

- synthetic or public-approved data by default;
- deterministic fixture IDs and hashes;
- no production personal or financial payloads;
- explicit provider-test classification;
- bounded fixture size;
- schema and quality validation;
- retention and update policy;
- secret scanning;
- linkage to tests and source revision.

## 50. Export Contract

Authorized dataset exports include:

- dataset manifest;
- quality report;
- lineage package;
- retention and hold package;
- archive package;
- reproducibility package;
- deletion plan and proof;
- anonymization report;
- account-data package according to policy;
- public dataset package.

Every export includes schema and generation versions, dataset/version identity, hashes, source, period, record counts, classification, quality, lineage, retention, holds, access, limitations, and authorization context without secrets.

## 51. Export Package Integrity

Required evidence:

- package ID;
- manifest;
- file/object list;
- hashes;
- schema versions;
- compression and encryption state;
- generation revision;
- authorization and purpose;
- expiration or access policy;
- verification command or procedure;
- restore/import test;
- limitations.

## 52. Import Boundary

Importing external data requires:

- approved dataset type and schema;
- bounded size and time range;
- source and license metadata;
- malware and content scan where applicable;
- secret and personal-data scan;
- quarantine;
- quality validation;
- manifest and hash generation;
- environment and access classification;
- owner approval before normal use.

## 53. Data Drift Contract

Drift may include:

- schema drift;
- source-distribution drift;
- missingness drift;
- symbol metadata drift;
- feature-distribution drift;
- provider-response drift;
- quality-rule outcome drift;
- label or evaluation-dataset drift;
- retention and access-policy drift.

Drift evidence must identify baseline, current window, method, samples, severity, limitations, and review state.

## 54. Data Incident Contract

Data incidents include:

- source correction;
- invalid or contaminated data used downstream;
- missing lineage;
- secret or personal data in a prohibited dataset;
- cross-environment leakage;
- unauthorized public exposure;
- failed archive restore;
- incorrect deletion;
- broken reproducibility;
- quality-gate bypass;
- retention cleanup failure.

Every incident links to affected datasets, downstream artifacts, containment, invalidation, correction, recovery, and audit evidence.

## 55. Page-State Matrix

Explicit states include:

- loading;
- no datasets;
- registering;
- ingesting;
- validating;
- quarantined;
- approved;
- approved with limitations;
- active;
- frozen;
- correction pending;
- invalidated;
- superseded;
- archive pending;
- archived;
- restore running;
- restore failed;
- retention due;
- hold active;
- cleanup dry run;
- cleanup failed;
- deletion blocked;
- deletion pending;
- deleted with tombstone;
- anonymization pending;
- anonymization failed;
- reproducibility verified;
- reproducibility mismatch;
- lineage incomplete;
- quality unavailable;
- schema mismatch;
- access denied;
- backend unavailable;
- export unavailable.

Missing quality or lineage evidence must not render as an approved empty state.

## 56. Responsive Behavior

Requirements:

- classification, quality, retention, hold, and access state remains first;
- manifest and schema tables provide narrow-layout alternatives;
- lineage graphs have ordered list/table alternatives;
- hashes, paths, versions, partition IDs, and policy IDs wrap or copy safely;
- deletion and anonymization controls remain separated from evidence;
- no critical state is hover-only;
- record and storage values retain units and source;
- diff and quality tables preserve context.

## 57. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- keyboard-accessible filters, tables, trees, lineage, diffs, disclosures, previews, and confirmations;
- text alternatives for graphs;
- visible focus;
- accessible definitions for dataset, manifest, lineage, quality, quarantine, retention, hold, archive, deletion, tombstone, anonymization, and reproducibility;
- no reliance on color alone;
- status announcements for lifecycle changes;
- reflow at 200% and relevant 400% zoom;
- reduced motion;
- screen-reader-readable counts, byte sizes, dates, hashes, and outcomes;
- safe copy controls.

## 58. Security and Authority Boundaries

The workspace must not:

- expose credentials, storage secrets, signed URLs, tokens, raw connection strings, or unrestricted provider payloads;
- allow arbitrary SQL, table, bucket, path, or object deletion;
- bypass RLS or storage policies;
- delete held, financial, audit, security, release, or reproducibility-required evidence;
- treat pseudonymization as irreversible anonymization;
- publish internal datasets automatically;
- import unscanned external data into normal workflows;
- mutate immutable source versions;
- weaken quality gates for storage savings;
- enable live trading or private exchange credentials.

## 59. Privacy and Data Minimization

The workspace must minimize:

- personal identity and membership data;
- raw provider payloads;
- search and support text;
- incident details;
- precise object paths;
- access-policy internals;
- account export data;
- deletion and anonymization previews.

Public exports and views require separate minimization and re-identification review.

## 60. Observability

Safe telemetry may include:

- datasets and versions by safe type/state;
- records and bytes by classification and tier;
- quality outcomes by rule code;
- quarantine and correction counts;
- lineage gap counts;
- retention due and cleanup outcomes;
- evidence holds;
- archive and restore outcomes;
- deletion plans, blockers, executions, and proof outcomes;
- anonymization outcomes;
- reproducibility verification results;
- export/import outcomes;
- access denials by safe category;
- data incidents;
- client and schema versions.

Telemetry must not include personal data, secret values, raw payloads, signed paths, or unbounded record identifiers.

## 61. Testing Strategy

### Contract Tests

Validate dataset, version, classification, manifest, schema, provenance, transformation, lineage, quality, quarantine, dependency, retention, hold, cleanup, archive, deletion, tombstone, anonymization, reproducibility, access, export, and incident schemas.

### Market Data Tests

Validate OHLC invariants, finalization, uniqueness, ordering, gaps, clock drift, precision, content hashes, correction lineage, and stale blocking.

### Derived Data Tests

Validate snapshot identity, feature alignment, no look-ahead, Gemini grounding, strategy/risk inputs, ledger/reconciliation, benchmark compatibility, and deterministic hashes.

### Quality and Quarantine Tests

Validate rule registry, full/sample scans, failure mapping, quarantine access, remediation, approval, and no downstream consumption.

### Lineage and Dependency Tests

Validate exact versions, required relationships, cycle detection, invalidation propagation, retention impact, deletion blockers, and authorization.

### Retention and Cleanup Tests

Validate policy application, schedules, holds, dry-run, candidates, exclusions, archive, anonymization, deletion, failures, bytes, idempotency, and audit.

### Archive and Restore Tests

Validate manifests, hashes, encryption metadata, isolated restore, schemas, migrations, quality, lineage, financial reconciliation, and cost evidence.

### Deletion Tests

Validate eligibility, prohibited categories, dependency completeness, plan hash, recent authentication, idempotency, expected version, confirmation, bounded execution, tombstones, proof, and post-delete checks.

### Anonymization Tests

Validate direct and quasi-identifiers, linkage risk, free text, timestamps, reversible tokens, utility, public suitability, and no false anonymization claims.

### Reproducibility Tests

Validate manifests, datasets, schemas, code, dependencies, migrations, configurations, seeds, provider evidence, output hashes, archive restore, and incomplete states.

### Security and Privacy Tests

Validate RLS, storage policies, environment boundaries, provider minimization, import quarantine, fixture scans, secret detection, public/private exports, and support-package boundaries.

### Accessibility Tests

Validate keyboard flow, lineage alternatives, tables, trees, definitions, previews, confirmations, focus, announcements, zoom, reflow, and contrast.

### Visual Regression

Capture registering, validating, quarantined, approved, correction, invalidated, frozen, retention due, hold, archived, restore failed, deletion blocked/pending/completed, anonymization, reproducibility mismatch, and lineage-gap states.

## 62. Acceptance Criteria

Sprint 16 documentation is accepted when:

1. every dataset has immutable identity, version, schema, manifest, hashes, classification, quality, retention, access, and lineage evidence;
2. used dataset versions are immutable;
3. source and transformation provenance includes code, configuration, dependencies, migrations, jobs, and input versions;
4. market and derived quality rules are versioned and executable;
5. quarantined, stale, invalid, contaminated, or lineage-incomplete data cannot feed normal workflows;
6. source corrections preserve originals and invalidate or supersede dependents without rewriting history;
7. retention policy, cleanup, archive, evidence hold, and deletion state are server-authoritative;
8. unknown dependencies or active holds block deletion;
9. financial, risk, ledger, reconciliation, experiment, audit, incident, and release evidence required for integrity cannot be silently deleted;
10. deletion requires immutable plan, dry run, approval, bounded execution, tombstone, and proof;
11. pseudonymization is not misrepresented as anonymization;
12. account profile data is separable from immutable actor and audit references;
13. reproducibility manifests preserve datasets, schemas, configurations, code, dependencies, migrations, provider evidence, seeds, and expected hashes;
14. archive readiness requires verified isolated restore;
15. public promotion requires privacy, license, quality, documentation, and approval evidence;
16. no arbitrary storage/SQL deletion, secret exposure, quality bypass, automatic publication, private exchange, or live-trading authority is introduced;
17. security, privacy, accessibility, quality, lineage, retention, archive, deletion, anonymization, reproducibility, access, and export gates are explicit.

## 63. Definition of Done

The Sprint 16 specification is complete when:

- this document is committed;
- `SPRINT_16_TASKS.md` is committed;
- terminology matches market data, database, Gemini, strategy, portfolio, backtest, experiments, audit, privacy, backups, performance, developer traceability, security, and testing documents;
- all dataset, classification, version, manifest, schema, source, transformation, lineage, quality, quarantine, correction, dependency, promotion, retention, hold, cleanup, archive, restore, deletion, tombstone, anonymization, account separation, reproducibility, access, environment, provider, fixture, export, import, drift, incident, accessibility, and authority states are explicit;
- both commits are fetched and verified.

## 64. Next Sprint Boundary

Sprint 17 defines the **Research Review, Strategy Lifecycle, Evidence Scoring, Decision Governance, and Promotion Workspace**, including hypothesis registry, research-plan approval, evidence completeness, backtest and paper-experiment comparison, robustness review, human sign-off, strategy version promotion, rollback, retirement, and explicit prohibition of automatic activation or live trading.
