# Security

Last reviewed: 2026-07-31
Status: Authoritative MVP security baseline

## 1. Security Objectives

- Prevent unauthorized state changes.
- Prevent secret disclosure.
- Prevent Google Gemini from gaining execution authority.
- Prevent replayed or duplicated financial side effects.
- Preserve integrity of market data, decisions, orders, fills, and ledger entries.
- Detect and halt on reconciliation or integrity failures.
- Keep live trading and private Binance execution outside MVP scope.

## 2. Assets

High-value assets include:

- Gemini API keys and billing project access;
- JWT signing secrets and authentication credentials;
- workspace and role assignments;
- frozen experiment configurations;
- market data and quality state;
- prompts, schemas, Gemini reports, and decision lineage;
- strategy and risk-policy versions;
- paper portfolios, orders, fills, and ledger entries;
- audit evidence;
- CI tokens, container registries, and deployment credentials.

## 3. Trust Boundaries

- browser to API;
- API and workers to PostgreSQL;
- API and workers to Redis;
- worker to Binance public APIs;
- worker to Google Gemini API;
- CI to GitHub and artifact registries;
- operator to configuration and halt controls.

All external input is untrusted until validated.

## 4. Threat Model

### Spoofing

Threats: stolen access token, forged worker identity, leaked Gemini key.

Controls: strong authentication, short-lived tokens, environment-separated secrets, TLS, least privilege, key rotation, server-side authorization.

### Tampering

Threats: altered candles, changed prompt version, mutable ledger, modified risk policy during experiment.

Controls: immutable finalized candles, hashes, versioned configuration, append-only ledger/audit, database constraints, frozen experiment configuration.

### Repudiation

Threats: user denies halt, configuration change, or experiment start.

Controls: immutable audit events with actor, correlation ID, entity, timestamp, outcome, and reason.

### Information Disclosure

Threats: secrets in logs, stack traces, prompts, API responses, metrics, or frontend bundles.

Controls: secret-aware settings, redaction filters, generic errors, safe details, no secrets in Gemini requests, no high-cardinality sensitive metric labels.

### Denial of Service

Threats: excessive backtests, analysis requests, Binance reconnect loops, Gemini quota exhaustion.

Controls: authentication rate limits, job concurrency limits, bounded ranges, timeouts, circuit breaking, budgets, backoff, queue monitoring.

### Elevation of Privilege

Threats: viewer creates orders, operator weakens risk, Gemini calls tools, compromised CI deploys unsafe code.

Controls: application-layer RBAC, owner-only policy changes, protected branches, review gates, no Gemini execution tools, least-privilege CI tokens.

## 5. Secrets Management

- Secrets come from environment variables or an approved secret manager.
- `.env` files containing real secrets are ignored and never committed.
- `.env.example` contains names and safe placeholders only.
- Secret values are excluded from object representations, logs, metrics, traces, errors, prompts, and API responses.
- Separate Gemini keys and projects are used for local, sandbox, and future production environments.
- Keys are rotated after suspected exposure, personnel changes, or according to policy.
- CI uses fake providers by default and does not require a paid Gemini key.
- Private Binance keys are prohibited in MVP.

## 6. Authentication and Authorization

- Roles: owner, operator, viewer.
- Authorization is enforced in application handlers.
- Local passwords, when implemented, use Argon2id.
- Access tokens are short-lived and signed with a rotatable secret or key pair.
- Refresh tokens must not be implemented without rotation, revocation, theft detection, and secure storage design.
- Privileged actions require recent authentication when appropriate.
- Denied privileged attempts are audited.

## 7. API Security

- Strict request schemas; reject unknown fields where appropriate.
- Bounded pagination and date ranges.
- Rate limits for login, analysis, backfill, backtest, and exports.
- CORS allowlist; no wildcard with credentials.
- Secure headers and HTTPS outside local development.
- State-changing commands use idempotency keys.
- Object ownership and workspace scope checked on every resource.
- Generic error responses with correlation ID.
- No arbitrary prompt endpoint in MVP.

## 8. Google Gemini Security

- Gemini receives only minimum structured market evidence.
- No credentials, personal data, database URLs, JWTs, or internal secrets are included.
- News or social text is untrusted data, never instructions.
- Structured output is validated independently after provider response.
- Safety block, refusal, empty output, malformed output, unsupported claims, and stale-source output are rejected.
- Gemini cannot call exchange, shell, database, network search, code execution, or risk-policy tools in MVP.
- Model and prompt changes are versioned and cannot silently alter an active experiment.
- Quota and budget exhaustion degrades to deterministic analysis or HOLD.

## 9. Financial and Trading Safety

- Live trading, withdrawals, leverage, futures, margin, and shorting are disabled and out of MVP scope.
- Strategy cannot create orders.
- Every actionable intent passes deterministic risk evaluation.
- Risk failures fail closed.
- One approved risk evaluation creates at most one paper order.
- Decimal arithmetic is mandatory.
- Fees, slippage, precision, and minimum-notional rules cannot be disabled without a new approved execution-model version.
- Reconciliation mismatch halts the portfolio or workspace.
- Ledger entries are append-only.

## 10. Database Security

- Separate least-privilege database roles for application, migration, and read-only operations where deployed.
- PostgreSQL is not publicly exposed.
- TLS is used where traffic crosses untrusted networks.
- Parameterized SQL and SQLAlchemy are required.
- Database backups are encrypted and restoration is tested before sandbox release.
- Applied migrations are immutable.
- Audit and ledger records cannot be updated or deleted through ordinary application paths.

## 11. Redis and Queue Security

- Redis is not publicly exposed.
- Authentication and TLS are used when not on a trusted local network.
- Queue payloads contain references rather than secrets.
- Jobs validate payload schema and workspace scope.
- Redis loss must not destroy authoritative state.
- Duplicate delivery is expected and handlers are idempotent.

## 12. Supply Chain Security

Required controls:

- dependency lock files;
- dependency review on pull requests;
- secret scanning;
- Bandit and Semgrep;
- frontend and Python vulnerability scanning;
- Trivy filesystem and container scanning;
- SBOM generation before sandbox release;
- pinned GitHub Actions by trusted version or commit;
- minimal, pinned container images;
- non-root containers where supported;
- protected main branch and required reviews.

No sandbox deployment proceeds with unresolved critical or high vulnerabilities unless an owner-approved, documented exception includes compensating controls and expiry.

## 13. Logging and Privacy

Never log:

- authorization headers;
- cookies;
- JWTs;
- API keys;
- passwords or password hashes;
- database URLs with credentials;
- full Gemini prompts containing sensitive content;
- unrestricted provider raw responses;
- future exchange signatures or secrets.

Audit logs contain safe business metadata, not secrets.

## 14. Prompt Injection and Untrusted Content

- Separate system instructions from evidence fields.
- Label external text as untrusted evidence.
- Do not allow external text to select tools, models, schemas, credentials, or policies.
- Validate cited evidence against supplied data.
- Test malicious instructions, encoded payloads, conflicting directions, and irrelevant text.
- A suspicious or unsupported report is rejected and cannot open a position.

## 15. Security Testing

Mandatory tests include:

- role and workspace authorization matrix;
- token expiry and invalid signature;
- secret redaction;
- idempotency replay;
- prompt injection corpus;
- Gemini malformed/safety-block/refusal paths;
- SQL and input validation cases;
- dependency and container scans;
- ledger tamper and reconciliation detection;
- halt enforcement;
- startup rejection of unsafe configuration.

## 16. Incident Response

1. Halt affected workspace and background jobs.
2. Revoke or rotate affected credentials.
3. Preserve logs, audit records, commits, and database evidence.
4. Determine scope, timeline, and data exposure.
5. Patch and add regression tests.
6. Restore from trusted state if integrity is uncertain.
7. Validate reconciliation and security gates.
8. Document root cause, impact, and preventive actions.
9. Resume only after owner approval.

## 17. Backup and Recovery

Before Binance sandbox progression:

- automated PostgreSQL backups exist;
- backups are encrypted;
- retention is documented;
- restore procedure is tested;
- restored ledger reconciliation passes;
- Redis is treated as rebuildable;
- configuration and migration revisions are recorded.

Exact RPO and RTO are set from measured deployed capability, not invented in advance.

## 18. Privacy and Compliance

The MVP should minimize personal data. Before public SaaS or third-party use, perform a legal review covering privacy, data processing, Gemini terms, consumer protection, financial-service boundaries, record retention, and applicable EU/Estonian requirements.

This document is an engineering baseline, not legal advice.

## 19. Security Release Gates

A release or sandbox promotion requires:

- no unresolved critical findings;
- no unresolved high findings without explicit time-limited exception;
- passing authentication and authorization tests;
- passing secret scan;
- passing static and dependency scans;
- passing ledger and halt safety tests;
- tested backup restoration;
- documented incident and rollback procedures;
- confirmation that live trading remains disabled.

## 20. Related Documents

- `/AGENTS.md`
- `ARCHITECTURE.md`
- `BACKEND.md`
- `API_SPECIFICATION.md`
- `DATABASE_SCHEMA.md`
- `GEMINI_INTEGRATION.md`
- `RISK_ENGINE.md`
- `TESTING.md`
- `DEPLOYMENT.md`
