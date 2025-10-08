@echo off
chcp 65001 >nul

:: 1. Configuration
set CONDA_ROOT=K:\MiniConda
set ENV_NAME=local_factory
set BACKEND_SCRIPT=scripts.web_server:app
set FRONTEND_DIR=scripts\react-ui

echo ========================================
echo Starting Development Environment...
echo ========================================
echo.

:: 2. Activate Conda Environment
echo [Step 1/5] Activating Conda environment: %ENV_NAME%...
call "%CONDA_ROOT%\condabin\conda.bat" activate %ENV_NAME%
if %errorlevel% neq 0 (
    echo CRITICAL ERROR: Failed to activate Conda environment '%ENV_NAME%'.
    goto :error
)
echo Environment activated.
echo.

:: 3. Install Backend Dependencies
echo [Step 2/5] Installing backend dependencies from requirements.txt...
pip install -r requirements.txt
echo Backend dependencies are up to date.
echo.

:: 4. Install Frontend Dependencies
echo [Step 3/5] Checking and installing frontend dependencies...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo 'node_modules' not found. Installing dependencies...
    call pushd %FRONTEND_DIR%
    npm install
    call popd
) else (
    echo 'node_modules' already exists. Skipping installation.
)
echo Frontend dependencies are ready.
echo.

:: 5. Start Servers
echo [Step 4/5] Starting backend and frontend servers...
echo    - Backend: http://localhost:8000
echo    - Frontend: http://localhost:5173
echo.
echo Two new terminal windows will open for the backend and frontend services.
echo Please keep them running.
echo.

:: Start Backend Server in a new window
start "Backend Server" cmd /k "call "%CONDA_ROOT%\condabin\conda.bat" activate %ENV_NAME% && uvicorn %BACKEND_SCRIPT% --host 0.0.0.0 --port 8000"

:: Start Frontend Server in a new window
start "Frontend Server" cmd /k "call "%CONDA_ROOT%\condabin\conda.bat" activate %ENV_NAME% && cd /d %FRONTEND_DIR% && npm run dev"

:: 6. Open Browser
echo [Step 5/5] Opening frontend application in your browser...
timeout /t 5 /nobreak >nul
start http://localhost:5173/

echo.
echo ========================================
echo Development environment is launching.
echo ========================================
goto :end

:error
echo.
echo ========================================
echo      AN ERROR OCCURRED.
echo ========================================
pause

:end
pause
