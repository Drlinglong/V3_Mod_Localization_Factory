# 语法检查器重大改进和优化

## 🎯 主要改进

### 1. 修复国际化(i18n)格式化错误
- **问题**: `validation_vic3_unknown_formatting` 等消息的格式化参数不匹配
- **修复**: 统一参数名称，修正所有相关验证消息的格式化调用
- **影响**: 消除了大量"国际化键格式化失败"的错误信息

### 2. 实现智能引号内容提取
- **问题**: 语法检查器错误地检查注释行和行内注释，导致大量无效报错
- **解决方案**: 实现"只检查引号内内容"的方案
- **功能**:
  - 智能移除行内注释（`#注释`）
  - 精确提取引号内的翻译内容
  - 支持各种YAML格式：`key:"value"`、`key: "value"`、`key:0 "value"`、`key:99 "value"`
  - 正确处理嵌套引号：`"He said \"Hello World\" to me"`

### 3. 添加未文档化的Victoria 3格式化命令
- **问题**: `#bold`、`#v` 和 `#tooltip` 命令在V3中实际有效但被误报为未知命令
- **修复**: 
  - 添加 `'bold'`、`'v'` 和 `'tooltip'` 到 `VALID_FORMATTING_KEYS`
  - 实现大小写不敏感的格式化命令检查
  - 将 `'tooltip'` 添加到 `NO_SPACE_REQUIRED_KEYS`（不需要强制空格）
- **影响**: 消除了"满屏幕无效报错"的问题

### 4. 强化翻译提示词(Prompt)
- **问题**: API经常添加不必要的引号，如 `""软件""` 而不是 `软件`
- **解决方案**: 为所有游戏添加严格的引号规则和空格规则
- **内容**:
  ```
  🚨 CRITICAL QUOTE RULE: DO NOT add extra quotes around your translations!
  The game engine will handle quote formatting automatically. Adding quotes will break the display!
  EXAMPLE: If input is 'software', output should be '软件', NOT '"软件"'!
  
  🚨 CRITICAL SPACING RULE: PRESERVE spaces after formatting commands!
  ❌ WRONG: #BOLDtext#! (missing space after #BOLD)
  ✅ CORRECT: #BOLD text#! (space after #BOLD)
  Formatting commands MUST be followed by a space to work properly!
  ```
- **覆盖**: Victoria 3, Stellaris, EU4, HOI4, CK3, 保底选项

### 5. 优化注释行处理
- **问题**: 语法检查器检查注释行，导致无效错误
- **修复**: 添加注释行跳过逻辑
- **代码**: `if not stripped or stripped.startswith("#"): continue`

## 📊 技术细节

### 引号提取算法
```python
def _extract_translatable_content(self, line: str) -> str:
    # 1. 智能移除行内注释（考虑引号内的#符号）
    # 2. 查找冒号后的引号位置（支持数字前缀）
    # 3. 逐字符解析，正确处理转义字符
    # 4. 返回引号内的纯净内容
```

### 支持的格式
- `key:"value"` - 冒号和引号紧贴
- `key: "value"` - 冒号和引号有空格
- `key:0 "value"` - 有数字前缀
- `key:99 "value"` - 任意数字前缀
- `key:0"value"` - 数字和引号紧贴
- `key: 0 "value"` - 数字前后都有空格

## 🎉 效果

- **减少无效报错**: 不再检查注释行和行内注释
- **提高准确性**: 只检查实际需要翻译的内容
- **增强兼容性**: 支持未文档化但有效的格式化命令(`#bold`, `#v`, `#tooltip`)
- **改善翻译质量**: 强化提示词减少API错误（引号+空格规则）
- **支持复杂格式**: 正确处理嵌套引号和转义字符
- **特殊命令处理**: `#tooltip` 命令不需要强制空格，符合实际使用习惯

## 📝 文件修改

- `scripts/core/post_processing_manager.py` - 添加引号提取逻辑
- `scripts/utils/post_process_validator.py` - 修复i18n参数，添加未文档化命令(`#bold`, `#v`, `#tooltip`)，设置`#tooltip`不需要空格
- `scripts/config.py` - 强化所有游戏的翻译提示词（引号规则+空格规则）
- `data/lang/en_US.json` - 添加缺失的i18n键

## ⚠️ 注意事项

- 引号提取算法可能对某些极端格式存在潜在问题
- 建议在实际使用中监控是否有遗漏的格式
- 如发现新的未文档化命令，需要手动添加到验证规则中
