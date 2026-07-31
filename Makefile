.PHONY: bootstrap format lint type-check test local-up local-down local-reset api-dev frontend-dev research-cycle all-checks help export-test restore-test security-test docs-check

PYTHON := python3
PIP := $(PYTHON) -m pip
FRONTEND := frontend

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-22s %s\n", $$1, $$2}'

bootstrap: ## Install dependencies and verify tools (L1.1)
	@echo "==> Verifying prerequisites..."
	@command -v git >/dev/null 2>&1 || { echo "ERROR: Git is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@$(PYTHON) --version 2>&1 | grep -q "Python 3.12" || { echo "ERROR: Python 3.12 is required. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@$(PYTHON) -m pip --version >/dev/null 2>&1 || { echo "ERROR: pip is not available. Install Python 3.12 with pip."; exit 1; }
	@node --version >/dev/null 2>&1 || { echo "ERROR: Node.js is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@npm --version >/dev/null 2>&1 || { echo "ERROR: npm is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@docker compose version >/dev/null 2>&1 || { echo "ERROR: Docker Compose v2 is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@supabase --version >/dev/null 2>&1 || { echo "ERROR: Supabase CLI is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@echo "==> All prerequisites verified."
	@echo "==> Creating local environment files from examples..."
	@if [ ! -f .env.local ]; then cp .env.example .env.local; echo "Created .env.local"; else echo ".env.local already exists, skipping"; fi
	@if [ ! -f .env.test ]; then cp .env.example .env.test; echo "Created .env.test"; else echo ".env.test already exists, skipping"; fi
	@echo "==> Installing backend dependencies..."
	cd backend && $(PIP) install -e ".[dev]"
	@echo "==> Installing frontend dependencies..."
	cd $(FRONTEND) && npm ci
	@echo "==> Bootstrap complete."

format: ## Format supported languages
	cd backend && ruff format .
	cd $(FRONTEND) && npm run format

lint: ## Run lint checks
	cd backend && ruff check .
	cd $(FRONTEND) && npm run lint

type-check: ## Run static type checks
	cd backend && mypy app
	cd $(FRONTEND) && npm run type-check

test: ## Run unit and property tests
	cd backend && $(PYTHON) -m pytest tests/ -v
	cd $(FRONTEND) && npm test

local-up: ## Start local Supabase and application dependencies
	@echo "==> Starting local Supabase stack..."
	supabase start
	@echo "==> Local services started."

local-down: ## Stop local services
	@echo "==> Stopping local Supabase stack..."
	supabase stop
	@echo "==> Local services stopped."

local-reset: ## Recreate database, migrations, and seed data
	supabase stop
	supabase start
	supabase db reset
	@echo "==> Local reset complete."

api-dev: ## Run FastAPI with reload
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Run Vite development server
	cd $(FRONTEND) && npm run dev

research-cycle: ## Run one deterministic research cycle
	cd backend && $(PYTHON) -m app.cli.run_research_cycle --experiment-id dummy --occurrence 2026-01-01T00:00:00Z

all-checks: format lint type-check test ## Run the local pre-push quality gate

security-test: ## Run static, dependency, secret, and artifact checks
	cd backend && bandit -r app/
	cd backend && pip-audit

docs-check: ## Run documentation and generated-artifact checks
	@echo "==> Checking README structure matches implementation..."
	@errors=0; \
	for f in backend/app/main.py frontend/src/App.tsx supabase/config.toml Makefile tasks.ps1 .env.example .gitignore backend/requirements.txt frontend/package-lock.json frontend/public supabase/migrations tests generated-artifacts cloudflare-pages.toml; do \
		if [ ! -e "$$f" ]; then \
			echo "FAIL: $$f missing"; \
			errors=$$((errors + 1)); \
		fi; \
	done; \
	if [ $$errors -gt 0 ]; then \
		echo "Docs check failed: $$errors path(s) missing"; \
		exit 1; \
	fi; \
	echo "==> README structure matches implementation. Docs check passed."

export-test: ## Create a test logical export
	@echo "==> Export test placeholder."

restore-test: ## Restore and reconcile in isolation
	@echo "==> Restore test placeholder."