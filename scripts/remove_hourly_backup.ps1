$ErrorActionPreference = "Stop"

$taskName = "CyberClub Manager Pro - PostgreSQL Backup"
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($task) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false

    Write-Host ""
    Write-Host "Почасовые резервные копии отключены." -ForegroundColor Yellow
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "Задача резервного копирования не найдена."
    Write-Host ""
}
