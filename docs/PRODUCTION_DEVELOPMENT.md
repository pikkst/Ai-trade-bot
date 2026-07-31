# Production Development After the MVP

Last reviewed: 2026-07-31
Status: Authoritative post-demo development plan; does not authorize live trading

## 1. Purpose

Define how the project evolves after the local prototype, public cloud demo, and controlled 30-day paper experiment into a reliable production-grade research product.

Production development means production-quality software engineering and operations. It does not automatically mean real-money trading, private Binance API access, or public SaaS availability.

## 2. Promotion Sequence

```text
Local development
  -> automated CI
  -> cloud demo
  -> controlled paper experiment
  -> staging
  -> production research service
  -> separately approved Binance sandbox
  -> separately approved live-trading assessment
```

No stage may be skipped solely because the previous stage appeared profitable.

## 3. Production Product Profiles

### 3.1 Production Research Service

A customer- or owner-facing system that provides:

- authenticated market research;
- Gemini-assisted reports;
- deterministic strategy comparisons;
- paper portfolios;
- reproducible backtests;
- exports and audit history.

This profile still uses public Binance data and simulated trading.

### 3.2 Binance Sandbox Profile

A later isolated profile using private test-environment credentials for order lifecycle and reconciliation. It requires a separate architecture and security gate.

### 3.3 Live Trading Profile

Not approved by this document. Requires a separate owner decision, legal review, financial-risk specification, independent review, and implementation milestone.

## 4. Environment Separation

Production development requires at least:

- local;
- CI;
- demo;
- staging;
- production.

Each environment must use separate:

- Supabase or PostgreSQL projects;
- Auth users and signing material;
- Gemini projects and API keys;
- domains;
- storage buckets;
- deployment credentials;
- monitoring destinations;
- experiment and risk configurations.

Data may move from production to lower environments only through approved anonymized or synthetic exports.

## 5. Production Architecture Review

The free-cloud stack is not automatically the final production stack. Before production promotion, review:

- managed PostgreSQL capacity and backup guarantees;
- connection pooling;
- API hosting availability;
- background-job reliability;
- scheduler guarantees;
- long-running worker requirements;
- WebSocket necessity;
- observability retention;
- incident response needs;
- cost and vendor limits.

Possible production changes include:

- managed paid PostgreSQL or upgraded Supabase;
- a persistent worker platform;
- Redis/ARQ or another durable job system;
- Binance WebSocket ingestion with REST gap repair;
- managed metrics and alerting;
- object storage for reports and backups.

Every change requires an ADR and migration plan.

## 6. Production Backend Requirements

- immutable deploy artifacts;
- explicit application version and commit SHA;
- database connection pooling suitable for the selected platform;
- graceful startup and shutdown;
- health and readiness checks;
- bounded concurrency;
- stable error taxonomy;
- idempotent commands and jobs;
- transactional outbox where post-commit delivery matters;
- no network calls inside financial transactions;
- safe retry and dead-letter behavior;
- complete audit and correlation identifiers.

## 7. Production Frontend Requirements

- custom domain and TLS;
- strict environment configuration;
- no server secrets in build artifacts;
- content security policy;
- secure authentication flow;
- error and loading states;
- accessibility for primary workflows;
- explicit environment and simulation labels;
- responsive portfolio and decision-lineage views;
- privacy-preserving analytics only after approval;
- frontend performance budgets.

## 8. Data and Migration Management

### Schema Changes

- all changes use committed migrations;
- migrations are tested from empty and current staging state;
- destructive changes require expand-migrate-contract sequencing;
- production migrations run once through a controlled job;
- application rollback compatibility is documented;
- migration drift blocks deployment.

### Data Retention

Production policy must define retention for:

- market candles;
- raw and validated Gemini responses;
- audit events;
- paper ledger and fills;
- backtest events;
- application logs;
- exports and backups;
- deleted user data.

### Data Privacy

Before serving external users:

- define controller and processor roles;
- document personal-data categories;
- define lawful basis and retention;
- support access, deletion, and export where required;
- avoid sending personal data to Gemini unless explicitly designed and approved.

## 9. Authentication and Authorization

Production must use:

- verified email or approved identity provider;
- short-lived sessions or tokens;
- secure refresh/session rotation;
- server-side role enforcement;
- owner, operator, and viewer permissions;
- privileged-action audit;
- rate limiting and abuse protection;
- account recovery and revocation procedures;
- optional MFA before high-risk administrative actions.

## 10. Secret Management

- no plaintext secrets in repositories, images, browser builds, logs, or reports;
- separate secrets per environment;
- least-privilege service accounts;
- scheduled rotation;
- emergency revocation;
- secret-access audit where supported;
- service-role credentials restricted to backend and controlled jobs;
- private Binance credentials prohibited until a later approved milestone.

## 11. CI/CD and Release Management

Production pipelines must use protected environments.

Required stages:

1. source and task validation;
2. formatting, linting, typing, and tests;
3. migration validation;
4. security and dependency scans;
5. frontend and backend builds;
6. generated artifact verification;
7. staging deployment;
8. staging smoke and E2E tests;
9. manual production approval;
10. migration deployment;
11. application deployment;
12. post-deploy smoke and reconciliation checks;
13. release record and rollback readiness.

Direct unreviewed deployment from a developer workstation is prohibited.

## 12. Branching and Release Strategy

Recommended:

- `main` remains releasable;
- short-lived feature branches;
- pull requests with required checks;
- semantic version tags;
- protected staging and production environments;
- release notes generated from task and changelog data;
- emergency fixes use the same review and audit standards with expedited approval.

A separate long-lived `develop` branch is optional and should be introduced only if it solves a demonstrated workflow problem.

## 13. Observability and SLOs

Production development must define measured SLOs for:

- API availability;
- API latency;
- scheduled-cycle success;
- market-data freshness;
- Gemini valid-report rate;
- experiment and portfolio integrity;
- backup completion;
- restore time;
- zero unresolved ledger mismatch;
- zero duplicate financial side effect.

Profit is not an SLO.

Required production signals:

- structured centralized logs;
- error aggregation;
- metrics and dashboards;
- alert routing;
- uptime checks;
- database health and slow-query monitoring;
- provider quota and cost alerts;
- security and authentication alerts;
- audit events.

## 14. Backup and Disaster Recovery

Production requires:

- automated encrypted backups;
- documented retention;
- point-in-time recovery where justified;
- off-provider or independent export where required;
- regular restore tests;
- ledger reconstruction checks after restore;
- documented RPO and RTO;
- incident command and communication process.

A backup is not accepted until a restore has been tested.

## 15. Security Review Gates

Before production research launch:

- threat model updated;
- authentication and RLS independently reviewed;
- dependency and container scans clean according to policy;
- secrets and environment boundaries reviewed;
- penetration test or focused security assessment completed as appropriate;
- incident response runbook tested;
- data-handling and privacy review completed;
- no critical or high unresolved finding without explicit documented exception.

Before private Binance API work, perform an additional credential and financial-side-effect threat model.

## 16. Cost and Capacity Management

Production development must include:

- service budgets and alerts;
- Gemini request, token, and cost budgets;
- database storage growth estimates;
- egress and build-minute estimates;
- backtest concurrency limits;
- report retention policies;
- cost per active user or experiment;
- documented degradation behavior when a budget is exhausted.

Provider free tiers must not be represented as permanent production capacity.

## 17. Operational Runbooks

Required before production research launch:

- failed deployment;
- failed migration;
- database unavailable;
- authentication provider failure;
- Gemini outage or quota exhaustion;
- Binance data stale;
- duplicate-cycle suspicion;
- ledger mismatch;
- backup failure;
- restore operation;
- suspected secret leak;
- account compromise;
- production halt and read-only mode.

## 18. Staging Requirements

Staging must be production-like but isolated.

It must support:

- production build artifacts;
- separate database and Auth;
- safe synthetic fixtures;
- migration rehearsal;
- protected Gemini smoke calls;
- full E2E tests;
- load and failure testing;
- release-candidate approval;
- reset without production impact.

## 19. Production Research Launch Gate

The production research service may launch when:

- local, CI, demo, and staging flows are stable;
- paper experiment findings are reviewed;
- production architecture and ADRs are approved;
- migrations and rollback compatibility are verified;
- Auth, RLS, and secret handling pass review;
- backup and restore pass;
- operational alerts and runbooks are active;
- costs and quotas are budgeted;
- user-facing disclaimers and data policies are present;
- live trading remains disabled.

## 20. Post-Launch Development

After production research launch:

- measure actual usage and reliability;
- prioritize from evidence rather than speculative scale;
- perform blameless incident reviews;
- maintain dependency and model upgrades through evaluation gates;
- compare Gemini versions using frozen datasets;
- maintain backward-compatible APIs;
- archive or migrate old strategy, prompt, and schema versions safely;
- review costs monthly;
- review security and recovery readiness regularly.

## 21. Live Trading Separation

A production research product may exist indefinitely without live trading.

Live trading requires a separate specification covering:

- jurisdiction and exchange eligibility;
- private API authentication;
- credential protection;
- exchange reconciliation;
- real-money risk policy;
- manual approvals;
- capital limits;
- market and operational failure handling;
- independent code and accounting review;
- legal and tax considerations;
- emergency disablement.

No production research task may silently introduce a live order path.

## 22. Related Documents

- `LOCAL_DEVELOPMENT.md`
- `TEST_ENVIRONMENTS.md`
- `DEPLOYMENT.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `SECURITY.md`
- `ROADMAP.md`
- `/LOCAL_AND_PRODUCTION_TASKS.md`
