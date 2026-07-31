# Information Architecture

Last reviewed: 2026-07-31  
Status: Authoritative navigation and content-structure specification

## 1. Purpose

Define how The Daily Roast AI organizes product areas, routes, entities, navigation, and content relationships.

## 2. Primary Product Areas

- Today
- Markets
- Research
- Strategies
- Paper Portfolio
- Backtests
- Experiments
- Audit
- Settings

## 3. Route Model

Recommended authenticated routes:

```text
/app
/app/today
/app/markets
/app/markets/:symbol
/app/research
/app/research/:analysisId
/app/strategies
/app/strategies/:strategyId
/app/portfolio
/app/portfolio/orders
/app/portfolio/fills
/app/backtests
/app/backtests/:backtestId
/app/experiments
/app/experiments/:experimentId
/app/audit
/app/settings
/app/settings/workspace
/app/settings/risk
/app/settings/ai
/app/settings/security
```

Public routes:

```text
/
/features
/methodology
/security
/about
/sign-in
/legal/privacy
/legal/terms
```

## 4. Navigation Rules

- Primary navigation contains no more than nine top-level items.
- Context navigation appears only where a domain has multiple related views.
- Breadcrumbs are required for deep detail routes.
- User role and environment determine available actions, not merely visible links.
- Current location is always visually identifiable.

## 5. Entity Relationships

```text
Workspace
  -> Experiment
  -> Market Snapshot
  -> Feature Set
  -> Gemini Analysis
  -> Strategy Evaluation
  -> Risk Evaluation
  -> Paper Order
  -> Fill
  -> Ledger Transaction
  -> Portfolio Projection
  -> Audit Events
```

Every detail screen should link backward and forward through this lineage where authorized.

## 6. Today Dashboard

The Today page contains:

1. environment and health banner;
2. market freshness;
3. latest research summary;
4. strategy and risk outcome;
5. paper portfolio summary;
6. active warnings or halts;
7. latest research-cycle status;
8. quick links to evidence and audit lineage.

## 7. Market Information Architecture

Market list:

- symbol;
- latest finalized candle time;
- regime;
- volatility;
- data status;
- latest analysis status.

Market detail tabs:

- Overview
- Evidence
- AI Analysis
- Decisions
- History

## 8. Research Information Architecture

Research list filters:

- symbol;
- time range;
- regime;
- validation state;
- strategy action;
- risk outcome.

Research detail sections follow decision lineage and must not hide rejected or contradictory evidence.

## 9. Portfolio Information Architecture

Sections:

- Summary
- Positions
- Orders
- Fills
- Ledger
- Performance
- Reconciliation

The simulation label and active risk profile remain visible throughout.

## 10. Settings Information Architecture

Settings are separated by responsibility:

- Workspace
- Market Data
- Gemini
- Strategy
- Risk
- Experiment
- Security
- Integrations

Settings must show active version, draft version, effective date, and whether changes require a new experiment.

## 11. Search and Filtering

Global search may cover symbols, analyses, backtests, experiments, and audit entity IDs.

Financial and audit lists require:

- deterministic ordering;
- pagination;
- shareable URL filters;
- clear reset behavior;
- empty-result explanation.

## 12. Authorization

- Viewer: read-only research, portfolio, reports, and audit access.
- Operator: operational research and paper-experiment actions within policy.
- Owner: configuration, policy activation, halt recovery, and privileged exports.

Authorization is enforced server-side. Information architecture must not imply otherwise.

## 13. URL and State Rules

- Stable resource IDs in URLs.
- Filters encoded in query parameters where shareable.
- Sensitive values never placed in URLs.
- Route state must survive refresh where reasonable.
- Invalid or inaccessible resources return an explicit not-found or unauthorized state.

## 14. Mobile Information Architecture

Mobile primary areas:

- Today
- Markets
- Research
- Portfolio
- More

The More area contains backtests, experiments, audit, and settings.

## 15. Definition of Done

Information architecture is implemented when:

- all routes are defined and role-mapped;
- navigation works by keyboard;
- deep links and refresh work;
- lineage links connect core entities;
- mobile navigation is tested;
- unauthorized routes fail securely;
- route names match API and documentation terminology.

## 16. Related Documents

- `UI_UX_GUIDELINES.md`
- `USER_JOURNEYS.md`
- `COMPONENT_LIBRARY.md`
- `API_SPECIFICATION.md`
- `NAMING_CONVENTIONS.md`
