> **中文用户请注意:** 本项目是一个基于Python和AI的P社游戏Mod自动化本地化工作流，支持多游戏配置、多语言互译，并为高扩展性而设计。
>
> **[点击此处阅读中文版README](README.md)**

***

# Paradox Mod Localization Factory

> Say goodbye to copy-paste, embrace automation. This project provides a powerful, semi-automated localization workflow for Paradox Interactive (PDS) game mods (e.g., Victoria 3, Stellaris).

## 📚 Documentation Navigation

### 🚀 Quick Start
- [Quick Start Guide](docs/user-guides/quick-start-en.md) - Get started in 5 minutes
- [Detailed Installation](docs/setup/installation-en.md) - Complete installation process

### 📖 User Guides
- [Beginner's Guide (Chinese)](docs/user-guides/beginner-guide-zh.md) - For Chinese users
- [Beginner's Guide (English)](docs/user-guides/beginner-guide-en.md) - For English users

### 🔧 Glossary System
- [Glossary System Overview](docs/glossary/overview.md) - Complete introduction to the glossary system
- [Glossary Tools Guide](docs/glossary/tools-guide.md) - How to use parser.py and validator.py
- [System Mechanism](docs/glossary/system-mechanism.md) - Technical implementation details
- [Blue Archive Glossary](docs/glossary/blue-archive-guide.md) - Specific topic glossary usage

### 👨‍💻 Developer Documentation
- [Project Architecture](docs/developer/architecture-en.md) - System design explanation
- [Parallel Processing Technology](docs/developer/parallel-processing.md) - Performance optimization details
- [Implementation Notes](docs/developer/implementation-notes.md) - Development process records

### ⚙️ Configuration & Troubleshooting
- [Configuration Guide](docs/setup/configuration.md) - Detailed configuration options
- [Common Issues](docs/examples/troubleshooting.md) - Problem solutions

---

### License

This project uses a **dual-licensing** model:

1. **Code** (including `/scripts`, `/core`, `/workflows`, `/utils`, and all other Python source files)  
   Licensed under the **[GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.html)**.  
   - You are free to use, modify, and distribute the code (including for commercial purposes), provided that:
     * You must retain proper attribution to the original author and include the license notice.
     * Any modified version must also be released under the **AGPL-3.0** license.
     * If you deploy this code as a network service (SaaS), you must also make the full source code available to its users.
   - For full terms, see the [AGPL-3.0 text](https://www.gnu.org/licenses/agpl-3.0.html).

2. **Data and Documentation** (including dictionary files under `/data/glossary/`, README files, and other non-code content)  
   Licensed under the **[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)**.  
   - You are free to share and adapt these materials, provided that:
     * You must give appropriate credit and link to the license.
     * **You may not use them for commercial purposes**.
     * Any derivative works must be distributed under the same license.

## 1. Project Vision: Translation Shouldn't Be a Barrier
Not everyone is fluent in eight languages.

And even if you are, you might not want to spend your after-work gaming time painstakingly translating a mod line by line.

The initial goal of this project is to simplify that process—to let you:

**See a mod you love, and with just a few clicks, be able to play it in your native language.**

This tool wasn't born to create "perfect" translations, but to ensure that language is no longer a barrier to the spread of creativity.

We hope that:
* Players can perform a one-click localization of great workshop mods, allowing them to enjoy the game even with a rough first draft.
* Multilingual creators can rapidly build first drafts, then focus on polishing and refinement, free from the shackles of repetitive labor.
* Local communities can participate in the global modding ecosystem with a much lower barrier to entry.

This is a tool to let creativity flow freely, a project in service of "expression, understanding, and re-creation."

In the age of Artificial Intelligence and Large Language Models, language should not and will not be a communication barrier between player communities.

***

## 2. Core Features

#### **Automated Translation Core**
* **Multi-API Support**: Supports various AI translation services like Gemini, OpenAI, and Qwen, allowing users to choose based on their needs.
* **Intelligent Glossary System**: Features a built-in, game-specific glossary manager that automatically identifies and injects relevant terms into API prompts, ensuring consistency and accuracy for game-specific terminology.
* **Robust Parser**: Includes a resilient parser specifically designed to handle various PDS `.yml` formats (e.g., `key:0 "value"`) to ensure all valid text is accurately extracted.
* **Intelligent Batch Processing (Chunking)**: When encountering large files, the script automatically splits the task into smaller batches to ensure the stability and success rate of API calls.
* **High-Fidelity Reconstruction**: Perfectly preserves the original file's indentation, comments, and complex key formats during file reconstruction.

#### **Multi-Game / Multi-Language Support**
* **Multi-Game Profiles**: Through a profile system in `config.py`, the tool can define different file structures, prompt templates, and processing rules for various PDS games (currently configured for Victoria 3 and Stellaris).
* **Many-to-Many Translation**: Supports selecting any of the officially supported languages as a source and translating to any other target language.
* **"One-to-All" Batch Mode**: Supports a one-click batch translation from a single source language to all other officially supported languages for that specific game. The number of supported languages varies by game:
  - Victoria 3: 11 official languages
  - Stellaris: 10 official languages  
  - Hearts of Iron IV: 9 official languages
  - Crusader Kings III: 8 official languages
  - Europa Universalis IV: 4 official languages

> **⚠️ Important Note on EU4**: Due to engine limitations in Europa Universalis IV, this project **does not support Chinese localization for EU4**. Its older engine version has fundamental differences in character encoding and file structure that cannot be correctly handled by this tool. While glossary support for EU4 is provided, the actual localization functionality is not available for CJK languages.
* **Dynamic File Generation**: Capable of generating game-compliant filenames (e.g., `..._l_french.yml`), file headers (e.g., `l_french:`), and folder names (e.g., `fr-ModName`) based on the selected target language and game.
* **Custom Target Language Support**: Provides a `[c] Custom/Disguise Other Language...` option in the target language menu, allowing users to create unofficial language packs or "disguised" language packs by specifying:
  - **Target Language Name**: For instructing the AI (e.g., `Italian`).
  - **Paradox Internal Language Key**: For the `.yml` file header (e.g., `l_italian`, or `l_english` for "disguise mode").
  - **Output Folder Prefix**: For the top-level folder name of the localization pack (e.g., `IT-`).

#### **Complete Mod Package Handling**
* **Recursive File Scanning**: Automatically traverses all subdirectories within the localization folder, ensuring no `.yml` files are missed.
* **Intelligent Metadata Processing**: Can automatically process and translate metadata files for both Victoria 3 (`.metadata/metadata.json`) and Stellaris-style games (`descriptor.mod`, generating both required files).
* **Asset Copying**: Automatically copies key assets defined in the game profile (e.g., `thumbnail.png`, `descriptor.mod`) to the localization folder.
* **Context-Aware Translation**: When processing metadata, the script reads the mod's name and allows the user to input additional thematic information, injecting this context into the prompt to improve the AI's translation accuracy.

#### **Internationalization & Workflow Management**
* **Bilingual UI (i18n)**: The script's own command-line interface supports both English and Chinese.
* **Intelligent Proofreading Progress Tracker**: Automatically generates a `proofreading_progress.csv` file, helping localizers track and manage their proofreading work.
* **Post-Processing Format Validation**: Automatically runs format validation after translation, detecting syntax errors, format issues, and tag pairing, generating detailed validation reports.
* **Safety Fallback Mechanism**: If an API call fails, a fallback file with the original text is automatically created to ensure the mod's integrity in-game.
* **Optional Source Directory Cleanup**: After all operations are successful, provides an optional cleanup function, precisely preserving only the necessary files as defined in the game profile.

***

## 3. Project Architecture

To ensure maintainability and scalability, the project adopts a clean, modular architecture:

```
scripts/
├── main.py                           # Main entry point / launcher
├── config.py                         # Global configuration (language db, API settings, etc.)
├── emergency_fix_chinese_punctuation.py # Emergency fix script for Chinese punctuation
│
├── core/                             # Core engine: reusable, low-level components
│   ├── api_handler.py                # API Handler Factory: Unified management of AI service interfaces
│   ├── openai_handler.py             # OpenAI Handler: OpenAI API interface
│   ├── gemini_handler.py             # Gemini Handler: Google Gemini API interface
│   ├── qwen_handler.py               # Qwen Handler: Alibaba Qwen API interface
│   ├── glossary_manager.py           # Glossary Manager: Loads and manages game-specific glossaries
│   ├── file_parser.py                # File Parser: Parses PDS-specific .yml format
│   ├── file_builder.py               # File Builder: Reconstructs localization files
│   ├── directory_handler.py          # Directory Handler: Manages folder structures
│   ├── asset_handler.py              # Asset Handler: Processes metadata and other assets
│   ├── proofreading_tracker.py       # Proofreading Tracker: Generates the progress CSV
│   ├── post_processing_manager.py    # Post-Processing Manager: Format validation & report generation ✨
│   ├── parallel_processor.py         # Parallel Processor: Multi-file concurrent processing
│   ├── scripted_loc_parser.py        # Scripted Parser: Script-driven localization parsing
│   ├── loc_parser.py                 # Localization Parser: Basic localization file parsing
│   └── llm/                          # LLM Module: Large Language Model related functionality
│
├── workflows/                        # Workflows: specific, high-level business logic
│   ├── initial_translate.py          # Initial Translation: Main translation workflow
│   ├── generate_workshop_desc.py     # Workshop Description: Generate Steam Workshop descriptions (TODO)
│   ├── publish_mod.py                # Mod Publishing: Publish mods to workshop (TODO)
│   ├── scrape_paratranz.py           # Paratranz Scraping: Fetch data from Paratranz (TODO)
│   └── update_translate.py           # Update Translation: Update existing translations (TODO)
│
├── hooks/                            # Hook System: Extend parser functionality
│   └── file_parser_hook.py          # File Parser Hook: Custom file parsing logic
│
└── utils/                            # Utilities: helper modules
    ├── post_process_validator.py     # Post-Processing Validator: Game-specific syntax rule validation ✨
    ├── punctuation_handler.py        # Punctuation Handler: Multi-language punctuation conversion
    ├── logger.py                     # Logger: Unified logging system
    ├── i18n.py                      # Internationalization: Multi-language UI support
    ├── text_clean.py                # Text Cleaner: Text preprocessing and cleaning
    └── report_generator.py          # Report Generator: Generate various reports (TODO)
```

***

## 4. How to Use

> **Note**: This quick start guide is primarily for users with some familiarity with Python and code. If you are completely new to API keys and environment variables, please refer to the `Beginner's Guide.md`.

### 4.1. Prerequisites

#### 🚀 Quick Setup (Recommended for Beginners)
1. **Install Python**: Ensure Python 3.8 or higher is installed on your system.
2. **Run Config Script**: Double-click the `Initial Setup.bat` file in the project's root directory.
3. **Follow Prompts**: Select your AI service, enter your API key, and the script will automatically install dependencies and configure your environment variable.

#### 📋 Manual Setup (For Experienced Users)
1. **Install Git**: Ensure [Git](https://git-scm.com/downloads) is installed.
2. **Install Python**: Ensure Python 3.8 or higher is installed.
3. **Install Dependencies**: 
    - For Gemini: `pip install --upgrade google-generativeai`
    - For OpenAI: `pip install -U openai`
    - For Qwen: `pip install -U dashscope`
4. **Set API Key**: Set the appropriate environment variable for your chosen API provider:
    - Gemini: `GEMINI_API_KEY`
    - OpenAI: `OPENAI_API_KEY`
    - Qwen: `DASHSCOPE_API_KEY`

### 4.2. Project Setup
1.  **Download/Clone Repository**: Get the project from GitHub.
2.  **Add Mod Source Files**: Place the complete folder of the mod you wish to process into the `source_mod/` directory.
    - **Recommendation**: Rename the mod folder from its workshop ID (a long number) to the mod's actual name to avoid confusion.
    - **Note**: Ensure the entire mod folder structure is intact. A typical structure for a mod named "ABCDEF" would be:
    ```
    V3_Mod_Localization_Factory/
    ├── source_mod/                    # <-- Source Mod Folder
    │   └── ABCDEF/                    # <-- Your target mod folder
    │       ├── descriptor.mod         # <-- Mod descriptor file (Stellaris)
    │       ├── thumbnail.png          # <-- Mod thumbnail
    │       ├── localisation/          # <-- Localization folder (Stellaris)
    │       │   └── english/           # <-- English localization files
    │       │       └── ABCDEF_l_english.yml
    │       ├── .metadata/             # <-- Metadata folder (Victoria 3)
    │       │   └── metadata.json     # <-- Metadata file
    │       ├── common/                # <-- Mod content folders (not relevant for localization)
    │       └── ... (other mod files)
    ├── scripts/                       # <-- Script folder
    └── data/                          # <-- Data folder
    ```
3.  **Configure Glossary** (Optional): Place game-specific glossary files in the `data/glossary/` directory to significantly improve translation quality.
    - Victoria 3: `data/glossary/victoria3/glossary.json`
    - Stellaris: `data/glossary/stellaris/glossary.json`

### 4.3. Running the Script
1.  Open a terminal in the project's **root directory**.
2.  For Windows users: double-click `run.bat`.
3.  Follow the on-screen prompts to select, in order: **UI Language -> API Provider -> Target Game -> Target Mod -> Cleanup Option -> Source Language -> Target Language -> (Optional) Mod Theme Input**.

### 4.4. Enabling the Mod (Victoria 3)
1.  After the script finishes, find the output in the `my_translation/` folder (e.g., `zh-CN-ABCDEFG`). This folder will also contain a proofreading tracker CSV file.
2.  Copy this folder and paste it into `Documents/Paradox Interactive/Victoria 3/mod`.
3.  The correct structure should look like this:
    ```
    Victoria 3/
    └── mod/
        └── zh-CN-ABCDEFG/            # <-- Main mod folder
            ├── .metadata/            # <-- V3 metadata folder
            │   └── metadata.json     # <-- Metadata file read by the game
            ├── thumbnail.png         # <-- Mod thumbnail
            ├── proofreading_tracker.csv # <-- Proofreading progress file
            └── localization/         # <-- Localization folder (note the spelling)
                └── simp_chinese/
                    └── ... (All .yml files are here)
    ```                
4.  Restart Victoria 3, add the new mod to your playset, and ensure it is placed **below** the original mod in the load order.
5.  Enjoy!

### 4.5. Enabling the Mod (Stellaris & Hearts of Iron IV)
1.  After the script finishes, find the output folder (e.g., `zh-CN-ABCDEFG`) and a corresponding `.mod` file (e.g., `zh-CN-ABCDEFG.mod`) in the `my_translation/` directory.
2.  Copy **both the folder and the `.mod` file** into `Documents/Paradox Interactive/Stellaris/mod`.
3.  The correct structure should look like this:
    ```
    Stellaris/
    └── mod/
        ├── zh-CN-ABCDEFG/            # <-- Main mod folder
        │   ├── descriptor.mod        # <-- Metadata file read by the game
        │   ├── thumbnail.png         # <-- Mod thumbnail
        │   ├── proofreading_tracker.csv # <-- Proofreading progress file
        │   └── localisation/         # <-- Localization folder
        │       └── simp_chinese/
        │           └── ... (All .yml files are here)
        │
        └── zh-CN-ABCDEFG.mod         # <-- .mod file read by the launcher, points to the folder above
    ```
4.  Restart the game, add the new mod to your playset, and ensure it is placed **below** the original mod in the load order.
5.  Enjoy!

***

## 5. Glossary System

### 5.1. Overview
The glossary system is a core feature that:
- **Automatically identifies terms**: Scans text during translation to find relevant game-specific terminology.
- **Injects prompts**: Injects the terms as high-priority instructions into the AI translation request.
- **Ensures consistency**: Guarantees that the same term is translated identically across all files.
- **Supports bidirectional translation**: Correctly identifies and applies terms regardless of the source or target language.

### 5.2. Glossary File Structure
The glossary files use a JSON format like this:
```json
{
  "metadata": {
    "description": "Victoria 3 Game and Mod Community Glossary",
    "last_updated": "2024-01-01",
    "sources": ["Official Translation", "Community Translation", "Mod Translation"]
  },
  "entries": [
    {
      "id": "victoria3_convoy",
      "translations": {
        "en": "convoy",
        "zh-CN": "船队"
      },
      "metadata": {
        "pos": "noun",
        "remarks": "Produced by ports, maintains the nation's shipping lanes."
      },
    }
  ]
}
```
### 5.3. Glossary File Locations
- **Victoria 3**: `data/glossary/victoria3/glossary.json`
- **Stellaris**: `data/glossary/stellaris/glossary.json`
- **Other Games**: You can create corresponding game folders under `data/glossary/`

### 5.4. Glossary Effect Example
**Before using the glossary**: The AI might translate "convoy" into various different terms like "escort," "convoy," or "fleet."
**After using the glossary**: The AI will strictly follow the glossary's rule and uniformly translate "convoy" as "船队" (fleet), ensuring term consistency.

### 5.5. Glossary Sources & Acknowledgements

The game-specific glossaries in this project are built upon the data from the following excellent official and community localization projects. We extend our sincerest gratitude to all the original contributors!

#### **Victoria 3 Glossary Sources**
* **Victoria 3 Chinese Localization Update V1.2**: The official localization update, containing the latest game terminology.
* **Morgenröte | Chinese Language**: A community localization project.
* **Better Politics Mod Simplified Chinese Localization**: A dedicated glossary from the political systems mod.
* **"Milk" Localization**: A community localization project providing an extensive list of game terms.

#### **Stellaris Glossary Sources**
* **"Pigeon Group" (鸽组) Chinese Glossary**: A well-known Stellaris localization group providing high-quality sci-fi terminology.
* **Shrouded Regions Chinese Glossary**: A glossary focused on terms for mysterious regions and special events.
* **L-Network Stellaris Mod Localization Collection Glossary**: A comprehensive glossary covering content from multiple Stellaris mods.

#### **Other Game Glossary Sources**
Currently, the glossaries for EU4, HOI4, and CK3 are basic examples containing only a small number of core terms. They serve primarily to:
- Validate the functionality of the glossary system.
- Demonstrate the standard format for glossary files.
- Provide a foundational structure for future expansion.

***

## 6. Collaboration & Future Plans
This is an open-source project that has grown through your feedback and my assistance. We have already planned many exciting features for the future, which have been created as Issues on GitHub.

We welcome all forms of feedback, suggestions, and code contributions!