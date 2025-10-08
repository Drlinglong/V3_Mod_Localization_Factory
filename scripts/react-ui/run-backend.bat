@echo off
title Remis Backend (FastAPI)
echo Activating Conda from absolute path and starting backend...

set CONDA_ROOT=K:\MiniConda
call "%CONDA_ROOT%\condabin\conda.bat" activate local_factory

if %errorlevel% neq 0 (
    echo ERROR: Failed to activate Conda. Please check your CONDA_ROOT.
    pause
    exit /b
)

echo Conda activated. Starting uvicorn...
uvicorn scripts.web_server:app --host 0.0.0.0 --port 8000

pause
