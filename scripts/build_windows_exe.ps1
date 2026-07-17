$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendPath = Join-Path $projectRoot "frontend"
$backendPath = Join-Path $projectRoot "backend"

$pythonPath = Join-Path $backendPath ".venv\Scripts\python.exe"
$envPath = Join-Path $backendPath ".env"
$buildRequirementsPath = Join-Path $backendPath "requirements-build.txt"
$specPath = Join-Path $projectRoot "CyberClubManagerPro.spec"

$outputPath = Join-Path $projectRoot "dist\CyberClub Manager Pro"
$outputExePath = Join-Path $outputPath "CyberClub Manager Pro.exe"

Write-Host ""
Write-Host "CyberClub Manager Pro - Windows EXE build" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path -LiteralPath $frontendPath)) {
    throw "Frontend folder not found: $frontendPath"
}

if (-not (Test-Path -LiteralPath $backendPath)) {
    throw "Backend folder not found: $backendPath"
}

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Virtual environment Python not found: $pythonPath"
}

if (-not (Test-Path -LiteralPath $envPath)) {
    throw "backend\.env not found."
}

if (-not (Test-Path -LiteralPath $buildRequirementsPath)) {
    throw "requirements-build.txt not found."
}

if (-not (Test-Path -LiteralPath $specPath)) {
    throw "CyberClubManagerPro.spec not found."
}

$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue

if (-not $npmCommand) {
    throw "npm.cmd not found. Check Node.js installation."
}

Write-Host "1. Frontend lint..." -ForegroundColor Yellow
Set-Location -LiteralPath $frontendPath

& $npmCommand.Source run lint

if ($LASTEXITCODE -ne 0) {
    throw "Frontend lint failed with code $LASTEXITCODE."
}

Write-Host ""
Write-Host "2. Frontend build..." -ForegroundColor Yellow

& $npmCommand.Source run build

if ($LASTEXITCODE -ne 0) {
    throw "Frontend build failed with code $LASTEXITCODE."
}

$frontendIndex = Join-Path $frontendPath "dist\index.html"

if (-not (Test-Path -LiteralPath $frontendIndex)) {
    throw "frontend\dist\index.html was not created."
}

Write-Host ""
Write-Host "3. Backend tests..." -ForegroundColor Yellow
Set-Location -LiteralPath $backendPath

& $pythonPath -m pytest -q

if ($LASTEXITCODE -ne 0) {
    throw "Backend tests failed with code $LASTEXITCODE."
}

Write-Host ""
Write-Host "4. Installing PyInstaller..." -ForegroundColor Yellow

& $pythonPath -m pip install -r $buildRequirementsPath

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller installation failed with code $LASTEXITCODE."
}

Write-Host ""
Write-Host "5. Building Windows application..." -ForegroundColor Yellow
Set-Location -LiteralPath $projectRoot

& $pythonPath -m PyInstaller --noconfirm --clean $specPath

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with code $LASTEXITCODE."
}

if (-not (Test-Path -LiteralPath $outputPath)) {
    throw "Build folder not found: $outputPath"
}

if (-not (Test-Path -LiteralPath $outputExePath)) {
    throw "EXE file not found: $outputExePath"
}

Copy-Item -LiteralPath $envPath -Destination (Join-Path $outputPath ".env") -Force

Write-Host ""
Write-Host "Build completed successfully." -ForegroundColor Green
Write-Host "Folder: $outputPath"
Write-Host "EXE: $outputExePath"
Write-Host ""
