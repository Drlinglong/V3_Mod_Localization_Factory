# 🚀 快速开始指南

> 5分钟上手，快速体验P社Mod本地化工厂的强大功能

## 📋 前置要求

- Windows 10/11 系统
- Python 3.8+ 已安装
- 网络连接正常（用于AI翻译API）

## ⚡ 5分钟快速开始

### 1️⃣ 下载项目
```bash
git clone https://github.com/your-repo/V3_Mod_Localization_Factory.git
cd V3_Mod_Localization_Factory
```

### 2️⃣ 一键配置
双击运行项目根目录的 `首次安装配置.bat` 文件，按照提示：
- 选择AI服务商（推荐Gemini CLI，每天1000次免费调用）
- 输入API密钥（Gemini CLI无需API密钥）
- 等待自动安装依赖

**Gemini CLI用户额外步骤**：
1. 安装Node.js（如果未安装）
2. 运行 `npm install -g @google/gemini-cli` 安装CLI工具
3. 首次使用运行 `gemini` 进行Google账户OAuth认证

### 3️⃣ 准备Mod文件
将你要本地化的Mod文件夹放入 `source_mod` 目录：
```
V3_Mod_Localization_Factory/
├── source_mod/
│   └── 你的Mod名称/          # 整个Mod文件夹
│       ├── localization/     # 本地化文件
│       ├── thumbnail.png     # 封面图
│       └── descriptor.mod    # 描述文件
```

### 4️⃣ 开始翻译
**推荐方式**：双击运行 `run.bat` 文件
- 自动检测并激活 conda 虚拟环境（如果存在）
- 自动检查 Python、API 库和密钥配置
- 提供简洁的环境状态反馈
- 无虚拟环境时自动回退到系统默认环境

**手动方式**：直接运行主程序
```bash
python scripts/main.py
```

按照菜单提示：
1. 选择API供应商
2. 选择游戏类型
3. 选择源语言和目标语言
4. 确认开始翻译

### 5️⃣ 查看结果
翻译完成后，在 `my_translation` 目录下找到你的本地化包！

## 🎯 支持的游戏

- ✅ **维多利亚3** - 11种语言
- ✅ **群星** - 10种语言  
- ✅ **钢铁雄心4** - 9种语言
- ✅ **十字军之王3** - 8种语言
- ⚠️ **欧陆风云4** - 4种语言（不支持中文）

## 🔧 常见问题

**Q: 提示"API密钥无效"怎么办？**
A: 检查环境变量设置，或重新运行配置脚本

**Q: Gemini CLI提示"未找到"怎么办？**
A: 确保已安装Node.js并运行 `npm install -g @google/gemini-cli`，然后运行 `gemini` 进行认证

**Q: 翻译速度慢怎么办？**
A: 系统会自动分批处理，耐心等待即可

**Q: 如何提高翻译质量？**
A: 使用更高质量的AI服务（如Gemini CLI的2.5 Pro模型），或添加游戏专用词典

## 📚 下一步

- 📖 阅读 [详细安装步骤](docs/setup/installation-zh.md)
- 🎓 查看 [小白专用指南](docs/user-guides/beginner-guide-zh.md)
- 🔧 了解 [词典系统](docs/glossary/overview.md)

---

> 💡 **提示**: 首次使用建议先用小Mod测试，熟悉流程后再处理大型Mod
