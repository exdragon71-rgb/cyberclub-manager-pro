@echo off
chcp 65001 >nul
title CyberClub Manager Pro - Production

powershell.exe -NoProfile -NoExit -ExecutionPolicy Bypass -File "%~dp0scripts\start_production.ps1"
