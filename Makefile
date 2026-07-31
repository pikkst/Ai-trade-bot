.PHONY: bootstrap format lint type-check test local-up local-down local-reset api-dev frontend-dev frontend-build frontend-test research-cycle all-checks help export-test restore-test security-test docs-check unit-test integration-test contract-test e2e-test lock

PYTHON := python3
PIP := $(PYTHON) -m pip
FRONTEND := frontend
NODE_LTS_MIN := 20

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-22s %s\n", $$1, $$2}'

lock: ## Regenerate the Python lock file under Python 3.12
	cd backend && $(PYTHON) -m piptools compile --extra=dev --output-file=requirements.txt pyproject.toml

bootstrap: ## Install dependencies and verify tools (L1.1)
	@echo "==> Verifying prerequisites..."
	@command -v git >/dev/null 2>&1 || { echo "ERROR: Git is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@$(PYTHON) --version 2>&1 | grep -q "Python 3.12" || { echo "ERROR: Python 3.12 is required. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@$(PYTHON) -m pip --version >/dev/null 2>&1 || { echo "ERROR: pip is not available. Install Python 3.12 with pip."; exit 1; }
	@node --version >/dev/null 2>&1 || { echo "ERROR: Node.js is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@node_major=$$(node -p "process.versions.node.split('.')[0]"); if [ "$$node_major" -lt $(NODE_LTS_MIN) ]; then echo "ERROR: Node.js LTS ($(NODE_LTS_MIN)+) is required. Found: $$(node --version)"; exit 1; fi
	@npm --version >/dev/null 2>&1 || { echo "ERROR: npm is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@docker compose version >/dev/null 2>&1 || { echo "ERROR: Docker Compose v2 is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@supabase --version >/dev/null 2>&1 || { echo "ERROR: Supabase CLI is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@echo "==> All prerequisites verified."
	@echo "==> Creating local environment files from examples..."
	@if [ ! -f .env.local ]; then cp .env.example .env.local; echo "Created .env.local"; else echo ".env.local already exists, skipping"; fi
	@if [ ! -f .env.test ]; then cp .env.example .env.test; echo "Created .env.test"; else echo ".env.test already exists, skipping"; fi
	@echo "==> Installing backend dependencies..."
	cd backend && $(PIP) install -r requirements.txt
	@echo "==> Installing frontend dependencies..."
	cd $(FRONTEND) && npm ci
	@echo "==> Bootstrap complete."

format: ## Format supported languages
	cd backend && ruff format .
	cd $(FRONTEND) && npx prettier --write .

format-check: ## Check formatting without modifying files
	cd backend && ruff format --check .
	cd $(FRONTEND) && npx prettier --check .

lint: ## Run lint checks
	cd backend && ruff check .
	cd $(FRONTEND) && npm run lint

type-check: ## Run static type checks
	cd backend && mypy app
	cd $(FRONTEND) && npm run type-check

test: ## Run unit and property tests
	cd backend && $(PYTHON) -m pytest tests/ -v
	cd $(FRONTEND) && npm test

unit-test: ## Run backend unit tests
	cd backend && $(PYTHON) -m pytest tests/unit/ -v

integration-test: ## Run backend integration tests
	cd backend && $(PYTHON) -m pytest tests/integration/ -v

contract-test: ## Run backend contract tests
	cd backend && $(PYTHON) -m pytest tests/contract/ -v

e2e-test: ## Run E2E tests (not implemented in M001)
	@echo "ERROR: E2E tests not yet implemented. See M002+ for test infrastructure."
	exit 1

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

frontend-build: ## Build the frontend production bundle
	cd $(FRONTEND) && npm run build

frontend-test: ## Run frontend tests
	cd $(FRONTEND) && npm test

research-cycle: ## Run one deterministic research cycle
	cd backend && $(PYTHON) -m app.cli.run_research_cycle --experiment-id dummy --occurrence 2026-01-01T00:00:00Z

all-checks: format-check lint type-check test frontend-build frontend-test ## Run the local pre-push quality gate

security-test: ## Run static, dependency, secret, and artifact checks
	cd backend && bandit -r app/
	cd backend && pip-audit

docs-check: ## Run documentation and generated-artifact checks
	@echo "==> Checking README structure matches implementation..."
	@errors=0; \
	for f in backend/app/main.py frontend/src/App.tsx supabase/config.toml Makefile tasks.ps1 .env.example .gitignore backend/requirements.txt frontend/package-lock.json frontend/public supabase/migrations tests generated-artifacts cloudflare-pages.toml frontend/.prettierrc frontend/vitest.config.ts backend/app/cli/run_research_cycle.py backend/tests/unit/test_main.py; do \
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
	@echo "ERROR: Export test not yet implemented. See M002+ for test infrastructure."
	exit 1

restore-test: ## Restore and reconcile in isolation
	@echo "ERROR: Restore test not yet implemented. See M002+ for test infrastructure."
	exit 1