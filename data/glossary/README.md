# 游戏专用词典模块

## 概述

本模块为V3_Mod_Localization_Factory项目提供了游戏专用的词典功能，确保翻译过程中术语的一致性和准确性。

## 功能特性

### 1. 自动词典加载
- 在启动翻译脚本时自动加载对应游戏的词典文件
- 支持多种游戏：Victoria 3、Stellaris、EU4、HOI4、CK3
- 如果词典文件不存在，自动回退到无词典模式

### 2. 智能术语提取
- 在翻译前快速扫描待翻译文本
- 自动识别与词典中匹配的术语
- 支持术语变体和别名

### 3. 动态提示注入
- 将相关术语作为高优先级指令注入到AI翻译请求中
- 确保AI严格按照词典进行术语翻译
- 保持游戏术语的一致性和准确性

## 词典文件结构

每个游戏的词典文件位于 `data/glossary/{game_id}/glossary.json`，结构如下：

```json
{
  "metadata": {
    "description": "词典描述",
    "sources": ["来源1", "来源2"],
    "last_updated": "更新时间"
  },
  "entries": [
    {
      "translations": {
        "en": "英文术语",
        "zh-CN": "中文翻译"
      },
      "id": "唯一标识符",
      "metadata": {
        "part_of_speech": "词性",
        "remarks": "备注说明"
      },
      "variants": {
        "en": ["变体1", "变体2"]
      }
    }
  ]
}
```

## 词典解析器工具

### 概述
本模块提供了两个Python脚本，用于将Paratranz.cn的"术语"功能导出的文本文件转换为结构化的JSON词典文件。

### 脚本文件说明

#### 1. `parser.py` - 通用词典解析器
- **功能**: 智能解析Paratranz词典文本，自动合并重复条目，生成结构化JSON文件
- **适用游戏**: 维多利亚3、群星、EU4、HOI4、CK3等所有支持的游戏
- **输入文件**: `input.txt`（Paratranz导出的术语文件）
- **输出文件**: `glossary.json`（结构化词典文件）

#### 2. `validator.py` - 词典验证器
- **功能**: 验证生成的词典文件质量，检查数据完整性和一致性
- **输入文件**: `glossary.json`（由parser.py生成的词典文件）
- **输出文件**: `validation_report.txt`（详细的验证报告）
- **验证项目**: ID冲突检查、翻译冲突检查、同义词问题检测



### 输入文件格式说明

Paratranz导出的术语文件格式如下：
```
术语英文名
词性（名词/形容词/动词）
中文翻译
备注信息（可选）
变体形式（可选，如：Term, Terms）
修改于 2024/01/01
评论 0
```

**示例**:
```
admiral
名词
舰队司令
原版术语
Admiral, Admirals, admirals
修改于 2024/11/15
评论 0
```

### 核心功能特性

#### 1. 智能去重
- 自动识别并合并重复的术语条目（忽略大小写）
- 智能合并备注信息，避免信息丢失
- 保留所有变体形式，提高术语匹配准确性

#### 2. 结构化解析
- 自动识别词性（名词、形容词、动词）
- 提取英文术语和中文翻译
- 保留备注信息和变体形式
- 生成标准化的JSON格式

#### 3. 元数据管理
- 自动生成唯一标识符（ID）
- 记录最后更新时间
- 标注数据来源信息

### 使用方法

#### 步骤1: 准备输入文件
1. 从Paratranz.cn项目导出术语文件
2. 将文件重命名为 `input.txt`
3. 确保文件使用UTF-8编码

#### 步骤2: 配置游戏前缀
在脚本中修改 `CURRENT_GAME_PREFIX` 变量：
```python
# 在parser.py或parserstellaris.py中
CURRENT_GAME_PREFIX = 'victoria3'  # 或 'stellaris', 'eu4', 'hoi4', 'ck3'
```

#### 步骤3: 运行解析器
```bash
# 在data/glossary目录下运行
python parser.py
# 或
python parserstellaris.py
```

#### 步骤4: 检查输出
- 脚本会生成 `glossary.json` 文件
- 控制台会显示处理结果和统计信息
- 检查生成的词典文件是否符合预期

#### 步骤5: 验证词典质量（推荐）
使用 `validator.py` 验证生成的词典文件：
```bash
python validator.py
```
验证器会检查：
- ID冲突（多个词条使用相同ID）
- 翻译冲突（同一英文术语有多个中文翻译）
- 同义词问题（同一中文词翻译多个英文术语）
- 生成详细的验证报告 `validation_report.txt`

### 输出文件示例

生成的 `glossary.json` 文件结构：
```json
{
  "metadata": {
    "description": "Victoria 3 游戏及Mod社区汉化词典",
    "sources": ["数据源自多个社区汉化项目，如Paratranz等"],
    "last_updated": "2025-01-27T10:30:00+11:00"
  },
  "entries": [
    {
      "id": "victoria3_admiral",
      "translations": {
        "en": "admiral",
        "zh-CN": "舰队司令"
      },
      "metadata": {
        "part_of_speech": "Noun",
        "remarks": "原版术语"
      },
      "variants": {
        "en": ["Admiral", "Admirals", "admirals"]
      }
    }
  ]
}
```

### 高级配置选项

#### 1. 自定义词性映射
可以修改 `pos_map` 变量来支持更多词性：
```python
pos_map = {
    "名词": "Noun", 
    "形容词": "Adjective", 
    "动词": "Verb",
    "副词": "Adverb",
    "介词": "Preposition"
}
```

#### 2. 自定义输出文件名
修改 `output_filename` 变量：
```python
output_filename = 'victoria3_glossary.json'  # 自定义输出文件名
```

#### 3. 时区设置
修改时区设置以匹配您的本地时间：
```python
# 修改为您的时区
aest = pytz.timezone('Asia/Shanghai')  # 中国标准时间
```

#### 4. 验证器配置
可以修改 `validator.py` 中的文件路径：
```python
def validate_glossary(input_path='glossary.json', output_path='validation_report.txt'):
    # 修改输入和输出文件路径
    # input_path: 要验证的词典文件路径
    # output_path: 验证报告输出路径
```

### 故障排除

#### 常见问题及解决方案

1. **编码错误**
   - 确保输入文件使用UTF-8编码
   - 检查文件是否包含特殊字符

2. **文件未找到**
   - 确认 `input.txt` 文件存在于脚本同一目录
   - 检查文件权限

3. **解析失败**
   - 检查输入文件格式是否符合要求
   - 查看控制台错误信息

4. **输出文件为空**
   - 检查输入文件内容
   - 确认游戏前缀设置正确

5. **验证器错误**
   - 确保先运行parser.py生成glossary.json文件
   - 检查JSON文件格式是否正确
   - 验证文件编码是否为UTF-8

#### 调试建议

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **测试小样本**
   - 先用少量数据测试脚本功能
   - 确认格式正确后再处理完整文件

3. **检查中间结果**
   - 在关键步骤添加print语句
   - 验证数据解析逻辑

### 性能优化建议

1. **大文件处理**
   - 对于超过10MB的输入文件，考虑分批处理
   - 监控内存使用情况

2. **批量处理**
   - 可以修改脚本支持批量处理多个输入文件
   - 自动合并多个词典文件

3. **缓存机制**
   - 对于重复运行的场景，可以添加缓存机制
   - 避免重复解析相同内容

## 支持的游戏

| 游戏 | 词典文件路径 | 状态 | 词典来源 |
|------|-------------|------|----------|
| Victoria 3 | `data/glossary/victoria3/glossary.json` | ✅ 已创建 | 维多利亚3 汉化 更新V1.2<br>Morgenröte \| 汉语<br>Better Politics Mod 简体中文汉化<br>牛奶汉化 |
| Stellaris | `data/glossary/stellaris/glossary.json` | ✅ 已创建 | 鸽组汉化词典<br>Shrouded Regions汉化词典<br>L网群星mod汉化集词典 |
| EU4 | `data/glossary/eu4/glossary.json` | ✅ 已创建 | 示例词典（基础术语） |
| HOI4 | `data/glossary/hoi4/glossary.json` | ✅ 已创建 | 示例词典（基础术语） |
| CK3 | `data/glossary/ck3/glossary.json` | ✅ 已创建 | 示例词典（基础术语） |

## 词典来源说明

### Victoria 3 词典来源
- **维多利亚3 汉化 更新V1.2**: 官方汉化更新版本，包含最新的游戏术语
- **Morgenröte \| 汉语**: 社区汉化项目
- **Better Politics Mod 简体中文汉化**: 政治系统Mod的专用汉化词典
- **牛奶汉化**: 社区汉化项目，提供丰富的游戏术语对照

### Stellaris 词典来源
- **鸽组汉化词典**: 著名的群星汉化组，提供高质量的科幻术语翻译
- **Shrouded Regions汉化词典**: 专注于神秘区域和特殊事件的术语翻译
- **L网群星mod汉化集词典**: 综合性的群星Mod汉化词典，涵盖多个Mod内容

### 其他游戏词典来源
目前EU4、HOI4和CK3只有基础的示例词典，包含少量核心术语。这些词典主要用于：
- 验证词典系统的功能
- 展示词典文件的标准格式
- 为后续扩展提供基础结构

**注意**: 这些示例词典不包含完整的游戏术语，仅用于系统测试和演示目的。

## 使用方法

### 1. 自动使用
词典功能已集成到主翻译流程中，无需手动配置。当您运行翻译脚本时：

1. 选择游戏后，系统自动加载对应词典
2. 翻译过程中自动提取相关术语
3. 将术语作为高优先级指令注入AI请求

### 2. 手动测试
可以使用测试脚本验证词典功能：

```bash
python test_glossary.py
```

### 3. 添加新游戏词典
1. 在 `data/glossary/` 下创建新的游戏文件夹
2. 创建 `glossary.json` 文件
3. 按照标准格式添加术语条目
4. 确保游戏配置中的 `id` 字段与文件夹名称一致

### 4. 使用词典解析器创建新词典
1. 从Paratranz.cn导出术语文件
2. 使用 `parser.py` 解析生成 `glossary.json`
3. 使用 `validator.py` 验证词典质量
4. 根据验证报告修正问题（如有）
5. 将最终的 `glossary.json` 放入对应游戏文件夹

## 词典条目格式说明

### 必需字段
- `translations`: 包含源语言和目标语言的翻译对照
- `id`: 唯一标识符，建议使用 `{game_id}_{term}` 格式

### 可选字段
- `metadata.part_of_speech`: 词性（如 Noun、Verb、Adjective）
- `metadata.remarks`: 翻译注意事项或说明
- `variants`: 术语的变体形式，用于提高匹配准确性

## 技术实现

### 核心组件
- `GlossaryManager`: 词典管理器类
- `load_game_glossary()`: 加载游戏词典
- `extract_relevant_terms()`: 提取相关术语
- `create_dynamic_glossary_prompt()`: 生成动态提示

### 集成点
- `initial_translate.py`: 启动时自动加载词典
- `openai_handler.py`: 翻译过程中注入词典提示
- 支持所有API供应商（OpenAI、Gemini、Qwen）

## 注意事项

1. **词典文件编码**: 请使用UTF-8编码保存词典文件
2. **术语更新**: 定期更新词典以保持术语的准确性和时效性
3. **性能影响**: 词典功能对翻译性能影响很小，主要是在启动时加载和翻译前扫描
4. **回退机制**: 如果词典加载失败，系统会自动使用无词典模式，确保翻译功能正常运行
5. **输入文件格式**: 使用解析器时，确保Paratranz导出的术语文件格式正确
6. **游戏前缀设置**: 创建新词典时，确保游戏前缀与目标游戏配置一致

## 故障排除

### 常见问题
1. **词典未加载**: 检查词典文件路径和格式是否正确
2. **术语未匹配**: 确认术语拼写和大小写是否一致
3. **性能问题**: 检查词典文件大小，过大的文件可能影响加载速度
4. **解析器错误**: 检查输入文件格式和编码
5. **输出文件异常**: 验证游戏前缀设置和文件权限

### 日志信息
词典相关的操作会在日志中记录，包括：
- 词典加载状态
- 术语提取数量
- 提示注入情况
- 解析器运行状态

## 更新日志

- 2025-01-27: 初始版本，支持5个主要游戏
- 集成到主翻译流程
- 支持动态提示注入
- 提供完整的测试和文档
- 2025-01-27: 更新词典来源信息
  - 添加Victoria 3词典详细来源说明
  - 添加Stellaris词典详细来源说明
  - 完善词典来源表格和说明文档
- 2025-01-27: 新增词典解析器工具说明
  - 添加parser.py和validator.py使用说明
  - 详细说明Paratranz术语文件格式
  - 提供完整的配置和使用指南
  - 添加故障排除和性能优化建议
  - 集成词典质量验证功能