# Cloudflare Pages deployment configuration

## Build settings

- **Build command:** `cd frontend && npm run build`
- **Output directory:** `frontend/dist`
- **Root directory:** repository root

## Deployment

The `deploy-to-cloudflare-pages.yml` workflow handles automated deployment to Cloudflare Pages. It requires the following GitHub Secrets:

- `CF_API_TOKEN` — Cloudflare API token with Pages edit permissions
- `CF_ACCOUNT_ID` — Cloudflare account ID

The frontend is built with Vite and the output is deployed to the `the-daily-roast` Cloudflare Pages project.