# Local Development, Testing, and Production Tasks

Last reviewed: 2026-07-31
Status: Active supplemental backlog

This file extends `TASKS.md` and `CLOUD_MVP_TASKS.md`. It defines the work required to build a reproducible local environment, validate the demo through layered tests, and continue into production-grade research-service development after the MVP.

---

# Epic L1 — Local Development Foundation

## [ ] L1.1 — Create Cross-Platform Local Bootstrap Command

**Priority:** P0

### Description

Create a bootstrap command that verifies required tools, installs locked dependencies, creates ignored local environment files, and explains missing prerequisites.

### User Story

As a developer, I want one reliable bootstrap entry point, so that a clean checkout can become a working development environment without undocumented manual steps.

### Acceptance Criteria

- The command verifies Python 3.12, Node.js LTS, Docker Compose v2, Git, and Supabase CLI.
- Python and frontend dependencies install from committed lock files.
- Missing tools produce actionable errors.
- Safe local environment files are created from committed examples without overwriting existing values.
- The command works on Windows PowerShell and at least one Unix-like shell.
- No paid-provider credential is required.
- Re-running the command is safe and idempotent.

### Definition of Done

- Bootstrap succeeds from a clean checkout on a documented supported environment.
- Windows-specific setup notes are verified.
- Failure-path tests or script checks exist.
- `docs/LOCAL_DEVELOPMENT.md` contains the exact command.

### Dependencies

- T1.1
- T1.2

### References

- `docs/LOCAL_DEVELOPMENT.md`
- `AGENTS.md`

---

## [ ] L1.2 — Implement Local Supabase Development Stack

**Priority:** P0

### Description

Configure Supabase CLI for local PostgreSQL, Auth, Data API, migrations, and deterministic seed data.

### User Story

As a backend developer, I want production-relevant database and authentication behavior locally, so that schema, Auth, and RLS changes can be tested before cloud deployment.

### Acceptance Criteria

- `supabase/config.toml` exists.
- Local Supabase starts and stops with documented commands.
- Migrations apply from an empty database.
- Seed data creates synthetic users, workspace, symbol metadata, candles, and a virtual portfolio.
- Local Auth supports owner and viewer test identities.
- RLS policies and read-only views can be tested locally.
- Reset removes all local state and recreates it deterministically.
- No cloud database credential is required.

### Definition of Done

- `supabase start`, migration, seed, reset, and stop workflows are verified.
- Integration tests connect to the local stack.
- Database schema documentation is synchronized.
- No secret is committed.

### Dependencies

- L1.1
- C1

### References

- `docs/LOCAL_DEVELOPMENT.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/SECURITY.md`

---

## [ ] L1.3 — Create Stable Local Command Runner

**Priority:** P0

### Description

Add a cross-platform command interface for common backend, frontend, database, test, and quality workflows.

### User Story

As a contributor, I want stable named commands, so that documentation and AI coding agents do not depend on ad hoc shell instructions.

### Acceptance Criteria

- Commands exist for bootstrap, local-up, local-down, local-reset, api-dev, frontend-dev, research-cycle, format, lint, type checking, unit tests, integration tests, contract tests, E2E tests, security tests, and all checks.
- Commands return non-zero exit codes on failure.
- Commands do not expose secrets.
- Windows and Unix execution are documented.
- CI reuses the same underlying commands where practical.

### Definition of Done

- Every documented command executes.
- Command help is available.
- CI uses at least the shared quality and test commands.
- `CONTRIBUTING.md` and local-development documentation are updated.

### Dependencies

- L1.1
- L1.2

### References

- `docs/LOCAL_DEVELOPMENT.md`
- `CONTRIBUTING.md`

---

## [ ] L1.4 — Build Deterministic Local Provider Fakes

**Priority:** P0

### Description

Implement configurable fake Binance and Gemini providers for normal development, CI, and failure injection.

### User Story

As a developer, I want deterministic providers, so that application behavior can be reproduced without network access, quotas, or changing model output.

### Acceptance Criteria

- Fake Binance supports symbol metadata, finalized candles, gaps, malformed data, timeout, and rate-limit scenarios.
- Fake Gemini supports valid reports, invalid schema, timeout, refusal, safety block, empty response, and rate-limit scenarios.
- Scenario selection is explicit and safe.
- Fake-provider types satisfy the same project contracts as real adapters.
- Fixtures are versioned.
- Normal local startup defaults to fake providers.

### Definition of Done

- Contract tests pass for fake providers.
- Failure-injection examples are documented.
- No normal test calls a paid API.
- Provider behavior is reproducible across runs.

### Dependencies

- T3.1
- T5.1
- L1.1

### References

- `docs/LOCAL_DEVELOPMENT.md`
- `docs/TEST_ENVIRONMENTS.md`
- `docs/GEMINI_INTEGRATION.md`

---

## [ ] L1.5 — Create Local End-to-End Demo Seed

**Priority:** P1

### Description

Create a deterministic local dataset and workflow that demonstrates the complete simulated decision path.

### User Story

As a developer or reviewer, I want a known demo scenario, so that the system can be validated visually and functionally before cloud deployment.

### Acceptance Criteria

- Seed data includes finalized BTC/EUR candles with a documented expected feature state.
- A fake Gemini report is linked to the exact snapshot.
- Strategy and risk produce a known outcome.
- A paper order and ledger result can be generated deterministically.
- The UI displays snapshot, Gemini report, strategy, risk, order, fill, portfolio, and audit lineage.
- Re-running the demo does not duplicate financial state.

### Definition of Done

- One command resets and runs the demo.
- Expected IDs or lookup method are documented.
- E2E test validates the complete flow.
- Screenshots are optional and must not contain secrets.

### Dependencies

- L1.2
- L1.4
- T7.2
- T9.2

### References

- `docs/LOCAL_DEVELOPMENT.md`
- `docs/TEST_ENVIRONMENTS.md`

---

# Epic L2 — Test Automation and Quality Gates

## [ ] L2.1 — Build the Unit and Property Test Baseline

**Priority:** P0

### Description

Create unit and property-based test structure for calculations, state machines, risk rules, and ledger invariants.

### User Story

As the development team, I want fast deterministic domain tests, so that financial and safety regressions are detected immediately.

### Acceptance Criteria

- Unit test packages exist for every core domain.
- Hypothesis tests verify ledger conservation, non-negative balances, sizing bounds, precision, idempotency, and deterministic decisions.
- Time and randomness are injected.
- Tests do not require network or database access.
- Coverage reporting identifies untested critical branches.

### Definition of Done

- Core domain unit suite passes locally and in CI.
- Failing invariant examples are demonstrated and reverted.
- Coverage thresholds are documented and enforced for safety-critical modules.

### Dependencies

- T1.2

### References

- `docs/TESTING.md`
- `docs/TEST_ENVIRONMENTS.md`

---

## [ ] L2.2 — Build Supabase Migration, RLS, and Integration Tests

**Priority:** P0

### Description

Create automated tests for migrations, constraints, RLS policies, views, transactions, and database leases.

### User Story

As the platform owner, I want database security and integrity verified automatically, so that cloud deployment cannot expose or corrupt critical state.

### Acceptance Criteria

- A clean database upgrades to migration head.
- Seed data applies.
- Invalid financial states fail database constraints.
- RLS tests cover owner, operator, viewer, unauthenticated user, and service backend.
- Critical tables cannot be modified directly by browser roles.
- Read-only views expose only approved columns.
- Concurrent lease tests prove only one research cycle owns a logical occurrence.
- Migration drift fails CI.

### Definition of Done

- Tests run against local Supabase in CI.
- Results are included in CI artifacts or logs.
- Security and database documents match implemented policies.

### Dependencies

- L1.2
- C2

### References

- `docs/DATABASE_SCHEMA.md`
- `docs/SECURITY.md`
- `docs/TEST_ENVIRONMENTS.md`

---

## [ ] L2.3 — Build Frontend Component, Accessibility, and E2E Tests

**Priority:** P1

### Description

Create a frontend testing stack covering components, routes, authorization, accessibility, production build, and browser workflows.

### User Story

As a user, I want the interface to be reliable, accessible, and explicit about simulation state, so that I can understand and safely operate the research platform.

### Acceptance Criteria

- Component tests cover loading, success, empty, stale, halted, and error states.
- Route tests verify authentication and role access.
- Accessibility tests cover primary workflows.
- Browser E2E tests run against the local stack.
- Environment and simulation labels are asserted.
- Frontend bundle checks fail if forbidden secret names or values appear.
- Production build succeeds in CI.

### Definition of Done

- Tests run locally and in GitHub Actions.
- Critical user journeys are covered.
- Accessibility violations are resolved or explicitly documented.
- Frontend documentation is updated.

### Dependencies

- T13.1 or equivalent frontend initialization
- L1.2

### References

- `docs/TEST_ENVIRONMENTS.md`
- `docs/SECURITY.md`

---

## [ ] L2.4 — Create Provider Contract and Bounded Smoke Workflows

**Priority:** P1

### Description

Add deterministic provider contract tests and optional protected smoke workflows for current Binance public REST and Gemini API behavior.

### User Story

As the development team, I want adapter assumptions checked against current providers, so that external API changes are detected without making normal CI unreliable or expensive.

### Acceptance Criteria

- Binance and Gemini adapter contracts are tested with fixtures or mocks.
- A manually triggered Gemini smoke workflow uses protected secrets and strict budgets.
- A bounded Binance public smoke workflow uses no private key.
- Fork pull requests cannot access secrets.
- Smoke failures are reported separately from deterministic tests.
- Provider response assumptions and fixture dates are documented.

### Definition of Done

- Deterministic contract tests pass in normal CI.
- Protected smoke workflows are documented.
- Budget and security controls are verified.

### Dependencies

- L1.4
- T3.2
- T5.3

### References

- `docs/TEST_ENVIRONMENTS.md`
- `docs/BINANCE_INTEGRATION.md`
- `docs/GEMINI_INTEGRATION.md`

---

## [ ] L2.5 — Add Documentation and Task Consistency CI

**Priority:** P0

### Description

Create automated checks for Markdown links, README inventory, environment-variable documentation, generated artifacts, and task-card structure.

### User Story

As the project owner, I want documentation drift detected in CI, so that AI coding agents and developers always work from accurate instructions.

### Acceptance Criteria

- Internal Markdown links are checked.
- README documentation inventory is compared with authoritative files.
- `.env.example` variables are compared with typed settings after implementation.
- Detailed task cards require ID, priority, description, user story, acceptance criteria, Definition of Done, dependencies, and references.
- Generated OpenAPI and other generated docs are checked for staleness when available.
- Deprecated architecture terms fail or warn according to policy.

### Definition of Done

- Documentation workflow runs on pull requests.
- Deliberate broken-link and malformed-task tests fail and are reverted.
- Audit procedure references the automated checks.

### Dependencies

- T1.4

### References

- `docs/DOCUMENTATION_AUDIT.md`
- `AGENTS.md`

---

## [ ] L2.6 — Build Export, Restore, and Recovery Tests

**Priority:** P1

### Description

Automate testable database export and restore procedures for the free cloud experiment and later environments.

### User Story

As the owner, I want verified recovery evidence, so that the experiment is not dependent on an untested provider backup assumption.

### Acceptance Criteria

- A documented command creates an encrypted or securely handled logical export.
- Restore into an isolated local or test database succeeds.
- Migration revision is verified after restore.
- Ledger reconstruction and reconciliation pass.
- Restored Auth-sensitive data is handled according to environment policy.
- Backup artifacts never enter source control.
- Failure and partial-export behavior are documented.

### Definition of Done

- A restore test is executed and recorded.
- Runbook is committed.
- Cloud experiment preflight references the latest successful test.

### Dependencies

- L1.2
- C7

### References

- `docs/TEST_ENVIRONMENTS.md`
- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/DEPLOYMENT.md`

---

# Epic P1 — Staging and Production Research Development

## [ ] P1.1 — Define Staging Environment Infrastructure

**Priority:** P1

### Description

Create a production-like but isolated staging environment for release validation after the demo.

### User Story

As the release owner, I want changes validated in an isolated production-like environment, so that migrations and deployments are rehearsed before production research users are affected.

### Acceptance Criteria

- Staging uses separate database, Auth, Gemini key, domains, and deployment credentials.
- Production artifacts are deployed unchanged to staging.
- Synthetic data is used.
- Migration rehearsal and E2E tests run automatically.
- Staging can be reset without production impact.
- Access is restricted.
- Costs and quotas are bounded.

### Definition of Done

- Staging deployment succeeds from CI/CD.
- Smoke, E2E, migration, and security checks pass.
- Environment inventory and ownership are documented.

### Dependencies

- C1-C7
- L2.1-L2.6

### References

- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/TEST_ENVIRONMENTS.md`

---

## [ ] P1.2 — Implement Protected Staging and Production Deployment Pipelines

**Priority:** P1

### Description

Create protected CI/CD workflows with staging deployment, manual production approval, migration control, smoke tests, and rollback evidence.

### User Story

As the project owner, I want auditable deployments, so that no workstation or unreviewed commit can modify production directly.

### Acceptance Criteria

- Required checks gate staging and production.
- Production uses a protected GitHub environment with manual approval.
- Database migrations run once in a controlled step.
- Deployment records commit SHA, migration revision, artifact hashes, and configuration versions.
- Post-deployment smoke and reconciliation checks run.
- Failed checks stop promotion.
- Rollback compatibility is documented per release.

### Definition of Done

- A staging release completes end to end.
- A simulated failed deployment proves promotion stops.
- Production workflow exists but does not enable live trading.
- Release documentation is generated.

### Dependencies

- P1.1

### References

- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/DEPLOYMENT.md`

---

## [ ] P1.3 — Upgrade Authentication and Account Security for Production Research

**Priority:** P1

### Description

Harden account authentication, authorization, session handling, recovery, and privileged operations for production research users.

### User Story

As a user, I want my account and research data protected, so that unauthorized users cannot access or mutate experiments and portfolios.

### Acceptance Criteria

- Verified identity flow is enabled.
- Session expiration and revocation are defined.
- Owner, operator, and viewer permissions are centrally enforced.
- Privileged changes require re-authentication or additional confirmation where appropriate.
- Rate limiting and abuse controls exist.
- Recovery and account-disable procedures are documented.
- Audit events cover privileged actions.
- MFA decision is documented through an ADR or security decision.

### Definition of Done

- Threat-oriented tests pass.
- Auth and RLS receive focused review.
- Security documentation reflects actual behavior.

### Dependencies

- P1.1
- T10.1

### References

- `docs/SECURITY.md`
- `docs/PRODUCTION_DEVELOPMENT.md`

---

## [ ] P1.4 — Establish Production Observability, SLOs, and Incident Routing

**Priority:** P1

### Description

Select and configure production-grade logs, error aggregation, metrics, uptime checks, alerts, SLOs, and incident ownership.

### User Story

As an operator, I want actionable production signals, so that failures are detected, diagnosed, and resolved before data integrity is affected.

### Acceptance Criteria

- Centralized logs and error aggregation are configured.
- SLOs exist for API, scheduled cycles, data freshness, AI validity, backups, and integrity.
- Alerts route to an identified owner.
- Provider quota and cost alerts exist.
- Critical alerts link to tested runbooks.
- No secrets or unbounded identifiers appear in telemetry.
- Paper and production-research states remain clearly labeled.

### Definition of Done

- Alert tests prove delivery.
- One incident exercise is completed.
- SLO dashboard and runbooks are documented.

### Dependencies

- P1.1
- C7

### References

- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/OBSERVABILITY.md`

---

## [ ] P1.5 — Establish Managed Backup, Restore, RPO, and RTO

**Priority:** P1

### Description

Configure production-suitable backups and prove recovery objectives.

### User Story

As the owner, I want measured recovery capability, so that database loss or corruption does not permanently destroy research and ledger evidence.

### Acceptance Criteria

- Automated encrypted backups are configured.
- Retention is documented.
- Independent export or off-provider copy is evaluated.
- RPO and RTO targets are approved.
- Restore is tested into isolation.
- Ledger reconciliation passes after restore.
- Backup failure alerts exist.

### Definition of Done

- Successful restore evidence is recorded.
- Recovery runbook is tested.
- Production launch gate references the latest restore result.

### Dependencies

- P1.1
- L2.6

### References

- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/DEPLOYMENT.md`

---

## [ ] P1.6 — Perform Production Research Security and Privacy Review

**Priority:** P1

### Description

Complete a focused security, privacy, data-retention, provider, and operational review before serving real users.

### User Story

As the product owner, I want material security and privacy risks identified before launch, so that the research service does not expose users or the project to avoidable harm.

### Acceptance Criteria

- Threat model is updated for production topology.
- Auth, RLS, secrets, CI/CD, dependencies, and incident response are reviewed.
- Personal-data inventory and retention are documented.
- Gemini data sent externally is minimized and documented.
- User export and deletion requirements are assessed.
- Critical and high findings are resolved or explicitly accepted with rationale and expiry.
- Live trading remains excluded.

### Definition of Done

- Review report is committed or stored securely with a repository reference.
- Required fixes are tracked as detailed tasks.
- Production research launch approval is recorded.

### Dependencies

- P1.2
- P1.3
- P1.4
- P1.5

### References

- `docs/SECURITY.md`
- `docs/PRODUCTION_DEVELOPMENT.md`

---

## [ ] P1.7 — Launch the Production Research Service

**Priority:** P2

### Description

Promote the tested research application to a production environment for authenticated research and paper-trading use only.

### User Story

As an approved user, I want a reliable production research service, so that I can access market analysis, paper portfolios, and backtests without depending on a developer environment.

### Acceptance Criteria

- All production launch gates are satisfied.
- Custom domains and TLS are active.
- Production database and Auth are isolated.
- Backups, alerts, and runbooks are active.
- User-facing disclaimer and privacy information are available.
- All trading is clearly simulated.
- Private Binance API and live order paths are absent.
- Release metadata and known limitations are published.

### Definition of Done

- Post-deploy smoke and reconciliation checks pass.
- Owner approves the launch.
- Monitoring confirms stable initial operation.
- A post-launch review date is scheduled.

### Dependencies

- P1.6

### References

- `docs/PRODUCTION_DEVELOPMENT.md`
- `ROADMAP.md`

---

# Epic P2 — Post-Launch Improvement

## [ ] P2.1 — Conduct Post-Launch Reliability and Cost Review

**Priority:** P2

### Description

Review measured production research usage, reliability, provider behavior, and costs after an agreed operating period.

### User Story

As the product owner, I want evidence-based infrastructure decisions, so that the platform scales only where real usage justifies cost and complexity.

### Acceptance Criteria

- API, database, scheduled-cycle, Gemini, storage, and frontend usage are measured.
- Reliability and incident data are reviewed.
- Cost per experiment or active user is estimated.
- Free-tier dependencies and risks are reassessed.
- Recommendations identify keep, optimize, upgrade, or replace decisions.
- Any Redis/ARQ, persistent worker, WebSocket, or managed observability proposal includes measured justification and an ADR.

### Definition of Done

- Review report is produced.
- Approved changes become detailed tasks.
- Roadmap and cost assumptions are updated.

### Dependencies

- P1.7

### References

- `docs/PRODUCTION_DEVELOPMENT.md`
- `docs/TECH_STACK.md`
- `docs/ADR.md`
