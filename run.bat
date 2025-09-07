@echo off
rem ---------------------------------------------------------------
rem Project Remis - Paradox Mod Localization Factory
rem Copyright (C) 2025 Drlinglong
rem ---------------------------------------------------------------

rem 设置UTF-8代码页 / Set codepage to UTF-8
chcp 65001 >nul
rem 清空屏幕 / Clear the screen
cls

rem 显示字符画头图 / Display banner from banner.txt
if exist "banner.txt" (
type "banner.txt"
) else (
rem 备用文本头图 / Fallback text banner
echo.
echo      =======================================
echo         Project Remis -蕾姆丝计划
echo      =======================================
)

echo.
echo.
echo     P社Mod本地化工厂 (Paradox Mod Localization Factory)
echo     版本: v1.0.4 / Version: v1.0.4
echo     ---------------------------------------------------
echo.

rem --- 依赖项检查 / Dependency Checks ---
set "error_occurred=0"
set "warning_message="

rem 检查Python / Check for Python
python --version >nul 2>&1
if errorlevel 1 (
echo 🔴 错误: 未找到Python。请先安装Python 3.8或更高版本。
echo    ERROR: Python not found. Please install Python 3.8 or higher.
echo.
echo    下载地址 / Download from: https://www.python.org/downloads/
echo.
set "error_occurred=1"
)

rem 检查项目结构 / Check for source_mod directory
if %error_occurred% equ 0 (
if not exist "source_mod" (
echo 🔴 错误: 'source_mod' 目录不存在。请在正确的项目根目录下运行。
echo    ERROR: 'source_mod' directory not found. Please run this script from the project root.
echo.
echo    当前目录 / Current Directory: %CD%
echo.
set "error_occurred=1"
)
)

rem 检查是否有mod文件 (警告，非致命错误) / Check if source_mod is empty (Warning, non-fatal)
if %error_occurred% equ 0 (
dir /b /ad "source_mod" | findstr /r ".*" >nul
if errorlevel 1 (
set "warning_message=🟡 警告: 'source_mod'目录为空，请添加要翻译的Mod文件夹。 / WARNING: 'source_mod' is empty, please add mod folders to translate."
)
)

rem --- 检查结果汇总 / Check Summary ---
if %error_occurred% equ 1 (
pause
exit /b 1
)

if defined warning_message (
echo %warning_message%
) else (
echo ✅ 所有依赖项正常 / All checks passed.
)
echo.

echo ===================================================
echo 🚀 正在启动本地化工厂主程序...
echo    Launching the Localization Factory...
echo ===================================================
echo.

rem 运行Python主程序 / Run the main Python program
python scripts\main.py

echo.
echo ===================================================
echo ✅ 程序执行完毕。您可以关闭此窗口。
echo    Execution finished. You can close this window now.
echo ===================================================
pause