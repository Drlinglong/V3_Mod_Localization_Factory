# 词典系统概览

## 📚 词典系统简介

词典系统是确保游戏Mod翻译一致性和准确性的关键组件。它通过智能术语匹配、模糊匹配算法和外挂词典支持，为AI翻译提供准确的术语参考。

## 🔧 工具和脚本

### 核心工具
- **[词典工具使用指南](tools-guide.md)** - 如何使用parser.py和validator.py
- **[系统机制说明](system-mechanism.md)** - 词典系统的核心机制和算法
- **[碧蓝档案词典指南](blue-archive-guide.md)** - 特定主题词典使用说明

### 脚本文件
- `parser.py` - 通用词典解析器，将Paratranz导出的文本转换为JSON
- `validator.py` - 词典验证器，检查数据完整性和一致性
- `input.txt` - Paratranz导出的术语文件模板

## 🗂️ 词典文件结构

### 主词典
```
data/glossary/
├── victoria3/
│   └── glossary.json          # 维多利亚3主词典
├── stellaris/
│   └── glossary.json          # 群星主词典
├── eu4/
│   └── glossary.json          # 欧陆风云4主词典
├── hoi4/
│   └── glossary.json          # 钢铁雄心4主词典
└── ck3/
    └── glossary.json          # 十字军之王3主词典
```

### 外挂词典
```
data/glossary/
├── stellaris/
│   ├── glossary.json          # 群星主词典
│   └── blue_archive.json      # 碧蓝档案外挂词典
└── victoria3/
    ├── glossary.json          # 维多利亚3主词典
    └── custom_theme.json      # 自定义主题词典
```

## 🚀 快速开始

### 1. 准备术语文件
从Paratranz.cn项目导出术语文件，格式如下：
```
术语英文名
词性（名词/形容词/动词）
中文翻译
备注信息（可选）
变体形式（可选，如：Term, Terms）
修改于 2024/01/01
评论 0
```

### 2. 生成词典
```bash
# 在data/glossary目录下运行
python parser.py
```

### 3. 验证词典质量
```bash
python validator.py
```

### 4. 部署词典
将生成的`glossary.json`文件放入对应游戏目录。

## 🔍 核心功能特性

### 智能术语匹配
- **EXACT**: 完全匹配（置信度: 1.0）
- **VARIANT**: 变体匹配（置信度: 0.9）
- **ABBREVIATION**: 缩写匹配（置信度: 0.8）
- **PARTIAL**: 部分匹配（置信度: 0.7）
- **FUZZY**: 模糊匹配（置信度: 0.3-0.6）

### 多语言变体支持
支持多种语言的术语变体和缩写，确保跨语言翻译的一致性。

### 外挂词典系统
可以为特定主题的MOD提供额外的术语支持，如碧蓝档案、科幻主题等。

## 📖 详细文档

- **[工具使用指南](tools-guide.md)** - 详细的工具使用说明
- **[系统机制](system-mechanism.md)** - 深入的技术实现说明
- **[碧蓝档案指南](blue-archive-guide.md)** - 特定词典的使用方法

## 🆘 常见问题

### Q: 如何添加新的外挂词典？
A: 参考`blue_archive.json`的格式，创建新的JSON文件并放入对应游戏目录。

### Q: 词典验证失败怎么办？
A: 检查输入文件格式是否正确，确保使用UTF-8编码。

### Q: 如何更新现有词典？
A: 重新运行parser.py，它会自动合并新的术语条目。
