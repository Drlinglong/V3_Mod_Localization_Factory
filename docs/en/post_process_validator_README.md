# 后处理验证器使用说明

## 概述

后处理验证器是一个专门用于检查AI翻译后文本格式的工具，确保翻译结果符合各个Paradox游戏的特定语法要求。它能够检测出可能导致游戏崩溃或显示异常的格式问题。

## 功能特性

- **多游戏支持**: 支持5个Paradox游戏（Victoria 3、Stellaris、EU4、HOI4、CK3）
- **智能检测**: 使用正则表达式检测各种格式问题
- **分级验证**: 提供ERROR、WARNING、INFO三个级别的验证结果
- **批量处理**: 支持批量验证多个文本
- **国际化支持**: 支持中英文界面
- **详细日志**: 提供详细的验证结果和问题描述

## 架构设计

### 核心类结构

```
BaseGameValidator (基类)
├── Victoria3Validator (维多利亚3)
├── StellarisValidator (群星)
├── EU4Validator (欧陆风云4)
├── HOI4Validator (钢铁雄心4)
└── CK3Validator (十字军之王3)

PostProcessValidator (主验证器)
```

### 验证级别

- **ERROR**: 严重问题，可能导致游戏崩溃
- **WARNING**: 警告问题，可能影响游戏显示
- **INFO**: 信息提示，不影响游戏运行

## 使用方法

### 基本用法

```python
from scripts.utils.post_process_validator import PostProcessValidator

# 创建验证器实例
validator = PostProcessValidator()

# 验证单个文本
results = validator.validate_game_text("1", "文本内容", line_number=1)

# 批量验证
batch_results = validator.validate_batch("1", ["文本1", "文本2"], start_line=1)

# 获取验证摘要
validator.log_validation_summary(batch_results, "Victoria 3")
```

### 便捷函数

```python
from scripts.utils.post_process_validator import validate_text, validate_batch

# 验证单个文本
results = validate_text("1", "文本内容", 1)

# 批量验证
batch_results = validate_batch("1", ["文本1", "文本2"], 1)
```

## 游戏特定验证规则

### Victoria 3
- 检查方括号内的中文字符（[GetName中文]）
- 验证格式化命令格式（#key text#!）
- 检查工具提示键格式
- 检测文本图标格式（@icon!）

### Stellaris
- 检查方括号内的中文字符
- 验证变量格式（$variable$）
- 检查图标标签格式（£icon£）
- 检测格式化标签（§Y...§!）

### Europa Universalis IV
- 检查方括号内的中文字符
- 验证变量格式
- 检查国家标签格式（@TAG）
- 检测图标和格式化标签

### Hearts of Iron IV
- 检查方括号内的中文字符
- 验证格式化变量（[?var|codes]）
- 检查字符串嵌套格式
- 检测颜色标签和图标

### Crusader Kings III
- 检查方括号内的中文字符
- 验证字符串嵌套格式
- 检查文本格式化命令
- 检测图标标签格式

## 集成到工作流

### 在翻译完成后调用

```python
# 假设这是翻译完成后的文本列表
translated_texts = ["翻译后的文本1", "翻译后的文本2", ...]

# 创建验证器
validator = PostProcessValidator()

# 进行格式验证
batch_results = validator.validate_batch(game_id, translated_texts, start_line=1)

# 记录验证结果
validator.log_validation_summary(batch_results, game_name)

# 根据验证结果决定是否需要人工检查
if any(result.level == ValidationLevel.ERROR for results in batch_results.values() for result in results):
    print("发现严重格式问题，建议人工检查！")
```

### 在文件处理过程中调用

```python
def process_translated_file(file_path, game_id):
    """处理翻译后的文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 验证每一行
    validator = PostProcessValidator()
    validation_results = validator.validate_batch(game_id, lines, 1)
    
    # 记录问题行
    problematic_lines = []
    for line_num, results in validation_results.items():
        for result in results:
            if result.level in [ValidationLevel.ERROR, ValidationLevel.WARNING]:
                problematic_lines.append({
                    'line': line_num,
                    'text': lines[line_num - 1].strip(),
                    'issues': [r.message for r in results]
                })
    
    return problematic_lines
```

## 配置和自定义

### 添加新的验证规则

```python
class CustomValidator(BaseGameValidator):
    def __init__(self):
        super().__init__("custom", "Custom Game")
        
    def validate_text(self, text: str, line_number: Optional[int] = None) -> List[ValidationResult]:
        results = []
        
        # 添加自定义验证逻辑
        if "问题模式" in text:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="发现自定义问题模式",
                details="具体问题描述",
                line_number=line_number,
                text_sample=text[:100]
            ))
        
        return results
```

### 修改验证级别

```python
# 在验证器中修改验证级别
class Victoria3Validator(BaseGameValidator):
    def validate_text(self, text: str, line_number: Optional[int] = None) -> List[ValidationResult]:
        results = []
        
        # 将某些验证从ERROR降级为WARNING
        if re.search(r'[\u4e00-\u9fff]', text):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,  # 改为WARNING
                message="发现中文字符",
                line_number=line_number
            ))
        
        return results
```

## 日志和输出

### 日志格式

验证器会输出结构化的日志信息：

```
2025-01-XX XX:XX:XX - ERROR - [Victoria 3] 方括号内发现中文字符，这可能导致游戏崩溃
详细信息: 问题内容: [GetName中文]
2025-01-XX XX:XX:XX - WARNING - [Victoria 3] 格式化命令格式不正确
详细信息: 命令: 123invalid
```

### 验证摘要

```
格式验证完成 - Victoria 3: 发现 2 个错误, 1 个警告
```

## 性能考虑

- **正则表达式优化**: 使用预编译的正则表达式提高性能
- **批量处理**: 支持批量验证，减少重复初始化开销
- **内存管理**: 验证结果使用轻量级数据结构

## 故障排除

### 常见问题

1. **导入错误**: 确保项目路径正确设置
2. **国际化加载失败**: 检查语言文件路径和格式
3. **正则表达式匹配异常**: 检查特殊字符转义

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志输出
validator = PostProcessValidator()
```

## 未来扩展

- 支持更多游戏类型
- 添加自动修复建议
- 集成到CI/CD流程
- 支持自定义验证规则配置
- 添加性能基准测试

## 贡献指南

欢迎提交Issue和Pull Request来改进这个验证器。请确保：

1. 遵循现有的代码风格
2. 添加适当的测试用例
3. 更新相关文档
4. 测试所有受影响的游戏类型
