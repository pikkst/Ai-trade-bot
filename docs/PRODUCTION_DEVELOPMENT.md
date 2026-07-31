# Production Development After the MVP

Last reviewed: 2026-08-01  
Status: Authoritative staging and production-research plan mapped to `M030–M036`; live trading not authorized

## 1. Purpose

Define how The Daily Roast AI evolves after the deterministic local product, free-cloud demo, and controlled paper experiment into a reliable production-grade research service.

Production development means production-quality software engineering, operations, security, privacy, support, and governance. It does not mean real-money trading, private Binance access, public billing, or automatic SaaS launch.

## 2. Canonical Master-Task Path

```text
M029       Complete and close the controlled paper experiment
M030       Measure performance, resilience, SLO, quota, cost, and capacity
M031       Govern datasets, lineage, retention, archive, and reproducibility
M032       Complete research review and strategy lifecycle decisions
M033       Operationalize incident response, postmortems, and corrective actions
M034       Govern material behavior changes and staged paper rollout
M035       Make post-experiment decision and validate isolated staging
M036       Launch and operate production research
Future     Separate Binance test/private and real-capital assessments
```

No phase may be skipped because paper or backtest performance appears favorable.

## 3. Product Profiles

### 3.1 Production Research Service — M036

An authenticated system providing:

- market evidence and immutable snapshots;
- validated Gemini-assisted advisory reports;
- deterministic strategy and risk comparisons;
- paper portfolios and append-only accounting;
- reproducible backtests and benchmarks;
- experiments, incidents, audit history, exports, and research reviews;
- governance, Trust Center, support, and operational status.

It uses public market data and simulated execution.

### 3.2 Binance Test Environment — Future Assessment

A later isolated profile using private test credentials for exchange order lifecycle and reconciliation. It is outside M001–M036 and requires a separate specification, threat model, tasks, accounting review, staged verification, and owner approval.

### 3.3 Live-Capital Profile — Not Approved

Requires a separate legal, exchange-eligibility, tax, financial-risk, credential, accounting, operational, emergency-control, independent-review, and owner-decision milestone. No current document authorizes it.

## 4. M030–M034 Evidence Hardening

Before staging is considered, the project must produce:

### Performance and FinOps — M030

- versioned SLIs/SLOs and error budgets;
- API/frontend/cycle/database/backtest/provider measurements;
- free-tier and provider quota snapshots;
- billed/estimated/free-allowance cost classification;
- capacity forecasts and architecture triggers;
- resilience and recovery evidence.

### Data Governance — M031

- dataset/version registry and manifests;
- source-to-derived lineage;
- quality gates, quarantine, and correction propagation;
- retention, legal/operational holds, archive, restore, deletion/anonymization boundaries;
- reproducibility after archive/restore.

### Research Review — M032

- hypothesis and test-plan evidence;
- train/validation/untouched-test integrity;
- variants, benchmarks, robustness, walk-forward, reproducibility, costs, risk, and paper observation;
- reviewer conflicts and owner decision;
- strategy promotion only to future paper configurations.

### Incident Learning — M033

- alert routing and deduplication;
- containment, restoration, financial-integrity verification, and resolution as distinct states;
- evidence preservation and communication;
- postmortems, corrective actions, and effectiveness review.

### Change Management — M034

- immutable change proposals and behavior-set hashes;
- impact, compatibility, security/privacy, migration, cost/capacity, accessibility, and evidence review;
- immutable approval snapshots;
- staged paper canaries and stop conditions;
- rollback/forward fix, emergency expiry, deprecation, and removal gates.

## 5. M035 Post-Experiment Decision

The owner records one explicit outcome:

- stop the project or a workstream;
- repeat the experiment with an approved new hypothesis/configuration;
- improve identified reliability, data, UX, AI, strategy, risk, or operational gaps;
- advance a specific release candidate to isolated staging.

The decision includes:

- experiment and evidence snapshot references;
- reliability, data, AI, strategy, risk, accounting, incident, security/privacy, cost, and user-comprehension findings;
- limitations and unfavorable results;
- reviewer conflicts;
- rationale and follow-up task IDs;
- owner approval.

Advancement is not automatic.

## 6. Staging Requirements — M035

Staging is production-like but fully isolated.

It uses separate:

- PostgreSQL/Supabase project;
- Auth identities and signing material;
- Gemini project and API key;
- domains and certificates;
- storage buckets;
- deployment credentials;
- monitoring and incident destinations;
- configurations, budgets, and paper portfolios.

Production data may enter staging only through an approved anonymized export. Synthetic data is preferred.

## 7. Production Architecture Review

The free-cloud stack is not assumed to be the permanent production stack. Before staging approval, review measured evidence for:

- PostgreSQL capacity, pooling, backups, and recovery;
- API hosting availability and cold starts;
- scheduler guarantees and delayed/missed cycle behavior;
- long-running job/backtest requirements;
- persistent worker or queue need;
- WebSocket ingestion need;
- object storage and retention;
- observability retention and incident routing;
- support requirements;
- provider quota, cost, and regional/terms constraints.

Possible changes such as paid hosting, upgraded Supabase/PostgreSQL, Redis/ARQ, persistent workers, WebSocket ingestion, managed metrics, or object storage must pass M034. No component is adopted from speculation alone.

## 8. Production Backend Requirements

- immutable deploy artifacts;
- application version and commit SHA;
- one migration head and controlled migration execution;
- connection management appropriate to measured load;
- graceful startup/shutdown;
- liveness and readiness;
- bounded concurrency and resource limits;
- stable error/reason taxonomy;
- idempotent commands and cycles;
- outbox where reliable post-commit delivery matters;
- no network call inside financial transactions;
- safe retry/dead-letter behavior where applicable;
- complete audit/correlation identities;
- append-only ledger and mandatory reconciliation;
- paper-only execution flags enforced at startup and runtime.

## 9. Production Frontend Requirements

- custom domain and TLS;
- strict environment allowlist;
- no server secret in client artifacts;
- CSP, secure Auth, session expiry, and recovery behavior;
- accessible loading/error/stale/halt/reconciliation states;
- keyboard, screen reader, zoom/reflow, contrast, and reduced motion;
- persistent environment, simulation, freshness, risk, incident, and blocker state;
- responsive evidence/portfolio/decision views;
- English/Estonian semantic parity;
- privacy-reviewed analytics only when approved;
- measured performance budgets.

## 10. Data and Migration Management

### Schema Changes

- all changes use committed additive migrations;
- applied migrations are immutable;
- clean and supported-upgrade paths are tested;
- destructive changes use expand-migrate-contract;
- staging rehearses the exact migration set;
- production migrations run once through a protected step;
- rollback compatibility or forward-fix strategy is documented;
- migration drift blocks deployment.

### Data Retention

Production policy defines retention and hold behavior for:

- market candles and corrections;
- snapshots and features;
- raw/provider metadata and validated Gemini reports;
- audit, incidents, approvals, and release evidence;
- paper orders, fills, ledger, and portfolio states;
- backtest events and artifacts;
- application/operational logs;
- exports, archives, and backups;
- personal data and deleted accounts.

### Privacy

Before external users:

- controller/processor roles are documented;
- personal-data categories and purposes are defined;
- lawful basis and retention are reviewed;
- access/export/correction/deletion workflows are implemented where required;
- provider transfers and regional terms are reviewed;
- personal data is not sent to Gemini unless separately designed and approved.

## 11. Authentication and Authorization

Production research requires:

- verified identity or approved provider;
- short-lived sessions/tokens;
- secure rotation/revocation/recovery design;
- optional/required MFA for sensitive owner commands according to policy;
- handler-level authorization plus RLS;
- owner/operator/viewer permissions and service-role separation;
- recent authentication for high-risk commands;
- privileged-action and denied-attempt audit;
- rate limiting and abuse protection;
- periodic access reviews.

## 12. Secrets

- no plaintext secrets in repository, images, browser builds, logs, prompts, reports, telemetry, screenshots, or fixtures;
- separate secrets by environment;
- least-privilege service identities;
- scheduled and incident-driven rotation;
- emergency revocation and verification;
- secret-access audit where supported;
- service-role/database/Gemini credentials remain backend/workflow-only;
- private Binance credentials remain prohibited.

## 13. CI/CD and Release Management

Required sequence:

1. validate Master Task and detailed-card evidence;
2. format, lint, type, unit/property/integration/contract/E2E/accessibility tests;
3. validate migrations, RLS, Auth, and restore;
4. run security/privacy/dependency/secret/artifact scans;
5. build immutable frontend/backend artifacts;
6. verify OpenAPI, types, schemas, docs, SBOM, and generated hashes;
7. deploy unchanged artifacts to staging;
8. run staging smoke, E2E, load, failure, security/privacy, accessibility, restore, and rollback checks;
9. create immutable release approval snapshot;
10. obtain manual production approval;
11. run controlled production migration;
12. deploy immutable artifacts;
13. run health, Auth, RLS, smoke, and reconciliation checks;
14. verify alerts, support, status, cost, and release metadata;
15. roll back or halt on critical failure.

Direct unreviewed deployment from a workstation is prohibited.

## 14. Branching and Release Strategy

- `main` remains releasable;
- short-lived Master-Task branches;
- pull requests with required checks and evidence;
- semantic version tags where adopted;
- protected staging/production-research environments;
- release notes generated from task/changelog evidence;
- emergency changes use M034 expiry and retrospective review;
- a long-lived `develop` branch is introduced only for measured workflow need.

## 15. Observability, SLOs, and Error Budgets

Production research defines measured objectives for:

- authenticated API availability and latency;
- scheduled-cycle completion and delay;
- market-data freshness;
- Gemini valid-report rate and fallback availability;
- portfolio reconciliation success;
- zero duplicate financial side effects;
- zero unresolved ledger mismatch;
- backup/export completion;
- restore and reconciliation success;
- documentation/release evidence availability.

Profit is not an SLI or SLO.

Signals include structured logs, errors, metrics, uptime checks, database/provider health, quota/cost alerts, security/Auth alerts, audit events, and status communication.

## 16. Backup and Disaster Recovery

Production requires:

- automated encrypted backups where selected;
- documented retention;
- point-in-time recovery where justified;
- independent exports where required;
- regular isolated restore tests;
- migration verification and ledger reconstruction after restore;
- measured RPO/RTO;
- incident command and communication;
- backup-failure alerts and blockers.

A backup is not accepted until restore succeeds and reconciles.

## 17. Security and Privacy Gates

Before M036:

- threat model updated;
- Auth/RLS independently reviewed;
- secrets and environment boundaries reviewed;
- dependency/container/filesystem scans satisfy policy;
- focused security assessment completed as appropriate;
- incident and credential-rotation runbooks tested;
- data-handling and privacy review completed;
- no critical/high unresolved finding without a permitted time-limited exception;
- no client secret or private exchange path;
- live-trading-disabled state verified.

## 18. Cost and Capacity

Production development includes:

- service budgets and alerts;
- Gemini request/token/cost controls;
- database/storage/egress/build-minute forecasts;
- backtest concurrency and retention limits;
- cost per experiment/workspace/user where evidence exists;
- billed versus estimated classification;
- degradation behavior at budget/quota exhaustion;
- no automatic purchase, scale, or budget increase.

Free tiers are not permanent production capacity claims.

## 19. Required Operational Runbooks

- failed deployment;
- failed migration;
- database unavailable;
- Auth provider failure/account compromise;
- Gemini outage/quota/safety/schema failure;
- Binance data stale/provider unavailable;
- duplicate-cycle suspicion;
- ledger/reconciliation mismatch;
- export/backup failure;
- restore operation;
- suspected secret leak and rotation;
- production halt/read-only mode;
- SLO fast burn or capacity exhaustion;
- incident communication and postmortem.

Runbooks require dry-run/drill evidence, owner, review date, prerequisites, validation, and recovery steps.

## 20. Staging Acceptance Gate — M035

Staging is accepted when:

- the post-experiment decision explicitly approves a release candidate;
- M030–M034 evidence is complete enough for the candidate;
- environment isolation is proven;
- production artifacts run unchanged;
- migration rehearsal and compatibility pass;
- E2E/load/failure/accessibility/security/privacy/restore/rollback tests pass;
- provider budgets/quotas and operational ownership are ready;
- all release blockers are resolved or permitted by policy;
- live trading remains disabled.

## 21. Production Research Launch Gate — M036

Launch occurs when:

- M035 is verified;
- protected CI/CD and manual approval are active;
- backup/restore and rollback are current;
- Auth/RLS/secrets/privacy/security reviews pass;
- SLO/capacity/cost and incident routing are active;
- support, status, disclaimers, and data policies are published;
- controlled migration/deploy/smoke/reconciliation succeeds;
- release evidence maps to one commit, migration head, dependency set, configuration set, and behavior set;
- live trading remains disabled.

## 22. Continuous Production Operation

After launch:

- measure usage, reliability, cost, and comprehension;
- review access, security, privacy, recovery, and provider terms;
- maintain dependencies and model/prompt upgrades through M034;
- maintain API compatibility and version migrations;
- run incident reviews and corrective-action effectiveness checks;
- review strategies through M032;
- review costs/capacity monthly or at approved cadence;
- keep documentation/generated evidence current;
- preserve paper-only operation.

## 23. Future Execution Separation

A production research product may operate indefinitely without live trading.

Binance test/private and live-capital work requires a separate specification covering jurisdiction, exchange eligibility, credentials, exchange reconciliation, real-loss limits, approvals, market/operational failures, independent code/accounting review, legal/tax obligations, and emergency disablement.

No M036 or production maintenance task may silently introduce a live order path.

## 24. Related Documents

- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `TASK_CATALOG_INDEX.md`
- `LOCAL_DEVELOPMENT.md`
- `TEST_ENVIRONMENTS.md`
- `DEPLOYMENT.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `SECURITY.md`
- `ROADMAP.md`
- `/LOCAL_AND_PRODUCTION_TASKS.md`
