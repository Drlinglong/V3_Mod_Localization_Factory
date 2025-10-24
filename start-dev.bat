@echo off
title Remis Project - Full Development Environment
color 0A

echo.
echo ===============================================================
echo        Remis Project - Development Environment Launcher
echo ===============================================================
echo.
echo Starting both Frontend (Vite) and Backend (FastAPI) servers...
echo.

REM Start Backend (FastAPI on port 8000)
echo [1/2] Starting Backend (FastAPI) on port 8000...
start "Remis Backend - FastAPI" cmd /k "cd scripts && python -m uvicorn web_server:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start Frontend (Vite on port 5173)
echo [2/2] Starting Frontend (Vite) on port 5173...
start "Remis Frontend - Vite" cmd /k "cd scripts/react-ui && npm run dev"

echo.
echo ===============================================================
echo Both servers are starting in separate windows.
echo.
echo Frontend: http://localhost:5173/
echo Backend:  http://localhost:8000/
echo.
echo This launcher window will close in 5 seconds...
echo ===============================================================
echo.

timeout /t 5 > nul
exit
