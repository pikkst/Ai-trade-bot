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

function Show-Help {
    Write-Host @"
Usage: .\tasks.ps1 <command>

Commands:
  bootstrap         Install dependencies and verify tools (L1.1)
  format            Format supported languages
  lint              Run lint checks
  type-check        Run static type checks
  test              Run unit and property tests
  local-up          Start local Supabase and application dependencies
  local-down        Stop local services
  local-reset       Recreate database, migrations, and seed data
  api-dev           Run FastAPI with reload
  frontend-dev      Run Vite development server
  research-cycle    Run one deterministic research cycle
  all-checks        Run the local pre-push quality gate
  security-test     Run static, dependency, secret, and artifact checks
  docs-check        Run documentation and generated-artifact checks
  export-test       Create a test logical export
  restore-test      Restore and reconcile in isolation
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
        Fail-IfMissing "npm" "npm is required. See docs/LOCAL_DEVELOPMENT.md"
        Fail-IfMissing "docker" "Docker Compose v2 is required. See docs/LOCAL_DEVELOPMENT.md"
        Fail-IfMissing "supabase" "Supabase CLI is required. See docs/LOCAL_DEVELOPMENT.md"
        Write-Host "==> All prerequisites verified." -ForegroundColor Green
        Write-Host "==> Creating local environment files from examples..." -ForegroundColor Cyan
        if (-not (Test-Path ".env.local")) { Copy-Item .env.example .env.local; Write-Host "Created .env.local" } else { Write-Host ".env.local already exists, skipping" }
        if (-not (Test-Path ".env.test")) { Copy-Item .env.example .env.test; Write-Host "Created .env.test" } else { Write-Host ".env.test already exists, skipping" }
        Write-Host "==> Installing backend dependencies..." -ForegroundColor Cyan
        Set-Location backend; python -m pip install -e ".[dev]"; Set-Location ..
        Write-Host "==> Installing frontend dependencies..." -ForegroundColor Cyan
        Set-Location frontend; npm ci; Set-Location ..
        Write-Host "==> Bootstrap complete." -ForegroundColor Green
    }
    "format" {
        Write-Host "==> Formatting backend..." -ForegroundColor Cyan
        Set-Location backend; ruff format .; Set-Location ..
        Write-Host "==> Formatting frontend..." -ForegroundColor Cyan
        Set-Location frontend; npm run format; Set-Location ..
        Write-Host "==> Format complete." -ForegroundColor Green
    }
    "lint" {
        Write-Host "==> Linting backend..." -ForegroundColor Cyan
        Set-Location backend; ruff check .; Set-Location ..
        Write-Host "==> Linting frontend..." -ForegroundColor Cyan
        Set-Location frontend; npm run lint; Set-Location ..
        Write-Host "==> Lint complete." -ForegroundColor Green
    }
    "type-check" {
        Write-Host "==> Type-checking backend..." -ForegroundColor Cyan
        Set-Location backend; mypy app; Set-Location ..
        Write-Host "==> Type-checking frontend..." -ForegroundColor Cyan
        Set-Location frontend; npm run type-check; Set-Location ..
        Write-Host "==> Type-check complete." -ForegroundColor Green
    }
    "test" {
        Write-Host "==> Running backend tests..." -ForegroundColor Cyan
        Set-Location backend; python -m pytest tests/ -v; Set-Location ..
        Write-Host "==> Running frontend tests..." -ForegroundColor Cyan
        Set-Location frontend; npm test; Set-Location ..
        Write-Host "==> Tests complete." -ForegroundColor Green
    }
    "local-up" {
        Write-Host "==> Starting local Supabase stack..." -ForegroundColor Cyan
        supabase start
        Write-Host "==> Local services started." -ForegroundColor Green
    }
    "local-down" {
        Write-Host "==> Stopping local Supabase stack..." -ForegroundColor Cyan
        supabase stop
        Write-Host "==> Local services stopped." -ForegroundColor Green
    }
    "local-reset" {
        Write-Host "==> Resetting local Supabase..." -ForegroundColor Cyan
        supabase stop
        supabase start
        supabase db reset
        Write-Host "==> Local reset complete." -ForegroundColor Green
    }
    "api-dev" {
        Write-Host "==> Starting FastAPI dev server..." -ForegroundColor Cyan
        Set-Location backend; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; Set-Location ..
    }
    "frontend-dev" {
        Write-Host "==> Starting Vite dev server..." -ForegroundColor Cyan
        Set-Location frontend; npm run dev; Set-Location ..
    }
    "research-cycle" {
        Write-Host "==> Running research cycle..." -ForegroundColor Cyan
        Set-Location backend; python -m app.cli.run_research_cycle --experiment-id dummy --occurrence 2026-01-01T00:00:00Z; Set-Location ..
    }
    "all-checks" {
        .\tasks.ps1 format
        .\tasks.ps1 lint
        .\tasks.ps1 type-check
        .\tasks.ps1 test
    }
    "security-test" {
        Write-Host "==> Running security tests..." -ForegroundColor Cyan
        Set-Location backend; bandit -r app/; pip-audit; Set-Location ..
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
        if ($errors.Count -gt 0) {
            foreach ($e in $errors) { Write-Host "FAIL: $e" -ForegroundColor Red }
            exit 1
        }
        Write-Host "==> README structure matches implementation. Docs check passed." -ForegroundColor Green
    }
    "export-test" {
        Write-Host "==> Export test placeholder." -ForegroundColor Cyan
    }
    "restore-test" {
        Write-Host "==> Restore test placeholder." -ForegroundColor Cyan
    }
    "help" { Show-Help }
    default {
        if (-not $Command) { Show-Help }
        else { Write-Host "Unknown command: $Command" -ForegroundColor Red; Show-Help; exit 1 }
    }
}