@echo off
rem 完全简化版本的 run.bat
chcp 65001 >nul
cls

rem 显示 banner
if exist "banner.txt" (
type "banner.txt"
) else (
echo.
echo      =======================================
echo         Project Remis -蕾姆丝计划
echo      =======================================
)

echo.
echo     P社Mod本地化工厂 (Paradox Mod Localization Factory)
echo     版本: v1.0.8 / Version: v1.0.8
echo     ---------------------------------------------------
echo.

set ENV_TYPE=System Default
set CONDA_ACTIVATION_SCRIPT_FOUND=

rem 检查 conda 环境
if exist "J:\miniconda\condabin\conda.bat" (
    call "J:\miniconda\condabin\conda.bat" info --envs | findstr "local_factory" >nul
    if not errorlevel 1 (
        set ENV_TYPE=Conda (local_factory)
        set CONDA_ACTIVATION_SCRIPT_FOUND=1
    )
)

rem 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    pause
    exit /b 1
)

rem 检查 source_mod 目录
if not exist "source_mod" (
    echo 错误: source_mod 目录不存在
    pause
    exit /b 1
)

rem 检查 API 库
set API_LIBRARIES_FOUND=
python -c "import openai" >nul 2>&1
if not errorlevel 1 (
    set API_LIBRARIES_FOUND=%API_LIBRARIES_FOUND%OpenAI 
)

python -c "import google.genai" >nul 2>&1
if not errorlevel 1 (
    set API_LIBRARIES_FOUND=%API_LIBRARIES_FOUND%Google 
)

python -c "import dashscope" >nul 2>&1
if not errorlevel 1 (
    set API_LIBRARIES_FOUND=%API_LIBRARIES_FOUND%Qwen 
)

if "%API_LIBRARIES_FOUND%"=="" (
    echo 错误: 未找到任何API库
    echo 请安装: pip install openai google-genai dashscope
    pause
    exit /b 1
)

rem 检查 API 密钥
set API_KEYS_FOUND=
if defined OPENAI_API_KEY (
    set API_KEYS_FOUND=%API_KEYS_FOUND%OpenAI 
)
if defined GEMINI_API_KEY (
    set API_KEYS_FOUND=%API_KEYS_FOUND%Google 
)
if defined DASHSCOPE_API_KEY (
    set API_KEYS_FOUND=%API_KEYS_FOUND%Qwen 
)

if "%API_KEYS_FOUND%"=="" (
    echo 错误: 未找到API密钥
    echo 请设置环境变量: OPENAI_API_KEY, GEMINI_API_KEY, DASHSCOPE_API_KEY
    pause
    exit /b 1
)

echo ✅ Python已安装，已检测到%API_LIBRARIES_FOUND%库，%ENV_TYPE%
echo    Python installed, %API_LIBRARIES_FOUND%libraries detected, %ENV_TYPE%
echo.

echo ===================================================
echo 正在启动本地化工厂主程序...
echo ===================================================
echo.

rem 运行 Python 程序
if defined CONDA_ACTIVATION_SCRIPT_FOUND (
    call "J:\miniconda\condabin\conda.bat" activate local_factory
    call python scripts\main.py
) else (
    python scripts\main.py
)

echo.
echo ===================================================
echo 程序执行完毕。您可以关闭此窗口。
echo ===================================================
pause