# 词典系统机制与运行说明

## 概述

本文档详细说明了V3_Mod_Localization_Factory项目中词典系统的核心机制、功能特性和运行方式。词典系统是确保游戏Mod翻译一致性和准确性的关键组件。

## 系统架构

### 核心组件

```
GlossaryManager (词典管理器)
├── 词典加载与合并
├── 术语提取与匹配
├── 智能匹配算法
├── 提示生成与注入
└── 外挂词典支持
```

### 数据流

```
词典文件 → GlossaryManager → 术语提取 → AI提示注入 → 翻译结果
    ↓              ↓              ↓           ↓
  JSON格式    内存管理      智能匹配     一致性保证
```

## 核心功能机制

### 1. 智能术语匹配系统

#### 匹配类型
- **EXACT**: 完全匹配（置信度: 1.0）
- **VARIANT**: 变体匹配（置信度: 0.9）
- **ABBREVIATION**: 缩写匹配（置信度: 0.8）
- **PARTIAL**: 部分匹配（置信度: 0.7）
- **FUZZY**: 模糊匹配（置信度: 0.3-0.6）

#### 匹配算法
```python
def _smart_term_matching(self, text: str, source_lang: str, target_lang: str):
    # 1. 精确匹配检查
    # 2. 变体匹配检查
    # 3. 缩写匹配检查
    # 4. 部分匹配检查（包含模糊匹配）
    # 5. 结果去重和排序
```

### 2. 模糊匹配机制

#### 触发条件
- 启用模糊匹配模式（loose模式）
- 文本长度超过阈值
- 未找到精确匹配

#### 算法实现
```python
def _check_fuzzy_match(self, text: str, term: str, lang: str):
    # 1. 文本分词（CJK语言按字符，其他按单词）
    # 2. 计算Levenshtein距离
    # 3. 计算相似度比率
    # 4. 返回置信度分数
```

#### 置信度计算
```python
# 模糊匹配置信度范围: 0.3 - 0.6
confidence = 0.3 + (match_ratio * 0.3)
```

### 3. 多语言变体支持

#### 变体结构
```json
{
  "variants": {
    "en": ["Shiro", "Shiro-chan"],
    "zh-CN": ["小白子", "狼女"],
    "ja": ["シロ", "シロちゃん"],
    "ko": ["시로", "시로짱"]
  }
}
```

#### 缩写支持
```json
{
  "abbreviations": {
    "en": ["Shiroko", "Shiro"],
    "zh-CN": ["白子", "小白"],
    "ja": ["シロコ", "シロ"],
    "ko": ["시로코", "시로"]
  }
}
```

### 4. 动态提示生成

#### 提示结构
```
=== GLOSSARY TERMS ===
[EXACT] English Term → 中文翻译 (Confidence: 1.0)
[VARIANT] English Variant → 中文翻译 (Confidence: 0.9)
[ABBREVIATION] English Abbr → 中文翻译 (Confidence: 0.8)
[FUZZY] English Fuzzy → 中文翻译 (Confidence: 0.5)

Translation Requirements:
- EXACT/VARIANT: Use exact translation
- ABBREVIATION: Use abbreviation translation
- FUZZY: Use fuzzy translation with caution
```

## 运行流程

### 1. 系统启动阶段

```python
# 1. 加载主词典
glossary_manager.load_game_glossary(game_id)

# 2. 扫描外挂词典
auxiliary_glossaries = glossary_manager.scan_auxiliary_glossaries(game_id)

# 3. 合并词典数据
merged_glossary = glossary_manager.merge_glossaries()
```

### 2. 翻译前准备阶段

```python
# 1. 提取待翻译文本中的相关术语
relevant_terms = glossary_manager.extract_relevant_terms(
    texts, source_lang, target_lang
)

# 2. 生成动态提示
glossary_prompt = glossary_manager.create_dynamic_glossary_prompt(
    relevant_terms, source_lang, target_lang
)
```

### 3. 翻译执行阶段

```python
# 1. 构建完整提示
full_prompt = base_prompt + glossary_prompt + format_instructions

# 2. 调用AI API
response = ai_client.generate_content(full_prompt)

# 3. 后处理翻译结果
translated_text = post_process(response.text)
```

## 配置选项

### 1. 模糊匹配模式

#### 严格模式 (strict)
- 禁用模糊匹配
- 只使用精确匹配和变体匹配
- 适用于需要高精度的场景

#### 宽松模式 (loose)
- 启用模糊匹配
- 容忍拼写错误和轻微差异
- 适用于一般翻译场景

### 2. 匹配阈值配置

```python
# 模糊匹配触发阈值
FUZZY_TRIGGER_THRESHOLD = 3  # 文本长度超过3个字符时启用

# 置信度范围
FUZZY_CONFIDENCE_MIN = 0.3
FUZZY_CONFIDENCE_MAX = 0.6
```

## 性能特性

### 1. 内存管理
- 词典数据在内存中缓存
- 支持大词典文件（100MB+）
- 智能内存释放机制

### 2. 匹配性能
- 时间复杂度: O(n*m)，n为文本长度，m为词典条目数
- 支持并行处理
- 缓存常用匹配结果

### 3. 扩展性
- 支持无限数量的外挂词典
- 动态词典加载
- 热更新支持

## 错误处理与回退

### 1. 词典加载失败
```python
try:
    glossary_manager.load_game_glossary(game_id)
except Exception as e:
    logging.warning("词典加载失败，使用无词典模式")
    # 回退到无词典模式
```

### 2. 术语提取失败
```python
try:
    relevant_terms = glossary_manager.extract_relevant_terms(...)
except Exception as e:
    logging.error("术语提取失败")
    relevant_terms = []  # 空列表，不影响翻译
```

### 3. 提示生成失败
```python
try:
    glossary_prompt = glossary_manager.create_dynamic_glossary_prompt(...)
except Exception as e:
    logging.error("提示生成失败")
    glossary_prompt = ""  # 空提示，使用基础翻译
```

## 监控与日志

### 1. 性能指标
- 词典加载时间
- 术语匹配数量
- 匹配类型分布
- 模糊匹配成功率

### 2. 日志记录
```python
logging.info(f"词典加载成功: {game_id}, 条目数: {count}")
logging.info(f"术语提取完成: 找到 {len(terms)} 个相关术语")
logging.info(f"提示注入成功: {len(terms)} 个术语")
```

### 3. 调试信息
- 匹配过程详细日志
- 置信度计算过程
- 词典合并状态

## 最佳实践

### 1. 词典设计
- 使用清晰的ID命名规范
- 合理组织变体和缩写
- 保持元数据的完整性

### 2. 性能优化
- 避免过大的词典文件
- 定期清理无用条目
- 使用合适的匹配模式

### 3. 维护建议
- 定期验证词典质量
- 及时更新过时术语
- 监控匹配效果

## 故障排除

### 1. 常见问题

#### 术语未匹配
- 检查拼写和大小写
- 确认变体配置
- 验证语言代码

#### 性能下降
- 检查词典文件大小
- 优化匹配算法
- 调整缓存策略

#### 内存占用过高
- 检查词典条目数量
- 优化数据结构
- 启用内存压缩

### 2. 调试工具

#### 测试脚本
```bash
# 测试基本功能
python test_glossary.py

# 测试模糊匹配
python test_fuzzy_matching.py

# 测试多语言支持
python test_multilingual.py
```

#### 验证工具
```bash
# 验证词典格式
python validator.py

# 检查词典质量
python check_glossary_quality.py
```

## 未来发展方向

### 1. 功能增强
- 支持更多匹配算法
- 增加机器学习优化
- 扩展语言支持

### 2. 性能提升
- 优化匹配算法
- 增加并行处理
- 改进缓存机制

### 3. 用户体验
- 可视化配置界面
- 实时性能监控
- 智能建议系统

## 技术规格

### 系统要求
- Python 3.8+
- 内存: 建议2GB+
- 存储: 词典文件大小无限制

### 支持格式
- 输入: JSON格式词典文件
- 输出: 结构化翻译提示
- 日志: 标准Python logging

### API接口
```python
class GlossaryManager:
    def load_game_glossary(self, game_id: str) -> bool
    def extract_relevant_terms(self, texts: List[str], source_lang: str, target_lang: str) -> List[Dict]
    def create_dynamic_glossary_prompt(self, terms: List[Dict], source_lang: str, target_lang: str) -> str
    def set_fuzzy_matching_mode(self, mode: str) -> None
```

## 总结

词典系统是V3_Mod_Localization_Factory项目的核心组件，通过智能匹配、多语言支持和动态提示注入，确保游戏Mod翻译的一致性和准确性。系统设计注重性能、扩展性和易用性，为游戏本地化提供了强大的技术支持。
