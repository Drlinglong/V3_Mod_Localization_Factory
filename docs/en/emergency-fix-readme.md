# 🚨 紧急修复：中文标点符号问题

## 问题概述

**严重Bug**: 英文版群星不支持中文字符，中文字符会变成问号（?），导致：
- 显示异常：中文标点符号变成问号
- 联机同步问题：携带中文符号的mod会导致联机不同步

## 快速修复

### 1. 运行修复脚本

```bash
# 修复my_translation目录下的所有yml文件
python scripts/emergency_fix_chinese_punctuation.py ./my_translation

# 修复source_mod目录下的所有yml文件
python scripts/emergency_fix_chinese_punctuation.py ./source_mod

# 仅扫描，不修改文件（推荐先运行）
python scripts/emergency_fix_chinese_punctuation.py ./my_translation --dry-run
```

### 2. 查看修复报告

脚本会自动生成修复报告，显示：
- 扫描的文件数量
- 发现的标点符号问题
- 已修复的问题数量
- 详细的替换记录

### 3. 验证修复结果

修复完成后，请：
1. 在英文版群星中测试mod
2. 确认标点符号显示正常
3. 测试联机同步功能

## 脚本功能

### 支持的标点符号替换

| 中文标点 | 英文标点 | 说明 |
|---------|---------|------|
| ， | , | 中文逗号 → 英文逗号 |
| 。 | . | 中文句号 → 英文句号 |
| ！ | ! | 中文感叹号 → 英文感叹号 |
| ？ | ? | 中文问号 → 英文问号 |
| ： | : | 中文冒号 → 英文冒号 |
| ； | ; | 中文分号 → 英文分号 |
| （） | () | 中文括号 → 英文括号 |
| 【】 | [] | 中文方括号 → 英文方括号 |
| 《》 | <> | 中文尖括号 → 英文尖括号 |
| "" | "" | 中文引号 → 英文引号 |
| '' | '' | 中文单引号 → 英文单引号 |
| … | ... | 中文省略号 → 英文省略号 |
| — | - | 中文破折号 → 英文连字符 |

### 高级选项

```bash
# 生成详细报告文件
python scripts/emergency_fix_chinese_punctuation.py ./my_translation --output report.txt

# 创建备份（推荐）
python scripts/emergency_fix_chinese_punctuation.py ./my_translation --backup

# 组合使用
python scripts/emergency_fix_chinese_punctuation.py ./my_translation --backup --output fix_report.txt
```

## 安全建议

### 1. 备份重要文件
```bash
# 手动备份
cp -r ./my_translation ./my_translation_backup_$(date +%Y%m%d)

# 或使用脚本的备份功能
python scripts/emergency_fix_chinese_punctuation.py ./my_translation --backup
```

### 2. 先进行干运行
```bash
# 先扫描，不修改
python scripts/emergency_fix_chinese_punctuation.py ./my_translation --dry-run

# 确认结果无误后再修复
python scripts/emergency_fix_chinese_punctuation.py ./my_translation
```

### 3. 分批处理
如果文件很多，建议分批处理：
```bash
# 先处理一个mod
python scripts/emergency_fix_chinese_punctuation.py ./my_translation/zh-CN-MODJAM2025

# 再处理另一个mod
python scripts/emergency_fix_chinese_punctuation.py ./my_translation/zh-CN-Blue\ Archive
```

## 常见问题

### Q: 脚本会修改哪些文件？
A: 脚本会扫描指定目录下所有`.yml`文件，只修改包含中文标点符号的文件。

### Q: 如何恢复被修改的文件？
A: 如果使用了`--backup`选项，脚本会创建备份文件。否则，请从版本控制系统恢复。

### Q: 脚本支持哪些编码？
A: 脚本自动尝试UTF-8、UTF-8-BOM、CP1252等编码，确保兼容性。

### Q: 可以只修复特定类型的标点符号吗？
A: 目前脚本会修复所有发现的中文标点符号。如需定制，可以修改脚本中的`CHINESE_PUNCTUATION_MAP`。

## 测试验证

### 运行测试脚本
```bash
python test_chinese_punctuation_fix.py
```

### 手动验证
1. 选择一个包含中文标点符号的yml文件
2. 运行修复脚本
3. 检查修复后的文件内容
4. 在游戏中验证显示效果

## 长期解决方案

### 1. AI翻译优化
- 在翻译提示中明确要求使用英文标点符号
- 建立标点符号使用规范

### 2. 自动化集成
- 在翻译流程中集成标点符号清理
- 建立mod发布前的质量检查

### 3. 预防措施
- 定期扫描现有mod文件
- 建立编码规范文档

## 技术支持

如果遇到问题，请：
1. 查看日志文件 `chinese_punctuation_fix.log`
2. 运行测试脚本验证功能
3. 检查文件权限和编码
4. 联系开发团队

## 更新日志

- **2025-01-27**: 创建紧急修复脚本
- **2025-01-27**: 添加测试脚本和文档
- **2025-01-27**: 支持多种编码格式

---

**⚠️ 重要提醒**: 这是一个紧急修复脚本，请在运行前备份重要文件！
