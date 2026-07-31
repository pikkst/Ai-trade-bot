# The Daily Roast AI — Mission and Values

Last reviewed: 2026-07-31
Status: Authoritative mission and values specification

## 1. Mission

> Make disciplined, evidence-driven market research accessible through transparent AI, reproducible analysis, realistic simulation, and deterministic risk controls.

The mission is not to automate speculation. It is to improve the quality of market reasoning before capital is placed at risk.

## 2. Why the Product Exists

Most market tools optimize for speed, engagement, alerts, or transaction volume. The Daily Roast AI optimizes for understanding, traceability, and disciplined experimentation.

The product exists to reduce the gap between:

- raw data and useful interpretation;
- AI output and verifiable evidence;
- strategy ideas and reproducible tests;
- simulated performance and honest assumptions;
- user intent and controlled risk.

## 3. Core Values

### 3.1 Evidence Over Hype

We prefer measurable evidence to narratives, urgency, popularity, or unsupported conviction.

Required behavior:

- cite the inputs used;
- distinguish observed facts from interpretation;
- disclose missing data;
- challenge unsupported claims;
- avoid sensational wording.

### 3.2 Transparency

Users should understand how a result was produced and which assumptions affected it.

Required behavior:

- preserve decision lineage;
- expose relevant strategy, risk, feature, prompt, model, and execution versions;
- disclose simulation assumptions;
- show provider and validation failures;
- label uncertainty.

### 3.3 Explainability

A recommendation without reasoning is insufficient.

Required behavior:

- present supporting evidence;
- present contradictory evidence;
- state invalidation conditions;
- separate AI interpretation from deterministic decisions;
- provide stable reason codes for risk and system outcomes.

### 3.4 Safety Before Automation

Automation is valuable only when controls are stronger than the side effects it can create.

Required behavior:

- keep live trading outside the MVP;
- require deterministic risk evaluation;
- fail closed on uncertainty affecting integrity;
- halt on reconciliation mismatch;
- require staged progression from research to paper testing.

### 3.5 Human Control

The user remains accountable for scope, configuration, promotion, and any future real-capital decision.

Required behavior:

- make active mode and environment obvious;
- require explicit approval for high-risk transitions;
- never hide automated state changes;
- preserve manual halt capability;
- avoid manipulative urgency.

### 3.6 Reproducibility

Research should be repeatable from versioned inputs and assumptions.

Required behavior:

- use immutable snapshots;
- version prompts, schemas, strategies, risk policies, and execution models;
- record configuration hashes;
- use deterministic fakes in tests;
- document when exact model reproduction is impossible.

### 3.7 Honest Simulation

Paper trading and backtesting must not be optimized to appear more profitable than realistic execution would allow.

Required behavior:

- include fees, spread, slippage, precision, and minimum-notional rules;
- prevent look-ahead;
- resolve ambiguity conservatively;
- disclose model limitations;
- compare against meaningful benchmarks.

### 3.8 Security by Design

Security is part of product correctness.

Required behavior:

- deny browser access by default;
- isolate secrets and environments;
- use least privilege;
- test authentication, authorization, and RLS;
- avoid secrets in logs, prompts, or bundles;
- verify restore procedures.

### 3.9 Learning Through Measurement

Features and infrastructure should be added based on observed value and measured need.

Required behavior:

- define success metrics;
- run controlled experiments;
- document incidents and failures;
- review costs and operational burden;
- avoid premature scale.

### 3.10 Respect for the User

Users deserve accurate language, clear limitations, accessible interfaces, and control over their data.

Required behavior:

- use plain language;
- avoid dark patterns;
- support accessibility;
- explain errors and consequences;
- avoid exploiting fear or greed.

## 4. Decision Framework

When values conflict, use this order:

1. safety and financial integrity;
2. legal, privacy, and security obligations;
3. correctness and auditability;
4. user clarity and control;
5. reproducibility;
6. performance and convenience;
7. growth and marketing.

A growth objective must never override safety, honesty, or user control.

## 5. Product Conduct Standards

The Daily Roast AI must not:

- advertise guaranteed outcomes;
- hide material assumptions;
- present simulated trading as real execution;
- fabricate evidence;
- disguise sponsored content as independent analysis;
- encourage users to bypass risk controls;
- imply regulatory approval without evidence;
- use personal data in AI prompts without approved design and disclosure.

## 6. Engineering Conduct Standards

Contributors and coding agents must:

- prefer explicit contracts to hidden behavior;
- preserve deterministic boundaries;
- add tests for safety-critical behavior;
- document assumptions;
- disclose incomplete work;
- avoid weakening controls for speed;
- correct documentation drift;
- treat financial calculation bugs as high severity.

## 7. AI Conduct Standards

Runtime AI must:

- use only approved supplied evidence;
- state uncertainty and missing information;
- avoid unsupported certainty;
- remain advisory;
- never receive execution credentials or side-effect tools;
- return structured output;
- disclose when a safe answer cannot be produced.

## 8. Mission Alignment Test

A feature is mission-aligned when it improves at least one of the following without weakening another:

- evidence quality;
- user understanding;
- reproducibility;
- risk control;
- simulation honesty;
- auditability;
- accessibility;
- learning value.

## 9. Examples

### Aligned

- showing contradictions next to an AI conclusion;
- adding transaction-cost assumptions to backtests;
- making risk rejection reasons visible;
- creating a reproducible experiment report;
- adding a restore drill.

### Misaligned

- adding a flashing buy button based on AI confidence;
- hiding drawdown to improve conversion;
- optimizing backtests only on in-sample results;
- enabling live trading from a feature flag without a dedicated review;
- using urgency notifications to increase trading frequency.

## 10. Governance

Mission or value changes require:

- explicit owner approval;
- updates to brand, product vision, product requirements, and coding-agent rules;
- review of marketing, UI, AI prompts, and roadmap;
- a documented reason and effective date.

## 11. Related Documents

- `BRAND_GUIDELINES.md`
- `PRODUCT_VISION.md`
- `DESIGN_PRINCIPLES.md`
- `PRODUCT_REQUIREMENTS.md`
- `SECURITY.md`
- `AI_ARCHITECTURE.md`
- `../AGENTS.md`
