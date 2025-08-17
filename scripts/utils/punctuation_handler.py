#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标点符号处理工具模块

提供智能的标点符号转换功能，支持多语言标点符号的自动转换
"""

from scripts.config import LANGUAGE_PUNCTUATION_CONFIG, TARGET_LANGUAGE_PUNCTUATION

def generate_punctuation_prompt(source_lang: str, target_lang: str) -> str:
    """
    根据源语言和目标语言智能生成标点符号转换提示词
    
    Args:
        source_lang: 源语言代码 (如 "zh-CN", "ja", "ko")
        target_lang: 目标语言代码 (如 "en")
        
    Returns:
        生成的提示词字符串，如果源语言不支持则返回空字符串
    """
    
    if source_lang not in LANGUAGE_PUNCTUATION_CONFIG:
        return ""  # 如果源语言不支持，返回空字符串
    
    source_config = LANGUAGE_PUNCTUATION_CONFIG[source_lang]
    target_config = TARGET_LANGUAGE_PUNCTUATION.get(target_lang, TARGET_LANGUAGE_PUNCTUATION["en"])
    
    # 构建智能提示词
    prompt_parts = [
        f"PUNCTUATION CONVERSION: Convert all {source_config['name']} punctuation to {target_config['name']} equivalents.",
        "",
        "Examples:"
    ]
    
    # 添加具体示例
    for example in source_config['examples']:
        prompt_parts.append(f"- {example}")
    
    prompt_parts.extend([
        "",
        "Rules:",
        "- Convert ALL punctuation marks from source language to target language",
        "- Preserve special syntax markers (e.g., §G, [Root.Variable], $VAR$)",
        "- Maintain text meaning and structure"
    ])
    
    return "\n".join(prompt_parts)

def get_source_language_punctuation(source_lang: str) -> dict:
    """
    获取源语言的标点符号映射
    
    Args:
        source_lang: 源语言代码
        
    Returns:
        标点符号映射字典，如果源语言不支持则返回空字典
    """
    if source_lang in LANGUAGE_PUNCTUATION_CONFIG:
        return LANGUAGE_PUNCTUATION_CONFIG[source_lang]["punctuation"]
    return {}

def clean_language_specific_punctuation(text: str, source_lang: str, target_lang: str) -> str:
    """
    根据源语言和目标语言智能清理标点符号
    
    Args:
        text: 要清理的文本
        source_lang: 源语言代码
        target_lang: 目标语言代码
        
    Returns:
        清理后的文本
    """
    
    # 获取源语言的标点符号
    source_punctuation = get_source_language_punctuation(source_lang)
    if not source_punctuation:
        return text  # 如果源语言不支持，直接返回
    
    # 执行转换
    cleaned_text = text
    for source_punct, target_punct in source_punctuation.items():
        cleaned_text = cleaned_text.replace(source_punct, target_punct)
    
    return cleaned_text

def has_language_specific_punctuation(text: str, source_lang: str) -> bool:
    """
    检查文本是否包含源语言特有的标点符号
    
    Args:
        text: 要检查的文本
        source_lang: 源语言代码
        
    Returns:
        如果包含源语言标点符号则返回True，否则返回False
    """
    source_punctuation = get_source_language_punctuation(source_lang)
    if not source_punctuation:
        return False
    
    return any(punct in text for punct in source_punctuation.keys())

def get_punctuation_statistics(text: str, source_lang: str) -> dict:
    """
    获取文本中源语言标点符号的统计信息
    
    Args:
        text: 要分析的文本
        source_lang: 源语言代码
        
    Returns:
        包含统计信息的字典
    """
    source_punctuation = get_source_language_punctuation(source_lang)
    if not source_punctuation:
        return {"total": 0, "details": {}, "found": False}
    
    stats = {"total": 0, "details": {}, "found": False}
    
    for punct, replacement in source_punctuation.items():
        count = text.count(punct)
        if count > 0:
            stats["details"][punct] = {
                "count": count,
                "replacement": replacement
            }
            stats["total"] += count
            stats["found"] = True
    
    return stats
