@echo off
title Remis Frontend (Vite on WSL)

echo Launching Vite development server inside WSL...
echo This window will automatically run all commands in the Linux environment.

:: Execute a chain of commands within WSL
:: 1. Source nvm to make it available
:: 2. Use the correct node version
:: 3. Change to the project directory (WSL path)
:: 4. Start the dev server
wsl -e bash -c "source ~/.nvm/nvm.sh && nvm use 22 && cd /mnt/j/V3_Mod_Localization_Factory/scripts/react-ui && npm run dev"

pause