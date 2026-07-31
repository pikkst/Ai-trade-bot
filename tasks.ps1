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
  bootstrap         Install dependencies and verify tools
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
  help              Show this help
"@
}

switch ($Command) {
    "bootstrap" {
        Write-Host "==> Verifying Python 3.12..." -ForegroundColor Cyan
        python --version
        Write-Host "==> Installing backend dependencies..." -ForegroundColor Cyan
        Set-Location backend; python -m pip install -e ".[dev]"; Set-Location ..
        Write-Host "==> Installing frontend dependencies..." -ForegroundColor Cyan
        Set-Location frontend; npm install; Set-Location ..
        Write-Host "==> Bootstrap complete." -ForegroundColor Green
    }
    "format" {
        Write-Host "==> Formatting backend..." -ForegroundColor Cyan
        Set-Location backend; ruff format .; Set-Location ..
        Write-Host "==> Formatting complete." -ForegroundColor Green
    }
    "lint" {
        Write-Host "==> Linting backend..." -ForegroundColor Cyan
        Set-Location backend; ruff check .; Set-Location ..
        Write-Host "==> Lint complete." -ForegroundColor Green
    }
    "type-check" {
        Write-Host "==> Type-checking backend..." -ForegroundColor Cyan
        Set-Location backend; mypy app; Set-Location ..
        Write-Host "==> Type-check complete." -ForegroundColor Green
    }
    "test" {
        Write-Host "==> Running tests..." -ForegroundColor Cyan
        Set-Location backend; python -m pytest tests/ -v; Set-Location ..
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
    "help" { Show-Help }
    default {
        if (-not $Command) { Show-Help }
        else { Write-Host "Unknown command: $Command" -ForegroundColor Red; Show-Help; exit 1 }
    }
}