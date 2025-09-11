@echo off
rem Simple launcher - Universal igniter
chcp 65001 >nul
cls

rem Try to find and activate the correct Python environment (Conda first, then system default)
set ENV_TYPE=System Default
set CONDA_ACTIVATION_SCRIPT_FOUND=

rem Check conda environment
if exist "J:\miniconda\condabin\conda.bat" (
    call "J:\miniconda\condabin\conda.bat" info --envs | findstr "local_factory" >nul
    if not errorlevel 1 (
        set ENV_TYPE=Conda (local_factory)
        set CONDA_ACTIVATION_SCRIPT_FOUND=1
    )
)

rem Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo Error: Python not found
    echo ========================================
    echo.
    echo Please ensure Python is installed and added to system PATH
    echo.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

rem Display startup environment info
if defined CONDA_ACTIVATION_SCRIPT_FOUND (
    echo Starting in virtual environment...
    call "J:\miniconda\condabin\conda.bat" activate local_factory && python scripts\main.py
) else (
    echo Starting in system default environment...
    python scripts\main.py
)

echo.
echo ===================================================
echo Program execution completed. You can close this window.
echo ===================================================
pause