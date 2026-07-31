# Contributing

Last reviewed: 2026-07-31

## 1. Before You Start

1. Select one task ID from `TASKS.md`.
2. Read `/AGENTS.md` and every document referenced by the task.
3. Confirm dependencies are complete.
4. Write down assumptions and scope exclusions.
5. Do not begin implementation when the task conflicts with security, product scope, or an accepted ADR.

## 2. Branching

Use a focused branch named from the task and purpose, for example:

```text
feature/T3.2-binance-public-adapter
fix/T7.5-drawdown-halt
chore/T1.9-ci-quality-workflow
```

Do not combine unrelated refactors, dependency upgrades, and feature work.

## 3. Development Rules

- Follow the modular-monolith boundaries in `docs/ARCHITECTURE.md`.
- Keep business logic out of FastAPI routes and infrastructure adapters.
- Use project-owned protocols for Binance, Gemini, persistence, clocks, queues, and metrics.
- Use `Decimal` for financial values.
- Use timezone-aware UTC timestamps.
- Add idempotency for repeatable side effects.
- Add tests with the implementation.
- Update documentation in the same change when behavior or contracts change.
- Never weaken risk, ledger, reconciliation, authentication, or AI safety controls to make tests pass.

## 4. Google Gemini Changes

A Gemini-related contribution must:

- use the official `google-genai` SDK inside the Gemini infrastructure adapter;
- keep provider SDK types out of domain and API models;
- use project-owned structured schemas;
- include timeout, rate-limit, safety-block, refusal, and invalid-output tests;
- use fake provider in normal CI;
- record prompt, schema, model, usage, cost, and validation lineage;
- never give Gemini order, shell, database mutation, or risk-policy tools.

## 5. Database Changes

- Create a new Alembic migration.
- Never edit an already-applied migration.
- Add constraints and indexes where invariants require them.
- Test upgrade from an empty database and the previous supported revision.
- Document migration and rollback/forward-fix implications.
- Keep ledger and audit records append-only.

## 6. Testing Before Pull Request

Run the available project commands for:

- formatting;
- Ruff linting;
- MyPy strict;
- unit and property tests;
- integration tests;
- migration tests;
- Bandit and Semgrep;
- dependency and secret scanning;
- frontend lint, type check, tests, and build when affected.

Do not claim a command passed unless it was run.

## 7. Pull Request Description

Every pull request should include:

- task/issue reference;
- problem statement;
- solution summary;
- scope exclusions;
- architecture impact;
- security and financial-risk impact;
- Gemini impact when relevant;
- database/migration impact;
- API compatibility impact;
- test evidence;
- documentation changes;
- metrics/alerts added;
- rollback or forward-fix plan;
- known limitations.

## 8. Review Checklist

Reviewers verify:

- task acceptance criteria and Definition of Done;
- architecture boundaries;
- no hidden live-trading scope;
- deterministic strategy and risk behavior;
- Gemini remains advisory;
- decimal and UTC rules;
- idempotency and concurrency;
- ledger conservation and reconciliation;
- authorization and secret handling;
- tests cover failure paths;
- docs and generated contracts are current.

## 9. Commit Guidance

Use clear imperative commit messages, for example:

```text
feat: add immutable market snapshot creation
fix: prevent duplicate paper fills after retry
docs: define Gemini evaluation contract
test: cover drawdown halt boundaries
```

Commits should be reviewable and must not include generated secrets, local databases, credentials, or unrelated artifacts.

## 10. Prohibited Contributions Without Owner Approval

- live trading;
- private Binance order placement;
- withdrawals;
- leverage, margin, futures, or shorting;
- weakening risk limits or halt controls;
- mutable ledger balances replacing the append-only ledger;
- arbitrary user prompts sent to Gemini;
- Gemini execution tools;
- replacing Google Gemini as V1 provider;
- changing core stack or accepted ADRs without a new ADR.

## 11. Definition of Done

A contribution is complete only when:

- all task acceptance criteria are met;
- tests and security checks pass;
- migrations are safe;
- logging and metrics are adequate;
- documentation and changelog are updated where required;
- no secret is present;
- no unresolved critical/P0 issue is introduced;
- the repository remains consistent with `/AGENTS.md`.

## 12. Security Reporting

Do not open a public issue containing a credential or exploitable secret. Revoke exposed credentials immediately, preserve evidence safely, and contact the repository owner through a private channel.
