@echo off
chcp 65001 >nul
title CyberClub Manager Pro - Резервная копия

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\backup_database.ps1"

echo.
pause
