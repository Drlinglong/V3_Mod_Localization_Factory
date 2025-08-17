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
        "encoding": "cp1252",         # klasyczne „ANSI” Paradoxu
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
    }
}
