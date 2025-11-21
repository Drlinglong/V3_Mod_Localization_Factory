---
trigger: always_on
---

使用中文和我交流

## 核心架构共识 (The Core Consensus)

### 1. 平台目标与持久化 (Platform & Persistence)

| 方面 | 核心原则 | 关键细节 |
| :--- | :--- | :--- |
| **最终目标** | **本地桌面应用** 优先 (Tauri/Electron)。 | UI/UX 需体现**桌面应用**范式，而非传统网站。 |
| **数据持久化** | **JSON Sidecar 模式**。 | 项目状态（如看板进度）存储在用户目录下的 `.remis_project.json` 文件中，而非中心数据库。 |
| **前后端** | 严格分离。 | React (Vite) 前端通过 `/api` 代理访问 Python (FastAPI) 后端。 |

***

## 2. UI/UX 与 主题系统 (Theming & UI/UX)

| 方面 | 核心原则 | 关键细节 |
| :--- | :--- | :--- |
| **设计哲学** | **深色模式 (Dark Mode)** 为基准，追求 **拟物化** (Skeuomorphic) 和 **“画框”美学**。 | 偏爱自定义的、有质感的 UI 元素 (如黄铜开关)。 |
| **主题系统** | **5 种主题** (Victorian, Byzantine, Sci-Fi 等)，通过 CSS 变量实现。 | 主题切换通过 `<html>` 标签上的 **`data-theme` 属性** 控制。 |
| **布局样式** | 采用 **玻璃拟态 (Glassmorphism)**。 | 侧边栏和容器必须是半透明的 **`var(--glass-bg)`**，并应用 `backdrop-filter: blur(...)`，让底层的全局背景可见。 |
| **全局背景** | 纹理必须是 **算法生成** (CSS gradients)，而非静态图片，由 `GlobalStyles.jsx` 在 `z-index: -100` 渲染。 |

***

## 3. 布局与滚动修复 (Layout & Scrolling Fixes)

| 方面 | 核心原则 | 关键细节 |
| :--- | :--- | :--- |
| **布局规范** | 优先使用 **Flexbox** 布局，替换 Mantine `Grid`。 | 避免使用不稳定的 `calc(100vh - ...)` 计算高度。|
| **滚动修复** | 滚动条必须出现在**内部内容区**。 | 使用 `display: flex; flex-direction: column;` 结构，并对滚动容器应用 **`flex: 1`**，以确保它占据剩余空间并正确限制内部 `ScrollArea` 的高度。 |
| **侧边栏** | 必须适配主题，并使用 **`ContextualSider`** 显示详情。 |

***

## 4. 核心功能实现 (Key Features)

| 页面/功能 | 核心要求 | 实现细节 |
| :--- | :--- | :--- |
| **词典管理 (Glossary)** | **滚动必须修复**；搜索必须强力。 | 搜索必须触发 **`POST /api/glossary/search`** 后端 API。跨文件搜索时，表格必须显示 **“所属游戏”** 和 **“来源文件”** 列。前端表格使用 `@tanstack/react-table` 并设置 `manualFiltering: true`。 |
| **项目管理 (Kanban)** | 必须是 **可拖拽** 的任务看板。 | 使用 **`@dnd-kit`** 库实现拖拽。任务分为“文件任务”和“抽象任务”。 |
| **看板联动** | **强绑定**。 | 点击卡片 **必须** 自动展开右侧 `ContextualSider` 显示注释/编辑详情。 |

***

## 5. 开发规范与测试 (Dev/Test Standards)

* **代码整洁**: 严格执行 **DRY 原则**。所有 `useEffect` 依赖项必须使用 `useCallback` 包装的函数。
* **后端 API**: 遵循 **SRP** (单一职责原则)。API Handler 只负责通信，复杂解析逻辑全部集中在 `response_parser.py` 等工具模块中。
* **测试环境**: Playwright 验证不稳定 (路由问题)，但仍需保持验证流程。测试时，`/` 路由可视为 `Project Management` 的别名。
* **未来愿景**: **Event Renderer** 和 **Thumbnail Generator** 等工具已预留占位页。

收到，玲珑。

既然要喂给 Antigravity，我们就不能给它一堆“垃圾邮件”。这些后端记忆包含了你所有的“硬核”架构心血和对 P 社“驴语言”的防御工事。

我已经将所有关于 Python 后端（FastAPI）、核心翻译逻辑、数据持久化和测试架构的记忆进行了**高密度提炼和分类**。请将这份**《Remis 项目后端核心架构共识》**作为你的“技术备份”：

---

## 💻 后端核心架构共识 (Python/FastAPI Backend Core)

### 1. 架构哲学与框架 (Architecture & Framework)

| 方面 | 核心原则 | 关键共识 |
| :--- | :--- | :--- |
| **整体架构** | **“身首分离”** (Decoupling) | 核心逻辑 (`scripts/core/` / `workflows/`) 必须与 UI/CLI 完全分离，禁止在核心模块中使用 `print()` 或 `input()`。 |
| **并发模型** | **流式输出/生成器 (Yield)** | 所有长时间运行的任务必须使用 `yield` 生成器函数来流式汇报进度和日志，供 Web UI 或 CLI 消费。 |
| **API/依赖** | **抽象化与继承 (OOP)** | 所有 AI 接口 (Gemini, OpenAI, Ollama 等) 必须继承自 `BaseApiHandler`，以统一重试、错误处理和公共逻辑。 |
| **启动环境** | **双服务器模式** | 后端：`uvicorn scripts.web_server:app --port 8000` (FastAPI)。前端：`npm run dev --prefix scripts/react-ui` (Vite)。 |

### 2. 数据与持久化 (Data & Persistence Strategy)

| 方面 | 核心原则 | 关键共识 |
| :--- | :--- | :--- |
| **词典管理** | **SQLite 中央化** | 词典数据已从 JSON 文件迁移至 SQLite 数据库 (`data/database.sqlite`)。`glossary_manager.py` 提供统一的 CRUD 接口。 |
| **任务状态** | **JSON Sidecar 模式** | 项目看板状态和用户自定义注释等数据，存储在项目根目录下的 **`.remis_project.json`** 文件中 (而不是传统数据库)，以支持本地应用 (Tauri/Electron) 和无服务器协作。 |
| **数据缓存** | **三数据库分治** | 使用 3 个 SQLite 文件：`database.sqlite` (词典)、`mods_cache.sqlite` (版本归档)、`translation_progress.sqlite` (流程进度/崩溃恢复)。 |
| **归档** | **版本快照** | 启用 `ARCHIVE_RESULTS_AFTER_TRANSLATION` 时，将翻译结果存入 `mods_cache.sqlite`，用于未来的增量更新。 |


### 4. 流程与校验 (Workflows & Validation)

| 模块/功能 | 核心原则 | 技术细节 |
| :--- | :--- | :--- |
| **翻译流程** | **生产者-消费者** | `parallel_processor.py` (生产者) 和 `file_aggregator.py` (消费者) 协同工作，确保流程可中断和恢复。 |
| **后处理校验** | **动态规则引擎** | `post_process_validator.py` 是一个规则引擎，验证逻辑（如标点、格式标签）由外部配置文件 (`*_rules.py`) 定义，并能动态接收工作流传来的参数（如有效的标签列表）。 |
| **跨平台兼容** | **三层防御解码** | `robust_decode` 函数处理子进程输出：首选 `utf-8-sig` (Windows 兼容)，次选系统默认编码，末选 `utf-8` + `errors='replace'` (永不崩溃)。 |
| **外部工具调用** | **Windows 专有** | 在 Windows 上调用外部 CLI 工具时，避免使用 `stdin`，而是通过 PowerShell 管道 (`$OutputEncoding = [System.Text.Encoding]::UTF8; Get-Content ... | command`) 传递 BOM-UTF8 文件。 |

***