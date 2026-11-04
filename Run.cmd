@echo off
setlocal
title Vector Studio - close this window to stop
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Vector Studio is not set up yet. Run Install.cmd first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" launcher.py
if errorlevel 1 (
  echo.
  echo The app could not start. Try running Install.cmd again to repair it.
  pause
  exit /b 1
)
