# Sprint 13 Tasks — Product Shell, Onboarding, Help, Trust Center, Global Search, Notifications, Internationalization, and Cross-Workspace Experience

Last reviewed: 2026-07-31  
Status: Ready for implementation

## Sprint Goal

Implement a coherent, accessible, bilingual product shell that keeps workspace, environment, simulation, freshness, risk, reconciliation, incident, and governance state globally visible; connects every evidence workspace through authorized navigation and search; teaches safe interpretation through onboarding and contextual help; and delivers privacy-minimized notifications and Trust Center content without adding financial or operational authority.

## Authoritative References

- `docs/PRODUCT_SHELL_ONBOARDING_TRUST_I18N_WORKSPACE_IMPLEMENTATION.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/TODAYS_ROAST_DASHBOARD_IMPLEMENTATION.md`
- `docs/MARKET_EVIDENCE_WORKSPACE_IMPLEMENTATION.md`
- `docs/GEMINI_ANALYSIS_VALIDATION_WORKSPACE_IMPLEMENTATION.md`
- `docs/STRATEGY_RISK_WORKSPACE_IMPLEMENTATION.md`
- `docs/PAPER_PORTFOLIO_EXECUTION_WORKSPACE_IMPLEMENTATION.md`
- `docs/BACKTEST_EXPERIMENT_COMPARISON_WORKSPACE_IMPLEMENTATION.md`
- `docs/EXPERIMENT_OPERATIONS_AUDIT_WORKSPACE_IMPLEMENTATION.md`
- `docs/AUTH_CONFIGURATION_SECURITY_RELEASE_WORKSPACE_IMPLEMENTATION.md`
- `docs/SECURITY.md`
- `docs/OBSERVABILITY.md`
- `docs/API_SPECIFICATION.md`
- `AGENTS.md`

## S13.1 Define Versioned Product Shell Schemas

### Objective

Create explicit contracts for product identity, account, workspace, environment, mode, global status, navigation, recent items, saved views, notifications, preferences, help, trust, permissions, diagnostics, and links.

### Work

- define `ProductShellReadModel` and nested schemas;
- define search, onboarding, glossary, notice, notification, saved-view, trust, and support-package models;
- define canonical route, status, message, locale, timezone, and content keys;
- define compatibility, stale, partial, unavailable, redaction, and authorization rules;
- publish schemas in OpenAPI;
- generate frontend types.

### Acceptance Criteria

- global safety state is server-provided;
- canonical IDs are locale-independent;
- notification and search contracts contain no secret-bearing payload fields;
- compatibility rules are explicit;
- contract tests pass.

## S13.2 Implement Product Shell Endpoint

### Objective

Return the complete authorized shell context in one bounded projection.

### Work

- implement `GET /api/v1/shell` or the approved aggregate endpoint;
- return product, account, workspace, environment, mode, global status, navigation, recent items, saved views, notification summary, preferences, help context, trust summary, permissions, diagnostics, and links;
- enforce authorization and RLS;
- calculate priority and critical status server-side;
- add safe caching and telemetry.

### Acceptance Criteria

- critical status is complete and correctly prioritized;
- unauthorized navigation and resources are absent;
- shell response does not expose secrets or private payloads;
- stale shell state is explicit;
- integration tests pass.

## S13.3 Implement Protected Application Shell

### Objective

Create the authenticated shell regions and consistent route layout.

### Work

- implement skip link, product identity, workspace/environment context, persistent mode/status, primary navigation, contextual navigation, search, notifications, help, account menu, breadcrumbs, notices, main content, optional inspector, and footer;
- preserve semantic landmark order;
- support route-level suspense and errors;
- avoid layout shifts that hide critical status;
- test all supported viewports.

### Acceptance Criteria

- shell landmarks are logical;
- critical status remains visible across routes;
- focus moves correctly after navigation;
- no workspace route implements a conflicting shell;
- accessibility and visual tests pass.

## S13.4 Implement Public Demo Shell

### Objective

Expose approved public read-only content without leaking authenticated state.

### Work

- implement a separate public shell;
- render public-demo, simulation, delayed/sample-data, and non-advice labels;
- expose only approved routes and data;
- remove workspace identity, membership, private incidents, security findings, and commands;
- add sign-in entry and Trust Center links;
- verify public assets contain no secrets.

### Acceptance Criteria

- public and authenticated modes cannot be confused;
- unauthorized resource existence is not leaked;
- all data is clearly sample, delayed, or approved public evidence;
- no privileged command is present;
- public E2E and security tests pass.

## S13.5 Implement Official Product Identity and Brand Tokens

### Objective

Use the official product name, tagline, domains, and non-promotional voice consistently.

### Work

- define product identity constants and content keys;
- replace user-facing legacy repository names;
- verify official domains and environment labels;
- define brand voice and prohibited financial language tests;
- expose product and client build version safely.

### Acceptance Criteria

- all user-facing routes use The Daily Roast AI;
- official tagline is correct;
- technical repository name appears only in developer contexts;
- prohibited hype and guarantee language fails content tests;
- brand tests pass.

## S13.6 Implement Global Mode and Safety Header

### Objective

Keep environment, simulation, live-trading-disabled, halt, reconciliation, freshness, incident, and blocker state persistent.

### Work

- render environment, product mode, paper/simulation state, live-trading-disabled state, workspace halt, reconciliation, market freshness, critical incident/blocker, data timestamp, and status timestamp;
- apply canonical priority hierarchy;
- link each state to evidence;
- preserve status on mobile and zoom;
- announce material changes accessibly.

### Acceptance Criteria

- critical failures outrank results;
- positive performance cannot suppress safety state;
- every state has text and evidence link;
- live-trading-disabled remains explicit;
- state hierarchy tests pass.

## S13.7 Implement Canonical Navigation Taxonomy

### Objective

Provide stable primary navigation across all evidence workspaces.

### Work

- define route IDs for Today’s Roast, Market Evidence, Gemini Analysis, Decisions and Risk, Paper Portfolio, Backtests, Experiments, Audit, Governance, Help, and Trust;
- map labels through localization keys;
- implement active-route and parent-route state;
- preserve stable ordering and direct URLs;
- add desktop and mobile variants.

### Acceptance Criteria

- labels are concise and semantically stable;
- route identity does not depend on translated text;
- all authorized primary routes are reachable by keyboard;
- no duplicated or orphaned primary route exists;
- navigation tests pass.

## S13.8 Implement Role-Aware Navigation and Route Guards

### Objective

Reflect server permissions without relying on frontend authorization.

### Work

- consume server-provided route and command permissions;
- render viewer, operator, and owner navigation variants;
- handle denied and not-enabled routes safely;
- verify direct navigation remains server-protected;
- clear cached protected data on permission change;
- audit privileged denied attempts server-side.

### Acceptance Criteria

- hidden links do not replace backend authorization;
- stale role state cannot expose protected content;
- permission changes take effect safely;
- denied routes reveal no private resource existence;
- authorization tests pass.

## S13.9 Implement Workspace Switcher

### Objective

Switch authorized workspaces while preserving clear context and clearing scoped cache.

### Work

- render workspace name, ID, effective role, mode, experiment, halt/blocker, last access, and archived state;
- support keyboard search and selection;
- clear workspace-scoped caches, recent request state, and open inspectors;
- preserve safe global preferences;
- route to an authorized workspace landing page.

### Acceptance Criteria

- old workspace data cannot flash after switch;
- archived and blocked states are explicit;
- effective role is visible;
- unauthorized workspaces never appear;
- concurrency and E2E tests pass.

## S13.10 Implement Environment Context and Approved Switching

### Objective

Keep environment boundaries clear and prevent cross-environment state reuse.

### Work

- render local, CI, public demo, paper experiment, staging, and production-research identity where applicable;
- show purpose, domain, mode, and live-trading-disabled state;
- require separate authentication when policy requires;
- clear tokens and caches according to environment boundary;
- confirm safe navigation when unsaved preferences exist.

### Acceptance Criteria

- environment identity is never hidden;
- credentials and caches are not reused unsafely;
- production research is not presented as live trading;
- unsupported switching is unavailable;
- environment tests pass.

## S13.11 Implement Breadcrumbs and Contextual Navigation

### Objective

Expose resource hierarchy and related views consistently.

### Work

- define breadcrumb builders from canonical route/resource metadata;
- preserve workspace, parent resource, and current resource context;
- disambiguate repeated names with safe IDs or type labels;
- provide contextual tabs and sibling links;
- handle archived or unavailable ancestors.

### Acceptance Criteria

- breadcrumbs represent hierarchy rather than browser history;
- all links remain authorization-aware;
- current page is not a redundant link;
- narrow layouts retain essential context;
- component tests pass.

## S13.12 Implement Cross-Workspace Lineage Navigator

### Objective

Allow users to trace evidence across market, AI, strategy, risk, execution, accounting, experiments, governance, and audit.

### Work

- define typed node and relationship contracts;
- render ordered chain and graph alternatives;
- include status, timestamp, relationship, source, target, and authorization state;
- support deep links and backtracking;
- classify missing required lineage;
- avoid graph-only meaning.

### Acceptance Criteria

- one fill can be traced to source candles and approvals;
- direction and relationship meaning are explicit;
- unauthorized nodes do not leak existence;
- required missing lineage is critical;
- lineage E2E and accessibility tests pass.

## S13.13 Implement Global Search Endpoint

### Objective

Search authorized metadata and approved content across the product.

### Work

- implement `GET /api/v1/search` with bounded query, resource filters, workspace scope, cursor pagination, and safe sort;
- index approved metadata for workspaces, snapshots, analyses, decisions, risk, orders, fills, ledger IDs, backtests, experiments, cycles, incidents, halts, audit, configurations, releases, help, and glossary;
- enforce authorization and RLS before result creation;
- normalize exact IDs and safe text fields;
- add timing and no-existence-leak protections.

### Acceptance Criteria

- unauthorized resources never appear or influence counts;
- exact identifiers resolve deterministically;
- raw SQL/search syntax is not accepted;
- queries and results are bounded;
- API and security tests pass.

## S13.14 Implement Global Search UI

### Objective

Provide accessible grouped search with clear context and status.

### Work

- implement search input, suggestions, parsed filters, grouped results, cursor loading, empty, error, and stale states;
- show resource type, safe title, context, status, timestamp, workspace, and matched category;
- preserve query in URL where privacy policy allows;
- support keyboard navigation and announcements;
- prevent unsafe HTML rendering.

### Acceptance Criteria

- results are understandable without icons or color;
- keyboard and screen reader interaction is complete;
- no-result and unauthorized states are not conflated;
- long IDs and labels remain usable;
- accessibility and E2E tests pass.

## S13.15 Implement Safe Command Palette

### Objective

Provide fast navigation and explicit authorized actions without arbitrary commands.

### Work

- support routes, recent items, workspace switch, help, trust, saved views, and approved command launchers;
- map all entries to canonical IDs;
- require normal confirmation, recent authentication, idempotency, expected version, and audit for privileged commands;
- prohibit free-form financial or operational instructions;
- expose shortcut and scope.

### Acceptance Criteria

- palette cannot bypass command gates;
- no natural-language order or policy command is accepted;
- entries are authorization-filtered;
- focus and dismissal behavior is accessible;
- command security tests pass.

## S13.16 Implement Recent Items and Personal History

### Objective

Help users return to evidence without storing sensitive payloads.

### Work

- store or fetch resource type, ID, safe label, workspace, route, last viewed time, status, and availability;
- define client and optional server retention;
- clear revoked or unauthorized items;
- implement user-clear command;
- keep audit history independent.

### Acceptance Criteria

- recent history contains no tokens or private payloads;
- revoked resources disappear safely;
- clearing personal history does not alter audit evidence;
- history is user-scoped;
- privacy tests pass.

## S13.17 Implement Favorites and Saved Views

### Objective

Persist private route/filter/display preferences safely.

### Work

- implement saved-view create, update, apply, rename, and delete commands;
- store canonical route, approved filters, sort, columns, display options, compatibility, scope, and timestamps;
- validate bounds and authorization;
- migrate or mark incompatible views;
- prohibit authoritative calculations and secret data.

### Acceptance Criteria

- saved views are user-scoped by default;
- locale changes do not corrupt canonical filters;
- incompatible views fail safely;
- deleting a view does not affect source evidence;
- contract and E2E tests pass.

## S13.18 Implement First-Run Onboarding Endpoint and State

### Objective

Persist role-aware onboarding progress and material acknowledgements.

### Work

- define onboarding version, user/workspace/role scope, stage IDs, completion, timestamps, skip policy, acknowledgement versions, last route, compatibility, and reset state;
- implement read and progress commands;
- require explicit acknowledgement for material safety content;
- preserve version history;
- prevent onboarding from hiding critical notices.

### Acceptance Criteria

- progress is deterministic and scoped;
- material wording changes can require re-acknowledgement;
- acknowledgement is not treated as waiver;
- critical notices remain visible;
- state tests pass.

## S13.19 Implement Role-Aware Onboarding Experience

### Objective

Teach each role the product scope, evidence chain, and permitted actions.

### Work

- implement common stages for product identity, research scope, simulation, AI limits, deterministic risk, portfolio costs, backtests, experiments, privacy, and support;
- add viewer, operator, and owner modules;
- link real authorized workspaces or safe demos;
- provide completion summary and next route;
- support English and Estonian.

### Acceptance Criteria

- role content matches server permissions;
- no module implies live trading or profit guarantee;
- users can revisit completed stages;
- localization preserves safety meaning;
- usability and E2E tests pass.

## S13.20 Implement Safety Acknowledgement Content

### Objective

Make material simulation, AI, risk, backtest, schedule, and performance limitations explicit.

### Work

- create versioned acknowledgements for paper execution, no advice, no guarantee, confidence meaning, backtest limits, costs, halts, best-effort scheduling, public-demo data, and live-trading-disabled state;
- render concise summary and full details;
- record user, version, timestamp, locale, and scope;
- preserve old versions;
- prohibit coercive wording.

### Acceptance Criteria

- acknowledgements use plain, precise language;
- locale versions are semantically equivalent;
- acknowledgement does not waive safety duties;
- missing required acknowledgement blocks only the documented flow;
- content tests pass.

## S13.21 Implement Contextual Help Framework

### Objective

Provide page-specific purpose, interpretation, terms, statuses, methodology, lineage, failures, actions, runbooks, and limitations.

### Work

- define help-context IDs for every primary route;
- render non-modal and modal help variants;
- link glossary, methodology, evidence, and runbooks;
- tailor permitted-action guidance by role;
- version and localize help content;
- keep help separate from authoritative data.

### Acceptance Criteria

- every primary workspace has help coverage;
- critical content is not hover-only;
- role guidance never implies denied permission;
- help versions are traceable;
- accessibility tests pass.

## S13.22 Implement Bilingual Glossary

### Objective

Define canonical English and Estonian terminology for technical and financial concepts.

### Work

- implement glossary entry schema and routes;
- define canonical term IDs, preferred terms, definitions, categories, synonyms, prohibited synonyms, units/formulas, related concepts, source, version, and review;
- seed core terms from all workspaces;
- support search and contextual definitions;
- add semantic parity review.

### Acceptance Criteria

- all high-risk terms have approved definitions in both languages;
- ambiguous or promotional synonyms are prohibited;
- definitions link to authoritative methodology;
- term IDs remain stable across locales;
- glossary tests pass.

## S13.23 Implement Methodology Center

### Objective

Provide coherent version-linked explanations for every evidence domain.

### Work

- create methodology sections for market data, features, Gemini, strategy, risk, execution, accounting, backtests, experiments, security, privacy, and releases;
- link exact configuration and evidence routes;
- render last reviewed date and version;
- distinguish general methodology from run-specific settings;
- support English and Estonian.

### Acceptance Criteria

- general explanations do not replace actual configuration;
- stale methodology is visible;
- all claims are linked to authoritative docs;
- translation parity is reviewed;
- content tests pass.

## S13.24 Implement Trust Center

### Objective

Present approved product-scope, simulation, AI, evidence, risk, security, privacy, incident, recovery, and release information.

### Work

- implement public and authenticated sections;
- render evidence timestamp, scope, environment, status, summary, limitations, public evidence, next review, and incident/notice links;
- cover product non-goals, paper trading, provenance, AI limits, risk, freshness, performance limits, security, privacy, incidents, backups, release, and disclosure;
- redact sensitive findings;
- classify stale or unavailable evidence.

### Acceptance Criteria

- unknown evidence never appears healthy;
- public content exposes no sensitive operational detail;
- simulation and non-advice scope is clear;
- Trust Center status is evidence-backed;
- security and content tests pass.

## S13.25 Implement Product Notice Model and Banners

### Objective

Deliver scoped informational, degraded, incident, security, privacy, release, and critical notices.

### Work

- define notice type, severity, scope, audience, timing, acknowledgement, source, evidence, and route;
- render global, workspace, and page notices;
- apply canonical priority and stacking rules;
- preserve critical notices across route changes;
- support localization and accessible announcements.

### Acceptance Criteria

- critical notices cannot be obscured by informational banners;
- expired notices disappear according to server state;
- notices contain safe summaries and evidence links;
- no notice performs a domain command;
- component tests pass.

## S13.26 Implement Notification Persistence and API

### Objective

Create durable, deduplicated, authorization-aware in-app notifications.

### Work

- implement notification list, detail, read, acknowledge, and preference endpoints;
- persist recipient, workspace, event type, severity, safe content, source, timestamps, state, action route, delivery, deduplication, correlation, and localization parameters;
- enforce RLS and role scope;
- exclude secret-bearing payloads;
- use cursor pagination.

### Acceptance Criteria

- notifications survive delivery failure;
- unauthorized recipients cannot access content;
- critical source events remain traceable;
- summaries contain no secrets;
- API tests pass.

## S13.27 Implement Notification Center

### Objective

Present unread, critical, grouped, resolved, and historical notifications accessibly.

### Work

- render counts, filters, groups, source, status, timestamps, repeat count, and routes;
- support read and acknowledgement separately;
- preserve critical items until policy permits resolution;
- handle empty, loading, stale, and unavailable states;
- support keyboard and screen readers.

### Acceptance Criteria

- unread counts are deterministic;
- reading does not acknowledge or resolve automatically;
- grouped failures retain underlying event count;
- critical notifications remain visible;
- accessibility tests pass.

## S13.28 Implement Notification Deduplication and Escalation

### Objective

Reduce noise without hiding repeated critical failures.

### Work

- define stable deduplication keys and grouping windows;
- persist first/last occurrence, repeat count, source, escalation threshold, and resolution;
- link underlying audit or incident events;
- preserve separate critical occurrences where policy requires;
- test concurrent delivery.

### Acceptance Criteria

- duplicate notifications do not inflate unread counts incorrectly;
- repeated critical failures escalate visibly;
- grouping never deletes source evidence;
- resolution state is deterministic;
- concurrency tests pass.

## S13.29 Implement Notification Preferences

### Objective

Allow user control of non-critical categories and approved channels.

### Work

- implement category, digest, locale, and channel preferences;
- define immutable critical categories that cannot be fully disabled;
- apply role and policy constraints;
- record material changes;
- provide conservative defaults;
- show channel limitations.

### Acceptance Criteria

- critical safety and security notices remain enabled;
- preferences are user-scoped;
- disabled channels do not delete durable in-app records;
- privacy-sensitive destination details are minimized;
- preference tests pass.

## S13.30 Implement Support and Responsible Disclosure Entry Points

### Objective

Provide safe help, issue reporting, and security disclosure workflows.

### Work

- add contextual support routes;
- explain how to copy correlation IDs;
- provide issue category, description, affected route/resource, and optional diagnostic package;
- warn against submitting secrets;
- provide responsible security disclosure instructions;
- route incident status separately.

### Acceptance Criteria

- support flows never request API keys, passwords, tokens, or connection strings;
- security reports use the approved private channel;
- public issue content is minimized;
- correlation IDs are safe to copy;
- support tests pass.

## S13.31 Implement Redacted Diagnostic Support Package

### Objective

Export bounded client and resource diagnostics for authorized support.

### Work

- include build version, route/resource IDs, safe environment/workspace IDs, correlations, timestamps, safe errors, status summaries, browser capabilities, and redacted diagnostics;
- exclude tokens, cookies, prompts, responses, secrets, and unnecessary financial data;
- require user preview and consent;
- generate deterministic package server-side or safely client-side according to policy;
- record export event.

### Acceptance Criteria

- prohibited fields are absent;
- package scope is visible before export;
- authorization and consent are enforced;
- hashes or manifests allow integrity verification;
- export tests pass.

## S13.32 Implement Internationalization Framework

### Objective

Support canonical locale-independent product behavior with English and Estonian catalogs.

### Work

- configure `en` and `et` message catalogs;
- use canonical keys and typed parameters;
- support ICU pluralization and formatting where practical;
- prohibit translated-sentence string concatenation;
- implement fallback and missing-key diagnostics;
- persist locale preference;
- preserve language attributes.

### Acceptance Criteria

- all primary routes render in both languages;
- missing translations fall back safely;
- parameter mismatches fail tests;
- locale changes do not alter data or permissions;
- i18n tests pass.

## S13.33 Implement Domain Terminology and Translation Governance

### Objective

Preserve exact domain meaning across English and Estonian.

### Work

- define approved translations for simulation, confidence, strategy, risk, halt, stale, ledger, reconciliation, gross/net, benchmarks, roles, findings, and blockers;
- maintain prohibited misleading synonyms;
- require reviewer and version for material safety terms;
- link glossary and content keys;
- add semantic parity tests.

### Acceptance Criteria

- no translated term changes authority or risk semantics;
- analytical confidence remains non-probabilistic;
- paper results remain explicitly simulated;
- terminology changes are reviewed and audited;
- content tests pass.

## S13.34 Implement Localized Numbers, Currency, Percentages, and Ratios

### Objective

Present values according to locale without changing authoritative decimals.

### Work

- implement locale-aware separators, explicit asset/currency codes, precision policy, canonical copy values, negative-value announcements, gross/net/available/reserved/estimated labels, percentage semantics, and ratio definitions;
- preserve decimal strings internally;
- handle null and unavailable values;
- test extreme and small values;
- prohibit confidence-to-probability conversion.

### Acceptance Criteria

- display formatting never changes stored values;
- units remain explicit;
- percentage and ratio semantics are unambiguous;
- screen readers announce values correctly;
- precision tests pass.

## S13.35 Implement Localized Date, Time, Duration, and Timezone

### Objective

Present evidence and schedule times unambiguously across locales and timezones.

### Work

- implement user timezone preference;
- show accessible UTC reference;
- distinguish intended and actual times;
- supplement relative times with absolute values;
- support DST and localized duration;
- keep ISO timestamps in exports;
- test Europe/Tallinn transitions.

### Acceptance Criteria

- critical events always expose absolute time;
- timezone and DST behavior is correct;
- schedule delay meaning is preserved;
- locale switching does not change instant identity;
- date/time tests pass.

## S13.36 Implement Content Registry and Review Workflow

### Objective

Version product copy, safety language, translations, parameters, and review state.

### Work

- define content key, owner, English source, Estonian translation, status, context, parameters, review requirement, version, date, and related requirement/code;
- implement content linting and catalog completeness checks;
- require review for safety, financial, privacy, security, and legal-adjacent wording;
- archive superseded versions;
- link release gates.

### Acceptance Criteria

- material content changes are traceable;
- unreviewed safety content blocks release;
- parameter and translation drift is detected;
- superseded content remains auditable;
- registry tests pass.

## S13.37 Implement Brand Voice and Unsupported-Claim Linting

### Objective

Prevent hype, urgency, advice, guarantees, and simulated-to-real misrepresentation.

### Work

- create prohibited phrase and semantic test cases for guarantees, risk-free claims, sure-win language, urgency, FOMO, AI certainty, profit probability, and real-return mislabeling;
- scan English and Estonian catalogs, help, trust, onboarding, notices, and notifications;
- require human review for ambiguous findings;
- preserve false-positive decisions;
- integrate with CI.

### Acceptance Criteria

- prohibited claims fail CI or require documented resolution;
- both languages are covered;
- content tests include context rather than phrase matching only;
- valid technical uses can be reviewed safely;
- lint tests pass.

## S13.38 Implement Consistent Error Content and Recovery Links

### Objective

Map stable server error codes to localized safe explanations and next actions.

### Work

- define error content registry;
- render title, code, explanation, correlation, scope, retry eligibility, next action, help, and incident route;
- keep severity and retry semantics locale-independent;
- prohibit stack traces, SQL, secrets, and internal paths;
- test unknown codes and fallbacks.

### Acceptance Criteria

- every public API error code has approved content;
- translations preserve severity and retry meaning;
- unknown codes degrade safely;
- no sensitive details appear;
- error tests pass.

## S13.39 Implement Empty, Loading, Offline, and Degraded States

### Objective

Distinguish no data, not configured, no authorization, missing evidence, outage, cold start, stale cache, and schema failure.

### Work

- implement canonical empty-state categories;
- load critical shell status first where practical;
- avoid fabricated metrics and endless skeletons;
- label offline and cached timestamps;
- prohibit privileged commands without authoritative state;
- implement bounded retry and reconnect behavior.

### Acceptance Criteria

- cached evidence never appears fresh;
- empty and integrity-failure states are distinct;
- cold start is not mislabeled as cycle failure;
- no offline mutation queue exists for privileged actions;
- state-matrix tests pass.

## S13.40 Implement Keyboard Shortcuts and Discoverability

### Objective

Provide safe productivity shortcuts without executing privileged actions.

### Work

- implement focus search, open palette, notifications, help, primary navigation, and close actions;
- avoid browser/assistive conflicts;
- provide shortcut help and optional disablement;
- preserve focus after navigation;
- prohibit direct financial or privileged command shortcuts.

### Acceptance Criteria

- all shortcuts are discoverable;
- assistive technology compatibility is tested;
- shortcuts never bypass confirmation;
- user preference is respected;
- keyboard tests pass.

## S13.41 Add Responsive and Accessibility Verification

### Objective

Make the entire shell and cross-product experience usable across devices and assistive technologies.

### Work

- verify desktop, tablet, mobile, landscape, portrait, 200% zoom, and relevant 400% zoom;
- test skip links, landmarks, navigation, switchers, breadcrumbs, search, palette, onboarding, help, trust, notifications, dialogs, status announcements, focus, target sizes, language attributes, and copy controls;
- verify reduced motion and contrast;
- record screen-reader spot checks in both languages;
- test long translated labels and IDs.

### Acceptance Criteria

- every route remains reachable by keyboard;
- critical status is never obscured;
- no meaning relies on color, icon, hover, or position alone;
- translated layouts reflow correctly;
- no critical automated violation remains;
- manual evidence is recorded.

## S13.42 Add Security, Privacy, Observability, and Full Test Coverage

### Objective

Make authorized navigation, search isolation, safe caching, notification privacy, content sanitization, localization parity, and critical-status integrity release-blocking.

### Work

- add contract, shell, navigation, workspace, environment, lineage, search, palette, recent, saved-view, onboarding, acknowledgement, help, glossary, methodology, trust, notice, notification, support, diagnostic, i18n, formatting, content, error, offline, keyboard, route, E2E, accessibility, visual, authorization, and RLS tests;
- add search injection, no-existence-leak, stale-cache, unsafe-command, secret, raw-query telemetry, notification, support, and unsanitized-content tests;
- verify no shell, search, notification, support, or localization path gains financial, governance, release, or live-trading authority;
- instrument safe shell, navigation, search, onboarding, help, notification, translation, accessibility, offline, and error metrics;
- test prohibited telemetry fields.

### Acceptance Criteria

- unauthorized resources never leak through shell or search;
- critical notices cannot be disabled or hidden;
- no unsafe cache or support package exposes secrets;
- translations preserve canonical meaning;
- no browser or AI path gains arbitrary command or live-trading authority;
- telemetry contains no prohibited fields;
- critical CI checks pass.

## Sprint Verification Matrix

| Area | Required evidence |
|---|---|
| Shell | Product identity, landmarks, global status, route layout, workspace/environment context, public/authenticated separation, and build metadata tests |
| Navigation | Taxonomy, permissions, direct routes, mobile, switchers, breadcrumbs, contextual links, and lineage tests |
| Search | Authorization, RLS, exact IDs, safe fuzzy match, bounds, pagination, injection, no-existence-leak, groups, and accessibility tests |
| Personalization | Recent items, clear history, favorites, saved views, canonical filters, compatibility, locale independence, and privacy tests |
| Onboarding | Role stages, progress, acknowledgements, version reset, safety content, localization, revisit, and E2E tests |
| Help and Trust | Context coverage, glossary, methodology, evidence timestamps, public/private scope, stale state, disclosure, and content tests |
| Notifications | Persistence, recipient scope, priorities, deduplication, grouping, delivery, read, acknowledgement, resolution, preferences, and critical non-disablement tests |
| Internationalization | English/Estonian catalogs, canonical keys, parameters, pluralization, terminology, numbers, currencies, percentages, dates, timezones, language, and fallback tests |
| Content | Product name, tagline, simulation, no advice, no guarantees, no urgency, confidence meaning, error registry, translation parity, and review workflow tests |
| Accessibility and security | Keyboard, screen reader, zoom, reflow, contrast, RLS search, safe cache, sanitization, support redaction, no commands, no authority, and telemetry tests |

## Sprint Exit Gate

Sprint 13 is complete only when:

- S13.1 through S13.42 are implemented and verified;
- official product identity and evidence-driven voice are used throughout;
- environment, workspace, simulation, live-trading-disabled, freshness, halt, reconciliation, incident, and governance blocker state remains globally visible;
- canonical priority ensures critical failures outrank performance;
- navigation is stable, role-aware, directly addressable, responsive, and accessible;
- workspace and environment switching clears unsafe scoped state;
- cross-workspace lineage can trace results to source evidence without authorization leaks;
- global search is bounded, RLS-protected, injection-safe, and no-existence-leak verified;
- command palette remains a safe navigation launcher and cannot bypass normal command gates;
- recent items and saved views store only bounded safe metadata;
- onboarding, acknowledgements, help, glossary, methodology, and Trust Center teach research scope, AI limits, deterministic risk, costs, backtest limits, schedule limits, privacy, and support;
- notifications are durable, deduplicated, priority-aware, privacy-minimized, and cannot directly mutate domain state;
- critical notifications cannot be fully disabled;
- English and Estonian preserve identical domain semantics and canonical values;
- number, currency, percentage, ratio, date, duration, and timezone formatting preserves authoritative data;
- content governance blocks guarantees, hype, urgency, advice, confidence-as-profit-probability, and simulated-to-real misrepresentation;
- offline or degraded state never presents cached evidence as fresh or permits privileged commands;
- no shell, search, notification, support, localization, browser, or AI path gains arbitrary command, financial, governance, release, private exchange, testnet, or live-trading authority;
- accessibility, responsive, security, privacy, contract, navigation, search, onboarding, notification, content, i18n, formatting, E2E, support, and visual checks pass;
- documentation and changelog are updated;
- the completed sprint commits are fetched and verified.

## Next Sprint

Sprint 14 defines and implements the Developer Portal, API Explorer, Documentation System, Test Evidence, Runbook Library, and Implementation Traceability Workspace.
