$ErrorActionPreference = "Stop"

$taskName = "CyberClub Manager Pro - PostgreSQL Backup"
$backupScriptPath = Join-Path $PSScriptRoot "backup_database.ps1"

if (-not (Test-Path -LiteralPath $backupScriptPath)) {
    throw "Не найден скрипт: $backupScriptPath"
}

$powerShellPath = (Get-Command powershell.exe -ErrorAction Stop).Source
$powerShellArguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$backupScriptPath`""

$action = New-ScheduledTaskAction -Execute $powerShellPath -Argument $powerShellArguments
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $currentUser -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Почасовая резервная копия PostgreSQL для CyberClub Manager Pro. Хранятся последние 7 дней." -Force | Out-Null

Write-Host ""
Write-Host "Почасовые резервные копии включены." -ForegroundColor Green
Write-Host "Первая автоматическая копия будет создана примерно через 2 минуты."
Write-Host "Задача: $taskName"
Write-Host ""
