> **For English Speakers:** This project is a Python-based, AI-powered automation workflow for localizing Paradox Interactive game mods. It supports multi-language translation, robustly handles various PDS file formats, and is designed to be extensible.
>
> **[Click here to read the English README](README_EN.md)**

***

# P社Mod本地化工厂 (Paradox Mod Localization Factory)

> 告别复制粘贴，拥抱自动化。本项目旨在为P社游戏（如维多利亚3、群星等）的Mod提供一套高效、可靠的半自动本地化解决方案。

## 📚 文档导航

### 🌍 选择语言 / Choose Language
- [📚 中文文档](docs/zh/README.md) - 查看所有中文文档
- [📚 English Documentation](docs/en/README.md) - View all English documentation

### 🚀 快速开始
- [快速开始指南](docs/zh/user-guides/quick-start-zh.md) - 5分钟上手
- [详细安装步骤](docs/zh/setup/installation-zh.md) - 完整安装流程

### 📖 用户指南
- [小白专用指南](docs/zh/user-guides/beginner-guide-zh.md) - 零基础用户必读
- [英文入门指南](docs/en/user-guides/beginner-guide-en.md) - English Beginner's Guide

### 🔧 词典系统
- [词典系统概览](docs/zh/glossary/overview.md) - 词典系统完整介绍
- [词典工具使用](docs/zh/glossary/tools-guide.md) - 如何使用parser.py和validator.py
- [系统机制说明](docs/zh/glossary/system-mechanism.md) - 技术实现详解
- [碧蓝档案词典](docs/zh/glossary/blue-archive-guide.md) - 特定主题词典使用

### 👨‍💻 开发者文档
- [项目架构](docs/zh/developer/architecture.md) - 系统设计说明
- [开发笔记](docs/zh/notes/) - 技术实现记录和架构说明

### ⚙️ 配置和故障排除
- [配置说明](docs/zh/setup/configuration.md) - 详细配置选项
- [常见问题](docs/zh/examples/troubleshooting.md) - 问题解决方案

---

### 许可协议 (License)

本项目采用**双许可证模式**：

1. **代码部分**（包括 `/scripts`, `/core`, `/workflows`, `/utils` 等目录，以及其他 Python 源代码文件）  
   采用 **[GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.html)**  
   - 你可以自由使用、修改和分发代码（包括商业用途），但必须：
     * 保留原始作者署名和许可证信息。
     * 修改后的版本必须同样以 **AGPL-3.0** 许可发布。
     * 如果将本项目代码部署为在线服务（SaaS），你也必须向用户公开全部源代码。
   - 详细条款请阅读 [AGPL-3.0 官方文本](https://www.gnu.org/licenses/agpl-3.0.html)。

2. **数据与文档部分**（包括 `/data/glossary/` 目录下的词典文件、README 文档及其他非代码内容）  
   采用 **[知识共享 署名-非商业性使用-相同方式共享 4.0 国际 (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)**  
   - 你可以自由分享和修改这些内容，但必须：
     * 保留原始作者署名和许可链接。
     * **不得将其用于商业目的**。
     * 基于这些内容的衍生作品必须采用相同的许可证分发。

## 1. 项目愿景：翻译，不该成为门槛
并不是每个人都精通八国语言。

即使你真的精通，也未必愿意在下班后打开游戏时还要开动脑筋逐句翻译Mod。

这个项目的初衷，是简化这个过程——让你：

**看到一个喜欢的Mod，只需动动鼠标，就能玩到母语版本。**

它不是为“完美翻译”而生，而是为了让翻译，不再成为阻碍创意传播的门槛。

我们希望：
* 玩家可以一键本地化工坊的优秀Mod，哪怕只是粗翻，也能顺利游玩；
* 多语言创作者可以快速构建初稿，再精修润色，不再困在重复劳动中；
* 本地社区可以更低门槛地参与全球Mod生态建设。

这是一个让创作自由流动的工具，一个服务于“表达、理解、再创造”的工程。

在人工智能和大语言模型的时代，语言不该也不会成为玩家社区之间的沟通障碍。

***

## 2. 核心功能

#### **自动化翻译核心**
* **多API支持**: 支持Gemini、OpenAI、Qwen等多种AI翻译服务，用户可根据需要选择。
* **智能词典系统**: 内置游戏专用词典管理器，自动识别并注入相关术语，确保游戏术语翻译的一致性和准确性。
* **稳健的解析器**: 内置专为应对P社“花式”`.yml`格式（如 `key:0 "value"`）而设计的解析器，确保所有有效文本都能被准确提取。
* **智能分批处理 (Chunking)**: 面对包含数百上千条文本的大型文件，脚本会自动将其分批次处理，以保证API调用的稳定性和成功率。
* **高保真重建**: 在重建文件时，能完美保留原始文件的缩进、注释和复杂的键名格式。

#### **多游戏/多语言支持**
* **多游戏档案**: 通过`config.py`中的游戏档案系统，可为不同P社游戏（目前已内置维多利亚3和群星的配置）定义不同的文件结构、Prompt模板和处理规则。
* **多语言互译**: 支持在官方支持的多种语言之间，选择任意一种作为源语言，翻译为另一种目标语言。
* **"一键多语"模式**: 支持将一个源语言版本，一键批量翻译为其余所有游戏官方支持的语言。不同游戏支持的语言数量不同：
  - 维多利亚3：11种官方语言
  - 群星：10种官方语言  
  - 钢铁雄心4：9种官方语言
  - 十字军之王3：8种官方语言
  - 欧陆风云4：4种官方语言

> **⚠️ 重要说明**: 由于欧陆风云4（EU4）的引擎限制，目前我们的项目**不支持对EU4的中文本地化**。EU4使用的是较老的Clausewitz引擎版本，其本地化系统与较新的P社游戏存在根本性差异，无法通过我们的工具正确处理中文字符编码和文件结构。虽然我们提供了EU4的词典支持，但实际的本地化功能暂不可用。
* **动态文件生成**: 能够根据选择的目标语言和游戏，自动生成符合规范的文件名（如 `..._l_french.yml`）、文件头（如 `l_french:`）和文件夹名（如 `fr-Mod名`）。
* **自定义目标语言支持**: 在目标语言选择列表末尾提供"[c] 自定义目标语言..."选项，支持用户创建非官方语言或"套壳"语言包：
  - **目标语言名称**: 用于向AI下达翻译指令（如：Italian）
  - **P社内部语言密钥**: 用于生成.yml文件的文件头（如：l_italian 或 l_english用于"套壳"）
  - **输出文件夹前缀**: 用于生成本地化包的顶层文件夹名（如：IT-）
  - **兼容"套壳"模式**: 支持将翻译内容伪装成英文文件，解决某些社区将Mod翻译成母语但伪装成英文文件的问题

#### **完整的Mod包处理**
* **深度文件扫描**: 自动递归遍历本地化文件夹下的所有子目录，确保不遗漏任何`.yml`文件。
* **智能元数据处理**: 能够根据游戏档案，自动处理并翻译维多利亚3的`.metadata/metadata.json`文件和群星的`descriptor.mod`文件（并生成两份）。
* **配套资源复制**: 自动将游戏档案中定义的关键资产（如 `thumbnail.png`, `descriptor.mod`）复制到本地化文件夹。
* **上下文感知翻译**: 在翻译元数据时，会读取Mod名称并允许用户输入额外的主题信息，将这些上下文注入到Prompt中，以提升AI翻译的准确性。

#### **国际化与工作流管理**
* **双语用户界面 (i18n)**: 脚本自身的命令行交互界面，支持中英双语切换。
* **智能校对进度追踪**: 自动生成CSV格式的校对进度表，支持中英文界面，帮助汉化者追踪和管理校对工作。
* **后处理格式验证**: 翻译完成后自动运行格式验证，检测语法错误、格式问题和标签配对，生成详细的验证报告。
* **安全回退机制**: 当API调用失败时，会自动创建一份保留原文的备用文件，以保证Mod在游戏中的完整性。
* **可选的源目录清理**: 在所有操作成功后，提供可选的清理功能，并根据游戏档案精确地保留必要文件。

***

## 3. 项目架构

为保证项目的可维护性和扩展性，我们采用了清晰的模块化架构：

```
scripts/
├── main.py                           # 【总启动器】唯一的程序入口
├── config.py                         # 【全局配置】存放语言数据库、API设置等
├── emergency_fix_chinese_punctuation.py # 【紧急修复】中文标点符号修复脚本
│
├── core/                             # 【核心引擎】可复用的底层功能模块
│   ├── api_handler.py                # 【API处理器工厂】统一管理不同AI服务接口
│   ├── openai_handler.py             # 【OpenAI处理器】OpenAI API翻译接口
│   ├── gemini_handler.py             # 【Gemini处理器】Google Gemini API翻译接口
│   ├── qwen_handler.py               # 【Qwen处理器】阿里云通义千问API翻译接口
│   ├── glossary_manager.py           # 【词典管理器】游戏专用术语词典加载与管理
│   ├── file_parser.py                # 【文件解析器】解析P社特有的.yml格式
│   ├── file_builder.py               # 【文件构建器】重建本地化文件
│   ├── directory_handler.py          # 【目录处理器】处理文件夹结构
│   ├── asset_handler.py              # 【资源处理器】处理元数据和资源文件
│   ├── proofreading_tracker.py       # 【校对追踪器】生成校对进度表
│   ├── post_processing_manager.py    # 【后处理管理器】格式验证与报告生成 ✨
│   ├── parallel_processor.py         # 【并行处理器】多文件并发处理
│   ├── scripted_loc_parser.py        # 【脚本化解析器】脚本驱动的本地化解析（EU4）
│   ├── loc_parser.py                 # 【本地化解析器】基础本地化文件解析
│   └── llm/                          # 【LLM模块】大语言模型相关功能
│
├── workflows/                        # 【工作流】具体的业务流程
│   ├── initial_translate.py          # 【初始翻译】主要的翻译工作流程
│   ├── generate_workshop_desc.py     # 【工坊描述】生成创意工坊描述（待实现）
│   ├── publish_mod.py                # 【Mod发布】发布Mod到工坊（待实现）
│   ├── scrape_paratranz.py           # 【Paratranz爬取】从Paratranz获取数据（待实现）
│   └── update_translate.py           # 【更新翻译】更新现有翻译（待实现）
│
├── hooks/                            # 【钩子系统】扩展解析器功能
│   └── file_parser_hook.py          # 【文件解析钩子】自定义文件解析逻辑
│
└── utils/                            # 【辅助工具】通用功能模块
    ├── post_process_validator.py     # 【后处理验证器】游戏特定语法规则验证 ✨
    ├── punctuation_handler.py        # 【标点符号处理器】多语言标点符号转换
    ├── logger.py                     # 【日志工具】统一的日志记录系统
    ├── i18n.py                      # 【国际化】多语言界面支持
    ├── text_clean.py                # 【文本清理】文本预处理和清理
    └── report_generator.py          # 【报告生成器】生成各种报告（待实现）
```

***

## 4. 使用方法

> **注意**: 此快速使用指南主要是针对对Python和代码知识有一定了解的人群。如果你完全不知道什么是API如何配置环境变量，请参见这个[小白说明文档](小白说明文档.md)

### 4.1. 环境准备

#### 🚀 快速配置（推荐新手）
1. **安装 Python**: 确保你的系统已安装 Python 3.8 或更高版本。
2. **运行配置脚本**: 双击项目根目录的 `首次安装配置.bat` 文件。
3. **按照提示操作**: 选择AI服务，输入API密钥，脚本会自动安装依赖并配置环境变量。

#### 📋 手动配置（适合有经验的用户）
1. **安装 Git**: 确保你的系统已安装 [Git](https://git-scm.com/downloads)。
2. **安装 Python**: 确保你的系统已安装 Python 3.8 或更高版本。
3. **安装依赖库**: 
    - 如果使用Gemini：`pip install --upgrade google-genai`
    - 如果使用OpenAI：`pip install -U openai`
    - 如果使用Qwen：`pip install -U dashscope`
4. **设置API密钥**: 根据你使用的API服务商设置对应的环境变量：
    - Gemini: `GEMINI_API_KEY`
    - OpenAI: `OPENAI_API_KEY`
    - Qwen: `DASHSCOPE_API_KEY`

### 4.2. 项目设置
1.  **下载/克隆仓库**: 从GitHub下载本项目。
2.  **添加Mod源文件**: 将你要处理的mod文件夹，完整地放入 `source_mod` 目录下。
    - **建议**: 将mod文件夹从创意工坊的一串数字重命名为mod名，以避免混淆。
    - **注意**: 确保整个mod文件夹结构完整，包括所有必要的文件和子文件夹。
    假设需要被本地化的mod名称是"ABCDEF"，项目结构应该如下：
    ```
    V3_Mod_Localization_Factory/
    ├── source_mod/                    # <-- 源Mod文件夹
    │   └── ABCDEF/                    # <-- 这是你要本地化的Mod文件夹
    │       ├── descriptor.mod         # <-- Mod描述文件（群星）
    │       ├── thumbnail.png          # <-- Mod封面图
    │       ├── localization/          # <-- 本地化文件夹（群星）
    │       │   └── english/           # <-- 英文本地化文件
    │       │       └── ABCDEF_l_english.yml
    │       ├── .metadata/             # <-- 元数据文件夹（维多利亚3）
    │       │   └── metadata.json     # <-- 元数据文件
    │       ├── common/                # <-- Mod内容文件夹（与本地化无关）
    │       └── ... (其他Mod文件)
    ├── scripts/                       # <-- 脚本文件夹
    ├── data/                          # <-- 数据文件夹
    └── README.md                      # <-- 说明文档
    ```
    
     **重要提示**:
     - 将整个mod文件夹（如"ABCDEF"）放入`source_mod`目录下
     - 根据游戏类型，mod可能包含不同的文件结构（如群星的`localization`、维多利亚3的`.metadata`等）
     - `common`等mod内容文件夹与本地化无关，你可以在后续的脚本运行过程中清理这些文件。

3.  **配置词典文件**（可选）: 在 `data/glossary/` 目录下放置游戏专用词典文件：
    - Victoria 3: `data/glossary/victoria3/glossary.json`
    - Stellaris: `data/glossary/stellaris/glossary.json`
    - 词典文件包含游戏术语的对照表，可显著提升翻译质量

### 4.3. 运行脚本
1.  在项目**根目录**打开终端。
2.  Windows 用户：双击 `run.bat`运行项目。
3.  根据终端提示，依次选择：**界面语言 -> API供应商 -> 目标游戏 -> 目标Mod -> 是否清理源文件 -> 源语言 -> 目标语言 -> (可选)输入Mod主题**。

### 4.4. 故障排除

#### 常见问题
- **权限错误**：确保对项目目录有读写权限
- **Python版本**：需要 Python 3.8 或更高版本
- **依赖缺失**：根据你使用的API服务商运行对应的安装命令：
  - Gemini: `pip install --upgrade google-genai`
  - OpenAI: `pip install -U openai`
  - Qwen: `pip install -U dashscope`

### 4.5. 启用Mod（维多利亚3）
1.  在完成汉化后，你能在`my_translation`文件夹下找到输出。文件夹的名称会根据你选择的本地化方式有所变化。例如 `zh-CN-ABCDEFG`。
2.  该文件夹下还会包含一个校对进度表（CSV格式），用于追踪校对工作进度。
3.  将该文件夹复制并粘贴到 `文档/Paradox Interactive/Victoria 3/mod` 文件夹下。（如果找不到`mod`文件夹，则新建一个）
4.  正确的文件夹结构应该如下图所示：
    ```
    Victoria 3/
    └── mod/
        └── zh-CN-ABCDEFG/            # <-- 这是Mod的主文件夹
            ├── .metadata/            # <-- 这是V3的元数据文件夹
            │   └── metadata.json     # <-- 这是游戏内读取的元数据
            ├── thumbnail.png         # <-- 这是Mod的封面图
            ├── 校对进度表.csv        # <-- 校对进度追踪文件
            └── localization/         # <-- 这是本地化文件所在的文件夹 (注意拼写)
                └── simp_chinese/
                    └── ... (所有.yml汉化文件都在这里)
    ```                
5.  重新启动维多利亚3并打开启动器。在播放集中添加该Mod，并确保它位于原Mod的下方。
6.  玩的开心！

### 4.6. 启用Mod（群星&钢铁雄心）
1.  在完成汉化后，你能在`my_translation`文件夹下找到输出文件夹（例如 `zh-CN-ABCDEFG`）和一个同名的`.mod`文件（例如 `zh-CN-ABCDEFG.mod`）。
2.  该文件夹下还会包含一个校对进度表（CSV格式），用于追踪校对工作进度。
3.  将**输出文件夹**和对应的 **`.mod` 文件**，一同复制并粘贴到 `文档/Paradox Interactive/Stellaris/mod` 目录下。（如果找不到`mod`文件夹，则新建一个）
4.  正确的文件夹结构应该如下图所示：
    ```
    Stellaris/
    └── mod/
        ├── zh-CN-ABCDEFG/            # <-- 这是Mod的主文件夹
        │   ├── descriptor.mod        # <-- 这是游戏内读取的元数据
        │   ├── thumbnail.png         # <-- 这是Mod的封面图
        │   ├── 校对进度表.csv        # <-- 校对进度追踪文件
        │   └── localisation/         # <-- 这是本地化文件所在的文件夹
        │       └── simp_chinese/
        │           └── ... (所有.yml汉化文件都在这里)
        │
        └── zh-CN-ABCDEFG.mod         # <-- 这是启动器读取的.mod文件，用来指向上面那个文件夹
    ```
5.  重新启动群星并打开启动器。在播放集中添加该Mod，并确保它位于原Mod的下方。
6.  玩的开心！

***

## 5. 词典系统

### 5.1. 词典功能概述
词典系统是项目的核心功能之一，它能够：
- **自动识别术语**: 在翻译过程中自动扫描文本，识别出游戏相关的专业术语
- **智能提示注入**: 将相关术语作为高优先级指令注入到AI翻译请求中
- **确保一致性**: 保证同一术语在不同文件中的翻译完全一致
- **支持双向翻译**: 无论从哪种语言翻译到哪种语言，都能正确识别和应用术语

### 5.2. 词典文件结构
词典文件采用JSON格式，结构如下：
```json
{
  "metadata": {
    "description": "Victoria 3 游戏及Mod社区汉化词典",
    "last_updated": "2024-01-01",
    "sources": ["官方汉化", "社区汉化", "Mod汉化"]
  },
  "entries": [
    {
      "id": "victoria3_convoy",
      "translations": {
        "en": "convoy",
        "zh-CN": "船队"
      },
      "metadata": {
        "pos": "noun",
        "remarks": "由港口生产，维持国家船运线路的运转"
      },
    }
  ]
}
```

### 5.3. 词典文件位置
- **Victoria 3**: `data/glossary/victoria3/glossary.json`
- **Stellaris**: `data/glossary/stellaris/glossary.json`
- **其他游戏**: 可在 `data/glossary/` 下创建对应的游戏文件夹

### 5.4. 词典效果示例
**使用词典前**: AI可能将"convoy"翻译为"护航"、"护送"、"车队"等不同词汇
**使用词典后**: AI严格按照词典要求，统一翻译为"船队"，确保术语一致性

### 5.5. 词典来源说明与致谢

本项目的游戏专用词典，其数据来源于以下优秀的官方及社区汉化项目，我们在此向所有原贡献者致以最诚挚的感谢！

#### **Victoria 3 词典来源**
* **维多利亚3 汉化 更新V1.2**: 官方汉化更新版本，包含最新的游戏术语。
* **Morgenröte | 汉语**: 社区汉化项目。
* **Better Politics Mod 简体中文汉化**: 政治系统Mod的专用汉化词典。
* **牛奶汉化**: 社区汉化项目，提供丰富的游戏术语对照。

#### **Stellaris 词典来源**
* **鸽组汉化词典**: 著名的群星汉化组，提供高质量的科幻术语翻译。
* **Shrouded Regions汉化词典**: 专注于神秘区域和特殊事件的术语翻译。
* **L网群星mod汉化集词典**: 综合性的群星Mod汉化词典，涵盖多个Mod内容。

#### **其他游戏词典来源**
目前EU4、HOI4和CK3只包含基础的示例词典。这些词典主要用于验证词典系统的功能，并为后续社区贡献者扩充词典提供基础结构。

***

## 6. 合作与未来计划
本项目是一个在你的反馈和我的协助下共同成长的开源项目。我们已经为未来规划了许多激动人心的功能，并已在GitHub的Issues中立项。

我们欢迎任何形式的反馈、建议和代码贡献！