@echo off
title Remis Backend (FastAPI on WSL)

echo Launching FastAPI backend server inside WSL...
echo This window will automatically run all commands in the Linux environment.

:: Execute a chain of commands within WSL
:: 1. [NEW!] Kill any existing process on port 8000 to ensure a clean start
:: 2. Source conda to make it available
:: 3. Activate the local_factory environment
:: 4. Change to the project directory (WSL path)
:: 5. Start the FastAPI server
wsl -e bash -c "fuser -k 8000/tcp || true && source ~/miniconda3/etc/profile.d/conda.sh && conda activate local_factory && cd /mnt/j/V3_Mod_Localization_Factory && python -m uvicorn scripts.web_server:app --host 0.0.0.0 --port 8000"

pause
