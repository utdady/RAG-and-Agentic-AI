# AI Lab smoke workflow (repo root)
param(
    [switch]$Live,
    [switch]$IncludeSlow,
    [switch]$SkipImports
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "== Preflight ==" -ForegroundColor Cyan
$preflightArgs = @()
if ($SkipImports) { $preflightArgs += "--skip-imports" }
python -m api.diagnostics.preflight @preflightArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`n== Unit tests ==" -ForegroundColor Cyan
python -m pytest api/tests/test_preflight.py api/tests/test_adapters_unit.py -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Live) {
    Write-Host "`n== HTTP smoke ==" -ForegroundColor Cyan
    $smokeArgs = @("--base", "http://127.0.0.1:8080")
    if ($IncludeSlow) { $smokeArgs += "--include-slow" }
    python -m api.diagnostics.smoke @smokeArgs
    exit $LASTEXITCODE
}

Write-Host "`nDone. Start API and re-run with -Live for HTTP smoke tests." -ForegroundColor Green
