@echo off
title Remis Frontend (Vite)
echo Setting Node version and starting frontend...

cd scripts/react-ui

:: Switch to the correct node version
nvm use v20.12.2
if %errorlevel% neq 0 (
    echo ERROR: Failed to set Node version with NVM.
    pause
    exit /b
)
echo Now using node v20.11.0.

:: Programmatically find the path to node.exe
FOR /F "tokens=*" %%G IN ('where node') DO (
    SET NODE_EXE_PATH=%%G
)

if not defined NODE_EXE_PATH (
    echo ERROR: Could not find node.exe even after 'nvm use'.
    pause
    exit /b
)

:: The npm.cmd script is in the same directory as node.exe.
:: This command extracts the directory part of the path.
FOR %%A IN ("%NODE_EXE_PATH%") DO (
    SET NODE_DIR=%%~dpA
)

if not defined NODE_DIR (
    echo ERROR: Could not determine the directory for node.exe.
    pause
    exit /b
)

echo Found npm directory at %NODE_DIR%
echo Starting Vite...

:: Call npm.cmd using its full, absolute path to bypass all PATH issues
call "%NODE_DIR%npm.cmd" run dev

pause
