P社Mod本地化工厂 (Paradox Mod Localization Factory)

<p align="center">
<!-- 建议在这里放一个150x150像素的Logo图片 -->
<img src="https://placehold.co/150x150/7e57c2/FFFFFF?text=P.M.L.F." alt="项目Logo"/>
</p>

<p align="center">
<strong>告别复制粘贴，拥抱AI自动化。为P社游戏MOD提供的一站式、智能本地化解决方案。</strong>
</p>

<p align="center">
<a href="https://github.com/Drlinglong/V3_Mod_Localization_Factory/issues">
<img src="https://img.shields.io/github/issues/Drlinglong/V3_Mod_Localization_Factory" alt="GitHub issues">
</a>
<a href="https://github.com/Drlinglong/V3_Mod_Localization_Factory/blob/main/LICENSE">
<img src="https://img.shields.io/github/license/Drlinglong/V3_Mod_Localization_Factory" alt="项目许可证">
</a>
<a href="https://github.com/Drlinglong/V3_Mod_Localization_Factory/releases">
<img src="https://img.shields.io/github/v/release/Drlinglong/V3_Mod_Localization_Factory" alt="最新版本">
</a>
</p>

    [!IMPORTANT]
    For English Speakers: A brief English introduction and a link to the full English documentation can be found at the bottom of this file. Jump to English Section

📖 项目简介：翻译，不该成为门槛

你是否曾因为语言障碍，而错过无数优秀的MOD？或者作为MOD作者，因为繁琐的本地化工作而头疼？

P社Mod本地化工厂旨在彻底改变这一现状。它利用强大的AI翻译引擎，为你提供一套高效、智能、开箱即用的自动化本地化工作流。

我们的目标是：让你看到一个喜欢的MOD，只需动动鼠标，就能玩到母语版本。

<!--
建议在此处嵌入一个GIF动图，展示CLI的核心工作流程。
<p align="center">
<img src="[你的GIF动图链接]" alt="核心工作流演示">
</p>
-->

👤 这是为谁准备的？

    🎮 对于P社玩家...

        你是否厌倦了等待汉化组的更新，或者想尝试那些只有英文的小众精品MOD？这个工具让你成为自己的汉化组，一键翻译，立刻开玩。

    🛠️ 对于MOD作者...

        想让你的作品走向世界，但被多语言本地化的工作量劝退？用本工具快速生成所有目标语言的初稿，将你的时间投入到最重要的创意和打磨上。

    👨‍💻 对于开发者...

        这是一个完全开源、模块化、采用现代AI工程思想构建的项目。欢迎你来学习、贡献，或者把它作为你下一个项目的灵感来源。

✨ 核心亮点

    🧠 智能翻译核心: 无缝集成Gemini、OpenAI等多种AI服务，并配备独创的、以“概念”为核心的结构化词典系统，智能处理简称、变体，保证术语统一。

    ⚙️ 全自动工作流: 从解析P社特有的.yml文件，到处理元数据和封面图，再到最终打包，全程自动化。

    🌐 强大的多语言支持: 支持游戏官方所有语言间的互译，并允许用户自定义目标语言，实现“一键多语”发布。

    🛡️ 健壮可靠: 内置并行处理引擎加速，拥有“双保险”的QA校验机制和断点续传功能（规划中），确保稳定可靠。

    💻 现代Web UI: (规划中) 提供基于Gradio的图形化界面，让非技术用户也能轻松上手。

🏗️ 项目架构：为何如此强大？

为保证项目的可维护性和扩展性，我们采用了清晰的模块化架构。这不仅仅是一个脚本，这是一个经过深思熟虑的工程项目。

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

🚀 快速开始

    [!NOTE]
    当前版本提供功能最全的命令行界面 (CLI)。一个更易于使用的在线Demo和Web UI版本正在规划中。

➡️ 查看本地部署完整指南

📚 了解更多 (文档导航)

想深入了解项目的每一个细节？我们为你准备了完整的文档。

    用户指南: 从零开始，一步步教你如何使用本工具。

    词典系统详解: 深入了解我们强大的词典系统是如何工作的。

    开发者文档: 查看项目架构、设计哲学和贡献指南。

    常见问题解答 (FAQ): 在这里找到常见问题的解决方案。

🤝 贡献与鸣谢

本项目是一个在你的反馈和我的协助下共同成长的开源项目。我们欢迎任何形式的反馈、建议和代码贡献！

特别鸣谢:

    本项目的游戏专用词典，其数据来源于以下优秀的官方及社区汉化项目，我们在此向所有原贡献者致以最诚挚的感谢！
Victoria 3 词典来源

    维多利亚3 汉化 更新V1.2: 官方汉化更新版本，包含最新的游戏术语。
    Morgenröte | 汉语: 社区汉化项目。
    Better Politics Mod 简体中文汉化: 政治系统Mod的专用汉化词典。
    牛奶汉化: 社区汉化项目，提供丰富的游戏术语对照。

Stellaris 词典来源

    鸽组汉化词典: 著名的群星汉化组，提供高质量的科幻术语翻译。
    Shrouded Regions汉化词典: 专注于神秘区域和特殊事件的术语翻译。
    L网群星mod汉化集词典: 综合性的群星Mod汉化词典，涵盖多个Mod内容。


📜 许可协议 (License)

本项目采用双许可证模式：

    源代码部分采用 AGPL-3.0 许可。

    数据与文档部分采用 CC BY-NC-SA 4.0 许可。

详细信息请查阅我们的许可声明。（建议你创建一个这样的文件来存放长篇的许可说明）

<br>

English Version

This project is a Python-based, AI-powered automation workflow for localizing Paradox Interactive game mods.

➡️ Click here to read the full English README and Documentation