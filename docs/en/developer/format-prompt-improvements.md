# Format Prompt Improvements and Game-Specific Rules

## Overview

The core of this improvement lies in configuring a dedicated `format_prompt` for each game, combined with a robust fallback mechanism implemented using `GAME_PROFILES` and `FALLBACK_FORMAT_PROMPT` from `scripts/config.py`. This series of optimizations aims to significantly enhance the quality and accuracy of AI translation, ensuring that translation results perfectly adapt to the complex localization format requirements of Paradox games.

## Improvements

### 1. Game-Specific Format Prompt

In the `GAME_PROFILES` dictionary within `scripts/config.py`, each game is now configured with an optimized `format_prompt` tailored to its characteristics. These prompts are based on official Wikis and game mechanics, ensuring that the AI strictly adheres to game-specific syntax and formatting rules during translation.

#### Victoria 3 ⭐ **Latest Update**
- **Accurate Localization Formatting Rules Based on Official Wiki**
- **Data Functions, Scopes, and Concepts ([...])**: This is the most complex syntax. The entire structure, including brackets, periods, parentheses, and single quotes, MUST be preserved.
- **Basic & Chained Functions**: Preserve simple functions like [GetName] and chained functions like [SCOPE.GetType.GetFunction] completely.
- **Functions with Parameters (...)**: Many functions use parentheses to hold parameters. Internal keys and scope names inside single quotes, like 'concept_construction' or 'usa_nation_scope', MUST NOT be translated. Crucially, user-facing text inside single quotes SHOULD BE translated. Example: For [Concept('concept_construction', 'State Construction Efficiency')], you MUST preserve [Concept('concept_construction', '...')] but translate 'State Construction Efficiency'.
- **Function Formatting (using |)**: A pipe | before the closing bracket ] adds formatting. Preserve the entire formatting code, such as [GetValue|*] (formats to K/M/B), [GetValue|+] (adds sign and color).
- **Formatting Commands (#key ... #!)**: These commands start with a #key, followed by a required space, the text, and an end tag #!. You MUST preserve the #key and #! tags. The text between them SHOULD be translated.
- **Simple Formatting**: Colors like #R text#! (red), #gold text#! (gold). Styles like #b text#! (bold).
- **Special Tooltip Formatting**: Structure: #tooltippable;tooltip:<tooltip_key> text_to_display#!. You MUST preserve the #tooltippable;tooltip:<tooltip_key> ... #! part. The text_to_display at the end SHOULD be translated. The <tooltip_key> MUST NOT be translated.
- **Text Icons (@key!)**: These are self-contained icon tags. The entire tag, including @ and !, MUST be preserved completely.
- **Internal Keys and Code References**: Strings with underscores and no spaces, like my_loc or usa_nation_scope, are internal keys. They MUST NOT be translated.
- **Line Breaks**: Preserve all internal newlines (`\n`) exactly as they appear in the source.

#### Stellaris ⭐ **Latest Update**
- **Accurate Localization Formatting Rules Based on Official Wiki**
- **Scoped Commands and Dynamic Text ([...])**: These commands, like [Root.GetName], [Actor.GetAllianceName], or GetDate, fetch dynamic text and MUST be preserved completely, including scopes, periods, and functions. Do not translate anything inside them.
- **Escaping Rule**: A double bracket `[[` is an escape sequence for a single `[`. You MUST preserve it as `[[`.
- **Scripting Rule**: A backslash-escaped command like `\[This.GetName]` is for scripts and MUST be preserved with the leading `\`.
- **Variables and Icons ($...$, £...£)**: Basic variables like $variable_name$ and icons like £energy£ MUST be preserved completely.
- **Modifiers (using |)**: Some variables and icons contain a pipe | to add formatting. The entire structure, including the pipe and the modifier, MUST be preserved. Number Formatting: e.g., $VALUE|*1$ (formats to 1 decimal place). Color Formatting: e.g., $AGE|Y$ (colors the variable's output). Icon Frames: e.g., £leader_skill|3£ (selects the 3rd frame of the icon).
- **Formatting Tags (§...§!)**: Color tags start with § followed by a letter (e.g., §Y) and end with §!. You MUST preserve the tags themselves (§Y, §!), but you SHOULD translate the plain text inside them.
- **Internal Keys and Code References**: Strings with underscores and no spaces, like mm_strategic_region or com_topbar_interests, are internal keys. They MUST NOT be translated.
- **Line Breaks and Tabs**: Preserve all internal newlines (`\n`) and tabs (`\t`) exactly as they appear in the source.

#### Europa Universalis IV ⭐ **Latest Update**
- **Accurate Localization Formatting Rules Based on Official Wiki**
- **Bracket Commands ([...]) - Modern Dynamic Text**: This is the modern system for dynamic text, using scopes and functions. Structures like [Root.GetAdjective] or [From.From.Owner.Monarch.GetHerHim] MUST be preserved completely. Do not translate anything inside the brackets.
- **Legacy Variables ($...$)**: These are a large set of predefined variables enclosed in dollar signs. Examples: $CAPITAL$, $COUNTRY_ADJ$, $MONARCH$, $YEAR$. These variables MUST be preserved completely.
- **Formatting, Icons, and Special Characters (§, £, @, ¤)**:
    - **Basic Color Formatting (§...§!)**: This format is used for simple text coloring. Example: §RRed Text§!. You MUST preserve the tags (§R, §!), but you SHOULD translate the text inside.
    - **Complex Variable Formatting (also using §...§!)**: This is a complex wrapper for formatting variables from section 2. There are two patterns. The entire structure MUST be preserved completely. Pattern 1 (Codes before variable): §<CODES>$VARIABLE$§!. Example: §=Y3$VAL$§!. Pattern 2 (Codes after pipe): $VARIABLE|<CODES>§!. Example: $VAL|%2+$!.
    - **Icons (£...£ and ¤)**: Most icons are wrapped in pound symbols, e.g., £adm£. These MUST be preserved. Special Exception: The ducats icon uses the ¤ symbol. This MUST also be preserved.
    - **Country Flags (@TAG)**: A tag like @HAB represents a country flag and MUST be preserved completely. It can be combined with bracket commands, e.g., @[Root.GetTag].
- **Internal Keys and Code References**: Strings with underscores and no spaces, like button_text, are internal keys. They MUST NOT be translated.
- **Line Breaks**: Preserve all internal newlines (`\n`) exactly as they appear in the source.
- **Historical Terminology**: Preserve all historical, colonial, and trade terminology accurately. Maintain the Renaissance/Enlightenment era tone appropriate for early modern European history.

#### Hearts of Iron IV ⭐ **Latest Update**
- **Accurate Localization Formatting Rules Based on Official Wiki**
- **Square Brackets ([...]): Two Main Uses**:
    - **Namespaces and Scopes**: Used to get dynamic information. Structures like [GetDateText] or [ROOT.GetNameDefCap] MUST be preserved completely. Do not translate anything inside them.
    - **Formatting Variables**: Used to format a variable's output, often starting with a ?. The entire structure [?variable|codes] MUST be preserved. The codes after the pipe | define the format. Examples to preserve: [?var|%G0] (percentage, green, 0 decimals), [?var|*] (SI units like K/M), [?var|+] (dynamic color: green for positive, red for negative), [?var|.1] (1 decimal place).
- **String Nesting and Variables ($...$)**: This syntax is used to nest other localization keys or variables. The entire structure, like $KEY_NAME$ or $FOCUS_NAME$, MUST be preserved completely. Escaping Rule: A double dollar sign $$ is an escape for a single $. You MUST preserve it as $.
- **Color, Icons, and Flags (§, £, @)**:
    - **Color Tags (§...§!)**: Color tags start with § and a letter (e.g., §R) and end with §!. You MUST preserve the tags, but you SHOULD translate the plain text inside them. Example: For §RRed Text§!, translate "Red Text" but keep §R and §!.
    - **Text Icons (£...)**: These are single tags representing an icon, like £GFX_army_experience. They MUST be preserved completely. Frame Modifier: An optional frame can be specified with a pipe, e.g., £icon_name|1. This entire structure must be preserved.
    - **Country Flags (@TAG)**: A tag like @GER represents a country flag and MUST be preserved completely.
- **Localization Formatters (Standalone formatter|token)**: Some strings are special formatters that consist of two parts separated by a pipe |, with no surrounding brackets. Example: building_state_modifier|dam. These strings are code references and MUST NOT be translated. Preserve them completely.
- **Internal Keys and Code References**: Strings with underscores and no spaces, like example_key or party_popularity@democracy, are internal keys. They MUST NOT be translated.
- **Line Breaks**: Preserve all internal newlines (`\n`) exactly as they appear in the source.

#### Crusader Kings III ⭐ **Latest Update**
- **Accurate Localization Formatting Rules Based on Official Wiki**
- **Data Functions and Linking ([...])**: This syntax is used to get dynamic text from game data. The entire structure inside the brackets MUST be preserved.
    - **Scopes and Functions**: Preserve commands like [ROOT.Char.GetLadyLord] completely. Do not translate any part of them.
    - **Function Arguments (using |)**: A pipe | at the end of a function applies formatting. Preserve the function and the entire argument. Examples: [ROOT.Char.GetLadyLord|U] (uppercase first letter), [some_value|2] (round to 2 decimals), [GetFullName|P] (formats as positive/green).
    - **Linking to Game Concepts**: A very common and specific use case. Preserve simple links like [faith|E] or [faith|El] (for lowercase). For alternate text forms like [Concept('faith','religion')|E], you MUST preserve the function structure [Concept('faith','...')|E], but the user-facing text, in this case 'religion', SHOULD BE translated.
    - **Linking to Traits/Titles**: Preserve complex function calls like [GetTrait('trait_name').GetName( CHARACTER.Self )] or [GetTitleByKey('title_name').GetName] completely.
- **String Nesting and Variables ($...$)**: This syntax has two main uses. The entire $key$ structure MUST be preserved.
    - **Nesting Other Keys**: Re-uses another localization key, e.g., $special_contract_march_short$.
    - **Game Engine Variables**: Displays a value from the game. These can have special formatting. Example: $VALUE|=+0$. The unique |=... formatting MUST be preserved completely.
- **Text Formatting (#...#!)**: These commands start with a #key, followed by a required space, the text, and an end tag #!. You MUST preserve the #key and #! tags. The text between them SHOULD be translated.
    - **Basic Formatting**: Examples include #P text#! (positive/green), #N text#! (negative/red), #bold text#!, #italic text#!.
    - **Combined Formatting**: Formatting can be combined with a semicolon ;. Preserve the entire combined key. Example: #high;bold.
- **Icons (@icon_name!)**: These are self-contained icon tags. The entire tag, including @ and !, MUST be preserved completely. Example: @gold_icon!.
- **Basic Characters**: Preserve all internal newlines (`\n`) and escaped double quotes (`\\"`) exactly as they appear in the source.
- **Medieval Terminology**: Preserve all medieval, feudal, and dynastic terminology accurately. Maintain the medieval, courtly tone appropriate for medieval role-playing and dynasty management.

### 2. Fallback Mechanism

The `FALLBACK_FORMAT_PROMPT` constant is defined in `scripts/config.py`. When a game configuration does not have a dedicated `format_prompt`, the system automatically uses this fallback option, ensuring that a usable format prompt template is always available, thereby guaranteeing the stability of the translation process.

### 3. API Handler Updates

All AI service handlers (including `openai_handler.py`, `gemini_handler.py`, and `qwen_handler.py`) have been updated to intelligently:
1.  Prioritize checking if the current game configuration (from `GAME_PROFILES`) has a dedicated `format_prompt`.
2.  If it does, use the game-specific template.
3.  If not, automatically fall back to the `FALLBACK_FORMAT_PROMPT` defined in `scripts/config.py`.

## Technical Implementation

### Configuration Structure (`scripts/config.py`)

In `scripts/config.py`, the `GAME_PROFILES` dictionary defines detailed configurations for each game, including game-specific `format_prompt`. At the same time, `FALLBACK_FORMAT_PROMPT` serves as a general fallback option.

```python
# scripts/config.py Example
GAME_PROFILES = {
    "1": {
        "id": "victoria3",
        "name": "Victoria 3 (维多利亚3)",
        # ... other configurations ...
        "prompt_template": (
            "You are a professional translator specializing in the grand strategy game Victoria 3, "
            "set in the 19th and early 20th centuries. "
            "Translate the following numbered list of texts from {source_lang_name} to {target_lang_name}.\n"
        ),
        "single_prompt_template": (
            "You are a direct, one-to-one translation engine. "
            "The text you are translating is for a Victoria 3 game mod named '{mod_name}'. "
            "Translate the following {task_description} from {source_lang_name} to {target_lang_name}.\n"
        ),
        "format_prompt": (
            # ... detailed Victoria 3 formatting rules ...
            "--- INPUT LIST ---\n{numbered_list}\n--- END OF INPUT LIST ---"
        ),
    },
    # ... other game configurations ...
}

# Fallback format prompt template
FALLBACK_FORMAT_PROMPT = (
    "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
    "{chunk_size}. "
    # ... general formatting rules ...
    "--- INPUT LIST ---\n{numbered_list}\n--- END OF INPUT LIST ---"
)
```

### Usage Logic (API Handler)

In AI service handlers (e.g., `gemini_handler.py`), `format_prompt` is intelligently selected based on the current game configuration:

```python
# Example: Selecting format_prompt in API Handler
# Prioritize game-specific format_prompt, otherwise use fallback option
if "format_prompt" in game_profile:
    format_prompt_part = game_profile["format_prompt"].format(
        chunk_size=len(chunk),
        punctuation_prompt=punctuation_prompt if punctuation_prompt else "",
        numbered_list=numbered_list
    )
else:
    # Import fallback option
    from scripts.config import FALLBACK_FORMAT_PROMPT
    format_prompt_part = FALLBACK_FORMAT_PROMPT.format(
        chunk_size=len(chunk),
        punctuation_prompt=punctuation_prompt if punctuation_prompt else "",
        numbered_list=numbered_list
    )
```

## Advantages

1. **Improved Accuracy**: Terminology and tone for each game are specifically optimized.
2. **Reduced Error Rate**: Addresses special syntax and formatting requirements for specific games.
3. **Maintained Compatibility**: The fallback mechanism ensures the system is always available.
4. **Easy Maintenance**: Centralized management of all format prompt templates.
5. **Extensibility**: New games can easily be added with corresponding `format_prompt`.
6. **Stellaris Specific Advantage**: Accurate rules based on the official Wiki significantly reduce localization error rates.
7. **Victoria 3 Specific Advantage**: Complex syntax rules based on the official Wiki, especially for data functions, scopes, and concepts.
8. **HOI4 Specific Advantage**: Military strategy game syntax rules based on the official Wiki, especially for formatting variables, country flags, and localization formatters.

## Notes

1. All `format_prompt` must include the following placeholders:
   - `{chunk_size}`: Batch size
   - `{punctuation_prompt}`: Punctuation conversion prompt (intelligently generated by `scripts/utils/punctuation_handler.py`)
   - `{numbered_list}`: Numbered list

2. When adding new games, it is recommended to refer to the structure of existing templates.
3. Maintain consistency with existing `prompt_template` and `single_prompt_template`.
4. **Stellaris Specific Requirements**: Strictly follow the official Wiki's syntax rules, especially for scoped commands, escape sequences, and modifiers.
5. **Victoria 3 Specific Requirements**: Strictly follow the official Wiki's complex syntax rules, especially for data functions, scopes, concepts, and formatting commands.
6. **HOI4 Specific Requirements**: Strictly follow the official Wiki's syntax rules, especially for formatting variables, country flags, localization formatters, and escape sequences.

## Test Results

Validated through test scripts:
- `format_prompt` for all 5 games are correctly formatted.
- Fallback option works correctly.
- All placeholders are correctly replaced.
- **Stellaris format_prompt**: Includes all key rules, formatted successfully, length 2068 characters.
- **Victoria 3 format_prompt**: Includes all key rules, formatted successfully, length 2798 characters.
- **HOI4 format_prompt**: Includes all key rules, formatted successfully, length 2708 characters.

## Update History

### 2025-10-06 - Latest Update
- Based on `GAME_PROFILES` in `scripts/config.py`, detailed `format_prompt` rules for Victoria 3, Stellaris, Europa Universalis IV, Hearts of Iron IV, and Crusader Kings III are explained.
- Emphasized the fallback mechanism of `FALLBACK_FORMAT_PROMPT`.
- Clarified how API Handlers intelligently select `format_prompt`.
- Added explanation for the `punctuation_prompt` placeholder.

### 2025-01-XX - HOI4 format_prompt Major Update
- Updated Hearts of Iron IV localization formatting rules based on the official Wiki.
- Added two main uses of square brackets: namespaces and scopes, formatting variables.
- Added explanations for advanced features such as formatting variables, country flags, and localization formatters.
- Significantly improved the accuracy and reliability of HOI4 localization.

### 2025-01-XX - Victoria 3 format_prompt Major Update
- Updated Victoria 3 localization formatting rules based on the official Wiki.
- Added detailed syntax explanations for data functions, scopes, and concepts.
- Added explanations for advanced features such as formatting commands and tooltip formatting.
- Significantly improved the accuracy and reliability of Victoria 3 localization.

### 2025-01-XX - Stellaris format_prompt Major Update
- Updated Stellaris localization formatting rules based on the official Wiki.
- Added detailed explanations for scoped commands, escape rules, and scripting rules.
- Added explanations for advanced features such as modifiers, number formatting, and color formatting.
- Significantly improved the accuracy and reliability of Stellaris localization.
