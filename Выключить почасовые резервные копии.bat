@echo off
chcp 65001 >nul
title CyberClub Manager Pro - Отключение резервных копий

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\remove_hourly_backup.ps1"

echo.
pause
