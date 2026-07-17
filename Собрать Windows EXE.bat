@echo off
title CyberClub Manager Pro - Build EXE
powershell.exe -NoProfile -NoExit -ExecutionPolicy Bypass -File "%~dp0scripts\build_windows_exe.ps1"
