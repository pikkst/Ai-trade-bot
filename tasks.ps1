<#
.SYNOPSIS
    The Daily Roast AI — Repository Commands (PowerShell)
.DESCRIPTION
    Cross-platform repository commands for Windows PowerShell.
    Run: .\tasks.ps1 <command>
#>

param(
    [Parameter(Position = 0)]
    [string]$Command
)

$ErrorActionPreference = "Stop"
$NODE_LTS_ACCEPTED = @(20, 22, 24)

function Invoke-Native {
    param(
        [string]$Name,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )
    try {
        & $Name @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "$Name exited with code $LASTEXITCODE"
        }
    } finally {
    }
}

function Show-Help {
    Write-Host @"
Usage: .\tasks.ps1 <command>

Commands:
  bootstrap         Install dependencies and verify tools (L1.1)
  lock              Regenerate the Python lock file under Python 3.12
  format            Format supported languages
  format-check      Check formatting without modifying files
  lint              Run lint checks
  type-check        Run static type checks
  test              Run unit and property tests
  unit-test         Run backend unit tests
  integration-test  Run backend integration tests
  contract-test     Run backend contract tests
  e2e-test          Run E2E tests (not implemented in M001)
  local-up          Start local Supabase and application dependencies
  local-down        Stop local services
  local-reset       Recreate database, migrations, and seed data
  api-dev           Run FastAPI with reload
  frontend-dev      Run Vite development server
  frontend-build    Build the frontend production bundle
  frontend-test     Run frontend tests
  research-cycle    Run one deterministic research cycle
  all-checks        Run the local pre-push quality gate
  security-test     Run static, dependency, secret, and artifact checks
  docs-check        Run documentation and generated-artifact checks
  export-test       Create a test logical export (not implemented in M001)
  restore-test      Restore and reconcile in isolation (not implemented in M001)
  help              Show this help
"@
}

function Fail-IfMissing {
    param([string]$Tool, [string]$Message)
    if (-not (Get-Command $Tool -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: $Tool is not installed. $Message" -ForegroundColor Red
        exit 1
    }
}

switch ($Command) {
    "bootstrap" {
        Write-Host "==> Verifying prerequisites..." -ForegroundColor Cyan
        Fail-IfMissing "git" "See docs/LOCAL_DEVELOPMENT.md"
        Fail-IfMissing "python" "Python 3.12 is required. See docs/LOCAL_DEVELOPMENT.md"
        $pyVersion = python --version 2>&1
        if ($pyVersion -notmatch "Python 3\.12") {
            Write-Host "ERROR: Python 3.12 is required. Found: $pyVersion" -ForegroundColor Red
            exit 1
        }
        Fail-IfMissing "node" "Node.js LTS is required. See docs/LOCAL_DEVELOPMENT.md"
        $nodeVersion = node --version 2>&1
        $nodeMajor = [int]($nodeVersion -replace "v(\d+).*", '$1')
        $nodeAccepted = $NODE_LTS_ACCEPTED -contains $nodeMajor
        if (-not $nodeAccepted) {
            Write-Host "ERROR: Node.js LTS ($($NODE_LTS_ACCEPTED -join ', ')) is required. Found: $nodeVersion" -ForegroundColor Red
            exit 1
        }
        Fail-IfMissing "npm" "npm is required. See docs/LOCAL_DEVELOPMENT.md"
        Fail-IfMissing "docker" "Docker Compose v2 is required. See docs/LOCAL_DEVELOPMENT.md"
        $dockerComposeVersion = docker compose version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Docker Compose v2 is not installed. See docs/LOCAL_DEVELOPMENT.md" -ForegroundColor Red
            exit 1
        }
        Fail-IfMissing "supabase" "Supabase CLI is required. See docs/LOCAL_DEVELOPMENT.md"
        Write-Host "==> All prerequisites verified." -ForegroundColor Green
        Write-Host "==> Creating local environment files from examples..." -ForegroundColor Cyan
        if (-not (Test-Path ".env.local")) { Copy-Item .env.example .env.local; Write-Host "Created .env.local" } else { Write-Host ".env.local already exists, skipping" }
        if (-not (Test-Path ".env.test")) { Copy-Item .env.example .env.test; Write-Host "Created .env.test" } else { Write-Host ".env.test already exists, skipping" }
        Write-Host "==> Installing backend dependencies..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native python -m pip install -r requirements.txt } finally { Pop-Location }
        Write-Host "==> Installing frontend dependencies..." -ForegroundColor Cyan
        try { Push-Location frontend; Invoke-Native npm ci } finally { Pop-Location }
        Write-Host "==> Bootstrap complete." -ForegroundColor Green
    }
    "lock" {
        Write-Host "==> Regenerating Python lock file..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native python -m piptools compile --extra=dev --output-file=requirements.txt pyproject.toml } finally { Pop-Location }
        Write-Host "==> Lock file regenerated." -ForegroundColor Green
    }
    "format" {
        Write-Host "==> Formatting backend..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native ruff format . } finally { Pop-Location }
        Write-Host "==> Formatting frontend..." -ForegroundColor Cyan
        try { Push-Location frontend; Invoke-Native npx prettier --write . } finally { Pop-Location }
        Write-Host "==> Format complete." -ForegroundColor Green
    }
    "format-check" {
        Write-Host "==> Checking backend formatting..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native ruff format --check . } finally { Pop-Location }
        Write-Host "==> Checking frontend formatting..." -ForegroundColor Cyan
        try { Push-Location frontend; Invoke-Native npx prettier --check . } finally { Pop-Location }
        Write-Host "==> Format check complete." -ForegroundColor Green
    }
    "lint" {
        Write-Host "==> Linting backend..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native ruff check . } finally { Pop-Location }
        Write-Host "==> Linting frontend..." -ForegroundColor Cyan
        try { Push-Location frontend; Invoke-Native npm run lint } finally { Pop-Location }
        Write-Host "==> Lint complete." -ForegroundColor Green
    }
    "type-check" {
        Write-Host "==> Type-checking backend..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native mypy app } finally { Pop-Location }
        Write-Host "==> Type-checking frontend..." -ForegroundColor Cyan
        try { Push-Location frontend; Invoke-Native npm run type-check } finally { Pop-Location }
        Write-Host "==> Type-check complete." -ForegroundColor Green
    }
    "test" {
        Write-Host "==> Running backend tests..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native python -m pytest tests/ -v } finally { Pop-Location }
        Write-Host "==> Running frontend tests..." -ForegroundColor Cyan
        try { Push-Location frontend; Invoke-Native npm test } finally { Pop-Location }
        Write-Host "==> Tests complete." -ForegroundColor Green
    }
    "unit-test" {
        Write-Host "==> Running backend unit tests..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native python -m pytest tests/unit/ -v } finally { Pop-Location }
    }
    "integration-test" {
        Write-Host "==> Running backend integration tests..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native python -m pytest tests/integration/ -v } finally { Pop-Location }
    }
    "contract-test" {
        Write-Host "==> Running backend contract tests..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native python -m pytest tests/contract/ -v } finally { Pop-Location }
    }
    "e2e-test" {
        Write-Host "ERROR: E2E tests not yet implemented. See M002+ for test infrastructure." -ForegroundColor Red
        exit 1
    }
    "local-up" {
        Write-Host "==> Starting local Supabase stack..." -ForegroundColor Cyan
        Invoke-Native supabase start
        Write-Host "==> Local services started." -ForegroundColor Green
    }
    "local-down" {
        Write-Host "==> Stopping local Supabase stack..." -ForegroundColor Cyan
        Invoke-Native supabase stop
        Write-Host "==> Local services stopped." -ForegroundColor Green
    }
    "local-reset" {
        Write-Host "==> Resetting local Supabase..." -ForegroundColor Cyan
        Invoke-Native supabase stop
        Invoke-Native supabase start
        Invoke-Native supabase db reset
        Write-Host "==> Local reset complete." -ForegroundColor Green
    }
    "api-dev" {
        Write-Host "==> Starting FastAPI dev server..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 } finally { Pop-Location }
    }
    "frontend-dev" {
        Write-Host "==> Starting Vite dev server..." -ForegroundColor Cyan
        try { Push-Location frontend; Invoke-Native npm run dev } finally { Pop-Location }
    }
    "frontend-build" {
        Write-Host "==> Building frontend..." -ForegroundColor Cyan
        try { Push-Location frontend; Invoke-Native npm run build } finally { Pop-Location }
    }
    "frontend-test" {
        Write-Host "==> Running frontend tests..." -ForegroundColor Cyan
        try { Push-Location frontend; Invoke-Native npm test } finally { Pop-Location }
    }
    "research-cycle" {
        Write-Host "==> Running research cycle..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native python -m app.cli.run_research_cycle --experiment-id dummy --occurrence 2026-01-01T00:00:00Z } finally { Pop-Location }
    }
    "all-checks" {
        .\tasks.ps1 format-check
        .\tasks.ps1 lint
        .\tasks.ps1 type-check
        .\tasks.ps1 test
        .\tasks.ps1 frontend-build
        .\tasks.ps1 frontend-test
    }
    "security-test" {
        Write-Host "==> Running security tests..." -ForegroundColor Cyan
        try { Push-Location backend; Invoke-Native bandit -r app/; Invoke-Native pip-audit } finally { Pop-Location }
    }
    "docs-check" {
        Write-Host "==> Checking README structure matches implementation..." -ForegroundColor Cyan
        $errors = @()
        if (-not (Test-Path "backend/app/main.py")) { $errors += "backend/app/main.py missing" }
        if (-not (Test-Path "frontend/src/App.tsx")) { $errors += "frontend/src/App.tsx missing" }
        if (-not (Test-Path "supabase/config.toml")) { $errors += "supabase/config.toml missing" }
        if (-not (Test-Path "Makefile")) { $errors += "Makefile missing" }
        if (-not (Test-Path "tasks.ps1")) { $errors += "tasks.ps1 missing" }
        if (-not (Test-Path ".env.example")) { $errors += ".env.example missing" }
        if (-not (Test-Path ".gitignore")) { $errors += ".gitignore missing" }
        if (-not (Test-Path "backend/requirements.txt")) { $errors += "backend/requirements.txt missing" }
        if (-not (Test-Path "frontend/package-lock.json")) { $errors += "frontend/package-lock.json missing" }
        if (-not (Test-Path "frontend/public")) { $errors += "frontend/public/ missing" }
        if (-not (Test-Path "supabase/migrations")) { $errors += "supabase/migrations/ missing" }
        if (-not (Test-Path "tests")) { $errors += "tests/ missing" }
        if (-not (Test-Path "generated-artifacts")) { $errors += "generated-artifacts/ missing" }
        if (-not (Test-Path "cloudflare-pages.toml")) { $errors += "cloudflare-pages.toml missing" }
        if (-not (Test-Path "frontend/.prettierrc")) { $errors += "frontend/.prettierrc missing" }
        if (-not (Test-Path "frontend/vitest.config.ts")) { $errors += "frontend/vitest.config.ts missing" }
        if (-not (Test-Path "backend/app/cli/run_research_cycle.py")) { $errors += "backend/app/cli/run_research_cycle.py missing" }
        if (-not (Test-Path "backend/tests/unit/test_main.py")) { $errors += "backend/tests/unit/test_main.py missing" }
        if ($errors.Count -gt 0) {
            foreach ($e in $errors) { Write-Host "FAIL: $e" -ForegroundColor Red }
            exit 1
        }
        Write-Host "==> README structure matches implementation. Docs check passed." -ForegroundColor Green
    }
    "export-test" {
        Write-Host "ERROR: Export test not yet implemented. See M002+ for test infrastructure." -ForegroundColor Red
        exit 1
    }
    "restore-test" {
        Write-Host "ERROR: Restore test not yet implemented. See M002+ for test infrastructure." -ForegroundColor Red
        exit 1
    }
    "help" { Show-Help }
    default {
        if (-not $Command) { Show-Help }
        else { Write-Host "Unknown command: $Command" -ForegroundColor Red; Show-Help; exit 1 }
    }
}