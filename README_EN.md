> **中文用户请注意:** 本项目是一个基于Python和AI的P社游戏Mod自动化本地化工作流。
>
> **[点击此处阅读中文版README](README.md)**

[hr][/hr]

# Paradox Mod Localization Factory

> Say goodbye to copy-paste, embrace automation. This project provides a powerful, semi-automated localization workflow for Paradox Interactive (PDS) game mods (e.g., Victoria 3, Stellaris).

## 1. Project Overview

This project is a modular, automated translation workflow based on Python and the Google Gemini API. Its core objective is to fully automate the initial "first pass" (from 0 to 1) of mod localization. It compresses the traditionally labor-intensive and repetitive work into a few minutes of machine processing, freeing up localizers to focus on the "1 to 100" tasks of proofreading, polishing, and quality assurance.

## 2. Core Features

Our "Galactic Battleship" has undergone multiple iterations and refactoring, and currently possesses the following core features:

#### **Automated Translation Core**
* **Powered by Gemini API:** Utilizes a powerful Large Language Model to provide high-quality first-draft translations.
* **Robust Parser:** Features a resilient parser specifically designed to handle various PDS `.yml` formats (e.g., `key:0 "value"`) to ensure all valid text is accurately extracted.
* **Intelligent Batch Processing (Chunking):** When encountering large files with hundreds or thousands of text entries, the script automatically splits the task into smaller batches to ensure the stability and success rate of API calls.
* **High-Fidelity Reconstruction:** Perfectly preserves the original file's indentation, comments, and complex key formats during file reconstruction.

#### **Multi-Language Support**
* **Many-to-Many Translation:** Supports selecting any of the 11 officially supported Victoria 3 languages as a source and translating to any other target language.
* **"One-to-All" Batch Mode:** Supports a one-click batch translation from a single source language to all 10 other supported languages, automatically creating corresponding folders and files.
* **Dynamic File Generation:** Capable of generating game-compliant filenames (e.g., `..._l_french.yml`) and file headers (e.g., `l_french:`) based on the selected target language.
* **Dynamic Folder Naming:** In single-language mode, output folders are named according to the target language (e.g., `FR-ModName`, `汉化-ModName`); in batch mode, they are uniformly named `Multilanguage-ModName`.

#### **Complete Mod Package Handling**
* **Recursive File Scanning:** Automatically traverses all subdirectories within the `localization` folder, ensuring no `.yml` files are missed.
* **Metadata Localization:** Automatically processes the `.metadata/metadata.json` file, translating the mod's name and short description.
* **Asset Copying:** Automatically copies the source mod's thumbnail (`thumbnail.png`) to the localization directory.

#### **Internationalization & Workflow Management**
* **Bilingual UI (i18n):** The script's own command-line interface supports both English and Chinese.
* **Safety Fallback Mechanism:** If an API call fails or returns an abnormal result, a fallback file with the original English text is automatically created. This ensures the mod's integrity in-game and prevents crashes due to missing localization entries.
* **Optional Source Directory Cleanup:** After all operations are successful, provides an optional cleanup function to delete non-essential gameplay files from the source mod folder to save disk space.

## 3. Project Architecture

To ensure maintainability and scalability, the project adopts a clean, modular architecture:
```
scripts/
├── main.py                 # Main entry point / launcher
├── config.py               # Global configuration
│
├── core/                   # Core engine: reusable, low-level components
│   ├── __init__.py
│   ├── api_handler.py
│   ├── file_parser.py
│   ├── file_builder.py
│   ├── directory_handler.py
│   └── asset_handler.py
│
├── workflows/              # Workflows: specific, high-level business logic
│   ├── __init__.py
│   └── initial_translate.py
│
└── utils/                  # Utilities: helper modules
    ├── __init__.py
    └── i18n.py
```
## 4. How to Use

### 4.1. Prerequisites
1.  **Install Git:** Ensure [Git](https://git-scm.com/downloads) is installed on your system.
2.  **Install Python:** Ensure Python 3.8 or a higher version is installed.
3.  **Install Dependencies:** Run `pip install --upgrade google-generativeai` in your terminal.
4.  **Set API Key:** Set an environment variable named `GEMINI_API_KEY` with your API key.

### 4.2. Project Setup
1.  **Initialize Repository:** Open a terminal in the project's root directory and run `git init`.
2.  **Add Mod Source Files:** Place the complete folder of the mod you wish to process into the `source_mod/` directory.
3.  **Create Version Snapshot:** Run `git add .` and `git commit -m "Initial commit"`.

### 4.3. Running the Script
1.  Open a terminal in the project's **root directory**.
2.  Run the command: `python scripts/main.py`
3.  Follow the on-screen prompts to select, in order: **UI Language -> Target Mod -> Cleanup Option -> Source Language -> Target Language**.

## 5. Important Notes
* **Git Commits:** It is highly recommended to commit your changes frequently.
* **File Encoding:** The script is configured to handle the required file encodings (`utf-8-sig` for reading, `utf-8-bom` for writing) to ensure compatibility with the game engine.
* **API Key:** Never hardcode your API key in the script. Using environment variables is the best practice for security.