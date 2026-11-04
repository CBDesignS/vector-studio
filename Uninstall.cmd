@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Uninstall Vector Studio
cd /d "%TEMP%"
rem Read the entire block before PowerShell removes this installed batch file.
(
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\Uninstall.ps1"
  set "uninstallResult=!errorlevel!"
  echo.
  pause
  exit /b !uninstallResult!
)
