# Sprint 18 Tasks — Incident Response, Alerting, Operational Communication, Postmortem, Corrective Action, and Reliability Learning Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a no-blame, evidence-preserving incident-response workspace that connects versioned alert rules, deduplication, routing, acknowledgement, escalation, incident command, financial and audit integrity, containment, recovery, communication, postmortem, corrective actions, recurrence, and readiness exercises without automatic resume, automatic repair, public disclosure, evidence deletion, or AI command authority.

## Authoritative References

- `docs/INCIDENT_RESPONSE_POSTMORTEM_LEARNING_WORKSPACE_IMPLEMENTATION.md`
- `docs/OBSERVABILITY.md`
- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`
- `docs/DATA_LIFECYCLE_DATASET_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/PERFORMANCE_RESILIENCE_CAPACITY_FINOPS_WORKSPACE_IMPLEMENTATION.md`
- `docs/AUTH_CONFIGURATION_SECURITY_RELEASE_WORKSPACE_IMPLEMENTATION.md`
- `docs/DEVELOPER_PORTAL_DOCUMENTATION_TRACEABILITY_WORKSPACE_IMPLEMENTATION.md`
- `docs/PRODUCT_SHELL_ONBOARDING_TRUST_I18N_WORKSPACE_IMPLEMENTATION.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `AGENTS.md`

## S18.1 Define Versioned Incident Schemas

### Objective

Create explicit contracts for alert rules, instances, grouping, routing, acknowledgement, escalation, incidents, command roles, impact, integrity, resources, evidence, timelines, decisions, containment, recovery, communications, postmortems, corrective actions, recurrence, readiness, blockers, permissions, and links.

### Work

- define `IncidentResponseReadModel` and nested schemas;
- define alert and corrective-action read models;
- define severity, lifecycle, communication, verification, recurrence, and exercise states;
- require immutable IDs, versions, timestamps, evidence, classification, and limitations;
- publish schemas in OpenAPI;
- generate frontend types.

### Acceptance Criteria

- every alert and incident state is machine-readable;
- service-restored and resolved states remain separate;
- command permissions are server-provided;
- no automatic repair/resume field exists;
- contract tests pass.

## S18.2 Implement Alert Rule Registry

### Objective

Persist versioned conditions, thresholds, duration, severity, evaluation, scope, grouping, routing, maintenance, runbook, owner, tests, and lifecycle.

### Work

- implement rule list/detail endpoints;
- map rules to metric/event catalogs;
- validate bounded labels and conditions;
- preserve activation, archive, and supersession;
- redact unsafe query details;
- link release evidence.

### Acceptance Criteria

- every active rule has tests and runbook;
- rule changes create new versions;
- secret-bearing expressions are absent;
- unknown metric/event references fail;
- registry tests pass.

## S18.3 Implement Canonical Alert Categories

### Objective

Define security, authorization, financial, audit, data, risk, experiment, schedule, provider, freshness, database, recovery, deployment, SLO, cost, and documentation categories.

### Work

- assign stable category codes;
- map severity defaults, prohibited suppression, route policies, incident requirements, and runbooks;
- preserve deprecations;
- connect notification priorities;
- add glossary content.

### Acceptance Criteria

- every alert maps to one category;
- zero-tolerance categories are explicit;
- category changes are versioned;
- unknown categories fail closed;
- tests pass.

## S18.4 Implement Alert Instance Ingestion

### Objective

Persist rule, source, values, thresholds, timing, repeats, lifecycle, grouping, acknowledgement, escalation, incident, resolution, and correlations.

### Work

- normalize metric and event alerts;
- enforce idempotent ingestion;
- verify rule version and resource scope;
- preserve first/last occurrence and repeat count;
- store bounded evidence references;
- add safe telemetry.

### Acceptance Criteria

- duplicate delivery does not create duplicate alert instances;
- observed units match rules;
- unauthorized resource data is absent;
- stale rule evidence is visible;
- ingestion tests pass.

## S18.5 Implement Alert Deduplication and Grouping

### Objective

Reduce noise without losing underlying events or hiding repeated critical failures.

### Work

- define stable deduplication and group keys;
- apply bounded windows;
- persist first/last occurrence, repeat count, members, and escalation state;
- treat zero-tolerance categories specially;
- expose underlying event references;
- test concurrency.

### Acceptance Criteria

- grouping is deterministic;
- underlying events remain auditable;
- repeated critical events escalate visibly;
- unread/active counts reconcile;
- property tests pass.

## S18.6 Implement Alert Routing and Delivery

### Objective

Route alerts to approved roles and channels with durable in-app fallback.

### Work

- define route-policy versions;
- support in-app and separately approved email/external channels;
- persist attempts, outcomes, fallback recipients, escalation times, quiet hours, and privacy class;
- enforce recipient authorization;
- preserve failed delivery.

### Acceptance Criteria

- external delivery failure does not remove durable record;
- critical alerts bypass non-critical quiet-hour suppression;
- recipient data is minimized;
- routes are versioned;
- delivery tests pass.

## S18.7 Implement Alert Acknowledgement Command

### Objective

Record who accepted responsibility for investigating without resolving the alert.

### Work

- require authorized actor, current version, note/reason, next action, incident or monitoring state, idempotency, expected version, and audit;
- preserve repeated attempts and conflicts;
- notify escalation policy;
- prevent acknowledgement from clearing halt or alert.

### Acceptance Criteria

- acknowledgement never equals resolution;
- stale versions fail safely;
- repeated commands are idempotent;
- actor and next action are explicit;
- workflow tests pass.

## S18.8 Implement Alert Escalation Engine

### Objective

Escalate unacknowledged, worsening, repeated, broad, integrity, containment, communication, action, and error-budget conditions.

### Work

- define trigger profiles and timers;
- calculate recipients and severity server-side;
- persist trigger, route, attempts, outcomes, and audit;
- support manual authorized escalation;
- prevent downgrade through stale evidence.

### Acceptance Criteria

- escalation is deterministic;
- failed delivery is retried within policy;
- critical financial/security events escalate immediately by profile;
- history is immutable;
- tests pass.

## S18.9 Implement Maintenance and Suppression Workflow

### Objective

Allow bounded approved maintenance while prohibiting suppression of integrity-critical categories.

### Work

- define window, environment, resources, owner approval, release/runbook, allowed categories, communications, and audit;
- calculate effective suppression server-side;
- preserve suppressed alert instances;
- reject security, ledger, audit, or unauthorized-live-state suppression;
- auto-expire window state.

### Acceptance Criteria

- prohibited categories cannot be suppressed;
- underlying events remain visible;
- expired windows cannot suppress new alerts;
- scope is bounded;
- security tests pass.

## S18.10 Implement Alert Workspace

### Objective

Present rule, state, source, grouping, routing, acknowledgement, escalation, incident, evidence, and limitations.

### Work

- implement alert list/detail routes;
- support category, severity, state, environment, resource, incident, rule, and date filters;
- use cursor pagination;
- keep firing and critical alerts first;
- provide accessible tables and timelines;
- enforce authorization.

### Acceptance Criteria

- acknowledged and resolved states are not conflated;
- grouped alerts expose repeat counts;
- unauthorized existence is not leaked;
- no critical content is color-only;
- E2E tests pass.

## S18.11 Implement Incident Registry

### Objective

Persist incident identity, severity, lifecycle, command, timestamps, alerts, resources, policies, and audit.

### Work

- implement incident list/detail endpoints;
- support safe creation from alerts or manual authorized declaration;
- assign immutable IDs;
- preserve all lifecycle timestamps;
- link workspaces/environments and source evidence;
- enforce RLS.

### Acceptance Criteria

- incidents remain discoverable after closure;
- source alerts are traceable;
- private incidents are authorization-limited;
- immutable identity is preserved;
- API tests pass.

## S18.12 Implement Incident Severity Engine

### Objective

Classify severity using integrity, security, privacy, research validity, side effects, scope, duration, recoverability, and unknowns.

### Work

- define severity rubric/version;
- consume verified impact evidence;
- return confidence and unknowns;
- support authorized manual increase with reason;
- require stricter evidence for downgrade;
- preserve history.

### Acceptance Criteria

- low downtime cannot downgrade ledger or audit failure;
- severity changes are auditable;
- unknown scope biases safe escalation according to policy;
- frontend cannot calculate severity;
- reference tests pass.

## S18.13 Implement Incident Lifecycle State Machine

### Objective

Govern suspected, declared, investigating, contained, recovering, service restored, integrity pending, monitoring, resolved, postmortem, actions, closed, and reopened states.

### Work

- define allowed transitions, roles, evidence, and gates;
- require idempotency, expected version, reason, and audit;
- separate service and integrity milestones;
- preserve failed transitions;
- prevent automatic close/resume.

### Acceptance Criteria

- service restoration cannot skip integrity verification;
- closed incidents can reopen with material evidence;
- invalid transitions fail closed;
- no automatic resume occurs;
- state tests pass.

## S18.14 Implement Incident Command Role Assignment

### Objective

Assign commander, operations, financial-integrity, security/privacy, communications, scribe, experts, and owner roles.

### Work

- implement assign, accept, decline, revoke, and handoff commands;
- support one person in multiple roles while showing coverage;
- require authorization, expected version, and audit;
- notify participants;
- minimize personal details.

### Acceptance Criteria

- every declared incident has commander coverage;
- required specialist gaps are visible;
- stale assignments cannot act;
- role history is immutable;
- workflow tests pass.

## S18.15 Implement Incident Command Handoff

### Objective

Transfer role with current state, blockers, evidence, next actions, communications, risks, and receiver acknowledgement.

### Work

- persist from/to, role, timing, severity, status, blockers, evidence, next actions, deadlines, risks, acknowledgement, and audit;
- prevent incomplete handoff for required roles;
- support emergency override with follow-up evidence;
- preserve failed/declined handoffs;
- notify escalation policy.

### Acceptance Criteria

- unacknowledged handoff does not remove prior responsibility;
- current context is immutable;
- communication deadline is preserved;
- emergency override is audited;
- tests pass.

## S18.16 Implement Affected Resource Registry

### Objective

Track services, deployments, workspaces, experiments, financial records, strategies, datasets, analyses, users, secrets, backups, releases, and docs.

### Work

- define typed resource references;
- persist effect, confidence, first/last impact, containment, and verification;
- enforce authorization and minimization;
- support dependency expansion through lineage;
- detect unknown scope;
- link incidents and blockers.

### Acceptance Criteria

- affected scope is versioned over time;
- unauthorized resources do not leak;
- confidence distinguishes verified from suspected;
- dependency expansion is traceable;
- tests pass.

## S18.17 Implement Impact Assessment

### Objective

Separate user, research, financial, security, privacy, data, availability, duration, scope, confidence, and unknowns.

### Work

- define impact dimensions and versions;
- require verified fact versus hypothesis classification;
- update through immutable revisions;
- link evidence and resources;
- support internal/public summaries with separate redaction;
- preserve limitations.

### Acceptance Criteria

- hypotheses cannot appear as verified impact;
- financial and research impact remain distinct;
- unknown scope is explicit;
- public summary uses approved facts only;
- tests pass.

## S18.18 Implement Financial and Audit Integrity Assessment

### Objective

Verify duplicates, ledger balance, reservations, state versions, projections, reconciliation, audit sequence, cycle locks, and report validity.

### Work

- execute approved integrity checks;
- persist findings, evidence, outcome, and limitations;
- link fills, ledger, portfolio, cycles, experiments, and reports;
- prohibit automatic repair;
- create correction plans where required;
- maintain halt until policy permits.

### Acceptance Criteria

- failed checks remain critical;
- service recovery cannot resolve integrity failure;
- repairs require explicit governed workflow;
- checks are reproducible;
- property and integration tests pass.

## S18.19 Implement Incident Evidence Registry

### Objective

Collect metrics, logs, traces, audit, workflows, deployments, database, datasets, financial references, screenshots, provider, commands, and communications safely.

### Work

- persist source, time, revision, collector, hash, classification, and limitations;
- redact secrets and personal data;
- support evidence holds;
- verify artifact integrity;
- prohibit raw unrestricted payloads in broad views;
- link traceability.

### Acceptance Criteria

- every critical claim links to evidence;
- evidence hashes verify;
- redaction is role-aware;
- tampered or missing artifacts are critical;
- registry tests pass.

## S18.20 Implement Immutable Incident Timeline

### Objective

Record facts, hypotheses, decisions, commands, observations, communications, status, corrections, and correlations.

### Work

- implement timeline event schema and ingestion;
- preserve ordering and source timestamps;
- append corrections rather than overwrite;
- support filters and pagination;
- link evidence and affected resources;
- expose accessible table/timeline alternatives.

### Acceptance Criteria

- timeline history cannot be silently edited;
- fact/hypothesis classification is visible;
- corrections preserve originals;
- ordering is deterministic;
- tests pass.

## S18.21 Implement Incident Decision Log

### Objective

Capture decision-maker, evidence, options, selected action, expected outcome, risks, stop conditions, authorization, and result.

### Work

- implement decision create and result update commands;
- require current incident version, actor role, reason, evidence, and audit;
- require recent authentication for privileged containment/recovery actions;
- preserve alternatives and failed outcomes;
- link runbooks.

### Acceptance Criteria

- every privileged action has a decision record;
- AI cannot be decision-maker;
- failed decisions remain visible;
- stop conditions are explicit;
- tests pass.

## S18.22 Implement Guarded Containment Actions

### Objective

Allow halt, pause, HOLD, restrict, revoke, disable, quarantine, isolate, hold, and read-only actions through approved commands.

### Work

- define allowlisted command types;
- require authorization, recent auth, idempotency, expected version, target, reason, confirmation, and audit;
- prevent arbitrary shell/SQL/workflow inputs;
- preserve evidence and status;
- never auto-resume.

### Acceptance Criteria

- containment cannot destroy evidence;
- commands are bounded and idempotent;
- prohibited arbitrary execution fails closed;
- resume requires separate review;
- security tests pass.

## S18.23 Implement Recovery Attempt Registry

### Objective

Track runbook, target, actor, steps, outcomes, failures, stop conditions, integrity, rollback/forward-fix, and artifacts.

### Work

- implement attempt create/update through guarded runbook helpers;
- persist start/finish, expected/observed, evidence, and audit;
- preserve failed and partial attempts;
- link decision log and incident state;
- enforce isolated/approved environment rules.

### Acceptance Criteria

- failed attempts remain visible;
- arbitrary commands are impossible;
- attempts identify exact runbook version;
- integrity checks accompany recovery;
- tests pass.

## S18.24 Implement Recovery Verification Gate

### Objective

Verify health, deployment, migration, Auth, RLS, market, quotas, datasets, locks, ledger, reconciliation, audit, experiments, backups, SLOs, and live-disabled state.

### Work

- define verification profile by incident category;
- execute or ingest check evidence;
- calculate complete, partial, failed, and unavailable states;
- block resolution on required failures;
- link runbooks and releases;
- preserve limitations.

### Acceptance Criteria

- financial incidents require reconciliation;
- security incidents require authorization and secret checks;
- no live-trading state is accepted;
- missing required checks fail closed;
- gate tests pass.

## S18.25 Implement Resolution Gate

### Objective

Require containment, bounded scope, integrity, security/privacy review, validity, communications, monitoring, owner approval, and postmortem/action policy.

### Work

- define severity-specific gate profiles;
- evaluate server-side;
- distinguish service restored from resolved;
- require idempotency, expected version, and audit for resolution;
- preserve unresolved limitations and continued halt;
- prevent automatic close.

### Acceptance Criteria

- unresolved integrity cannot be marked resolved;
- gate result is deterministic;
- owner approval is required by severity policy;
- limitations remain visible;
- tests pass.

## S18.26 Implement Internal Communication Workflow

### Objective

Create versioned role-scoped updates with facts, impact, unknowns, actions, next update, evidence, and sensitivity.

### Work

- implement draft, review, approve, publish, correct, supersede, and restrict states;
- require author/reviewer roles;
- sanitize content;
- enforce update deadlines;
- preserve edit/version history;
- notify audiences.

### Acceptance Criteria

- communications distinguish facts and unknowns;
- published versions are immutable;
- missed updates trigger escalation;
- sensitive content is role-limited;
- tests pass.

## S18.27 Implement Public-Safe Communication Boundary

### Objective

Publish only reviewed facts, safe impact, paper context, status, and next update.

### Work

- define public redaction profile;
- require owner/communications and security/privacy review where applicable;
- scan secrets, exploit details, personal data, private financial evidence, and unsupported causes;
- preserve immutable versions and corrections;
- prohibit automatic publication.

### Acceptance Criteria

- public content exposes no restricted evidence;
- root cause is withheld until verified;
- paper/simulation scope is explicit;
- legal notification is not auto-determined;
- security/content tests pass.

## S18.28 Implement Postmortem Registry and Template

### Objective

Capture impact, detection, timeline, factors, cause confidence, controls, recovery, communication, actions, recurrence, lessons, reviews, and visibility.

### Work

- implement postmortem draft/detail;
- enforce required sections by severity;
- link immutable incident evidence;
- support reviewer comments and approval;
- preserve versions and corrections;
- define public-safe derivative separately.

### Acceptance Criteria

- postmortem cannot omit financial/integrity impact when applicable;
- unsupported root cause is labeled uncertain;
- evidence links are complete;
- closed incidents retain postmortem history;
- tests pass.

## S18.29 Implement No-Blame Content and Accountability Checks

### Objective

Focus analysis on systems while preserving exact command and approval evidence.

### Work

- define content guidance and prohibited personal ranking/blame patterns;
- require decision-context sections;
- distinguish process/system failure from intentional unauthorized action;
- minimize personnel details;
- perform human review for ambiguous findings;
- preserve accountability audit.

### Acceptance Criteria

- individual league tables are prohibited;
- actor evidence remains available to authorized audit roles;
- wording is system-focused;
- intentional policy violations are not obscured;
- content tests pass.

## S18.30 Implement Root-Cause and Contributing-Factor Registry

### Objective

Classify architecture, implementation, data, configuration, provider, deployment, monitoring, runbook, review, test, capacity, UX, and access factors.

### Work

- define factor IDs and versions;
- require evidence, confidence, scope, and relation to incident;
- support multiple factors;
- preserve rejected hypotheses;
- link corrective actions;
- avoid automatic causal conclusions.

### Acceptance Criteria

- root cause has confidence and evidence;
- rejected hypotheses remain traceable;
- multiple contributing factors are supported;
- similarity alone is not causation;
- tests pass.

## S18.31 Implement Corrective Action Registry

### Objective

Track risk-reduction hypothesis, scope, owner, priority, due date, dependencies, implementation, verification, release, state, and audit.

### Work

- implement action list/detail and lifecycle;
- map categories and incidents;
- require task/source/test references;
- preserve cancelled and ineffective actions;
- notify overdue owners;
- link release gates.

### Acceptance Criteria

- every action has owner and verification plan;
- implementation does not equal verified;
- overdue state is automatic by policy;
- ineffective actions remain visible;
- API tests pass.

## S18.32 Implement Corrective Action Workflow

### Objective

Govern proposed, accepted, in-progress, blocked, implemented, verification, verified, ineffective, superseded, cancelled, and overdue states.

### Work

- define state transitions and actors;
- require expected version, idempotency, evidence, reason, and audit;
- prevent self-verification where independent review is required;
- preserve failed verification;
- link change management and releases.

### Acceptance Criteria

- invalid transitions fail closed;
- verification evidence is mandatory;
- cancellation requires rationale and risk acceptance;
- history is immutable;
- workflow tests pass.

## S18.33 Implement Corrective Action Verification

### Objective

Verify effectiveness through tests, monitors, runbooks, exercises, deployments, documentation, and observation windows.

### Work

- define verification plan and required evidence;
- execute or ingest unit/property/integration/E2E/security/accessibility/load/resilience/restore/smoke results;
- reproduce incident condition where safe;
- verify no new invariant failure;
- require reviewer sign-off;
- classify verified or ineffective.

### Acceptance Criteria

- code merged alone cannot close an action;
- regression tests map to incident cause/control gap;
- failed verification reopens action;
- effectiveness limitations are visible;
- tests pass.

## S18.34 Implement Recurrence Detection

### Objective

Identify repeated patterns across alerts, incidents, resources, symptoms, factors, controls, and overdue actions.

### Work

- define pattern features and versioned methods;
- return linked incidents, confidence, evidence, existing actions, and limitations;
- support manual review;
- escalate repeated ineffective/overdue actions;
- avoid automatic causal labeling;
- preserve historical patterns.

### Acceptance Criteria

- similarity is labeled investigative evidence;
- insufficient evidence yields no confident pattern;
- linked incidents remain authorization-scoped;
- escalation is auditable;
- tests pass.

## S18.35 Implement Reliability Learning Registry

### Objective

Track new invariants, alerts, SLOs, runbooks, ADRs, quality rules, controls, UX, release gates, capacity triggers, docs, and exercises.

### Work

- define learning item types and lifecycle;
- link incidents, evidence, owner, tasks, implementation, verification, and review;
- prevent duplicates through traceability;
- preserve unimplemented lessons as gaps;
- expose status.

### Acceptance Criteria

- every material lesson maps to implementation or explicit rejection;
- verified changes link to tests/releases;
- learning history is immutable;
- unresolved gaps remain visible;
- tests pass.

## S18.36 Implement Response Readiness Workspace

### Objective

Expose role coverage, runbook freshness, delivery tests, escalation, exercises, restore/reconciliation drills, templates, actions, and gaps.

### Work

- aggregate readiness evidence;
- define environment/severity profiles;
- calculate complete, warning, blocked, and unavailable states;
- link overdue actions and stale runbooks;
- schedule reviews;
- preserve no guarantee language.

### Acceptance Criteria

- missing critical runbooks/exercises block applicable release;
- readiness is evidence-backed;
- stale evidence is explicit;
- small-team role overlap is visible;
- tests pass.

## S18.37 Implement Tabletop and Game-Day Registry

### Objective

Record isolated synthetic scenarios, roles, injections, decisions, response, runbooks, communication, gaps, actions, and outcomes.

### Work

- implement exercise plan/run models;
- require isolated environment and synthetic data;
- prohibit private provider/exchange credentials;
- capture timeline and evidence;
- link learning and corrective actions;
- preserve failed exercises.

### Acceptance Criteria

- exercises cannot affect production research;
- failed objectives remain visible;
- participant data is minimized;
- evidence maps to runbooks and actions;
- tests pass.

## S18.38 Implement Incident Metrics and SLO Linkage

### Objective

Measure response process and connect incidents to error budgets without creating personal scoreboards.

### Work

- calculate alert actionability, acknowledgement, declaration, containment, service restoration, integrity verification, communication, postmortem, action, recurrence, and coverage metrics;
- link SLOs and zero-tolerance invariants;
- aggregate by safe categories;
- prohibit person-level rankings;
- expose definitions and limitations.

### Acceptance Criteria

- service and integrity durations remain separate;
- metrics identify sample counts and definitions;
- no individual leaderboard exists;
- error-budget linkage is traceable;
- tests pass.

## S18.39 Implement Incident Closure and Reopening Commands

### Objective

Close only after resolution, postmortem/action policy, holds, communications, approval, and audit; reopen on material evidence.

### Work

- require gate profile, owner role, recent authentication, expected version, idempotency, reason, and audit;
- verify corrective action ownership/dates;
- establish evidence holds;
- support reopen triggers for integrity, scope, recurrence, or communication changes;
- preserve all decisions.

### Acceptance Criteria

- unresolved critical evidence blocks closure;
- reopening preserves original closure;
- repeated commands are idempotent;
- no automatic close/resume occurs;
- tests pass.

## S18.40 Implement Authorized Incident Export

### Objective

Generate alert, incident, timeline, decision, recovery, communication, postmortem, action, recurrence, exercise, and public-safe packages.

### Work

- generate server-side;
- include schema/generation versions, environment, revision, IDs, times, hashes, classification, blockers, unresolved limitations, paper-only state, and authorization context;
- apply role/public redaction profiles;
- preserve failed recovery and overdue actions;
- include integrity manifest.

### Acceptance Criteria

- critical failures cannot be omitted;
- public-safe package exposes no restricted details;
- exports identify exact evidence versions;
- secrets and private payloads are absent;
- export tests pass.

## S18.41 Add Explicit State Handling

### Objective

Define safe rendering for every alert, incident, recovery, communication, action, recurrence, and readiness state.

### Work

- implement loading, empty, pending, firing, grouped, acknowledged, escalated, suppressed, resolved alert, suspected, declared, investigating, contained, recovering, service restored, integrity pending, monitoring, resolved, postmortem pending, actions open, closed, reopened, integrity failure, security/privacy, dataset invalid, recovery failed, communication review, action overdue, verification failed, recurrence, readiness gap, schema mismatch, unauthorized, unavailable, conflict, and export failure;
- define bounded retry;
- distinguish empty from evidence failure;
- label cached revision.

### Acceptance Criteria

- service restored never appears fully resolved while integrity is pending;
- stale incident state is explicit;
- unauthorized pages leak no incident existence;
- deterministic failures are not infinitely retried;
- state tests pass.

## S18.42 Add Responsive and Accessibility Verification

### Objective

Ensure alerts, timelines, decisions, communications, postmortems, actions, and exercises remain usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, 200% zoom, and relevant 400% zoom;
- test headings, landmarks, tables, timelines, dialogs, communications, comments, filters, focus, announcements, definitions, and copy controls;
- verify reduced motion and contrast;
- test long IDs, timestamps, statuses, and evidence links;
- record screen-reader spot checks.

### Acceptance Criteria

- no severity/state relies only on color;
- timelines have accessible table semantics;
- privileged confirmations are keyboard accessible;
- public/restricted content is distinguishable;
- no critical automated violation remains;
- manual evidence is recorded.

## S18.43 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make prohibited suppression, integrity verification, no-auto-resume, no-auto-repair, communication redaction, action verification, and incident evidence release-blocking.

### Work

- add contract, rule, alert, deduplication, routing, acknowledgement, escalation, maintenance, incident, severity, lifecycle, command, handoff, resource, impact, integrity, evidence, timeline, decision, containment, recovery, verification, resolution, communication, postmortem, factors, actions, recurrence, learning, readiness, exercise, metrics, closure, route, E2E, accessibility, visual, authorization, RLS, and export tests;
- add secret, exploit, personal, financial-payload, prohibited-suppression, auto-resume, auto-repair, arbitrary-command, evidence-deletion, AI-authority, private exchange, and live-trading checks;
- instrument safe alert/incident process metrics;
- test prohibited telemetry fields;
- link critical failures to release gates.

### Acceptance Criteria

- integrity-critical alerts cannot be suppressed;
- no AI, browser, or automated process can command, resolve, close, publicly disclose, resume, or repair an incident;
- failed attempts, timelines, postmortems, and actions remain immutable;
- no browser or AI path gains arbitrary shell/SQL/workflow/provider/deployment, private exchange, testnet, or live-trading authority;
- telemetry contains no prohibited fields;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Alerting | Rules, metrics/events, thresholds, duration, severity, ingestion, idempotency, grouping, routing, delivery, acknowledgement, escalation, maintenance, suppression, and resolution tests |
| Incident command | Registry, severity, lifecycle, role assignment, handoff, resources, impact, evidence, timeline, decisions, authorization, and audit tests |
| Integrity and recovery | Ledger, reconciliation, audit, datasets, cycles, halts, containment, runbooks, attempts, service restoration, verification, resolution, and no-auto-repair/resume tests |
| Communication | Internal/public scope, fact/unknown separation, redaction, review, deadlines, versioning, corrections, localization, and no-auto-publication tests |
| Learning | Postmortem, no-blame/accountability, factors, corrective actions, verification, recurrence, readiness, exercises, metrics, closure, and reopening tests |
| Accessibility and security | Keyboard, timelines, dialogs, zoom, RLS, secret/exploit/privacy redaction, prohibited suppression, no arbitrary commands, no AI authority, no live trading, and telemetry tests |

## Sprint Exit Gate

Sprint 18 is complete only when:

- S18.1 through S18.43 are implemented and verified;
- alert rules, instances, grouping, routing, acknowledgement, escalation, maintenance, suppression, and resolution are versioned and auditable;
- security, ledger, audit, and unauthorized-live-state alerts cannot be suppressed;
- incident severity includes financial/audit integrity, security/privacy, research validity, scope, duration, recoverability, and unknowns;
- acknowledgement, containment, service restoration, integrity verification, resolution, and closure remain distinct states;
- incident command roles, handoffs, decisions, evidence, and timelines are immutable;
- containment and recovery use only allowlisted, authorized, idempotent, audited commands and never auto-resume;
- failed recovery attempts remain visible;
- resolution requires category-specific integrity, security, privacy, data, experiment, communication, monitoring, and owner evidence;
- internal and public communications preserve facts, redaction, review, versions, and paper/simulation context;
- postmortems are no-blame while preserving exact accountability;
- corrective actions require risk-reduction hypothesis, owner, due date, implementation, verification, effectiveness, and release evidence;
- recurrence is an evidence-backed investigative signal and readiness uses isolated synthetic exercises;
- no AI, browser, or automation path gains incident command, public disclosure, auto-resume, auto-repair, prohibited suppression, evidence deletion, arbitrary shell/SQL/workflow/provider/deployment, private exchange, testnet, or live-trading authority;
- accessibility, responsive, security, privacy, contract, alert, incident, integrity, recovery, communication, postmortem, action, recurrence, readiness, E2E, export, audit, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 19 defines and implements the Model, Prompt, Strategy, Risk, Execution, and Configuration Change Management Workspace.
