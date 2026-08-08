.PHONY: bootstrap toolchain-bootstrap format lint type-check test local-up local-down local-migrate local-seed local-reset alembic-upgrade database-test api-dev frontend-dev frontend-build frontend-test frontend-bundle-scan research-cycle all-checks quality help export-test restore-test security-test frontend-audit docs-check unit-test integration-test contract-test e2e-test lock lock-check format-check

PYTHON := python3
PIP := $(PYTHON) -m pip
PIP_VERSION := 25.3
PIP_TOOLS_VERSION := 7.6.0
FRONTEND := frontend
NODE_LTS_ACCEPTED := 20 22 24
LOCAL_DATABASE_URL ?= postgresql+psycopg://postgres:postgres@127.0.0.1:54322/postgres

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-22s %s\n", $$1, $$2}'

toolchain-bootstrap: ## Install the pinned Python packaging toolchain
	$(PIP) install --upgrade "pip==$(PIP_VERSION)"
	$(PIP) install "pip-tools==$(PIP_TOOLS_VERSION)"

lock: ## Regenerate the Python lock file under Python 3.12
	@$(PYTHON) --version 2>&1 | grep -q "Python 3.12" || { echo "ERROR: Python 3.12 is required to regenerate the lock file."; exit 1; }
	$(MAKE) toolchain-bootstrap
	cd backend && $(PYTHON) -m piptools compile --extra=dev --output-file=requirements.txt pyproject.toml
	$(PYTHON) infrastructure/scripts/normalize_python_lock.py backend/requirements.txt
	@echo "==> Python lock file regenerated under Python 3.12."

lock-check: ## Fail when either dependency lock is stale
	@backup=$$(mktemp); cp backend/requirements.txt "$$backup"; \
	set -e; trap 'cp "$$backup" backend/requirements.txt; rm -f "$$backup"' EXIT; \
	$(MAKE) lock; \
	git diff --exit-code -- backend/requirements.txt
	cd $(FRONTEND) && npm ci

bootstrap: ## Install dependencies and verify tools (L1.1)
	@echo "==> Verifying prerequisites..."
	@command -v git >/dev/null 2>&1 || { echo "ERROR: Git is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@$(PYTHON) --version 2>&1 | grep -q "Python 3.12" || { echo "ERROR: Python 3.12 is required. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@$(PYTHON) -m pip --version >/dev/null 2>&1 || { echo "ERROR: pip is not available. Install Python 3.12 with pip."; exit 1; }
	@node --version >/dev/null 2>&1 || { echo "ERROR: Node.js is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@node_major=$$(node -p "process.versions.node.split('.')[0]"); accepted=0; for v in $(NODE_LTS_ACCEPTED); do if [ "$$node_major" = "$$v" ]; then accepted=1; fi; done; if [ "$$accepted" -ne 1 ]; then echo "ERROR: Node.js LTS ($(NODE_LTS_ACCEPTED)) is required. Found: $$(node --version) (major: $$node_major)"; exit 1; fi
	@npm --version >/dev/null 2>&1 || { echo "ERROR: npm is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@docker compose version >/dev/null 2>&1 || { echo "ERROR: Docker Compose v2 is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@supabase --version >/dev/null 2>&1 || { echo "ERROR: Supabase CLI is not installed. See docs/LOCAL_DEVELOPMENT.md"; exit 1; }
	@echo "==> All prerequisites verified."
	@echo "==> Creating local environment files from examples..."
	@if [ ! -f .env.local ]; then cp .env.example .env.local; echo "Created .env.local"; else echo ".env.local already exists, skipping"; fi
	@if [ ! -f .env.test ]; then cp .env.example .env.test; echo "Created .env.test"; else echo ".env.test already exists, skipping"; fi
	@echo "==> Installing pinned Python packaging tools..."
	$(MAKE) toolchain-bootstrap
	@echo "==> Installing backend dependencies..."
	cd backend && $(PIP) install -r requirements.txt
	@echo "==> Installing frontend dependencies..."
	cd $(FRONTEND) && npm ci
	@echo "==> Bootstrap complete."

format: ## Format supported languages
	cd backend && ruff format app tests ../infrastructure/scripts
	cd $(FRONTEND) && npx prettier --write .

format-check: ## Check formatting without modifying files
	cd backend && ruff format --check app tests ../infrastructure/scripts
	cd $(FRONTEND) && npx prettier --check .

lint: ## Run lint checks
	cd backend && ruff check app tests ../infrastructure/scripts
	cd $(FRONTEND) && npm run lint

type-check: ## Run static type checks
	cd backend && mypy app ../infrastructure/scripts
	cd $(FRONTEND) && npm run type-check

test: ## Run unit and property tests
	cd backend && $(PYTHON) -m pytest tests/ -v
	cd $(FRONTEND) && npm test

unit-test: ## Run backend unit tests
	cd backend && $(PYTHON) -m pytest tests/unit/ -v

integration-test: ## Run backend integration tests
	cd backend && $(PYTHON) -m pytest --no-cov tests/integration/ -v

contract-test: ## Run backend contract tests
	cd backend && $(PYTHON) -m pytest --no-cov tests/contract/ -v

e2e-test: ## Run E2E tests (not implemented in M001)
	@echo "ERROR: E2E tests not yet implemented. See M002+ for test infrastructure."
	exit 1

local-up: ## Start local Supabase and apply migrations and seed when needed
	@echo "==> Starting local Supabase stack..."
	supabase start
	@echo "==> Local services started."

local-down: ## Stop local Supabase while preserving local state
	@echo "==> Stopping local Supabase stack..."
	supabase stop
	@echo "==> Local services stopped."

local-migrate: ## Apply pending migrations to the running local Supabase database
	supabase migration up --local

local-reset: ## Recreate local database, apply all migrations, and run deterministic seed
	supabase db reset --local
	@echo "==> Local reset complete."

local-seed: local-reset ## Reapply the deterministic seed from an empty local database

alembic-upgrade: ## Upgrade an empty PostgreSQL database to the Alembic migration head
	cd backend && DATABASE_URL="$(LOCAL_DATABASE_URL)" $(PYTHON) -m alembic -c alembic.ini upgrade head

database-test: ## Run M003 database, transaction, workspace, and RLS integration tests
	cd backend && TEST_DATABASE_URL="$(LOCAL_DATABASE_URL)" $(PYTHON) -m pytest --no-cov -m database tests/integration/ -v

api-dev: ## Run FastAPI with reload
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Run Vite development server
	cd $(FRONTEND) && npm run dev

frontend-build: ## Build the frontend production bundle
	cd $(FRONTEND) && npm run build
	python infrastructure/scripts/scan_bundle_secrets.py $(FRONTEND)/dist

frontend-bundle-scan: ## Scan frontend bundle for leaked server secrets
	python infrastructure/scripts/scan_bundle_secrets.py $(FRONTEND)/dist

frontend-test: ## Run frontend tests
	cd $(FRONTEND) && npm test

research-cycle: ## Run one deterministic research cycle
	cd backend && $(PYTHON) -m app.cli.run_research_cycle --experiment-id dummy --occurrence 2026-01-01T00:00:00Z

quality: format-check lint type-check test contract-test frontend-build docs-check ## Run the deterministic baseline quality gate

all-checks: quality ## Run the local pre-push quality gate

security-test: ## Run static analysis and Python dependency audit
	cd backend && bandit -r app/ ../infrastructure/scripts/
	cd backend && pip-audit --requirement requirements.txt

frontend-audit: ## Fail on moderate-or-higher frontend dependency findings
	cd $(FRONTEND) && npm audit --audit-level=moderate

docs-check: ## Run documentation and generated-artifact checks
	$(PYTHON) infrastructure/scripts/check_docs.py

export-test: ## Create a test logical export
	@echo "ERROR: Export test not yet implemented. See M002+ for test infrastructure."
	exit 1

restore-test: ## Restore and reconcile in isolation
	@echo "ERROR: Restore test not yet implemented. See M002+ for test infrastructure."
	exit 1