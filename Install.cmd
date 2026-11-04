@echo off
setlocal
title Vector Studio Setup
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\Install.ps1"
if errorlevel 1 (
  echo.
  echo Setup did not complete. Read the message above before trying again.
  pause
  exit /b 1
)
echo.
pause
