@echo off
chcp 65001 >nul
title P社Mod本地化工厂 - 首次安装配置

echo.
echo ========================================
echo    🚀 P社Mod本地化工厂 - 首次安装配置
echo ========================================
echo.
echo 欢迎使用P社Mod本地化工厂！
echo 这是首次使用项目时的配置向导。
echo.
echo 注意：此配置只需要运行一次，除非重装系统或换电脑。
echo.

:: 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未检测到Python环境！
    echo.
    echo 请先安装Python 3.8或更高版本：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载最新版本Python
    echo 3. 安装时请勾选"Add Python to PATH"
    echo 4. 安装完成后重新运行此文件
    echo.
    pause
    exit /b 1
)

echo ✅ Python环境检测成功！
python --version
echo.

:: 检查pip是否可用
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：pip不可用！
    echo 请重新安装Python，确保勾选"Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ pip可用
echo.

:: 显示API选项
echo 请选择要使用的AI翻译服务：
echo.
echo [1] Google Gemini (推荐)
echo     - 使用 Gemini 2.5 Flash 模型
echo     - 翻译质量高，支持中文
echo     - 需要Google账号
echo.
echo [2] OpenAI GPT
echo     - 使用 GPT-5 Mini 模型
echo     - 翻译质量极高，支持多种语言
echo     - 需要OpenAI账号
echo.
echo [3] 阿里云通义千问
echo     - 使用 Qwen Plus 模型
echo     - 国产AI服务，允许国内用户直连
echo     - 建议国内用户选择此选项
echo     - 需要阿里云账号
echo.
echo ⚠️  重要提醒：
echo     - 申请API密钥需要注册账户并绑定银行卡
echo     - 使用API可能会产生费用，具体以服务商收费条款为准
echo     - 请注意妥善保管API密钥，否则可能会被刷爆银行卡
echo.

:choice
set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" goto gemini
if "%choice%"=="2" goto openai
if "%choice%"=="3" goto qwen
echo.
echo ❌ 无效选择，请输入1、2或3
echo.
goto choice

:gemini
echo.
echo 🎯 你选择了 Google Gemini
echo.
echo 正在安装 Gemini 依赖库...
pip install --upgrade google-genai
if %errorlevel% neq 0 (
    echo ❌ 安装失败！请检查网络连接或手动安装
    echo 手动安装命令：pip install --upgrade google-genai
    echo.
    pause
    exit /b 1
)
echo ✅ Gemini 依赖库安装成功！
echo.
echo 📝 接下来需要获取 Gemini API 密钥：
echo 1. 访问 https://aistudio.google.com/
echo 2. 登录Google账号
echo 3. 根据提示创建API密钥
echo 4. 复制生成的API密钥
echo.
set /p api_key="请输入你的 Gemini API 密钥: "
if "%api_key%"=="" (
    echo ❌ API密钥不能为空！
    pause
    exit /b 1
)
echo.
echo 正在设置环境变量...
setx GEMINI_API_KEY "%api_key%"
if %errorlevel% neq 0 (
    echo ❌ 环境变量设置失败！
    echo 请手动设置环境变量 GEMINI_API_KEY
    echo.
    pause
    exit /b 1
)
echo ✅ 环境变量设置成功！
goto success

:openai
echo.
echo 🎯 你选择了 OpenAI GPT
echo.
echo 正在安装 OpenAI 依赖库...
pip install --upgrade openai
if %errorlevel% neq 0 (
    echo ❌ 安装失败！请检查网络连接或手动安装
    echo 手动安装命令：pip install --upgrade openai
    echo.
    pause
    exit /b 1
)
echo ✅ OpenAI 依赖库安装成功！
echo.
echo 📝 接下来需要获取 OpenAI API 密钥：
echo 1. 访问 https://platform.openai.com/
echo 2. 注册/登录账号
echo 3. 进入 API Keys 页面
echo 4. 根据提示创建API密钥
echo 5. 复制生成的API密钥
echo.
set /p api_key="请输入你的 OpenAI API 密钥: "
if "%api_key%"=="" (
    echo ❌ API密钥不能为空！
    pause
    exit /b 1
)
echo.
echo 正在设置环境变量...
setx OPENAI_API_KEY "%api_key%"
if %errorlevel% neq 0 (
    echo ❌ 环境变量设置失败！
    echo 请手动设置环境变量 OPENAI_API_KEY
    echo.
    pause
    exit /b 1
)
echo ✅ 环境变量设置成功！
goto success

:qwen
echo.
echo 🎯 你选择了 阿里云通义千问
echo.
echo 正在安装 通义千问 依赖库...
pip install --upgrade dashscope
if %errorlevel% neq 0 (
    echo ❌ 安装失败！请检查网络连接或手动安装
    echo 手动安装命令：pip install --upgrade dashscope
    echo.
    pause
    exit /b 1
)
echo ✅ 通义千问 依赖库安装成功！
echo.
echo 📝 接下来需要获取 通义千问 API 密钥：
echo 1. 访问 https://dashscope.console.aliyun.com/
echo 2. 登录阿里云账号
echo 3. 根据提示创建API密钥
echo 4. 复制生成的API密钥
echo.
set /p api_key="请输入你的 通义千问 API 密钥: "
if "%api_key%"=="" (
    echo ❌ API密钥不能为空！
    pause
    exit /b 1
)
echo.
echo 正在设置环境变量...
setx DASHSCOPE_API_KEY "%api_key%"
if %errorlevel% neq 0 (
    echo ❌ 环境变量设置失败！
    echo 请手动设置环境变量 DASHSCOPE_API_KEY
    echo.
    pause
    exit /b 1
)
echo ✅ 环境变量设置成功！

:success
echo.
echo ========================================
echo           🎉 配置完成！
echo ========================================
echo.
echo ✅ 依赖库安装完成
echo ✅ 环境变量设置完成
echo ✅ API配置完成
echo.
echo 🚀 现在你可以使用项目了！
echo.
echo 📋 使用方法：
echo 1. 双击 "run.bat" 运行主程序
echo 2. 按照提示选择游戏和Mod
echo 3. 开始自动翻译！
echo.
echo 💡 提示：
echo - 此配置只需要运行一次
echo - 除非重装系统或换电脑，否则无需重新配置
echo - 如果遇到问题，请查看 README.md 或 小白说明文档.md
echo.
echo 🔄 环境变量将在下次重启后生效
echo 如果急需使用，请重新打开命令提示符
echo.
pause
