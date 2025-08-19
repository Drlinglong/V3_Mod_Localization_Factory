# 🚀 Quick Start Guide

> Get started in 5 minutes and experience the power of Paradox Mod Localization Factory

## 📋 Prerequisites

- Windows 10/11 system
- Python 3.8+ installed
- Normal network connection (for AI translation API)

## ⚡ 5-Minute Quick Start

### 1️⃣ Download Project
```bash
git clone https://github.com/your-repo/V3_Mod_Localization_Factory.git
cd V3_Mod_Localization_Factory
```

### 2️⃣ One-Click Configuration
Double-click the `Initial Setup.bat` file in the project root directory, then follow the prompts:
- Select AI service provider (Gemini recommended)
- Enter API key
- Wait for automatic dependency installation

### 3️⃣ Prepare Mod Files
Place the mod folder you want to localize into the `source_mod` directory:
```
V3_Mod_Localization_Factory/
├── source_mod/
│   └── Your_Mod_Name/          # Entire mod folder
│       ├── localization/        # Localization files
│       ├── thumbnail.png        # Thumbnail
│       └── descriptor.mod       # Descriptor file
```

### 4️⃣ Start Translation
Run the main program:
```bash
python scripts/main.py
```

Follow the menu prompts:
1. Select API provider
2. Select game type
3. Select source and target languages
4. Confirm to start translation

### 5️⃣ View Results
After translation is complete, find your localization package in the `my_translation` directory!

## 🎯 Supported Games

- ✅ **Victoria 3** - 11 languages
- ✅ **Stellaris** - 10 languages  
- ✅ **Hearts of Iron IV** - 9 languages
- ✅ **Crusader Kings III** - 8 languages
- ⚠️ **Europa Universalis IV** - 4 languages (Chinese not supported)

## 🔧 Common Issues

**Q: "Invalid API key" error?**
A: Check environment variable settings or re-run the configuration script

**Q: Translation is slow?**
A: The system automatically processes in batches, please be patient

**Q: How to improve translation quality?**
A: Use higher quality AI services or add game-specific glossaries

## 📚 Next Steps

- 📖 Read [Detailed Installation](docs/setup/installation-zh.md)
- 🎓 Check [Beginner's Guide](docs/user-guides/beginner-guide-en.md)
- 🔧 Learn about [Glossary System](docs/glossary/overview.md)

---

> 💡 **Tip**: For first-time use, it's recommended to test with a small mod to familiarize yourself with the process before handling large mods
