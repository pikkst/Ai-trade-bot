# Roadmap

Last reviewed: 2026-07-31
Status: Product evolution plan; later phases require explicit owner approval

## Roadmap Principles

- Safety gates are more important than calendar dates.
- A later phase cannot weaken invariants proven in an earlier phase.
- Google Gemini remains advisory.
- Live trading is not part of MVP and is never enabled by completing documentation alone.
- Every promotion requires evidence, audit, tests, security review, and an owner decision.

## Phase 0 — Documentation and Governance

### Objective

Create a coherent implementation specification and AI-coding workflow.

### Deliverables

- authoritative product requirements;
- system architecture and ADRs;
- AI coding-agent rules;
- Gemini integration and AI guardrails;
- backend, API, and database specifications;
- market data, strategy, risk, portfolio, paper execution, and backtesting specifications;
- security, testing, deployment, and observability baselines;
- detailed task cards with acceptance criteria and definition of done;
- documentation audit and cross-reference checks.

### Exit Gate

- no material contradiction between documents;
- README inventory matches real files;
- Gemini is the only required cloud AI provider for MVP;
- MVP scope and prohibited features are consistent everywhere;
- implementation may begin from `T1.1` without making hidden architecture decisions.

## Phase 1 — Engineering Foundation

### Objective

Create a secure, typed, testable runtime foundation.

### Deliverables

- Python 3.12 backend structure;
- FastAPI application;
- PostgreSQL and Redis integration;
- Alembic migrations;
- ARQ worker and scheduler;
- settings validation;
- structured logging and correlation IDs;
- authentication and role authorization;
- CI quality and security gates;
- Docker Compose development environment.

### Exit Gate

- foundation P0 tasks pass;
- migration and startup tests pass;
- no secret required for normal CI;
- no live-trading path exists.

## Phase 2 — Market Research Core

### Objective

Build reliable market-data and deterministic analysis foundations.

### Deliverables

- Binance Spot public REST adapter;
- Binance public WebSocket streams;
- symbol filters and precision metadata;
- finalized OHLCV ingestion;
- data-quality detection and gap repair;
- immutable market snapshots;
- versioned feature calculations;
- audit lineage and operational metrics.

### Exit Gate

- representative historical backfill succeeds;
- duplicate and gap tests pass;
- stale data blocks downstream decisions;
- snapshots and feature hashes are reproducible.

## Phase 3 — Google Gemini Analysis

### Objective

Add bounded, structured, explainable AI analysis without execution authority.

### Deliverables

- provider-independent `LLMProvider` protocol;
- deterministic fake provider;
- Google Gemini adapter using the official SDK;
- structured report schema;
- prompt and schema versioning;
- grounding and unsupported-claim validation;
- budget reservation and cost tracking;
- provider failure, refusal, safety-block, and rate-limit handling;
- Gemini evaluation dataset and reports.

### Exit Gate

- Gemini output cannot bypass deterministic controls;
- invalid or unsafe output always produces safe degradation;
- schema-valid and grounding metrics are measured;
- CI uses fake provider;
- Gemini key is never committed or logged.

## Phase 4 — Strategy, Risk, and Portfolio Core

### Objective

Implement deterministic decision and accounting boundaries.

### Deliverables

- HOLD-only smoke strategy;
- BTC/EUR baseline trend strategy;
- immutable strategy versions;
- deterministic risk engine;
- EUR 20 research risk profile;
- append-only double-entry ledger;
- reconciled portfolio projections;
- portfolio and workspace halt controls.

### Exit Gate

- all actionable intents pass risk;
- risk failures fail closed;
- ledger property tests pass;
- reconciliation mismatch halts activity;
- AI has no position-sizing or order authority.

## Phase 5 — Paper Trading

### Objective

Run realistic internal simulated execution.

### Deliverables

- market and limit paper orders;
- cancellation and partial fills;
- fee, spread, slippage, precision, and minimum-notional models;
- idempotent order/fill workflow;
- atomic fill and ledger posting;
- paper portfolio API and UI;
- reconciliation jobs and alerts.

### Exit Gate

- no duplicate order, fill, or ledger entry under replay/restart tests;
- fill quantity never exceeds approval;
- fees and slippage cannot be silently disabled;
- critical E2E paper-trading flows pass.

## Phase 6 — Backtesting and Evaluation

### Objective

Validate strategies and execution assumptions through reproducible historical replay.

### Deliverables

- event-driven backtest engine;
- shared strategy, risk, execution, and portfolio contracts;
- cash and buy-and-hold benchmarks;
- performance and risk metrics;
- reproducibility metadata;
- walk-forward evaluation as a P1 enhancement;
- report exports and comparison UI.

### Exit Gate

- look-ahead prevention tests pass;
- identical runs are reproducible;
- fee and slippage assumptions are explicit;
- no profitability claim is made solely from optimized in-sample results.

## Phase 7 — Observability and User Interface

### Objective

Make the system operable, auditable, and understandable.

### Deliverables

- React and TypeScript UI;
- workspace and experiment views;
- market and Gemini analysis views;
- strategy/risk lineage;
- paper portfolio and backtest reports;
- audit timeline;
- Prometheus metrics;
- Grafana dashboards and alerts;
- operational runbooks.

### Exit Gate

- simulation and halt states are visually unmistakable;
- critical alerts have valid runbooks;
- users can trace a decision end to end;
- primary workflows meet accessibility requirements.

## Phase 8 — Controlled 30-Day Paper Experiment

### Objective

Evaluate the complete system under a frozen configuration using EUR 20 virtual capital.

### Configuration

- BTC/EUR primary symbol;
- no leverage or shorting;
- maximum position 25%;
- maximum order EUR 5 equivalent;
- daily drawdown halt 5%;
- total drawdown halt 15%;
- one open order maximum;
- fees and slippage enabled;
- cash and buy-and-hold benchmarks;
- real Gemini analysis within approved budget;
- human/owner oversight.

### Deliverables

- preflight report;
- frozen experiment configuration;
- continuous data-quality, AI, risk, and portfolio monitoring;
- incident and halt records;
- final experiment report;
- explicit recommendation to stop, repeat paper testing, or consider Binance sandbox design.

### Exit Gate

- zero unresolved reconciliation mismatch;
- zero duplicate financial side effect;
- complete decision lineage;
- final report produced without manual database repair;
- owner reviews all safety and quality evidence.

Profit is not an exit criterion.

## Phase 9 — Binance Test Environment Design and Validation

### Objective

Validate private API order lifecycle using a Binance-provided test or demo environment where currently supported.

### Preconditions

- Phase 8 complete;
- separate private API and credential threat model;
- exact current Binance test-environment capability verified against official documentation;
- restricted environment-specific credentials;
- no withdrawal permission;
- complete reconciliation design;
- explicit owner approval.

### Deliverables

- private exchange adapter contract;
- signed-request handling;
- clock and receive-window controls;
- order, fill, balance, and open-order reconciliation;
- credential rotation runbook;
- sandbox-specific alerts and incident procedures.

### Exit Gate

- private API tests and reconciliation pass;
- credential handling audit passes;
- no live capital is used.

## Phase 10 — Tiny Live Experiment Assessment

This phase is not approved by the roadmap alone.

Before any real-capital experiment, create a separate milestone and owner decision covering:

- current legal and regulatory review;
- Binance availability and terms for the user's jurisdiction;
- production security assessment;
- independent code and accounting review;
- explicit real-money loss limits;
- manual approval flow;
- restricted credentials with no withdrawals;
- immediate kill switch;
- operational coverage and incident response;
- evidence that extended paper and sandbox testing justify the risk.

The possible EUR 20 real-capital test is a future hypothesis, not a promised feature.

## Phase 11 — Productization

Possible future scope:

- multi-user and multi-tenant isolation;
- additional exchanges behind audited adapters;
- billing and subscription management;
- stronger reporting and experiment comparison;
- optional local models behind the provider protocol;
- managed deployment;
- compliance controls;
- enterprise audit and retention policies.

Public SaaS requires separate product, security, privacy, legal, support, and operational plans.

## Deferred Ideas

The following are intentionally deferred until evidence exists:

- multi-agent debate orchestration;
- news and social-data ingestion;
- whale or on-chain analysis;
- multi-exchange execution;
- automated strategy search;
- self-learning or self-modifying strategies;
- futures, leverage, margin, options, shorting, market making, or arbitrage.

## Roadmap Change Control

A roadmap change must:

1. identify the business or engineering reason;
2. state security and financial-risk impact;
3. update product requirements and tasks;
4. add or update an ADR when architectural;
5. preserve current safety invariants;
6. receive explicit owner approval for live, leveraged, private-exchange, or customer-facing scope.
