> **For English Speakers:** This project is a Python-based, AI-powered automation workflow for localizing Paradox Interactive game mods. It supports multi-language translation, robustly handles various PDS file formats, and is designed to be extensible.
>
> **[Click here to read the English README](README_EN.md)**

***

# P社Mod本地化工厂 (Paradox Mod Localization Factory)

> 告别复制粘贴，拥抱自动化。本项目旨在为P社游戏（如维多利亚3、群星等）的Mod提供一套高效、可靠的半自动本地化解决方案。

## 1. 项目简介

本项目是一套基于Python和Google Gemini API的模块化自动翻译工作流。它的核心目标是将Mod本地化的“首次翻译”阶段（从0到1）完全自动化，将原本需要耗费大量人力的重复性劳动，压缩为几分钟的机器处理时间，让本地化贡献者可以专注于“从1到100”的校对、润色和质量提升工作。

## 2. 核心功能

#### **自动化翻译核心**
* **Gemini API 驱动**: 利用强大的大型语言模型，提供高质量的翻译初稿。
* **稳健的解析器**: 内置专为应对P社“花式”`.yml`格式（如 `key:0 "value"`）而设计的解析器，确保所有有效文本都能被准确提取。
* **智能分批处理 (Chunking)**: 面对包含数百上千条文本的大型文件，脚本会自动将其分批次处理，以保证API调用的稳定性和成功率。
* **高保真重建**: 在重建文件时，能完美保留原始文件的缩进、注释和复杂的键名格式。

#### **多语言支持**
* **多语言互译**: 支持在维多利亚3官方支持的11种语言之间，选择任意一种作为源语言，翻译为另一种目标语言。
* **“一键多语”模式**: 支持将一个源语言版本，一键批量翻译为其余所有10种支持的语言，自动创建对应的文件夹和文件。
* **动态文件生成**: 能够根据选择的目标语言，自动生成符合游戏规范的文件名（如 `..._l_french.yml`）和文件头（如 `l_french:`）。
* **动态文件夹命名**: 在单一语言模式下，输出文件夹会根据目标语言命名（如 `FR-Mod名`, `汉化-Mod名`）；在批量模式下，则会统一命名为 `Multilanguage-Mod名`。

#### **完整的Mod包处理**
* **深度文件扫描**: 自动递归遍历 `localization` 文件夹下的所有子目录，确保不遗漏任何`.yml`文件。
* **元数据汉化**: 自动处理 `.metadata/metadata.json` 文件，翻译其中的Mod名称和简介。
* **配套资源复制**: 自动将源mod的封面图 `thumbnail.png` 复制到本地化文件夹。

#### **国际化与工作流管理**
* **双语用户界面 (i18n)**: 脚本自身的命令行交互界面，支持中英双语切换。
* **安全回退机制**: 当API调用失败或返回结果异常时，会自动创建一份保留英文原文的备用文件，以保证Mod在游戏中的完整性，避免因缺少本地化条目而显示错误代码。
* **可选的源目录清理**: 在所有操作成功后，提供可选的清理功能，删除源mod文件夹中不再需要的游戏性文件，以节约磁盘空间。

## 3. 项目架构

为保证项目的可维护性和扩展性，我们采用了清晰的模块化架构：

```
scripts/
├── main.py                 # 【总启动器】唯一的程序入口
├── config.py               # 【全局配置】存放语言数据库、API设置等
│
├── core/                   # 【核心引擎】可复用的底层功能模块
│   ├── api_handler.py
│   ├── file_parser.py
│   ├── file_builder.py
│   ├── directory_handler.py
│   └── asset_handler.py
│
├── workflows/              # 【工作流】具体的业务流程
│   └── initial_translate.py
│
└── utils/                  # 【辅助工具】
    └── i18n.py
```

## 4. 使用方法

### 4.1. 环境准备
1.  **安装 Git**: 确保你的系统已安装 [Git](https://git-scm.com/downloads)。
2.  **安装 Python**: 确保你的系统已安装 Python 3.8 或更高版本。
3.  **安装依赖库**: 在终端中运行 `pip install --upgrade google-generativeai`。
4.  **设置API密钥**: 设置一个名为 `GEMINI_API_KEY` 的环境变量，并填入你的API密钥。

### 4.2. 项目设置
1.  **初始化仓库**: 在项目根目录打开终端，运行 `git init`。
2.  **添加Mod源文件**: 将你要处理的mod文件夹，完整地放入 `source_mod` 目录下。
3.  **创建版本快照**: 运行 `git add .` 和 `git commit -m "Initial commit"`。

### 4.3. 运行脚本
1.  在项目**根目录**打开终端。
2.  运行命令： `python scripts/main.py`
3.  根据终端提示，依次选择：**界面语言 -> 目标Mod -> 是否清理源文件 -> 源语言 -> 目标语言**。

### 4.4. 启用Mod
1.  在完成汉化后，你能在my_translation文件夹下找到输出。文件夹的名称会根据你选择的本地化方式有所变化。例如汉化-，FR-，Multilanguage-等。
2.  将该文件夹复制并粘贴到文档/Paradox Interactive/Victoria 3/mod文件夹下。（如果找不到该文件夹，则新建一个名为mod的文件夹）
3.  重新启动维多利亚3并打开启动器。打开你想要加载该汉化补丁的播放集。在播放集页面，点击右上角的添加更多mod。
4.  在“已安装的MOD”中找到刚刚被你添加的本地化mod，并将其添加到播放集。
5.  启用MOD并将本地化MOD置于原MOD的下方。选择正确的播放集，启动游戏。
6.  玩的开心！