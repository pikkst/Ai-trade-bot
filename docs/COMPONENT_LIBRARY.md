# Component Library

Last reviewed: 2026-07-31  
Status: Authoritative reusable-component specification

## 1. Purpose

Define the reusable frontend components required to implement The Daily Roast AI consistently, accessibly, and safely.

## 2. Implementation Principles

- Components consume design tokens.
- Accessibility is built in.
- Domain components do not duplicate business logic.
- Server state is managed through TanStack Query.
- Financial values use explicit formatting helpers.
- Every component supports loading, empty, error, stale, disabled, and unauthorized states where applicable.

## 3. Foundation Components

- Button
- IconButton
- Link
- TextField
- NumberField
- Select
- Checkbox
- RadioGroup
- Switch
- TextArea
- FormField
- Tooltip
- Popover
- Dialog
- Drawer
- Tabs
- Accordion
- Badge
- Avatar
- Divider
- Skeleton
- Spinner
- Toast
- Alert

## 4. Layout Components

- AppShell
- PublicSiteShell
- Header
- Sidebar
- MobileNavigation
- Breadcrumbs
- PageHeader
- ContentSection
- Card
- Grid
- Stack
- SplitPane
- ContextPanel
- EmptyState
- ErrorState

## 5. Status Components

### EnvironmentBadge

Displays Local, Demo, Paper, Staging, or Production Research.

### SystemHealthBanner

Displays healthy, degraded, stale, paused, or halted state.

### DataFreshnessIndicator

Shows latest finalized timestamp, age, threshold, and status.

### ReconciliationBadge

Shows reconciled, pending, or mismatch.

### ProviderStatus

Shows Gemini or Binance availability without exposing credentials.

## 6. Market Components

- SymbolSelector
- MarketSummaryCard
- PriceChange
- CandleChart
- VolumeChart
- IndicatorTable
- DataQualityPanel
- MarketRegimeBadge
- EvidenceList
- EvidenceReference
- MissingDataWarning

Charts require accessible text summaries.

## 7. AI Components

### AIAnalysisCard

Required fields:

- Gemini attribution;
- generated time;
- model and schema version;
- regime;
- recommendation;
- confidence;
- summary;
- validation state.

### EvidenceAndContradictions

Separates supporting evidence, contradictory evidence, risks, and missing information.

### AIValidationStatus

Displays valid, rejected, safety-blocked, stale, or unavailable.

AI components must never use language implying certainty or execution authority.

## 8. Strategy and Risk Components

- StrategyIntentCard
- RiskDecisionPanel
- RiskLimitProgress
- RiskReasonList
- DrawdownGauge
- ExposureGauge
- HaltBanner
- PolicyVersionLink
- RequestedVsApproved

## 9. Paper Trading Components

- PaperTradingBanner
- PortfolioSummary
- PositionTable
- OrderTable
- FillTable
- LedgerTable
- FeeSummary
- PnLSummary
- EquityCurve
- BenchmarkComparison
- CancelOrderDialog

Every component must visibly label data as simulated.

## 10. Backtest Components

- BacktestBuilder
- DateRangeSelector
- AssumptionSummary
- BacktestStatus
- MetricGrid
- DrawdownChart
- TradeDistribution
- BenchmarkChart
- WarningPanel
- ReproducibilityPanel
- ExportMenu

## 11. Experiment Components

- ExperimentStatus
- ExperimentPreflight
- FrozenConfigSummary
- CycleTimeline
- DailyStatusSummary
- PauseExperimentDialog
- HaltExperimentDialog
- CompletionReport

## 12. Audit Components

- AuditTimeline
- AuditEventCard
- CorrelationLink
- EntityLineage
- ActorBadge
- ReasonCode
- RawMetadataDisclosure

Sensitive metadata is redacted before rendering.

## 13. Table Standards

Reusable tables must support:

- accessible headers;
- sorting;
- pagination;
- column visibility;
- loading and empty states;
- responsive alternatives;
- CSV export where authorized;
- decimal alignment;
- timezone display configuration.

## 14. Form Standards

All forms must:

- use schema-based validation;
- show server and client validation coherently;
- preserve user input after safe errors;
- display units and limits;
- disable duplicate submission;
- support keyboard operation;
- generate audit context for privileged changes.

## 15. Storybook and Documentation

Each reusable component should include:

- default story;
- interactive states;
- loading, empty, error, and disabled stories;
- light and dark theme;
- mobile viewport where relevant;
- accessibility checks;
- usage guidance and prohibited use.

## 16. Testing

Required tests:

- component behavior;
- keyboard interaction;
- accessibility;
- semantic status output;
- financial formatting;
- secret-redaction boundaries;
- critical dialog confirmations;
- visual regression for core components.

## 17. Definition of Done

A component is complete when:

- API and states are typed;
- tokens are used;
- accessibility checks pass;
- Storybook documentation exists;
- tests cover key behavior;
- responsive behavior is verified;
- product copy follows brand rules;
- no domain safety rule is implemented only in the browser.

## 18. Related Documents

- `DESIGN_SYSTEM.md`
- `UI_UX_GUIDELINES.md`
- `INFORMATION_ARCHITECTURE.md`
- `USER_JOURNEYS.md`
- `NAMING_CONVENTIONS.md`
