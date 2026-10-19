@echo off
cd /d "%~dp0\.."
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 -m desktop.app
) else (
  python -m desktop.app
)
if errorlevel 1 pause
