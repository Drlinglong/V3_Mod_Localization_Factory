@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Project Remis - Portable Setup

echo =================================================================
echo.
echo                  Project Remis - Portable Setup
echo.
echo =================================================================
echo.

REM --- Portable Toolkit Environment Setup ---
REM Temporarily "hijack" the current command-line session environment
set "ORIGINAL_PATH=%PATH%"
set "ORIGINAL_PYTHONPATH=%PYTHONPATH%"
set "ORIGINAL_PYTHONHOME=%PYTHONHOME%"

REM Set portable Python as priority
set "PATH=%CD%\python-embed;%PATH%"
set "PYTHONPATH=%CD%\python-embed"
set "PYTHONHOME=%CD%\python-embed"

echo [INFO] Portable Python environment activated
echo [INFO] Python path: %CD%\python-embed
echo.

REM --- Change to portable package directory ---
cd /d "%CD%"

REM --- Check if Python is available ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Portable Python environment not available
    echo.
    echo Please ensure python-embed directory contains complete Python embeddable package
    echo Download: https://www.python.org/downloads/windows/
    echo.
    pause
    exit /b 1
)

echo [OK] Portable Python environment detected successfully!
python --version
echo.

echo Starting Python setup script...
echo.

REM --- Change to app directory for proper Python script execution ---
cd /d "%CD%\app"
REM --- Run setup installer with correct path ---
python scripts\utils\setup_installer.py

REM --- Restore original environment ---
set "PATH=!ORIGINAL_PATH!"
set "PYTHONPATH=!ORIGINAL_PYTHONPATH!"
set "PYTHONHOME=!ORIGINAL_PYTHONHOME!"

echo.
echo =================================================================
echo Setup process completed.
echo =================================================================
echo.
pause
