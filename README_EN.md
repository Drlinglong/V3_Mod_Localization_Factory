> **中文用户请注意:** 本项目是一个基于Python和AI的P社游戏Mod自动化本地化工作流，支持多游戏配置、多语言互译，并为高扩展性而设计。
>
> **[点击此处阅读中文版README](README.md)**

***

# Paradox Mod Localization Factory

> Say goodbye to copy-paste, embrace automation. This project provides a powerful, semi-automated localization workflow for Paradox Interactive (PDS) game mods (e.g., Victoria 3, Stellaris).

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
* **Powered by Gemini API:** Utilizes a powerful Large Language Model to provide high-quality first-draft translations.
* **Robust Parser:** Features a resilient parser specifically designed to handle various PDS `.yml` formats (e.g., `key:0 "value"`) to ensure all valid text is accurately extracted.
* **Intelligent Batch Processing (Chunking):** When encountering large files with hundreds or thousands of text entries, the script automatically splits the task into smaller batches to ensure the stability and success rate of API calls.
* **High-Fidelity Reconstruction:** Perfectly preserves the original file's indentation, comments, and complex key formats during file reconstruction.

#### **Multi-Game / Multi-Language Support**
* **Multi-Game Profiles:** Through a profile system in `config.py`, the tool can define different file structures, prompt templates, and processing rules for various PDS games (currently configured for Victoria 3 and Stellaris).
* **Many-to-Many Translation:** Supports selecting any of the 11 officially supported languages as a source and translating to any other target language.
* **"One-to-All" Batch Mode:** Supports a one-click batch translation from a single source language to all 10 other supported languages.
* **Dynamic File Generation:** Capable of generating game-compliant filenames (e.g., `..._l_french.yml`), file headers (e.g., `l_french:`), and folder names (e.g., `fr-ModName`) based on the selected target language and game.

#### **Complete Mod Package Handling**
* **Recursive File Scanning:** Automatically traverses all subdirectories within the localization folder, ensuring no `.yml` files are missed.
* **Intelligent Metadata Processing:** Can automatically process and translate metadata files for both Victoria 3 (`.metadata/metadata.json`) and Stellaris (`descriptor.mod`, generating both required files).
* **Asset Copying:** Automatically copies key assets defined in the game profile (e.g., `thumbnail.png`, `descriptor.mod`) to the localization folder.
* **Context-Aware Translation:** When processing metadata, the script reads the mod's name and allows the user to input additional thematic information, injecting this context into the prompt to improve the AI's translation accuracy.

#### **Internationalization & Workflow Management**
* **Bilingual UI (i18n):** The script's own command-line interface supports both English and Chinese.
* **Safety Fallback Mechanism:** If an API call fails, a fallback file with the original text is automatically created to ensure the mod's integrity in-game.
* **Optional Source Directory Cleanup:** After a successful run, provides an optional cleanup function, precisely preserving only the necessary files as defined in the game profile.

***

## 3. Project Architecture

To ensure maintainability and scalability, the project adopts a clean, modular architecture:

```
scripts/
├── main.py                 # Main entry point / launcher
├── config.py               # Global configurations (language database, API settings, etc.)
│
├── core/                   # Core engine: reusable, low-level components
│   ├── api_handler.py
│   ├── file_parser.py
│   ├── file_builder.py
│   ├── directory_handler.py
│   └── asset_handler.py
│
├── workflows/              # Workflows: specific, high-level business logic
│   └── initial_translate.py
│
└── utils/                  # Utilities: helper modules
    └── i18n.py
```

***

## 4. How to Use

### 4.1. Prerequisites
1.  **Install Git:** Ensure [Git](https://git-scm.com/downloads) is installed on your system.
2.  **Install Python:** Ensure Python 3.8 or a higher version is installed.
3.  **Install Dependencies:** Run `pip install --upgrade google-genai` in your terminal.
4.  **Set API Key:** Set an environment variable named `GEMINI_API_KEY` with your API key.

### 4.2. Project Setup
1.  **Download/Clone Repository:** Download this project from GitHub.
2.  **Add Mod Source Files:** Place the complete folder of the mod you wish to process into the `source_mod/` directory.

### 4.3. Running the Script
1.  Open a terminal in the project's **root directory**.
2.  Run the command: `python scripts/main.py`
3.  Follow the on-screen prompts to select, in order: **UI Language -> Target Game -> Target Mod -> Cleanup Option -> Source Language -> Target Language -> (Optional) Mod Theme Input**.

### 4.4. Enabling the Mod (Victoria 3)
1.  After the script finishes, you will find the output in the `my_translation/` folder. The folder name will vary based on your selection (e.g., `zh-CN-ABCDEFG`).
2.  Copy this folder and paste it into your game's mod directory: `Documents/Paradox Interactive/Victoria 3/mod`. (If the `mod` folder doesn't exist, create it.)
3.  The final, correct folder structure should look like this:
    ```
    Victoria 3/
    └── mod/
        └── zh-CN-ABCDEFG/            # <-- This is the main mod folder
            ├── .metadata/            # <-- V3 metadata folder
            │   └── metadata.json     # <-- Metadata file read by the game
            ├── thumbnail.png         # <-- Mod thumbnail
            └── localization/         # <-- Localization folder (note the spelling)
                └── simp_chinese/
                    └── ... (All .yml files are here)
    ```                
4.  Restart Victoria 3 and open the launcher. Add the mod to your desired playset.
5.  Enable the mod and ensure it is placed **below** the original mod in the load order. Select the playset and launch the game.
6.  Enjoy!

### 4.5. Enabling the Mod (Stellaris)
1.  After the script finishes, you will find an output folder (e.g., `zh-CN-ABCDEFG`) and a corresponding `.mod` file (e.g., `zh-CN-ABCDEFG.mod`) in the `my_translation/` directory.
2.  Copy **both the folder and the `.mod` file** and paste them into your game's mod directory: `Documents/Paradox Interactive/Stellaris/mod`. (If the `mod` folder doesn't exist, create it.)
3.  The final, correct folder structure should look like this:
    ```
    Stellaris/
    └── mod/
        ├── zh-CN-ABCDEFG/            # <-- This is the main mod folder
        │   ├── descriptor.mod        # <-- Metadata file read by the game
        │   ├── thumbnail.png         # <-- Mod thumbnail
        │   └── localisation/         # <-- Localization folder
        │       └── simp_chinese/
        │           └── ... (All .yml files are here)
        │
        └── zh-CN-ABCDEFG.mod         # <-- .mod file read by the launcher, points to the folder above
    ```
4.  Restart Stellaris and open the launcher. Add the mod to your desired playset.
5.  Enable the mod and ensure it is placed **below** the original mod in the load order. Select the playset and launch the game.
6.  Enjoy!

***

## 5. Collaboration & Future Plans
This is an open-source project that has grown through your feedback and my assistance. We have already planned many exciting features for the future (such as custom glossaries, incremental updates, one-click workshop publishing, etc.), which have been created as Issues on GitHub.

We welcome all forms of feedback, suggestions, and code contributions!