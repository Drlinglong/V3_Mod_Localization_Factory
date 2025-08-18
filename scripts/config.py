# scripts/config.py
# ---------------------------------------------------------------
import os  # 导入os模块以备后用
import multiprocessing

# --- 项目信息 ----------------------------------------------------
PROJECT_NAME = "Paradox Mod Localization Factory"
PROJECT_DISPLAY_NAME = "Project Remis (蕾姆丝计划)"
VERSION = "1.0.2"
LAST_UPDATE_DATE = "2025-08-17"
COPYRIGHT = "© 2025 Project Remis Team"

# --- 核心配置 ----------------------------------------------------
CHUNK_SIZE = 40
MAX_RETRIES = 3

# --- 智能线程池配置 ----------------------------------------------------
def get_smart_max_workers():
    """
    智能计算最优线程池大小
    使用Python内置的智能线程池管理，避免线程爆炸
    """
    # Python内置的智能线程池公式：min(32, (cpu_count or 1) + 4)
    cpu_count = multiprocessing.cpu_count()
    # 对于I/O密集型任务，可以适当增加，但不超过系统核心数的2倍
    recommended = min(32, cpu_count * 2)
    return recommended

# 智能线程池大小
RECOMMENDED_MAX_WORKERS = get_smart_max_workers()

# 每个批次的最大文本数量
BATCH_SIZE = CHUNK_SIZE

# --- 路径配置 ----------------------------------------------------
# 使用绝对路径，避免工作目录依赖问题
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SOURCE_DIR = os.path.join(PROJECT_ROOT, 'source_mod')
DEST_DIR = os.path.join(PROJECT_ROOT, 'my_translation')

# --- API Provider Configuration ---
DEFAULT_API_PROVIDER = "gemini" 

API_PROVIDERS = {
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "default_model": "gemini-2.5-flash",
        "enable_thinking": False,      # 禁用思考功能，节约成本
        "thinking_budget": 0,          # 0=完全禁用, -1=动态启用, >0=限制token数
    },
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "default_model": "gpt-5-mini" # or gpt-5 
    },
    "qwen": {
        "api_key_env": "DASHSCOPE_API_KEY",
        "default_model": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "region": "beijing",  # 华北2（北京）地域
        "enable_thinking": False,      # 禁用思考功能，节约成本
    },
    # 未来可以在这里增加 deepseek 等
}

# --- 语言数据库 --------------------------------------------------
LANGUAGES = {
    "1":  {"code": "en",     "key": "l_english",      "name": "English",             "folder_prefix": "en-"},
    "2":  {"code": "zh-CN",  "key": "l_simp_chinese", "name": "简体中文",             "folder_prefix": "zh-CN-"},
    "3":  {"code": "fr",     "key": "l_french",       "name": "Français",            "folder_prefix": "fr-"},
    "4":  {"code": "de",     "key": "l_german",       "name": "Deutsch",             "folder_prefix": "de-"},
    "5":  {"code": "es",     "key": "l_spanish",      "name": "Español",             "folder_prefix": "es-"},
    "6":  {"code": "ja",     "key": "l_japanese",     "name": "日本語",               "folder_prefix": "ja-"},
    "7":  {"code": "ko",     "key": "l_korean",       "name": "한국어",               "folder_prefix": "ko-"},
    "8":  {"code": "pl",     "key": "l_polish",       "name": "Polski",              "folder_prefix": "pl-"},
    "9":  {"code": "pt-BR",  "key": "l_braz_por",     "name": "Português do Brasil", "folder_prefix": "pt-BR-"},
    "10": {"code": "ru",     "key": "l_russian",      "name": "Русский",             "folder_prefix": "ru-"},
    "11": {"code": "tr",     "key": "l_turkish",      "name": "Türkçe",              "folder_prefix": "tr-"}
}

# --- 语言标点符号配置 --------------------------------------------------
LANGUAGE_PUNCTUATION_CONFIG = {
    "zh-CN": {
        "name": "简体中文",
        "punctuation": {
            "，": ",", "。": ".", "！": "!", "？": "?", "：": ":", "；": ";",
            "（": "(", "）": ")", "【": "[", "】": "]", "《": "<", "》": ">",
            '"': '"', '"': '"', ''': "'", ''': "'", "…": "...", "—": "-",
            "－": "-", "　": " ", "、": ",", "·": ".", "～": "~", "％": "%",
            "＃": "#", "＄": "$", "＆": "&", "＊": "*", "＋": "+", "＝": "=",
            "／": "/", "＼": "\\", "｜": "|", "＠": "@"
        },
        "examples": ["你好，世界！", "这是一个测试：标点符号。", "（重要）信息"]
    },
    
    "ja": {
        "name": "日本語",
        "punctuation": {
            "、": ",", "。": ".", "！": "!", "？": "?", "：": ":", "；": ";",
            "（": "(", "）": ")", "【": "[", "】": "]", "「": '"', "」": '"',
            "『": "'", "』": "'", "・": "·", "…": "...", "—": "-", "～": "~"
        },
        "examples": ["こんにちは、世界！", "これはテストです：句読点。", "（重要）情報"]
    },
    
    "ko": {
        "name": "한국어",
        "punctuation": {
            "，": ",", "。": ".", "！": "!", "？": "?", "：": ":", "；": ";",
            "（": "(", "）": ")", "［": "[", "］": "]", "｛": "{", "｝": "}",
            "《": "<", "》": ">", "「": '"', "」": '"', "『": "'", "』": "'"
        },
        "examples": ["안녕하세요, 세계!", "이것은 테스트입니다: 문장 부호.", "（중요）정보"]
    },
    
    "ru": {
        "name": "Русский",
        "punctuation": {
            "«": '"', "»": '"', "—": "-", "…": "...", "№": "#"
        },
        "examples": ["Привет, мир!", "Это тест: пунктуация.", "«Важная» информация"]
    },
    
    "fr": {
        "name": "Français",
        "punctuation": {
            "«": '"', "»": '"', "‹": "'", "›": "'", "…": "...", "—": "-", "–": "-"
        },
        "examples": ["Bonjour, monde!", "C'est un test: ponctuation.", "«Important» information"]
    },
    
    "es": {
        "name": "Español",
        "punctuation": {
            "¿": "?", "¡": "!", "«": '"', "»": '"', "…": "...", "—": "-", "–": "-"
        },
        "examples": ["¿Hola, mundo!", "¡Es una prueba: puntuación!", "«Importante» información"]
    },
    
    "tr": {
        "name": "Türkçe",
        "punctuation": {
            "«": '"', "»": '"', "…": "...", "—": "-", "–": "-"
        },
        "examples": ["Merhaba, dünya!", "Bu bir test: noktalama.", "«Önemli» bilgi"]
    },
    
    "de": {
        "name": "Deutsch",
        "punctuation": {
            "„": '"', """: '"', "‚": "'", "'": "'", "…": "...", "—": "-", "–": "-"
        },
        "examples": ["Hallo, Welt!", "Das ist ein Test: Interpunktion.", "„Wichtige" Informationen"]
    },
    
    "pl": {
        "name": "Polski",
        "punctuation": {
            "„": '"', """: '"', "‚": "'", "'": "'", "…": "...", "—": "-", "–": "-"
        },
        "examples": ["Witaj, świecie!", "To jest test: interpunkcja.", "Ważne informacje"]
    },
    
    "pt-BR": {
        "name": "Português do Brasil",
        "punctuation": {
            """: '"', """: '"', "'": "'", "'": "'", "…": "...", "—": "-", "–": "-"
        },
        "examples": ["Olá, mundo!", "Este é um teste: pontuação.", "Importante informação"]
    }
}

# 目标语言标点符号标准
TARGET_LANGUAGE_PUNCTUATION = {
    "en": {
        "name": "English",
        "punctuation": [",", ".", "!", "?", ":", ";", "(", ")", "[", "]", "<", ">", '"', "'", "...", "-", "~", "#", "$", "%", "&", "*", "+", "=", "/", "\\", "|", "@"]
    }
}

# --- 游戏档案数据库 ---------------------------------------------
GAME_PROFILES = {
    # 1 ─ Victoria 3
    "1": {
        "id": "victoria3",
        "name": "Victoria 3 (维多利亚3)",
        "supported_language_keys": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
        "source_localization_folder": "localization",
        "protected_items": {".metadata", "localization", "thumbnail.png"},
        "metadata_file": os.path.join(".metadata", "metadata.json"),

        # ↓↓↓   NOWE KLUCZE   ↓↓↓
        "encoding": "utf-8-sig",          # V3 używa UTF-8
        "strip_pl_diacritics": False, # ogonków nie ruszamy
        # ↑↑↑----------------↑↑↑

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
            "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
            "{chunk_size}. "
            "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
            "DO NOT merge, add, or omit lines. DO NOT add any explanations or notes.\n\n"
            "Preserve the following Victoria 3 specific syntax rules precisely:\n\n"
            "1. **Data Functions, Scopes, and Concepts ([...])**\n\n"
            "   This is the most complex syntax. The entire structure, including brackets, periods, parentheses, and single quotes, MUST be preserved.\n\n"
            "   a. **Basic & Chained Functions**: Preserve simple functions like [GetName] and chained functions like [SCOPE.GetType.GetFunction] completely.\n\n"
            "   b. **Functions with Parameters (...)**: Many functions use parentheses to hold parameters.\n\n"
            "       Internal keys and scope names inside single quotes, like 'concept_construction' or 'usa_nation_scope', MUST NOT be translated.\n\n"
            "       Crucially, user-facing text inside single quotes SHOULD BE translated.\n\n"
            "       Example: For [Concept('concept_construction', 'State Construction Efficiency')], you MUST preserve [Concept('concept_construction', '...')] but translate 'State Construction Efficiency'.\n\n"
            "   c. **Function Formatting (using |)**: A pipe | before the closing bracket ] adds formatting. Preserve the entire formatting code.\n\n"
            "       Examples: [GetValue|*] (formats to K/M/B), [GetValue|+] (adds sign and color), [GetValue|%] (adds percent sign), [GetValue|2] (formats to 2 decimal places).\n\n"
            "2. **Formatting Commands (#key ... #!)**\n\n"
            "   These commands start with a #key, followed by a required space, the text, and an end tag #!.\n\n"
            "   You MUST preserve the #key and #! tags. The text between them SHOULD be translated.\n\n"
            "   a. **Simple Formatting (Color & Style)**:\n\n"
            "       Color examples: #R text#! (red), #gold text#! (gold).\n\n"
            "       Style examples: #b text#! (bold), #italic text#! (italic), #L text#! (underline).\n\n"
            "   b. **Special Tooltip Formatting**: This is a complex but specific format.\n\n"
            "       Structure: #tooltippable;tooltip:<tooltip_key> text_to_display#!\n\n"
            "       You MUST preserve the #tooltippable;tooltip:<tooltip_key> ... #! part.\n\n"
            "       The text_to_display at the end SHOULD be translated. The <tooltip_key> MUST NOT be translated.\n\n"
            "3. **Text Icons (@key!)**\n\n"
            "   These are self-contained icon tags. The entire tag, including @ and !, MUST be preserved completely.\n\n"
            "   Examples: @capitalists!, @money!, @warning!.\n\n"
            "4. **Internal Keys and Code References**\n\n"
            "   Strings with underscores and no spaces, like my_loc or usa_nation_scope, are internal keys. They MUST NOT be translated.\n\n"
            "5. **Line Breaks**\n\n"
            "   Preserve all internal newlines (\\n) exactly as they appear in the source.\n\n"
            "6. **Industrial Era Terminology**\n\n"
            "   Preserve all industrial, colonial, and Victorian era terminology accurately. Maintain the 19th and early 20th century tone appropriate for the Industrial Revolution and Age of Imperialism.\n\n"
            "--- INPUT LIST ---\n{numbered_list}\n--- END OF INPUT LIST ---"
        ),
    },

    # 2 ─ Stellaris
    "2": {
        "id": "stellaris",
        "name": "Stellaris (群星)",
        "supported_language_keys": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], # 支持10种 (无土耳其语)
        "source_localization_folder": "localisation",
        "protected_items": {"descriptor.mod", "localisation", "thumbnail.png"},
        "metadata_file": "descriptor.mod",

        # ↓↓↓   NOWE KLUCZE   ↓↓↓
        "encoding": "utf-8-sig",          # Stellaris również UTF-8
        "strip_pl_diacritics": False, # pełna polska pisownia
        # ↑↑↑----------------↑↑↑

        "prompt_template": (
            "You are a professional translator specializing in the grand strategy science-fiction game Stellaris. "
            "Translate the following numbered list of texts from {source_lang_name} to {target_lang_name}.\n"
        ),
        "single_prompt_template": (
            "You are a direct, one-to-one translation engine. "
            "The text you are translating is for a Stellaris game mod named '{mod_name}'. "
            "Translate the following {task_description} from {source_lang_name} to {target_lang_name}.\n"
        ),
        "format_prompt": (
            "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
            "{chunk_size}. "
            "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
            "DO NOT merge, add, or omit lines. DO NOT add any explanations or notes.\n\n"
            "Preserve the following special syntax rules precisely:\n\n"
            "1. **Scoped Commands and Dynamic Text ([...])**\n\n"
            "   These commands, like [Root.GetName], [Actor.GetAllianceName], or GetDate, fetch dynamic text and MUST be preserved completely, including scopes, periods, and functions. Do not translate anything inside them.\n\n"
            "   Escaping Rule: A double bracket [[ is an escape sequence for a single [. You MUST preserve it as [[.\n\n"
            "   Scripting Rule: A backslash-escaped command like \\\\[This.GetName] is for scripts and MUST be preserved with the leading \\\\.\n\n"
            "2. **Variables and Icons ($...$, £...£)**\n\n"
            "   Basic variables like $variable_name$ and icons like £energy£ MUST be preserved completely.\n\n"
            "   Modifiers (using |): Some variables and icons contain a pipe | to add formatting. The entire structure, including the pipe and the modifier, MUST be preserved.\n\n"
            "       Number Formatting: e.g., $VALUE|*1$ (formats to 1 decimal place).\n\n"
            "       Color Formatting: e.g., $AGE|Y$ (colors the variable's output).\n\n"
            "       Icon Frames: e.g., £leader_skill|3£ (selects the 3rd frame of the icon).\n\n"
            "3. **Formatting Tags (§...§!)**\n\n"
            "   Color tags start with § followed by a letter (e.g., §Y) and end with §!.\n\n"
            "   You MUST preserve the tags themselves (§Y, §!), but you SHOULD translate the plain text inside them.\n\n"
            "   Example: For §YImportant Text§!, translate \"Important Text\" but keep §Y and §!.\n\n"
            "4. **Internal Keys and Code References**\n\n"
            "   Strings with underscores and no spaces, like mm_strategic_region or com_topbar_interests, are internal keys. They MUST NOT be translated.\n\n"
            "5. **Line Breaks and Tabs**\n\n"
            "   Preserve all internal newlines (\\n) and tabs (\\t) exactly as they appear in the source.\n\n"
            "6. **Science Fiction Terminology**\n\n"
            "   Preserve all science fiction, space exploration, and futuristic terminology accurately. Maintain the grand strategy science-fiction tone appropriate for space exploration and interstellar empire management.\n\n"
            "--- INPUT LIST ---\n{numbered_list}\n--- END OF INPUT LIST ---"
        ),
    },

    # 3 ─ Europa Universalis IV
    "3": {
        "id": "eu4",
        "name": "Europa Universalis IV (欧陆风云4)",
        "supported_language_keys": ["1", "3", "4", "5"], # 支持4种
        "source_localization_folder": "localisation",
        "protected_items": {"descriptor.mod", "localisation", "thumbnail.png"},
        "metadata_file": "descriptor.mod",

        # ↓↓↓   NOWE KLUCZE   ↓↓↓
        "encoding": "cp1252",         # klasyczne „ANSI" Paradoxu
        "strip_pl_diacritics": True,  # usuń ąęłś… przy zapisie
        # ↑↑↑----------------↑↑↑

        "prompt_template": (
            "You are a professional translator specializing in the grand strategy game Europa Universalis IV, "
            "set in the early modern era (1444–1821). "
            "Translate the following numbered list of texts from {source_lang_name} to {target_lang_name}.\n"
        ),
        "single_prompt_template": (
            "You are a direct, one-to-one translation engine. "
            "The text you are translating is for an Europa Universalis IV game mod named '{mod_name}'. "
            "Translate the following {task_description} from {source_lang_name} to {target_lang_name}.\n"
        ),
        "format_prompt": (
            "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
            "{chunk_size}. "
            "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
            "DO NOT merge, add, or omit lines. DO NOT add any explanations or notes.\n\n"
            "Preserve the following Europa Universalis IV specific syntax rules precisely:\n\n"
            "1. **Bracket Commands ([...]) - Modern Dynamic Text**\n\n"
            "   This is the modern system for dynamic text, using scopes and functions.\n\n"
            "   Structures like [Root.GetAdjective] or [From.From.Owner.Monarch.GetHerHim] MUST be preserved completely. Do not translate anything inside the brackets.\n\n"
            "2. **Legacy Variables ($...$)**\n\n"
            "   These are a large set of predefined variables enclosed in dollar signs.\n\n"
            "   Examples: $CAPITAL$, $COUNTRY_ADJ$, $MONARCH$, $YEAR$.\n\n"
            "   These variables MUST be preserved completely.\n\n"
            "3. **Formatting, Icons, and Special Characters (§, £, @, ¤)**\n\n"
            "   a. **Basic Color Formatting (§...§!)**:\n\n"
            "       This format is used for simple text coloring.\n\n"
            "       Example: §RRed Text§!. You MUST preserve the tags (§R, §!), but you SHOULD translate the text inside.\n\n"
            "   b. **Complex Variable Formatting (also using §...§!)**:\n\n"
            "       This is a complex wrapper for formatting variables from section 2. There are two patterns. The entire structure MUST be preserved completely.\n\n"
            "       Pattern 1 (Codes before variable): §<CODES>$VARIABLE$§!. Example: §=Y3$VAL$§!.\n\n"
            "       Pattern 2 (Codes after pipe): $VARIABLE|<CODES>§!. Example: $VAL|%2+$!.\n\n"
            "   c. **Icons (£...£ and ¤)**:\n\n"
            "       Most icons are wrapped in pound symbols, e.g., £adm£. These MUST be preserved.\n\n"
            "       Special Exception: The ducats icon uses the ¤ symbol. This MUST also be preserved.\n\n"
            "   d. **Country Flags (@TAG)**:\n\n"
            "       A tag like @HAB represents a country flag and MUST be preserved completely. It can be combined with bracket commands, e.g., @[Root.GetTag].\n\n"
            "4. **Internal Keys and Code References**\n\n"
            "   Strings with underscores and no spaces, like button_text, are internal keys. They MUST NOT be translated.\n\n"
            "5. **Line Breaks**\n\n"
            "   Preserve all internal newlines (\\n) exactly as they appear in the source.\n\n"
            "6. **Historical Terminology**\n\n"
            "   Preserve all historical, colonial, and trade terminology accurately. Maintain the Renaissance/Enlightenment era tone appropriate for early modern European history.\n\n"
            "--- INPUT LIST ---\n{numbered_list}\n--- END OF INPUT LIST ---"
        ),
    },

    "4": {
        "id": "hoi4",
        "name": "Hearts of Iron IV (钢铁雄心4)",
        "supported_language_keys": ["1", "2", "3", "4", "5", "6" , "8", "9", "10"],#9种语言不支持韩语和土耳其语
        "source_localization_folder": "localisation", # 和群星一样same as stellaris
        "protected_items": {'descriptor.mod', 'localisation', 'thumbnail.png'}, # 和群星一样same as stellaris
        "metadata_file": 'descriptor.mod', # 和群星一样same as stellaris
        "encoding": "utf-8-sig", # 和群星/V3一样same as stellaris/VIC3
        "strip_pl_diacritics": False,
        "prompt_template": (
            "You are a professional translator specializing in the grand strategy game Hearts of Iron IV, set during World War II. "
            "Translate the following numbered list of texts from {source_lang_name} to {target_lang_name}.\n"
            "The tone must be appropriate for a historical military and political strategy game."
        ),
        "single_prompt_template": (
            "You are a direct, one-to-one translation engine. "
            "The text you are translating is for a Hearts of Iron IV game mod named '{mod_name}'. "
            "Translate the following {task_description} from {source_lang_name} to {target_lang_name}.\n"
        ),
        "format_prompt": (
            "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
            "{chunk_size}. "
            "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
            "DO NOT merge, add, or omit lines. DO NOT add any explanations or notes.\n\n"
            "Preserve the following Hearts of Iron IV specific syntax rules precisely:\n\n"
            "1. **Square Brackets ([...]): Two Main Uses**\n\n"
            "   a. **Namespaces and Scopes**: Used to get dynamic information. Structures like [GetDateText] or [ROOT.GetNameDefCap] MUST be preserved completely. Do not translate anything inside them.\n\n"
            "   b. **Formatting Variables**: Used to format a variable's output, often starting with a ?. The entire structure [?variable|codes] MUST be preserved.\n\n"
            "       The codes after the pipe | define the format. Examples to preserve:\n\n"
            "           [?var|%G0] (percentage, green, 0 decimals)\n\n"
            "           [?var|*] (SI units like K/M)\n\n"
            "           [?var|+] (dynamic color: green for positive, red for negative)\n\n"
            "           [?var|.1] (1 decimal place)\n\n"
            "2. **String Nesting and Variables ($...$)**\n\n"
            "   This syntax is used to nest other localization keys or variables.\n\n"
            "   The entire structure, like $KEY_NAME$ or $FOCUS_NAME$, MUST be preserved completely.\n\n"
            "   Escaping Rule: A double dollar sign $$ is an escape for a single $. You MUST preserve it as $$.\n\n"
            "3. **Color, Icons, and Flags (§, £, @)**\n\n"
            "   a. **Color Tags (§...§!)**: Color tags start with § and a letter (e.g., §R) and end with §!. You MUST preserve the tags, but you SHOULD translate the plain text inside them.\n\n"
            "       Example: For §RRed Text§!, translate \"Red Text\" but keep §R and §!.\n\n"
            "   b. **Text Icons (£...)**: These are single tags representing an icon, like £GFX_army_experience. They MUST be preserved completely.\n\n"
            "       Frame Modifier: An optional frame can be specified with a pipe, e.g., £icon_name|1. This entire structure must be preserved.\n\n"
            "   c. **Country Flags (@TAG)**: A tag like @GER represents a country flag and MUST be preserved completely.\n\n"
            "4. **Localization Formatters (Standalone formatter|token)**\n\n"
            "   Some strings are special formatters that consist of two parts separated by a pipe |, with no surrounding brackets.\n\n"
            "   Example: building_state_modifier|dam.\n\n"
            "   These strings are code references and MUST NOT be translated. Preserve them completely.\n\n"
            "5. **Internal Keys and Code References**\n\n"
            "   Strings with underscores and no spaces, like example_key or party_popularity@democracy, are internal keys. They MUST NOT be translated.\n\n"
            "6. **Line Breaks**\n\n"
            "   Preserve all internal newlines (\\n) exactly as they appear in the source.\n\n"
            "--- INPUT LIST ---\n{numbered_list}\n--- END OF INPUT LIST ---"
        ),
    },
    "5": {
        "id": "ck3",
        "name": "Crusader Kings III (十字军之王3)",
        "supported_language_keys": ["1", "2", "3", "4", "5", "6" , "8",  "10"],#9种语言不支持日语、葡萄牙语和土耳其语
        "source_localization_folder": "localization", # same as V3
        "protected_items": {'descriptor.mod', 'localization', 'thumbnail.png'}, # same as stellaris /HOI4
        "metadata_file": 'descriptor.mod', # same as stellaris /HOI4
        "encoding": "utf-8-sig", 
        "strip_pl_diacritics": False,
        "prompt_template": (
            "You are a professional translator specializing in the grand strategy game Crusader Kings III, set in the Middle Ages. "
            "Translate the following numbered list of texts from {source_lang_name} to {target_lang_name}.\n"
            "The tone must be appropriate for a role-playing game focused on characters, dynasties, and medieval intrigue."
        ),
        "single_prompt_template": (
            "You are a direct, one-to-one translation engine. "
            "The text you are translating is for a Crusader Kings III game mod named '{mod_name}'. "
            "Translate the following {task_description} from {source_lang_name} to {target_lang_name}.\n"
        ),
        "format_prompt": (
            "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
            "{chunk_size}. "
            "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
            "DO NOT merge, add, or omit lines. DO NOT add any explanations or notes.\n\n"
            "Preserve the following Crusader Kings III specific syntax rules precisely:\n\n"
            "1. **Data Functions and Linking ([...])**\n\n"
            "   This syntax is used to get dynamic text from game data. The entire structure inside the brackets MUST be preserved.\n\n"
            "   a. **Scopes and Functions**: Preserve commands like [ROOT.Char.GetLadyLord] completely. Do not translate any part of them.\n\n"
            "   b. **Function Arguments (using |)**: A pipe | at the end of a function applies formatting. Preserve the function and the entire argument.\n\n"
            "       Examples: [ROOT.Char.GetLadyLord|U] (uppercase first letter), [some_value|2] (round to 2 decimals), [GetFullName|P] (formats as positive/green).\n\n"
            "   c. **Linking to Game Concepts**: A very common and specific use case.\n\n"
            "       Preserve simple links like [faith|E] or [faith|El] (for lowercase).\n\n"
            "       For alternate text forms like [Concept('faith','religion')|E], you MUST preserve the function structure [Concept('faith','...')|E], but the user-facing text, in this case 'religion', SHOULD BE translated.\n\n"
            "   d. **Linking to Traits/Titles**: Preserve complex function calls like [GetTrait('trait_name').GetName( CHARACTER.Self )] or [GetTitleByKey('title_name').GetName] completely.\n\n"
            "2. **String Nesting and Variables ($...$)**\n\n"
            "   This syntax has two main uses. The entire $key$ structure MUST be preserved.\n\n"
            "   a. **Nesting Other Keys**: Re-uses another localization key, e.g., $special_contract_march_short$.\n\n"
            "   b. **Game Engine Variables**: Displays a value from the game. These can have special formatting.\n\n"
            "       Example: $VALUE|=+0$. The unique |=... formatting MUST be preserved completely.\n\n"
            "3. **Text Formatting (#...#!)**\n\n"
            "   These commands start with a #key, followed by a required space, the text, and an end tag #!.\n\n"
            "   You MUST preserve the #key and #! tags. The text between them SHOULD be translated.\n\n"
            "   a. **Basic Formatting**: Examples include #P text#! (positive/green), #N text#! (negative/red), #bold text#!, #italic text#!.\n\n"
            "   b. **Combined Formatting**: Formatting can be combined with a semicolon ;. Preserve the entire combined key.\n\n"
            "       Example: #high;bold.\n\n"
            "4. **Icons (@icon_name!)**\n\n"
            "   These are self-contained icon tags. The entire tag, including @ and !, MUST be preserved completely.\n\n"
            "   Example: @gold_icon!.\n\n"
            "5. **Basic Characters (\\n, \\\")**\n\n"
            "   Preserve all internal newlines (\\n) and escaped double quotes (\\\") exactly as they appear in the source.\n\n"
            "6. **Medieval Terminology**\n\n"
            "   Preserve all medieval, feudal, and dynastic terminology accurately. Maintain the medieval, courtly tone appropriate for medieval role-playing and dynasty management.\n\n"
            "--- INPUT LIST ---\n{numbered_list}\n--- END OF INPUT LIST ---"
        ),
    }
}

# --- 保底格式提示模板 ---------------------------------------------
# 当某个游戏配置中没有专门的format_prompt时，使用这个保底选项
FALLBACK_FORMAT_PROMPT = (
    "CRITICAL FORMATTING: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
    "{chunk_size}. "
    "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
    "DO NOT merge, add, or omit lines. DO NOT add any explanations. "
    "There are two types of special syntax:\n"
    "1. **Variables** like `$variable$`, `[Concept('key', '$concept_name$')]`, `[SCOPE.some.Function]`. You MUST preserve these variables completely. DO NOT translate any text inside them.\n"
    "2. **Formatting Tags** like `#R ... #!`, `§Y...§!`. You MUST preserve the tags themselves (e.g., `#R`, `#!`), but you SHOULD translate the plain text that is inside them.\n"
    "3. **Icon Tags** like `@prestige!`, `£minerals£`. These are variables. You MUST preserve them completely. DO NOT translate any text inside them.\n"
    "4. **Internal Keys** like `mm_strategic_region` or `com_topbar_interests`. These are strings that often contain underscores and no spaces. They are code references and MUST NOT be translated. Preserve them completely.\n"
    "Preserve all internal newlines (\\n).\n\n"
    "--- INPUT LIST ---\n{numbered_list}\n--- END OF INPUT LIST ---"
)
