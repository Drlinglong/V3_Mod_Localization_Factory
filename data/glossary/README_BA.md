# 碧蓝档案外挂词典使用说明

## 概述

本项目现在支持外挂词典功能，可以为特定主题的MOD提供额外的术语支持。目前包含一个碧蓝档案（Blue Archive）专用词典。

## 功能特点

### 1. 外挂词典系统
- **主词典**：每个游戏目录下的 `glossary.json` 文件
- **外挂词典**：其他名称的 `.json` 文件（如 `blue_archive.json`）
- **自动合并**：外挂词典条目会与主词典合并，外挂词典优先级更高

### 2. 碧蓝档案词典内容
- **角色名**：阿罗娜、白子、优香、星野、野乃美等
- **技能系统**：EX技能、普通技能、被动技能
- **游戏机制**：战术、战斗、训练、社交等
- **装备道具**：武器、防具、消耗品
- **世界观**：学园、神秘、剧情等

## 使用方法

### 1. 启动程序
运行主程序后，按正常流程选择：
- MOD
- 游戏类型（选择 Stellaris）
- API供应商
- 源语言和目标语言

### 2. 选择外挂词典
在语言选择完成后，程序会显示：
```
主词典 glossary.json 已启用 (包含 X 条术语)
已检测到外挂词典:
[1] Blue Archive (碧蓝档案) - Korean anime mobile game terminology and character names (20 条术语)
请选择需要启用的外挂词典:
输入 0 全部启用
输入 N 不使用外挂词典
```

**选项说明**：
- `0`：启用所有外挂词典
- `1, 2, 3...`：启用特定的外挂词典
- `N`：不使用任何外挂词典

### 3. 工程总览确认
选择外挂词典后，程序会显示完整的工程信息：
```
=== 工程总览 ===
目标MOD: [MOD名称]
API供应商: [供应商名称]
游戏类型: Stellaris (群星)
源语言: [源语言]
目标语言: [目标语言]
是否清理多余文件: 待确认
词典配置: 主词典 + X 个外挂词典
翻译完成后，将询问是否清理多余文件

按 Y 确认开始翻译，按 N 返回语言选择:
```

**确认选项**：
- `Y`：确认并开始翻译
- `N`：返回语言选择界面

### 4. 翻译过程
- 外挂词典会自动与主词典合并
- AI翻译时会优先使用外挂词典中的术语
- 确保碧蓝档案相关术语的翻译一致性

### 5. 清理确认
翻译完成后，程序会询问是否清理源文件：
```
翻译完成！是否要清理源MOD文件夹 '[MOD名称]' 以节省磁盘空间？
This will delete all files except '.metadata', 'localization', and 'thumbnail.png'.
Do you want to continue? (Enter 'y' or 'yes' to confirm):
```

## 词典文件结构

### 主词典 (glossary.json)
```json
{
  "metadata": {
    "name": "Stellaris Glossary",
    "description": "Main game terminology"
  },
  "entries": [...]
}
```

### 外挂词典 (blue_archive.json)
```json
{
  "metadata": {
    "name": "Blue Archive (碧蓝档案)",
    "description": "Korean anime mobile game terminology and character names",
    "type": "auxiliary"
  },
  "entries": [
    {
      "id": "ba_001",
      "translations": {
        "en": "Arona",
        "zh-CN": "阿罗娜",
        "ja": "アロナ",
        "ko": "아로나"
      },
      "metadata": {
        "category": "character",
        "remarks": "Main AI assistant character"
      }
    }
  ]
}
```

## 添加新的外挂词典

### 1. 创建词典文件
在 `data/glossary/[游戏ID]/` 目录下创建新的 `.json` 文件

### 2. 文件命名规范
- 使用描述性的名称（如 `blue_archive.json`）
- 避免使用 `glossary.json`（这是主词典的保留名称）

### 3. 元数据要求
```json
{
  "metadata": {
    "name": "词典名称",
    "description": "词典描述",
    "version": "版本号",
    "type": "auxiliary"
  }
}
```

### 4. 条目格式
每个条目应包含：
- `id`：唯一标识符
- `translations`：多语言翻译
- `metadata`：分类和备注信息

## 注意事项

1. **优先级**：外挂词典条目会覆盖主词典中相同ID的条目
2. **兼容性**：外挂词典需要与主词典使用相同的语言代码
3. **性能**：词典合并会增加少量内存使用，但影响很小
4. **错误处理**：如果外挂词典加载失败，程序会继续使用主词典

## 故障排除

### 问题：外挂词典没有显示
**可能原因**：
- 文件不在正确的目录下
- 文件格式错误（JSON语法错误）
- 文件权限问题

**解决方法**：
- 检查文件路径：`data/glossary/stellaris/blue_archive.json`
- 验证JSON格式
- 检查文件权限

### 问题：词典合并失败
**可能原因**：
- 主词典未正确加载
- 外挂词典格式不兼容

**解决方法**：
- 确保主词典文件存在且可读
- 检查外挂词典的JSON结构

## 扩展建议

1. **更多游戏主题**：可以添加其他游戏的外挂词典
2. **词典验证**：添加词典文件的格式验证
3. **在线词典**：支持从网络加载词典
4. **词典管理**：提供词典的启用/禁用管理界面

---

如有问题或建议，请参考项目主文档或提交Issue。
