@echo off
chcp 65001 >nul
cls

echo ========================================
echo Conda 环境诊断工具
echo ========================================
echo.

echo --- 1. 检查 conda_path.txt ---
if not exist "conda_path.txt" (
echo 🔴 错误: 未找到 conda_path.txt 文件。
goto :end
)

set /p CONDA_BASE_PATH=<conda_path.txt
echo 从 conda_path.txt 文件中读取到的路径是:
echo.
echo -->[%CONDA_BASE_PATH%]<--
echo.
echo (请仔细检查上面的方括号内，是否有任何多余的空格或换行)
echo.

echo --- 2. 检查构造出的 conda.bat 路径 ---
set "CONDA_SCRIPT_PATH_1=%CONDA_BASE_PATH%\Scripts\conda.bat"
set "CONDA_SCRIPT_PATH_2=%CONDA_BASE_PATH%\condabin\conda.bat"

echo 正在检查路径 1: "%CONDA_SCRIPT_PATH_1%"
if exist "%CONDA_SCRIPT_PATH_1%" (
echo   --> ✅ 找到！
) else (
echo   --> ❌ 未找到。
)

echo 正在检查路径 2: "%CONDA_SCRIPT_PATH_2%"
if exist "%CONDA_SCRIPT_PATH_2%" (
echo   --> ✅ 找到！
) else (
echo   --> ❌ 未找到。
)
echo.

echo --- 3. 尝试激活 ---
echo 正在尝试用找到的路径激活 'local_factory' 环境...
if exist "%CONDA_SCRIPT_PATH_1%" (
call "%CONDA_SCRIPT_PATH_1%" activate local_factory 2>nul
) else if exist "%CONDA_SCRIPT_PATH_2%" (
call "%CONDA_SCRIPT_PATH_2%" activate local_factory 2>nul
)

if "%CONDA_DEFAULT_ENV%" EQU "local_factory" (
echo.
echo 🟢 成功！环境已成功激活。
echo    当前激活的环境是: %CONDA_DEFAULT_ENV%
) else (
echo.
echo 🔴 失败！未能激活环境。
)
echo.

:end
echo ========================================
echo 诊断结束。
pause