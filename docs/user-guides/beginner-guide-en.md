# 🚀 A Beginner's Guide

> **Welcome to the Paradox Mod Localization Factory!** > If you have no programming knowledge and don't know what an API or an environment variable is, don't worry! This guide is made for you.

## 📖 Table of Contents

- [What is this project?](#what-is-this-project)
- [What do I need?](#what-do-i-need)
- [What is an API?](#what-is-an-api)
- [How do I get an API Key?](#how-do-i-get-an-api-key)
- [What is an Environment Variable?](#what-is-an-environment-variable)
- [Detailed Installation Steps](#detailed-installation-steps)
- [Enabling the Mod in Your Game](#enabling-the-mod-in-your-game)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)

## 🎯 What is this project?

The **Paradox Mod Localization Factory** is an automation tool that helps you:
- Automatically translate English game mods into Chinese (or other languages).
- Supports multiple Paradox games (Victoria 3, Stellaris, Hearts of Iron IV, etc.).
- Uses Artificial Intelligence for translation, which is much better than traditional machine translation.
- Generates a complete, ready-to-use localization mod pack with a single click.

**In simple terms**: You provide an English mod, and the tool automatically translates it for you. Then, you can play the mod in your native language!

## 🛠️ What do I need?

Before you begin, you will need:

1. **A PC** (Windows 10/11)
2. **An internet connection** (for downloading and API calls)
3. **An account with an AI translation service** (Gemini is recommended as it's simple and has a free tier)
4. **Patience** (the first-time setup might take around 30 minutes)

## 🤖 What is an API?

**API** sounds complicated, but it's actually simple:

**Imagine this**:
- You have a very smart friend in another country.
- You want to chat with them but don't speak their language.
- You need a translator to help you communicate.
- **An API provider is that translator.**

**In our project**:
- You have a lot of English game text that needs to be translated.
- There are many API providers online (like Google's Gemini) that can translate it for you.
- But these providers need a "pass" to work for you.
- That "pass" is the **API Key**.

## 🔑 How do I get an API Key?

We support three AI translation services. You can choose one based on your needs:

### 1. Google Gemini (Recommended)
- **Model**: Uses the Gemini 2.5 Flash model
- **Features**: High translation quality, fast performance
- **Requires**: A Google account
- **Steps to get the key**:
  1. Visit [Google AI Studio](https://aistudio.google.com/)
  2. Log in with your Google account
  3. Follow the prompts to create a new API key
  4. Copy the generated API key

### 2. OpenAI GPT
- **Model**: Uses the GPT-5 Mini model
- **Features**: Extremely high translation quality
- **Requires**: An OpenAI account
- **Steps to get the key**:
  1. Visit the [OpenAI Platform](https://platform.openai.com/)
  2. Sign up or log in to your account
  3. Follow the prompts to create a new API key
  4. Copy the generated API key

### 3. Alibaba Cloud Qwen (Tongyi Qianwen)
- **Model**: Uses the Qwen Plus model
- **Features**: A domestic AI service, providing a direct connection for users in China
- **Requires**: An Alibaba Cloud account
- **Recommendation**: Recommended for users in Mainland China.
- **Steps to get the key**:
  1. Visit [Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/)
  2. Log in with your Alibaba Cloud account
  3. Follow the prompts to create an API key
  4. Copy the generated API key

⚠️ **Important Reminder**:
- You will likely need to register an account and may need to add a payment method (like a credit card) to get an API key.
- Using the API may incur costs, depending on the provider's terms and your usage.
- Please keep your API key safe and private. If it leaks, others could use it and generate costs on your account.

## 🌍 What is an Environment Variable?

**Environment Variable** sounds professional, but it's just a "setting" on your computer:

**Simple Explanation**:
- Your computer has many "settings," like language and time zone.
- An environment variable is a setting that tells programs "here is your API key."
- This way, the program can automatically use your key without you having to type it in every time.

**Why do we use it?**
- **Security**: It prevents your key from being accidentally saved in a public file.
- **Convenience**: Set it once, and it works forever.
- **Professionalism**: This is the standard, correct way to handle secret keys.

## 📥 Detailed Installation Steps

### Step 1: Download the Project Files

1. **Download the project**:
   - Go to the project's GitHub page.
   - Click the green "<> Code" button.
   - Select "Download ZIP".
   - After the download is complete, unzip it to a folder you can easily find.
   - For example: `C:\Users\YourName\Desktop\V3_Mod_Localization_Factory-main`

2. **Check the files**:
   - After unzipping, you should see a folder named `V3_Mod_Localization_Factory-main`.
   - Inside, there should be files like `run.bat`, `README.md`, etc.

### Step 2: Install Python

1. **Download Python**:
   - Visit the [official Python website](https://www.python.org/downloads/).
   - Click "Download Python 3.x.x" (the latest version is fine).
   - Run the installer after it downloads.

2. **Install Python**:
   - **IMPORTANT**: During installation, check the box that says **"Add Python to PATH"**.
   - Click "Install Now".
   - Wait for the installation to finish.

3. **Verify Installation**:
   - Press `Win + R`, type `cmd`, and press Enter.
   - In the black command window, type: `python --version`
   - If it shows a version number (e.g., `Python 3.12.0`), the installation was successful.

### Step 3: Install Libraries & Configure API

**If you are a beginner, using the automatic setup script is recommended**:
1. Find the `Initial Setup.bat` file in the project folder.
2. Double-click to run it.
3. Follow the prompts to select your AI service.
4. Paste in your API key when asked.
5. The script will automatically install the necessary libraries and configure the environment variable for you.

### Step 4: Prepare the Mod Files

1. **Get the Mod**:
   - Download the mod you want to translate from the Steam Workshop.
   - You can easily find the mod files by opening the game launcher (Stellaris, HOI4, V3), finding the mod in your playset, and clicking the "Show in folder" option.
   - Or, get the mod files from another source.

2. **Place the Mod Files**:
   - Copy the entire mod folder into the project's `source_mod` directory.
   - **Recommendation**: It's a good idea to rename the mod folder from its workshop ID (a long number) to the mod's actual name to avoid confusion.
   - **Note**: Ensure the entire mod folder structure is intact. An example structure is shown below:
    ```
    V3_Mod_Localization_Factory-main/
    ├── source_mod/                    # <-- Source Mod Folder
    │   └── ABCDEF/                    # <-- This is the mod you want to localize
    │       ├── descriptor.mod         # <-- Mod descriptor file (Stellaris)
    │       ├── thumbnail.png          # <-- Mod thumbnail
    │       ├── localisation/          # <-- Localization folder (Stellaris)
    │       │   └── english/           # <-- English localization files
    │       │       └── ABCDEF_l_english.yml
    │       ├── .metadata/             # <-- Metadata folder (Victoria 3)
    │       │   └── metadata.json     # <-- Metadata file
    │       └── ... (other mod files)
    ├── scripts/                       # <-- Script folder
    └── data/                          # <-- Data folder
    ```

### Step 5: Run the Program

1. **Double-click to run**:
   - Find the `run.bat` file in the project folder.
   - Double-click it.

2. **Follow the prompts**:
   - Select the UI language.
   - Select your API provider.
   - Select the game type.
   - Select the mod you want to translate.
   - Choose whether to clean up unnecessary files.
   - Select the source and target languages.

3. **Wait for the translation to complete**:
   - The program will start translating automatically.
   - This process can take anywhere from a few minutes to over an hour, depending on the size of the mod.
   - Please be patient and do not close the program.

## 🎮 Enabling the Mod in Your Game

### Enabling for Victoria 3
1. **Find the output**: After localization is complete, you will find the output in the `my_translation` folder (e.g., a folder named `zh-CN-ABCDEFG`).
2. **Copy to game directory**: Copy this folder and paste it into `Documents/Paradox Interactive/Victoria 3/mod`. (If the `mod` folder doesn't exist, create it.)
3. **Correct folder structure**:
   ```
   Victoria 3/
   └── mod/
       └── zh-CN-ABCDEFG/            # <-- Main mod folder
           ├── .metadata/            # <-- V3 metadata folder
           │   └── metadata.json     # <-- Metadata file read by the game
           ├── thumbnail.png         # <-- Mod thumbnail
           ├── proofreading_tracker.csv # <-- Proofreading progress file
           └── localization/         # <-- Localization folder
               └── simp_chinese/
                   └── ... (All .yml files are here)
   ```
4. **Enable the mod**: Restart Victoria 3, add the mod to your playset, and ensure it is placed **below** the original mod in the load order. Have fun!

### Enabling for Stellaris & Hearts of Iron IV
1. **Find the output**: Find the output folder (e.g., `zh-CN-ABCDEFG`) and a corresponding `.mod` file (e.g., `zh-CN-ABCDEFG.mod`) in the `my_translation` folder.
2. **Copy to game directory**: Copy **both the folder and the `.mod` file** into the game's mod directory (e.g., `Documents/Paradox Interactive/Stellaris/mod`).
3. **Correct folder structure**:
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
       └── zh-CN-ABCDEFG.mod         # <-- .mod file read by the launcher
   ```
4. **Enable the mod**: Restart the game, add the mod to your playset, and ensure it is placed **below** the original mod in the load order. Have fun!

## ❓ Frequently Asked Questions (FAQ)

### Q1: The program says "Python not found." What do I do?
**A**: This means Python was not installed correctly or not added to the PATH. Please reinstall Python and make sure to check the "Add Python to PATH" box.

### Q2: It says "pip is not recognized as an internal or external command."
**A**: This also points to an incorrect Python installation. Please try reinstalling.

### Q3: My API key is invalid.
**A**: Please check that the key was copied completely, set in the correct environment variable, and has not expired or been disabled.

### Q4: The program crashed during translation.
**A**: Please check your internet connection and that your API key is still valid and has sufficient quota.

### Q5: The generated mod doesn't load in the game.
**A**: Please double-check that you copied all the necessary files/folders correctly and that the mod is enabled in the correct playset.

## 🎉 Congratulations!

If you've followed this guide and successfully run the program, congratulations! You have successfully:
- Installed a Python environment
- Configured an AI translation service
- Run an automation tool
- Generated a localized mod

## 📞 Need Help?

If you run into issues, you can:
1. Ask in the project's discussion section.
2. Contact the project maintainer.

**Remember**: Everyone starts from zero. Don't give up if you encounter a problem. Follow the steps one by one, and you will succeed!

Good luck! 🎮✨