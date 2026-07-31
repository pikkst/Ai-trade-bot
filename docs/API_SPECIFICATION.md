# API Specification

Last reviewed: 2026-08-01  
Status: Authoritative design contract mapped to `M014–M036`; generated OpenAPI becomes executable source of truth after implementation

## 1. General Conventions

- Base path: `/api/v1`
- Content type: `application/json`
- Authentication: Supabase Auth bearer evidence for protected resources
- Authorization: handler-level application permissions plus RLS where applicable
- Timestamps: RFC 3339 timezone-aware UTC
- Money, prices, quantities, rates, costs, and percentages: decimal strings with explicit units
- Request correlation: accept or generate `X-Correlation-ID`
- Repeatable side-effect commands: require `Idempotency-Key`
- Mutable aggregate commands: require an expected version through `If-Match` or an explicit version field
- Sensitive owner commands: require recent authentication according to policy
- Lists: cursor-paginated with bounded server-approved filters and deterministic ordering
- Errors: stable safe code, message, correlation ID, and bounded details
- Breaking public changes: explicit API/schema version and migration plan
- Generated OpenAPI: deterministic and verified in CI

The browser must not calculate authoritative permission, risk, accounting, reconciliation, experiment validity, SLO, cost, compatibility, approval, or release outcomes.

## 2. Master-Task Ownership

| API area | Master Tasks |
|---|---|
| identity, workspace, configuration, market, AI, strategy, risk, execution, portfolio, backtest | M003, M007–M014 |
| product workspaces and shell aggregates | M015–M025 |
| integrated verification and recovery | M026–M027 |
| cloud/experiment operation | M028–M029 |
| performance, data, research, incident, and change governance | M030–M034 |
| staging, release, and production research | M035–M036 |

An endpoint is not complete because it appears here. It requires implementation, authorization, schema, tests, observability, and generated OpenAPI evidence in its mapped Master Task.

## 3. Roles and Identity Classes

Human roles:

- `owner`
- `operator`
- `viewer`

System identities may include:

- application runtime
- scheduled workflow/service
- approved read-only operations identity
- migration identity

Every protected operation resolves server-authoritative effective permissions. A role label alone is not sufficient authorization evidence.

## 4. Standard Error Envelope

```json
{
  "error": {
    "code": "risk_rejected",
    "message": "The requested action was rejected by the active risk policy.",
    "correlation_id": "7e470bf2-f3fc-4e62-95ce-7f6f79a82581",
    "details": {
      "reason_codes": ["position_limit_exceeded"]
    }
  }
}
```

Never return stack traces, raw SQL, credentials, tokens, cookies, unrestricted prompts/provider responses, secret-bearing configuration, private cross-workspace identifiers, or filesystem paths.

## 5. Common Command Contract

Every material command requires as applicable:

- authenticated actor and eligible permission;
- workspace/resource ownership and scope;
- valid current state;
- `Idempotency-Key`;
- expected aggregate version;
- canonical reason code;
- explicit confirmation context for destructive, privilege-increasing, lifecycle, or release actions;
- recent-authentication evidence;
- immutable audit result;
- safe response containing resulting state/version and evidence links.

Duplicate requests return the canonical prior result or a deterministic `409` conflict. The browser never writes critical tables directly.

## 6. Pagination and Filtering

Response shape:

```json
{
  "items": [],
  "page": {
    "next_cursor": null,
    "has_more": false
  }
}
```

Requirements:

- bounded default and maximum page sizes;
- server-approved sort/filter fields;
- deterministic tie-breaking;
- no raw SQL/search expression passthrough;
- no unauthorized existence leak through counts, timing, or suggestions;
- exact identifier lookup remains deterministic.

## 7. Health and Runtime Identity

### `GET /health/live`

Unauthenticated process-liveness check only.

It does not imply database readiness, schedule health, provider health, financial integrity, or completed cycles.

### `GET /health/ready`

Dependency-aware readiness for the current process. Checks typed configuration, PostgreSQL, expected migration head, required Auth verification configuration, and unrecoverable startup state.

### `GET /runtime/revision`

Role: viewer or higher; a minimized public variant may exist.

Returns application version, commit SHA, build ID, migration head, API hash, client/backend artifact versions, environment, publication time, and paper/live-disabled status.

## 8. Authentication and Account

### `GET /auth/me`

Returns authenticated identity, provider, session issue/expiry, recent-auth state, account state, workspace memberships, effective role summaries, allowed session commands, and safe security-event summary.

No token, cookie, signature, password, recovery secret, or provider credential is returned.

### `POST /auth/sign-out`

Idempotent session/provider revocation command where supported.

### `POST /auth/revoke-sessions`

Role: authenticated account owner; recent authentication required.

Revokes eligible sessions and records audit evidence.

Authentication itself uses the approved Supabase Auth flow rather than an unrelated application password/JWT subsystem.

## 9. Product Shell, Preferences, and Search

### `GET /shell`

Returns product identity, account/workspace/environment context, global safety state, navigation, recent items, saved views, notification summary, preferences, help/trust context, permissions, diagnostics, and links.

### `GET /search`

Searches only authorized indexed metadata and approved content. Supports bounded query, resource type, workspace, status, date, and cursor filters.

### `GET /notifications`

Returns authorized in-app notifications/notices with severity, category, source, status, timestamps, evidence links, and required awareness/review classification.

### `POST /notifications/{notification_id}/read`

Personal idempotent state command. It does not alter source incidents, audit events, or financial evidence.

### `GET|PATCH /preferences`

Reads or updates non-authoritative user preferences such as locale, timezone, display density, and safe presentation options.

### Saved-view commands

```http
POST   /saved-views
PATCH  /saved-views/{saved_view_id}
DELETE /saved-views/{saved_view_id}
```

Saved views contain only approved route/filter/display state and never secrets, raw prompts, unrestricted queries, or authoritative calculations.

## 10. Workspaces and Memberships

### `POST /workspaces`

Role: owner. Idempotency and reason required.

Creates an isolated research workspace with base currency, initial safe metadata, and all live/private execution flags disabled.

### `GET /workspaces`

Lists only authorized workspaces.

### `GET /workspaces/{workspace_id}`

Returns workspace identity, status, owners, active configuration, experiment/portfolio summaries, membership counts, retention profile, and blockers.

### `PATCH /workspaces/{workspace_id}`

Owner-only mutable metadata command. Versioned behavioral changes use configuration resources rather than silent in-place mutation.

### Membership and invitation commands

```http
GET    /workspaces/{workspace_id}/members
POST   /workspaces/{workspace_id}/invitations
POST   /workspaces/{workspace_id}/members/{membership_id}/role-changes
POST   /workspaces/{workspace_id}/members/{membership_id}/revoke
GET    /workspaces/{workspace_id}/access-reviews
POST   /workspaces/{workspace_id}/access-reviews
```

Privilege increase or owner removal requires recent authentication, confirmation, expected version, reason, and owner-count invariant checks. Invitation tokens are never returned after issuance.

## 11. Configuration and Behavior Sets

### `POST /workspaces/{workspace_id}/configurations`

Creates a draft immutable configuration version from validated project-owned fields. It never accepts secret values.

### `GET /workspaces/{workspace_id}/configurations`

### `GET /workspaces/{workspace_id}/configurations/{configuration_id}`

Returns canonical JSON, hash, lifecycle, domain references, dependencies, approvals, usage, and limitations.

### Configuration lifecycle commands

```http
POST /workspaces/{workspace_id}/configurations/{configuration_id}/validate
POST /workspaces/{workspace_id}/configurations/{configuration_id}/approve
POST /workspaces/{workspace_id}/configurations/{configuration_id}/activate
POST /workspaces/{workspace_id}/configurations/{configuration_id}/archive
```

Used configurations are immutable. Activation applies only to future eligible resources and never mutates a running experiment.

### `GET /behavior-sets/{behavior_set_id}`

Returns immutable provider/model/prompt/schema/feature/strategy/risk/execution/accounting/schedule/budget/retention/code/dependency/migration references and aggregate hash.

## 12. Market Data and Data Quality

### `GET /market/symbols`

Filters: exchange, base asset, quote asset, active status, metadata version.

### `GET /market/candles`

Required: exchange, symbol, interval, start, end. Returns validated persisted finalized candles unless an authorized diagnostic mode is explicitly used.

### `POST /market/backfills`

Operator/owner, idempotent asynchronous bounded REST backfill.

### `GET /market/backfills/{job_id}`

Returns checkpoint, inserted, duplicate, invalid, gap, retry, provider, duration, and terminal status evidence.

### `POST /market/snapshots`

Creates an immutable quality-approved snapshot from exact finalized candle identities.

### `GET /market/snapshots/{snapshot_id}`

Returns ordered candle references, data-quality/freshness state, hash, lineage, and limitations.

### Data-quality resources

```http
GET  /data-quality/events
GET  /data-quality/events/{event_id}
POST /data-quality/events/{event_id}/review
```

Corrections create replacement/invalidation lineage rather than silent mutation.

## 13. Dataset Governance

### `GET /datasets`

Filters: class, market, interval, quality, lifecycle, retention, hold, source, environment.

### `GET /datasets/{dataset_id}`

Returns immutable manifest, schema, source range, hashes, lineage, quality gates, correction state, retention/hold, archive, restore, and dependent resources.

### Dataset lifecycle commands

```http
POST /datasets/{dataset_id}/validate
POST /datasets/{dataset_id}/quarantine
POST /datasets/{dataset_id}/approve
POST /datasets/{dataset_id}/archive
POST /datasets/{dataset_id}/restore
POST /datasets/{dataset_id}/holds
POST /datasets/{dataset_id}/deletion-reviews
```

Destructive or anonymizing action requires dependency analysis, hold checks, approval, expected version, reason, and audit. It must not break financial, incident, audit, legal-hold, or reproducibility evidence.

### `GET /lineage/{resource_type}/{resource_id}`

Returns authorization-filtered typed relationships across source and derived resources.

## 14. Feature Calculations

### `POST /feature-calculations`

References an immutable snapshot and feature-set version. Idempotent.

### `GET /feature-calculations/{calculation_id}`

Returns typed values, units, input/output hashes, warm-up, status, warnings, version, and source lineage.

## 15. Gemini Analysis

### `POST /analyses`

Operator/owner, idempotent. Input references immutable snapshot, feature calculation, prompt, schema, provider configuration, validation, and budget policy versions. The API never accepts an API key or arbitrary system prompt.

### `GET /analyses`

### `GET /analyses/{analysis_id}`

Returns provider/configuration identity, attempts, source evidence, parsing/validation, accepted report if any, grounding, safety, fallback, downstream lineage, usage, cost estimate, budget, diagnostics, and limitations.

### Analysis evidence subresources

```http
GET /analyses/{analysis_id}/request
GET /analyses/{analysis_id}/report
GET /analyses/{analysis_id}/validation
GET /analyses/{analysis_id}/evidence
GET /analyses/{analysis_id}/usage
GET /analyses/{analysis_id}/compare
```

Raw prompts and unrestricted provider responses are not returned by default.

### `POST /analyses/{analysis_id}/revalidate`

Creates a new immutable validation record against an approved compatible policy without silently modifying the original report or making an unnecessary provider request.

### AI governance reads

```http
GET /ai/prompts/{prompt_version_id}
GET /ai/schemas/{schema_version_id}
GET /ai/evaluations
GET /ai/evaluations/{evaluation_id}
GET /ai/budgets
```

All are read-only in normal product flows unless governed configuration/change commands explicitly apply.

## 16. Strategy and Risk

### `POST /strategy-evaluations`

Idempotently evaluates immutable market/features, optional accepted AI report, strategy version, and portfolio-state version.

### `GET /strategy-evaluations/{evaluation_id}`

Returns HOLD/ENTER/EXIT/REDUCE intent, requested boundary, evidence, contradictions/blockers, versions, hashes, and reason codes.

### `GET|POST /risk/policies`

Create/list immutable risk-policy versions. Owner approval is required for activation; running experiments retain their frozen version.

### `POST /risk-evaluations`

Idempotently evaluates a strategy intent against exact market, portfolio-state, and policy versions.

### `GET /risk-evaluations/{evaluation_id}`

Returns approve, reduce, reject, halt-portfolio, or halt-workspace with rule results, approved boundary, reason codes, and lineage.

### Halt resources

```http
GET  /halts
GET  /halts/{halt_id}
POST /paper-portfolios/{portfolio_id}/halt
POST /experiments/{experiment_id}/halt
```

There is no generic clear-halt endpoint. Review/resume requires domain-specific eligibility and unresolved blocker checks.

## 17. Paper Portfolios, Orders, Fills, and Ledger

### `POST /paper-portfolios`

Owner-only, idempotent. Creates a virtual portfolio with base currency, starting virtual cash, execution/accounting/risk references, and paper/live-disabled state.

### `GET /paper-portfolios/{portfolio_id}`

Returns reconciled balances, positions, realized/unrealized P&L, fees, exposure, drawdown, state version/hash, valuation, halt, and reconciliation.

### Portfolio reads

```http
GET /paper-portfolios/{portfolio_id}/history
GET /paper-portfolios/{portfolio_id}/orders
GET /paper-portfolios/{portfolio_id}/fills
GET /paper-portfolios/{portfolio_id}/ledger
GET /paper-portfolios/{portfolio_id}/reconciliations
```

### `POST /paper-orders`

Internal/approved operator command only. Must reference an approved risk evaluation and exact portfolio-state version. Arbitrary client notional is prohibited.

### `GET /paper-orders/{order_id}`

Returns requested, approved, rounded, reserved, filled, remaining, lifecycle, model, cost, ledger, reconciliation, and decision lineage.

### `POST /paper-orders/{order_id}/cancel`

Idempotent only for eligible states. Completed fills are not reversed by cancellation.

### `GET /paper-fills/{fill_id}`

Returns deterministic fill sequence, prices, notional, spread, slippage, fee, eligible market event, model, ledger, state, and reconciliation references.

### `GET /ledger/transactions/{transaction_id}`

Returns ordered append-only entries, balance check, business/correction lineage, projection impact, and reconciliation references.

### `POST /paper-portfolios/{portfolio_id}/reconcile`

Explicit idempotent reconciliation command. Mismatch creates critical evidence and halt.

No API updates or deletes ledger entries, fills, completed orders, or used portfolio-state evidence.

## 18. Research Cycles and Jobs

### `GET /research-cycles`

Filters: experiment, intended/actual time, status, delay, lock, duplicate, data, AI, risk, order/fill, reconciliation, incident, workflow, error, validity.

### `GET /research-cycles/{cycle_id}`

Returns identity, schedule, lock/lease, idempotency, stages, market, AI/fallback, strategy, risk, execution, accounting, reconciliation, workflow, audit, incidents, completeness, validity, and limitations.

### `GET /jobs/{job_id}`

Returns asynchronous job type, status, attempts, timing, progress based on persisted work units, safe error, and result resource. A job process success does not replace domain completeness checks.

Ordinary clients cannot arbitrarily dispatch production workflows.

## 19. Backtests and Comparisons

### `POST /backtests`

Operator/owner, idempotent, bounded. References immutable dataset, strategy, risk, execution, accounting, benchmark, Gemini mode, seed, code, dependency, and configuration versions.

### Backtest reads

```http
GET /backtests
GET /backtests/{backtest_id}
GET /backtests/{backtest_id}/report
GET /backtests/{backtest_id}/trades
GET /backtests/{backtest_id}/events
GET /backtests/{backtest_id}/ledger
GET /backtests/{backtest_id}/reproducibility
GET /backtests/{backtest_id}/compare
```

Incomplete, failed, timed-out, cancelled, unreconciled, or non-reproducible results remain explicit.

### `POST /backtests/{backtest_id}/cancel`

Idempotent cancellation for eligible running/queued state.

Backtests cannot automatically promote a strategy or enable execution.

## 20. Experiments and Preflight

### `POST /experiments`

Owner-only draft creation referencing a frozen workspace configuration, behavior set, paper portfolio, virtual funding, schedule, and planned period.

### Experiment reads

```http
GET /experiments
GET /experiments/{experiment_id}
GET /experiments/{experiment_id}/configuration
GET /experiments/{experiment_id}/preflight
GET /experiments/{experiment_id}/cycles
GET /experiments/{experiment_id}/incidents
GET /experiments/{experiment_id}/audit
GET /experiments/{experiment_id}/exports
GET /experiments/{experiment_id}/report
```

### Experiment commands

```http
POST /experiments/{experiment_id}/preflight
POST /experiments/{experiment_id}/start
POST /experiments/{experiment_id}/pause
POST /experiments/{experiment_id}/resume
POST /experiments/{experiment_id}/halt
POST /experiments/{experiment_id}/complete
```

`resume` is available only when implemented and eligible. It never clears unresolved risk, reconciliation, integrity, security, RLS, data, or incident blockers.

Start requires Ready state, unexpired exact-hash preflight, owner approval, reconciled initial portfolio, current export/restore evidence, valid schedule/period, no active critical incident/halt, and all private/live execution flags disabled.

## 21. Incidents and Corrective Actions

### Incident reads

```http
GET /incidents
GET /incidents/{incident_id}
GET /incidents/{incident_id}/timeline
GET /incidents/{incident_id}/communications
GET /incidents/{incident_id}/evidence
GET /incidents/{incident_id}/postmortem
GET /incidents/{incident_id}/corrective-actions
```

### Incident commands

```http
POST /incidents
POST /incidents/{incident_id}/acknowledge
POST /incidents/{incident_id}/assign
POST /incidents/{incident_id}/contain
POST /incidents/{incident_id}/restore-service
POST /incidents/{incident_id}/verify-integrity
POST /incidents/{incident_id}/resolve
POST /incidents/{incident_id}/postmortems
POST /incidents/{incident_id}/corrective-actions
POST /corrective-actions/{action_id}/verify
```

Acknowledgement, containment, restoration, integrity verification, and resolution are distinct immutable transitions. Restoration alone does not clear financial/security halts.

## 22. Research Reviews and Strategy Lifecycle

### Research resources

```http
GET  /research/reviews
POST /research/reviews
GET  /research/reviews/{review_id}
GET  /research/reviews/{review_id}/evidence
GET  /research/reviews/{review_id}/variants
GET  /research/reviews/{review_id}/robustness
GET  /research/reviews/{review_id}/paper-observation
GET  /research/reviews/{review_id}/approvals
POST /research/reviews/{review_id}/decisions
```

Decisions may reject, request changes, retain observation, approve future paper candidacy, roll back, retire, or archive. No live-trading approval outcome exists.

Every approval references an immutable evidence snapshot and becomes invalid after material evidence changes.

## 23. Performance, SLO, Quota, and Cost

Read resources:

```http
GET /operations/performance
GET /operations/reliability
GET /operations/slis
GET /operations/slos
GET /operations/error-budgets
GET /operations/capacity
GET /operations/quotas
GET /operations/costs
GET /operations/forecasts
GET /operations/resilience-tests
GET /operations/resilience-tests/{test_run_id}
```

Returns source quality, environment/revision/window, definitions, sample adequacy, results, limitations, incidents, and evidence links.

Cost/quota/forecast endpoints never expose credentials and cannot purchase, upgrade, scale, or increase budgets automatically.

Profit is not an SLI/SLO.

## 24. Governance, Security, Privacy, and Release

Read resources:

```http
GET /governance/authorization
GET /governance/rls
GET /governance/secrets
GET /governance/migrations
GET /governance/security
GET /governance/privacy
GET /governance/backups
GET /releases
GET /releases/{release_id}
GET /releases/{release_id}/gates
GET /releases/{release_id}/deployment
GET /releases/{release_id}/rollback
GET /releases/{release_id}/audit
```

Approved commands include versioned configuration lifecycle, finding/exception review, secret-rotation evidence, migration/release approval, deployment state recording, and rollback according to M023/M035/M036 contracts.

No API returns secret values, usable secret hashes, direct database credentials, or arbitrary deployment controls.

## 25. Change Management and Staged Rollout

Read resources:

```http
GET /changes
GET /changes/proposals
GET /changes/proposals/{change_id}
GET /changes/proposals/{change_id}/impact
GET /changes/proposals/{change_id}/evidence
GET /changes/proposals/{change_id}/approvals
GET /changes/proposals/{change_id}/rollout
GET /changes/proposals/{change_id}/rollback
GET /changes/proposals/{change_id}/audit
GET /changes/calendar
GET /changes/freezes
GET /changes/emergency
GET /changes/deprecations
```

Commands support proposal lifecycle, evidence-plan approval, immutable approval decisions, stage start/complete/pause/halt, rollback, emergency containment with expiry, deprecation, and archive.

Every approval references the exact immutable snapshot hash. Material changes invalidate prior approval. Activation applies only to future paper configurations. Tests, AI, metrics, scores, CI, or browser state cannot auto-approve or activate behavior.

## 26. Developer Portal and Evidence

Read resources:

```http
GET /developers
GET /developers/revision
GET /developers/docs
GET /developers/adrs
GET /developers/api
GET /developers/schemas
GET /developers/errors
GET /developers/events
GET /developers/permissions
GET /developers/metrics
GET /developers/tasks
GET /developers/requirements
GET /developers/traceability
GET /developers/tests
GET /developers/invariants
GET /developers/runbooks
GET /developers/docs-health
GET /developers/releases/{release_id}/evidence
```

Interactive API examples default to static/fake or isolated environments. Arbitrary hosts, secret headers, production-research mutations, raw SQL, and browser code execution are prohibited.

## 27. Audit and Exports

### `GET /audit/events`

Filters: workspace, actor, source, entity, event type, outcome, severity, error/reason code, correlation/cycle/experiment, and bounded date range.

Audit records are immutable and authorization-filtered.

### Export commands

```http
POST /exports
GET  /exports
GET  /exports/{export_id}
POST /exports/{export_id}/verify
POST /restores
GET  /restores/{restore_id}
```

Exports/restores record scope, environment, revision, migration head, hashes, protected storage classification, outcome, rebuild/reconciliation, limitations, and audit.

A successful backup/export request is not restore proof.

## 28. HTTP Status Guidance

- `200` successful read or synchronous command
- `201` resource created synchronously
- `202` asynchronous command accepted
- `204` successful command without response body
- `400` malformed request
- `401` unauthenticated or invalid session
- `403` unauthorized/recent-auth/permission failure as defined by endpoint policy
- `404` resource absent or not visible
- `409` state, idempotency, expected-version, freeze, or compatibility conflict
- `410` explicitly expired/removed resource when exposure is safe
- `422` semantic/domain validation failure
- `423` locked/frozen resource when used by the generated contract
- `429` rate limit or approved budget/quota gate
- `503` dependency unavailable or process not ready

Domain rejection must include stable machine-readable codes. Missing evidence never returns a misleading empty success.

## 29. OpenAPI and Contract Verification

Implementation requirements:

- generated OpenAPI is deterministic and revision/hash identified;
- CI detects uncommitted OpenAPI or generated-type changes;
- every public operation has a stable operation ID, permission, schemas, error codes, idempotency/concurrency rules, environment availability, source handler, and automated tests;
- examples validate against schemas and use synthetic values;
- endpoint inventory detects undocumented operations;
- public project schemas never leak provider SDK types;
- Decimal, timestamp, enum, nullability, unit, redaction, and compatibility rules are explicit;
- breaking differences require M034 review and an API migration/version plan.

## 30. Prohibited APIs

M001–M036 must not expose:

- private Binance credentials, orders, withdrawals, custody, leverage, margin, derivatives, options, shorting, or live execution;
- arbitrary prompt/system-instruction submission;
- Gemini tool invocation or side-effect control;
- arbitrary SQL or database console;
- raw environment-variable/secret editing;
- arbitrary workflow dispatch or deployment shell;
- direct ledger/fill/audit/approval mutation or deletion;
- generic risk/halt/reconciliation bypass;
- automatic plan purchase, scaling, budget increase, strategy promotion, release approval, or behavior activation.

## 31. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `PRODUCT_REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `DATABASE_SCHEMA.md`
- `SECURITY.md`
- `OBSERVABILITY.md`
- `TESTING.md`
- `AUTH_CONFIGURATION_SECURITY_RELEASE_WORKSPACE_IMPLEMENTATION.md`
- `EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `CHANGE_MANAGEMENT_ROLLOUT_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
