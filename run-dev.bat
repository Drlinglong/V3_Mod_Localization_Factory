@echo off
ECHO =================================================================
ECHO == Remis Project - One-Click Development Environment Launcher  ==
ECHO =================================================================
ECHO.

ECHO Launching backend and frontend servers in separate windows...

start "Remis Backend" scripts\react-ui\run-backend.bat
start "Remis Frontend" scripts\react-ui\run-frontend.bat

ECHO.
ECHO This launcher window will now close.
timeout /t 3 > nul