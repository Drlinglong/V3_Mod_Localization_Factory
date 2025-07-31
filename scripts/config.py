# scripts/config.py

# 这个文件用于存放所有全局配置变量

# --- 核心配置 ---
MODEL_NAME = 'gemini-2.5-flash'
CHUNK_SIZE = 150

# --- 路径配置 ---
SOURCE_DIR = 'source_mod'
DEST_DIR = 'my_translation'

# --- 语言数据库 ---
# 根据你提供的官方语言表创建
LANGUAGES = {
    "1": {"code": "en", "key": "l_english", "name": "English"},
    "2": {"code": "zh-CN", "key": "l_simp_chinese", "name": "简体中文"},
    "3": {"code": "fr", "key": "l_french", "name": "Français"},
    "4": {"code": "de", "key": "l_german", "name": "Deutsch"},
    "5": {"code": "es", "key": "l_spanish", "name": "Español"},
    "6": {"code": "ja", "key": "l_japanese", "name": "日本語"},
    "7": {"code": "ko", "key": "l_korean", "name": "한국어"},
    "8": {"code": "pl", "key": "l_polish", "name": "Polski"},
    "9": {"code": "pt-BR", "key": "l_braz_por", "name": "Português do Brasil"},
    "10": {"code": "ru", "key": "l_russian", "name": "Русский"},
    "11": {"code": "tr", "key": "l_turkish", "name": "Türkçe"}
}