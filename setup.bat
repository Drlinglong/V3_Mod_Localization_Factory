@echo off
rem This batch file starts the smart setup installer for Project Remis.
rem It checks for a valid Python installation before executing the script.

chcp 65001 >nul
title Project Remis - Setup

echo =================================================================
echo.
echo                  Project Remis - 安装配置引导器
echo.
echo =================================================================
echo.

rem 检查Python环境是否存在
python --version >nul 2>&1
if errorlevel 1 (
    cls
    echo ❌ 错误: 未在您的系统中找到Python。
    echo.
    echo 请先安装Python 3.8或更高版本:
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装最新版本的Python
    echo 3. [重要] 安装时，请务必勾选 "Add Python to PATH" 选项！
    echo 4. 安装完成后，请重新运行本文件 (setup.bat)。
    echo.
    pause
    exit /b 1
)

echo [✓] 已成功检测到Python环境！
python --version
echo.

echo 正在启动Python安装脚本 (scripts/utils/setup_installer.py)...
echo.

rem 运行Python安装脚本 (作为模块)
python -m scripts.utils.setup_installer

echo.
echo =================================================================
echo 安装配置流程已结束。
echo 如果您设置了新的环境变量，建议重启您的终端或电脑以确保生效。
echo =================================================================
echo.
pause