@echo off
echo [INFO] Starting Remis Development Environment...
echo [INFO] calling scripts/run_dev_servers.py...

python scripts/run_dev_servers.py

if errorlevel 1 (
    echo.
    echo [ERROR] The server launcher exited with an error.
    echo Please check the output above for details.
    pause
)
