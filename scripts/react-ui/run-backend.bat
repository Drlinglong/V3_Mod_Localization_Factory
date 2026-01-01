@echo off
title Remis Backend (FastAPI on Windows)

echo Launching FastAPI backend server...
echo Activating Conda environment 'local_factory'...

call K:\MiniConda\Scripts\activate.bat local_factory
cd /d J:\V3_Mod_Localization_Factory

echo Starting Python server...
python -m uvicorn scripts.web_server:app --host 127.0.0.1 --port 8081 --reload

pause
