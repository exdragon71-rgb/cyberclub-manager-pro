$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendPath = Join-Path $projectRoot "frontend"
$backendPath = Join-Path $projectRoot "backend"
$pythonPath = Join-Path $backendPath ".venv\Scripts\python.exe"

Write-Host ""
Write-Host "CyberClub Manager Pro" -ForegroundColor Cyan
Write-Host "Production-запуск" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path -LiteralPath $frontendPath)) {
    throw "Не найдена папка frontend: $frontendPath"
}

if (-not (Test-Path -LiteralPath $backendPath)) {
    throw "Не найдена папка backend: $backendPath"
}

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Не найден Python виртуального окружения: $pythonPath"
}

$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue

if (-not $npmCommand) {
    throw "Не найден npm.cmd. Проверьте установку Node.js."
}

Write-Host "1. Сборка frontend..." -ForegroundColor Yellow
Set-Location -LiteralPath $frontendPath

& $npmCommand.Source run build

if ($LASTEXITCODE -ne 0) {
    throw "Сборка frontend завершилась с кодом $LASTEXITCODE."
}

$frontendIndex = Join-Path $frontendPath "dist\index.html"

if (-not (Test-Path -LiteralPath $frontendIndex)) {
    throw "После сборки не найден frontend\dist\index.html."
}

Write-Host ""
Write-Host "2. Запуск FastAPI..." -ForegroundColor Yellow
Write-Host "Адрес: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "Для остановки нажмите Ctrl+C." -ForegroundColor DarkGray
Write-Host ""

$browserCommand = @"
Start-Sleep -Seconds 2
Start-Process 'http://127.0.0.1:8000/'
"@

Start-Process `
    -FilePath "powershell.exe" `
    -WindowStyle Hidden `
    -ArgumentList @(
        "-NoProfile",
        "-Command",
        $browserCommand
    )

Set-Location -LiteralPath $backendPath

& $pythonPath `
    -m uvicorn `
    app.main:app `
    --host 127.0.0.1 `
    --port 8000

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "Сервер остановлен. Код: $exitCode" -ForegroundColor Yellow
