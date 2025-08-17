# ⚙️ 配置说明

> 详细配置选项和参数说明

## 🎯 配置文件概览

项目的主要配置文件位于 `scripts/config.py`，包含以下配置类别：

- **游戏档案配置** - 不同P社游戏的文件结构和语言支持
- **API配置** - AI翻译服务的设置
- **系统参数** - 性能优化和功能开关
- **常量定义** - 项目级别的固定值

## 🎮 游戏档案配置

### 维多利亚3 (Victoria 3)
```python
"victoria3": {
    "name": "Victoria 3",
    "localization_dir": "localization",
    "metadata_file": ".metadata/metadata.json",
    "supported_languages": [
        {"code": "en", "name": "English"},
        {"code": "zh-CN", "name": "简体中文"},
        {"code": "ja", "name": "日本語"},
        # ... 其他语言
    ],
    "file_patterns": ["*.yml"],
    "asset_files": ["thumbnail.png", "descriptor.mod"]
}
```

### 群星 (Stellaris)
```python
"stellaris": {
    "name": "Stellaris",
    "localization_dir": "localisation",
    "metadata_file": "descriptor.mod",
    "supported_languages": [
        {"code": "en", "name": "English"},
        {"code": "zh-CN", "name": "简体中文"},
        # ... 其他语言
    ],
    "file_patterns": ["*.yml"],
    "asset_files": ["thumbnail.png", "descriptor.mod"]
}
```

### 自定义游戏档案
```python
"custom_game": {
    "name": "自定义游戏",
    "localization_dir": "your_localization_path",
    "metadata_file": "your_metadata_file",
    "supported_languages": [
        {"code": "en", "name": "English"},
        {"code": "zh-CN", "name": "简体中文"}
    ],
    "file_patterns": ["*.yml", "*.txt"],
    "asset_files": ["thumbnail.png", "descriptor.mod"]
}
```

## 🔑 API配置

### 环境变量设置
```bash
# Gemini API
export GEMINI_API_KEY="your_gemini_api_key"

# OpenAI API
export OPENAI_API_KEY="your_openai_api_key"

# Qwen API
export DASHSCOPE_API_KEY="your_qwen_api_key"
```

### API配置参数
```python
API_PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "handler": "gemini_handler",
        "model": "gemini-2.5-flash",
        "api_key_env": "GEMINI_API_KEY"
    },
    "openai": {
        "name": "OpenAI GPT",
        "handler": "openai_handler",
        "model": "gpt-5-mini",
        "api_key_env": "OPENAI_API_KEY"
    },
    "qwen": {
        "name": "阿里云通义千问",
        "handler": "qwen_handler",
        "model": "qwen-plus",
        "api_key_env": "DASHSCOPE_API_KEY",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "region": "beijing"
    }
}
```

## ⚡ 系统参数配置

### 性能优化参数
```python
# 并行处理配置
RECOMMENDED_MAX_WORKERS = min(32, cpu_count * 2)  # 智能线程池大小
CHUNK_SIZE = 40  # 批处理大小

# 超时设置
API_TIMEOUT = 30  # API调用超时时间（秒）
RETRY_ATTEMPTS = 3  # 重试次数
RETRY_DELAY = 1  # 重试延迟（秒）
```

### 功能开关
```python
# 调试模式
DEBUG_MODE = False  # 启用详细日志
VERBOSE_OUTPUT = False  # 启用详细输出

# 功能开关
ENABLE_FUZZY_MATCHING = True  # 启用模糊匹配
ENABLE_PARALLEL_PROCESSING = True  # 启用并行处理
ENABLE_SOURCE_CLEANUP = True  # 启用源文件清理
```

## 📁 目录结构配置

### 输入输出目录
```python
# 源文件目录
SOURCE_DIR = "source_mod"

# 输出目录
OUTPUT_DIR = "my_translation"

# 词典目录
GLOSSARY_DIR = "data/glossary"

# 语言文件目录
LANG_DIR = "data/lang"
```

### 文件命名规则
```python
# 输出文件夹命名格式
OUTPUT_FOLDER_FORMAT = "{lang_code}-{mod_name}"

# 本地化文件命名格式
LOCALIZATION_FILE_FORMAT = "{mod_name}_l_{lang_code}.yml"

# 校对进度表命名
PROOFREADING_FILE_FORMAT = "proofreading_progress.csv"
```

## 🌍 国际化配置

### 语言设置
```python
# 默认语言
DEFAULT_LANGUAGE = "zh-CN"

# 支持的语言
SUPPORTED_LANGUAGES = ["zh-CN", "en-US"]

# 语言文件映射
LANGUAGE_FILES = {
    "zh-CN": "data/lang/zh_CN.json",
    "en-US": "data/lang/en_US.json"
}
```

### 界面文本配置
```python
# 界面文本键值对
UI_TEXTS = {
    "zh-CN": {
        "welcome": "欢迎使用P社Mod本地化工厂",
        "select_game": "请选择游戏类型"
    },
    "en-US": {
        "welcome": "Welcome to Paradox Mod Localization Factory",
        "select_game": "Please select game type"
    }
}
```

## 🔧 词典配置

### 词典加载配置
```python
# 主词典文件
MAIN_GLOSSARY_FILE = "glossary.json"

# 外挂词典目录
AUXILIARY_GLOSSARY_DIR = "auxiliary"

# 词典合并策略
GLOSSARY_MERGE_STRATEGY = "priority_based"  # 优先级合并
```

### 模糊匹配配置
```python
# 模糊匹配阈值
FUZZY_MATCH_THRESHOLD = 0.8

# 匹配模式
FUZZY_MATCH_MODES = {
    "strict": 0.9,      # 严格模式
    "normal": 0.8,      # 正常模式
    "loose": 0.7        # 宽松模式
}
```

## 📊 日志配置

### 日志级别
```python
# 日志级别设置
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 日志文件配置
LOG_FILE_FORMAT = "translation_{timestamp}.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
```

### 日志格式
```python
# 日志格式模板
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 时间格式
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
```

## 🚀 高级配置

### 自定义翻译提示词
```python
# 翻译提示词模板
TRANSLATION_PROMPT_TEMPLATE = """
请将以下游戏Mod文本从{source_lang}翻译为{target_lang}。

游戏类型: {game_type}
Mod名称: {mod_name}
Mod描述: {mod_description}

请保持游戏术语的一致性，使用以下词典：
{glossary_terms}

翻译要求：
1. 保持原文格式和结构
2. 使用游戏常用术语
3. 保持文化适应性
4. 确保可读性

待翻译文本：
{texts}
"""
```

### 自定义输出格式
```python
# 输出格式配置
OUTPUT_FORMATS = {
    "csv": {
        "enabled": True,
        "encoding": "utf-8",
        "delimiter": ",",
        "include_headers": True
    },
    "json": {
        "enabled": False,
        "indent": 2,
        "ensure_ascii": False
    }
}
```

## 🔍 配置验证

### 配置检查
```python
def validate_config():
    """验证配置文件的完整性"""
    required_keys = [
        "SOURCE_DIR",
        "OUTPUT_DIR",
        "API_PROVIDERS",
        "GAME_PROFILES"
    ]
    
    for key in required_keys:
        if not hasattr(config, key):
            raise ValueError(f"Missing required config: {key}")
```

### 环境检查
```python
def check_environment():
    """检查运行环境"""
    # 检查Python版本
    if sys.version_info < (3, 8):
        raise RuntimeError("Python 3.8+ required")
    
    # 检查必要目录
    required_dirs = [SOURCE_DIR, OUTPUT_DIR, GLOSSARY_DIR]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
```

## 📝 配置示例

### 完整配置示例
```python
# config.py 示例
import os
import multiprocessing

# 基础配置
PROJECT_NAME = "Paradox Mod Localization Factory"
VERSION = "1.0.2"
LAST_UPDATE_DATE = "2025-08-17"

# 目录配置
SOURCE_DIR = "source_mod"
OUTPUT_DIR = "my_translation"
GLOSSARY_DIR = "data/glossary"

# 性能配置
RECOMMENDED_MAX_WORKERS = min(32, multiprocessing.cpu_count() * 2)
CHUNK_SIZE = 40

# API配置
API_PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "handler": "gemini_handler",
        "model": "gemini-2.0-flash-exp"
    }
}

# 游戏档案
GAME_PROFILES = {
    "victoria3": {
        "name": "Victoria 3",
        "localization_dir": "localization",
        "metadata_file": ".metadata/metadata.json"
    }
}
```

## 🔧 配置修改建议

### 性能调优
- 根据CPU核心数调整 `RECOMMENDED_MAX_WORKERS`
- 根据API限制调整 `CHUNK_SIZE`
- 根据网络情况调整超时时间

### 功能定制
- 添加新的游戏档案支持
- 自定义翻译提示词
- 配置特定的输出格式

---

> 📚 **相关文档**: 
> - [快速开始指南](docs/user-guides/quick-start-zh.md)
> - [详细安装步骤](docs/setup/installation-zh.md)
> - [项目架构](docs/developer/architecture.md)
