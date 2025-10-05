@echo off
setlocal enabledelayedexpansion

REM =================================================================
REM Project Remis - Portable Release Build Script (Final Architect's Edition)
REM Version: 1.1.0
REM Assumption: This script is run from an already activated Conda/Python environment.
REM =================================================================

echo [INFO] =================================================================
echo [INFO] Project Remis - Portable Release Build Script
echo [INFO] =================================================================
echo.

REM --- Step 1: Initialization ---
REM ** CRITICAL FIX: Robustly determine the project root **
REM The project root is two levels up from this script's directory.
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\"

set "PROJECT_NAME=Project_Remis"
set "VERSION=1.1.0"
set "RELEASE_DIR=%PROJECT_ROOT%\%PROJECT_NAME%_%VERSION%"
set "RELEASE_DIR_NAME=%PROJECT_NAME%_%VERSION%"

echo [INFO] Verifying execution environment...
echo [INFO] Project Root detected as: %PROJECT_ROOT%
echo [INFO] Release will be built in: %RELEASE_DIR%
echo.

REM --- Step 2: Cleanup ---
echo [INFO] Cleaning up previous build directory...
if exist "%RELEASE_DIR%" (
    rd /s /q "%RELEASE_DIR%"
    echo [INFO] Old release directory removed.
) else (
    echo [INFO] No old directory to clean.
)
echo.

REM --- Step 3: Scaffolding ---
echo [INFO] Creating new release directory structure...
mkdir "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%\app"
mkdir "%RELEASE_DIR%\packages"
mkdir "%RELEASE_DIR%\python-embed"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create directory structure. Aborting.
    pause
    exit /b 1
)
echo [INFO] Directory structure created.
echo.

REM --- Step 4: User Action: Python ---
echo [ACTION REQUIRED] Please prepare the embedded Python environment.
echo =================================================================
echo 1. Go to https://www.python.org/downloads/windows/
echo 2. Download the "Windows embeddable package (64-bit)" for Python 3.12+.
echo 3. Unzip ALL contents into the following folder:
echo    %RELEASE_DIR%\python-embed\
echo =================================================================
pause
if not exist "%RELEASE_DIR%\python-embed\python.exe" (
    echo [ERROR] python.exe not found! Please ensure you have correctly extracted the files. Aborting.
    pause
    exit /b 1
)
echo [INFO] Embedded Python detected.
echo.

REM --- Step 5: Copy Source Code ---
echo [INFO] Copying application source code...
xcopy "%PROJECT_ROOT%\scripts" "%RELEASE_DIR%\app\scripts\" /s /i /y /q
xcopy "%PROJECT_ROOT%\data" "%RELEASE_DIR%\app\data\" /s /i /y /q
xcopy "%PROJECT_ROOT%\docs" "%RELEASE_DIR%\app\docs\" /s /i /y /q
copy "%PROJECT_ROOT%\requirements.txt" "%RELEASE_DIR%\app\requirements.txt" /y
copy "%PROJECT_ROOT%\README.md" "%RELEASE_DIR%\app\README.md" /y
copy "%PROJECT_ROOT%\README_EN.md" "%RELEASE_DIR%\app\README_EN.md" /y
copy "%PROJECT_ROOT%\LICENSE" "%RELEASE_DIR%\app\LICENSE" /y
copy "%PROJECT_ROOT%\banner.txt" "%RELEASE_DIR%\app\banner.txt" /y
echo [INFO] Source code copied.
echo.

REM --- Step 5.5: Create Required Empty Directories ---
echo [INFO] Creating required empty directories...
mkdir "%RELEASE_DIR%\app\logs" 2>nul
mkdir "%RELEASE_DIR%\app\my_translation" 2>nul
mkdir "%RELEASE_DIR%\app\source_mod" 2>nul
echo [INFO] Empty directories created.
echo.

REM --- Step 5.6: Copy Pre-written Setup Script ---
echo [INFO] Copying portable setup.bat...
copy "%SCRIPT_DIR%setup.bat" "%RELEASE_DIR%\setup.bat" /y
if %errorlevel% neq 0 (
    echo [ERROR] Failed to copy setup.bat
    pause
    exit /b 1
)
echo [INFO] Portable setup.bat copied successfully.
echo.

REM --- Step 6: Vendor Dependencies ---
echo [INFO] Downloading all dependencies to 'packages' folder...
REM ** CRITICAL FIX: This now uses the Python from your activated Conda env **
python -m pip download -r "%PROJECT_ROOT%\requirements.txt" -d "%RELEASE_DIR%\packages"
if %errorlevel% neq 0 (
    echo [ERROR] 'pip download' failed. Please ensure your Conda environment is activated and can access the internet. Aborting.
    pause
    exit /b 1
)
echo [INFO] All dependencies downloaded successfully.
echo.

REM --- Step 7: Copy Pre-written run.bat ---
echo [INFO] Copying portable run.bat...
copy "%SCRIPT_DIR%run.bat" "%RELEASE_DIR%\run.bat" /y
if %errorlevel% neq 0 (
    echo [ERROR] Failed to copy run.bat
    pause
    exit /b 1
)
echo [INFO] Portable run.bat copied successfully.
echo.

REM --- Step 8: Final Packaging ---
REM (This section remains the same, it checks for 7-Zip and packages the folder)
echo [INFO] Attempting to create ZIP archive...
set "SEVENZIP_PATH="
if exist "%ProgramFiles%\7-Zip\7z.exe" set "SEVENZIP_PATH=%ProgramFiles%\7-Zip\7z.exe"
if exist "%ProgramFiles(x86)%\7-Zip\7z.exe" set "SEVENZIP_PATH=%ProgramFiles(x86)%\7-Zip\7z.exe"

if not "%SEVENZIP_PATH%"=="" (
    echo [INFO] 7-Zip found. Compressing...
    "%SEVENZIP_PATH%" a -tzip "%PROJECT_ROOT%\%RELEASE_DIR_NAME%.zip" "%RELEASE_DIR%"
    echo [INFO] ZIP archive created: %PROJECT_ROOT%\%RELEASE_DIR_NAME%.zip
) else (
    echo [WARNING] 7-Zip not found. Skipping automatic zipping.
    echo [ACTION REQUIRED] Please manually zip the folder: %RELEASE_DIR%
)
echo.

REM --- Build Complete ---
echo =================================================================
echo [SUCCESS] Build process completed!
echo =================================================================
pause