# scripts/config.py

# 这个文件用于存放所有全局配置变量

# --- 核心配置 ---
MODEL_NAME = 'gemini-2.5-flash'
CHUNK_SIZE = 150

# --- 路径配置 ---
SOURCE_DIR = 'source_mod'
DEST_DIR = 'my_translation'

# --- 语言数据库 ---
# scripts/config.py -> LANGUAGES 字典

LANGUAGES = {
    "1": {"code": "en", "key": "l_english", "name": "English", "folder_prefix": "EN-"},
    "2": {"code": "zh-CN", "key": "l_simp_chinese", "name": "简体中文", "folder_prefix": "汉化-"},
    "3": {"code": "fr", "key": "l_french", "name": "Français", "folder_prefix": "FR-"},
    "4": {"code": "de", "key": "l_german", "name": "Deutsch", "folder_prefix": "DE-"},
    "5": {"code": "es", "key": "l_spanish", "name": "Español", "folder_prefix": "ES-"},
    "6": {"code": "ja", "key": "l_japanese", "name": "日本語", "folder_prefix": "日本語化-"},
    "7": {"code": "ko", "key": "l_korean", "name": "한국어", "folder_prefix": "한국어-"},
    "8": {"code": "pl", "key": "l_polish", "name": "Polski", "folder_prefix": "PL-"},
    "9": {"code": "pt-BR", "key": "l_braz_por", "name": "Português do Brasil", "folder_prefix": "PT-BR-"},
    "10": {"code": "ru", "key": "l_russian", "name": "Русский", "folder_prefix": "RU-"},
    "11": {"code": "tr", "key": "l_turkish", "name": "Türkçe", "folder_prefix": "TR-"}
}