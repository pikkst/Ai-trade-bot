# Deployment

## Environments
- Local: Docker Compose, public or mock data, optional local LLM
- CI: ephemeral PostgreSQL and Redis, fake exchange and AI
- Sandbox: persistent environment, restricted credentials, full monitoring
- Future production: isolated execution service, managed secrets, encrypted backups, restricted network access

## Services
`api`, `worker`, `scheduler`, `postgres`, `redis`, `prometheus`, `grafana`, and optional `ollama`.

Deployments require migrations, health checks, rollback plan, backup verification, release checklist, and explicit environment separation.
