# 测试说明文档

## 📋 测试脚本概览

本项目包含两个主要的测试脚本，用于验证后处理验证器的功能：

### 🔧 `test_validation_with_issues.py`
**用途**: 生成包含各种格式问题的测试文件
**功能**: 
- 创建 `test_validation_issues/` 目录
- 生成 Victoria 3 和 Stellaris 的测试文件
- 包含 ERROR、WARNING、INFO 三个级别的格式问题
- 用于测试后处理验证器的检测能力

**使用方法**:
```bash
python test_validation_with_issues.py
```

**生成的文件**:
- `test_validation_issues/vic3_test.yml` - Victoria 3 测试用例
- `test_validation_issues/stellaris_test.yml` - Stellaris 测试用例

### 🎯 `test_post_processor_direct.py`
**用途**: 直接测试后处理验证器
**功能**:
- 直接处理 `test_validation_issues/` 目录中的测试文件
- 验证后处理器的文件扫描和问题检测功能
- 测试特定验证器的规则
- 显示详细的验证结果和统计信息

**使用方法**:
```bash
python test_post_processor_direct.py
```

## 🧪 测试流程

### 1. 生成测试用例
```bash
python test_validation_with_issues.py
```

### 2. 直接测试后处理器
```bash
python test_post_processor_direct.py
```

### 3. 集成测试（可选）
将生成的测试文件复制到你的mod的 `localization` 文件夹中，然后运行完整的翻译流程，观察后处理验证器的输出。

## 📊 验证级别说明

### 🔴 ERROR (错误) - 最高级别，必须修复
- **方括号内包含中文**: `[中文函数]` → 游戏崩溃
- **概念键包含中文**: `[Concept('中文key', ...)]` → 无法识别
- **变量名包含中文**: `$中文变量$` → 显示异常
- **图标标签包含中文**: `@中文图标!` → 无法加载

### 🟡 WARNING (警告) - 中等级别，建议修复  
- **格式化命令缺少空格**: `#b粗体文本#!` → 应该 `#b 粗体文本#!`
- **未知格式化命令**: `#bold` → 应该是 `#b`
- **标签不成对**: `#R 红色文本` → 缺少 `#!`
- **颜色标签不匹配**: `§R 红色 §Y 黄色` → 没有 `§!`

### 🔵 INFO (信息) - 最低级别，建议检查
- 复杂提示框结构中的中文
- 作用域格式化中的中文

## 📁 项目结构

```
V3_Mod_Localization_Factory/
├── test_validation_with_issues.py      # 生成测试用例
├── test_post_processor_direct.py       # 直接测试后处理器
├── test_validation_issues/             # 测试用例目录
│   ├── vic3_test.yml                   # Victoria 3 测试文件
│   └── stellaris_test.yml              # Stellaris 测试文件
├── archive/tests/                      # 过时的测试文件
├── docs/                               # 项目文档
├── scripts/                            # 核心脚本
└── data/                               # 数据和配置
```

## 🎮 支持的验证规则

### Victoria 3
- 概念链接: `[concept_legitimacy]`
- 复杂函数: `[Concept('key', 'text')]`
- 作用域函数: `[SCOPE.sType('key')]`
- 图标标签: `@icon_name!`
- 格式化命令: `#b 粗体文本#!`

### Stellaris
- 作用域命令: `[Root.GetName]`
- 变量: `$variable$`
- 图标: `£icon£`
- 颜色标签: `§Y 黄色文本§!`

### 其他游戏
- EU4、HOI4、CK3 的特定语法规则

## 🔍 故障排除

### 常见问题

1. **导入错误**: 确保在项目根目录运行脚本
2. **文件不存在**: 先运行 `test_validation_with_issues.py` 生成测试文件
3. **权限问题**: 确保有写入目录的权限

### 调试技巧

- 查看控制台输出的详细错误信息
- 检查 `test_output/` 目录中的验证结果
- 使用 `test_post_processor_direct.py` 进行快速测试

## 📝 扩展测试

如需添加新的测试用例：

1. 修改 `test_validation_with_issues.py` 中的测试内容
2. 在 `test_post_processor_direct.py` 中添加对应的测试逻辑
3. 运行测试验证新用例是否被正确检测

---

**注意**: 这些测试脚本仅用于开发和调试，生产环境中请使用完整的翻译流程。
