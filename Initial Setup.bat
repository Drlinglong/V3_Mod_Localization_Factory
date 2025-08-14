@echo off
chcp 65001 >nul
title Paradox Mod Localization Factory - Initial Setup

echo.
echo ========================================
echo    🚀 Paradox Mod Localization Factory - Initial Setup
echo ========================================
echo.
echo Welcome to Paradox Mod Localization Factory!
echo This is the configuration wizard for first-time users.
echo.
echo Note: This configuration only needs to be run once, unless you reinstall your system or change computers.
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python environment not detected!
    echo.
    echo Please install Python 3.8 or higher first:
    echo 1. Visit https://www.python.org/downloads/
    echo 2. Download the latest Python version
    echo 3. During installation, make sure to check "Add Python to PATH"
    echo 4. After installation, run this file again
    echo.
    pause
    exit /b 1
)

echo ✅ Python environment detected successfully!
python --version
echo.

:: Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: pip is not available!
    echo Please reinstall Python, ensuring "Add Python to PATH" is checked
    echo.
    pause
    exit /b 1
)

echo ✅ pip is available
echo.

:: Display API options
echo Please select the AI translation service you want to use:
echo.
echo [1] Google Gemini (Recommended)
echo     - Uses Gemini 2.5 Flash model
echo     - High translation quality, fast speed
echo     - Requires Google account
echo.
echo [2] OpenAI GPT
echo     - Uses GPT-5 Mini model
echo     - Extremely high translation quality, supports multiple languages
echo     - Requires OpenAI account
echo.
echo [3] Alibaba Cloud Qwen
echo     - Uses Qwen Plus model
echo     - Domestic AI service, direct connection for Chinese users
echo     - Recommended for domestic users
echo     - Requires Alibaba Cloud account
echo.
echo ⚠️  Important Reminder:
echo     - Applying for API keys requires account registration and bank card binding
echo     - Using APIs may incur costs, subject to service provider terms
echo     - Please keep your API keys secure, otherwise your bank card may be compromised
echo.

:choice
set /p choice="Please enter your choice (1-3): "

if "%choice%"=="1" goto gemini
if "%choice%"=="2" goto openai
if "%choice%"=="3" goto qwen
echo.
echo ❌ Invalid choice, please enter 1, 2, or 3
echo.
goto choice

:gemini
echo.
echo 🎯 You selected Google Gemini
echo.
echo Installing Gemini dependencies...
pip install --upgrade google-genai
if %errorlevel% neq 0 (
    echo ❌ Installation failed! Please check your network connection or install manually
    echo Manual installation command: pip install --upgrade google-genai
    echo.
    pause
    exit /b 1
)
echo ✅ Gemini dependencies installed successfully!
echo.
echo 📝 Next, you need to obtain a Gemini API key:
echo 1. Visit https://aistudio.google.com/
echo 2. Log in to your Google account
echo 3. Create API key according to prompts
echo 4. Copy the generated API key
echo.
set /p api_key="Please enter your Gemini API key: "
if "%api_key%"=="" (
    echo ❌ API key cannot be empty!
    pause
    exit /b 1
)
echo.
echo Setting environment variable...
setx GEMINI_API_KEY "%api_key%"
if %errorlevel% neq 0 (
    echo ❌ Failed to set environment variable!
    echo Please manually set the GEMINI_API_KEY environment variable
    echo.
    pause
    exit /b 1
)
echo ✅ Environment variable set successfully!
goto success

:openai
echo.
echo 🎯 You selected OpenAI GPT
echo.
echo Installing OpenAI dependencies...
pip install --upgrade openai
if %errorlevel% neq 0 (
    echo ❌ Installation failed! Please check your network connection or install manually
    echo Manual installation command: pip install --upgrade openai
    echo.
    pause
    exit /b 1
)
echo ✅ OpenAI dependencies installed successfully!
echo.
echo 📝 Next, you need to obtain an OpenAI API key:
echo 1. Visit https://platform.openai.com/
echo 2. Register/Log in to your account
echo 3. Go to API Keys page
echo 4. Create API key according to prompts
echo 5. Copy the generated API key
echo.
set /p api_key="Please enter your OpenAI API key: "
if "%api_key%"=="" (
    echo ❌ API key cannot be empty!
    pause
    exit /b 1
)
echo.
echo Setting environment variable...
setx OPENAI_API_KEY "%api_key%"
if %errorlevel% neq 0 (
    echo ❌ Failed to set environment variable!
    echo Please manually set the OPENAI_API_KEY environment variable
    echo.
    pause
    exit /b 1
)
echo ✅ Environment variable set successfully!
goto success

:qwen
echo.
echo 🎯 You selected Alibaba Cloud Qwen
echo.
echo Installing Qwen dependencies...
pip install --upgrade dashscope
if %errorlevel% neq 0 (
    echo ❌ Installation failed! Please check your network connection or install manually
    echo Manual installation command: pip install --upgrade dashscope
    echo.
    pause
    exit /b 1
)
echo ✅ Qwen dependencies installed successfully!
echo.
echo 📝 Next, you need to obtain a Qwen API key:
echo 1. Visit https://dashscope.console.aliyun.com/
echo 2. Log in to your Alibaba Cloud account
echo 3. Create API key according to prompts
echo 4. Copy the generated API key
echo.
set /p api_key="Please enter your Qwen API key: "
if "%api_key%"=="" (
    echo ❌ API key cannot be empty!
    pause
    exit /b 1
)
echo.
echo Setting environment variable...
setx DASHSCOPE_API_KEY "%api_key%"
if %errorlevel% neq 0 (
    echo ❌ Failed to set environment variable!
    echo Please manually set the DASHSCOPE_API_KEY environment variable
    echo.
    pause
    exit /b 1
)
echo ✅ Environment variable set successfully!

:success
echo.
echo ========================================
echo           🎉 Configuration Complete!
echo ========================================
echo.
echo ✅ Dependencies installed
echo ✅ Environment variables set
echo ✅ API configuration complete
echo.
echo 🚀 You can now use the project!
echo.
echo 📋 How to use:
echo 1. Double-click "run.bat" to run the main program
echo 2. Follow the prompts to select game and Mod
echo 3. Start automatic translation!
echo.
echo 💡 Tips:
echo - This configuration only needs to be run once
echo - No need to reconfigure unless you reinstall your system or change computers
echo - If you encounter issues, please check README.md or 小白说明文档.md
echo.
echo 🔄 Environment variables will take effect after next restart
echo If you need to use immediately, please reopen Command Prompt
echo.
pause
