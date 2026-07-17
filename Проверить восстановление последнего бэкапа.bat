@echo off
chcp 65001 >nul
title CyberClub Manager Pro - Проверка восстановления

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\test_restore_latest_backup.ps1"

echo.
pause
