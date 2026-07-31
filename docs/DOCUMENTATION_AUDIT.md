# Documentation Audit

Last reviewed: 2026-07-31
Audit scope: root documentation, all `docs/` specifications, environment examples, and all task-governance files
Status: Completed for local, free-cloud MVP, testing, staging, and production-research planning

## Executive Result

The documentation now defines one coherent lifecycle:

```text
Local Development
  -> CI and Test Environments
  -> Free Cloud Demo
  -> Controlled Paper Experiment
  -> Staging
  -> Production Research Service
  -> Separate Binance Sandbox Assessment
  -> Separate Live-Trading Assessment
```

Production development is explicitly separated from live trading. The planned production service remains a research, backtesting, audit, and paper-trading platform.

## Authoritative Environment Documents

- `LOCAL_DEVELOPMENT.md` — local tools, Supabase CLI, fake providers, commands, seed data, debugging, and Windows support.
- `TEST_ENVIRONMENTS.md` — test environment matrix, fixtures, CI, provider policy, recovery, and promotion gates.
- `FREE_CLOUD_ARCHITECTURE.md` — zero-required-cost demo and paper-experiment topology.
- `FREE_CLOUD_REQUIREMENTS.md` — free-cloud refinement of the main product requirements.
- `DEPLOYMENT.md` — deployment and promotion across all environments.
- `PRODUCTION_DEVELOPMENT.md` — staging and production-grade research development.

## Authoritative Task Sources

- `/TASKS.md` — shared domains and application functionality.
- `/CLOUD_MVP_TASKS.md` — free cloud deployment and experiment.
- `/LOCAL_AND_PRODUCTION_TASKS.md` — local bootstrap, test automation, staging, production research, and post-launch work.

Every task source uses detailed work cards with user story, acceptance criteria, Definition of Done, dependencies, and references.

## Consistency Findings

### Local Development

The local profile now consistently uses local Supabase/PostgreSQL and Auth, fake Binance and Gemini by default, deterministic seed data, cross-platform commands, and no paid credentials for normal work.

### Testing

The test strategy now consistently requires migration, RLS, authorization, financial invariant, provider contract, frontend bundle, E2E, failure, export, restore, staging, and production promotion tests.

References to Redis, ARQ, persistent WebSocket, and hosted Prometheus/Grafana are treated as deferred architecture options, not active free-cloud requirements.

### Cloud Demo and Experiment

The active cloud profile consistently uses Cloudflare Pages, Render Free, dedicated Supabase Free, GitHub Actions, Binance REST, and bounded Gemini usage. Render cold start does not control the research schedule.

### Production Research

Production development consistently requires isolated staging and production environments, protected CI/CD, manual approval, managed backups, measured recovery, SLOs, incident routing, Auth/RLS review, privacy review, and cost planning.

No production document authorizes private Binance execution or live capital.

## Documentation Coverage

| Area | Authoritative document | Status |
|---|---|---|
| Product and experiment | `PRODUCT_REQUIREMENTS.md` | Complete pre-implementation baseline |
| Local development | `LOCAL_DEVELOPMENT.md` | Complete specification |
| Test environments | `TEST_ENVIRONMENTS.md` | Complete specification |
| Free cloud topology | `FREE_CLOUD_ARCHITECTURE.md` | Complete specification |
| Free cloud requirements | `FREE_CLOUD_REQUIREMENTS.md` | Complete refinement |
| Runtime architecture | `ARCHITECTURE.md` | Free-cloud aligned |
| Deployment lifecycle | `DEPLOYMENT.md` | Local through production research aligned |
| Production development | `PRODUCTION_DEVELOPMENT.md` | Complete planning baseline |
| Test strategy | `TESTING.md` | Environment-aligned |
| Coding-agent rules | `/AGENTS.md` | Environment-aligned |
| Shared domain tasks | `/TASKS.md` | Detailed baseline |
| Cloud deployment tasks | `/CLOUD_MVP_TASKS.md` | Detailed active sequence |
| Local and production tasks | `/LOCAL_AND_PRODUCTION_TASKS.md` | Detailed active sequence |
| Roadmap | `/ROADMAP.md` | Full lifecycle aligned |
| README inventory | `/README.md` | Matches authoritative document set |

## Known Implementation-Dependent Artifacts

These remain intentionally incomplete until code or environments exist:

- package lock files;
- local command scripts;
- `supabase/config.toml`, migrations, RLS SQL, and seed data;
- exact CI workflow YAML;
- generated OpenAPI and API inventory;
- frontend build and E2E configuration;
- Render and Cloudflare deployment files;
- actual cloud project references and public URLs;
- provider smoke evidence;
- backup/export and restore evidence;
- staging and production infrastructure selections;
- measured SLO, RPO, RTO, performance, and cost evidence;
- production security and privacy review results.

These are implementation deliverables, not missing prose. Their tasks require documentation to be updated in the same change.

## Audit Rules for Future Changes

1. Verify README links and inventory.
2. Verify new work is placed in the correct task source.
3. Verify local, CI, demo, paper, staging, and production credentials remain isolated.
4. Verify normal CI does not require paid APIs or production data.
5. Verify migrations, RLS, and frontend secret controls stay synchronized.
6. Verify free-tier infrastructure is not represented as an SLA.
7. Verify production research remains separate from private exchange and live trading.
8. Verify backup claims include restore evidence.
9. Verify financial side effects remain idempotent, risk-gated, and ledger-reconciled.
10. Verify Gemini remains advisory and cost-bounded.
11. Record material changes in `CHANGELOG.md`.

## Conclusion

The documentation is coherent for beginning local implementation, constructing the free cloud demo, running the controlled paper experiment, and continuing afterward into staging and a production-grade research service.

Recommended implementation order:

1. `T1.1-T1.2`;
2. `L1.1-L1.4`;
3. applicable shared domain tasks;
4. `C1-C8`;
5. `L2.1-L2.6` before the formal experiment;
6. post-experiment review;
7. `P1.1-P1.7` for staging and production research.
