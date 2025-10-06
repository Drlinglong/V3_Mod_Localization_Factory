# Blue Archive Auxiliary Glossary Usage Guide

## Overview

This project now supports an auxiliary glossary feature, providing additional terminology support for MODs with specific themes. Currently, it includes a dedicated glossary for Blue Archive.

## Features

### 1. Auxiliary Glossary System
- **Main Glossary**: `glossary.json` file in each game directory.
- **Auxiliary Glossaries**: `.json` files with other names (e.g., `blue_archive.json`).
- **Automatic Merging**: Auxiliary glossary entries will be merged with the main glossary, with auxiliary glossaries having higher priority.

### 2. Blue Archive Glossary Content
- **Character Names**: Arona, Shiroko, Yuuka, Hoshino, Nonomi, etc.
- **Skill System**: EX Skills, Normal Skills, Passive Skills.
- **Game Mechanics**: Tactics, Combat, Training, Social, etc.
- **Equipment Items**: Weapons, Armor, Consumables.
- **Worldview**: Academy, Mystery, Story, etc.

## Usage

### 1. Start the Program
After running the main program, follow the normal process to select:
- MOD
- Game type (select Stellaris)
- API provider
- Source language and target language

### 2. Select Auxiliary Glossaries
After language selection, the program will display:
```
Main glossary.json enabled (contains X terms)
Auxiliary glossaries detected:
[1] Blue Archive (碧蓝档案) - Korean anime mobile game terminology and character names (20 terms)
Please select auxiliary glossaries to enable:
Enter 0 to enable all
Enter N to not use auxiliary glossaries
```

**Option Description**:
- `0`: Enable all auxiliary glossaries.
- `1, 2, 3...`: Enable specific auxiliary glossaries.
- `N`: Do not use any auxiliary glossaries.

### 3. Project Overview Confirmation
After selecting auxiliary glossaries, the program will display complete project information:
```
=== Project Overview ===
Target MOD: [MOD Name]
API Provider: [Provider Name]
Game Type: Stellaris
Source Language: [Source Language]
Target Language: [Target Language]
Clean redundant files: To be confirmed
Glossary Configuration: Main Glossary + X Auxiliary Glossaries
After translation, it will ask whether to clean redundant files.

Press Y to confirm and start translation, press N to return to language selection:
```

**Confirmation Options**:
- `Y`: Confirm and start translation.
- `N`: Return to language selection interface.

### 4. Translation Process
- Auxiliary glossaries will be automatically merged with the main glossary.
- AI translation will prioritize terms from auxiliary glossaries.
- Ensures consistency in the translation of Blue Archive related terminology.

### 5. Cleanup Confirmation
After translation, the program will ask whether to clean source files:
```
Translation complete! Do you want to clean the source MOD folder '[MOD Name]' to save disk space?
This will delete all files except '.metadata', 'localization', and 'thumbnail.png'.
Do you want to continue? (Enter 'y' or 'yes' to confirm):
```

## Glossary File Structure

### Main Glossary (glossary.json)
```json
{
  "metadata": {
    "name": "Stellaris Glossary",
    "description": "Main game terminology"
  },
  "entries": [...]
}
```

### Auxiliary Glossary (blue_archive.json)
```json
{
  "metadata": {
    "name": "Blue Archive",
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

## Adding New Auxiliary Glossaries

### 1. Create Glossary File
Create a new `.json` file in the `data/glossary/[Game ID]/` directory.

### 2. File Naming Convention
- Use descriptive names (e.g., `blue_archive.json`).
- Avoid using `glossary.json` (this is the reserved name for the main glossary).

### 3. Metadata Requirements
```json
{
  "metadata": {
    "name": "Glossary Name",
    "description": "Glossary Description",
    "version": "Version Number",
    "type": "auxiliary"
  }
}
```

### 4. Entry Format
Each entry should contain:
- `id`: Unique identifier.
- `translations`: Multi-language translations.
- `metadata`: Category and remarks information.

## Notes

1. **Priority**: Auxiliary glossary entries will overwrite entries with the same ID in the main glossary.
2. **Compatibility**: Auxiliary glossaries need to use the same language codes as the main glossary.
3. **Performance**: Glossary merging will slightly increase memory usage, but the impact is minimal.
4. **Error Handling**: If an auxiliary glossary fails to load, the program will continue to use the main glossary.

## Troubleshooting

### Problem: Auxiliary glossary not displayed
**Possible Causes**:
- File is not in the correct directory.
- File format error (JSON syntax error).
- File permission issues.

**Solution**:
- Check file path: `data/glossary/stellaris/blue_archive.json`.
- Validate JSON format.
- Check file permissions.

### Problem: Glossary merging failed
**Possible Causes**:
- Main glossary not loaded correctly.
- Auxiliary glossary format incompatible.

**Solution**:
- Ensure the main glossary file exists and is readable.
- Check the JSON structure of the auxiliary glossary.

## Extension Suggestions

1. **More Game Themes**: Can add auxiliary glossaries for other game themes.
2. **Glossary Validation**: Add format validation for glossary files.
3. **Online Glossaries**: Support loading glossaries from the network.
4. **Glossary Management**: Provide a management interface for enabling/disabling glossaries.

---

If you have any questions or suggestions, please refer to the project's main documentation or submit an Issue.
