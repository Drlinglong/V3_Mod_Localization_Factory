@echo off
title Remis Frontend (Vite on WSL)

echo Launching Vite development server inside WSL...
echo This window will automatically run all commands in the Linux environment.

:: Execute a chain of commands within WSL
:: 1. [NEW!] Kill any existing process on port 5173 to ensure a clean start
:: 2. Source nvm to make it available
:: 3. Use the correct node version
:: 4. Change to the project directory (WSL path)
:: 5. Start the dev server
wsl -e bash -c "fuser -k 5173/tcp || true && source ~/.nvm/nvm.sh && nvm use 22 && cd /mnt/j/V3_Mod_Localization_Factory/scripts/react-ui && npm run dev"

pause