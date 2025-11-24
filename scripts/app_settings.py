# scripts/app_settings.py
# ---------------------------------------------------------------
import os
import multiprocessing
from scripts.config import prompts

# Global switch for archiving translation results
ARCHIVE_RESULTS_AFTER_TRANSLATION = True

# --- 项目信息 ----------------------------------------------------
PROJECT_NAME = "Paradox Mod 本地化工厂 - Paradox Mod Localization Factory"
PROJECT_DISPLAY_NAME = "蕾姆丝计划 - Project Remis "
VERSION = "1.2.2"
LAST_UPDATE_DATE = "2025-11-13"
COPYRIGHT = "© 2025 Project Remis Team"

# --- 项目信息显示配置 --------------------------------------------
PROJECT_INFO = {
    "display_name": PROJECT_DISPLAY_NAME,
    "engineering_name": PROJECT_NAME,
    "version": VERSION,
    "last_update": LAST_UPDATE_DATE,
    "copyright": COPYRIGHT
}

# --- 核心配置 ----------------------------------------------------
CHUNK_SIZE = 40
MAX_RETRIES = 2

# --- Gemini CLI 特定配置 -----------------------------------------
GEMINI_CLI_CHUNK_SIZE = 100
GEMINI_CLI_MAX_RETRIES = 2

# --- Ollama 特定配置 ---------------------------------------------
OLLAMA_CHUNK_SIZE = 20
OLLAMA_MAX_RETRIES = 2

# --- 智能线程池配置 ----------------------------------------------------
def get_smart_max_workers():
    cpu_count = multiprocessing.cpu_count() or 1
    return min(32, cpu_count * 2)

RECOMMENDED_MAX_WORKERS = get_smart_max_workers()
BATCH_SIZE = CHUNK_SIZE

# --- 路径配置 ----------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SOURCE_DIR = os.path.join(PROJECT_ROOT, 'source_mod')
DEST_DIR = os.path.join(PROJECT_ROOT, 'my_translation')

# --- Database Paths ---
PROJECTS_DB_PATH = os.path.join(DATA_DIR, "projects.sqlite")
MODS_CACHE_DB_PATH = os.path.join(DATA_DIR, "mods_cache.sqlite")
TRANSLATION_PROGRESS_DB_PATH = os.path.join(DATA_DIR, "translation_progress.sqlite")

# --- API Provider Configuration ---
DEFAULT_API_PROVIDER = "gemini"

API_PROVIDERS = {
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "default_model": "gemini-2.5-flash",
        "enable_thinking": False,
        "thinking_budget": 0,
    },
    "gemini_cli": {
        "cli_path": "gemini",
        "default_model": "gemini-2.5-flash",
        "enable_thinking": True,
        "thinking_budget": -1,
        "chunk_size": GEMINI_CLI_CHUNK_SIZE,
        "max_retries": GEMINI_CLI_MAX_RETRIES,
        "max_daily_calls": 1000,
        "description": "通过Google Gemini CLI调用，每天1000次免费，使用2.5 Pro模型，支持并行处理"
    },
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "default_model": "gpt-5-mini",
        "enable_thinking": False,
        "reasoning_effort": "minimal"
    },
    "qwen": {
        "api_key_env": "DASHSCOPE_API_KEY",
        "default_model": "qwen-plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "region": "beijing",
        "enable_thinking": False,
    },
    "grok": {
        "api_key_env": "XAI_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "default_model": "grok-4-fast-reasoning",
        "description": "通过xAI官方API访问grok-4-fast-reasoning模型"
    },
    "deepseek": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "enable_thinking": False,
        "description": "DeepSeek-V3.2-Exp (Non-thinking Mode) - 与OpenAI API兼容"
    },
    "ollama": {
        "base_url_env": "OLLAMA_BASE_URL",
        "default_model": "qwen3:4b",
        "enable_thinking": False,
        "chunk_size": OLLAMA_CHUNK_SIZE,
        "max_retries": OLLAMA_MAX_RETRIES,
        "description": "本地Ollama模型，无需API密钥"
    },
    "modelscope": {
        "api_key_env": "MODELSCOPE_API_KEY",
        "base_url": "https://api-inference.modelscope.cn/v1/",
        "default_model": "deepseek-ai/DeepSeek-V3.2-Exp",
        "description": "通过魔搭（ModelScope）调用AI模型"
    },
    "siliconflow": {
        "api_key_env": "SILICONFLOW_API_KEY",
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "DeepSeek-R1",
        "description": "通过硅基流动（SiliconFlow）调用AI模型"
    },
    "your_favourite_api": {
        "api_key_env": "YOUR_FAVOURITE_API_KEY",
        "base_url": "YOUR_BASE_URL_HERE",
        "default_model": "YOUR_MODEL_NAME_HERE",
        "description": "（需要技术知识）连接到您自选的任何兼容OpenAI的API服务"
    },
}

# --- 语言数据库 --------------------------------------------------
LANGUAGES = {
    "1":  {"code": "en",     "key": "l_english",      "name": "English",             "name_en": "English",             "folder_prefix": "en-"},
    "2":  {"code": "zh-CN",  "key": "l_simp_chinese", "name": "简体中文",             "name_en": "Simplified Chinese",  "folder_prefix": "zh-CN-"},
    "3":  {"code": "fr",     "key": "l_french",       "name": "Français",            "name_en": "French",              "folder_prefix": "fr-"},
    "4":  {"code": "de",     "key": "l_german",       "name": "Deutsch",             "name_en": "German",              "folder_prefix": "de-"},
    "5":  {"code": "es",     "key": "l_spanish",      "name": "Español",             "name_en": "Spanish",             "folder_prefix": "es-"},
    "6":  {"code": "ja",     "key": "l_japanese",     "name": "日本語",               "name_en": "Japanese",            "folder_prefix": "ja-"},
    "7":  {"code": "ko",     "key": "l_korean",       "name": "한국어",               "name_en": "Korean",              "folder_prefix": "ko-"},
    "8":  {"code": "pl",     "key": "l_polish",       "name": "Polski",              "name_en": "Polish",              "folder_prefix": "pl-"},
    "9":  {"code": "pt-BR",  "key": "l_braz_por",     "name": "Português do Brasil", "name_en": "Brazilian Portuguese", "folder_prefix": "pt-BR-"},
    "10": {"code": "ru",     "key": "l_russian",      "name": "Русский",             "name_en": "Russian",             "folder_prefix": "ru-"},
    "11": {"code": "tr",     "key": "l_turkish",      "name": "Türkçe",              "name_en": "Turkish",             "folder_prefix": "tr-"}
}

# --- 语言标点符号配置 --------------------------------------------------
LANGUAGE_PUNCTUATION_CONFIG = {
    "zh-CN": {"name": "简体中文", "punctuation": {"，": ",", "。": ".", "！": "!", "？": "?", "：": ":", "；": ";", "（": "(", "）": ")", "【": "[", "】": "]", "《": "<", "》": ">", "“": "\"", "”": "\"", "‘": "'", "’": "'", "…": "...", "—": "-", "－": "-", "　": " ", "、": ",", "·": ".", "～": "~", "％": "%", "＃": "#", "＄": "$", "＆": "&", "＊": "*", "＋": "+", "＝": "=", "／": "/", "＼": "\\", "｜": "|", "＠": "@"}, "examples": ["你好，世界！", "这是一个测试：标点符号。", "（重要）信息"]},
    "ja": {"name": "日本語", "punctuation": {"、": ",", "。": ".", "！": "!", "？": "?", "：": ":", "；": ";", "（": "(", "）": ")", "【": "[", "】": "]", "「": "\"", "」": "\"", "『": "'", "』": "'", "・": "·", "…": "...", "—": "-", "～": "~"}, "examples": ["こんにちは、世界！", "これはテストです：句読点。", "（重要）情報"]},
    "ko": {"name": "한국어", "punctuation": {"，": ",", "。": ".", "！": "!", "？": "?", "：": ":", "；": ";", "（": "(", "）": ")", "［": "[", "］": "]", "｛": "{", "｝": "}", "《": "<", "》": ">", "「": "\"", "」": "\"", "『": "'", "』": "'"}, "examples": ["안녕하세요, 세계!", "이것은 테스트입니다: 문장 부호.", "（중요）정보"]},
    "ru": {"name": "Русский", "punctuation": {"«": "\"", "»": "\"", "—": "-", "…": "...", "№": "#"}, "examples": ["Привет, мир!", "Это тест: пунктуация.", "«Важная» информация"]},
    "fr": {"name": "Français", "punctuation": {"«": "\"", "»": "\"", "‹": "'", "›": "'", "…": "...", "—": "-", "–": "-"}, "examples": ["Bonjour, monde!", "C'est un test: ponctuation.", "«Important» information"]},
    "es": {"name": "Español", "punctuation": {"¿": "?", "¡": "!", "«": "\"", "»": "\"", "…": "...", "—": "-", "–": "-"}, "examples": ["¿Hola, mundo!", "¡Es una prueba: puntuación!", "«Importante» информация"]},
    "tr": {"name": "Türkçe", "punctuation": {"«": "\"", "»": "\"", "…": "...", "—": "-", "–": "-"}, "examples": ["Merhaba, dünya!", "Bu bir test: noktalama.", "«Önemli» bilgi"]},
    "de": {"name": "Deutsch", "punctuation": {"„": "\"", "“": "\"", "‚": "'", "‘": "'", "…": "...", "—": "-", "–": "-"}, "examples": ["Hallo, Welt!", "Das ist ein Test: Interpunktion.", "„Wichtige Informationen"]},
    "pl": {"name": "Polski", "punctuation": {"„": "\"", "”": "\"", "‚": "'", "’": "'", "…": "...", "—": "-", "–": "-"}, "examples": ["Witaj, świecie!", "To jest test: interpunkcja.", "Ważne informacje"]},
    "pt-BR": {"name": "Português do Brasil", "punctuation": {"“": "\"", "”": "\"", "‘": "'", "’": "'", "…": "...", "—": "-", "–": "-"}, "examples": ["Olá, mundo!", "Este é um teste: pontuação.", "Importante informação"]}
}

TARGET_LANGUAGE_PUNCTUATION = {
    "en": {"name": "English", "punctuation": [".", "!", "?", ":", ";", "(", ")", "[", "]", "<", ">", "\"", "'", "...", "-", "~", "#", "$", "%", "&", "*", "+", "=", "/", "\\", "|", "@"]}
}

# --- 游戏档案数据库 ---------------------------------------------
GAME_PROFILES = {
    "1": {
        "id": "victoria3", "name": "Victoria 3 (维多利亚3)",
        "supported_language_keys": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
        "source_localization_folder": "localization",
        "protected_items": {".metadata", "localization", "thumbnail.png"},
        "metadata_file": os.path.join(".metadata", "metadata.json"),
        "encoding": "utf-8-sig", "strip_pl_diacritics": False,
        "prompt_template": prompts.VICTORIA3_PROMPT_TEMPLATE,
        "single_prompt_template": prompts.VICTORIA3_SINGLE_PROMPT_TEMPLATE,
        "format_prompt": prompts.VICTORIA3_FORMAT_PROMPT,
        "official_tags_codex": "scripts/config/validators/vic3_official_tags.json",
    },
    "2": {
        "id": "stellaris", "name": "Stellaris (群星)",
        "supported_language_keys": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        "source_localization_folder": "localisation",
        "protected_items": {".descriptor.mod", "localisation", "thumbnail.png"},
        "metadata_file": "descriptor.mod",
        "encoding": "utf-8-sig", "strip_pl_diacritics": False,
        "prompt_template": prompts.STELLARIS_PROMPT_TEMPLATE,
        "single_prompt_template": prompts.STELLARIS_SINGLE_PROMPT_TEMPLATE,
        "format_prompt": prompts.STELLARIS_FORMAT_PROMPT,
        "official_tags_codex": "scripts/config/validators/stellaris_official_tags.json",
    },
    "3": {
        "id": "eu4", "name": "Europa Universalis IV (欧陆风云4)",
        "supported_language_keys": ["1", "3", "4", "5"],
        "source_localization_folder": "localisation",
        "protected_items": {".descriptor.mod", "localisation", "thumbnail.png"},
        "metadata_file": "descriptor.mod",
        "encoding": "cp1252", "strip_pl_diacritics": True,
        "prompt_template": prompts.EU4_PROMPT_TEMPLATE,
        "single_prompt_template": prompts.EU4_SINGLE_PROMPT_TEMPLATE,
        "format_prompt": prompts.EU4_FORMAT_PROMPT,
        "official_tags_codex": "scripts/config/validators/eu4_official_tags.json",
    },
    "4": {
        "id": "hoi4", "name": "Hearts of Iron IV (钢铁雄心4)",
        "supported_language_keys": ["1", "2", "3", "4", "5", "6" , "8", "9", "10"],
        "source_localization_folder": "localisation",
        "protected_items": {'descriptor.mod', 'localisation', 'thumbnail.png'},
        "metadata_file": 'descriptor.mod',
        "encoding": "utf-8-sig", "strip_pl_diacritics": False,
        "prompt_template": prompts.HOI4_PROMPT_TEMPLATE,
        "single_prompt_template": prompts.HOI4_SINGLE_PROMPT_TEMPLATE,
        "format_prompt": prompts.HOI4_FORMAT_PROMPT,
        "official_tags_codex": "scripts/config/validators/hoi4_official_tags.json",
    },
    "5": {
        "id": "ck3", "name": "Crusader Kings III (十字军之王3)",
        "supported_language_keys": ["1", "2", "3", "4", "5", "6" , "8",  "10"],
        "source_localization_folder": "localization",
        "protected_items": {'descriptor.mod', 'localisation', 'thumbnail.png'},
        "metadata_file": 'descriptor.mod',
        "encoding": "utf-8-sig", "strip_pl_diacritics": False,
        "prompt_template": prompts.CK3_PROMPT_TEMPLATE,
        "single_prompt_template": prompts.CK3_SINGLE_PROMPT_TEMPLATE,
        "format_prompt": prompts.CK3_FORMAT_PROMPT,
        "official_tags_codex": "scripts/config/validators/ck3_official_tags.json",
    },
    "6": {
        "id": "eu5", "name": "Europa Universalis V (欧陆风云5)",
        "supported_language_keys": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
        "source_localization_folder": "localization", # Will be searched recursively
        "protected_items": {".metadata", "localization", "thumbnail.png"},
        "metadata_file": os.path.join(".metadata", "metadata.json"),
        "encoding": "utf-8-sig", "strip_pl_diacritics": False,
        "prompt_template": prompts.EU5_PROMPT_TEMPLATE,
        "single_prompt_template": prompts.EU5_SINGLE_PROMPT_TEMPLATE,
        "format_prompt": prompts.EU5_FORMAT_PROMPT,
        "official_tags_codex": "", # No official tags yet
    }
}

# --- 保底格式提示模板 ---------------------------------------------
FALLBACK_FORMAT_PROMPT = prompts.FALLBACK_FORMAT_PROMPT
