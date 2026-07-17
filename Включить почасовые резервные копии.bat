@echo off
chcp 65001 >nul
title CyberClub Manager Pro - Почасовые резервные копии

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_hourly_backup.ps1"

echo.
pause
