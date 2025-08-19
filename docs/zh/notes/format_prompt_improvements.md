# Format Prompt 改进文档

## 概述

本次改进为每个游戏配置添加了专门的 `format_prompt`，并实现了保底机制，以提高翻译质量和准确性。

## 改进内容

### 1. 游戏特定的 Format Prompt

每个游戏现在都有针对其特点优化的 `format_prompt`：

#### Victoria 3 ⭐ **最新更新**
- **基于官方Wiki的准确本地化格式规则**
- **数据函数、作用域和概念 ([...])**: 最复杂的语法，完全保留包括括号、句点、圆括号和单引号
- **基础和链式函数**: 保留简单函数如 [GetName] 和链式函数如 [SCOPE.GetType.GetFunction]
- **带参数的函数 (...)**: 圆括号内的内部键和作用域名称不翻译，用户面向的文本应翻译
- **函数格式化 (使用 |)**: 保留完整的格式化代码，如 [GetValue|*] (K/M/B格式)、[GetValue|+] (添加符号和颜色)
- **格式化命令 (#key ... #!)**: 保留 #key 和 #! 标签，翻译中间文本
- **简单格式化**: 颜色如 #R text#! (红色)、#gold text#! (金色)，样式如 #b text#! (粗体)
- **特殊工具提示格式化**: #tooltippable;tooltip:<tooltip_key> text_to_display#! 结构
- **文本图标 (@key!)**: 完全保留包括 @ 和 ! 的整个标签
- **内部键和代码引用**: 下划线字符串不翻译
- **换行**: 完全保留 \n

#### Stellaris ⭐ **最新更新**
- **基于官方Wiki的准确本地化格式规则**
- **作用域命令和动态文本 ([...])**: 完全保留，包括作用域、句点和函数
- **转义规则**: 双括号 `[[` 作为单括号 `[` 的转义序列
- **脚本规则**: 反斜杠转义命令 `\\[This.GetName]` 必须保留前导 `\\`
- **变量和图标 ($...$, £...£)**: 完全保留，包括修饰符（使用 `|` 管道符）
- **数字格式化**: 如 `$VALUE|*1$`（格式化为1位小数）
- **颜色格式化**: 如 `$AGE|Y$`（为变量输出着色）
- **图标帧**: 如 `£leader_skill|3£`（选择图标的第3帧）
- **格式化标签 (§...§!)**: 保留标签本身，翻译内部纯文本
- **内部键和代码引用**: 下划线字符串不翻译
- **换行和制表符**: 完全保留 `\n` 和 `\t`

#### Europa Universalis IV
- 专注于历史、殖民和贸易术语
- 保持文艺复兴/启蒙时代的语调
- 强调早期现代欧洲历史相关术语

#### Hearts of Iron IV ⭐ **最新更新**
- **基于官方Wiki的准确本地化格式规则**
- **方括号 ([...]) 的两种主要用途**: 命名空间和作用域、格式化变量
- **命名空间和作用域**: 如 [GetDateText] 或 [ROOT.GetNameDefCap]，完全保留不翻译
- **格式化变量**: [?variable|codes] 结构，使用 ? 开头，管道符后的代码定义格式
- **格式代码示例**: [?var|%G0] (百分比、绿色、0位小数)、[?var|*] (SI单位如K/M)、[?var|+] (动态颜色)、[?var|.1] (1位小数)
- **字符串嵌套和变量 ($...$)**: 嵌套其他本地化键或变量，如 $KEY_NAME$ 或 $FOCUS_NAME$
- **转义规则**: 双美元符号 $$ 作为单美元符号 $ 的转义序列
- **颜色标签 (§...§!)**: 保留标签本身，翻译内部纯文本
- **文本图标 (£...)**: 单标签表示图标，如 £GFX_army_experience，支持帧修饰符 £icon_name|1
- **国家旗帜 (@TAG)**: 如 @GER 表示国家旗帜，完全保留
- **本地化格式化器**: 独立的 formatter|token 结构，如 building_state_modifier|dam
- **内部键和代码引用**: 下划线字符串不翻译
- **换行**: 完全保留 \n

#### Crusader Kings III
- 专注于中世纪、封建和王朝术语
- 保持中世纪、宫廷的语调
- 强调中世纪角色扮演和王朝管理相关术语

### 2. 保底机制

- 新增 `FALLBACK_FORMAT_PROMPT` 常量
- 当游戏配置中没有专门的 `format_prompt` 时自动使用
- 确保系统始终有可用的格式提示模板

### 3. API Handler 更新

所有三个 API handler 都已更新：

- `openai_handler.py`
- `gemini_handler.py`
- `qwen_handler.py`

现在它们会：
1. 优先检查游戏配置中是否有专门的 `format_prompt`
2. 如果有，使用游戏特定的模板
3. 如果没有，自动回退到保底选项

## 技术实现

### 配置结构

```python
GAME_PROFILES = {
    "1": {
        # ... 其他配置 ...
        "format_prompt": "游戏特定的格式提示模板...",
    },
    # ... 其他游戏 ...
}

# 保底选项
FALLBACK_FORMAT_PROMPT = "通用格式提示模板..."
```

### 使用逻辑

```python
# 优先使用游戏特定的format_prompt，如果没有则使用保底选项
if "format_prompt" in game_profile:
    format_prompt_part = game_profile["format_prompt"].format(
        chunk_size=len(chunk),
        punctuation_prompt=punctuation_prompt if punctuation_prompt else "",
        numbered_list=numbered_list
    )
else:
    # 导入保底选项
    from scripts.config import FALLBACK_FORMAT_PROMPT
    format_prompt_part = FALLBACK_FORMAT_PROMPT.format(
        chunk_size=len(chunk),
        punctuation_prompt=punctuation_prompt if punctuation_prompt else "",
        numbered_list=numbered_list
    )
```

## 优势

1. **提高准确性**: 每个游戏的术语和语调都得到专门优化
2. **降低错误率**: 针对特定游戏的特殊语法和格式要求
3. **保持兼容性**: 保底机制确保系统始终可用
4. **易于维护**: 集中管理所有格式提示模板
5. **可扩展性**: 新增游戏时只需添加相应的 `format_prompt`
6. **群星特殊优势**: 基于官方Wiki的准确规则，大幅降低本地化错误率
7. **Victoria 3特殊优势**: 基于官方Wiki的复杂语法规则，特别是数据函数、作用域和概念的处理
8. **HOI4特殊优势**: 基于官方Wiki的军事策略游戏语法规则，特别是格式化变量、国家旗帜和本地化格式化器的处理

## 注意事项

1. 所有 `format_prompt` 都必须包含以下占位符：
   - `{chunk_size}`: 批次大小
   - `{punctuation_prompt}`: 标点符号转换提示
   - `{numbered_list}`: 编号列表

2. 新增游戏时，建议参考现有模板的结构
3. 保持与现有 `prompt_template` 和 `single_prompt_template` 的一致性
4. **群星特殊要求**: 严格遵循官方Wiki的语法规则，特别是作用域命令、转义序列和修饰符的处理
5. **Victoria 3特殊要求**: 严格遵循官方Wiki的复杂语法规则，特别是数据函数、作用域、概念和格式化命令的处理
6. **HOI4特殊要求**: 严格遵循官方Wiki的语法规则，特别是格式化变量、国家旗帜、本地化格式化器和转义序列的处理

## 测试验证

已通过测试脚本验证：
- 所有5个游戏的 `format_prompt` 都能正确格式化
- 保底选项能正常工作
- 所有占位符都能正确替换
- **群星format_prompt**: 包含所有关键规则，格式化成功，长度2068字符
- **Victoria 3 format_prompt**: 包含所有关键规则，格式化成功，长度2798字符
- **HOI4 format_prompt**: 包含所有关键规则，格式化成功，长度2708字符

## 更新历史

### 2025-01-XX - HOI4 format_prompt重大更新
- 基于官方Wiki更新Hearts of Iron IV的本地化格式规则
- 添加方括号的两种主要用途：命名空间和作用域、格式化变量
- 增加格式化变量、国家旗帜、本地化格式化器等高级功能说明
- 大幅提高HOI4本地化的准确性和可靠性

### 2025-01-XX - Victoria 3 format_prompt重大更新
- 基于官方Wiki更新Victoria 3的本地化格式规则
- 添加数据函数、作用域和概念的详细语法说明
- 增加格式化命令、工具提示格式化等高级功能说明
- 大幅提高Victoria 3本地化的准确性和可靠性

### 2025-01-XX - 群星format_prompt重大更新
- 基于官方Wiki更新群星的本地化格式规则
- 添加作用域命令、转义规则、脚本规则等详细说明
- 增加修饰符、数字格式化、颜色格式化等高级功能说明
- 大幅提高群星本地化的准确性和可靠性

## 未来改进方向

1. 可以考虑为不同语言对添加特定的格式提示
2. 可以添加更多游戏特定的语法规则
3. 可以考虑动态生成格式提示模板
4. **优先考虑**: 为其他游戏也收集官方Wiki的准确格式规则
