# Product Shell, Onboarding, Help, Trust Center, Global Search, Notifications, Internationalization, and Cross-Workspace Experience Specification

Last reviewed: 2026-07-31  
Status: Sprint 13 authoritative cross-product experience specification

## 1. Purpose

This document defines the implementation contract for the Product Shell, Onboarding, Help, Trust Center, Global Search, Notifications, Internationalization, and Cross-Workspace Experience of The Daily Roast AI.

The product shell turns the evidence, AI, strategy, risk, portfolio, backtest, experiment, governance, and audit workspaces into one coherent research product. It must help users understand simulation status, evidence freshness, uncertainty, role boundaries, terminology, cross-resource lineage, current blockers, and next safe actions before they interpret performance.

The shell is an orientation and communication layer. It must not create financial authority, hide critical state, invent data, weaken authorization, convert notifications into commands, or use marketing language that implies guaranteed performance.

## 2. Scope

Sprint 13 covers:

- authenticated application shell and public demo shell;
- primary, secondary, contextual, breadcrumb, and mobile navigation;
- workspace and environment switchers;
- first-run onboarding and role-aware setup guidance;
- paper-trading and AI-literacy education;
- global search across authorized evidence resources;
- command palette limited to safe navigation and authorized explicit commands;
- saved views, recent items, favorites, and history;
- in-app notifications, notices, banners, notification center, and preferences;
- contextual help, glossary, methodology, keyboard shortcuts, and support links;
- Trust Center covering simulation, evidence, AI limits, security posture, privacy, incidents, uptime limitations, and release state;
- product-wide status hierarchy and persistent safety labels;
- Estonian and English localization architecture;
- number, currency, percentage, date, duration, and timezone localization;
- content governance, terminology, translation review, and unsupported-claim policy;
- cross-workspace lineage navigation;
- empty, loading, stale, partial, unauthorized, unavailable, and degraded states;
- responsive, accessible, secure, observable, and testable product behavior.

Sprint 13 does not implement:

- public billing or paid SaaS;
- social trading, chat, community, or copy trading;
- marketing claims based on backtests or paper performance;
- notification-driven order execution;
- arbitrary natural-language commands;
- AI-generated navigation that bypasses authorization;
- browser-side authority over risk, accounting, reconciliation, experiments, governance, or release state;
- automatic translation of immutable audit or financial evidence without preserving canonical values;
- live trading or private Binance execution.

## 3. Product Identity

Required identity:

- product name: **The Daily Roast AI**;
- tagline: **Evidence-Driven Market Intelligence**;
- application domain: `app.thedailyroast.online`;
- public product domain: `thedailyroast.online`;
- API domain: `api.thedailyroast.online`;
- repository name treated as a technical legacy identifier only.

All user-facing content must use the official product identity.

## 4. Experience Principles

1. Evidence before interpretation.
2. Safety state before performance.
3. Simulation before action language.
4. Provenance before confidence.
5. Uncertainty before persuasion.
6. Deterministic controls around probabilistic AI.
7. Role and permission clarity before commands.
8. One canonical meaning for every status.
9. No hidden lineage or manual override.
10. Keyboard, screen reader, zoom, and mobile support are release requirements.
11. Estonian and English content preserve identical domain meaning.
12. No hype, urgency, guaranteed return, or fear-of-missing-out language.

## 5. User Outcomes

A user should be able to answer:

1. Which workspace and environment am I using?
2. Is this paper trading, historical simulation, public demo, or production research?
3. What is fresh, stale, incomplete, halted, blocked, or unavailable?
4. Which critical issue requires attention first?
5. Which areas can my role read or change?
6. Where do I find today’s market evidence, AI report, decision, risk result, portfolio, backtest, experiment, governance, and audit records?
7. How do I trace one result across every related resource?
8. What does each technical or financial term mean?
9. Why is AI confidence not probability of profit?
10. Why is paper performance not evidence of future results?
11. What should I complete during first-run setup?
12. Which notifications require awareness, review, or an authorized command?
13. Which notices are informational and which are safety-critical?
14. Which interface language, locale, timezone, and number format are active?
15. Does translated content preserve canonical status codes, values, units, and evidence links?
16. Where can I inspect security, privacy, AI limitations, incidents, service limitations, and release readiness?
17. How do I get help without exposing secrets or sensitive data?

## 6. Canonical Routes

```text
/
/onboarding
/search
/recent
/saved-views
/notifications
/help
/help/getting-started
/help/glossary
/help/methodology
/help/keyboard-shortcuts
/trust
/trust/simulation
/trust/ai
/trust/security
/trust/privacy
/trust/incidents
/trust/service-status
/settings/preferences
/settings/notifications
/settings/language
```

The shell wraps all protected workspace routes and provides a separate minimal public-demo shell for approved public content.

## 7. Shell Read Model

Recommended contract:

```ts
interface ProductShellReadModel {
  schemaVersion: string;
  product: ProductIdentitySummary;
  account: ShellAccountSummary | null;
  workspace: ShellWorkspaceSummary | null;
  environment: ShellEnvironmentSummary;
  mode: ProductModeSummary;
  globalStatus: GlobalStatusSummary;
  navigation: NavigationModel;
  recentItems: RecentItemSummary[];
  savedViews: SavedViewSummary[];
  notifications: NotificationSummary;
  preferences: UserPreferenceSummary;
  help: HelpContextSummary;
  trust: TrustCenterSummary;
  permissions: ShellPermissionSummary;
  diagnostics: DiagnosticSummary[];
  links: ShellResourceLinks;
}
```

The frontend must not infer global safety status, effective permissions, critical blockers, freshness, or mode from unrelated raw fields.

## 8. Application Shell Regions

The protected shell includes:

- skip link;
- product identity;
- workspace and environment context;
- persistent mode and safety state;
- primary navigation;
- contextual navigation;
- global search or command trigger;
- notification trigger;
- help trigger;
- account menu;
- page title and breadcrumb region;
- critical notices;
- main content;
- optional contextual inspector;
- footer with version, environment, and trust links.

Landmarks and reading order must remain logical across desktop, tablet, mobile, and zoomed layouts.

## 9. Public Demo Shell

The public demo may expose approved read-only sample or delayed evidence.

Requirements:

- explicit public-demo label;
- explicit simulation label;
- no authenticated workspace identity leakage;
- no membership, secret, security-finding, incident-detail, or private financial evidence;
- delayed or sample-data timestamp;
- limited routes;
- no privileged commands;
- product and risk disclaimers;
- accessible sign-in entry;
- clear distinction from authenticated experiment state.

## 10. Global Mode and Safety Header

Required persistent state:

- environment;
- product mode;
- paper/simulation status;
- live-trading-disabled state;
- active workspace halt;
- portfolio reconciliation status;
- market freshness status;
- active critical incident or governance blocker;
- data timestamp;
- global status timestamp.

Critical state must not disappear when navigating between workspaces.

## 11. Status Hierarchy

Canonical priority order:

1. security or secret exposure;
2. ledger, audit, or reconciliation integrity failure;
3. active workspace or portfolio halt;
4. invalid or blocked experiment;
5. authorization or RLS mismatch;
6. stale or invalid market evidence;
7. provider or dependency failure;
8. budget exhausted or fallback active;
9. incomplete, delayed, or partial process;
10. ordinary warning;
11. healthy informational status;
12. performance or result summaries.

Lower-priority positive status must never suppress a higher-priority failure.

## 12. Navigation Taxonomy

Primary navigation groups:

- Today’s Roast;
- Market Evidence;
- Gemini Analysis;
- Decisions and Risk;
- Paper Portfolio;
- Backtests;
- Experiments;
- Audit;
- Governance;
- Help and Trust.

Navigation labels must be concise, stable, localized, and mapped to canonical route IDs rather than literal translated strings.

## 13. Role-Aware Navigation

Navigation visibility and command affordances use server-provided permissions.

Requirements:

- viewers see authorized evidence routes;
- operators see authorized research operations;
- owners see governance and approved lifecycle commands;
- hidden navigation does not replace server authorization;
- unavailable features may show an explanatory denied or not-enabled state when policy allows;
- route access remains directly testable;
- no role is inferred only from frontend state.

## 14. Workspace Switcher

Required fields:

- workspace ID;
- name;
- effective role;
- mode;
- active experiment summary;
- halt or blocker state;
- last accessed timestamp;
- permission to switch;
- archived status.

Switching must clear workspace-scoped cached data and preserve only safe user preferences.

## 15. Environment Switcher

Environment switching is available only where explicitly supported.

Required behavior:

- environment identity and purpose;
- domain and data-boundary clarity;
- separate authentication when required;
- no cross-environment token or secret reuse;
- clear public-demo, local, paper, staging, and production-research labels;
- confirmation before leaving an unsaved preference form;
- no implication that production research enables live trading.

## 16. Breadcrumbs and Contextual Navigation

Breadcrumbs reflect resource hierarchy, not browser history.

Examples:

```text
Workspace > Experiments > Experiment > Cycle
Workspace > Portfolio > Order > Fill > Ledger Transaction
Workspace > Market Evidence > Snapshot > Feature Calculation
Workspace > Backtests > Run > Trade > Decision
```

Breadcrumb labels must preserve IDs or disambiguating context when names repeat.

## 17. Cross-Workspace Lineage Navigator

The lineage navigator exposes related resources as a typed graph or ordered chain.

Supported node types include:

- candle and market snapshot;
- feature calculation;
- Gemini request, validation, and report;
- strategy and risk evaluation;
- paper order and fill;
- ledger transaction and portfolio state;
- reconciliation;
- backtest and trade;
- experiment and cycle;
- incident, halt, configuration, release, and audit event.

The navigator must preserve direction, relationship type, status, timestamp, and authorization.

## 18. Global Search Contract

Search covers only authorized indexed metadata and bounded approved content.

Searchable resource types may include:

- workspaces;
- market snapshots;
- analyses;
- decisions;
- risk evaluations;
- orders and fills;
- ledger transactions by safe identifiers;
- backtests;
- experiments and cycles;
- incidents and halts;
- audit events;
- configurations;
- releases;
- help and glossary content.

Search must not expose secret values, unrestricted raw prompts, private provider responses, or unauthorized resource existence.

## 19. Search Read Model

Recommended contract:

```ts
interface GlobalSearchReadModel {
  schemaVersion: string;
  query: string;
  parsedFilters: SearchFilterSummary[];
  results: SearchResultSummary[];
  groups: SearchResultGroupSummary[];
  suggestions: SearchSuggestionSummary[];
  page: CursorPage;
  limitations: LimitationSummary[];
  diagnostics: DiagnosticSummary[];
}
```

Result fields include resource type, safe title, context, status, timestamp, workspace, permitted route, matched field category, and freshness.

## 20. Search Behavior

Requirements:

- minimum query length where appropriate;
- bounded query size;
- debounced requests;
- cursor pagination;
- server-approved filters;
- deterministic ordering rules;
- exact identifier matching;
- safe fuzzy matching for names and help content;
- no raw SQL or search syntax passthrough;
- no existence leak through counts or timing;
- generic unauthorized result behavior;
- accessible result announcements.

## 21. Command Palette

The command palette may support:

- route navigation;
- opening recent items;
- switching workspace;
- opening help or trust pages;
- applying saved views;
- invoking an already-authorized explicit command through its normal confirmation flow.

It must not accept arbitrary natural-language financial instructions or bypass confirmation, recent authentication, idempotency, expected-version, or audit requirements.

## 22. Recent Items and History

Recent-item fields:

- resource type and ID;
- safe label;
- workspace;
- route;
- last viewed timestamp;
- status summary;
- availability state.

Requirements:

- client history contains no sensitive payloads;
- server history is optional and authorization-filtered;
- revoked resources disappear safely;
- users can clear personal recent history;
- audit evidence is unaffected.

## 23. Favorites and Saved Views

A saved view contains:

- immutable saved-view ID;
- owner user ID;
- workspace scope;
- route ID;
- approved filters, sort, columns, and display options;
- locale-independent canonical values;
- name;
- creation and update timestamps;
- compatibility version;
- private or approved shared state.

Saved views must not store tokens, secrets, raw prompts, unrestricted queries, or authoritative calculations.

## 24. Onboarding Stages

Recommended stages:

1. product identity and research-only scope;
2. simulation and live-trading-disabled explanation;
3. role and workspace context;
4. evidence lineage overview;
5. market freshness and quality;
6. Gemini advisory and validation limits;
7. deterministic strategy and risk authority;
8. paper portfolio, costs, and reconciliation;
9. backtest limitations and benchmarks;
10. experiment schedule and incidents;
11. privacy, security, and support;
12. completion and next safe route.

Onboarding progress must not gate emergency notices or critical safety information.

## 25. Role-Aware Onboarding

Viewer onboarding emphasizes reading, evidence, uncertainty, exports, and trust.

Operator onboarding adds market operations, analysis, backtests, cycle investigation, and incident runbooks.

Owner onboarding adds workspace configuration, budgets, risk governance, experiment lifecycle, access control, security, and release gates.

Role-specific content must not imply permissions that the server denies.

## 26. Onboarding Progress Contract

Required fields:

- onboarding version;
- user and workspace scope;
- role context;
- stage IDs;
- completion status;
- completed timestamps;
- skipped state and reason where allowed;
- required acknowledgement versions;
- last route;
- compatibility and reset state.

A content-version change may require re-acknowledgement for material safety changes.

## 27. Safety Acknowledgements

Material acknowledgements may cover:

- paper and simulated execution;
- no financial advice;
- no guarantee of profit;
- Gemini confidence meaning;
- backtest limitations;
- fees, spread, slippage, and precision;
- risk halts and fail-closed behavior;
- best-effort cloud scheduling;
- public-demo delay or sample data;
- live trading disabled.

Acknowledgement records do not waive product safety obligations.

## 28. Contextual Help

Every primary workspace should expose:

- page purpose;
- interpretation order;
- key terms;
- status definitions;
- methodology links;
- evidence lineage explanation;
- common failure states;
- permitted role actions;
- related runbooks where authorized;
- limitations.

Help must not cover critical content or require hover-only interaction.

## 29. Glossary Contract

Glossary entries include:

- canonical term ID;
- English preferred term;
- Estonian preferred term;
- definition in both languages;
- category;
- synonyms and prohibited misleading synonyms;
- unit or formula references where applicable;
- related concepts;
- source document;
- version and review status.

Examples include analytical confidence, market regime, finalized candle, slippage, exposure, drawdown, ledger, reconciliation, benchmark, RLS, idempotency, and halt.

## 30. Methodology Center

The methodology center provides version-linked explanations for:

- market data and freshness;
- deterministic features;
- Gemini request and validation;
- strategy and risk;
- paper execution and costs;
- accounting and reconciliation;
- backtests and benchmarks;
- experiments and scheduling;
- security, privacy, and release governance.

It must link to authoritative evidence and avoid replacing exact configuration details.

## 31. Trust Center

Recommended sections:

- product scope and non-goals;
- simulation and paper trading;
- evidence and provenance;
- Gemini limitations and validation;
- deterministic risk boundaries;
- market data freshness;
- performance and backtest limitations;
- security controls and current assurance summary;
- privacy and provider data handling;
- incidents and service limitations;
- backup and recovery posture;
- release and environment status;
- contact and responsible disclosure.

The Trust Center must avoid exposing sensitive findings or infrastructure details.

## 32. Trust Center Status Contract

Required fields:

- section ID;
- public or authenticated visibility;
- status;
- evidence timestamp;
- scope and environment;
- summary;
- limitations;
- approved public evidence references;
- next review date;
- incident or notice reference where appropriate.

Unknown, stale, or unavailable evidence must not be represented as healthy.

## 33. Product Notices

Notice types:

- informational;
- maintenance;
- degraded service;
- stale data;
- provider limitation;
- budget warning;
- experiment delay;
- incident;
- security advisory;
- privacy or terms update;
- release or migration notice;
- critical halt or integrity warning.

Each notice has canonical type, severity, scope, audience, start, expiry, acknowledgement policy, source, evidence, and route.

## 34. Notification Contract

Required fields:

- immutable notification ID;
- recipient user or role scope;
- workspace and environment scope;
- canonical event type;
- severity;
- title and safe summary;
- source entity type and ID;
- created timestamp;
- read, acknowledged, resolved, or expired state;
- action route;
- delivery-channel status;
- deduplication key;
- correlation ID;
- localization key and parameters.

Notifications contain references and summaries, not secret-bearing payloads.

## 35. Notification Priorities

Priority order aligns with global status hierarchy.

Critical notification categories include:

- secret exposure;
- authorization or RLS mismatch;
- ledger or reconciliation failure;
- active halt;
- invalid experiment;
- security incident;
- failed restore;
- critical release failure.

Critical notices must remain visible until resolved or explicitly acknowledged according to policy.

## 36. Notification Delivery

MVP delivery may include:

- in-app notification center;
- persistent banners;
- optional email only when separately configured and approved.

Browser push, SMS, and external chat integrations require separate privacy, security, delivery, and cost specifications.

Delivery failure must not remove the durable in-app record.

## 37. Notification Preferences

Users may configure non-critical categories, digest behavior, locale, and approved channels.

Requirements:

- critical safety and security notices cannot be fully disabled;
- preferences are user-scoped and versioned;
- workspace role and legal requirements may constrain preferences;
- no secret destination details appear broadly;
- changes are audited when material;
- defaults are conservative.

## 38. Notification Deduplication and Grouping

Requirements:

- stable deduplication key;
- repeat count;
- first and last occurrence timestamps;
- grouping by source and category;
- escalation after configured thresholds;
- resolution linkage;
- no loss of underlying audit events;
- deterministic unread counts.

Grouping must not hide repeated critical failures.

## 39. Support Entry Points

Approved support entry points may include:

- contextual help;
- documentation links;
- issue-report form;
- security disclosure instructions;
- incident-status reference;
- correlation-ID copy;
- export of safe diagnostic package.

The UI must warn users not to submit API keys, tokens, passwords, database URLs, or unrestricted private evidence.

## 40. Diagnostic Support Package

An authorized support package may include:

- product and client build version;
- route and resource IDs;
- environment and workspace safe identifiers;
- correlation IDs;
- timestamps;
- safe error codes;
- status summaries;
- browser capability summary;
- redacted network and feature diagnostics;
- user-provided description.

It must exclude secrets, tokens, cookies, raw prompts, unrestricted provider responses, and private financial details not required for diagnosis.

## 41. Internationalization Architecture

Requirements:

- canonical locale-independent route, status, event, permission, and glossary IDs;
- message catalogs for `en` and `et`;
- ICU-compatible parameterized messages where practical;
- no string concatenation for translated sentences;
- fallback to approved English message when translation is missing;
- missing-translation telemetry without user data;
- locale stored as user preference;
- server error codes translated only in the client presentation layer;
- canonical evidence values remain unchanged.

## 42. Supported Locales

MVP supported interface locales:

- `en` — English;
- `et` — Estonian.

Default behavior may use user preference, browser preference, or approved product default, but must be deterministic and user-changeable.

Language selection must not change authorization, resource identity, calculation, or report hashes.

## 43. Domain Translation Rules

Translations must preserve exact meaning for:

- paper and simulated execution;
- analytical confidence;
- strategy intent;
- risk approval and rejection;
- halt;
- stale and invalid data;
- ledger and reconciliation;
- gross and net performance;
- backtest and benchmark;
- owner, operator, viewer;
- security finding and exception;
- release blocker.

Ambiguous casual financial terms must not replace canonical domain terms.

## 44. Machine and Human Content Boundaries

Canonical machine values remain untranslated:

- IDs and hashes;
- enum codes in exports;
- currency and asset codes;
- configuration versions;
- timestamps in machine formats;
- reason and error codes;
- evidence references.

Human presentation adds localized labels and explanations without changing canonical data.

## 45. Number and Currency Localization

Requirements:

- locale-aware display separators;
- explicit currency or asset codes;
- authoritative decimal strings preserved internally;
- no value rounding that changes meaning;
- consistent significant-digit and precision policy;
- negative values announced accessibly;
- gross, net, available, reserved, and estimated values labeled;
- copy action may provide canonical machine value separately.

## 46. Percentage and Ratio Localization

Requirements:

- explicit percentage versus decimal-ratio semantics;
- no conversion ambiguity;
- versioned rounding policy;
- undefined values remain unavailable with reasons;
- analytical confidence is not formatted as probability of profit;
- ratios such as Sharpe and Sortino remain unitless and definition-linked.

## 47. Date, Time, Duration, and Timezone

Requirements:

- user-selected display timezone;
- accessible UTC reference for evidence timestamps;
- explicit intended versus actual schedule times;
- locale-aware date and time formatting;
- unambiguous absolute timestamps for critical events;
- relative times supplemented by absolute values;
- duration localization;
- DST-aware behavior;
- canonical ISO timestamps in exports.

## 48. Content Governance

Every user-facing message category must have:

- canonical content key;
- owner;
- English source text;
- Estonian translation;
- status;
- context and parameter definitions;
- risk and legal review requirement where applicable;
- version;
- last reviewed date;
- related product requirement or domain code.

Material safety wording changes require review and audit.

## 49. Brand Voice and Prohibited Language

Required voice:

- precise;
- calm;
- evidence-driven;
- transparent about uncertainty;
- non-promotional;
- respectful of user control.

Prohibited language includes:

- guaranteed profit;
- risk-free;
- sure win;
- beat the market claims without complete evidence;
- urgent buy or sell pressure;
- fear of missing out;
- AI knows the future;
- confidence interpreted as success probability;
- simulated results described as real returns.

## 50. Error Content Contract

Every user-facing error includes:

- localized safe title;
- stable machine-readable error code;
- localized explanation;
- correlation ID where appropriate;
- affected scope;
- retry eligibility;
- safe next action;
- help or incident route;
- no stack trace, SQL, secret, or internal path.

Translations must not change retry or severity semantics.

## 51. Empty and First-Use States

Empty states must distinguish:

- not configured;
- not run yet;
- no result by design;
- no authorized data;
- filters returned no matches;
- data expired or archived;
- required evidence missing;
- backend unavailable;
- schema incompatible.

Empty states must not invent sample performance unless clearly labeled as demo content.

## 52. Loading and Progressive Disclosure

Requirements:

- preserve page structure during loading;
- do not fabricate metrics;
- critical global status loads independently and first where practical;
- indicate cold start separately;
- use progressive disclosure for dense evidence;
- keep critical failures expanded;
- avoid infinite skeletons;
- support cancellation or route change safely.

## 53. Offline and Degraded Behavior

The web application may support limited cached shell and help content.

Requirements:

- no cached evidence presented as fresh;
- explicit offline or stale label;
- no privileged command when authoritative server state is unavailable;
- cached resource timestamps;
- bounded retry;
- no offline financial mutation queue;
- safe recovery after reconnect.

## 54. Keyboard Shortcuts

Approved shortcuts may cover:

- focus global search;
- open command palette;
- open notifications;
- open help;
- navigate primary sections;
- close dialogs and inspectors.

Requirements:

- no conflict with browser or assistive technology defaults;
- discoverable shortcut help;
- user-disable option where appropriate;
- no shortcut directly executes privileged or financial commands;
- visible focus after navigation.

## 55. Responsive Behavior

Requirements:

- critical mode and safety state remains visible;
- mobile navigation preserves all authorized primary routes;
- workspace and environment context remains accessible;
- search, notifications, help, and account actions remain reachable;
- breadcrumbs may adapt without losing resource context;
- long IDs and statuses wrap safely;
- no critical content is hover-only;
- sticky regions do not obscure content or focus;
- landscape, portrait, and zoom layouts are tested.

## 56. Accessibility Requirements

The shell targets WCAG 2.2 AA where practical.

Required behavior:

- skip links and logical landmarks;
- consistent navigation and naming;
- keyboard access to all routes and controls;
- visible focus;
- accessible menus, dialogs, disclosures, tabs, notifications, search results, and switchers;
- text alternatives and semantic status announcements;
- no reliance on color, position, or icon alone;
- reflow at 200% and relevant 400% zoom cases;
- reduced motion;
- minimum target sizes where practical;
- accessible autocomplete and command palette;
- screen-reader-readable numbers, units, dates, statuses, and lineage;
- language attributes for translated and mixed-language content.

## 57. Security and Authority Boundaries

The shell must not:

- expose unauthorized route or resource existence;
- cache secrets, tokens, raw prompts, unrestricted responses, or private financial evidence;
- trust client roles or permissions;
- use search to bypass RLS;
- execute arbitrary natural-language commands;
- execute privileged actions without normal server gates;
- allow notifications to mutate domain state directly;
- expose support packages without authorization and redaction;
- render unsanitized model, incident, audit, or user content;
- weaken critical notices through preference settings;
- enable live trading or private exchange access.

## 58. Privacy and Data Minimization

The shell, search, recent history, saved views, notifications, support, and telemetry must minimize:

- user identity;
- workspace membership;
- private route history;
- search queries;
- notification content;
- support descriptions;
- diagnostic metadata;
- locale and preference data.

Search and telemetry must avoid storing unrestricted query text when canonical filters or hashed safe identifiers suffice.

## 59. Observability

Safe telemetry may include:

- shell load and route transition timings;
- navigation failures;
- search outcomes by safe resource category;
- no-result and authorization-filter counts;
- onboarding completion and acknowledgement versions;
- help and glossary usage;
- notification created, delivered, read, acknowledged, grouped, and expired outcomes;
- missing translation keys;
- locale and timezone distribution at aggregate level;
- accessibility interaction failures;
- offline and degraded-state counts;
- safe client build and environment identifiers.

Telemetry must not include raw search queries, secret values, full notification content, unrestricted resource names, or support descriptions.

## 60. Testing Strategy

### Contract Tests

Validate shell, navigation, status, search, saved view, onboarding, notification, help, trust, locale, glossary, preference, and support schemas.

### Navigation Tests

Validate route taxonomy, role visibility, direct addressing, breadcrumbs, workspace switching, environment switching, lineage links, mobile navigation, and unauthorized routes.

### Search Tests

Validate authorization filtering, exact IDs, fuzzy names, help search, pagination, bounds, injection input, no existence leak, and accessible announcements.

### Onboarding Tests

Validate role-aware stages, progress, acknowledgements, version reset, skip policy, completion, and critical-notice independence.

### Notification Tests

Validate creation, deduplication, grouping, priority, unread counts, acknowledgement, resolution, expiry, preferences, critical non-disablement, and failed delivery.

### Internationalization Tests

Validate English and Estonian catalogs, missing keys, parameter types, pluralization, status semantics, domain terms, numbers, currencies, percentages, dates, durations, timezones, language attributes, and canonical exports.

### Content Tests

Validate product name, tagline, simulation language, no advice, no guaranteed returns, no urgency, confidence meaning, benchmark limitations, and translated semantic parity.

### Trust and Help Tests

Validate evidence timestamps, stale states, public/private visibility, methodology links, glossary definitions, security disclosure, and no sensitive detail exposure.

### Accessibility Tests

Validate landmarks, skip links, consistent navigation, menus, dialogs, search, notifications, switchers, focus, target size, announcements, language, zoom, reflow, reduced motion, and contrast.

### Security and Privacy Tests

Validate RLS-filtered search, safe caching, history clearing, saved-view bounds, support redaction, notification privacy, content sanitization, no arbitrary commands, and no critical-notice disablement.

### Visual Regression

Capture public demo, authenticated shell, mobile navigation, critical halt, stale data, onboarding, search, empty results, notifications, Trust Center, English, Estonian, offline, cold-start, and authorization-error states.

### E2E Tests

Validate first sign-in, onboarding, workspace selection, route discovery, search-to-evidence, lineage traversal, saved view, notification-to-resource, language switch, help lookup, support package, and sign-out.

## 61. Acceptance Criteria

Sprint 13 documentation is accepted when:

1. official product identity is used everywhere;
2. environment, workspace, simulation, live-trading-disabled, freshness, halt, reconciliation, incident, and blocker state remains globally visible;
3. critical status outranks performance;
4. navigation is stable, role-aware, directly addressable, responsive, and keyboard accessible;
5. search returns only authorized resources and cannot leak existence;
6. command palette remains a safe navigation layer and cannot bypass normal command gates;
7. onboarding teaches evidence, AI limits, deterministic risk, simulation, backtest limits, scheduling, privacy, and support;
8. help, glossary, methodology, and Trust Center content is versioned and evidence-linked;
9. notifications are durable, deduplicated, priority-aware, privacy-minimized, and cannot directly mutate domain state;
10. critical notifications cannot be fully disabled;
11. English and Estonian preserve identical domain semantics and canonical machine values;
12. numbers, currencies, percentages, dates, durations, and timezones are localized without changing authoritative data;
13. all content avoids guarantees, urgency, hype, financial advice, and confidence-as-profit-probability language;
14. offline and degraded states never present cached evidence as fresh or permit privileged commands;
15. no unauthorized search, arbitrary command, unsafe caching, unsanitized content, notification bypass, or live-trading authority is introduced;
16. security, privacy, accessibility, content, localization, navigation, search, onboarding, notification, and E2E gates are explicit.

## 62. Definition of Done

The Sprint 13 specification is complete when:

- this document is committed;
- `SPRINT_13_TASKS.md` is committed;
- terminology matches product requirements, all workspace specifications, security, privacy, API, observability, accessibility, and deployment documents;
- all shell, navigation, search, onboarding, help, glossary, trust, notification, localization, content, degraded, responsive, accessibility, and authority states are explicit;
- both commits are fetched and verified.

## 63. Next Sprint Boundary

Sprint 14 defines the **Developer Portal, API Explorer, Documentation System, Test Evidence, Runbook Library, and Implementation Traceability Workspace**, including versioned OpenAPI discovery, authenticated API examples, schema and error catalogs, task-to-code-to-test traceability, documentation freshness, runbook execution evidence, architecture decision records, generated reference checks, and contributor onboarding without exposing secrets or bypassing operational authority.
