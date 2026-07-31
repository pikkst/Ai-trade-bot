# The Daily Roast AI — Design Principles

Last reviewed: 2026-07-31
Status: Authoritative product and interface design principles

## 1. Purpose

These principles guide product, UX, UI, content, reporting, and interaction design. They apply to the public website, authenticated application, reports, exports, alerts, and administrative experiences.

## 2. Principle: Evidence Is the Primary Interface

The product should lead with evidence, not decorative dashboards or opaque scores.

Every material analytical view should make it possible to identify:

- the source data;
- data freshness;
- data quality;
- derived features;
- AI interpretation;
- contradictions;
- uncertainty;
- deterministic strategy outcome;
- deterministic risk outcome.

## 3. Principle: Separate Facts, Interpretation, and Action

The interface must visually and semantically separate:

1. observed market facts;
2. deterministic calculations;
3. Gemini interpretation;
4. strategy intent;
5. risk decision;
6. simulated execution.

Users must not confuse AI prose with an approved action.

## 4. Principle: Make Risk Visible Before Opportunity

Risk state must be at least as prominent as positive market interpretation.

Required visible states include:

- stale data;
- incomplete data;
- elevated volatility;
- risk rejection;
- cooldown;
- drawdown proximity;
- portfolio halt;
- experiment halt;
- provider failure;
- simulation mode.

## 5. Principle: Calm, Not Urgent

The product must avoid visual or verbal pressure that encourages impulsive behavior.

Do not use:

- flashing price elements;
- countdowns designed to provoke action;
- celebratory trade animations;
- exaggerated gain colors;
- aggressive notification language.

Use restrained transitions and clear status changes.

## 6. Principle: Simulation Must Be Unmistakable

Every paper-trading surface must display a persistent simulation label.

The user must be able to distinguish:

- local development;
- cloud demo;
- paper experiment;
- staging;
- production research;
- future exchange sandbox.

Environment and execution mode must never depend only on color.

## 7. Principle: Progressive Disclosure

Show the most important information first, while preserving access to full evidence and audit detail.

Suggested hierarchy:

1. current state and freshness;
2. concise market summary;
3. key evidence and contradictions;
4. risk state;
5. strategy and simulated effect;
6. detailed indicators and lineage;
7. raw technical metadata.

## 8. Principle: Explain Every Important State

Errors and restrictions should explain:

- what happened;
- why it matters;
- what the system did safely;
- what the user may do next;
- whether data or state remains reliable.

Avoid generic messages such as `Something went wrong` when a safe specific status is available.

## 9. Principle: Design for Auditability

Important records should be linkable through stable identifiers and human-readable context.

A user should be able to navigate from a paper fill to:

- order;
- risk evaluation;
- strategy intent;
- Gemini report;
- feature set;
- market snapshot;
- source candles;
- experiment configuration.

## 10. Principle: Accessibility Is a Product Requirement

Primary workflows must support:

- keyboard navigation;
- visible focus states;
- sufficient contrast;
- semantic headings;
- screen-reader labels;
- reduced motion preferences;
- text alternatives for charts;
- status communication independent of color;
- responsive layouts.

## 11. Principle: Mobile for Review, Desktop for Deep Research

Mobile experiences should support:

- today's summary;
- risk and halt status;
- recent analysis;
- portfolio overview;
- alerts;
- report reading.

Complex backtest configuration, large comparison tables, and detailed chart research may be optimized for wider screens while remaining usable on mobile.

## 12. Principle: Honest Charts

Charts must:

- label units and intervals;
- disclose missing data;
- avoid misleading axis truncation;
- distinguish actual market data from simulated results;
- display benchmark context where relevant;
- show fee and slippage assumptions for performance views;
- support accessible summaries.

## 13. Principle: Consistent Status Language

Use stable status vocabulary across UI, API, logs, and reports.

Examples:

- Draft
- Ready
- Running
- Paused
- Halted
- Completed
- Archived
- Valid
- Rejected
- Stale
- Unavailable
- Simulated

Do not create multiple labels for the same domain state without a documented reason.

## 14. Principle: AI Must Not Masquerade as Certainty

AI output must display:

- model and report version where appropriate;
- confidence as model self-assessment, not probability of profit;
- evidence references;
- contradictions;
- missing information;
- validation status;
- provider failure or fallback state.

## 15. Principle: User Control Requires Consequence Clarity

Before a user changes an experiment, risk policy, or halt state, the interface should explain:

- the affected scope;
- whether the change is immediate;
- whether the active experiment configuration permits it;
- whether a new experiment version is required;
- the audit consequence.

## 16. Principle: Defaults Must Be Safe

Default UI and configuration behavior should:

- use fake providers locally;
- keep live trading disabled;
- require explicit opt-in for real Gemini usage;
- use conservative risk limits;
- show stale states rather than silently using old data;
- prevent browser writes to critical financial tables.

## 17. Principle: Performance Must Support Comprehension

Prioritize fast display of:

- application shell;
- last known safe status;
- data freshness;
- current risk and halt state.

Do not hide integrity uncertainty behind skeleton loading states for extended periods. Show a truthful status.

## 18. Principle: Brand Expression Must Support Trust

Use the warm Roast identity as an accent, not as entertainment that undermines analytical seriousness.

The product can be distinctive and memorable while remaining calm, precise, and credible.

## 19. Design Review Checklist

A feature design is ready when:

- facts, AI interpretation, strategy, risk, and simulation are separated;
- risk and stale states are visible;
- simulation and environment labels are explicit;
- accessibility requirements are addressed;
- mobile and desktop behavior are defined;
- empty, loading, unavailable, error, paused, and halted states exist;
- analytics do not imply guaranteed performance;
- terminology follows naming conventions;
- security-sensitive actions are not available through presentation-only controls.

## 20. Related Documents

- `BRAND_GUIDELINES.md`
- `PRODUCT_VISION.md`
- `MISSION_AND_VALUES.md`
- `NAMING_CONVENTIONS.md`
- `SECURITY.md`
- `API_SPECIFICATION.md`
- `../AGENTS.md`
