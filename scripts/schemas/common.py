from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class LanguageCode(str, Enum):
    """ISO 639-1 代码 - 这是数据库存储的唯一合法格式"""
    EN = "en"
    ZH_CN = "zh-CN"
    FR = "fr"
    DE = "de"
    ES = "es"
    JA = "ja"
    KO = "ko"
    PL = "pl"
    PT_BR = "pt-BR"
    RU = "ru"
    TR = "tr"

    @classmethod
    def from_str(cls, value: str):
        """
        强力清洗器：能把 'English', 'english', 'l_english' 统统自动转成 'en'。
        """
        if not value:
            raise ValueError("语言代码不能为空")
            
        value = value.lower().strip()
        # 别名映射表
        mapping = {
            # English
            "english": cls.EN, "l_english": cls.EN, "en_us": cls.EN, "en": cls.EN,
            # Chinese
            "chinese": cls.ZH_CN, "simp_chinese": cls.ZH_CN, "l_simp_chinese": cls.ZH_CN, "zh": cls.ZH_CN, "zh_cn": cls.ZH_CN, "zh-cn": cls.ZH_CN,
            # French
            "french": cls.FR, "l_french": cls.FR, "fr": cls.FR,
            # German
            "german": cls.DE, "l_german": cls.DE, "de": cls.DE,
            # Spanish
            "spanish": cls.ES, "l_spanish": cls.ES, "es": cls.ES,
            # Japanese
            "japanese": cls.JA, "l_japanese": cls.JA, "ja": cls.JA,
            # Korean
            "korean": cls.KO, "l_korean": cls.KO, "ko": cls.KO,
            # Polish
            "polish": cls.PL, "l_polish": cls.PL, "pl": cls.PL,
            # Portuguese
            "braz_por": cls.PT_BR, "l_braz_por": cls.PT_BR, "pt": cls.PT_BR, "pt_br": cls.PT_BR, "pt-br": cls.PT_BR, "portuguese": cls.PT_BR,
            # Russian
            "russian": cls.RU, "l_russian": cls.RU, "ru": cls.RU,
            # Turkish
            "turkish": cls.TR, "l_turkish": cls.TR, "tr": cls.TR,
        }
        
        if value in mapping:
            return mapping[value]
            
        # 兜底：尝试直接匹配枚举值
        try:
            return cls(value)
        except ValueError:
            # 再次尝试匹配 value (case-insensitive check against enum values)
            for member in cls:
                if member.value.lower() == value:
                    return member
            raise ValueError(f"不支持的语言代码: {value}")

class ProjectID(str):
    """
    类型别名：明确指示这个字符串必须是文件夹名 (ID)，绝不能是显示名称。
    """
    pass
