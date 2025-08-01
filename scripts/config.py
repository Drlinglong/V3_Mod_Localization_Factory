# scripts/config.py
import os # 导入os模块以备后用

# --- 核心配置 ---
MODEL_NAME = 'gemini-2.5-flash'
CHUNK_SIZE = 60

# --- 路径配置 ---
SOURCE_DIR = 'source_mod'
DEST_DIR = 'my_translation'

# --- 语言数据库 ---
LANGUAGES = {
    "1": {"code": "en", "key": "l_english", "name": "English", "folder_prefix": "en-"},
    "2": {"code": "zh-CN", "key": "l_simp_chinese", "name": "简体中文", "folder_prefix": "zh-CN-"},
    "3": {"code": "fr", "key": "l_french", "name": "Français", "folder_prefix": "fr-"},
    "4": {"code": "de", "key": "l_german", "name": "Deutsch", "folder_prefix": "de-"},
    "5": {"code": "es", "key": "l_spanish", "name": "Español", "folder_prefix": "es-"},
    "6": {"code": "ja", "key": "l_japanese", "name": "日本語", "folder_prefix": "ja-"},
    "7": {"code": "ko", "key": "l_korean", "name": "한국어", "folder_prefix": "ko-"},
    "8": {"code": "pl", "key": "l_polish", "name": "Polski", "folder_prefix": "pl-"},
    "9": {"code": "pt-BR", "key": "l_braz_por", "name": "Português do Brasil", "folder_prefix": "pt-BR-"},
    "10": {"code": "ru", "key": "l_russian", "name": "Русский", "folder_prefix": "ru-"},
    "11": {"code": "tr", "key": "l_turkish", "name": "Türkçe", "folder_prefix": "tr-"}
}

# --- 游戏档案数据库 ---
GAME_PROFILES = {
    "1": {
        "id": "victoria3",
        "name": "Victoria 3 (维多利亚3)",
        "source_localization_folder": "localization",
        "protected_items": {'.metadata', 'localization', 'thumbnail.png'},
        "metadata_file": os.path.join('.metadata', 'metadata.json'), # V3的元数据文件路径
        "prompt_template": (
            "You are a professional translator specializing in the grand strategy game Victoria 3, set in the 19th and early 20th centuries. "
            "Translate the following numbered list of texts from {source_lang_name} to {target_lang_name}.\n"
        ),
        "single_prompt_template": (
            "You are a direct, one-to-one translation engine. "
            "The text you are translating is for a Victoria 3 game mod named '{mod_name}'. "
            "Translate the following {task_description} from {source_lang_name} to {target_lang_name}.\n"
        )
    },
    "2": {
        "id": "stellaris",
        "name": "Stellaris (群星)",
        "source_localization_folder": "localisation",
        "protected_items": {'descriptor.mod', 'localisation', 'thumbnail.png'},
        "metadata_file": 'descriptor.mod', # 群星的元数据文件名
        "prompt_template": (
            "You are a professional translator specializing in the grand strategy science fiction game Stellaris. "
            "Translate the following numbered list of texts from {source_lang_name} to {target_lang_name}.\n"
        ),
        "single_prompt_template": (
            "You are a direct, one-to-one translation engine. "
            "The text you are translating is for a Stellaris game mod named '{mod_name}'. "
            "Translate the following {task_description} from {source_lang_name} to {target_lang_name}.\n"
        )
    }
}