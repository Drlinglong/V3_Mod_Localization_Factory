# 维多利亚3 Mod 汉化自动化工厂

> 告别复制粘贴，拥抱自动化。

## 1. 项目简介

本项目旨在提供一套标准化的半自动工作流，用于管理和加速多个维多利亚3 Mod的本地化（汉化）工作。通过结合版本控制工具(Git)和大型语言模型(LLM)，本工作流能够将繁琐的、重复性的文本处理工作自动化，让译者能更专注于翻译的质量与润色。

## 2. 工作流核心

本工厂包含两大核心工作流程：

* **首次汉化**: 针对一个全新的、未曾汉化过的Mod，从零开始批量生成完整的汉化文件初稿。
* **增量更新**: 当已汉化的Mod发布新版本后，能够自动比对文件差异，仅针对新增和修改的内容进行翻译，实现快速更新。

## 3. 目录结构

为了支持对多个Mod的管理，本项目采用以下标准目录结构：

```
V3_Mod_Localization_Factory/
├── .git/
├── source_mod/
│   ├── Another_Cool_Mod/      # 存放Mod A的源英文文件
│   │   └── localisation/
│   │       └── english/
│   └── Yet_Another_Mod/         # 存放Mod B的源英文文件
│       └── localisation/
│           └── english/
├── my_translation/
│   ├── Another_Cool_Mod/      # 存放Mod A的中文汉化文件
│   │   └── localisation/
│   │       └── simp_chinese/
│   └── Yet_Another_Mod/         # 存放Mod B的中文汉化文件
│       └── localisation/
│           └── simp_chinese/
├── scripts/
│   ├── initial_translate.py
│   └── update_translate.py
└── README.md
```

**关键点**:
* 每个需要处理的Mod，在 `source_mod/` 和 `my_translation/` 目录下都拥有一个同名的独立子文件夹。

## 4. 使用方法

### 4.1. 准备工作：添加新Mod

1.  在 `source_mod/` 目录下，创建一个以Mod命名的**新文件夹**（例如 `source_mod/My_New_Mod/`）。
2.  将该Mod的**完整英文本地化文件**（通常是 `localisation/english` 目录）复制到这个新文件夹内。
3.  **（重要！）** 使用Git提交这次添加操作：`git add .` 后 `git commit -m "feat: Add source files for My_New_Mod"`。这为将来的“增量更新”奠定了基础。

### 4.2. 首次汉化

1.  在终端中运行命令：`python scripts/initial_translate.py`
2.  脚本启动后，会自动扫描 `source_mod/` 目录下的所有Mod，并**列出供你选择**。
3.  输入对应Mod的**序号**并按回车。
4.  脚本将开始执行全量翻译，并在 `my_translation/` 目录下生成对应的汉化文件。
5.  完成后，对生成的文件进行人工校对和润色。
6.  **（重要！）** 提交你校对好的汉化文件到Git。

### 4.3. 更新汉化

1.  将新版本的Mod英文文件**覆盖**到 `source_mod/` 下对应的Mod文件夹中。
2.  在终端中运行命令：`python scripts/update_translate.py`
3.  同样，脚本会**列出所有Mod供你选择**。选择你刚刚更新了源文件的那个Mod。
4.  脚本将利用Git自动比对差异，仅翻译变化的部分，并更新到 `my_translation/` 中对应的文件。
5.  对本次更新的少量文本进行校对后，提交到Git。

## 5. 注意事项

* **Git! Git! Git!**: 请频繁使用 `git commit` 保存你的进度。无论是添加了新Mod，还是完成了一轮校对，一个清晰的提交记录是你的“后悔药”和项目管理的核心。
* **API 密钥**: 请将你的API密钥配置为环境变量或保存在独立的 `.env` 文件中，**切勿**将其硬编码在脚本里。
* **文件编码**: 脚本应确保所有输出的中文本地化文件均为 `UTF-8 with BOM` 编码。

---
*文档版本 V1.1 - 已更新为支持多Mod的交互式工作流*