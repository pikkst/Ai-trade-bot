# Security

Last reviewed: 2026-08-01  
Status: Authoritative security, privacy, financial-integrity, and release-gate baseline mapped to `M001–M036`

## 1. Security Objectives

- prevent unauthorized reads and state changes;
- prevent secret, credential, personal-data, and provider-payload disclosure;
- preserve integrity of market data, AI evidence, decisions, orders, fills, ledger, portfolio state, experiments, approvals, releases, and audit history;
- prevent replayed, overlapping, or duplicated side effects;
- keep probabilistic AI outside execution and control authority;
- detect and halt on financial, reconciliation, configuration, Auth, RLS, or evidence-integrity failures;
- recover from export, database, provider, deployment, and credential incidents without fabricating evidence;
- preserve environment isolation and immutable running-experiment behavior;
- keep private Binance, Binance test orders, live capital, leverage, margin, derivatives, shorting, custody, and withdrawals outside M001–M036.

## 2. Master-Task Ownership

| Security area | Master Tasks |
|---|---|
| toolchain, secrets, local database/Auth/RLS, settings/errors/logging, provider fakes | M001–M006 |
| market/AI/strategy/risk/execution/accounting safety | M007–M013 |
| API authorization, commands, product surfaces, governance/release views | M014–M025 |
| integrated security, export/restore, recovery gate | M026–M027 |
| cloud isolation and experiment preflight/operation | M028–M029 |
| operational, data, research, incident, and change evidence | M030–M034 |
| staging and production-research review/operation | M035–M036 |

A control is not complete because its documentation exists. Its mapped Master Task must be `VERIFIED` with implementation evidence.

## 3. Protected Assets

High-value assets include:

- Supabase Auth signing/JWKS configuration and user identities;
- application, workflow/service, read-only, and migration credentials;
- Gemini API keys, provider projects, budgets, prompts, schemas, and validated reports;
- workspace memberships, effective permissions, recent-authentication evidence, and RLS policies;
- immutable configuration and behavior-set versions;
- market data, corrections, datasets, snapshots, features, and lineage;
- deterministic strategy/risk versions and decisions;
- paper orders, reservations, fills, append-only ledger entries, portfolio states, and reconciliation evidence;
- experiments, cycles, locks, incidents, exports, restores, approvals, releases, deployments, and rollbacks;
- audit, documentation, test, scan, SBOM, and change-management evidence;
- CI/CD credentials and protected environment approvals.

## 4. Trust Boundaries

- browser to Supabase Auth;
- browser to FastAPI;
- approved browser reads to RLS-protected Supabase objects;
- FastAPI/CLI to PostgreSQL;
- FastAPI to Supabase Auth verification configuration;
- one-shot CLI to Binance public REST;
- one-shot CLI to Gemini;
- GitHub Actions to protected cloud environment;
- Cloudflare Pages and Render deployment boundaries;
- operator/owner commands to application authorization and audit;
- staging and production-research environment boundaries;
- export/archive/backup storage boundaries.

All external input, provider output, environment configuration, and browser state is untrusted until validated.

## 5. Threat Model

### Spoofing

Threats:

- stolen or forged Supabase access token;
- stale/revoked session;
- forged workflow/service identity;
- leaked Gemini, database, service-role, or deployment credential;
- impersonated actor in audit evidence.

Controls:

- issuer/audience/signature/JWKS/expiry verification;
- short-lived sessions and provider-supported revocation;
- recent authentication for sensitive owner commands;
- separate scoped service/workflow/migration identities;
- environment-separated secrets and protected CI environments;
- actor/correlation/request evidence and denied-attempt audit.

### Tampering

Threats:

- altered candles, datasets, prompts, schemas, strategy/risk rules, execution assumptions, migrations, ledger entries, approvals, or release evidence;
- changing a running experiment through mutable environment variables or database rows;
- editing an applied migration;
- browser direct writes to critical tables.

Controls:

- immutable finalized evidence and explicit corrections;
- versioned canonical hashes and behavior sets;
- additive immutable migrations and drift detection;
- append-only ledger/audit/approval/transition evidence;
- RLS plus handler authorization;
- browser direct-write denial;
- exact configuration-hash preflight and active-experiment freeze;
- M034 change governance.

### Repudiation

Threats:

- denial of experiment start/halt, role change, risk-policy change, release approval, emergency change, or incident action.

Controls:

- immutable actor, source, from/to state, reason, timestamp, correlation, expected version, approval snapshot, and audit references;
- durable denied-attempt evidence;
- protected environment approvals and release provenance.

### Information Disclosure

Threats:

- secrets in source, environment dumps, logs, metrics, traces, prompts, responses, screenshots, artifacts, client bundles, exports, errors, or source maps;
- cross-workspace existence leaks;
- unrestricted raw provider content;
- personal data sent to Gemini or lower environments.

Controls:

- strict variable inventory and public frontend allowlist;
- redaction filters and bounded telemetry labels;
- generic authentication/resource errors;
- RLS and application scope checks before result creation;
- minimum-data provider requests;
- synthetic/anonymized lower-environment data;
- role-aware diagnostics and retention;
- secret/bundle/artifact scanning.

### Denial of Service and Resource Exhaustion

Threats:

- excessive API, export, analysis, backfill, backtest, search, or login requests;
- provider retry storms;
- GitHub schedule overlap;
- database connection/storage exhaustion;
- Gemini quota or cost exhaustion;
- unbounded metrics or logs.

Controls:

- rate limits, bounded schemas/ranges/pagination/concurrency/timeouts;
- exponential backoff with jitter and circuit/fallback policy;
- workflow concurrency plus database lock/lease;
- resource budgets and M030 capacity evidence;
- no automatic purchase, upgrade, scale, or budget increase;
- bounded telemetry cardinality and retention.

### Elevation of Privilege

Threats:

- viewer/operator performing owner actions;
- API allows while RLS allows too broadly;
- service role exposed to browser/runtime paths;
- migration credentials available to application runtime;
- Gemini/tool output changing financial or governance state;
- CI/test result automatically approving release or behavior.

Controls:

- server-provided effective permissions;
- handler-level authorization and workspace/resource checks;
- RLS assurance matrix and mismatch detection;
- scoped separated identities;
- no Gemini tools or side-effect authority;
- explicit human approvals tied to immutable snapshots;
- no automatic release, strategy, configuration, or behavior activation.

## 6. Identity and Session Model

Supabase Auth is the active identity provider profile.

Requirements:

- verify token issuer, audience, signature/JWKS, expiry, and required claims;
- use generic authentication errors and prevent account enumeration;
- apply rate limits and abuse controls;
- support provider/session revocation and secure sign-out;
- require recent authentication for sensitive owner commands according to policy;
- handle expired, revoked, invalid, disabled, locked, recovery-pending, and provider-unavailable states fail closed;
- never expose tokens, cookies, signatures, password hashes, recovery secrets, or Auth provider internals;
- do not introduce an unrelated custom password or JWT-signing subsystem without M034 governance and a separate reviewed design.

Exact refresh/session rotation, recovery, and MFA behavior must be implemented before production research and versioned through M023/M036.

## 7. Application Authorization

Roles:

- owner;
- operator;
- viewer.

System identities may include:

- application runtime;
- scheduled workflow/service;
- approved read-only operational identity;
- migration identity.

Every protected operation verifies:

- authenticated actor/system identity;
- workspace and resource scope;
- server-provided effective permission;
- recent authentication when required;
- expected version/optimistic concurrency for mutable aggregates;
- idempotency key for repeatable side effects;
- canonical reason code;
- command-state eligibility;
- immutable audit result.

Frontend visibility never substitutes for authorization.

## 8. Row Level Security

- enable RLS on every Data API-visible table/view;
- deny by default;
- expose only approved read views/fields;
- test anonymous, viewer, operator, owner, application, workflow/service, read-only, and migration identities;
- enforce workspace isolation;
- deny browser insert/update/delete on financial, AI, audit, experiment-control, access, incident, release, and change-management evidence;
- verify Supabase claim mapping and policy migration versions;
- detect API/RLS mismatch and treat API-deny/RLS-allow as a critical exposure;
- block experiment/release on missing or failed RLS assurance.

## 9. API Security

- strict project-owned request schemas and unknown-field rejection where appropriate;
- bounded body, query, date range, pagination, sort, filters, search, export, and backtest scope;
- operation-specific permissions and rate-limit classes;
- CORS allowlist and no wildcard credential mode;
- HTTPS outside local development;
- CSP and secure headers for the frontend/API profile;
- idempotency keys and expected versions for state-changing commands;
- recent authentication and explicit confirmation for sensitive owner actions;
- stable safe error envelopes with correlation IDs;
- ownership/resource-scope checks before revealing existence;
- immutable command/audit evidence;
- no arbitrary SQL, prompt, environment-variable, database-console, workflow-dispatch, provider-tool, or exchange-execution endpoint.

## 10. Secrets and Environment Configuration

- secrets come from protected environment stores or approved secret management;
- `.env.example` contains names, safe placeholders, and false defaults only;
- separate credentials per environment;
- frontend assets receive only explicitly allowlisted public values;
- environment variables configure wiring and bootstrap defaults, not mutable running-experiment behavior;
- a running experiment uses immutable database configuration and behavior-set hashes;
- secret inventory tracks purpose, environment, storage, scope, presence, rotation, exposure, and verification metadata without value or usable hash;
- suspected exposure creates an incident/blocker and requires revocation/rotation, dependent-service validation, and audit;
- `ALLOW_PAID_PROVIDER_USAGE`, auto-upgrade, auto-scale, private/test/live exchange, leverage/derivatives/shorting/custody/withdrawals, Gemini tools, and automatic approval/activation flags remain false in M001–M036;
- startup and release checks reject unsafe combinations.

## 11. Gemini Security

- send minimum approved structured evidence only;
- never send credentials, tokens, personal data, database URLs, unrelated private data, or unrestricted internal payloads;
- separate trusted instructions from untrusted evidence;
- disable search, shell, code, database, exchange, file, network, and side-effect tools in the MVP analysis flow;
- validate provider outcome, parsing, schema, fields/enums/ranges, evidence references, unsupported claims, false certainty, injection resistance, freshness/quality, and application policy;
- distinguish provider success from report acceptance;
- reject blocked, refused, malformed, stale, unsupported, injected, empty, or invalid output;
- degrade to deterministic fallback or HOLD on failure/budget exhaustion;
- enforce request/token/cost budgets before calls;
- preserve model/prompt/schema/safety/validation/fallback/usage/cost versions;
- process model/provider/prompt/schema changes through M034.

Gemini cannot create orders, size positions, change risk, alter experiments, approve releases, or mutate state.

## 12. Market, Strategy, Risk, and Execution Security

- public Binance REST only;
- no private exchange credential or order endpoint;
- finalized, approved, fresh data only for action paths;
- correction and invalidation evidence rather than silent rewrite;
- deterministic feature/strategy/risk outputs for identical inputs/versions;
- strategy emits typed intent and has no order authority;
- every non-HOLD intent passes deterministic risk;
- missing/invalid policy fails closed;
- risk can reduce, reject, or halt;
- one approved risk evaluation creates at most one paper order;
- paper execution applies immutable fee/spread/slippage/precision/minimum-notional/timing/partial-fill/cancellation rules;
- no shorting, leverage, margin, derivatives, custody, or withdrawals.

## 13. Financial Integrity

- use Decimal and explicit asset/currency units;
- use timezone-aware UTC;
- perform no network call inside a financial transaction;
- atomically commit order transition, fill, reservations, ledger entries, audit/outbox, and portfolio-state effect;
- append-only double-entry ledger is the financial source of truth;
- corrections use reversal/replacement transactions;
- filled quantity never exceeds approval;
- one logical side effect has one canonical idempotent identity;
- projections are rebuildable;
- every final financial cycle/experiment/report requires reconciliation;
- process exit or workflow success is not financial completion;
- mismatch, missing required lineage, duplicate-effect suspicion, negative/impossible balance, or unable-to-reconcile state creates critical evidence and halt.

## 14. Research-Cycle and Scheduler Security

- GitHub Actions schedule is best effort;
- use workflow concurrency and PostgreSQL lock/lease;
- persist intended/actual time, delay, lock, idempotency, stage, and terminal evidence;
- use actual eligible finalized data for delayed cycles;
- never reconstruct imagined trades for missed cycles;
- retries return existing resources or deterministic conflicts;
- a cycle is complete only after required stages and reconciliation;
- Render sleep/cold start must not control the schedule;
- untrusted fork code cannot access protected secrets or cloud environments.

## 15. Database and Migration Security

- separate application, workflow/service, read-only, and migration roles where deployed;
- PostgreSQL not publicly exposed beyond approved managed interfaces;
- TLS across untrusted networks;
- parameterized SQL/SQLAlchemy;
- committed additive migrations only;
- applied migrations immutable;
- clean reset, supported upgrade, one head, drift, constraint, index, RLS, and compatibility tests;
- destructive changes use expand-migrate-contract and approved forward-fix/rollback planning;
- staging rehearses the exact production migration set;
- production migration runs once through a protected job;
- migration drift/failure blocks deployment;
- ordinary paths cannot update/delete ledger, audit, approval, incident, release, or used-version evidence.

## 16. Data Governance and Privacy

- classify market, derived, AI, financial, operational, personal, public, and restricted data;
- minimize collection and provider transfer;
- use synthetic/anonymized lower-environment data;
- version retention, archival, legal/operational hold, deletion/anonymization, and export rules;
- cleanup is idempotent and cannot break financial, audit, incident, hold, or reproducibility lineage;
- destructive actions require dependency analysis, approval, expected version, and audit;
- do not claim legal compliance certification from engineering documentation;
- perform EU/Estonian privacy, consumer-protection, provider-terms, financial-service-boundary, and retention review before external production use.

## 17. Supply Chain and CI/CD

Required controls:

- committed dependency lock files;
- pinned GitHub Actions and images;
- dependency review and vulnerability scanning;
- Ruff, MyPy, Pytest/Hypothesis, Bandit, Semgrep;
- frontend audit and bundle inspection;
- Trivy for applicable filesystem/container artifacts;
- SBOM and release provenance before production research;
- secret scanning across source, history, artifacts, logs, examples, prompts, screenshots, and generated output;
- protected branches/environments and manual approvals;
- no normal PR access to production data, paid provider keys, cloud experiment secrets, or private exchange credentials;
- generated OpenAPI/schema/type/migration/documentation drift checks.

No release proceeds with unresolved critical findings or high findings outside a permitted time-limited exception with compensating controls and expiry.

## 18. Incident Response

Incident states are distinct:

- detected/alerted;
- acknowledged;
- triaged;
- contained;
- service restored;
- financial/data/security integrity verified;
- resolved;
- postmortem/corrective action complete.

Minimum response:

1. preserve evidence and establish incident ownership;
2. halt or restrict affected scope;
3. revoke/rotate compromised credentials;
4. determine scope, timeline, side effects, data exposure, and affected versions;
5. restore from trusted evidence when integrity is uncertain;
6. rebuild projections and reconcile;
7. patch and add regression tests;
8. communicate safely without exposing sensitive details;
9. complete postmortem and corrective actions;
10. resume only through explicit reviewed command/approval.

Service restoration does not automatically clear unresolved integrity, risk, security, privacy, RLS, or reconciliation halts.

## 19. Export, Backup, Restore, and Recovery

Before M028/M029 and production promotion:

- create protected exports/backups with revision, migration head, scope, time, and hash evidence;
- restore into an isolated environment;
- verify migrations and required records;
- rebuild projections;
- reconcile the ledger;
- record duration, outcome, limitations, and incident/runbook links;
- define measured RPO/RTO only from deployed capability;
- block applicable gate on failed/stale restore evidence.

A configured backup or provider success log is insufficient without tested restore.

## 20. Release, Research, and Change Governance

- release candidates reference immutable source, artifact, dependency, migration, configuration, behavior-set, scan, test, restore, and approval evidence;
- staging uses separate credentials/data and immutable production artifacts;
- research promotion requires hypothesis, benchmarks, untouched test, variants, robustness, reproducibility, costs, risk, paper observation, reviewer conflicts, and owner decision;
- material changes use immutable before/after behavior sets, impact, compatibility, evidence plan, approvals, staged paper canary, stop conditions, rollback/forward fix, and deprecation;
- emergency changes expire and require retrospective review;
- tests, AI, metrics, scores, browser controls, or CI cannot auto-approve or activate behavior;
- activation affects only future configurations and never mutates a running experiment.

## 21. Observability and Security Evidence

Durable evidence includes:

- authentication/authorization/RLS assurance and denied attempts;
- cycle locks, idempotency, stages, completeness, and failures;
- market quality/freshness/corrections;
- Gemini attempts/validation/usage/budget/fallback;
- strategy/risk/order/fill/ledger/state/reconciliation/halt;
- incidents, export/restore, releases, deployments, rollbacks, and changes;
- security findings, exceptions, scans, rotations, and reviews.

Logs and metrics are bounded/redacted diagnostic sources, not substitutes for durable evidence.

Profit is not an SLI/SLO. Zero duplicate financial effects and zero unresolved ledger mismatch are zero-tolerance invariants.

## 22. Mandatory Security Testing

- token issuer/audience/signature/expiry/revocation and session states;
- role/resource/recent-auth/expected-version/idempotency matrix;
- RLS identities, workspace isolation, and browser direct-write denial;
- secret, log, response, export, prompt, telemetry, screenshot, and bundle redaction;
- SQL/input/rate-limit/abuse cases;
- Gemini failure, grounding, unsupported claim, false certainty, injection, and budget paths;
- market stale/gap/correction behavior;
- risk boundaries and halts;
- duplicate/overlap/restart/cycle-completeness behavior;
- atomic ledger and reconciliation tamper detection;
- migration drift and applied-file immutability;
- export/restore/recovery and credential-rotation drills;
- dependency/supply-chain/artifact scans;
- unsafe environment-flag startup rejection;
- incident, approval, release, and change-state security.

## 23. Security Promotion Gates

### M026

All relevant deterministic security, Auth/RLS, financial, frontend, and generated-contract tests pass locally/CI.

### M027

Current export/restore, reconciliation, recovery drills, secret/supply-chain scans, and release-blocking finding review pass.

### M028

Cloud environment isolation, protected secrets, Auth/RLS, CORS/CSP/HTTPS, bundle safety, workflow concurrency, cold-start, and deployment smoke tests pass.

### M029

Exact configuration preflight, current restore, no active critical incident/halt, risk/ledger/reconciliation, provider budgets/fallback, and owner approval pass.

### M030–M034

Operational, data, research, incident, and behavior-change security evidence is complete.

### M035

Isolated staging migration, restore, E2E, load/failure, security/privacy/accessibility, rollback, and approval gates pass.

### M036

Protected deployment, controlled migration, current backup/restore, Auth/RLS/secrets/privacy review, incident/support/SLO/cost ownership, smoke/reconciliation, and live-trading-disabled assertion pass.

## 24. Related Documents

- `/AGENTS.md`
- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `API_SPECIFICATION.md`
- `DATABASE_SCHEMA.md`
- `GEMINI_INTEGRATION.md`
- `OBSERVABILITY.md`
- `TESTING.md`
- `DEPLOYMENT.md`
- `INCIDENT_RESPONSE_POSTMORTEM_LEARNING_WORKSPACE_IMPLEMENTATION.md`
- `CHANGE_MANAGEMENT_ROLLOUT_GOVERNANCE_WORKSPACE_IMPLEMENTATION.md`
