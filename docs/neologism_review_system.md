# 新词审判庭 (Neologism Review System) 技术文档

## 1. 概述 (Overview)

**新词审判庭** 是 Project Remis 的一个核心子系统，旨在解决游戏本地化过程中的“术语一致性”难题。它允许用户在正式翻译之前，利用 LLM 从源文件中挖掘潜在的专有名词（Neologisms），并提供一个人工审查界面（审判庭）来决定是否将其纳入术语表。

## 2. 核心架构 (Core Architecture)

系统采用 **双阶段挖掘 (Two-Stage Mining)** 和 **人机协作 (Human-in-the-loop)** 的设计模式。

### 2.1 数据流 (Data Flow)

1.  **源文件 (Source Files)** -> `NeologismMiner` (提取) -> **原始术语 (Raw Terms)**
2.  **原始术语** + **上下文 (Context)** -> `LLM` (分析) -> **候选词 (Candidates)**
3.  **候选词** -> `neologism_candidates.json` (持久化存储)
4.  **前端 UI** (审查) -> **用户决策 (Approve/Reject)**
5.  **批准 (Approve)** -> `GlossaryManager` -> **SQLite 数据库** (正式生效)

## 3. 后端实现 (Backend Implementation)

### 3.1 挖掘器 (`NeologismMiner`)
*   **位置**: `scripts/core/neologism_miner.py`
*   **职责**: 负责与 LLM 交互，执行纯粹的“提取”任务。
*   **核心逻辑**:
    *   使用精心设计的 `SYSTEM_PROMPT`，指示 LLM 扮演“Paradox 游戏本地化专家”。
    *   强制 LLM 输出纯 JSON 格式的字符串列表 `["Term1", "Term2"]`。
    *   **通用兼容性**: 依赖 `BaseApiHandler.generate_with_messages`，支持所有已接入的 API 供应商（OpenAI, Gemini, Ollama 等）。

### 3.2 管理器 (`NeologismManager`)
*   **位置**: `scripts/core/neologism_manager.py`
*   **职责**: 编排整个挖掘工作流，管理候选词的生命周期。
*   **工作流 (Mining Workflow)**:
    1.  **Stage A (Mining)**: 遍历指定文件，分块调用 Miner 提取术语。
    2.  **Deduplication**: 对提取出的术语进行去重，并过滤掉已在术语表或已处理（Approved/Ignored）的词。
    3.  **Context Extraction**: 回溯源文件，为每个新术语抓取 1-3 个包含该词的句子作为上下文证据。
    4.  **Stage B (Analysis)**: 再次调用 LLM，传入术语和上下文，要求 LLM 提供：
        *   `suggestion`: 建议的中文译名。
        *   `reasoning`: 推荐理由（基于上下文的分析）。
*   **持久化**: 数据存储在 `data/cache/neologism_candidates.json`，确保服务重启后进度不丢失。

### 3.3 API 接口 (`web_server.py`)
*   `GET /api/projects/{id}/files`: 列出项目下的所有文本文件，供前端选择。
*   `POST /api/neologisms/mine`: 触发后台挖掘任务（支持指定 `file_paths`）。
*   `GET /api/neologisms`: 获取所有状态为 `pending` 的候选词。
*   `POST /api/neologisms/{id}/approve`: 批准词汇，将其写入 `GlossaryManager` 并更新状态。
*   `POST /api/neologisms/{id}/reject`: 驳回词汇，更新状态为 `ignored`。

## 4. 前端实现 (Frontend Implementation)

### 4.1 页面架构 (`NeologismReviewPage.jsx`)
页面采用 **Tab 布局** 分离配置与执行：

1.  **Mining Console (挖掘控制台)**
    *   **功能**: 任务配置中心。
    *   **交互**: 用户选择项目 -> (可选) 勾选特定文件 -> 选择 API 供应商 -> 启动挖掘。
    *   **设计**: 清晰的左右分栏，左侧配置参数，右侧文件树选择。

2.  **Judgment Court (审判庭)**
    *   **功能**: 沉浸式审查界面。
    *   **布局**:
        *   **Docket (左侧列表)**: 显示待审案件（候选词）。
        *   **Main View (主视图)**:
            *   **Header**: 显示巨大化的原文和来源文件。
            *   **Left Panel**: 显示 AI 的推理 (Reasoning) 和可编辑的最终译名输入框。
            *   **Right Panel**: 显示高亮的上下文例句 (Contextual Evidence)，帮助用户理解词汇在游戏中的实际用法。
    *   **操作**: "Approve" (批准) 和 "Ignore" (忽略) 按钮。

### 4.2 国际化 (I18N)
*   全面支持中英双语，翻译键值位于 `neologism_review` 命名空间下。

## 5. 扩展性设计 (Extensibility)

*   **多模型支持**: 通过 `BaseApiHandler` 的抽象，系统天然支持未来接入的任何新 LLM，无需修改挖掘逻辑。
*   **独立存储**: 候选词使用 JSON Sidecar 模式存储，不污染主数据库，方便迁移和清理。
