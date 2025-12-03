@echo off
REM Wrapper script to run PowerShell pre-commit check
REM Double-click this file to run the quality check

echo.
echo ===================================
echo   Pre-Commit Quality Check
echo ===================================
echo.

REM Run PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0check_before_commit.ps1"

REM Pause to see results
pause
