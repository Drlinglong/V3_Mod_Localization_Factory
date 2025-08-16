# 游戏专用词典模块 - 工具使用指南

## 概述

本模块为V3_Mod_Localization_Factory项目提供了游戏专用的词典功能，确保翻译过程中术语的一致性和准确性。

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
# 在parser.py中
CURRENT_GAME_PREFIX = 'victoria3'  # 或 'stellaris', 'eu4', 'hoi4', 'ck3'
```

#### 步骤3: 运行解析器
```bash
# 在data/glossary目录下运行
python parser.py
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