> **For English Speakers:** This project is a Python-based, AI-powered automation workflow for localizing Paradox Interactive game mods. It supports multi-language translation, robustly handles various PDS file formats, and is designed to be extensible.
>
> **[Click here to read the English README](README_EN.md)**

***

# P社Mod本地化工厂 (Paradox Mod Localization Factory)

> 告别复制粘贴，拥抱自动化。本项目旨在为P社游戏（如维多利亚3、群星等）的Mod提供一套高效、可靠的半自动本地化解决方案。

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
* **Gemini API 驱动**: 利用强大的大型语言模型，提供高质量的翻译初稿。
* **稳健的解析器**: 内置专为应对P社“花式”`.yml`格式（如 `key:0 "value"`）而设计的解析器，确保所有有效文本都能被准确提取。
* **智能分批处理 (Chunking)**: 面对包含数百上千条文本的大型文件，脚本会自动将其分批次处理，以保证API调用的稳定性和成功率。
* **高保真重建**: 在重建文件时，能完美保留原始文件的缩进、注释和复杂的键名格式。

#### **多游戏/多语言支持**
* **多游戏档案**: 通过`config.py`中的游戏档案系统，可为不同P社游戏（目前已内置维多利亚3和群星的配置）定义不同的文件结构、Prompt模板和处理规则。
* **多语言互译**: 支持在官方支持的11种语言之间，选择任意一种作为源语言，翻译为另一种目标语言。
* **“一键多语”模式**: 支持将一个源语言版本，一键批量翻译为其余所有10种支持的语言。
* **动态文件生成**: 能够根据选择的目标语言和游戏，自动生成符合规范的文件名（如 `..._l_french.yml`）、文件头（如 `l_french:`）和文件夹名（如 `fr-Mod名`）。

#### **完整的Mod包处理**
* **深度文件扫描**: 自动递归遍历本地化文件夹下的所有子目录，确保不遗漏任何`.yml`文件。
* **智能元数据处理**: 能够根据游戏档案，自动处理并翻译维多利亚3的`.metadata/metadata.json`文件和群星的`descriptor.mod`文件（并生成两份）。
* **配套资源复制**: 自动将游戏档案中定义的关键资产（如 `thumbnail.png`, `descriptor.mod`）复制到本地化文件夹。
* **上下文感知翻译**: 在翻译元数据时，会读取Mod名称并允许用户输入额外的主题信息，将这些上下文注入到Prompt中，以提升AI翻译的准确性。

#### **国际化与工作流管理**
* **双语用户界面 (i18n)**: 脚本自身的命令行交互界面，支持中英双语切换。
* **安全回退机制**: 当API调用失败时，会自动创建一份保留原文的备用文件，以保证Mod在游戏中的完整性。
* **可选的源目录清理**: 在所有操作成功后，提供可选的清理功能，并根据游戏档案精确地保留必要文件。

***

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

***

## 4. 使用方法

### 4.1. 环境准备
1.  **安装 Git**: 确保你的系统已安装 [Git](https://git-scm.com/downloads)。
2.  **安装 Python**: 确保你的系统已安装 Python 3.8 或更高版本。
3.  **安装依赖库**: 如果使用gemini则在终端中运行 `pip install --upgrade google-genai`。
                    如果使用Qwen或者chatgptapi则需要运行 `pip install -U openai`   
5.  **设置API密钥**: 设置一个名为 `GEMINI_API_KEY` 的环境变量，并填入你的API密钥。

### 4.2. 项目设置
1.  **下载/克隆仓库**: 从GitHub下载本项目。
2.  **添加Mod源文件**: 将你要处理的mod文件夹，完整地放入 `source_mod` 目录下。

### 4.3. 运行脚本
1.  在项目**根目录**打开终端。
2.  Windows 用户：双击 `run.bat`
    或者运行命令： `python scripts/main.py`
3.  根据终端提示，依次选择：**界面语言 -> 目标游戏 -> 目标Mod -> 是否清理源文件 -> 源语言 -> 目标语言 -> (可选)输入Mod主题**。

### 4.4. 故障排除

#### 常见错误：`sourcemod` 不存在
**错误原因：**
- 程序没有在项目根目录下运行
- `source_mod` 文件夹名称错误或不存在
- Windows 路径兼容性问题

**解决方案：**
1. **使用提供的启动脚本**（推荐）：
   - Windows 用户：双击 `run.bat`
   - 其他系统：运行 `python run.py`

2. **手动检查**：
   - 确保在包含 `source_mod` 文件夹的目录下运行程序
   - 检查文件夹名称是否为 `source_mod`（不是 `sourcemod` 或其他）
   - 确保 `source_mod` 文件夹存在且包含mod文件

3. **项目结构验证**：
   ```
   V3_Mod_Localization_Factory/
   ├── source_mod/          ← 必须存在
   ├── scripts/
   ├── run.py              ← 新的启动脚本
   ├── run.bat             ← Windows启动脚本
   └── README.md
   ```

#### 其他常见问题
- **权限错误**：确保对项目目录有读写权限
- **Python版本**：需要 Python 3.8 或更高版本
- **依赖缺失**：运行 `pip install --upgrade google-genai`

### 4.4. 启用Mod（维多利亚3）
1.  在完成汉化后，你能在`my_translation`文件夹下找到输出。文件夹的名称会根据你选择的本地化方式有所变化。例如 `zh-CN-ABCDEFG`。
2.  将该文件夹复制并粘贴到 `文档/Paradox Interactive/Victoria 3/mod` 文件夹下。（如果找不到`mod`文件夹，则新建一个）
3.  正确的文件夹结构应该如下图所示：
    ```
    Victoria 3/
    └── mod/
        └── zh-CN-ABCDEFG/            # <-- 这是Mod的主文件夹
            ├── .metadata/            # <-- 这是V3的元数据文件夹
            │   └── metadata.json     # <-- 这是游戏内读取的元数据
            ├── thumbnail.png         # <-- 这是Mod的封面图
            └── localization/         # <-- 这是本地化文件所在的文件夹 (注意拼写)
                └── simp_chinese/
                    └── ... (所有.yml汉化文件都在这里)
    ```                
4.  重新启动维多利亚3并打开启动器。在播放集中添加该Mod，并确保它位于原Mod的下方。
5.  玩的开心！

### 4.5. 启用Mod（群星）
1.  在完成汉化后，你能在`my_translation`文件夹下找到输出文件夹（例如 `zh-CN-ABCDEFG`）和一个同名的`.mod`文件（例如 `zh-CN-ABCDEFG.mod`）。
2.  将**输出文件夹**和对应的 **`.mod` 文件**，一同复制并粘贴到 `文档/Paradox Interactive/Stellaris/mod` 目录下。（如果找不到`mod`文件夹，则新建一个）
3.  正确的文件夹结构应该如下图所示：
    ```
    Stellaris/
    └── mod/
        ├── zh-CN-ABCDEFG/            # <-- 这是Mod的主文件夹
        │   ├── descriptor.mod        # <-- 这是游戏内读取的元数据
        │   ├── thumbnail.png         # <-- 这是Mod的封面图
        │   └── localisation/         # <-- 这是本地化文件所在的文件夹
        │       └── simp_chinese/
        │           └── ... (所有.yml汉化文件都在这里)
        │
        └── zh-CN-ABCDEFG.mod         # <-- 这是启动器读取的.mod文件，用来指向上面那个文件夹
    ```
4.  重新启动群星并打开启动器。在播放集中添加该Mod，并确保它位于原Mod的下方。
5.  玩的开心！

***

## 5. 合作与未来计划
本项目是一个在你的反馈和我的协助下共同成长的开源项目。我们已经为未来规划了许多激动人心的功能（如自定义词典、增量更新、一键发布到工坊等），并已在GitHub的Issues中立项。

我们欢迎任何形式的反馈、建议和代码贡献！
