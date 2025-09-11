@echo off
rem Smart Setup Installer - Universal Configuration Guide
chcp 65001 >nul
title Paradox Mod Localization Factory - Setup Installer

echo.
echo ========================================
echo    🚀 Paradox Mod Localization Factory
echo    🚀 蕾姆丝计划 - 安装配置引导器
echo ========================================
echo.

rem Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found
    echo ❌ 错误: 未找到Python
    echo.
    echo Please install Python 3.8 or higher first:
    echo 请先安装Python 3.8或更高版本：
    echo 1. Visit https://www.python.org/downloads/
    echo 2. Download the latest Python version
    echo 3. During installation, make sure to check "Add Python to PATH"
    echo 4. After installation, run this file again
    echo.
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载最新版本Python
    echo 3. 安装时请勾选"Add Python to PATH"
    echo 4. 安装完成后重新运行此文件
    echo.
    pause
    exit /b 1
)

echo ✅ Python environment detected successfully!
echo ✅ Python环境检测成功！
python --version
echo.

echo Starting smart setup installer...
echo 启动智能安装配置引导器...
echo.

rem Run the Python setup installer
python scripts\utils\setup_installer.py

echo.
echo ========================================
echo Setup installer completed.
echo 安装配置引导器运行完成。
echo ========================================
pause
