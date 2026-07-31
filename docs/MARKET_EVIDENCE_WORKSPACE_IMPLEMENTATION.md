# Market Evidence and Charting Workspace Implementation Specification

Last reviewed: 2026-07-31  
Status: Sprint 6 authoritative market-evidence implementation specification

## 1. Purpose

This document defines the implementation contract for the Market Evidence workspace of The Daily Roast AI.

The workspace provides a traceable, accessible, and reproducible view of finalized market candles, versioned indicators, data-quality events, snapshot lineage, and comparisons between research cycles. It is an evidence inspection tool, not a real-time trading terminal and not an execution interface.

The workspace must make source time, finalization state, data gaps, repairs, indicator parameters, snapshot identity, and uncertainty visible. It must never present incomplete candles as finalized evidence or allow chart appearance to override persisted source truth.

## 2. Scope

Sprint 6 covers:

- the Market Evidence route and navigation;
- versioned market-evidence read models;
- finalized OHLCV visualization;
- indicator overlays and panels;
- snapshot and cycle comparison;
- data-quality annotations;
- evidence tables and accessible chart alternatives;
- zoom, pan, range selection, and crosshair behavior;
- evidence export and provenance metadata;
- responsive and accessible chart behavior;
- frontend performance limits;
- privacy, security, observability, and testing requirements.

Sprint 6 does not implement ingestion, candle finalization, gap repair, indicator calculation, strategy evaluation, risk evaluation, paper execution, or live market streaming. Those remain backend domain responsibilities.

## 3. User Outcomes

A user should be able to answer:

1. Which finalized candles and source snapshot support a selected roast?
2. Are there gaps, repairs, stale intervals, or provider problems in the evidence?
3. Which indicators were calculated, with which parameters and feature-set version?
4. How did the current cycle differ from a prior cycle or selected comparison window?
5. Which data points supported deterministic strategy and risk decisions?
6. Can the evidence be reviewed without relying only on a visual chart?
7. Can an exported evidence package be traced back to immutable source records?

## 4. Canonical Routes

```text
/market-evidence
/market-evidence/:snapshotId
```

Optional query parameters may represent symbol, interval, range, comparison snapshot, and visible indicator set when these values are validated and URL-safe.

The route must be reachable from:

- primary application navigation;
- Today’s Roast market snapshot section;
- decision-lineage links;
- cycle and snapshot detail views.

The route is read-only in Sprint 6.

## 5. Information Architecture

The workspace is ordered as follows:

1. safety, freshness, and data-integrity banners;
2. page header and evidence identity;
3. symbol, interval, range, and comparison controls;
4. primary finalized-candle chart;
5. indicator panels and overlays;
6. selected-point evidence inspector;
7. data-quality event timeline;
8. accessible evidence table;
9. snapshot metadata and lineage;
10. export, methodology, limitations, and disclaimer context.

Critical data-quality or integrity warnings must precede chart interpretation.

## 6. Market Evidence Read Model

Recommended endpoints:

```http
GET /api/v1/market-evidence/snapshots/{snapshot_id}
GET /api/v1/market-evidence/snapshots/{snapshot_id}/series
GET /api/v1/market-evidence/snapshots/{snapshot_id}/quality-events
GET /api/v1/market-evidence/snapshots/{snapshot_id}/export
```

Recommended top-level contract:

```ts
interface MarketEvidenceReadModel {
  schemaVersion: string;
  snapshot: MarketSnapshotSummary;
  series: FinalizedCandleSeries;
  indicators: IndicatorSeries[];
  qualityEvents: DataQualityEventSummary[];
  comparison: SnapshotComparisonSummary | null;
  lineage: MarketEvidenceLineage;
  limitations: LimitationSummary[];
  links: MarketEvidenceLinks;
}
```

The server must provide display-ready decimal-safe values, explicit units, series metadata, indicator parameters, and version identifiers. The frontend may transform coordinates for rendering but must not recalculate source prices, volumes, indicators, returns, gaps, repairs, or quality classifications.

## 7. Snapshot Identity

Required snapshot fields:

- immutable snapshot ID;
- market symbol and normalized asset identifiers;
- base and quote assets;
- interval;
- source provider;
- requested and covered time range;
- finalized-through timestamp;
- ingestion and validation timestamps;
- row count;
- source timezone and canonical UTC policy;
- snapshot schema version;
- feature-set version;
- checksum or content fingerprint;
- quality status;
- supersession status;
- related cycle IDs.

A superseded snapshot may be inspected but must be labeled. It must not silently replace or rewrite historical cycle evidence.

## 8. Finalized Candle Contract

Each candle must include:

- immutable or stable record identifier;
- open time and close time in UTC;
- open, high, low, and close values;
- base and quote volume where available;
- trade count where available;
- finalized state;
- source status;
- repair or backfill metadata;
- quality flags;
- source snapshot ID.

Rules:

- only finalized candles may be represented as final evidence;
- incomplete candles must be omitted or explicitly segregated;
- decimal values must remain decimal-safe;
- timestamps must be monotonic for a valid series;
- duplicate intervals are integrity failures unless an explicit resolution record exists;
- missing intervals must be represented through quality metadata rather than visually compressed away;
- repaired values must remain distinguishable from originally ingested values.

## 9. Primary Chart Contract

The primary chart should support:

- candlestick or approved OHLC rendering;
- volume display;
- deterministic visible range;
- keyboard-reachable range controls;
- pointer and keyboard point inspection;
- zoom and pan within bounded limits;
- reset-to-evidence-range action;
- finalized-through marker;
- gap and repair markers;
- comparison markers where approved;
- textual summary of the visible range.

The chart must not:

- interpolate missing candles as observed data;
- imply tick-level precision that is not present;
- hide gaps through continuous line rendering;
- use animation that changes perceived values;
- show live flashing prices;
- contain buy, sell, or order-entry controls;
- use color as the only direction or quality encoding.

## 10. Indicator Contract

Supported indicators are determined by the persisted feature set, not by arbitrary frontend calculations.

Every indicator series must expose:

- canonical name;
- display name;
- parameter values;
- feature-set version;
- source fields;
- output scale and unit;
- warm-up period;
- null or unavailable rules;
- calculation timestamp;
- evidence references.

The UI may group indicators into trend, momentum, volatility, and volume families. It must preserve parameter visibility and must not compare indicators with incompatible scales on one unlabeled axis.

## 11. Selected-Point Evidence Inspector

Selecting a candle or timestamp should expose:

- UTC and local display time;
- OHLCV values;
- quality flags;
- repair metadata;
- indicator values at that point;
- relevant strategy evidence references;
- relevant risk evidence references;
- related cycle IDs;
- source record identifiers.

The inspector must be keyboard operable and must not exist only as a hover tooltip.

## 12. Data-Quality Event Model

Supported quality-event categories include:

- missing interval;
- duplicate interval;
- out-of-order record;
- invalid OHLC relationship;
- invalid or negative volume;
- provider timeout or throttle;
- delayed finalization;
- gap repair requested;
- gap repair completed;
- repair failed;
- checksum mismatch;
- stale snapshot;
- schema mismatch;
- superseded snapshot;
- unresolved integrity failure.

Each event must include severity, category, affected interval or range, detection time, resolution state, source, impact, and evidence link.

Critical unresolved events must be shown before ordinary chart interpretation.

## 13. Snapshot Comparison

The workspace may compare two compatible snapshots or cycles.

Compatibility requires:

- the same normalized market;
- the same interval;
- an overlapping time range;
- supported schema and feature-set compatibility;
- explicit handling of different quality states.

Comparison may show:

- changed or newly available candles;
- repaired intervals;
- changed feature outputs caused by version differences;
- changed quality classifications;
- changed finalized-through time;
- source or schema differences.

The comparison must not suggest that a historical immutable snapshot changed. It must explain whether the difference comes from range extension, repair, provider correction, schema migration, or feature-version change.

## 14. Accessible Evidence Table

Every charted series must have a non-visual alternative.

The evidence table must support:

- semantic headers and caption;
- UTC time;
- OHLCV values;
- selected indicator columns;
- quality and repair status;
- cursor-based pagination or bounded windowing;
- export of the selected evidence range;
- keyboard navigation without implementing an inaccessible spreadsheet clone.

Column visibility changes must not remove access to critical quality fields.

## 15. Range and Filter Controls

Controls may include:

- symbol;
- interval;
- predefined range;
- custom bounded range;
- comparison snapshot;
- indicator visibility;
- quality-event visibility.

Rules:

- options are server-approved;
- unsupported symbols or intervals fail safely;
- selected state is URL-stable where useful;
- changing controls must not mutate source evidence;
- historical snapshot selection remains stable during background refetch;
- large-range requests must be bounded to protect browser and API reliability.

## 16. Export Contract

Supported export formats may include CSV and a structured JSON evidence package.

Every export must include:

- export schema version;
- snapshot ID and checksum;
- market and interval;
- covered range;
- finalized-through timestamp;
- feature-set version;
- quality-event summary;
- generation timestamp;
- source and limitation metadata.

Exports must be generated from authoritative server-side records. The UI must not create an unofficial export that omits provenance or quality information.

## 17. Responsive Behavior

Desktop may use chart, inspector, and diagnostics in a multi-column layout. Mobile must preserve evidence order and access.

Requirements:

- critical warnings remain first;
- chart controls remain reachable without horizontal page scrolling;
- the chart has a minimum useful height without obscuring other content;
- the selected-point inspector becomes an inline region or drawer with correct focus behavior;
- the evidence table provides a stacked or detail alternative;
- labels do not truncate into ambiguity;
- no evidence is hover-only;
- orientation changes preserve selected range and point when practical.

## 18. Accessibility Requirements

The workspace targets WCAG 2.2 AA where practical.

Required behavior:

- logical headings and landmarks;
- visible focus;
- keyboard-accessible controls;
- textual chart summaries;
- non-visual evidence table;
- patterns or labels in addition to color;
- reduced-motion support;
- announced critical quality-state changes;
- preserved focus during range and snapshot changes;
- reflow at 200% and relevant cases at 400% zoom;
- large pointer targets for chart controls where practical.

Canvas or SVG rendering must not be the sole semantic representation of the evidence.

## 19. Performance and Data Volume

The workspace must use bounded data windows.

Requirements:

- server-side range limits;
- deterministic downsampling only when explicitly identified;
- no downsampling for exported evidence unless the export says so;
- lazy loading of non-critical panels;
- request cancellation for obsolete ranges;
- stable memoization of render-ready series;
- no unbounded DOM row rendering;
- browser memory and render-budget tests;
- visible notice when a display representation is sampled.

Performance optimization must never alter authoritative values or hide integrity events.

## 20. Frontend Data Fetching

The approved frontend data layer should provide:

- stable query keys by snapshot, range, comparison, and indicator set;
- bounded retries;
- no retries for schema or integrity failures;
- cancellation of obsolete requests;
- stale-cache labeling;
- immutable historical snapshot caching where safe;
- explicit loading for chart and table ranges;
- sanitized error mapping.

## 21. Security and Privacy

The workspace must not expose:

- private exchange credentials;
- account secrets;
- private order endpoints;
- internal stack traces or SQL;
- unsanitized provider payloads;
- hidden live-execution controls;
- unrestricted arbitrary file export paths;
- browser-calculated authorization decisions.

All exports and endpoints remain subject to server authorization and RLS.

## 22. Observability

Required safe telemetry includes:

- evidence endpoint latency and status;
- range size and response row count;
- chart render duration;
- schema mismatch count;
- quality-event count by safe category;
- export request status;
- stale-cache presentation count;
- client build version;
- approved correlation identifiers.

Telemetry must not include credentials, full provider payloads, or unnecessarily detailed private financial context.

## 23. Testing Strategy

### Contract Tests

Validate schema version, decimal serialization, timestamp ordering, candle finalization, indicator parameters, quality events, and export metadata.

### Domain Integration Tests

Validate snapshot lookup, immutable historical evidence, repaired interval representation, compatibility checks, and lineage links.

### Component and Route Tests

Validate controls, URL state, selected-point inspection, error mapping, accessible tables, and historical stability.

### Accessibility Tests

Validate keyboard chart controls, focus, text alternatives, table semantics, announcements, contrast, zoom, and reduced motion.

### Visual Regression

Capture light and dark themes, desktop and mobile, complete and gapped series, repaired data, stale snapshots, comparison mode, and critical integrity states.

### Performance Tests

Validate bounded requests, large supported ranges, cancellation, memory limits, render duration, and table virtualization behavior.

### Export Tests

Validate provenance, checksum, schema version, quality metadata, authorization, and deterministic output.

## 24. Acceptance Criteria

Sprint 6 documentation is accepted when:

1. market-evidence routes and read models are explicit;
2. finalized candles and incomplete data are clearly separated;
3. indicators expose parameters and versions;
4. gaps, repairs, stale state, and integrity failures are visible;
5. chart data has an accessible non-visual alternative;
6. comparison semantics preserve immutable history;
7. exports include provenance and quality metadata;
8. frontend calculations cannot replace authoritative market or indicator outputs;
9. performance limits are bounded and testable;
10. no live execution or private exchange access is introduced.

## 25. Definition of Done

The Sprint 6 specification is complete when:

- this document is committed;
- a measurable `SPRINT_6_TASKS.md` is committed;
- terminology matches architecture, data, API, UX, security, and Sprint 5 documents;
- chart, table, comparison, quality, export, accessibility, and testing contracts are explicit;
- both commits are fetched and verified.

## 26. Next Sprint Boundary

Sprint 7 defines the **Strategy and Risk Decision Workspace**, including deterministic strategy evidence, risk-policy evaluation, reason codes, exposure constraints, rejected and reduced intents, decision lineage, and policy-version comparison. It remains read-only and must not introduce execution authority.