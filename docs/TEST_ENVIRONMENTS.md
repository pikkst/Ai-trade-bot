# Test Environments and Validation Strategy

Last reviewed: 2026-07-31
Status: Authoritative test-environment specification

## 1. Purpose

Define how code moves from isolated tests to a public demo, a controlled paper experiment, and later production development without mixing credentials, data, or risk assumptions.

## 2. Environment Matrix

| Environment | Database | Providers | Purpose | Persistent |
|---|---|---|---|---|
| Unit | none or in-memory domain fakes | all fake | pure logic | no |
| Integration | ephemeral local PostgreSQL/Supabase | fake Binance and Gemini | persistence and transactions | no |
| Contract | isolated database | recorded public responses or SDK mocks | adapter compatibility | no |
| E2E local | local Supabase | fake by default | browser-to-ledger workflows | resettable |
| Cloud demo | dedicated Supabase project | Binance REST, fake or bounded Gemini | public demonstration | yes |
| Paper experiment | dedicated Supabase project | Binance REST and bounded Gemini | formal 30-day test | yes |
| Staging | separate managed project | production-like providers with test controls | release validation | yes |
| Production | separate managed project | approved production providers | future customer-facing operation | yes |

No environment may share database credentials, service-role keys, user pools, or Gemini keys with another environment.

## 3. Test Pyramid

### Unit Tests

Cover:

- value objects;
- indicator formulas;
- strategy decisions;
- risk limits;
- order state machine;
- fee and slippage formulas;
- ledger balancing;
- P&L and drawdown;
- schema validation;
- error mapping.

Unit tests must be deterministic and fast.

### Integration Tests

Cover:

- SQLAlchemy mappings;
- migrations;
- constraints and indexes;
- transaction rollback;
- idempotency;
- concurrent lease acquisition;
- atomic fill and ledger posting;
- Supabase Auth JWT verification where applicable;
- RLS and view permissions.

### Contract Tests

Cover:

- Binance REST response mapping;
- Gemini SDK response and error mapping;
- Supabase/PostgREST behavior used by the frontend;
- Cloudflare build assumptions;
- Render health and startup contract.

Contract fixtures must record source date and schema assumptions without containing secrets.

### End-to-End Tests

Minimum flows:

1. authenticate owner;
2. create or load workspace;
3. ingest finalized candles;
4. run analysis with fake Gemini;
5. create strategy intent;
6. apply risk decision;
7. create and fill paper order;
8. post ledger entries;
9. reconcile portfolio;
10. display decision lineage in UI.

Failure E2E flows:

- stale data;
- invalid Gemini schema;
- risk rejection;
- drawdown halt;
- duplicate research cycle;
- reconciliation mismatch;
- unauthorized command.

## 4. Deterministic Fixtures

The repository must include versioned fixtures for:

- Binance symbol metadata;
- normal and malformed candles;
- gaps and duplicate events;
- bullish, bearish, sideways, and insufficient-history feature sets;
- valid and invalid Gemini reports;
- fee, spread, slippage, and precision cases;
- risk boundary cases;
- ledger transactions and reversals.

Fixture changes require review because they may alter expected behavior.

## 5. Test Clocks and Randomness

- all time-dependent code depends on a project-owned clock;
- tests freeze or advance time explicitly;
- random behavior uses an injected seeded generator;
- production timestamps are timezone-aware UTC;
- no test depends on the current wall clock unless explicitly marked as a smoke test.

## 6. Database Test Policy

CI must prove:

- migrations apply from an empty database;
- migrations reach the expected head revision;
- seed data loads successfully;
- constraints reject invalid states;
- ledger records are append-only;
- RLS policies prevent cross-user and unauthorized access;
- read-only views expose only approved fields;
- schema drift is detected.

Destructive downgrade tests are required only where a downgrade is explicitly supported. Forward-fix migration strategy is preferred.

## 7. Provider Test Policy

### Gemini

Normal CI uses the deterministic fake provider. SDK-boundary tests use mocks or recorded non-sensitive response structures.

A manually triggered Gemini smoke workflow may run only when:

- a protected secret is configured;
- a strict request and token budget is set;
- no pull request from an untrusted fork can access the secret;
- results are marked non-deterministic;
- failure does not invalidate unrelated deterministic tests.

### Binance

Normal CI uses fixtures and fake adapters. A scheduled public REST smoke test may verify server time, exchange metadata, and a bounded candle request. It must not use private credentials.

## 8. Frontend Testing

Required layers:

- component tests;
- route and authorization tests;
- generated API type checks;
- accessibility tests for primary flows;
- E2E browser tests;
- production build verification;
- environment-variable allowlist test;
- source-map and bundle inspection for accidental secrets.

The UI must clearly identify local, demo, paper, staging, and future production modes.

## 9. Security Testing

Required checks:

- secret scanning;
- dependency vulnerability review;
- Python static security analysis;
- Semgrep rules;
- frontend dependency audit;
- container and filesystem scan where containers exist;
- authentication and authorization abuse tests;
- RLS policy tests;
- prompt injection fixtures;
- log redaction tests;
- CORS and security-header tests;
- service-role key absence from frontend bundles.

## 10. Performance Testing

Before the 30-day experiment:

- one research cycle completes within the GitHub Actions timeout budget;
- API read endpoints meet documented development targets;
- database indexes support common reads;
- backtests enforce bounded data ranges and resource limits;
- concurrent duplicate cycles resolve through leases and idempotency.

Before production development promotion:

- load tests use realistic read/write ratios;
- slow query analysis is performed;
- connection pool behavior is measured;
- rate-limit and provider-degradation tests are run;
- frontend performance budgets are defined.

## 11. Reliability and Recovery Testing

Test:

- interrupted research cycle restart;
- duplicate GitHub Actions delivery;
- Render cold start;
- temporary Supabase unavailability;
- Gemini quota exhaustion;
- Binance timeout;
- partial database transaction failure;
- export and restore;
- corrupted projection rebuilt from ledger;
- experiment halt and safe resume policy.

## 12. CI Workflows

Recommended workflows:

- `quality.yml` — format, lint, types, unit tests;
- `integration.yml` — local Supabase/PostgreSQL, migrations, integration tests;
- `frontend.yml` — frontend lint, type, component, E2E, build;
- `security.yml` — secret, dependency, static, and container scans;
- `docs.yml` — links, inventory, generated artifacts, task format;
- `provider-smoke.yml` — manually triggered or scheduled bounded public checks;
- `research-cycle.yml` — hourly cloud experiment execution;
- `deploy-demo.yml` — demo deployment after required checks;
- `deploy-staging.yml` — future protected staging deployment;
- `deploy-production.yml` — future manual production promotion.

## 13. Branch and Pull Request Validation

Every pull request must:

- identify task IDs;
- pass required checks;
- include migration and rollback notes where applicable;
- include test evidence;
- update documentation;
- avoid unrelated refactors;
- not receive production secrets;
- not auto-deploy database changes before migration validation.

## 14. Demo Acceptance Gate

The cloud demo is accepted when:

- authentication works;
- no service-role secret is in the browser;
- API and frontend health checks pass;
- sample data is clearly marked;
- one-shot research cycle works with fake Gemini;
- real Gemini can be enabled only by protected configuration;
- all displayed trades are labeled simulated;
- export and reset procedures work.

## 15. Paper Experiment Acceptance Gate

Before starting the formal 30-day experiment:

- P0 domain tests pass;
- migration and RLS tests pass;
- research cycle is idempotent;
- Binance data freshness checks work;
- Gemini failure safely degrades;
- risk limits and halts are proven;
- ledger reconstruction and reconciliation pass;
- backup/export and restore are tested;
- monitoring and daily status report are available;
- configuration is frozen and hashed.

## 16. Production Development Acceptance Gate

Moving beyond the demo does not mean enabling live trading. Production development begins only after:

- the demo and paper experiment are reviewed;
- a staging environment exists;
- production architecture and threat model are approved;
- provider costs and quotas are budgeted;
- managed backups and restore objectives are defined;
- CI/CD uses protected environments and manual approval;
- legal and privacy requirements are reviewed;
- operational ownership and incident response are defined.

## 17. Test Evidence

Each release stores:

- commit SHA;
- test summary;
- coverage report;
- migration revision;
- generated OpenAPI hash;
- security scan results;
- frontend build artifact hash;
- provider smoke result when run;
- known flaky tests and approved exceptions;
- unresolved risks.

## 18. Related Documents

- `LOCAL_DEVELOPMENT.md`
- `TESTING.md`
- `FREE_CLOUD_ARCHITECTURE.md`
- `PRODUCTION_DEVELOPMENT.md`
- `SECURITY.md`
- `/LOCAL_AND_PRODUCTION_TASKS.md`
