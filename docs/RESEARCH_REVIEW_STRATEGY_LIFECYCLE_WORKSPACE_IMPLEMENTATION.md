# Research Review, Strategy Lifecycle, Evidence Scoring, Decision Governance, and Promotion Workspace Specification

Last reviewed: 2026-07-31  
Status: Sprint 17 authoritative research-review and strategy-lifecycle specification

## 1. Purpose

This document defines the implementation contract for the Research Review, Strategy Lifecycle, Evidence Scoring, Decision Governance, and Promotion Workspace of The Daily Roast AI.

The workspace turns research artifacts into an explicit, human-governed lifecycle. It connects hypotheses, research plans, dataset splits, strategy versions, backtests, benchmarks, robustness studies, reproducibility checks, paper experiments, incidents, costs, security and privacy gates, reviewer comments, owner decisions, promotion records, rollback plans, and retirement evidence.

The workspace must never equate a profitable backtest with approval, let Gemini promote or activate a strategy, conceal failed variants, bypass deterministic risk, automatically progress to Binance test or live environments, or mutate historical evidence after a decision.

## 2. Scope

Sprint 17 covers:

- research hypotheses, plans, reviews, evidence packages, scores, decisions, strategy lifecycle, promotion, rollback, suspension, retirement, and archive routes;
- hypothesis statement, rationale, falsification criteria, risks, datasets, benchmarks, costs, and planned analyses;
- pre-registered design, validation, final-test, walk-forward, and paper-experiment stages;
- strategy-version identity, parameters, feature dependencies, AI dependencies, risk compatibility, execution assumptions, and configuration hashes;
- complete evidence inventory across data, methods, backtests, variants, robustness, reproducibility, paper observation, incidents, costs, security, privacy, accessibility, and operations;
- rule-based evidence completeness and reviewer-oriented evidence scoring;
- qualitative and quantitative review dimensions without a single automatic approval score;
- reviewer assignments, conflicts, comments, requests for change, approvals, rejections, and owner decisions;
- lifecycle states from idea through research, paper validation, approved research use, suspension, retirement, and archive;
- activation only for approved future paper-research configurations;
- rollback, supersession, and retirement plans;
- evidence holds and reproducibility preservation;
- authorized export and audit lineage;
- responsive, accessible, secure, observable, and testable presentation.

Sprint 17 does not implement:

- automatic strategy generation and promotion;
- automatic parameter optimization as an approval mechanism;
- live trading;
- private Binance or test-environment execution;
- strategy activation from a model-generated recommendation;
- owner approval inferred from a score;
- deletion of failed, rejected, or unfavorable evidence;
- changing a running experiment’s frozen strategy;
- rewriting historical decisions;
- public investment recommendations;
- legal, fiduciary, or suitability conclusions.

## 3. User Outcomes

An owner, operator, researcher, engineer, or reviewer should be able to answer:

1. What is the research hypothesis, and what would falsify it?
2. Which strategy version and exact parameters are under review?
3. Which data, features, Gemini behavior, risk policy, execution model, accounting policy, benchmarks, and costs apply?
4. Was the study pre-registered before final-test and paper evidence existed?
5. Which design, validation, final-test, walk-forward, robustness, and paper stages are complete?
6. Which failed, rejected, cancelled, incomplete, and unfavorable variants were tested?
7. Are results reproducible from immutable manifests?
8. Are cash and buy-and-hold comparisons compatible?
9. What changed between backtest and paper experiment results?
10. Which incidents, data corrections, quota failures, schedule gaps, halts, and reconciliation issues affect interpretation?
11. Which security, privacy, accessibility, release, and operational gates remain unresolved?
12. Which evidence is missing, stale, incompatible, or invalidated?
13. How was each evidence dimension scored, and what is the definition?
14. Why can no aggregate score automatically approve the strategy?
15. Who reviewed the package, what conflicts exist, and which comments remain unresolved?
16. Who made the owner decision, when, and against which immutable evidence snapshot?
17. What future paper configuration may use the approved strategy?
18. Which rollback or suspension conditions apply?
19. Why was a strategy rejected, suspended, superseded, retired, or archived?
20. Is live trading still explicitly prohibited?

## 4. Canonical Routes

```text
/research
/research/hypotheses
/research/hypotheses/:hypothesisId
/research/plans/:planId
/research/reviews
/research/reviews/:reviewId
/research/reviews/:reviewId/evidence
/research/reviews/:reviewId/scores
/research/reviews/:reviewId/comments
/research/reviews/:reviewId/decision
/strategies
/strategies/:strategyVersionId
/strategies/:strategyVersionId/lifecycle
/strategies/:strategyVersionId/promotions
/strategies/:strategyVersionId/rollback
/strategies/:strategyVersionId/retirement
```

The workspace must link to data governance, market evidence, Gemini analyses, strategy and risk, backtests, experiments, portfolio, incidents, costs, governance, releases, audit, and developer traceability.

## 5. Information Architecture

The review detail page is ordered as follows:

1. research-only, paper-only, lifecycle, evidence integrity, decision, and blocker state;
2. hypothesis, falsification criteria, strategy version, and research plan;
3. immutable review snapshot and evidence completeness;
4. data and split integrity;
5. backtest, benchmark, variant, and robustness evidence;
6. reproducibility and data-correction evidence;
7. paper experiment, incidents, costs, and operations;
8. security, privacy, accessibility, and release readiness;
9. dimension scores, definitions, and limitations;
10. reviewer comments, conflicts, and requested changes;
11. owner decision, promotion scope, rollback, retirement, and audit.

Missing final-test, failed reconciliation, invalid dataset, unreproducible evidence, unresolved critical incident, or live-trading configuration must dominate positive returns or scores.

## 6. Recommended Read Models

Recommended review contract:

```ts
interface ResearchReviewReadModel {
  schemaVersion: string;
  review: ResearchReviewIdentity;
  hypothesis: ResearchHypothesisSummary;
  plan: ResearchPlanSummary;
  strategy: StrategyVersionReviewSummary;
  evidenceSnapshot: ReviewEvidenceSnapshotSummary;
  completeness: EvidenceCompletenessSummary;
  data: ResearchDataReviewSummary;
  backtests: BacktestReviewSummary;
  robustness: RobustnessReviewSummary;
  reproducibility: ReproducibilityReviewSummary;
  paperExperiment: PaperExperimentReviewSummary | null;
  operations: OperationalReviewSummary;
  governance: GovernanceReviewSummary;
  scores: EvidenceScoreSummary[];
  reviewers: ReviewerAssignmentSummary[];
  comments: ReviewCommentSummary[];
  decision: ResearchDecisionSummary | null;
  promotion: StrategyPromotionSummary | null;
  rollback: StrategyRollbackSummary | null;
  blockers: ResearchReviewBlocker[];
  diagnostics: DiagnosticSummary[];
  limitations: LimitationSummary[];
  permissions: ResearchReviewPermissions;
  links: ResearchReviewLinks;
}
```

Recommended strategy lifecycle contract:

```ts
interface StrategyLifecycleReadModel {
  schemaVersion: string;
  strategy: StrategyVersionIdentity;
  lifecycle: StrategyLifecycleSummary;
  dependencies: StrategyDependencySummary;
  reviews: ResearchReviewReference[];
  promotions: StrategyPromotionReference[];
  activeConfigurations: ConfigurationReference[];
  experiments: ExperimentReference[];
  incidents: IncidentReference[];
  rollback: StrategyRollbackSummary | null;
  retirement: StrategyRetirementSummary | null;
  blockers: ResearchReviewBlocker[];
  auditEvents: AuditEventReference[];
}
```

Recommended decision contract:

```ts
interface ResearchDecisionReadModel {
  schemaVersion: string;
  decision: ResearchDecisionIdentity;
  evidenceSnapshotHash: string;
  outcome: "approved_for_future_paper_research" | "changes_requested" | "rejected" | "suspended" | "retired";
  scope: ResearchDecisionScope;
  rationale: string;
  conditions: ResearchDecisionCondition[];
  unresolvedLimitations: LimitationSummary[];
  ownerApproval: OwnerApprovalSummary;
  effectiveAt: string;
  invalidationRules: DecisionInvalidationRule[];
  auditReference: string;
}
```

The frontend must not calculate approval, reviewer eligibility, conflict status, evidence completeness, lifecycle transitions, promotion scope, or decision validity.

## 7. Research Hypothesis Contract

Required fields:

- immutable hypothesis ID;
- workspace;
- title;
- precise hypothesis statement;
- domain and market scope;
- expected mechanism;
- rationale;
- supporting prior evidence;
- falsification criteria;
- primary and secondary outcomes;
- baseline and benchmarks;
- risks and confounders;
- planned data period and splits;
- cost and operational assumptions;
- owner and authors;
- creation time;
- status;
- supersession references;
- audit evidence.

A hypothesis must be falsifiable and must not be phrased as a guaranteed profit claim.

## 8. Hypothesis Lifecycle

Supported states:

- draft;
- under review;
- accepted for research;
- rejected;
- in progress;
- falsified;
- supported with limitations;
- inconclusive;
- superseded;
- archived.

Hypothesis outcome is distinct from strategy promotion.

## 9. Research Plan Contract

Required fields:

- immutable plan ID and version;
- hypothesis reference;
- strategy candidate references;
- data sources and versions;
- design, validation, final-test, walk-forward, and paper stages;
- split ranges and policies;
- primary and secondary metrics;
- benchmarks;
- cost, execution, and accounting assumptions;
- robustness and sensitivity plan;
- reproducibility plan;
- stopping and invalidation rules;
- incident and data-correction behavior;
- owner and reviewers;
- approval and preregistration timestamps;
- plan hash.

## 10. Pre-Registration Evidence

Required evidence:

- plan hash;
- timestamp before final-test or paper evidence;
- approved metrics and thresholds;
- parameter-selection boundaries;
- dataset split definitions;
- benchmark definitions;
- robustness plan;
- planned paper duration;
- planned decision criteria;
- authors and approvers;
- immutable audit event.

Post-hoc changes require a new plan version and explicit disclosure.

## 11. Strategy Version Identity

Required fields:

- immutable strategy version ID;
- strategy family;
- semantic or monotonic version;
- implementation revision;
- configuration hash;
- parameter schema and values;
- feature-set dependencies;
- Gemini dependency and fallback behavior;
- market and interval compatibility;
- risk-policy compatibility;
- execution and accounting assumptions;
- lifecycle state;
- owner;
- creation time;
- supersession and retirement references.

Used strategy versions are immutable.

## 12. Strategy Lifecycle

Supported states:

- idea;
- draft;
- research planned;
- backtest in progress;
- validation review;
- final test pending;
- paper experiment pending;
- paper experiment running;
- research review pending;
- approved for future paper research;
- active in approved paper configuration;
- suspended;
- changes required;
- rejected;
- superseded;
- retired;
- archived.

No state in Sprint 17 represents live-trading approval.

## 13. Strategy Dependency Contract

Dependencies include:

- feature-set version;
- market-data schema and metadata;
- Gemini provider/model/prompt/schema/validation/fallback versions where applicable;
- strategy parameters;
- risk-policy version;
- execution-model version;
- accounting-policy version;
- benchmark versions;
- configuration version;
- code and dependency revisions;
- migration revision;
- compatible environments.

A dependency change creates a new strategy behavior set or review scope.

## 14. Review Identity

Required fields:

- immutable review ID;
- workspace;
- hypothesis and plan;
- strategy version;
- review type;
- target lifecycle transition;
- evidence snapshot ID and hash;
- review status;
- assigned reviewers;
- owner decision-maker;
- creation, due, submitted, decided, and archived timestamps;
- revision and schema versions;
- audit references.

## 15. Review Types

Supported review types:

- hypothesis review;
- plan and preregistration review;
- design-stage review;
- validation-stage review;
- final-test readiness review;
- paper-experiment readiness review;
- post-experiment research review;
- promotion review;
- suspension review;
- rollback review;
- retirement review.

Each type has a versioned gate profile.

## 16. Evidence Snapshot Contract

The review snapshot freezes references to:

- hypothesis and plan versions;
- strategy behavior set;
- datasets and reproducibility manifests;
- backtest runs and reports;
- benchmarks;
- variants and robustness studies;
- paper experiment and cycles;
- incidents and halts;
- cost and SLO evidence;
- security, privacy, accessibility, and release evidence;
- reviewer assignments;
- definitions and score versions.

Any material evidence change invalidates or supersedes the decision snapshot.

## 17. Evidence Inventory

Required categories:

- research plan and preregistration;
- data classification, quality, lineage, and splits;
- methodology and no-look-ahead;
- strategy version and dependencies;
- risk, execution, accounting, and cost assumptions;
- design and validation backtests;
- untouched final test;
- cash and buy-and-hold benchmarks;
- tested variants and selection context;
- parameter sensitivity;
- walk-forward and regime evidence;
- reproducibility rerun;
- paper experiment and forward observation;
- incidents, schedule gaps, provider failures, and halts;
- ledger and reconciliation;
- security, privacy, accessibility, and operational readiness;
- limitations and unresolved gaps.

## 18. Evidence Completeness Engine

Completeness is a rule-based inventory result, not a judgment of quality or approval.

Required fields:

- profile version;
- required, optional, and not-applicable evidence items;
- present, missing, stale, invalid, incompatible, warning, and unavailable states;
- evidence references;
- blockers;
- completion percentage only as a descriptive inventory metric;
- sample and period adequacy;
- last evaluated timestamp.

A 100% inventory does not imply strategy approval.

## 19. Data and Split Review

Required checks:

- exact dataset versions and hashes;
- quality and lineage;
- finalized data;
- metadata and timezone versions;
- design, validation, final-test, and walk-forward ranges;
- overlap and leakage checks;
- untouched final-test status;
- correction and invalidation state;
- representativeness and known gaps;
- retention and reproducibility holds.

## 20. Methodology Review

Required checks:

- replay clock;
- finalized-data semantics;
- no-look-ahead;
- order activation and fill timing;
- intrabar policy;
- fees, spread, slippage, precision, and minimum notional;
- partial fills and cancellations;
- ledger and reconciliation;
- Gemini replay mode;
- failure and fallback behavior;
- deterministic seeds and ordering.

## 21. Backtest Evidence Review

Required evidence:

- complete and reconciled runs;
- design, validation, and final-test classification;
- gross and net metrics;
- drawdown, volatility, exposure, turnover, costs, and sample counts;
- trades, events, ledger, and warnings;
- cash and buy-and-hold benchmarks;
- report hashes;
- failed and partial runs;
- definition versions and limitations.

## 22. Tested Variant Disclosure

Required disclosure:

- all strategy versions and parameter combinations tested;
- symbols, periods, costs, and methodology variants;
- selected, rejected, failed, cancelled, and incomplete results;
- manual selection steps;
- optimization method where used;
- multiple-comparison or selection-bias limitations;
- final-test contamination status;
- experiment and code references.

## 23. Robustness Review

Required dimensions may include:

- neighboring parameters;
- higher fees, spread, and slippage;
- execution delay;
- alternative periods;
- market regimes;
- related symbols where justified;
- walk-forward windows;
- data gaps and corrections;
- reduced Gemini availability;
- quota and scheduler disruption;
- operational stress and cold starts;
- portfolio-capital sensitivity.

Every result must identify changed and unchanged assumptions.

## 24. Reproducibility Review

Required evidence:

- complete reproducibility manifest;
- repeated run with exact datasets and versions;
- code, dependencies, and migrations;
- seeds and ordering;
- event, trade, ledger, metric, benchmark, report, and state hashes;
- archived-data restore where applicable;
- differences and limitations;
- verified, limited, mismatch, incomplete, or unavailable outcome.

## 25. Paper Experiment Review

Required evidence:

- frozen configuration and preflight;
- actual period and cycle counts;
- schedule delays and missed cycles;
- market freshness and quality;
- Gemini validity and budget;
- strategy and risk outcomes;
- orders, fills, costs, ledger, and reconciliation;
- incidents, halts, recovery, exports, and restore;
- cash and buy-and-hold comparison;
- backtest-to-paper methodological differences;
- final report and limitations.

## 26. Operational and Cost Review

Required evidence:

- SLO and error-budget state;
- provider quotas and free-tier constraints;
- cycle duration relative to cadence;
- database and backtest capacity;
- recovery and resilience tests;
- cost allocation and budgets;
- cost per cycle, report, and experiment day;
- anomalies;
- scale triggers;
- no-auto-upgrade and live-trading-disabled state.

## 27. Governance Review

Required checks:

- Auth, membership, permissions, and RLS assurance;
- immutable configuration;
- secret posture;
- migration readiness;
- security findings and exceptions;
- privacy, retention, provider terms, and regional readiness;
- backup and restore;
- accessibility and content review;
- release and deployment evidence;
- open blockers and incidents.

## 28. Evidence Score Registry

Scores may summarize review dimensions but do not authorize promotion.

Each score definition includes:

- stable score ID and version;
- dimension;
- purpose;
- inputs;
- calculation or rubric;
- range and unit;
- missing-data behavior;
- severity thresholds;
- limitations;
- owner;
- tests;
- activation and archive state.

## 29. Recommended Score Dimensions

Possible dimensions:

- evidence completeness;
- data integrity;
- methodological validity;
- benchmark adequacy;
- robustness;
- reproducibility;
- paper-experiment completeness;
- accounting integrity;
- operational reliability;
- cost sustainability;
- security and privacy readiness;
- accessibility and documentation readiness;
- unresolved risk and limitation severity.

No single aggregate score is authoritative.

## 30. Score Presentation

Requirements:

- show definition, version, inputs, missing data, and limitations;
- show dimension values separately;
- avoid ranking strategies by a hidden weighted total;
- show critical blockers regardless of score;
- preserve qualitative reviewer comments;
- prohibit probability-of-profit interpretation;
- provide accessible non-color presentation.

## 31. Reviewer Assignment

Required fields:

- reviewer assignment ID;
- review;
- reviewer identity;
- role and expertise category;
- assigned scope;
- conflict-of-interest declaration;
- assigned and due timestamps;
- accepted, declined, completed, or revoked state;
- comments and decision recommendation;
- audit references.

## 32. Reviewer Conflict Contract

Conflicts may include:

- sole author reviewing own work;
- owner and independent reviewer role overlap;
- financial or organizational conflict where documented;
- unreviewed manual parameter selection;
- reviewer participation in disputed evidence creation;
- insufficient expertise for assigned scope.

Conflicts must be disclosed and resolved according to policy; the system does not make legal judgments.

## 33. Review Comments

Every comment includes:

- immutable comment ID;
- review and evidence scope;
- author;
- category and severity;
- text with safe sanitization;
- evidence references;
- created and edited timestamps;
- edit history;
- resolved, superseded, rejected, or open state;
- resolution rationale;
- audit references.

Critical comments cannot be silently deleted or marked resolved by the author alone when policy requires independent verification.

## 34. Change Request Contract

Required fields:

- request ID;
- review;
- affected strategy, plan, dataset, run, or document;
- reason;
- required evidence or implementation;
- owner;
- due date;
- blocker severity;
- status;
- completion evidence;
- verification reviewer;
- audit references.

A material change creates new immutable versions and may require a new review snapshot.

## 35. Decision Gate Profiles

Profiles include:

- plan acceptance;
- final-test readiness;
- paper-experiment readiness;
- post-experiment research approval;
- suspension;
- rollback;
- retirement.

Each profile defines required evidence, blockers, reviewer roles, owner decision, recent authentication, and invalidation conditions.

## 36. Owner Decision Contract

Every decision requires:

- eligible owner role;
- recent authentication;
- immutable evidence snapshot hash;
- completed required reviews;
- resolved critical comments;
- no prohibited blockers;
- outcome;
- scope;
- rationale;
- conditions;
- unresolved limitations;
- effective timestamp;
- invalidation rules;
- idempotency key;
- expected version;
- audit event.

## 37. Decision Outcomes

Supported outcomes:

- approved for future paper research;
- changes requested;
- rejected;
- suspended;
- retired.

There is no live-trading approval outcome.

## 38. Promotion Scope

Approved promotion scope may allow:

- use in a new versioned paper-research configuration;
- use in a new preflighted paper experiment;
- continued evaluation in backtests;
- approved public methodology disclosure without private evidence;
- versioned comparison and monitoring.

It must not allow automatic activation in a running experiment or any private exchange execution.

## 39. Promotion Command Boundary

Promotion requires:

- owner authorization and recent authentication;
- exact approved decision and evidence snapshot;
- idempotency and expected-version guards;
- target future configuration;
- strategy dependency compatibility;
- no active critical blocker;
- rollback and suspension conditions;
- explicit confirmation;
- immutable transition and audit.

## 40. Strategy Activation Boundary

Activation means associating an approved strategy version with a future paper configuration.

Requirements:

- approved strategy lifecycle state;
- approved configuration lifecycle;
- exact compatible dependencies;
- no running experiment mutation;
- preflight before experiment start;
- paper-only and live-trading-disabled state;
- owner approval and audit;
- no model or browser inference.

## 41. Suspension Contract

Suspension triggers may include:

- data correction or invalidation;
- reproducibility mismatch;
- ledger or reconciliation failure;
- unexpected paper behavior;
- security or privacy incident;
- critical provider drift;
- risk-policy incompatibility;
- unresolved release blocker;
- evidence manipulation or missing audit;
- owner decision.

Suspension blocks new use while preserving evidence and existing incident response.

## 42. Rollback Contract

Required fields:

- rollback ID;
- affected strategy version and configurations;
- trigger and incident;
- target prior approved strategy/configuration where available;
- compatibility checks;
- active experiment behavior;
- halt or pause requirements;
- migration and data implications;
- owner approval;
- execution and verification;
- audit references;
- limitations.

Rollback must not rewrite completed experiment or portfolio evidence.

## 43. Supersession Contract

A strategy version may be superseded by a new version after a complete review.

Required fields:

- old and new versions;
- change summary;
- compatibility;
- new hypothesis or plan where required;
- evidence comparison;
- activation scope;
- prior-version status;
- migration guidance;
- approval and audit.

## 44. Retirement Contract

Required fields:

- retirement ID;
- strategy version;
- reason;
- effective time;
- owner approval;
- active configuration and experiment checks;
- public/reference documentation impact;
- evidence and retention holds;
- rollback availability;
- final report;
- audit references.

Retired versions remain available for historical review and reproducibility.

## 45. Decision Invalidation

A decision may be invalidated by:

- changed evidence snapshot;
- dataset correction;
- reproducibility mismatch;
- critical incident;
- security, privacy, or RLS failure;
- strategy dependency change;
- risk or execution incompatibility;
- report or benchmark correction;
- expired required approval;
- discovered undeclared variant selection.

Invalidation preserves the original decision and creates a new lifecycle event.

## 46. Evidence Holds and Retention

Approved or rejected reviews may require holds on:

- datasets and manifests;
- backtest and benchmark reports;
- experiment cycles and reports;
- Gemini reports and validation evidence;
- strategy and risk decisions;
- orders, fills, ledger, and reconciliation;
- review comments and decisions;
- incidents, security findings, and releases;
- export packages.

Holds must be linked to data-governance policy.

## 47. Review Audit Timeline

Events include:

- hypothesis and plan creation;
- preregistration;
- strategy version creation;
- evidence snapshot;
- reviewer assignment and conflict declaration;
- comments and resolutions;
- change requests;
- score calculation;
- owner decision;
- promotion, activation, suspension, rollback, supersession, retirement, and archive;
- invalidation and incident linkage.

## 48. Authorized Export

Exports may include:

- hypothesis and plan;
- evidence snapshot manifest;
- completeness report;
- data/methodology/backtest/robustness/reproducibility/paper/operations/governance review;
- score definitions and results;
- reviewer assignments, conflicts, comments, and change requests according to authorization;
- owner decision;
- promotion, rollback, suspension, and retirement records;
- audit and limitations.

Every export includes schema and generation versions, review and strategy IDs, snapshot hash, timestamps, evidence hashes, decision scope, paper-only disclaimer, blockers, limitations, and authorization context.

## 49. Page-State Matrix

Explicit states include:

- loading;
- no hypotheses;
- hypothesis draft;
- plan review;
- preregistered;
- research in progress;
- evidence incomplete;
- evidence stale;
- data invalid;
- final test contaminated;
- reproducibility mismatch;
- paper experiment incomplete;
- accounting mismatch;
- critical incident;
- review pending;
- reviewer conflict;
- changes requested;
- approved for future paper research;
- rejected;
- suspended;
- rollback pending;
- rolled back;
- superseded;
- retired;
- archived;
- decision invalidated;
- schema mismatch;
- unauthorized;
- not found;
- backend unavailable;
- command conflict;
- export unavailable.

Positive performance must not hide any critical state.

## 50. Responsive Behavior

Requirements:

- paper-only, lifecycle, decision, integrity, and blockers remain first;
- evidence inventory and score tables provide narrow-layout alternatives;
- review comments preserve author, scope, severity, evidence, and state;
- strategy dependency and version hashes wrap or copy safely;
- command controls remain separated from evidence;
- no critical content is hover-only;
- charts have accessible tables;
- historical failed variants remain discoverable on mobile.

## 51. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- keyboard-accessible filters, evidence tables, score definitions, comments, dialogs, diffs, and timelines;
- visible focus;
- accessible definitions for hypothesis, preregistration, final test, robustness, reproducibility, score, review, promotion, suspension, rollback, and retirement;
- no reliance on color alone;
- status announcements for review and lifecycle changes;
- reflow at 200% and relevant 400% zoom;
- reduced motion;
- screen-reader-readable metrics, dates, versions, hashes, and outcomes;
- safe copy controls.

## 52. Security and Authority Boundaries

The workspace must not:

- let Gemini or any AI approve, promote, activate, suspend, rollback, or retire a strategy;
- infer owner approval from scores;
- expose secret, private provider, or unrestricted financial payloads;
- mutate immutable evidence snapshots or historical decisions;
- delete failed, rejected, or unfavorable variants;
- activate a strategy in a running experiment;
- bypass deterministic risk, preflight, configuration governance, RLS, or release gates;
- allow arbitrary code, parameter, SQL, or configuration execution;
- enable Binance test or live trading;
- present research as investment advice or guaranteed performance.

## 53. Privacy and Data Minimization

The workspace must minimize:

- reviewer and author personal details;
- conflicts and comments outside authorized roles;
- security and privacy findings;
- raw provider and financial payloads;
- private strategy implementation details in public exports;
- account and support data.

Public methodology may describe approved rules and limitations but not private evidence or personal reviewer details.

## 54. Observability

Safe telemetry may include:

- hypotheses and plans by state;
- review and lifecycle outcomes;
- evidence completeness states;
- missing and stale categories;
- data, reproducibility, paper, accounting, security, and operational blockers;
- review duration;
- reviewer assignment and conflict counts;
- comment and change-request state counts;
- decision, promotion, suspension, rollback, supersession, retirement, and invalidation outcomes;
- export outcomes;
- client and schema versions.

Telemetry must not contain comment text, personal conflict details, private strategy parameters, raw evidence, or financial payloads.

## 55. Testing Strategy

### Contract Tests

Validate hypothesis, plan, preregistration, strategy version, lifecycle, review, evidence snapshot, completeness, score, reviewer, conflict, comment, change request, decision, promotion, suspension, rollback, retirement, blocker, and export schemas.

### Hypothesis and Plan Tests

Validate falsifiability, required outcomes, benchmarks, splits, robustness, stopping rules, hashes, preregistration timing, post-hoc changes, and supersession.

### Evidence Tests

Validate inventory categories, exact dataset versions, split leakage, methodology, no-look-ahead, backtests, variants, robustness, reproducibility, paper experiments, operations, governance, and limitations.

### Score Tests

Validate definitions, ranges, missing-data behavior, versioning, independent dimensions, no hidden total, no profit-probability semantics, and critical-blocker precedence.

### Review Workflow Tests

Validate assignments, conflicts, comments, edit history, resolutions, change requests, required reviewers, due dates, authorization, idempotency, expected versions, and audit.

### Decision and Promotion Tests

Validate snapshot immutability, recent authentication, owner role, blockers, conditions, invalidation, future-paper scope, configuration compatibility, preflight boundary, and no running-experiment mutation.

### Suspension, Rollback, and Retirement Tests

Validate triggers, incidents, evidence preservation, active configuration checks, halt/pause behavior, prior-version compatibility, verification, and historical accessibility.

### Security and Privacy Tests

Validate no AI authority, no score approval, no secret exposure, no evidence deletion, no arbitrary execution, no live trading, role-scoped comments, and redacted exports.

### Accessibility Tests

Validate keyboard flow, headings, evidence tables, score definitions, comments, dialogs, timelines, focus, announcements, zoom, reflow, and contrast.

### Visual Regression

Capture plan, incomplete evidence, invalid data, final-test contamination, reproducibility mismatch, paper incomplete, review conflict, changes requested, approved, rejected, suspended, rollback, retired, invalidated, and error states.

## 56. Acceptance Criteria

Sprint 17 documentation is accepted when:

1. every hypothesis is falsifiable and tied to a versioned research plan;
2. preregistration freezes split, metric, benchmark, robustness, and decision criteria before final-test or paper evidence;
3. every strategy version has immutable parameters, dependencies, configuration hash, and lifecycle state;
4. review evidence snapshots are immutable and material changes invalidate old decisions;
5. completeness is a rule-based inventory and never an automatic approval signal;
6. failed, rejected, cancelled, incomplete, and unfavorable variants remain visible;
7. untouched final-test, no-look-ahead, benchmarks, costs, robustness, reproducibility, and paper evidence are explicit;
8. accounting, incidents, quota, scheduling, security, privacy, accessibility, and release evidence influence review;
9. scores expose definitions, inputs, missing data, and limitations and cannot automatically approve a strategy;
10. reviewer assignments, conflicts, comments, change requests, and resolutions are immutable and auditable;
11. owner decisions require recent authentication, exact snapshot hash, required reviews, no prohibited blockers, idempotency, expected version, and audit;
12. promotion is limited to future paper-research configurations;
13. running experiments remain frozen;
14. suspension, rollback, supersession, retirement, and decision invalidation preserve historical evidence;
15. no AI approval, hidden aggregate score, evidence deletion, arbitrary execution, Binance test, private exchange, or live-trading authority is introduced;
16. security, privacy, accessibility, hypothesis, evidence, score, review, decision, lifecycle, rollback, and export gates are explicit.

## 57. Definition of Done

The Sprint 17 specification is complete when:

- this document is committed;
- `SPRINT_17_TASKS.md` is committed;
- terminology matches strategy, risk, backtest, paper experiment, data governance, Gemini, accounting, performance, governance, developer traceability, security, and testing documents;
- all hypothesis, plan, preregistration, strategy version, lifecycle, review, snapshot, evidence, completeness, data, methodology, backtest, variant, robustness, reproducibility, paper, operations, governance, score, reviewer, conflict, comment, change request, decision, promotion, activation, suspension, rollback, supersession, retirement, invalidation, hold, export, accessibility, and authority states are explicit;
- both commits are fetched and verified.

## 58. Next Sprint Boundary

Sprint 18 defines the **Incident Response, Alerting, Operational Communication, Postmortem, Corrective Action, and Reliability Learning Workspace**, including alert routing, deduplication, acknowledgement, severity, incident command, evidence collection, customer-safe communication, timeline, containment, recovery, postmortem, corrective actions, verification, recurrence detection, and no-blame learning without enabling unsafe automated recovery or hiding financial integrity failures.
