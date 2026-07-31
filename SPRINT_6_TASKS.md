# Sprint 6 Tasks — Market Evidence and Charting Workspace

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a read-only, evidence-first workspace for finalized market candles, indicators, data-quality events, snapshot comparison, accessible inspection, and provenance-preserving export.

## Authoritative References

- `docs/MARKET_EVIDENCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/TODAYS_ROAST_DASHBOARD_IMPLEMENTATION.md`
- `docs/CORE_COMPONENT_LIBRARY_IMPLEMENTATION.md`
- `docs/API_SPECIFICATION.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `AGENTS.md`

## S6.1 Define Versioned Market-Evidence Schemas

### Objective

Create explicit API schemas for snapshots, finalized candles, indicators, quality events, comparison results, lineage, and export metadata.

### Work

- define `MarketEvidenceReadModel` and nested schemas;
- use UTC timestamps and decimal-safe serialization;
- define quality, repair, finalization, supersession, and compatibility enums;
- include source IDs, checksums, versions, parameters, and evidence links;
- document nullability and unavailable states;
- publish schemas in OpenAPI.

### Acceptance Criteria

- every monetary or price value has explicit serialization and unit context;
- every series identifies snapshot and feature-set version;
- incomplete candles cannot satisfy finalized-candle schemas;
- reason codes and quality states are machine-readable;
- schema compatibility tests pass.

## S6.2 Implement Snapshot Metadata Endpoint

### Objective

Expose immutable snapshot identity, coverage, quality, lineage, and related-cycle metadata.

### Work

- implement `GET /api/v1/market-evidence/snapshots/{snapshot_id}`;
- enforce authorization and RLS;
- return supersession without rewriting history;
- map not-found, unauthorized, schema, and integrity errors safely;
- add correlation and latency telemetry.

### Acceptance Criteria

- snapshot lookup is deterministic by immutable ID;
- checksum, finalized-through time, versions, and quality state are returned;
- historical snapshots remain inspectable;
- sensitive internals are not leaked;
- integration tests pass.

## S6.3 Implement Bounded Series Endpoint

### Objective

Serve finalized OHLCV and persisted indicators for an approved bounded range.

### Work

- implement series endpoint with validated range parameters;
- enforce row and time-span limits;
- return only finalized candles as finalized evidence;
- include gaps, repairs, source state, and indicator metadata;
- support request cancellation and stable pagination or windowing;
- reject unsupported symbols, intervals, and ranges.

### Acceptance Criteria

- output timestamps are ordered and unique;
- gaps are represented rather than compressed away;
- repaired records remain labeled;
- frontend calculation of indicators is unnecessary;
- limit and abuse tests pass.

## S6.4 Implement Data-Quality Event Endpoint

### Objective

Expose interpretation-affecting quality events separately from ordinary series data.

### Work

- implement quality-event retrieval by snapshot and range;
- support missing, duplicate, invalid, delayed, repair, stale, checksum, and schema categories;
- include severity, impact, resolution, source, and links;
- preserve unresolved critical events;
- sanitize provider failure details.

### Acceptance Criteria

- critical unresolved events are identifiable and ordered;
- resolution history is traceable;
- no raw provider secret or internal stack trace appears;
- event category contracts are tested;
- missing events and failed retrieval remain distinct states.

## S6.5 Add Market Evidence Routes

### Objective

Create canonical latest-selection and snapshot-specific routes in the application shell.

### Work

- implement `/market-evidence`;
- implement `/market-evidence/:snapshotId`;
- add primary navigation entry;
- link from Today’s Roast and lineage resources;
- preserve snapshot and safe query state on refresh;
- add route-level error boundaries.

### Acceptance Criteria

- routes are directly addressable and keyboard reachable;
- historical snapshots are not silently replaced;
- invalid query state fails safely;
- route metadata is correct;
- no execution controls are introduced.

## S6.6 Implement Evidence Identity Header

### Objective

Present market, interval, snapshot, finalization, freshness, quality, and version context before chart interpretation.

### Work

- render symbol, assets, interval, range, source, checksum reference, and IDs;
- render `EnvironmentBadge`, `SimulationBadge`, and `FreshnessIndicator`;
- show finalized-through and supersession state;
- show snapshot and feature-set versions;
- add links to related cycles and methodology.

### Acceptance Criteria

- critical identity and state remain visible at all widths;
- UTC value is accessible;
- stale, superseded, or degraded state cannot appear ordinary;
- IDs remain traceable;
- accessibility and responsive tests pass.

## S6.7 Implement Finalized Candle Chart

### Objective

Render bounded finalized OHLCV evidence without interpolation or implied live precision.

### Work

- implement candlestick or approved OHLC rendering;
- add volume, visible-range summary, finalization marker, gap markers, and repair markers;
- add bounded zoom, pan, reset, pointer, and keyboard inspection;
- provide loading and failure states without fabricated values;
- prohibit live flashing and execution UI.

### Acceptance Criteria

- missing intervals remain visually evident;
- incomplete candles are not presented as final;
- direction and quality do not rely only on color;
- keyboard point inspection works;
- chart visual and interaction tests pass.

## S6.8 Implement Indicator Panels

### Objective

Display persisted indicators with explicit parameters, units, scales, warm-up rules, and versions.

### Work

- render approved trend, momentum, volatility, and volume indicator families;
- support server-approved visibility controls;
- label parameters and feature version;
- preserve null warm-up values;
- prevent incompatible unlabeled axes;
- link indicator points to evidence.

### Acceptance Criteria

- no indicator is recalculated in the browser;
- parameters and scale are visible;
- null values are not invented;
- incompatible scales remain separated;
- contract and visual tests pass.

## S6.9 Implement Selected-Point Inspector

### Objective

Provide a persistent, accessible alternative to hover-only chart tooltips.

### Work

- show UTC/local time, OHLCV, quality flags, repair metadata, and indicators;
- show related strategy, risk, cycle, and source references;
- support keyboard point navigation;
- preserve selection during compatible layout changes;
- define no-selection and unavailable states.

### Acceptance Criteria

- all chart point details are keyboard accessible;
- hover is not required;
- source identifiers are traceable;
- quality and repair state remain visible;
- focus behavior is tested.

## S6.10 Implement Data-Quality Timeline

### Objective

Present quality events in chronological and severity-aware form.

### Work

- render critical events before ordinary diagnostics;
- support range filtering and evidence links;
- show affected intervals, impact, status, and resolution;
- distinguish detection from repair completion;
- prevent critical unresolved events from being collapsed by default.

### Acceptance Criteria

- unresolved integrity failures are prominent;
- timeline chronology is deterministic;
- mobile and screen-reader ordering is preserved;
- empty and unavailable states differ;
- hostile diagnostic content is sanitized.

## S6.11 Implement Accessible Evidence Table

### Objective

Provide a semantic non-visual alternative for all charted evidence.

### Work

- render UTC, OHLCV, selected indicators, quality, and repair columns;
- add semantic headers, caption, and bounded pagination or windowing;
- provide accessible row detail for narrow screens;
- keep critical quality fields available;
- support selected-range export initiation.

### Acceptance Criteria

- table relationships are programmatically available;
- keyboard use does not require spreadsheet behavior;
- narrow layouts preserve access to all critical fields;
- row counts remain bounded;
- accessibility tests pass.

## S6.12 Implement Snapshot Comparison

### Objective

Compare compatible snapshots or cycles without implying mutation of immutable history.

### Work

- validate symbol, interval, range, schema, and feature compatibility;
- show range extension, repair, correction, version, and quality differences;
- label incompatible comparisons;
- link each difference to source evidence;
- preserve both snapshot identities.

### Acceptance Criteria

- incompatible comparisons fail explicitly;
- historical snapshots remain immutable in language and behavior;
- the cause of each difference is classified;
- changed feature outputs identify version differences;
- deterministic comparison tests pass.

## S6.13 Implement Provenance-Preserving Export

### Objective

Export evidence with identity, quality, version, and limitation metadata.

### Work

- implement CSV and structured JSON export where approved;
- generate exports server-side;
- include snapshot ID, checksum, range, finalization, versions, quality summary, and generation time;
- authorize export requests;
- record safe export telemetry.

### Acceptance Criteria

- exports are deterministic for the same source and options;
- provenance cannot be omitted;
- exports do not contain secrets;
- authorization and range limits apply;
- export contract tests pass.

## S6.14 Add Explicit Workspace State Handling

### Objective

Define deterministic rendering for all market-evidence states.

### Work

- implement loading, no snapshot, not found, unauthorized, stale, degraded, superseded, schema mismatch, integrity failure, backend unavailable, and export failure states;
- define retry eligibility;
- label cached stale evidence;
- preserve prior safe evidence where policy allows;
- prevent infinite retries.

### Acceptance Criteria

- integrity failure is not rendered as emptiness;
- loading fabricates no values;
- stale cache is labeled;
- non-retryable failures do not loop;
- state-matrix tests pass.

## S6.15 Add Responsive and Accessibility Verification

### Objective

Ensure charts, controls, inspectors, tables, and diagnostics remain usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, and orientation changes;
- verify 200% and relevant 400% zoom;
- test keyboard chart controls and focus preservation;
- test textual summaries and table alternatives;
- test reduced motion, contrast, touch targets, and long labels;
- record manual screen-reader spot checks.

### Acceptance Criteria

- no evidence is hover-only;
- critical content is not clipped;
- chart rendering is not the sole semantic source;
- no critical automated accessibility violation remains;
- manual review evidence is recorded.

## S6.16 Add Performance and Reliability Controls

### Objective

Protect browser and API reliability while preserving evidence integrity.

### Work

- enforce server range limits;
- add request cancellation;
- add bounded caching and rendering;
- virtualize long tables where needed;
- identify any sampled display representation;
- measure memory, render duration, and request volume.

### Acceptance Criteria

- unsupported large ranges fail safely;
- optimization never changes authoritative values;
- sampling is explicit and never used silently in export;
- browser budget tests pass;
- request storms are prevented.

## S6.17 Add Observability and Privacy Controls

### Objective

Measure workspace reliability without collecting secrets or excessive private detail.

### Work

- instrument endpoint latency, rows, chart render duration, quality categories, schema mismatch, stale cache, and export status;
- propagate approved correlation IDs;
- add prohibited-field telemetry tests;
- document retention and access;
- ensure telemetry failure is non-blocking.

### Acceptance Criteria

- no credentials or raw provider payloads are logged;
- metrics use safe categories;
- client and backend failures can be correlated where approved;
- telemetry tests pass;
- privacy documentation is updated.

## S6.18 Add Contract, Integration, E2E, Visual, and Export Tests

### Objective

Make evidence correctness and fail-closed behavior release-blocking.

### Work

- add API schema and integration tests;
- add complete, gapped, repaired, stale, superseded, and integrity-failure fixtures;
- add route and control E2E tests;
- add keyboard and accessibility tests;
- add visual baselines for themes and viewports;
- add deterministic export tests;
- add performance-limit tests.

### Acceptance Criteria

- the same source records produce the same series and export;
- gaps and repairs remain visible;
- historical snapshot selection is stable;
- incompatible comparisons fail safely;
- critical tests pass in CI;
- visual changes require review.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| API contracts | OpenAPI schemas, decimal and timestamp tests |
| Evidence integrity | Finalization, gap, duplicate, repair, checksum and lineage tests |
| Charting | Interaction, keyboard, visual and bounded-range tests |
| Accessibility | Text alternatives, evidence table, zoom and manual review |
| Comparison | Compatibility and immutable-history tests |
| Export | Provenance, authorization and deterministic-output tests |
| Reliability | Cancellation, range limit, memory and render-budget tests |
| Security and privacy | RLS, sanitization, secret scan and telemetry-field tests |

## Sprint Exit Gate

Sprint 6 is complete only when:

- S6.1 through S6.18 are implemented and verified;
- only finalized candles receive finalized presentation;
- gaps, repairs, stale state, supersession, and integrity failures remain visible;
- indicators are persisted, versioned, and parameterized;
- every visual series has an accessible non-visual alternative;
- historical evidence remains immutable;
- comparison and export preserve provenance;
- accessibility, responsive, performance, security, privacy, contract, integration, E2E, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commit is fetched and verified.

## Next Sprint

Sprint 7 defines and implements the Strategy and Risk Decision Workspace, preserving the separation between deterministic strategy intent, risk-policy evaluation, permitted paper action, and actual simulated execution.