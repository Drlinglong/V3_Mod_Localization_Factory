# 📋 详细安装步骤

> 完整的项目安装和配置指南，适合所有用户

## 🎯 安装方式选择

### 🚀 方式一：一键安装（推荐新手）
- **优点**: 自动化程度高，出错率低
- **适用**: 不熟悉命令行操作的用户
- **文件**: `首次安装配置.bat`

### 🔧 方式二：手动安装（推荐有经验用户）
- **优点**: 可控性强，便于调试
- **适用**: 熟悉Python环境的用户
- **步骤**: 见下方详细说明

## 🚀 一键安装步骤

### 1. 下载项目
```bash
# 方式1: 使用Git克隆
git clone https://github.com/your-repo/V3_Mod_Localization_Factory.git

# 方式2: 直接下载ZIP包
# 从GitHub下载并解压到本地
```

### 2. 运行配置脚本
1. 进入项目目录
2. 双击 `首次安装配置.bat`
3. 按照提示选择AI服务商
4. 输入对应的API密钥
5. 等待自动安装完成

### 3. 验证安装
**推荐方式**：双击运行 `run.bat`
- 自动检测环境配置
- 显示简洁的状态信息
- 自动激活虚拟环境（如果存在）

**手动方式**：
```bash
python scripts/main.py
```
如果看到版本信息界面，说明安装成功！

## 🔧 手动安装步骤

### 1. 环境准备

#### 安装Python
- 下载 [Python 3.8+](https://www.python.org/downloads/)
- 安装时勾选"Add Python to PATH"
- 验证安装：`python --version`

#### 安装Git（可选）
- 下载 [Git](https://git-scm.com/downloads)
- 安装时选择默认选项即可

### 2. 项目设置

#### 克隆/下载项目
```bash
# 使用Git
git clone https://github.com/your-repo/V3_Mod_Localization_Factory.git
cd V3_Mod_Localization_Factory

# 或直接下载ZIP包并解压
```

#### 安装依赖库
```bash
# 基础依赖
pip install --upgrade pip

# AI服务商依赖（选择你需要的）
pip install --upgrade google-genai    # Gemini API
npm install -g @google/gemini-cli     # Gemini CLI（需要先安装Node.js）
pip install -U openai                 # OpenAI
pip install -U dashscope             # Qwen

# 其他依赖
pip install -r requirements.txt       # 如果有requirements.txt文件
```

### 3. API配置

#### 获取API密钥
- **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Gemini CLI**: 无需API密钥，使用Google账户OAuth认证
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/api-keys)
- **Qwen**: [阿里云通义千问](https://dashscope.console.aliyun.com/)

#### Gemini CLI配置（推荐）
1. **安装Node.js**（如果未安装）
   - 下载 [Node.js](https://nodejs.org/)
   - 安装时选择默认选项

2. **安装Gemini CLI**
   ```bash
   npm install -g @google/gemini-cli
   ```

3. **首次认证**
   ```bash
   gemini
   ```
   - 会自动打开浏览器进行Google账户OAuth认证
   - 完成认证后即可使用，每天1000次免费调用

#### 设置环境变量
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"    # Gemini API密钥
$env:OPENAI_API_KEY="your_api_key_here"     # OpenAI API密钥
$env:DASHSCOPE_API_KEY="your_api_key_here"  # Qwen API密钥
# 注意：Gemini CLI无需设置环境变量

# Windows (CMD)
set GEMINI_API_KEY=your_api_key_here
set OPENAI_API_KEY=your_api_key_here
set DASHSCOPE_API_KEY=your_api_key_here

# 永久设置（推荐）
# 在系统环境变量中添加
```

### 4. 验证配置
```bash
python scripts/main.py
```

## 🔍 安装验证

### ✅ 成功标志
- 程序正常启动
- 显示版本信息
- 可以选择语言界面
- 可以选择API供应商

### ❌ 常见问题

#### 问题1: "python不是内部或外部命令"
**解决方案**: 
- 检查Python是否正确安装
- 检查PATH环境变量
- 重启命令行窗口

#### 问题2: "No module named 'xxx'"
**解决方案**:
```bash
pip install 缺失的模块名
```

#### 问题3: "API密钥无效"
**解决方案**:
- 检查环境变量设置
- 验证API密钥是否正确
- 检查网络连接

#### 问题4: "Gemini CLI未找到"
**解决方案**:
- 确保已安装Node.js：`node --version`
- 重新安装Gemini CLI：`npm install -g @google/gemini-cli`
- 检查PATH环境变量是否包含npm全局安装路径

#### 问题5: "权限不足"
**解决方案**:
- 以管理员身份运行命令行
- 检查文件夹权限设置

## 🎮 首次使用

### 1. 准备Mod文件
将Mod文件夹放入 `source_mod` 目录

### 2. 运行程序
```bash
python scripts/main.py
```

### 3. 按提示操作
- 选择界面语言
- 选择API供应商
- 选择游戏类型
- 选择源语言和目标语言
- 确认开始翻译

## 📚 相关文档

- 🚀 [快速开始指南](docs/user-guides/quick-start-zh.md)
- 🎓 [小白专用指南](docs/user-guides/beginner-guide-zh.md)
- 🔧 [配置说明](docs/setup/configuration.md)
- ❓ [常见问题](docs/examples/troubleshooting.md)

---

> 💡 **提示**: 如果遇到问题，请查看 [常见问题](docs/examples/troubleshooting.md) 或提交Issue
