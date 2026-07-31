# Test Environments and Validation Strategy

Last reviewed: 2026-08-01  
Status: Authoritative test-environment specification mapped to `TASKS.md`

## 1. Purpose

Define how implementation evidence progresses from isolated tests to integrated local verification, a free-cloud demo, a controlled paper experiment, isolated staging, and production research without mixing credentials, data, authority, or risk assumptions.

`TASKS.md` defines implementation order. This document defines test environments and promotion evidence, not a competing backlog.

## 2. Environment Matrix

| Environment | Database | Providers | Purpose | Persistent |
|---|---|---|---|---|
| Unit | none or project-owned fakes | all fake | pure deterministic logic | no |
| Integration | ephemeral local PostgreSQL/Supabase | fake Binance and Gemini | persistence, Auth, RLS, transactions | no |
| Contract | isolated database | fixtures, mocks, recorded public structures | adapter/API compatibility | no |
| E2E local | local Supabase | fake by default | browser-to-ledger workflows | resettable |
| Free-cloud demo | dedicated Supabase project | Binance REST, fake or bounded Gemini | deployment and product demonstration | yes |
| Paper experiment | dedicated isolated project | Binance REST and bounded Gemini | formal 30-day paper test | yes |
| Staging | separate managed project | production-like providers with test controls | release validation | yes |
| Production research | separate managed project | approved research providers | authenticated paper-research operation | yes |

No environment shares database credentials, service-role keys, Auth user pools, signing material, Gemini keys, storage, or deployment credentials with another environment unless an explicit approved architecture says otherwise.

All environments remain live-trading-disabled within the current milestone.

## 3. Master-Task Promotion Mapping

| Gate | Required Master Tasks |
|---|---|
| Local foundation ready | M001–M006 |
| Core domains ready | M007–M013 |
| Product/API workspaces ready | M014–M025 |
| Integrated local/CI verification | M026 |
| Export/restore/security gate | M027 |
| Free-cloud demo | M028 |
| Formal paper experiment | M029 |
| Evidence hardening and governance | M030–M034 |
| Staging release candidate | M035 |
| Production research | M036 |

A later environment cannot compensate for an unverified earlier gate.

## 4. Test Pyramid

### Unit Tests

Cover:

- value objects and canonical serialization;
- indicator formulas;
- strategy decisions;
- risk limits and halts;
- order state machines;
- fees, spread, slippage, precision, and minimum-notional rules;
- ledger balancing and correction patterns;
- P&L, exposure, equity, and drawdown;
- schema validation and error mapping;
- compatibility, classification, and policy decisions.

Unit tests are deterministic, isolated, and fast.

### Property Tests

Cover invariants such as:

- every ledger transaction balances;
- no duplicate side effect under idempotent replay;
- only one lease owner per logical cycle;
- filled quantity never exceeds approval;
- approved notional never exceeds risk policy;
- balances and positions remain valid;
- reconstructed state equals reconciled state;
- stale/invalid AI cannot authorize an order;
- a halt blocks new entries;
- hashes are stable for canonical identical input.

### Integration Tests

Cover:

- SQLAlchemy mappings;
- migrations, constraints, indexes, and drift;
- transaction rollback and atomic fill/ledger posting;
- idempotency and optimistic concurrency;
- advisory lock or durable lease acquisition;
- Supabase Auth verification and claim mapping;
- RLS, approved views, and direct-write denial;
- export, restore, rebuild, and reconciliation.

### Contract Tests

Cover:

- Binance REST response mapping and error behavior;
- Gemini SDK request/response/error mapping;
- Supabase/PostgREST behavior used by the frontend;
- project OpenAPI and generated frontend types;
- Cloudflare build assumptions;
- Render startup, health, and cold-start contract;
- GitHub Actions schedule/concurrency assumptions.

Fixtures record source date, schema version, provider assumptions, and hashes without secrets or personal data.

### End-to-End Tests

Minimum successful flow:

1. authenticate an authorized synthetic identity;
2. load an authorized workspace and frozen configuration;
3. ingest finalized candles;
4. create a snapshot and deterministic features;
5. run fake Gemini analysis and validation;
6. create strategy intent;
7. apply deterministic risk;
8. create and fill a paper order when approved;
9. post ledger entries atomically;
10. reconcile the portfolio;
11. display complete decision lineage;
12. export and restore evidence when applicable.

Minimum failure flows:

- unauthenticated or unauthorized access;
- stale, missing, invalid, corrected, or gapped market data;
- Gemini authentication, timeout, rate limit, refusal, safety block, malformed or unsupported output, injection, stale source, and budget exhaustion;
- risk rejection or reduced size;
- drawdown or integrity halt;
- duplicate or overlapping research cycle;
- partial transaction failure;
- reconciliation mismatch;
- stale expected version;
- failed migration or restore;
- critical accessibility or secret-bundle regression.

## 5. Deterministic Fixtures

The repository includes versioned fixtures for:

- Binance symbol metadata;
- normal, malformed, duplicate, out-of-order, gapped, stale, and corrected candles;
- bullish, bearish, sideways, contradictory, and insufficient-history features;
- valid, invalid, malicious, refused, safety-blocked, and empty Gemini results;
- fee, spread, slippage, partial-fill, precision, and minimum-notional cases;
- strategy and risk boundaries;
- ledger transactions, reservations, reversals, replacements, rebuilds, and mismatches;
- backtest datasets, benchmarks, variants, and insufficient samples;
- Auth/RLS identities and workspace isolation;
- incidents, alerts, approvals, and change rollouts where implemented.

Fixture changes are reviewed as behavior changes because they may change expected outcomes.

## 6. Test Clocks, IDs, and Randomness

- time-dependent code uses a project-owned clock;
- tests freeze or advance time explicitly;
- random behavior uses an injected seeded generator;
- IDs are injected or generated deterministically where assertions require stability;
- production timestamps use timezone-aware UTC;
- no deterministic suite depends on wall-clock time, current market prices, or live provider output;
- smoke tests are explicitly separated and labeled non-deterministic.

## 7. Database and RLS Policy

CI proves:

- migrations apply from an empty database;
- one expected migration head exists;
- applied migrations are unchanged;
- seed data loads deterministically;
- constraints reject invalid states;
- financial and audit evidence is append-only where required;
- RLS prevents cross-workspace and unauthorized access;
- browser roles cannot write critical tables directly;
- service, workflow, read-only, and migration roles remain scoped and separated;
- approved views expose only approved fields;
- lease and idempotency behavior prevents overlap and duplicate effects;
- schema and generated documentation drift is detected.

Destructive downgrade tests are required only where downgrade is explicitly supported. Forward-fix is preferred, and expand-migrate-contract is used where compatibility windows are needed.

## 8. Provider Test Policy

### Gemini

Normal CI uses the deterministic fake provider. SDK-boundary tests use mocks or recorded non-sensitive structures.

A manually triggered protected Gemini smoke workflow may run only when:

- a dedicated non-production secret is configured;
- strict request, token, and cost budgets are enforced;
- untrusted fork code cannot access secrets;
- the provider/model/prompt/schema versions are recorded;
- results are labeled non-deterministic;
- failure is reported separately from deterministic tests;
- no tool, execution, credential, or risk authority is enabled.

### Binance

Normal CI uses fixtures and fakes. A bounded public REST smoke test may verify server time, exchange metadata, and a small finalized-candle request. It uses no private credential and cannot place an order.

## 9. Frontend and Accessibility Testing

Required layers:

- component tests;
- route and permission tests;
- generated API type checks;
- loading, empty, stale, partial, degraded, halted, unauthorized, and error states;
- keyboard and screen-reader checks;
- zoom/reflow, reduced-motion, and contrast checks;
- visual regression for safety-critical states;
- E2E browser tests;
- production build verification;
- public/private shell separation;
- English/Estonian semantic parity tests;
- environment-variable allowlist and source-map/bundle inspection.

The UI always identifies local, demo, paper experiment, staging, and production-research modes without implying live trading.

## 10. Security and Privacy Testing

Required checks:

- secret scanning;
- dependency and supply-chain review;
- Python and frontend static security analysis;
- Semgrep and approved custom rules;
- container/filesystem scan where artifacts exist;
- authentication, session, recent-authentication, authorization, and abuse tests;
- RLS and service-role isolation;
- prompt injection and unsupported-claim fixtures;
- log, trace, metric, response, export, and bundle redaction;
- CORS, CSP, HTTPS, and security-header assumptions;
- personal-data minimization, retention, export, deletion/anonymization, and provider-request boundaries when implemented;
- incident and credential-rotation drills.

## 11. Performance, Capacity, and Resilience Testing

Before the formal experiment:

- one cycle fits within the configured GitHub Actions timeout;
- common API reads meet measured development targets;
- database indexes support expected reads;
- backtests enforce bounded ranges, concurrency, memory, and timeout;
- duplicate cycles resolve through leases and idempotency;
- cold starts, provider delays, quota exhaustion, and database outages degrade safely;
- recovery does not fabricate trades.

Before production research:

- load, stress, spike, soak, and failure tests use approved isolated environments;
- query and connection-pool behavior is measured;
- frontend performance budgets are enforced;
- restore and recovery objectives are measured rather than invented;
- provider quota, cost, and capacity evidence is current;
- SLI/SLO/error-budget definitions and exclusions are versioned;
- no test automatically purchases or scales infrastructure.

## 12. Reliability and Recovery Scenarios

Test:

- interrupted cycle restart;
- duplicate or overlapping workflow delivery;
- delayed or missed GitHub schedule;
- Render cold start;
- temporary Supabase unavailability or pause;
- Gemini quota exhaustion and fallback;
- Binance timeout or stale data;
- partial database transaction failure;
- export and isolated restore;
- projection rebuild from ledger;
- reconciliation mismatch;
- experiment pause/halt and constrained resume;
- failed deployment or migration;
- secret exposure and rotation;
- incident containment, restoration, integrity verification, and corrective-action validation.

A backup is not accepted until restore and reconciliation succeed.

## 13. CI and Deployment Workflows

Expected workflow classes:

- quality — format, lint, types, unit/property tests;
- integration — local Supabase/PostgreSQL, migrations, Auth, RLS, integration tests;
- frontend — lint, types, components, accessibility, visual, E2E, build;
- security — secret, dependency, static, and artifact scans;
- documentation — links, IDs, inventory, generated artifacts, task format, conflicts, and freshness;
- provider smoke — protected bounded checks;
- research cycle — scheduled/manual one-shot cloud experiment;
- demo deployment — after M026–M027 gates;
- staging deployment — protected and production-like;
- production-research deployment — manual approval, controlled migration, smoke, and reconciliation.

Normal pull requests do not access production data, paid-provider credentials, or private Binance APIs.

## 14. Branch and Pull Request Validation

Every pull request:

- identifies one Master Task and exact detailed card IDs;
- proves hard dependencies are verified;
- passes the selected task’s required checks;
- includes migration, compatibility, rollback, or forward-fix notes where applicable;
- includes test and scan evidence;
- updates task status, documentation, and generated artifacts;
- avoids unrelated scope;
- receives no production secret;
- cannot auto-deploy database changes before migration validation;
- cannot mark a Master Task verified solely from documentation or coverage.

## 15. Free-Cloud Demo Gate — M028

The demo is accepted when:

- M001–M027 required gates are verified;
- authentication and workspace isolation work;
- no service-role or provider secret is in the browser;
- API and frontend health/smoke checks pass;
- sample/delayed/simulation data is clearly labeled;
- the one-shot cycle works with fake and approved bounded provider profiles;
- deployment revision, migration head, CORS, CSP, HTTPS, and route fallback are correct;
- Render cold start does not stop scheduled research;
- export/reset/restore procedures work;
- no live/private exchange capability exists.

## 16. Paper Experiment Gate — M029

Before starting the formal experiment:

- M028 is verified;
- all required domain, migration, RLS, Auth, idempotency, and financial-invariant tests pass;
- Binance freshness and gap repair work;
- Gemini failures and budgets degrade safely;
- risk limits and halts are proven;
- ledger reconstruction and reconciliation pass;
- export and restore are current;
- monitoring, status, incidents, and runbooks are available;
- configuration and behavior-set hashes are frozen;
- owner approval and planned end state are recorded;
- live trading and private credentials remain disabled.

## 17. Staging Gate — M035

Staging requires:

- completed experiment and post-experiment decision;
- verified M030–M034 evidence;
- separate database, Auth, Gemini, storage, domains, and deployment credentials;
- immutable production artifacts;
- synthetic data;
- migration rehearsal and compatibility evidence;
- restore, rollback/forward-fix, E2E, accessibility, load, failure, security, privacy, content, and runbook validation;
- protected access and bounded costs.

## 18. Production Research Gate — M036

Production research begins only after:

- M035 is verified;
- protected CI/CD and manual approval are active;
- controlled migration, smoke, and reconciliation checks pass;
- Auth, RLS, secrets, backups, restore, incident response, privacy, support, SLO, cost, capacity, and rollback evidence is current;
- release artifacts map to one commit, migration head, dependency set, and configuration set;
- user-facing limitations and data policies are published;
- live trading remains disabled.

## 19. Test Evidence

Each task/release records as applicable:

- Master Task and detailed task IDs;
- commit SHA and source revision;
- environment and configuration hashes;
- commands executed and result summary;
- test inventory and coverage;
- invariant and failure-path evidence;
- migration revision;
- OpenAPI/schema/type hashes;
- security/privacy/accessibility scan results;
- frontend/backend artifact hashes;
- provider smoke result when run;
- export/restore/recovery evidence;
- known flaky tests with issue, owner, reason, and expiry;
- exceptions, limitations, and unresolved risks.

## 20. Related Documents

- `/AGENTS.md`
- `/TASKS.md`
- `IMPLEMENTATION_EXECUTION_PLAN.md`
- `LOCAL_DEVELOPMENT.md`
- `TESTING.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `PRODUCTION_DEVELOPMENT.md`
- `SECURITY.md`
- `/LOCAL_AND_PRODUCTION_TASKS.md`
