# Contributing

Last reviewed: 2026-08-01  
Status: Contributor workflow governed by `TASKS.md` Master Tasks

## 1. Before You Start

1. Read `AGENTS.md`.
2. Read `docs/IMPLEMENTATION_EXECUTION_PLAN.md`.
3. Select one Master Task (`M001`–`M036`) from `TASKS.md` whose hard dependencies are `[x] VERIFIED`.
4. Select the exact detailed task cards mapped by that Master Task.
5. Read every referenced specification and inspect current source, migrations, tests, and generated artifacts.
6. Record assumptions, scope exclusions, invariants, failure cases, security/privacy impact, environment impact, and verification commands.
7. Do not begin when the task conflicts with security, product scope, financial integrity, or an accepted ADR.

`TASKS.md` is the only implementation-order authority. Supplemental task files contain detailed acceptance criteria but do not create independent implementation entry points.

## 2. Branching

Use a focused branch named from the Master Task and purpose, for example:

```text
feature/M007-binance-rest-ingestion
fix/M011-prevent-duplicate-paper-fill
chore/M002-baseline-quality-ci
```

Do not combine unrelated refactors, dependency upgrades, architecture changes, and feature work.

## 3. Development Rules

- Follow the modular-monolith boundaries in `docs/ARCHITECTURE.md`.
- Keep business logic out of FastAPI routes, CLI parsing, ORM models, and provider adapters.
- Use project-owned protocols for Binance, Gemini, persistence, clocks, and scheduling boundaries.
- Use `Decimal` for financial values.
- Use timezone-aware UTC timestamps internally.
- Add deterministic idempotency for repeatable side effects.
- Perform network calls outside database transactions.
- Add tests with the implementation.
- Update documentation and generated artifacts in the same change when behavior or contracts change.
- Never weaken typing, validation, Auth, RLS, risk, ledger, reconciliation, backup, recovery, or AI safety controls to make tests pass.
- Do not introduce deferred infrastructure from historical task cards without measured need and an approved ADR.

## 4. Active and Deferred Infrastructure

Active MVP architecture:

- FastAPI plus a one-shot research-cycle CLI;
- Supabase PostgreSQL and Auth;
- Binance Spot public REST and finalized candles;
- Gemini through the official `google-genai` SDK;
- React/TypeScript/Vite;
- GitHub Actions best-effort scheduling;
- Cloudflare Pages and Render Free for the initial cloud profile.

Deferred unless separately approved:

- Redis and ARQ;
- persistent workers;
- Binance WebSocket ingestion;
- hosted Prometheus/Grafana;
- Kubernetes;
- Binance test/private credentials;
- live trading.

## 5. Google Gemini Changes

A Gemini-related contribution must:

- use the official `google-genai` SDK inside the Gemini infrastructure adapter;
- keep provider SDK types out of domain and API models;
- use project-owned structured schemas;
- send minimum required structured evidence only;
- include authentication, timeout, cancellation, rate-limit, safety-block, refusal, empty, malformed, invalid-schema, grounding, unsupported-claim, injection, stale-source, and budget tests as applicable;
- use the fake provider in normal CI;
- record provider configuration, model identifier, prompt, schema, safety, validation, usage, cost, retry, fallback, and evidence lineage;
- never give Gemini exchange, shell, database, network-search, code-execution, order, position-sizing, risk-policy, experiment, release, or deployment authority.

## 6. Database Changes

- Create a new additive migration.
- Never edit an already-applied migration.
- Add constraints and indexes where invariants require them.
- Test upgrade from an empty database and every supported prior revision affected by the change.
- Test RLS, Auth claim mapping, browser direct-write denial, and workspace isolation.
- Document compatibility, migration rehearsal, rollback or forward-fix implications.
- Keep ledger and audit records append-only.
- Treat a backup as valid only after isolated restore, migration verification, ledger rebuild, and reconciliation.

## 7. Testing Before Pull Request

Run the repository commands required by the selected Master Task for:

- formatting;
- Ruff linting;
- MyPy strict;
- unit and property tests;
- integration, migration, RLS, Auth, and transaction tests;
- provider and API contract tests;
- frontend lint, type check, component, accessibility, visual, E2E, and production build when affected;
- Bandit, Semgrep, dependency, secret, and artifact scans;
- export, restore, recovery, resilience, or rollback drills when affected;
- documentation, link, task-ID, OpenAPI, schema, and generated-artifact consistency.

Do not claim a command passed unless it was executed and its result recorded.

For the M002 baseline, run `make quality` on Unix-like systems or `.\tasks.ps1 quality` on Windows. Run the separate `security-test` and `frontend-audit` commands before requesting review. Dependency locks are authoritative installation inputs; regenerate them only with the pinned Python/Node toolchains and verify drift with `lock-check`.

## 8. Pull Request Evidence

Every pull request should include:

- Master Task ID and detailed task-card IDs;
- dependency verification;
- problem statement and solution summary;
- scope exclusions;
- architecture and ADR impact;
- security, privacy, and financial-integrity impact;
- Gemini impact where relevant;
- database, migration, RLS, and data-retention impact;
- API/schema/event compatibility impact;
- environment and deployment impact;
- tests and commands executed with results;
- coverage and invariant evidence where required;
- documentation and generated-artifact changes;
- metrics, alerts, runbooks, or support impact;
- rollback or forward-fix plan;
- known limitations and follow-up IDs.

## 9. Review Checklist

Reviewers verify:

- the selected Master Task was eligible to start;
- every mandatory detailed acceptance criterion is addressed;
- architecture boundaries are preserved;
- no hidden live-trading, private Binance, leverage, derivatives, shorting, custody, or withdrawal scope exists;
- deterministic strategy and risk behavior remains non-bypassable;
- Gemini remains advisory;
- decimal and UTC rules are followed;
- idempotency, concurrency, transaction, and restart behavior are safe;
- ledger conservation, reconstruction, and reconciliation hold;
- authorization, RLS, recent-authentication, and secret handling are correct;
- failure paths are tested;
- accessibility and safety-content semantics are preserved;
- documentation and generated contracts are current;
- task status does not claim `VERIFIED` without evidence.

## 10. Commit Guidance

Use clear imperative commit messages, for example:

```text
feat: add finalized candle ingestion
fix: prevent duplicate paper fills after retry
docs: synchronize Gemini validation contract
test: cover drawdown halt boundaries
```

Commits must remain reviewable and must not include secrets, production data, local databases, provider payloads, unapproved screenshots, or unrelated artifacts.

## 11. Prohibited Contributions Without a Separate Approved Milestone

- live trading;
- private Binance order placement or Binance test activation;
- withdrawals, custody, leverage, margin, futures, options, or shorting;
- weakening risk limits, halt controls, Auth, RLS, ledger, reconciliation, backup, recovery, or release gates;
- mutable ledger balances replacing append-only evidence;
- arbitrary browser prompts sent to Gemini;
- Gemini side-effect tools;
- automatic provider/model/prompt/strategy/configuration activation;
- editing applied migrations;
- reusing the Eventnexus Supabase project;
- automatic paid-plan purchase, resource scaling, or budget increase;
- mandatory Redis/ARQ/WebSocket/hosted metrics without measured need, ADR, migration, tests, and owner approval;
- changing the official product identity or introducing promotional financial claims outside approved governance.

## 12. Definition of Verified

A contribution is complete only when:

- every mandatory acceptance criterion is met;
- all required tests, scans, builds, and drills pass;
- migrations and compatibility are safe;
- logging, metrics, audit, and runbooks are adequate;
- documentation, task evidence, generated artifacts, and changelog are updated where required;
- no secret or production data is present;
- no unresolved release-blocking finding is introduced;
- the final commit or pull request is fetched and inspected;
- the corresponding Master Task evidence is recorded;
- the repository remains consistent with `AGENTS.md` and `docs/IMPLEMENTATION_EXECUTION_PLAN.md`.

Only `VERIFIED` is complete. An implementation, documentation update, passing coverage percentage, or successful demo alone is insufficient.

## 13. Security Reporting

Do not open a public issue containing a credential, exploitable secret, personal data, or private provider payload. Revoke exposed credentials immediately, preserve evidence safely, activate the incident process, and contact the repository owner through a private channel.
