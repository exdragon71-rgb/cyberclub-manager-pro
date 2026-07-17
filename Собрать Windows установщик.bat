@echo off
title CyberClub Manager Pro - Build Installer
powershell.exe -NoProfile -NoExit -ExecutionPolicy Bypass -File "%~dp0scripts\build_windows_installer.ps1"
