@echo off
title Remis Project - Development Environment

echo Launching backend and frontend servers...

REM Start backend server (FastAPI)
start "Remis Backend" cmd /k "cd scripts && python web_server.py"

REM Start frontend server (Vite)
start "Remis Frontend" cmd /k "cd scripts/react-ui && npm run dev"

echo Both servers launched in separate windows.
pause
