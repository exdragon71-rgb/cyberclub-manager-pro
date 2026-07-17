$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$exeBuildScript = Join-Path $projectRoot "scripts\build_windows_exe.ps1"
$installerScript = Join-Path $projectRoot "CyberClubManagerPro.iss"
$applicationFolder = Join-Path $projectRoot "dist\CyberClub Manager Pro"
$applicationExe = Join-Path $applicationFolder "CyberClub Manager Pro.exe"
$outputFolder = Join-Path $projectRoot "installer-output"
$outputInstaller = Join-Path $outputFolder "CyberClubManagerPro-Setup.exe"

Write-Host ""
Write-Host "CyberClub Manager Pro - Windows installer build" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path -LiteralPath $exeBuildScript)) {
    throw "EXE build script not found: $exeBuildScript"
}

if (-not (Test-Path -LiteralPath $installerScript)) {
    throw "Inno Setup script not found: $installerScript"
}

Write-Host "1. Rebuilding application..." -ForegroundColor Yellow

& $exeBuildScript

if ($LASTEXITCODE -ne 0) {
    throw "EXE build script failed with code $LASTEXITCODE."
}

if (-not (Test-Path -LiteralPath $applicationExe)) {
    throw "Application EXE was not created: $applicationExe"
}

Write-Host ""
Write-Host "2. Searching for Inno Setup compiler..." -ForegroundColor Yellow

$isccPath = $null
$isccCommand = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue

if ($null -ne $isccCommand) {
    $isccPath = $isccCommand.Source
}

$programFiles = [Environment]::GetEnvironmentVariable("ProgramFiles")
$programFilesX86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")

if (-not $isccPath -and $programFiles) {
    $candidate = Join-Path $programFiles "Inno Setup 7\ISCC.exe"

    if (Test-Path -LiteralPath $candidate) {
        $isccPath = $candidate
    }
}

if (-not $isccPath -and $programFilesX86) {
    $candidate = Join-Path $programFilesX86 "Inno Setup 7\ISCC.exe"

    if (Test-Path -LiteralPath $candidate) {
        $isccPath = $candidate
    }
}

if (-not $isccPath -and $programFiles) {
    $candidate = Join-Path $programFiles "Inno Setup 6\ISCC.exe"

    if (Test-Path -LiteralPath $candidate) {
        $isccPath = $candidate
    }
}

if (-not $isccPath -and $programFilesX86) {
    $candidate = Join-Path $programFilesX86 "Inno Setup 6\ISCC.exe"

    if (Test-Path -LiteralPath $candidate) {
        $isccPath = $candidate
    }
}

if (-not $isccPath) {
    throw "ISCC.exe was not found. Reinstall Inno Setup using the standard path."
}

Write-Host "Compiler: $isccPath" -ForegroundColor DarkGray
Write-Host ""
Write-Host "3. Building installer..." -ForegroundColor Yellow

Set-Location -LiteralPath $projectRoot

& $isccPath $installerScript

if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup failed with code $LASTEXITCODE."
}

if (-not (Test-Path -LiteralPath $outputInstaller)) {
    throw "Installer was not created: $outputInstaller"
}

Write-Host ""
Write-Host "Installer built successfully." -ForegroundColor Green
Write-Host "File: $outputInstaller"
Write-Host ""
