# 数据存储与归档机制指南

## 1. 背景与目的

为了提升应用的健壮性、性能和可扩展性，项目的数据存储核心已从原先的JSON文件系统迁移至两个独立的SQLite数据库。本文档旨在详细说明这些数据库的技术细节，并为未来的开发者提供一份清晰的数据维护与工作流交互指南。

- **词典数据库 (`data/database.sqlite`)**: 存储所有游戏的词典术语。
- **Mod缓存数据库 (`data/mods_cache.sqlite`)**: 存储翻译过程中的源语言快照和翻译结果，是实现“增量更新”功能的基础。

## 2. 词典数据库 (`database.sqlite`)

该数据库负责管理所有结构化的词典数据。

### 2.1. 数据库模式 (Schema)

数据库包含两个核心表格：`glossaries` 和 `entries`。

#### 表1: `glossaries` (词典元数据表)
该表存储每个词典（无论是主词典还是辅助词典）的元信息。

| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `glossary_id` | INTEGER | 主键, 唯一的词典标识符。 |
| `game_id` | TEXT | 所属游戏 (如 'victoria3')。 |
| `name` | TEXT | 词典名称。 |
| `description` | TEXT | 词典的详细描述。 |
| `is_main` | INTEGER | 是否为主词典 (1 是, 0 否)。 |
| ... | ... | (其他元数据字段) |

#### 表2: `entries` (词条表)
该表存储具体的词条翻译信息。

| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `entry_id` | TEXT | 主键, 词条的唯一ID。 |
| `glossary_id` | INTEGER | 外键, 关联到 `glossaries.glossary_id`。 |
| `translations` | TEXT | 包含所有语言翻译的JSON字符串对象。 |
| `variants` | TEXT | 变体形式的JSON字符串对象。 |
| ... | ... | (其他词条相关字段) |

### 2.2. 数据交互与加载逻辑

所有与词典数据库的交互都应通过 `scripts/core/glossary_manager.py` 中的 `GlossaryManager` 类进行。

#### 核心加载方法：

1.  **`get_available_glossaries(game_id)`**:
    -   **功能**: 查询并返回指定游戏所有可用词典的列表（包括ID, 名称, 描述等）。
    -   **用途**: 供UI（无论是CLI还是Web）构建一个让用户选择词典的界面。

2.  **`load_selected_glossaries(selected_ids)`**:
    -   **功能**: 接收一个包含多个 `glossary_id` 的列表，**只加载并合并这些被选中的词典**到内存中，供后续的翻译流程使用。
    -   **用途**: 这是实现按需加载的核心。

3.  **`load_game_glossary(game_id)`**:
    -   **功能**: 作为一个便捷的默认加载方式，它内部会查找指定游戏的**主词典** (`is_main = 1`)，然后调用 `load_selected_glossaries` 来仅加载这个主词典。
    -   **用途**: 当用户未通过UI指定任何词典时，系统默认执行此操作。

## 3. Mod缓存数据库 (`mods_cache.sqlite`)

该数据库用于归档每次“初次翻译”的结果，为未来的“增量更新”功能提供数据支持。

### 3.1. 数据库模式 (Schema)

| 表名 | 用途 |
| :--- | :--- |
| `mods` | 存储Mod的基本信息，生成唯一的内部`mod_id`。 |
| `mod_identities` | 存储Mod的唯一标识（如创意工坊ID `remote_file_id`），并关联到`mod_id`。 |
| `source_versions` | 存储一个Mod在某个时间点的源语言文件快照。通过对所有源文件内容计算哈希值(`snapshot_hash`)来确保唯一性。 |
| `source_entries` | 存储某个版本快照下的所有源语言键值对 (`entry_key`, `source_text`)。 |
| `translated_entries` | 存储最终的翻译结果，关联到源条目和目标语言。 |

### 3.2. “初始翻译”工作流中的归档流程

在 `scripts/workflows/initial_translate.py` 中，归档流程由 `ARCHIVE_RESULTS_AFTER_TRANSLATION` 开关控制，并分为三个阶段：

-   **阶段一 (任务启动时)**:
    1.  解析 `.mod` 文件，提取 `remote_file_id`。
    2.  使用 `remote_file_id` 查询 `mod_identities` 表，找到或创建一个对应的内部 `mod_id`。这个 `mod_id` 将贯穿整个归档流程。

-   **阶段二 (翻译开始前)**:
    1.  在读取并解析完所有源语言文件后，将所有待翻译的文本内容合并，计算一个总的 `snapshot_hash`。
    2.  用 `mod_id` 和 `snapshot_hash` 查询 `source_versions` 表。
    3.  如果哈希**不存在**，则说明这是一个全新的版本：
        -   在 `source_versions` 表中创建一个新版本记录，获得 `version_id`。
        -   将当前版本的所有源语言键值对 (`entry_key`, `source_text`) 存入 `source_entries` 表，并与 `version_id` 关联。
    4.  如果哈希**已存在**，则直接获取对应的 `version_id`，跳过源条目插入。

-   **阶段三 (各语言翻译完成后)**:
    1.  在针对**每一种**目标语言的翻译循环结束时（例如，中文翻译全部完成后）。
    2.  遍历该语言的翻译结果（`entry_key` -> `translated_text`）。
    3.  根据 `version_id` 和 `entry_key` 从 `source_entries` 表中查出 `source_entry_id`。
    4.  使用 `source_entry_id` 和 `language_code`（如 'zh-CN'）作为联合唯一键，将翻译结果通过 `UPSERT`（存在则更新，不存在则插入）操作写入 `translated_entries` 表。

这个流程确保了每次翻译都有源和译文的快照记录，为后续的版本比对和增量翻译提供了坚实的数据基础。
