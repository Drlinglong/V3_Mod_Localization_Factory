@echo off
chcp 65001 >nul
echo ========================================
echo V3_Mod_Localization_Factory 启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查项目结构
if not exist "source_mod" (
    echo 错误: source_mod 目录不存在
    echo 请确保在项目根目录下运行此脚本
    echo.
    echo 当前目录: %CD%
    echo.
    echo 请检查:
    echo 1. 是否在正确的项目目录下
    echo 2. source_mod 文件夹是否存在
    echo 3. 文件夹名称是否正确（应为 'source_mod'）
    echo.
    pause
    exit /b 1
)

REM 检查是否有mod文件
dir /b /ad "source_mod" | findstr /r ".*" >nul
if errorlevel 1 (
    echo 警告: source_mod 目录为空
    echo 请添加要翻译的mod文件夹
    echo.
    echo 支持的mod类型:
    echo - Victoria 3
    echo - Stellaris  
    echo - EU4
    echo - HOI4
    echo - CK3
    echo.
)

echo 启动本地化工厂...
echo ========================================
echo.

REM 运行Python程序
python scripts\main.py

echo.
echo 程序执行完毕
pause
