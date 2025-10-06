# Frequently Asked Questions (FAQ)

Welcome to Project Remis! This FAQ aims to help "novice users" quickly get started with this tool and solve common problems they may encounter during use.

## 1. Installation and Startup

### Q1.1: How to download and extract Project Remis?
**A:** Please go to the project's release page (usually on GitHub Releases or other download platforms) to download the latest **Portable** compressed package (e.g., `Project_Remis_vX.X.X.zip`). After downloading, extract it to any location on your computer.

### Q1.2: What are `setup.bat` and `run.bat` for?
**A:**
*   `setup.bat`: This is the script you need to run **for the first time**. It automatically installs the project's dependencies and guides you to set the API Key for the AI translation service as an environment variable. You only need to run it once.
*   `run.bat`: This is the script you need to run **each time** you start Project Remis for localization. Double-click it to launch the localization program.

### Q1.3: Why do I need an API Key? How to obtain and set it?
**A:** Project Remis itself does not provide translation capabilities; it is an "AI translation porter." You need to use your own AI service's (e.g., Gemini, OpenAI, etc.) API Key for translation.
*   **How to obtain**: Please go to the official website of your chosen AI service provider to register an account and obtain an API Key.
*   **How to set**: When you run `setup.bat` for the first time, the program will prompt you to enter the API Key. After you enter it, it will be securely set as an environment variable, without you needing to configure it manually.
*   ⚠️ **Important Reminder**:
- Applying for an API key requires registering an account and binding a bank card.
- Using the API may incur costs, subject to the service provider's billing terms.
- Please **keep your API key safe**, otherwise your bank card may be overcharged.

### Q1.4: What is an environment variable?

**Environment variables** sound professional, but they are actually just "settings":

**Simple understanding**:
- Your computer has many "settings".
- Such as language settings, time zone settings, etc.
- An environment variable tells the program "what your API key is".
- This way, the program can automatically use your key without you having to enter it every time.

**Why are environment variables needed?**
- Security: Avoid accidental disclosure of keys.
- Convenience: Set it once, and you don't need to set it again later.
- Professionalism: This is standard practice.
   
**How do I set environment variables?**
- `setup.bat` will prompt you to enter the API key during its execution. After you enter the API key, the script will automatically set and store the environment variable in your system.
- Therefore, in most cases, you only need to execute it once, and then you can continue to use that API key for translation on the same computer.
- If your API key expires, or you want to use a new key for translation, you need to re-execute `setup.bat` to set it.

## 2. Mod Placement and Recognition

### Q2.1: Where should I put the Mod files I want to localize?
**A:** After extracting Project Remis, you will see a folder named `source_mod`. Please copy and paste the entire Mod folder you want to localize into `source_mod`.

### Q2.2: Why is it recommended to rename Mod folders?
**A:** Mod folders downloaded from the workshop usually have a name consisting of a string of numbers (e.g., `3535929411`). For easier identification and management, it is strongly recommended that you rename it to the Mod's actual name (e.g., `Extended Timeline`).

### Q2.3: What if the program cannot recognize the Mod I placed?
**A:**
1.  Please ensure that you have copied the entire Mod folder completely into the `source_mod` directory, not just a part of it.
2.  Check if the Mod folder structure conforms to the standard Mod structure of Paradox games.
3.  Try restarting `run.bat`.

## 3. Translation Process

### Q3.1: How to select games, Mods, languages, and AI services?
**A:** After running `run.bat`, the program will prompt you in Chinese to make selections step by step:
*   Select the game you want to play (e.g., Victoria 3, Stellaris).
*   Select the Mod you want to localize.
*   Select the original language of the Mod and the target language you want to translate it into.
*   Select the AI translation service you want to use.
*   Enter the Mod's theme or keywords as prompted, which helps the AI better understand the context.

### Q3.2: What is a glossary? What is its use?
**A:** A glossary is like a "game terminology cheat sheet." It contains specific proper nouns and terms unique to the game (e.g., "convoy," "ideology"). During translation, the AI will strictly follow the translations in the glossary to handle these terms, ensuring the professionalism and consistency of the entire Mod's translation, avoiding the stiffness of machine translation.

### Q3.3: After translation, where is the localized Mod?
**A:** After successful translation, the localized Mod package will automatically appear in the `my_translation` folder in the Project Remis root directory.

## 4. Enabling the Mod in Game

### Q4.1: How to copy the localized Mod to the game directory?
**A:** Go to the `my_translation` folder and find the newly generated localized Mod package (e.g., `zh-CN-Your Mod Name`). Copy this entire folder to the corresponding `mod` directory of your game.
*   **Victoria 3**: `C:\Users\YourUsername\Documents\Paradox Interactive\Victoria 3\mod`
*   **Stellaris**: `C:\Users\YourUsername\Documents\Paradox Interactive\Stellaris\mod`
*   **Hearts of Iron IV**: `C:\Users\YourUsername\Documents\Paradox Interactive\Hearts of Iron IV\mod`
*   **Crusader Kings III**: `C:\Users\YourUsername\Documents\Paradox Interactive\Crusader Kings III\mod`

### Q4.2: How to enable the Mod in the game launcher?
**A:** Launch the game launcher, go to the "Playsets" or "Mod Management" interface. You need to enable both the **Original Mod** and the **Localized Mod**.

### Q4.3: Why is the loading order of the localized Mod important?
**A:** **This is a crucial step!** In the game launcher, please ensure that the **Localized Mod** is sorted **below** the Original Mod in the list. This way, the localized Mod can correctly overwrite the original Mod's text, making the translation effective.

### Q4.4: What are fake localization (fake Chinese) files? Why should I delete them?
**A:** Paradox game localization files are stored in subfolders under `localization` according to different languages. For example, Victoria 3 supports 11 official languages, so the original game has eleven localization subfiles. They are stored in subfolders such as `french`, `japanese`, `simp_chinese`, `english`, etc.
*   However, most mod authors are unable to create multi-language localization patches for their mods. Therefore, they adopt a clever strategy: they modify the file headers to allow clients of other languages to **read their original localization files**.
*   For example, when you load an English mod in a Chinese client and see some **English localization content**, what you are seeing is a "fake Chinese file."
*   Because without this method, you would see a series of extremely abstract key values with underscores, making it almost **impossible to play normally**. By adding "fake Chinese," players who do not use localization patches can **barely** play the game through mental translation or external translators.
*   However, since these fake localization files are located in the original mod path, their reading priority is often **higher** than that of the localized mod. If we want to use the real localization files created by this project, they **must be deleted**.
*   You need to manually delete these files.
    - Please go to `SteamLibrary\steamapps\workshop\content\[Game ID]\[Mod Workshop ID]\localization`.
    - **Delete all folders except the original language folder of the Mod** (e.g., if the original mod is English, delete all folders under `localization` except the `english` folder).
    - Alternatively, you can choose to **directly overwrite** the content of this localization patch into the original MOD folder. This can reduce annoying verification processes, and Steam will no longer try to re-download missing fake localization files from the workshop.

## 5. Common Issues and Troubleshooting

### Q5.1: What if the program crashes or reports an error?
**A:**
*   **API Key Issue**: Please check if your API Key is correct, valid, and if your AI account balance is sufficient.
*   **Incomplete Mod Files**: Please ensure you have copied the entire Mod folder to `source_mod`, not just the `localization` folder within it.
*   **Check Logs**: The program will generate log files in the `logs/` directory, which may contain detailed error messages that can help you pinpoint the problem.

### Q5.2: What if the translation does not take effect in the game?
**A:**
1.  **Check Loading Order**: Reconfirm that the loading order of the localized Mod in the game launcher is **below** the Original Mod.
2.  **Delete "Fake Localization Files"**: Some Mods may come with empty or incomplete localization files, which will prevent your localized Mod from taking effect.
    *   Please go to `SteamLibrary\steamapps\workshop\content\[Game ID]\[Mod Workshop ID]\localization`.
    *   **Delete all folders except the original language folder of the Mod** (e.g., if the original mod is English, delete all folders under `localization` except the `english` folder).
    *   Alternatively, you can choose to **directly overwrite** the content of this localization patch into the original MOD folder. This can reduce annoying verification processes, and Steam will no longer try to re-download missing fake localization files from the workshop.
3.  **Check for Other Mod Conflicts**: Try enabling only the Original Mod and the Localized Mod to rule out interference from other Mods.

### Q5.3: What if the translation quality is poor?
**A:**
1.  **Optimize Glossary**: You can try adding or modifying glossary files for the corresponding game in the `data/glossary` folder, which can significantly improve the accuracy of terminology.
2.  **Provide Mod Theme**: When starting the translation, entering the Mod's theme or keywords as prompted can also help the AI better understand the context and provide more appropriate translations.

### Q5.4: What if the API Key is invalid or the quota is insufficient?
**A:**
*   **Invalid/Incorrect**: Please carefully check if your API Key is correct and ensure there are no extra spaces or characters.
*   **Insufficient Quota**: This means you may have used up your AI service's free tier or paid quota. You can try waiting for the quota to refresh, or upgrade your AI service plan.
*   **Network Issues**: Ensure your network connection is stable and you can access the AI service's servers normally.

### Q5.5: What if I have other questions or want to add new features?
**A:** We welcome your feedback and suggestions!
*   **Ask Questions or Report Bugs**: If you encounter any problems, program bugs, or have questions about the documentation during use, please feel free to submit an Issue in the project's GitHub repository.
*   **Suggest New Features**: If you have any new features you'd like to see added or suggestions for improvement, please also submit them as a GitHub Issue.
When submitting an Issue, please provide as much detailed information as possible, such as: problem description, reproduction steps, error screenshots, your system environment, etc. This will help us understand and resolve the issue more quickly.

---
