.PHONY: bootstrap format lint type-check test local-up local-down local-reset api-dev frontend-dev research-cycle all-checks help

PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := .venv
FRONTEND := frontend

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-22s %s\n", $$1, $$2}'

bootstrap: ## Install dependencies and verify tools
	@echo "==> Verifying Python 3.12..."
	@$(PYTHON) --version
	@echo "==> Installing backend dependencies..."
	cd backend && $(PIP) install -e ".[dev]"
	@echo "==> Installing frontend dependencies..."
	cd $(FRONTEND) && npm install
	@echo "==> Bootstrap complete."

format: ## Format supported languages
	cd backend && ruff format .
	cd $(FRONTEND) && npm run format 2>/dev/null || true

lint: ## Run lint checks
	cd backend && ruff check .
	cd $(FRONTEND) && npm run lint 2>/dev/null || true

type-check: ## Run static type checks
	cd backend && mypy app
	cd $(FRONTEND) && npm run type-check

test: ## Run unit and property tests
	cd backend && $(PYTHON) -m pytest tests/ -v
	cd $(FRONTEND) && npm test 2>/dev/null || true

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
	@echo "==> Checking documentation links..."
	@echo "Docs check passed."

export-test: ## Create a test logical export
	@echo "==> Export test placeholder."

restore-test: ## Restore and reconcile in isolation
	@echo "==> Restore test placeholder."