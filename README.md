# 维多利亚3 Mod 汉化自动化工厂

> 告别复制粘贴，拥抱自动化。我们的目标是为P社游戏Mod提供一套高效、可靠的半自动汉化解决方案。

## 1. 项目简介

本项目旨在提供一套标准化的工作流程，利用Python脚本和大型语言模型（LLM）的强大能力，实现对维多利亚3 Mod的快速、批量汉化。它能够处理复杂的本地化文件格式，自动翻译元数据，并为未来的增量更新打下坚实基础。

## 2. 当前功能与工作流 (V2.4+)

目前，项目核心脚本 `initial_translate.py` 已实现对一个全新Mod的**首次全量汉化**功能。

**其自动化流程包括：**
* **交互式Mod选择**: 自动扫描 `source_mod` 目录下的所有mod项目，并提供菜单供用户选择本次要处理的目标。
* **深度文件扫描**: 使用 `os.walk` 递归遍历 `localization/english` 目录及其所有子目录，确保不会遗漏任何 `.yml` 文件。
* **智能文本解析**: 内置了专为应对P社“花式”本地化格式（如 `key:0 "value"`）而设计的稳健解析器。
* **核心内容翻译**: 调用Gemini API对所有提取出的有效文本进行翻译，并通过“编号列表”模式确保翻译结果的稳定性和完整性。
* **元数据汉化**: 自动读取 `.metadata/metadata.json` 文件，翻译其中的 `name` 和 `short_description` 字段。
* **配套文件复制**: 自动将源mod的封面图 `thumbnail.png` 复制到汉化目录。
* **智能分批处理 (Chunking)**: 在处理包含数百条文本的超大型本地化文件时，为保证最高的翻译成功率和稳定性，脚本会自动将任务“化整为零”，分批次（如每150条为一批）提交给AI进行处理，有效避免了因单次请求内容过长可能导致的API错误。
* **（可选）源目录清理**: 在所有操作成功后，提供可选的清理功能，删除源mod文件夹中不再需要的大文件，以节约磁盘空间。

## 3. 目录结构

```
V3_Mod_Localization_Factory/
├── .git/
├── glossary/
│   └── glossary.json        # (未来功能) 用于存放自定义术语词典
├── my_translation/
│   └── 汉化-Mod名/          # 存放汉化成果
│       ├── .metadata/
│       ├── localization/
│       └── thumbnail.png
├── scripts/
│   ├── initial_translate.py # 当前核心脚本
│   └── update_translate.py  # (未来功能) 增量更新脚本
├── source_mod/
│   └── Mod名/               # 存放待汉化的mod源文件
└── README.md
```

## 4. 使用方法

### 4.1. 环境准备
1.  **安装 Git**: 确保你的系统已安装 [Git](https://git-scm.com/downloads)。
2.  **安装 Python**: 确保你的系统已安装 Python 3.8 或更高版本。
3.  **安装依赖库**: 在终端中运行以下命令，安装并升级Google AI的Python库。
    ```bash
    pip install --upgrade google-generativeai
    ```
4.  **设置API密钥**: 在你的操作系统中设置一个名为 `GEMINI_API_KEY` 的环境变量，并填入你的API密钥。

### 4.2. 项目设置
1.  **初始化仓库**: 在项目根目录（`V3_Mod_Localization_Factory`）打开终端，运行 `git init`。
2.  **添加Mod源文件**: 将你要汉化的mod文件夹完整地放入 `source_mod` 目录下。
3.  **创建版本快照**: 在终端中运行 `git add .` 和 `git commit -m "Initial commit: Add source files for [Mod名]"`，为源文件创建初始版本记录。

### 4.3. 执行首次汉化
1.  在项目根目录打开终端。
2.  运行命令：
    ```bash
    python scripts/initial_translate.py
    ```
3.  根据终端提示，输入你想要汉化的mod对应的数字序号，然后按回车。
4.  脚本将开始全自动执行所有汉化流程。

### 4.4. 校对与提交
1.  脚本执行完毕后，进入 `my_translation/` 目录下对应的汉化文件夹，检查并人工校对、润色所有生成的翻译文件。
2.  校对完成后，使用 `git add .` 和 `git commit -m "feat: Finish translation and proofreading for [Mod名]"` 提交你的劳动成果。

## 5. 未来计划

* **[进行中] 自定义词典功能**:
    * 通过 `glossary/glossary.json` 文件，允许用户定义专有名词的固定翻译，脚本在翻译时将强制AI遵守这些规则，以确保术语统一和精准。

* **[待开发] 增量更新脚本 (`update_translate.py`)**:
    * 当源mod更新后，此脚本将利用 `git diff` 对比新旧版本文件的差异。
    * 只提取**新增和被修改**的文本行发送给AI翻译，极大地提升更新效率。

## 6. 注意事项
* **Git提交**: 请养成频繁使用 `git commit` 的好习惯，它是你项目版本安全的基石。
* **文件编码**: 脚本已内置处理，所有输出的中文 `.yml` 文件均为游戏可识别的 `utf-8-sig` 编码。
* **API密钥**: 切勿将API密钥硬编码在脚本中或上传到公共仓库。使用环境变量是最佳实践。