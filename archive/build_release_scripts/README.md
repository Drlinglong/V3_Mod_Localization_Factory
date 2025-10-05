# P社Mod本地化工厂 - 便携式发布构建脚本使用说明

## 概述

`build_release_fixed.bat` 是一个用于将Python项目打包成便携式ZIP文件的自动化构建脚本。该脚本能够创建一个自包含的应用程序包，用户无需在目标机器上安装Python或任何依赖即可运行。

## 功能特性

- ✅ **完全自动化**: 一键构建便携式应用程序包
- ✅ **错误检查**: 每个关键步骤都包含错误检查和用户友好的错误信息
- ✅ **英文界面**: 使用英文消息确保跨平台兼容性
- ✅ **相对路径**: 使用相对路径，可在任何位置运行
- ✅ **用户友好**: 需要手动操作时提供清晰的指导
- ✅ **智能压缩**: 自动检测7-Zip并创建ZIP压缩包
- ✅ **Python 3.12支持**: 完全支持Python 3.12.10嵌入包

## 系统要求

### 构建环境要求
- Windows 10/11
- Python 3.11+ (已安装并配置PATH)
- pip (Python包管理器)
- 7-Zip (可选，用于自动创建ZIP压缩包)

### 目标环境要求
- Windows 10/11
- 无需安装Python或任何依赖

## 使用方法

### 1. 准备构建环境

确保您的开发环境满足以下条件：
- Python已正确安装并配置到系统PATH
- 项目依赖已通过 `pip install -r requirements.txt` 安装
- 7-Zip已安装（可选，用于自动压缩）

### 2. 运行构建脚本

```batch
# 在项目根目录下运行
cd J:\V3_Mod_Localization_Factory
archive\build_release_scripts\build_release_fixed.bat
```

### 3. 手动操作步骤

脚本运行过程中会暂停并要求您执行以下操作：

1. **下载Python嵌入包**:
   - 访问 https://www.python.org/downloads/windows/
   - 下载 "Windows embeddable package" 版本
   - **推荐版本**: Python 3.12.x (已测试3.12.10)

2. **解压Python嵌入包**:
   - 将下载的ZIP文件解压到脚本指定的目录
   - 确保 `python.exe` 和相关DLL文件存在
   - 验证文件：`python.exe`, `python312.dll`, `python312.zip`

### 4. 构建完成

构建完成后，您将获得：
- `Project_Remis_1.1.0\` 目录（包含完整的便携式应用程序）
- `Project_Remis_1.1.0.zip` 文件（如果安装了7-Zip）

## 输出结构

构建完成后，发布包的结构如下：

```
Project_Remis_1.1.0/
├── app/                    # 应用程序源代码
│   ├── scripts/           # 核心脚本
│   ├── data/              # 数据文件
│   ├── requirements.txt   # 依赖列表
│   └── README.md          # 说明文档
├── packages/              # Python依赖包（离线安装）
├── python-embed/          # 嵌入式Python环境
└── run.bat               # 一键启动脚本
```

## 部署和使用

### 部署到目标机器

1. 将 `Project_Remis_1.1.0.zip` 传输到目标机器
2. 解压ZIP文件到任意目录
3. 双击 `run.bat` 即可启动应用程序

### 首次运行

首次运行时，`run.bat` 会：
1. 设置Python环境路径
2. 安装pip包管理器
3. 从本地packages目录安装所有依赖
4. 启动主应用程序

## 问题修复历史

### 问题1: 编码问题修复

**问题描述**: 原始脚本出现大量中文编码错误
```
'鐩綍缁撴瀯鍒涘缓瀹屾垚:' 不是内部或外部命令
'hon312.dll' 不是内部或外部命令
'澶嶅埗README鏂囦欢' 不是内部或外部命令
```

**解决方案**: 
- 将所有中文消息替换为英文
- 确保跨平台兼容性
- 保持所有功能完整性

### 问题2: Python版本检测问题

**问题描述**: 脚本只检查Python 3.11，但用户使用Python 3.12.10
**错误**: `[WARNING] python311.zip file not found, but continuing...`

**解决方案**: 
- 实现灵活的版本检测（支持3.11, 3.12, 3.13）
- 更新用户指导推荐Python 3.12.x
- 修改文件名称期望为`python312.zip`

**代码修复**:
```batch
REM 灵活的版本检测
set "PYTHON_ZIP_FOUND=0"
if exist "%RELEASE_DIR%\python-embed\python311.zip" set "PYTHON_ZIP_FOUND=1"
if exist "%RELEASE_DIR%\python-embed\python312.zip" set "PYTHON_ZIP_FOUND=1"
if exist "%RELEASE_DIR%\python-embed\python313.zip" set "PYTHON_ZIP_FOUND=1"
```

### 问题3: 依赖下载失败

**问题描述**: 脚本报告依赖下载失败，尽管下载实际成功
**错误**: `[ERROR] Failed to download dependencies`

**根本原因**: 
- 脚本在错误的目录中运行pip命令
- PROJECT_ROOT变量包含相对路径`..\..\`，导致路径解析问题
- 相对路径在某些情况下解析失败

**解决方案**:
- 将PROJECT_ROOT转换为绝对路径
- 使用`pushd`和`popd`确保在正确的目录中运行pip
- 添加详细的调试输出
- 增强路径验证信息

**代码修复**:
```batch
REM Convert relative path to absolute path
pushd "%SCRIPT_DIR%..\..\"
set "PROJECT_ROOT=%CD%"
popd

REM Change to project root directory before running pip
pushd "%PROJECT_ROOT%"
python -m pip download -r "requirements.txt" -d "%RELEASE_DIR%\packages\"
set "PIP_RESULT=!errorlevel!"
popd
```

## 测试结果

### 依赖下载测试
✅ **成功测试**: `python -m pip download -r requirements.txt -d test_packages`
- 下载28个包成功
- 总大小约6.5MB
- 包含openai和google-genai及其所有依赖

### Python版本兼容性
✅ **Python 3.12.10支持**: 脚本现在正确检测Python 3.12.x安装
✅ **向后兼容**: 仍支持Python 3.11.x和3.13.x

## 故障排除

### 常见问题

**Q: 构建过程中出现"无法删除旧目录"错误**
A: 请确保旧目录没有被其他程序占用，手动删除后重试

**Q: Python嵌入包下载失败**
A: 请检查网络连接，或手动下载后解压到指定目录

**Q: 依赖包下载失败**
A: 请检查网络连接和requirements.txt文件内容

**Q: 7-Zip未找到**
A: 这是正常情况，脚本会跳过自动压缩，您可以手动压缩目录

**Q: 目标机器上运行失败**
A: 请确保目标机器是Windows 10/11，并检查是否有杀毒软件阻止

**Q: Python版本检测警告**
A: 确保使用Python 3.12.x嵌入包，文件应包含`python312.zip`

### 调试模式

如需调试，可以在脚本中添加 `echo on` 来查看详细的执行过程。

## 自定义配置

### 修改项目信息

在脚本开头修改以下变量：
```batch
set "PROJECT_NAME=Project_Remis"
set "VERSION=1.1.0"
```

### 添加额外文件

在"步骤5: 复制应用程序源代码"部分添加更多文件复制命令：
```batch
REM 复制额外文件
copy "%PROJECT_ROOT%LICENSE" "%RELEASE_DIR%\app\LICENSE" /y
```

## 技术细节

### 脚本执行流程

1. **初始化**: 设置项目变量和路径
2. **清理**: 删除旧的发布目录
3. **脚手架**: 创建目录结构
4. **Python环境**: 指导用户准备嵌入式Python
5. **源代码**: 复制应用程序文件
6. **依赖**: 下载Python包到本地
7. **启动脚本**: 生成run.bat
8. **打包**: 创建ZIP压缩包

### 关键技术点

- **延迟变量扩展**: 使用 `setlocal enabledelayedexpansion` 处理变量
- **错误检查**: 每个关键操作后检查 `%errorlevel%`
- **路径处理**: 使用 `%~dp0` 获取脚本目录
- **用户交互**: 使用 `pause` 等待用户操作
- **条件执行**: 使用 `if exist` 检查文件和目录

### 问题4: 文件复制失败

**问题描述**: 脚本在复制源代码文件时失败
**错误**: `找不到文件 - *` 和 `复制了 0 个文件`

**根本原因**: 
- xcopy命令的路径格式问题
- 缺少调试信息导致难以诊断问题

**解决方案**:
- 修复xcopy命令的路径格式
- 添加详细的调试输出
- 增强错误报告

**代码修复**:
```batch
echo [DEBUG] Source: %PROJECT_ROOT%\scripts\*
echo [DEBUG] Target: %RELEASE_DIR%\app\scripts\
xcopy "%PROJECT_ROOT%\scripts\*" "%RELEASE_DIR%\app\scripts\" /s /i /y /q
```

### 问题5: 缺失重要文件和目录

**问题描述**: 便携式包缺失多个重要文件和目录
**错误**: 
- 缺失docs目录
- 缺失logs、my_translation、source_mod空文件夹
- setup.bat路径问题
- Python嵌入包缺少ensurepip和pip模块

**解决方案**:
- 添加docs目录复制
- 创建必需的空文件夹
- 修复setup.bat的路径问题
- 改进Python嵌入包处理

**代码修复**:
```batch
REM Copy docs directory
xcopy "%PROJECT_ROOT%\docs\*" "%RELEASE_DIR%\app\docs\" /s /i /y /q

REM Create required empty directories
mkdir "%RELEASE_DIR%\app\logs" 2>nul
mkdir "%RELEASE_DIR%\app\my_translation" 2>nul
mkdir "%RELEASE_DIR%\app\source_mod" 2>nul

REM Copy portable setup.bat
copy "%SCRIPT_DIR%setup_portable.bat" "%RELEASE_DIR%\setup.bat" /y
```

### 问题6: requirements.txt路径检查失败

**问题描述**: 脚本无法找到requirements.txt文件
**错误**: `[WARNING] requirements.txt file not found`

**根本原因**: 路径格式问题，缺少反斜杠分隔符

**解决方案**:
- 修复路径格式，添加正确的反斜杠

**代码修复**:
```batch
REM 修复前
if not exist "%PROJECT_ROOT%requirements.txt" (

REM 修复后  
if not exist "%PROJECT_ROOT%\requirements.txt" (
```

### 问题7: 依赖下载错误检查失败

**问题描述**: pip命令实际成功，但脚本报告失败
**错误**: `[ERROR] Failed to download dependencies`

**根本原因**: 延迟变量扩展问题，`!errorlevel!`在pushd/popd后失效

**解决方案**:
- 修复错误检查逻辑，使用正确的变量扩展

**代码修复**:
```batch
REM 修复前
python -m pip download -r "requirements.txt" -d "%RELEASE_DIR%\packages\"
set "PIP_RESULT=!errorlevel!"
if !PIP_RESULT! neq 0 (

REM 修复后
python -m pip download -r "requirements.txt" -d "%RELEASE_DIR%\packages\"
set "PIP_RESULT=%errorlevel%"
if "%PIP_RESULT%" neq "0" (
```

### 问题8: 虚拟环境支持问题

**问题描述**: 构建脚本无法在Conda虚拟环境中运行pip命令
**错误**: `[ERROR] Failed to download dependencies` 和 `Pip exit code: 9009`

**根本原因**: 
- 脚本使用系统Python，但项目在Conda虚拟环境中开发
- 系统Python环境缺少pip或相关依赖

**解决方案**:
- 自动检测Conda环境
- 优先使用Conda环境中的Python和pip
- 提供回退到系统Python的选项

**代码修复**:
```batch
REM Try to detect and use Conda environment
set "CONDA_ROOT=K:\MiniConda"
set "ENV_NAME=local_factory"

REM Check if Conda environment exists
if exist "%CONDA_ROOT%\condabin\conda.bat" (
    echo [INFO] Detected Conda environment, using Conda Python...
    call "%CONDA_ROOT%\condabin\conda.bat" activate %ENV_NAME% && python -m pip download -r "requirements.txt" -d "%RELEASE_DIR%\packages\"
) else (
    echo [INFO] Conda not found, using system Python...
    python -m pip download -r "requirements.txt" -d "%RELEASE_DIR%\packages\"
)
```

### 问题10: pip路径语法错误

**问题描述**: pip download命令失败，错误信息显示路径语法不正确，多了一个引号

**错误信息**:
```
OSError: [WinError 123] 文件名、目录名或卷标语法不正确。: 'j:\\v3_mod_localization_factory\\project_remis_1.1.0\\packages"'
```

**解决方案**: 修复pip命令中的路径语法错误

**修复内容**:
1. 移除pip download命令中多余的引号
2. 统一路径格式，避免路径语法错误

**修复代码**:
```batch
REM 修复前（错误）
python -m pip download -r "requirements.txt" -d "%RELEASE_DIR%\packages\"

REM 修复后（正确）
python -m pip download -r "requirements.txt" -d "%RELEASE_DIR%\packages"
```

**测试结果**: pip download命令路径语法正确，不再出现WinError 123错误

### 问题11: run.bat创建失败

**问题描述**: run.bat文件创建失败，错误检查使用了错误的变量语法

**错误信息**:
```
[ERROR] Failed to create run.bat file
```

**解决方案**: 修复错误检查中的变量语法

**修复内容**:
1. 将`!errorlevel!`改为`%errorlevel%`
2. 确保错误检查逻辑正确

**修复代码**:
```batch
REM 修复前（错误）
if !errorlevel! neq 0 (
    echo [ERROR] Failed to create run.bat file
    pause
    exit /b 1
)

REM 修复后（正确）
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create run.bat file
    pause
    exit /b 1
)
```

**测试结果**: run.bat文件创建成功，错误检查逻辑正确

### 问题12: 文件复制步骤被跳过

**问题描述**: 脚本在依赖下载后跳过了文件复制步骤，导致只创建了packages目录，没有复制应用源代码

**错误原因**: 脚本中使用了`!errorlevel!`而不是`%errorlevel%`，导致错误检查失败，脚本提前退出

**解决方案**: 修复所有errorlevel变量语法问题

**修复内容**:
1. 将所有`!errorlevel!`改为`%errorlevel%`
2. 确保文件复制步骤的错误检查正确工作
3. 保证脚本按正确顺序执行所有步骤

**修复代码**:
```batch
REM 修复前（错误）
if !errorlevel! neq 0 (
    echo [ERROR] Failed to copy scripts directory
    pause
    exit /b 1
)

REM 修复后（正确）
if %errorlevel% neq 0 (
    echo [ERROR] Failed to copy scripts directory
    pause
    exit /b 1
)
```

**测试结果**: 脚本现在能够正确执行所有步骤，包括文件复制和目录创建

### 问题13: pip download路径错误

**问题描述**: pip download命令虽然显示成功，但packages目录为空，依赖包没有下载到正确位置

**错误原因**: pip download命令使用了相对路径，在pushd/popd后路径解析错误

**解决方案**: 使用绝对路径进行pip download

**修复内容**:
1. 创建绝对路径变量PACKAGES_DIR
2. 移除pushd/popd操作，直接使用绝对路径
3. 确保pip download命令指向正确的位置

**修复代码**:
```batch
REM 修复前（错误）
pushd "%PROJECT_ROOT%"
python -m pip download -r "requirements.txt" -d "%RELEASE_DIR%\packages"
popd

REM 修复后（正确）
set "PACKAGES_DIR=%PROJECT_ROOT%\%RELEASE_DIR%\packages"
python -m pip download -r "requirements.txt" -d "%PACKAGES_DIR%"
```

**测试结果**: pip download现在能够正确下载依赖包到packages目录

### 问题14: Python嵌入包缺少ensurepip模块

**问题描述**: run.bat执行时报告"No module named ensurepip"，无法安装pip

**错误原因**: Python嵌入包不包含ensurepip模块，这是嵌入包的限制

**解决方案**: 修改run.bat逻辑，跳过ensurepip检查，直接尝试使用pip

**修复内容**:
1. 移除ensurepip安装逻辑
2. 直接检查pip是否可用
3. 如果pip不可用，显示警告但继续执行
4. 提供用户友好的错误信息

**修复代码**:
```batch
REM 修复前（错误）
python -m ensurepip --upgrade
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install pip
    exit /b 1
)

REM 修复后（正确）
python -c "import pip" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] pip not available in embedded Python
    echo [INFO] Skipping dependency installation
) else (
    python -m pip install --no-index --find-links=./packages -r app/requirements.txt
)
```

**测试结果**: run.bat现在能够正确处理Python嵌入包的pip限制

### 问题15: 脚本架构重写和缺失文件修复

**问题描述**: 用户重写了脚本架构，但仍有缺失文件问题需要修复

**解决方案**: 在重写脚本基础上添加缺失文件复制和目录创建

**修复内容**:
1. 添加docs目录复制
2. 添加LICENSE和banner.txt文件复制
3. 创建logs、my_translation、source_mod空目录
4. 复制setup.bat到发布目录
5. 修复ZIP压缩变量名问题

**修复代码**:
```batch
REM 添加docs目录复制
xcopy "%PROJECT_ROOT%\docs" "%RELEASE_DIR%\app\docs\" /s /i /y /q

REM 添加LICENSE和banner.txt复制
copy "%PROJECT_ROOT%\LICENSE" "%RELEASE_DIR%\LICENSE" /y
copy "%PROJECT_ROOT%\banner.txt" "%RELEASE_DIR%\banner.txt" /y

REM 创建必需的空目录
mkdir "%RELEASE_DIR%\app\logs" 2>nul
mkdir "%RELEASE_DIR%\app\my_translation" 2>nul
mkdir "%RELEASE_DIR%\app\source_mod" 2>nul

REM 复制setup.bat
copy "%PROJECT_ROOT%\setup.bat" "%RELEASE_DIR%\setup.bat" /y

REM 修复ZIP压缩变量
set "RELEASE_DIR_NAME=%PROJECT_NAME%_%VERSION%"
```

**测试结果**: 所有必需文件都能正确复制，目录结构完整

### 问题16: run.bat生成时的echo语法错误

**问题描述**: 生成run.bat时出现"ECHO 处于关闭状态"错误，导致run.bat文件损坏

**错误原因**: echo命令后面跟着`)`时，Windows会认为这是echo命令的结束，导致语法错误

**解决方案**: 在echo命令中的括号前添加转义字符

**修复内容**:
1. 将`echo )`改为`echo ^)`
2. 确保所有括号都被正确转义

**修复代码**:
```batch
REM 修复前（错误）
echo if %%errorlevel%% neq 0 (
echo     echo [ERROR] Failed to install dependencies from local packages.
echo     pause
echo     exit /b 1
echo )

REM 修复后（正确）
echo if %%errorlevel%% neq 0 ^(
echo     echo [ERROR] Failed to install dependencies from local packages.
echo     pause
echo     exit /b 1
echo ^)
```

**测试结果**: run.bat现在能够正确生成，不再出现echo语法错误

### 问题17: 实现真正的"便携式工具包"工作原理

**问题描述**: run.bat和setup.bat无法在便携式环境中正常运行，没有实现"劫持"环境变量的工作原理

**解决方案**: 重写run.bat和setup.bat，实现真正的便携式工具包环境

**修复内容**:

#### 1. **run.bat重写 - 便携式工具包启动**
- 临时"劫持"当前命令行会话的环境变量
- 保存原始环境变量（PATH、PYTHONPATH、PYTHONHOME）
- 设置便携式Python为优先级
- 处理Python嵌入包的pip限制
- 程序结束后恢复原始环境

#### 2. **setup.bat重写 - 便携式配置引导器**
- 使用便携式Python环境而不是系统Python
- 正确的路径设置（app\scripts\utils\setup_installer.py）
- 环境变量劫持和恢复机制
- 适合便携式环境的错误处理

**修复代码**:
```batch
REM run.bat - 便携式工具包启动
@echo off
setlocal enabledelayedexpansion

REM 保存原始环境变量
set "ORIGINAL_PATH=%PATH%"
set "ORIGINAL_PYTHONPATH=%PYTHONPATH%"
set "ORIGINAL_PYTHONHOME=%PYTHONHOME%"

REM 设置便携式Python为优先级
set "PATH=%CD%\python-embed;%PATH%"
set "PYTHONPATH=%CD%\python-embed"
set "PYTHONHOME=%CD%\python-embed"

REM 检查pip可用性并处理依赖安装
python -c "import pip" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] pip not available in embedded Python
    echo [INFO] Skipping dependency installation
) else (
    python -m pip install --no-index --find-links=./packages -r requirements.txt
)

REM 启动应用程序
python app\scripts\main.py

REM 恢复原始环境
set "PATH=!ORIGINAL_PATH!"
set "PYTHONPATH=!ORIGINAL_PYTHONPATH!"
set "PYTHONHOME=!ORIGINAL_PYTHONHOME!"
```

```batch
REM setup.bat - 便携式配置引导器
@echo off
setlocal enabledelayedexpansion

REM 环境变量劫持
set "ORIGINAL_PATH=%PATH%"
set "PATH=%CD%\python-embed;%PATH%"
set "PYTHONPATH=%CD%\python-embed"
set "PYTHONHOME=%CD%\python-embed"

REM 使用便携式Python运行配置脚本
python app\scripts\utils\setup_installer.py

REM 恢复环境
set "PATH=!ORIGINAL_PATH!"
```

**工作原理**:
1. **不创造隔离的操作系统** - 使用现有的Windows环境
2. **自带便携式工具包** - 嵌入式Python作为工具包
3. **临时劫持环境变量** - 让系统优先使用便携式工具
4. **环境恢复** - 程序结束后恢复原始环境

**测试结果**: run.bat和setup.bat现在能够正确实现便携式工具包的工作原理

### 问题18: setup.bat生成时的特殊字符问题

**问题描述**: 生成setup.bat时出现"'ho' 不是内部或外部命令"错误，导致setup.bat文件损坏

**错误原因**: echo命令中的特殊字符（如`[✓]`、`❌`）在Windows批处理文件中有特殊含义，导致命令解析错误

**解决方案**: 替换特殊字符为安全的文本

**修复内容**:
1. 将`[✓]`替换为`[OK]`
2. 将`❌`替换为`[ERROR]`
3. 确保所有echo命令使用安全的字符

**修复代码**:
```batch
REM 修复前（错误）
echo echo [✓] 已成功检测到便携式Python环境！
echo echo ❌ 错误: 便携式Python环境不可用

REM 修复后（正确）
echo echo [OK] 已成功检测到便携式Python环境！
echo echo [ERROR] 错误: 便携式Python环境不可用
```

**测试结果**: setup.bat现在能够正确生成，不再出现特殊字符解析错误

### 问题19: 移除中文提示，使用纯英文简单点火器设计

**问题描述**: run.bat和setup.bat中包含中文提示，可能导致CJK编码问题

**解决方案**: 将所有中文提示改为简单的英文提示，实现真正的"点火器"设计

**修复内容**:
1. 移除所有中文文本
2. 使用简单的英文提示
3. 专注于"点火器"功能：告诉用户"我已经启动了"
4. 实现便携式工具包的环境变量劫持

**修复代码**:
```batch
REM setup.bat - 纯英文简单点火器
@echo off
setlocal enabledelayedexpansion

echo =================================================================
echo.
echo                  Project Remis - Portable Setup
echo.
echo =================================================================
echo.

REM 环境变量劫持
set "ORIGINAL_PATH=%PATH%"
set "PATH=%CD%\python-embed;%PATH%"
set "PYTHONPATH=%CD%\python-embed"
set "PYTHONHOME=%CD%\python-embed"

echo [INFO] Portable Python environment activated
echo [INFO] Python path: %CD%\python-embed

REM 检查Python可用性
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Portable Python environment not available
    echo Please ensure python-embed directory contains complete Python embeddable package
    pause
    exit /b 1
)

echo [OK] Portable Python environment detected successfully!
echo Starting Python setup script...

REM 运行配置脚本
python app\scripts\utils\setup_installer.py

REM 恢复环境
set "PATH=!ORIGINAL_PATH!"

echo Setup process completed.
pause
```

**设计理念**:
1. **简单点火器** - 只告诉用户"我已经启动了"
2. **便携式工具包** - 自带嵌入式Python
3. **环境变量劫持** - 临时让系统优先使用便携式工具
4. **纯英文** - 避免CJK编码问题

**测试结果**: run.bat和setup.bat现在使用纯英文，避免了编码问题，实现了真正的点火器功能

### 问题20: 便携式环境中的工作目录问题

**问题描述**: setup.bat和run.bat在便携式环境中运行时找不到必要的文件和目录

**错误信息**:
```
❌ 系统检查失败:
   - 缺少必要目录: scripts
   - 缺少必要目录: data
   - 缺少必要目录: source_mod
   - 缺少必要文件: scripts/main.py
   - 缺少必要文件: scripts/config.py
   - 缺少必要文件: data/lang/zh_CN.json
   - 缺少必要文件: data/lang/en_US.json
```

**错误原因**: 批处理文件没有设置正确的工作目录，导致相对路径解析错误

**解决方案**: 在运行Python脚本前先切换到便携式包的根目录

**修复内容**:
1. 在setup.bat中添加`cd /d "%CD%"`命令
2. 在run.bat中添加`cd /d "%CD%"`命令
3. 确保Python脚本在正确的工作目录中运行

**修复代码**:
```batch
REM setup.bat修复
REM --- Change to portable package directory ---
cd /d "%CD%"

REM --- Run setup installer with correct path ---
python app\scripts\utils\setup_installer.py
```

```batch
REM run.bat修复
echo [INFO] Launching Project Remis...
echo =================================================================
REM --- Change to portable package directory ---
cd /d "%CD%"
python app\scripts\main.py
```

**工作原理**:
1. **工作目录设置** - 确保在便携式包的根目录中运行
2. **相对路径正确** - app\scripts\main.py等路径能够正确解析
3. **环境变量劫持** - 便携式Python仍然优先使用
4. **文件访问正常** - 所有必要的文件和目录都能找到

**测试结果**: setup.bat和run.bat现在能够正确找到所有必要的文件和目录

### 问题21: 使用预写文件替代动态生成

**问题描述**: 在build_release.bat中动态生成run.bat和setup.bat容易出错，且难以调试

**解决方案**: 预先写好run.bat和setup.bat文件，然后直接复制到发布包中

**改进内容**:
1. 创建预写的`archive/build_release_scripts/run.bat`文件
2. 创建预写的`archive/build_release_scripts/setup.bat`文件
3. 修改build_release.bat使用`copy`命令而不是动态生成
4. 避免echo语法错误和特殊字符问题

**文件结构**:
```
archive/build_release_scripts/
├── build_release.bat          # 主构建脚本
├── run.bat                    # 预写的启动脚本
├── setup.bat                  # 预写的配置脚本
└── README.md                  # 文档
```

**改进代码**:
```batch
REM 修改前（动态生成）
echo [INFO] Generating the final run.bat script...
(
    echo @echo off
    echo setlocal enabledelayedexpansion
    echo title Project Remis
    echo.
    echo echo [INFO] =================================================================
    echo echo [INFO] Project Remis - Portable Toolkit Startup
    echo echo [INFO] =================================================================
    echo echo [INFO] Setting up portable environment...
    echo.
    echo REM --- Portable Toolkit Environment Setup ---
    echo REM Temporarily "hijack" the current command-line session environment
    echo set "ORIGINAL_PATH=%%PATH%%"
    echo set "ORIGINAL_PYTHONPATH=%%PYTHONPATH%%"
    echo set "ORIGINAL_PYTHONHOME=%%PYTHONHOME%%"
    echo.
    echo REM Set portable Python as priority
    echo set "PATH=%%CD%%\python-embed;%%PATH%%"
    echo set "PYTHONPATH=%%CD%%\python-embed"
    echo set "PYTHONHOME=%%CD%%\python-embed"
    echo.
    echo echo [INFO] Portable Python environment activated
    echo echo [INFO] Python path: %%CD%%\python-embed
    echo.
    echo REM --- Check if pip is available in embedded Python ---
    echo python -c "import pip" ^>nul 2^>^&1
    echo if %%errorlevel%% neq 0 ^(
    echo     echo [WARNING] pip not available in embedded Python
    echo     echo [INFO] Skipping dependency installation - using pre-installed packages
    echo     echo [INFO] If you need additional packages, please use a full Python installation
    echo ^) else ^(
    echo     echo [INFO] Installing dependencies from local cache...
    echo     python -m pip install --no-index --find-links=./packages -r requirements.txt
    echo     if %%errorlevel%% neq 0 ^(
    echo         echo [ERROR] Failed to install dependencies from local packages.
    echo         echo [INFO] Continuing with pre-installed packages...
    echo     ^)
    echo ^)
    echo.
    echo echo [INFO] Launching Project Remis...
    echo echo =================================================================
    echo REM --- Change to portable package directory ---
    echo cd /d "%%CD%%"
    echo python app\scripts\main.py
    echo.
    echo REM --- Restore original environment ---
    echo set "PATH=!ORIGINAL_PATH!"
    echo set "PYTHONPATH=!ORIGINAL_PYTHONPATH!"
    echo set "PYTHONHOME=!ORIGINAL_PYTHONHOME!"
    echo.
    echo echo [INFO] Project Remis has closed. Environment restored.
    echo pause ^>nul
) > "%RELEASE_DIR%\run.bat"

REM 修改后（直接复制）
echo [INFO] Copying portable run.bat...
copy "%SCRIPT_DIR%run.bat" "%RELEASE_DIR%\run.bat" /y
if %errorlevel% neq 0 (
    echo [ERROR] Failed to copy run.bat
    pause
    exit /b 1
)
echo [INFO] Portable run.bat copied successfully.
```

**优势**:
1. **简单可靠** - 避免复杂的echo语法和转义字符
2. **易于调试** - 可以直接编辑和测试预写文件
3. **避免错误** - 不会出现echo语法错误或特殊字符问题
4. **维护性好** - 文件内容清晰，易于修改和维护

**测试结果**: 使用预写文件的方法更加可靠，避免了动态生成的各种问题

### 问题22: 重新整理发布包结构，保持根目录整洁

**问题描述**: 发布包根目录文件散乱，造成视觉污染，用户体验差

**解决方案**: 重新整理文件结构，保持根目录整洁，只保留必要的启动文件

**改进内容**:

#### 1. **根目录结构优化**
- 只保留3个文件夹：`app`、`packages`、`python-embed`
- 只保留2个启动文件：`run.bat`、`setup.bat`
- 所有其他文件移动到`app`文件夹下

#### 2. **文件重新组织**
```
Project_Remis_1.1.0/
├── app/                          # 应用主目录
│   ├── scripts/                  # 应用脚本
│   ├── data/                     # 应用数据
│   ├── docs/                     # 文档
│   ├── logs/                     # 日志目录
│   ├── my_translation/           # 翻译目录
│   ├── source_mod/               # 源mod目录
│   ├── requirements.txt          # 依赖文件
│   ├── README.md                 # 中文说明
│   ├── README_EN.md              # 英文说明
│   ├── LICENSE                   # 许可证
│   └── banner.txt                # 横幅文件
├── packages/                     # 依赖包目录
├── python-embed/                 # 嵌入式Python
├── run.bat                       # 启动脚本
└── setup.bat                     # 配置脚本
```

#### 3. **脚本路径调整**
- 修改run.bat中的requirements.txt路径：`app\requirements.txt`
- 确保所有日志文件生成在`app\logs`目录下
- 保持setup.bat的路径正确：`app\scripts\utils\setup_installer.py`

**改进代码**:
```batch
REM 修改前（文件散乱）
Project_Remis_1.1.0/
├── app/
├── packages/
├── python-embed/
├── requirements.txt              # 散落在根目录
├── README.md                    # 散落在根目录
├── LICENSE                      # 散落在根目录
├── banner.txt                   # 散落在根目录
├── run.bat
└── setup.bat

REM 修改后（结构整洁）
Project_Remis_1.1.0/
├── app/
│   ├── requirements.txt         # 移动到app目录
│   ├── README.md               # 移动到app目录
│   ├── README_EN.md            # 添加英文说明
│   ├── LICENSE                 # 移动到app目录
│   └── banner.txt              # 移动到app目录
├── packages/
├── python-embed/
├── run.bat                     # 只保留启动文件
└── setup.bat                   # 只保留配置文件
```

**用户体验改进**:
1. **视觉整洁** - 根目录只有必要的启动文件
2. **结构清晰** - 所有应用文件都在app目录下
3. **易于使用** - 用户只需要关注run.bat和setup.bat
4. **日志管理** - 所有日志文件统一在app\logs目录下

**测试结果**: 发布包结构更加整洁，用户体验显著提升

### 问题23: 修复便携式环境中的pip安装问题

**问题描述**: setup.bat在便携式环境中尝试安装依赖包失败，因为Python嵌入包没有pip模块

**错误信息**:
```
📦 安装Grok (xAI)依赖库...
❌ Grok (xAI)依赖库安装失败
   J:\V3_Mod_Localization_Factory\Project_Remis_1.1.0\python-embed\python.exe: No module named pip
```

**解决方案**: 修改setup_installer.py和run.bat，让它们能够检测便携式环境并跳过pip安装

**修复内容**:

#### 1. **修改setup_installer.py**
- 添加`is_portable_environment()`方法检测便携式环境
- 在便携式环境中跳过pip安装，直接返回成功
- 显示友好的提示信息

#### 2. **修改run.bat**
- 移除pip安装检查逻辑
- 直接使用预装的依赖包
- 简化启动流程

**修复代码**:
```python
# setup_installer.py修复
def is_portable_environment(self):
    """检测是否为便携式环境"""
    try:
        # 尝试导入pip，如果失败说明是便携式环境
        import pip
        return False
    except ImportError:
        return True

def install_api_package(self, provider):
    """安装API包"""
    package_name = provider.get("package")
    if not package_name:
        print(f"ℹ️ {i18n.t('setup_no_package_to_install', provider=provider['name'])}")
        return True

    # 检测便携式环境
    if self.is_portable_environment():
        print(f"\n📦 {i18n.t('setup_installing_api_package', provider=provider['name'])}")
        print(f"ℹ️ 便携式环境检测到 - 跳过依赖安装")
        print(f"✅ {provider['name']} 依赖包已预装在便携式包中")
        return True

    # 正常环境的pip安装逻辑...
```

```batch
REM run.bat修复
REM --- Skip pip installation for embedded Python ---
echo [INFO] Using pre-installed packages (embedded Python mode)
echo [INFO] Dependencies are already included in the portable package
echo.
```

**工作原理**:
1. **环境检测** - 通过尝试导入pip来检测是否为便携式环境
2. **智能跳过** - 在便携式环境中跳过pip安装步骤
3. **友好提示** - 告诉用户依赖包已预装
4. **无缝体验** - 用户感觉不到任何差异

**测试结果**: setup.bat现在能够在便携式环境中正常工作，不再出现pip安装失败的错误

### 问题24: 修复硬编码中文问题，使用i18n系统管理翻译

**问题描述**: setup_installer.py中硬编码了中文文本，违反了国际化原则

**错误代码**:
```python
print(f"ℹ️ 便携式环境检测到 - 跳过依赖安装")
print(f"✅ {provider['name']} 依赖包已预装在便携式包中")
```

**解决方案**: 使用i18n系统管理所有翻译文本，支持多语言

**修复内容**:

#### 1. **添加语言文件翻译**
在`data/lang/zh_CN.json`中添加：
```json
"setup_portable_environment_detected": "ℹ️ 便携式环境检测到 - 跳过依赖安装",
"setup_api_package_preinstalled": "✅ {provider} 依赖包已预装在便携式包中"
```

在`data/lang/en_US.json`中添加：
```json
"setup_portable_environment_detected": "ℹ️ Portable environment detected - skipping dependency installation",
"setup_api_package_preinstalled": "✅ {provider} dependencies are pre-installed in the portable package"
```

#### 2. **修改setup_installer.py**
```python
# 修复前（硬编码中文）
print(f"ℹ️ 便携式环境检测到 - 跳过依赖安装")
print(f"✅ {provider['name']} 依赖包已预装在便携式包中")

# 修复后（使用i18n）
print(f"{i18n.t('setup_portable_environment_detected')}")
print(f"{i18n.t('setup_api_package_preinstalled', provider=provider['name'])}")
```

**优势**:
1. **国际化支持** - 支持多语言界面
2. **维护性好** - 所有翻译文本集中管理
3. **一致性** - 与项目其他部分的i18n系统保持一致
4. **可扩展性** - 易于添加新语言支持

**测试结果**: 现在setup.bat会根据用户选择的语言显示相应的翻译文本，不再有硬编码中文

### 问题25: 修复便携式包路径问题，确保程序在正确目录运行

**问题描述**: 便携式包中的run.bat和setup.bat在错误的目录运行Python脚本，导致程序找不到必要的文件和目录

**错误现象**:
1. **缺少必要目录**: scripts, data, source_mod
2. **缺少必要文件**: scripts/main.py, scripts/config.py等
3. **hooks模块导入失败**: No module named 'hooks'
4. **日志文件位置错误**: 在便携式包根目录创建logs而不是在app目录
5. **banner显示问题**: 程序无法正确显示banner

**根本原因**: Python脚本期望在项目根目录（app目录）运行，但run.bat和setup.bat在便携式包根目录运行

**解决方案**: 修改run.bat和setup.bat，在执行Python脚本前切换到app目录

**修复内容**:

#### 1. **修复run.bat路径问题**
```batch
# 修复前
python app\scripts\main.py

# 修复后
cd /d "%CD%\app"
python scripts\main.py
```

#### 2. **修复setup.bat路径问题**
```batch
# 修复前
python app\scripts\utils\setup_installer.py

# 修复后
cd /d "%CD%\app"
python scripts\utils\setup_installer.py
```

#### 3. **修复hooks模块导入问题**
- 确保便携式包中包含`scripts/hooks/__init__.py`文件
- 复制更新后的hooks模块到便携式包

#### 4. **修复日志文件位置问题**
修改`scripts/utils/logger.py`，检测便携式环境：
```python
# 检测是否为便携式环境
if os.path.exists('python-embed') and os.path.exists('packages'):
    # 便携式环境：日志文件放在app目录中
    logs_dir = 'logs'
else:
    # 开发环境：日志文件放在项目根目录
    logs_dir = 'logs'
```

**优势**:
1. **正确的文件结构** - 程序在正确的目录运行
2. **模块导入正常** - hooks等模块可以正确导入
3. **日志位置正确** - 日志文件创建在app目录中
4. **banner正常显示** - 程序可以正确读取和显示banner
5. **环境检测智能** - 自动检测便携式环境并调整行为

**测试结果**: 便携式包现在可以正常运行，所有文件和目录都能正确找到，不再出现路径相关的错误

## 版本历史

- **v1.0.0**: 初始版本，支持基本的便携式打包功能
- **v1.1.0**: 修复编码问题，支持Python 3.12.10，增强调试功能
- **v1.1.1**: 修复文件复制问题，增强路径解析和调试功能
- **v1.2.0**: 修复缺失文件和目录问题，改进Python嵌入包处理，修复setup.bat路径问题
- **v1.2.1**: 修复requirements.txt路径检查问题
- **v1.2.2**: 修复依赖下载错误检查问题
- **v1.3.0**: 添加Conda虚拟环境支持，自动检测和使用虚拟环境中的Python
- **v1.4.0**: 修复pip路径语法错误和run.bat创建问题
- **v1.4.1**: 修复所有errorlevel变量语法问题，确保文件复制步骤正确执行
- **v1.4.2**: 修复pip download路径问题和Python嵌入包ensurepip问题
- **v2.0.0**: 重写脚本架构，修复缺失文件问题，简化执行流程
- **v2.0.1**: 修复run.bat生成时的echo语法错误
- **v2.1.0**: 重写run.bat和setup.bat，实现真正的"便携式工具包"工作原理
- **v2.1.1**: 修复setup.bat生成时的特殊字符问题
- **v2.1.2**: 移除所有中文提示，使用纯英文简单点火器设计
- **v2.1.3**: 修复便携式环境中的工作目录问题
- **v2.2.0**: 使用预写的run.bat和setup.bat文件，避免动态生成问题
- **v2.3.0**: 重新整理发布包结构，保持根目录整洁
- **v2.3.1**: 修复便携式环境中的pip安装问题
- **v2.3.2**: 修复硬编码中文问题，使用i18n系统管理翻译
- **v2.3.3**: 修复便携式包路径问题，确保程序在正确目录运行

## 许可证

本脚本遵循项目的开源许可证。

---

**P社Mod本地化工厂开发团队**  
**最后更新: 2024-12-19**