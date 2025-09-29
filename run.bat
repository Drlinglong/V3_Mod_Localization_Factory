@echo off
rem Conda Strict Mode V5.0: Uses 'start /b' to isolate environment activation and prevent flash-backs.
chcp 65001 >nul

rem 1. Configuration
set CONDA_ROOT=K:\MiniConda
set ENV_NAME=local_factory
set PYTHON_SCRIPT=scripts\main.py

echo ========================================
echo Starting Universal Launcher (V5.0 - Isolated Start)...
echo ----------------------------------------

rem 2. Check Conda Root Path
if not exist "%CONDA_ROOT%\condabin\conda.bat" (
    echo CRITICAL ERROR: Conda installation not found at "%CONDA_ROOT%".
    echo Please check CONDA_ROOT path or install Miniconda.
    goto :final_error
)

rem === 3. Isolated Activation and Execution ===
echo Status: Conda found. Launching isolated session for environment (%ENV_NAME%)...

rem CRITICAL FIX: We use 'start' to launch a new, isolated CMD session that initializes Conda and runs the command.
rem This prevents PATH conflicts and the 'not was unexpected' errors from the main script.
start "Running Project" /B cmd /K ( call "%CONDA_ROOT%\condabin\conda.bat" activate %ENV_NAME% ^&^& python %PYTHON_SCRIPT% )

rem We assume the isolated session has successfully launched the python script.
echo SUCCESS: Isolated Conda session launched.
echo Note: The Python script is running in a background process.
goto :end

rem === 4. Error Handling & Exit ===
:final_error
echo.
echo ========================================
echo PROGRAM FAILED TO START.
echo ========================================

:end
echo.
echo ===================================================
echo Program execution completed. You can close this window.
echo ===================================================
pause
