# Start AI Lab hub: FastAPI (8080) + Next.js (3000) in separate windows.
param(
    [switch]$NoKill,
    [switch]$OpenBrowser,
    [int]$ApiPort = 8080,
    [int]$WebPort = 3000
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$WebRoot = Join-Path $RepoRoot "web"

function Stop-PortListener {
    param([int]$Port)
    for ($i = 0; $i -lt 3; $i++) {
        $pids = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) {
            if ($procId -and $procId -ne 0) {
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Milliseconds 500
    }
}

function Stop-LabApiProcesses {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -eq "python.exe" -and (
                $_.CommandLine -match "uvicorn\s+api\.main:app" -or
                $_.CommandLine -match "multiprocessing\.spawn"
            )
        } |
        ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
}

function Wait-HttpOk {
    param(
        [string]$Url,
        [int]$MaxSeconds = 90,
        [string]$ExpectedRevision = ""
    )
    $deadline = (Get-Date).AddSeconds($MaxSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) {
                if ($ExpectedRevision) {
                    $body = $r.Content | ConvertFrom-Json
                    if ($body.revision -eq $ExpectedRevision) {
                        return $true
                    }
                } else {
                    return $true
                }
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    return $false
}

Set-Location $RepoRoot

if (-not $NoKill) {
    Write-Host "Stopping old API processes and freeing ports $ApiPort and $WebPort..." -ForegroundColor DarkGray
    Stop-LabApiProcesses
    Stop-PortListener -Port $ApiPort
    Stop-PortListener -Port $WebPort
    Start-Sleep -Seconds 2
}

Write-Host "Starting API on port $ApiPort..." -ForegroundColor Cyan
$apiCmd = @"
Set-Location '$RepoRoot'
`$env:LLM_PROVIDER = 'groq'
Write-Host 'AI Lab API — http://127.0.0.1:$ApiPort/health' -ForegroundColor Green
python -m uvicorn api.main:app --host 0.0.0.0 --port $ApiPort --reload --reload-dir api --reload-dir shared --reload-dir "Style Finder"
"@
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $apiCmd)

Write-Host "Waiting for API health..." -ForegroundColor DarkGray
if (-not (Wait-HttpOk -Url "http://127.0.0.1:$ApiPort/health" -ExpectedRevision "vision-qwen-1")) {
    Write-Host "API did not become ready on port $ApiPort (or an old API is still bound)." -ForegroundColor Red
    Write-Host "Close any other PowerShell windows running uvicorn, then run this script again." -ForegroundColor Yellow
    exit 1
}
Write-Host "API ready." -ForegroundColor Green

if (-not (Test-Path (Join-Path $WebRoot "node_modules"))) {
    Write-Host "Installing web dependencies (first run)..." -ForegroundColor Cyan
    Set-Location $WebRoot
    npm install
    Set-Location $RepoRoot
}

Write-Host "Starting Next.js on port $WebPort..." -ForegroundColor Cyan
$webCmd = @"
Set-Location '$WebRoot'
Write-Host 'AI Lab UI — http://localhost:$WebPort' -ForegroundColor Green
Write-Host 'API proxy — http://localhost:$WebPort/api/hub/health' -ForegroundColor DarkGray
npx next dev --webpack -p $WebPort
"@
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $webCmd)

Write-Host "Waiting for UI + proxy..." -ForegroundColor DarkGray
if (-not (Wait-HttpOk -Url "http://localhost:$WebPort/api/hub/health")) {
    Write-Host "Next.js proxy did not become ready on port $WebPort." -ForegroundColor Red
    Write-Host "Check the Next.js window for errors (try: cd web; npx next dev --webpack)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "AI Lab is running." -ForegroundColor Green
Write-Host "  Hub:    http://localhost:$WebPort" -ForegroundColor White
Write-Host "  API:    http://127.0.0.1:$ApiPort/health" -ForegroundColor White
Write-Host "  Proxy:  http://localhost:$WebPort/api/hub/health" -ForegroundColor White
Write-Host ""
Write-Host "Leave both PowerShell windows open. Stop with Ctrl+C in each." -ForegroundColor DarkGray

if ($OpenBrowser) {
    Start-Process "http://localhost:$WebPort"
}
