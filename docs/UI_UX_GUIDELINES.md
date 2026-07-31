# UI/UX Guidelines

Last reviewed: 2026-07-31  
Status: Authoritative product-experience specification

## 1. Purpose

Define how The Daily Roast AI presents market evidence, AI analysis, risk, simulation, and system state so that users can understand what happened, why it happened, and what remains uncertain.

## 2. Experience Principles

1. Evidence before action.
2. Safety state before performance state.
3. Explainability before density.
4. Progressive disclosure before information overload.
5. Consistency before novelty.
6. Accessibility before decoration.
7. Simulation must never look like live execution.
8. AI confidence must never be presented as probability of profit.

## 3. Product Modes

Every screen must visibly identify the active environment and trading mode:

- Local
- Demo
- Paper
- Staging
- Production Research

Live trading is not available. Paper-trading labels must remain visible on portfolio, order, fill, and performance screens.

## 4. Primary Navigation

Recommended top-level areas:

- Today
- Markets
- Research
- Strategies
- Paper Portfolio
- Backtests
- Experiments
- Audit
- Settings

Navigation labels must use plain language and remain stable.

## 5. Core Screen Patterns

### 5.1 Today

The default authenticated screen should answer:

- Is the system healthy?
- Is market data fresh?
- What is today's market regime?
- What changed since the previous cycle?
- Did strategy or risk block an action?
- Is the paper portfolio safe and reconciled?

### 5.2 Market Detail

Required sections:

- current market status;
- data freshness;
- price and volume context;
- deterministic indicators;
- Gemini analysis;
- contradictory evidence;
- risks and missing information;
- strategy intent;
- risk outcome;
- decision lineage.

### 5.3 Paper Portfolio

Required sections:

- virtual cash;
- open positions;
- exposure;
- realized and unrealized P&L;
- fees and simulated slippage;
- drawdown;
- open orders;
- reconciliation state;
- explicit paper-trading badge.

### 5.4 Backtest Report

Must show:

- strategy and risk versions;
- data range;
- execution assumptions;
- fees and slippage;
- cash and buy-and-hold benchmarks;
- return and drawdown;
- warnings and limitations;
- reproducibility metadata.

## 6. Information Hierarchy

Use this order when presenting a decision:

1. System and data status
2. Market snapshot
3. Deterministic evidence
4. Gemini interpretation
5. Contradictions and uncertainty
6. Strategy intent
7. Risk decision
8. Simulated execution result
9. Portfolio impact
10. Audit lineage

## 7. Status Language

Approved status labels:

- Healthy
- Degraded
- Stale
- Paused
- Halted
- Pending
- Rejected
- Approved
- Reduced
- Simulated
- Reconciled
- Needs Review

Do not use vague labels such as "Good", "Bad", or "Hot" for system or market state.

## 8. AI Presentation Rules

Gemini output must be visually separated from deterministic evidence.

Every AI report must show:

- model identifier or model family;
- generated timestamp;
- prompt/schema version;
- confidence label;
- evidence references;
- contradictions;
- risks;
- missing information;
- validation status.

The UI must not imply that AI generated a trade order.

## 9. Risk Presentation Rules

Risk state must be prominent and understandable.

- Rejections show the exact reason code and plain-language explanation.
- Reduced approvals show requested versus allowed exposure.
- Halts show scope, trigger, timestamp, and recovery requirements.
- Drawdown warnings show current value and configured threshold.
- Color is supplementary; text and icons remain mandatory.

## 10. Loading, Empty, Error, and Stale States

Every data-driven component must support:

- initial loading;
- background refresh;
- empty result;
- partial result;
- stale data;
- provider unavailable;
- authorization denied;
- validation failure;
- retry available;
- safe fallback active.

Never display stale analysis as current without a visible warning.

## 11. Confirmation and Destructive Actions

Require explicit confirmation for:

- starting an experiment;
- pausing or halting an experiment;
- changing active strategy or risk policy;
- cancelling an order;
- resetting demo data;
- deleting exports or user data;
- rotating credentials.

Confirmation copy must explain consequence and reversibility.

## 12. Accessibility

Primary workflows must meet WCAG 2.2 AA targets where practical.

Requirements:

- keyboard navigation;
- visible focus state;
- semantic landmarks;
- sufficient contrast;
- form labels and error associations;
- non-color-only status communication;
- accessible tables and charts;
- reduced-motion support;
- screen-reader announcements for critical state changes.

## 13. Responsive Behavior

Desktop is optimized for analysis density. Mobile is optimized for status, review, and safe actions.

On small screens:

- collapse secondary navigation;
- stack cards;
- keep critical status and halt controls visible;
- avoid horizontally compressed financial tables;
- provide summary-first chart alternatives.

## 14. Content Style

Use American English, concise labels, and plain-language explanations.

Avoid:

- hype;
- slang;
- emojis in operational UI;
- guaranteed outcomes;
- unexplained acronyms;
- anthropomorphic claims that AI "knows" or "believes".

## 15. UX Definition of Done

A feature is not complete until:

- all required states are implemented;
- keyboard and accessibility checks pass;
- mobile behavior is verified;
- simulation and environment labels are visible;
- AI and deterministic outputs are separated;
- critical actions have appropriate confirmation;
- copy follows brand and safety rules;
- tests cover loading, error, stale, halted, and unauthorized states.

## 16. Related Documents

- `BRAND_GUIDELINES.md`
- `DESIGN_PRINCIPLES.md`
- `DESIGN_SYSTEM.md`
- `INFORMATION_ARCHITECTURE.md`
- `USER_JOURNEYS.md`
- `COMPONENT_LIBRARY.md`
- `PRODUCT_REQUIREMENTS.md`
- `SECURITY.md`
