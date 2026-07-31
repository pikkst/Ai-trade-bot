# The Daily Roast AI — Product Vision

Last reviewed: 2026-07-31
Status: Authoritative product vision

## 1. Executive Summary

The Daily Roast AI is an evidence-driven market intelligence platform designed to help users understand markets, test hypotheses, compare strategies, simulate decisions, and learn from outcomes before risking capital.

The product combines:

- reliable market data;
- deterministic analytical features;
- Google Gemini-assisted interpretation;
- transparent strategy logic;
- non-bypassable risk controls;
- realistic paper trading;
- reproducible backtesting;
- complete decision lineage.

The product is not defined by automated trading. Trading is one possible downstream capability. Research, evidence, simulation, and risk intelligence are the core product.

## 2. Vision Statement

> The Daily Roast AI will become a trusted AI-assisted research operating system for financial markets, enabling people to make more informed decisions through transparent evidence, reproducible analysis, and controlled experimentation.

## 3. Product Thesis

Market participants face too much fragmented data, emotional commentary, unexplained AI output, and misleading performance claims.

The Daily Roast AI addresses this by creating one auditable workflow:

```text
Market evidence
  -> validated data
  -> deterministic features
  -> explainable AI interpretation
  -> strategy hypothesis
  -> deterministic risk review
  -> simulation or research output
  -> measured outcome
  -> learning and audit
```

The product's advantage is not simply access to an LLM. Its advantage is the controlled system around the model.

## 4. Core Problem

Individual investors and researchers often lack:

- a reliable way to distinguish evidence from opinion;
- transparent explanations for AI-generated conclusions;
- reproducible methods for testing strategies;
- realistic simulation including fees and slippage;
- disciplined risk controls;
- a complete history of why a decision was made;
- an affordable research environment that does not require institutional infrastructure.

## 5. Product Promise

The Daily Roast AI helps users answer:

- What is happening in the market?
- What evidence supports that interpretation?
- What evidence contradicts it?
- What is uncertain or missing?
- How would a defined strategy respond?
- Would the risk policy allow that response?
- How would the decision behave in simulation?
- What can be learned from the result?

The product never promises that a forecast will be correct.

## 6. Product Philosophy

### Evidence Before Opinion

Claims must be traceable to validated data or clearly marked interpretation.

### Research Before Execution

A strategy must be specified, tested, and simulated before any future private exchange integration is considered.

### AI Assists; Deterministic Controls Decide

Gemini may interpret evidence. It may not bypass strategy, risk, accounting, or execution controls.

### Reproducibility Before Optimization

A result that cannot be explained and reproduced has limited research value.

### Human Control

The user remains responsible for configuration, approval, and progression between safety stages.

### Honest Limitations

The product must disclose stale data, missing information, model failure, simulation assumptions, and uncertainty.

## 7. Initial Product Scope

The first version focuses on cryptocurrency research because public market data is accessible and supports rapid controlled experimentation.

Initial capabilities:

- Binance Spot public market data;
- BTC/EUR primary research pair;
- deterministic indicators;
- Gemini structured market reports;
- strategy and risk evaluation;
- paper portfolio and simulated execution;
- backtesting;
- audit and experiment reporting;
- a 30-day EUR 20 virtual-capital experiment.

## 8. Long-Term Scope

The architecture should permit later support for:

- additional cryptocurrencies;
- equities;
- exchange-traded funds;
- foreign exchange;
- commodities;
- macroeconomic data;
- portfolio-level research;
- research alerts;
- collaborative workspaces;
- institutional reporting APIs.

Expansion to a new asset class requires new data-quality, market-structure, risk, legal, and product reviews. The platform must not assume crypto rules apply unchanged to other markets.

## 9. Target Users

### 9.1 Independent Investor

Wants understandable market research, risk context, paper simulation, and decision history without building a quantitative platform.

### 9.2 Active Researcher or Trader

Wants reproducible backtests, strategy comparison, configurable assumptions, and evidence-backed reports.

### 9.3 Analyst

Wants structured market summaries, contradiction analysis, exports, and auditable source lineage.

### 9.4 Developer or Quantitative Builder

Wants APIs, versioned data, strategy contracts, testable provider boundaries, and reproducible research runs.

### 9.5 Future Professional Team

May require team workspaces, governance, access control, compliance retention, custom research models, and enterprise deployment.

## 10. Product Pillars

### Markets

Validated market data, freshness, quality, normalization, and market-state views.

### Research

Deterministic evidence and Gemini-assisted interpretation with uncertainty and contradictions.

### Strategies

Versioned hypotheses that convert approved inputs into deterministic intents.

### Risk

Non-bypassable deterministic limits, halts, and reason codes.

### Simulation

Paper execution with realistic costs, precision, and accounting.

### Backtesting

Reproducible historical replay using shared strategy, risk, execution, and portfolio contracts.

### Portfolio Intelligence

Balances, exposure, drawdown, P&L, benchmarks, and decision history.

### Audit and Learning

Complete lineage, reports, comparisons, and post-experiment review.

## 11. Product Differentiation

The Daily Roast AI differentiates through the combination of:

- structured and validated AI output;
- explicit evidence and contradiction references;
- deterministic strategy and risk boundaries;
- realistic simulation rather than abstract recommendations;
- append-only accounting and reconciliation;
- reproducible backtests;
- local and low-cost cloud development paths;
- safety-first progression from research to paper experimentation.

The product does not rely on an opaque proprietary score as its only value proposition.

## 12. User Experience Vision

The primary user experience should feel like a research workspace, not a casino or high-pressure trading terminal.

A user should be able to open **Today's Roast** and see:

1. market condition;
2. data freshness and quality;
3. key evidence;
4. Gemini interpretation;
5. contradictions and uncertainty;
6. deterministic strategy intent;
7. risk decision;
8. simulated portfolio impact;
9. related historical and backtest context.

Every important state must be understandable without inspecting raw logs.

## 13. Product Evolution

### Stage 1 — Local Research Prototype

- deterministic fake providers;
- local Supabase stack;
- core domains and tests;
- reproducible end-to-end scenario.

### Stage 2 — Public Cloud Demo

- Cloudflare Pages;
- Render FastAPI;
- dedicated Supabase project;
- GitHub Actions research cycles;
- bounded Gemini usage;
- public read-only research experience.

### Stage 3 — Controlled Paper Experiment

- frozen 30-day configuration;
- EUR 20 virtual capital;
- complete audit and reconciliation;
- cash and buy-and-hold benchmarks.

### Stage 4 — Production Research Service

- staging and production isolation;
- stronger authentication;
- managed backup and recovery;
- measured SLOs;
- customer-facing research and paper portfolios.

### Stage 5 — Binance Sandbox Assessment

- private test-environment credentials;
- order lifecycle and reconciliation;
- separate security gate;
- no live capital.

### Stage 6 — Live Trading Assessment

Not authorized by this vision. It requires a separate legal, security, financial-risk, operational, and owner approval process.

## 14. One-Year Vision

Within one year, the product should aim to provide:

- stable crypto market research;
- transparent Gemini-assisted reports;
- paper portfolios;
- reproducible backtests;
- daily or hourly research cycles;
- clear audit lineage;
- a refined user interface under `thedailyroast.online`;
- evidence from real user and experiment feedback.

## 15. Three-Year Vision

Subject to validated demand:

- broader crypto coverage;
- multi-strategy research;
- portfolio intelligence;
- collaborative workspaces;
- alerts and scheduled reports;
- configurable research templates;
- professional exports and APIs;
- additional market-data providers;
- selective expansion to other asset classes.

## 16. Five-Year Vision

The Daily Roast AI may become a market research operating system used by individuals, analysts, and small professional teams.

Potential capabilities:

- cross-asset research;
- portfolio-wide risk intelligence;
- enterprise workspaces;
- governed model and prompt selection;
- institutional audit and retention;
- customer-defined strategies;
- integrated research APIs;
- optional approved execution integrations separated from the research core.

This is a direction, not a commitment to implement every capability.

## 17. Success Metrics

### Product Quality

- percentage of analyses with valid structured output;
- evidence-reference validation rate;
- data freshness and completeness;
- complete decision-lineage rate;
- zero unresolved reconciliation mismatch;
- zero duplicate financial side effects.

### User Value

- research reports opened and completed;
- repeated use of evidence and contradiction views;
- backtests completed;
- paper experiments completed;
- user-reported clarity and trust;
- time saved in preparing market research.

### Operational Quality

- scheduled research-cycle success;
- API and UI reliability;
- provider failure recovery;
- backup and restore success;
- security and authorization test results.

### Business Metrics for Future Productization

- activated workspaces;
- retained active users;
- conversion from demo to sustained research use;
- cost per active workspace;
- support burden;
- willingness to pay for validated features.

Profitability of a simulated strategy is not the sole product success metric.

## 18. Non-Goals and Permanent Boundaries

The product must not:

- guarantee returns;
- fabricate evidence;
- conceal model failure;
- present AI confidence as probability of profit;
- bypass risk controls;
- silently convert paper results into live orders;
- manipulate users through urgency or fear;
- sell undisclosed conflicts of interest;
- weaken auditability to improve apparent performance;
- present backtests as proof of future returns.

## 19. Business Model Direction

The initial objective is product validation, not immediate monetization.

Possible future models include:

- free research tier;
- paid individual research workspace;
- advanced backtesting and portfolio tier;
- professional analyst tier;
- enterprise or private deployment;
- API access.

Pricing must follow measured value, cost, and user demand. It must not depend on misleading performance claims.

## 20. Strategic Risks

- users may misinterpret analysis as financial advice;
- LLM output may be incorrect or inconsistent;
- market data or provider availability may change;
- free cloud services may be unreliable;
- backtests may encourage overfitting;
- product scope may expand faster than validation;
- brand confusion may arise from existing uses of similar names;
- regulatory requirements may change by market and jurisdiction.

These risks require explicit product, legal, technical, and communication controls.

## 21. Vision Decision Rules

A proposed feature should be prioritized when it:

- improves evidence quality;
- improves explainability;
- improves reproducibility;
- reduces user risk;
- improves auditability;
- enables measured learning;
- solves a validated user problem.

A feature should be deferred when it primarily:

- creates hype;
- increases automation without control;
- adds operational cost without evidence;
- weakens safety boundaries;
- depends on unsupported profitability claims;
- expands to a new market without domain-specific validation.

## 22. Related Documents

- `BRAND_GUIDELINES.md`
- `MISSION_AND_VALUES.md`
- `DESIGN_PRINCIPLES.md`
- `PRODUCT_REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `../AGENTS.md`
