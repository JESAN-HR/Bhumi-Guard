$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$bundle = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies'
if (Get-Command python -ErrorAction SilentlyContinue) { $pythonCommand = 'python' }
elseif (Test-Path "$bundle/python/python.exe") { $pythonCommand = "$bundle/python/python.exe" }
else { throw 'Install Python 3.12 or newer.' }
if (!(Test-Path '.venv/Scripts/python.exe')) { & $pythonCommand -m venv .venv }
$pythonCommand = (Resolve-Path '.venv/Scripts/python.exe').Path
if (!(Test-Path 'frontend/dist/index.html')) {
  throw 'Build frontend first: cd frontend; pnpm install --frozen-lockfile; pnpm build. See README.'
}
& $pythonCommand -m alembic -c backend/alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Migration failed' }
if (!(Test-Path 'runtime/demo.db') -or !(Test-Path 'runtime/local-account.txt')) {
  Write-Host 'If no reviewer exists, run python -m backend.app.seed first.'
}
& $pythonCommand -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
