# 📋 Detailed Installation Steps

> Complete project installation and configuration guide for all users

## 🎯 Installation Method Selection

### 🚀 Method 1: One-Click Installation (Recommended for Beginners)
- **Advantages**: High automation, low error rate
- **Suitable for**: Users unfamiliar with command line operations
- **File**: `Initial Setup.bat`

### 🔧 Method 2: Manual Installation (Recommended for Experienced Users)
- **Advantages**: High controllability, easy debugging
- **Suitable for**: Users familiar with Python environment
- **Steps**: See detailed instructions below

## 🚀 One-Click Installation Steps

### 1. Download Project
```bash
# Method 1: Use Git to clone
git clone https://github.com/your-repo/V3_Mod_Localization_Factory.git

# Method 2: Direct download ZIP package
# Download from GitHub and extract to local
```

### 2. Run Configuration Script
1. Enter project directory
2. Double-click `Initial Setup.bat`
3. Follow prompts to select AI service provider
4. Enter corresponding API key
5. Wait for automatic installation to complete

### 3. Verify Installation
**Recommended way**: Double-click `run.bat`
- Automatically detects environment configuration
- Shows concise status information
- Automatically activates virtual environment (if available)

**Manual way**:
```bash
python scripts/main.py
```
If you see the version information interface, the installation is successful!

## 🔧 Manual Installation Steps

### 1. Environment Preparation

#### Install Python
- Download [Python 3.8+](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation
- Verify installation: `python --version`

#### Install Git (Optional)
- Download [Git](https://git-scm.com/downloads)
- Choose default options during installation

### 2. Project Setup

#### Clone/Download Project
```bash
# Use Git
git clone https://github.com/your-repo/V3_Mod_Localization_Factory.git
cd V3_Mod_Localization_Factory

# Or download ZIP package and extract
```

#### Install Dependencies
```bash
# Basic dependencies
pip install --upgrade pip

# AI service provider dependencies (choose what you need)
pip install --upgrade google-genai    # Gemini API
npm install -g @google/gemini-cli     # Gemini CLI (requires Node.js to be installed first)
pip install -U openai                 # OpenAI
pip install -U dashscope             # Qwen

# Other dependencies
pip install -r requirements.txt       # If requirements.txt exists
```

### 3. API Configuration

#### Get API Keys
- **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Gemini CLI**: No API key required, uses Google account OAuth authentication
- **OpenAI**: [OpenAI Platform](https://platform.openai.com/api-keys)
- **Qwen**: [Alibaba Cloud Tongyi Qianwen](https://dashscope.console.aliyun.com/)

#### Gemini CLI Configuration (Recommended)
1. **Install Node.js** (if not already installed)
   - Download [Node.js](https://nodejs.org/)
   - Choose default options during installation

2. **Install Gemini CLI**
   ```bash
   npm install -g @google/gemini-cli
   ```

3. **Initial Authentication**
   ```bash
   gemini
   ```
   - Will automatically open browser for Google account OAuth authentication
   - After authentication, you can use it with 1000 free calls daily

#### Set Environment Variables
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"    # Gemini API key
$env:OPENAI_API_KEY="your_api_key_here"     # OpenAI API key
$env:DASHSCOPE_API_KEY="your_api_key_here"  # Qwen API key
# Note: Gemini CLI does not require environment variables

# Windows (CMD)
set GEMINI_API_KEY=your_api_key_here
set OPENAI_API_KEY=your_api_key_here
set DASHSCOPE_API_KEY=your_api_key_here

# Permanent setting (recommended)
# Add in System Environment Variables
```

### 4. Verify Configuration
```bash
python scripts/main.py
```

## 🔍 Installation Verification

### ✅ Success Indicators
- Program starts normally
- Version information displayed
- Can select language interface
- Can select API provider

### ❌ Common Issues

#### Issue 1: "python is not recognized as an internal or external command"
**Solution**: 
- Check if Python is correctly installed
- Check PATH environment variable
- Restart command line window

#### Issue 2: "No module named 'xxx'"
**Solution**:
```bash
pip install missing_module_name
```

#### Issue 3: "Invalid API key"
**Solution**:
- Check environment variable settings
- Verify API key is correct
- Check network connection

#### Issue 4: "Gemini CLI not found"
**Solution**:
- Ensure Node.js is installed: `node --version`
- Reinstall Gemini CLI: `npm install -g @google/gemini-cli`
- Check if PATH environment variable includes npm global installation path

#### Issue 5: "Insufficient permissions"
**Solution**:
- Run command line as administrator
- Check folder permission settings

## 🎮 First Use

### 1. Prepare Mod Files
Place mod folder into `source_mod` directory

### 2. Run Program
```bash
python scripts/main.py
```

### 3. Follow Prompts
- Select interface language
- Select API provider
- Select game type
- Select source and target languages
- Confirm to start translation

## 📚 Related Documentation

- 🚀 [Quick Start Guide](docs/user-guides/quick-start-en.md)
- 🎓 [Beginner's Guide](docs/user-guides/beginner-guide-en.md)
- 🔧 [Configuration Guide](docs/setup/configuration.md)
- ❓ [Common Issues](docs/examples/troubleshooting.md)

---

> 💡 **Tip**: If you encounter problems, please check [Common Issues](docs/examples/troubleshooting.md) or submit an Issue
