@echo off
rem 简易启动脚本：自动检测虚拟环境并启动 Web UI
chcp 65001 >nul
cd /d %~dp0

set "VENV_PY=venv\Scripts\python.exe"

rem 1. 优先使用虚拟环境中的 Python
if exist "%VENV_PY%" (
    echo 已检测到虚拟环境，使用其中的 Python...
    "%VENV_PY%" scripts\webui.py
) else (
    rem 2. 如果没有虚拟环境，尝试系统环境
    python --version >nul 2>&1
    if errorlevel 1 (
        rem 两种环境均无 Python
        echo 未找到 Python，无法启动 Web UI。
        pause
        exit /b 1
    )
    echo 未检测到虚拟环境，改用系统 Python...
    python scripts\webui.py
)

rem 3. Python 执行结束后暂停，便于查看输出
pause

