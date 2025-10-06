@echo off
pushd "%~dp0"
setlocal enabledelayedexpansion
title Project Remis

echo [INFO] =================================================================
echo [INFO] Project Remis - Portable Toolkit Startup
echo [INFO] =================================================================
echo [INFO] Setting up portable environment...
echo.

REM --- Portable Toolkit Environment Setup ---
REM Temporarily "hijack" the current command-line session environment
set "ORIGINAL_PATH=%PATH%"
set "ORIGINAL_PYTHONPATH=%PYTHONPATH%"
set "ORIGINAL_PYTHONHOME=%PYTHONHOME%"

REM Set portable Python as priority
set "PATH=%CD%\python-embed;%PATH%"
set "PYTHONPATH=%CD%\packages;%CD%\python-embed"
REM PYTHONHOME is not needed and can cause path issues in embedded environments.

echo [INFO] Portable Python environment activated
echo [INFO] Python path: %CD%\python-embed
echo [INFO] Packages path: %CD%\packages
echo.

REM --- Change to portable package directory ---
cd /d "%CD%"

REM --- Skip pip installation for embedded Python ---
echo [INFO] Using pre-installed packages (embedded Python mode)
echo [INFO] Dependencies are already included in the portable package
echo.

echo [INFO] Launching Project Remis...
echo =================================================================
REM --- Change to app directory for proper Python script execution ---
cd /d "%CD%\app"
python scripts\main.py
echo.

REM --- Restore original environment ---
set "PATH=!ORIGINAL_PATH!"
set "PYTHONPATH=!ORIGINAL_PYTHONPATH!"
set "PYTHONHOME=!ORIGINAL_PYTHONHOME!"

echo [INFO] Project Remis has closed. Environment restored.
pause >nul
popd
