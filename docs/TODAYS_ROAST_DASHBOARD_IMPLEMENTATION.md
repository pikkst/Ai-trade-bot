# Today’s Roast Dashboard Implementation Specification

Last reviewed: 2026-07-31  
Status: Sprint 5 authoritative dashboard implementation specification

## 1. Purpose

This document defines the implementation contract for the **Today’s Roast** dashboard: the primary evidence-summary experience of The Daily Roast AI.

The dashboard must help a user understand what the system knows, what it does not know, what changed, which deterministic controls were applied, what Gemini contributed, and whether the current research cycle is safe to inspect. It is a research and decision-support interface, not a trading terminal.

The dashboard must preserve evidence lineage, uncertainty, simulation state, freshness, reconciliation status, and halt conditions. It must never imply that an AI narrative is an instruction to trade or that simulated performance predicts future results.

## 2. Scope

Sprint 5 covers:

- the Today’s Roast route and page composition;
- dashboard read-model contracts;
- summary hierarchy and evidence ordering;
- market snapshot presentation;
- deterministic strategy and risk-decision presentation;
- Gemini advisory presentation;
- portfolio and benchmark summary presentation;
- cycle status, freshness, reconciliation, degraded, and halt states;
- decision-lineage navigation;
- responsive, accessible, loading, empty, partial, and failure states;
- frontend integration boundaries;
- dashboard testing, visual regression, analytics, and observability requirements.

Sprint 5 does not implement market-data ingestion, feature calculations, strategy logic, risk logic, paper execution, ledger accounting, reconciliation, authentication, or Gemini prompting. Those remain backend and domain responsibilities.

## 3. User Outcomes

A user should be able to answer the following questions within one page:

1. Is this research cycle current, simulated, reconciled, and safe to inspect?
2. Which market and interval does the summary cover?
3. What materially changed since the prior finalized cycle?
4. What does deterministic evidence indicate?
5. What did the strategy propose, and what did risk controls allow, reduce, or reject?
6. What did Gemini observe, and how confident or uncertain was that advisory output?
7. What happened in the paper portfolio and against the selected benchmarks?
8. Which evidence, model output, policy decision, order, fill, or ledger entry supports each statement?
9. Are any data-quality, provider, integrity, or service problems affecting interpretation?

## 4. Route and Navigation Contract

Canonical route:

```text
/todays-roast
```

Optional cycle-specific route:

```text
/todays-roast/:cycleId
```

The primary navigation label is **Today’s Roast**. The route must be reachable through the Sprint 3 application shell and use the shell’s canonical environment, simulation, service-state, and account context.

The page must support:

- latest completed cycle;
- a selected historical cycle;
- direct links to evidence and lineage resources;
- browser refresh without losing the selected cycle;
- URL-stable filter or view state only when it is safe and useful;
- a clear return path from cycle detail to the latest summary.

## 5. Information Architecture

The page is composed in this order:

1. global safety and integrity banners;
2. page header and cycle identity;
3. executive evidence summary;
4. market snapshot;
5. deterministic strategy and risk outcome;
6. Gemini advisory analysis;
7. paper portfolio and benchmark summary;
8. decision-lineage timeline;
9. data-quality and service diagnostics;
10. methodology, limitations, and disclaimer context.

Critical warnings must appear before positive performance information. Halt, reconciliation failure, stale data, or incomplete-cycle state must never be visually subordinated to portfolio gains or AI commentary.

## 6. Canonical Page Header

The page header must include:

- title: `Today’s Roast`;
- selected market and interval;
- cycle completion timestamp in local display with accessible UTC value;
- cycle identifier or shortened traceable reference;
- `SimulationBadge`;
- `EnvironmentBadge`;
- `FreshnessIndicator`;
- reconciliation status;
- a link to the full cycle evidence view.

The header must not include `Buy`, `Sell`, `Trade Now`, urgency countdowns, profit promises, or celebratory language tied to financial outcomes.

## 7. Dashboard Read Model

The frontend consumes one purpose-built read model rather than assembling the page from loosely related requests.

Recommended endpoint:

```http
GET /api/v1/roasts/latest
GET /api/v1/roasts/{cycle_id}
```

Recommended top-level contract:

```ts
interface TodaysRoastReadModel {
  schemaVersion: string;
  cycle: CycleSummary;
  serviceState: ServiceStateSummary;
  market: MarketSummary;
  deterministicAnalysis: DeterministicAnalysisSummary;
  riskDecision: RiskDecisionSummary;
  aiAdvisory: AiAdvisorySummary | null;
  portfolio: PortfolioSummary;
  benchmarks: BenchmarkSummary[];
  lineage: LineageSummary;
  dataQuality: DataQualitySummary;
  limitations: LimitationSummary[];
  links: RoastResourceLinks;
}
```

The read model must be produced server-side from authoritative persisted data. The frontend may format, group, sort approved collections, and manage presentation state, but must not recalculate indicators, risk, position size, P&L, drawdown, benchmark return, confidence, or reconciliation status.

## 8. Cycle Identity and State

Required cycle fields:

- immutable cycle ID;
- schema version;
- market symbol;
- quote currency;
- interval;
- source candle close time;
- cycle start and completion timestamps;
- status: pending, running, completed, degraded, failed, halted, or superseded;
- data snapshot ID;
- feature-set version;
- strategy version;
- risk-policy version;
- AI provider and model identifiers when AI was used;
- reconciliation status;
- trace or correlation ID.

The UI must not present a running, failed, unreconciled, or superseded cycle as an ordinary completed roast.

## 9. Executive Evidence Summary

The executive summary is concise and evidence-linked. It contains:

- one deterministic market-state statement;
- one strategy-intent statement;
- one risk-outcome statement;
- one portfolio-impact statement;
- one AI-advisory statement when available;
- one explicit limitations or uncertainty statement;
- links to supporting evidence.

Each statement must expose its provenance category:

- market evidence;
- deterministic strategy;
- deterministic risk control;
- paper execution or ledger;
- benchmark calculation;
- Gemini advisory;
- system or data-quality state.

AI text must be visually and semantically labeled as advisory. It cannot be merged into deterministic statements in a way that obscures source boundaries.

## 10. Market Snapshot

The market snapshot may include:

- finalized close price;
- interval return;
- selected trend indicators;
- selected momentum indicators;
- selected volatility indicators;
- volume context;
- prior-cycle comparison;
- source and snapshot identifiers;
- freshness and completeness state.

Rules:

- all values come from the backend read model;
- indicator names include parameters where material;
- unsupported precision is not displayed;
- missing values remain missing and are explained;
- charts must identify finalized versus unavailable periods;
- color is not the only encoding for direction;
- the page must not infer intraperiod prices from incomplete candles.

## 11. Deterministic Strategy and Risk Outcome

This section must distinguish:

1. strategy intent;
2. risk evaluation;
3. permitted paper action;
4. actual paper execution result.

Required strategy fields:

- strategy name and version;
- intent category;
- deterministic reason codes;
- evaluated inputs or evidence references;
- evaluation timestamp.

Required risk fields:

- policy version;
- decision: allowed, reduced, rejected, halted, or not-applicable;
- reason codes;
- requested and approved exposure when applicable;
- binding constraints;
- current drawdown and limits;
- reconciliation precondition;
- halt state.

The interface must not collapse strategy intent and risk approval into one label. A proposed action rejected by risk must remain visibly rejected.

## 12. Gemini Advisory Analysis

Gemini output is optional and non-authoritative.

The section must include:

- provider and model name;
- prompt-template or analysis-contract version;
- generated timestamp;
- advisory summary;
- structured observations;
- uncertainty and limitations;
- cited evidence references;
- validation state;
- fallback or omission reason when unavailable.

The section must clearly state that Gemini cannot place orders, determine final position size, override risk policy, alter credentials, mutate the ledger, or enable live trading.

Invalid, unvalidated, stale, budget-blocked, or unavailable AI output must not be replaced with synthetic commentary. The safe state is an explicit unavailable or omitted state.

## 13. Portfolio and Benchmark Summary

The portfolio area may include:

- reconciled simulated equity;
- available simulated cash;
- open simulated position value;
- realized and unrealized P&L;
- fees and modeled execution costs;
- daily and total drawdown;
- open paper orders;
- benchmark values for cash and buy-and-hold;
- experiment start value and elapsed day count.

Rules:

- simulation labeling remains visible within or immediately adjacent to the section;
- values must be reconciled before ordinary display;
- unreconciled values must be blocked or explicitly quarantined;
- gains and losses use signs and text, not color alone;
- benchmark methodology is accessible;
- no annualized projection or forward return is inferred from the experiment;
- no celebratory confetti, streaks, urgency, or gamified profit treatment is allowed.

## 14. Decision Lineage

The lineage section provides a traceable ordered view:

```text
finalized candle
  -> validation result
  -> immutable snapshot
  -> feature set
  -> deterministic strategy intent
  -> risk decision
  -> optional Gemini advisory
  -> paper order
  -> simulated fill
  -> ledger postings
  -> reconciliation result
  -> dashboard read model
```

Each available step must include:

- event or resource type;
- immutable identifier;
- timestamp;
- version where applicable;
- status;
- link to detail;
- reason code or concise description.

Missing required lineage is an integrity problem, not an ordinary empty state.

## 15. Data Quality and Diagnostics

The page must expose interpretation-affecting diagnostics without leaking secrets or internal stack traces.

Supported diagnostics include:

- missing or repaired candles;
- stale market data;
- snapshot validation warnings;
- provider throttling or outage;
- delayed scheduled execution;
- AI budget exhaustion;
- schema-version mismatch;
- reconciliation warning or failure;
- partial read-model assembly;
- superseded cycle;
- system halt.

Every diagnostic must include severity, user impact, affected data, timestamp, and safe next action or investigation path when available.

## 16. Page-State Matrix

The route must define explicit rendering for:

- initial loading;
- latest completed cycle;
- selected historical cycle;
- no completed cycle yet;
- running cycle with prior completed cycle available;
- running cycle with no prior cycle;
- degraded but inspectable cycle;
- stale data;
- AI unavailable with deterministic evidence available;
- unauthorized;
- not found;
- backend unavailable;
- read-model schema mismatch;
- reconciliation failure;
- lineage-integrity failure;
- system halt.

Loading states may show structure but never plausible prices, P&L, confidence, or timestamps.

## 17. Responsive Behavior

Desktop may use a multi-column composition. Mobile must preserve the same semantic ordering and safety hierarchy.

Requirements:

- safety banners remain first and visible;
- cycle identity remains readable without horizontal scrolling;
- summary cards reflow into one column;
- critical labels are not truncated into ambiguity;
- tables provide an accessible stacked or detail alternative;
- charts provide textual summaries;
- lineage remains navigable by keyboard and touch;
- sticky elements must not obscure content at zoom;
- no critical evidence exists only on hover.

## 18. Accessibility Requirements

The dashboard targets WCAG 2.2 AA where practical.

Required behavior:

- one clear page heading;
- logical heading hierarchy;
- landmarks for navigation and main content;
- skip-link support through the application shell;
- accessible names for cycle selectors and evidence links;
- status conveyed through text and semantics;
- chart summaries and accessible data alternatives;
- focus preservation when changing cycles;
- polite announcements for ordinary refreshes;
- assertive announcements only for material halt or integrity changes;
- keyboard-operable disclosures and timeline controls;
- no forced motion;
- readable reflow at 200% and relevant cases at 400% zoom.

## 19. Frontend Data-Fetching Contract

The route should use TanStack Query or the approved frontend data layer.

Requirements:

- stable query keys by cycle ID;
- latest-cycle refetch policy that does not create request storms;
- no automatic replacement of a historical cycle with the newest cycle;
- cancellation of obsolete requests;
- explicit retry policy by error class;
- no retry loop for authorization, schema mismatch, or integrity failure;
- cached data visibly marked stale when applicable;
- server timestamps remain authoritative;
- sanitized client-side error mapping.

## 20. Analytics and Privacy

Allowed product analytics are limited to privacy-preserving interaction events such as:

- route viewed;
- cycle changed;
- evidence detail opened;
- methodology opened;
- diagnostic expanded;
- retry requested.

Analytics must not contain:

- credentials or tokens;
- raw AI prompts or provider payloads;
- full account identifiers;
- private financial data beyond approved coarse event metadata;
- order, fill, or ledger payloads;
- user-entered secrets.

## 21. Observability

The dashboard integration should expose:

- read-model request latency and status;
- latest-cycle age;
- schema-version mismatch count;
- stale-response count;
- dashboard error-state count by safe category;
- evidence-link failure count;
- client build version;
- correlation ID propagation where approved.

Observability must not log secrets, private payloads, or full AI content.

## 22. Security Boundaries

The dashboard is read-only for Sprint 5.

It must not:

- expose private exchange credentials;
- include live-order controls;
- mutate risk policy;
- mutate strategy configuration;
- mutate ledger records;
- enable private Binance access;
- allow AI output to invoke commands;
- trust browser-calculated authorization;
- render unsanitized provider or Markdown content;
- reveal stack traces, SQL, tokens, or internal network details.

Server authorization and Supabase RLS remain authoritative.

## 23. Testing Strategy

### Contract Tests

Validate read-model schemas, version compatibility, nullability, reason codes, currency fields, timestamps, and evidence links.

### Component and Route Tests

Validate section ordering, source labels, loading behavior, error mapping, cycle selection, historical-cycle stability, and link generation.

### Accessibility Tests

Validate headings, landmarks, keyboard flow, focus, announcements, chart alternatives, contrast, zoom, and reflow.

### Visual Regression

Capture approved states for:

- desktop and mobile;
- light and dark themes;
- completed, degraded, stale, halted, and reconciliation-failure states;
- AI available and unavailable states;
- positive, neutral, and negative simulated outcomes;
- long reason codes and long localized content.

### End-to-End Tests

Verify latest and historical routes, refresh behavior, backend failure, stale cache, schema mismatch, evidence navigation, and sanitized diagnostics.

## 24. Acceptance Criteria

Sprint 5 documentation is accepted when:

1. the Today’s Roast route, hierarchy, and read model are explicit;
2. deterministic evidence, risk decisions, AI advisory, execution, and ledger outcomes remain distinguishable;
3. all material values are server-derived and evidence-linked;
4. simulation, freshness, reconciliation, degraded, and halt states cannot be hidden;
5. AI unavailable and invalid states fail safely without fabricated replacement text;
6. loading states do not fabricate market or financial evidence;
7. responsive and accessible behavior preserves safety hierarchy;
8. security, privacy, analytics, and observability boundaries are defined;
9. implementation tasks contain measurable verification gates;
10. no requirement introduces live trading or weakens deterministic controls.

## 25. Definition of Done

The specification is complete when:

- it is committed with `SPRINT_5_TASKS.md`;
- terminology matches the shell, component library, API, database, AI, security, testing, and product documents;
- the dashboard read model and all page states are explicit;
- evidence lineage and provenance are mandatory;
- the resulting commits are fetched and verified.

## 26. Next Sprint Boundary

Sprint 6 should define the detailed **market evidence and charting workspace**, including finalized-candle visualization, indicator overlays, accessible chart alternatives, snapshot comparison, data-quality annotation, and evidence export without introducing frontend domain calculations.