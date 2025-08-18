#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标点符号处理工具模块

提供智能的标点符号转换功能，支持多语言标点符号的自动转换
重构版本：消除重复代码，明确函数职责，遵循单一职责原则
"""

from ..config import LANGUAGE_PUNCTUATION_CONFIG, TARGET_LANGUAGE_PUNCTUATION

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

def clean_punctuation_core(text: str, source_lang: str, target_lang: str = None) -> str:
    """
    核心标点符号清理函数 - 唯一的"工人"函数
    
    这个函数负责执行实际的标点符号替换操作，是唯一真正做清理工作的函数
    
    重要：只替换源语言的标点符号，英文标点符号绝对不能替换
    这样可以保护游戏格式语法，如 [Root.GetName], $variable$, §Ytext§! 等
    
    Args:
        text: 要清理的文本
        source_lang: 源语言代码
        target_lang: 目标语言代码（可选，如果提供则尝试使用目标语言特定配置）
        
    Returns:
        清理后的文本
    """
    source_punctuation = get_source_language_punctuation(source_lang)
    if not source_punctuation:
        return text
    
    # 如果指定了目标语言且有配置，尝试使用目标语言特定的映射
    if target_lang and target_lang in LANGUAGE_PUNCTUATION_CONFIG:
        target_punctuation = LANGUAGE_PUNCTUATION_CONFIG[target_lang]["punctuation"]
        # 创建源语言到目标语言的映射
        mapping = {}
        for source_punct in source_punctuation.keys():
            if source_punct in target_punctuation:
                mapping[source_punct] = target_punctuation[source_punct]
            else:
                # 如果目标语言没有对应配置，使用英文标点作为默认值
                mapping[source_punct] = source_punctuation[source_punct]
    else:
        # 使用默认的英文标点映射
        mapping = source_punctuation
    
    # 执行替换 - 只替换源语言标点，绝对不替换英文标点
    # 这样可以保护游戏格式语法，如 [Root.GetName], $variable$, §Ytext§! 等
    cleaned_text = text
    for source_punct, target_punct in mapping.items():
        # 重要：只替换源语言标点，不替换英文标点
        # 例如：中文的"，。！？：；（）【】《》" 变成英文的 ",.!?:;()[]<>"
        # 但是英文的 "[Root.GetName]", "$variable$", "§Ytext§!" 保持不变
        cleaned_text = cleaned_text.replace(source_punct, target_punct)
    
    return cleaned_text

def analyze_punctuation(text: str, source_lang: str) -> dict:
    """
    标点符号分析函数 - 纯粹的"分析师"函数
    
    这个函数只负责分析文本中的标点符号，不进行任何修改
    
    Args:
        text: 要分析的文本
        source_lang: 源语言代码
        
    Returns:
        包含分析结果的字典
    """
    source_punctuation = get_source_language_punctuation(source_lang)
    if not source_punctuation:
        return {
            "found": False,
            "total": 0,
            "details": {},
            "source_language": source_lang,
            "reason": "source_language_not_supported"
        }
    
    stats = {
        "found": False,
        "total": 0,
        "details": {},
        "source_language": source_lang
    }
    
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

def clean_text_with_analysis(text: str, source_lang: str, target_lang: str = None) -> tuple[str, dict]:
    """
    主接口函数 - "项目经理"函数
    
    这个函数协调清理和分析工作，对外提供清晰、简单的接口
    
    Args:
        text: 要清理的文本
        source_lang: 源语言代码
        target_lang: 目标语言代码（可选）
        
    Returns:
        (清理后的文本, 分析统计信息)
    """
    # 首先分析原始文本
    original_stats = analyze_punctuation(text, source_lang)
    
    # 如果没有找到需要清理的标点符号，直接返回
    if not original_stats["found"]:
        return text, {
            **original_stats,
            "cleaned": False,
            "method": "no_cleaning_needed"
        }
    
    # 执行清理
    cleaned_text = clean_punctuation_core(text, source_lang, target_lang)
    
    # 分析清理后的文本
    cleaned_stats = analyze_punctuation(cleaned_text, source_lang)
    
    # 构建完整的统计报告
    final_stats = {
        **original_stats,
        "cleaned": True,
        "method": "punctuation_conversion",
        "replacements_made": original_stats["total"] - cleaned_stats["total"],
        "target_language": target_lang if target_lang else "english_fallback"
    }
    
    return cleaned_text, final_stats

def generate_punctuation_prompt(source_lang: str, target_lang: str) -> str:
    """
    根据源语言和目标语言生成标点符号转换提示词
    
    Args:
        source_lang: 源语言代码 (如 "zh-CN", "ja", "ko")
        target_lang: 目标语言代码 (如 "en", "it", "fr")
        
    Returns:
        生成的提示词字符串，如果源语言不支持则返回空字符串
    """
    if source_lang not in LANGUAGE_PUNCTUATION_CONFIG:
        return ""
    
    source_config = LANGUAGE_PUNCTUATION_CONFIG[source_lang]
    
    # 检查目标语言是否有配置
    if target_lang in LANGUAGE_PUNCTUATION_CONFIG:
        # 目标语言有配置，使用具体的标点符号映射
        target_config = LANGUAGE_PUNCTUATION_CONFIG[target_lang]
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
    else:
        # 目标语言没有配置，使用保底提示词
        return get_fallback_punctuation_prompt(source_lang, target_lang)
    
    return "\n".join(prompt_parts)

def get_fallback_punctuation_prompt(source_lang: str, target_lang: str) -> str:
    """
    生成保底标点符号转换提示词
    
    当目标语言不在配置中时，生成一个通用的提示词
    
    Args:
        source_lang: 源语言代码
        target_lang: 目标语言代码
        
    Returns:
        生成的提示词字符串
    """
    if source_lang not in LANGUAGE_PUNCTUATION_CONFIG:
        return ""
    
    source_config = LANGUAGE_PUNCTUATION_CONFIG[source_lang]
    
    prompt_parts = [
        f"PUNCTUATION CONVERSION: Convert all {source_config['name']} punctuation marks to {target_lang.upper()} language equivalents.",
        "",
        "Examples:",
        "- Convert Chinese punctuation (，。！？：；（）【】《》""''…—) to target language equivalents",
        "- Convert Japanese punctuation (、。！？：；（）【】「」『』・…—～) to target language equivalents",
        "- Convert Korean punctuation (，。！？：；（）［］｛｝《》「」『』) to target language equivalents",
        "",
        "Rules:",
        "- Convert ALL punctuation marks from source language to target language",
        "- Preserve special syntax markers (e.g., §G, [Root.Variable], $VAR$)",
        "- Maintain text meaning and structure",
        "- Use standard punctuation marks appropriate for the target language"
    ]
    
    return "\n".join(prompt_parts)

# 向后兼容的别名函数（为了不破坏现有代码）
def clean_language_specific_punctuation(text: str, source_lang: str, target_lang: str) -> str:
    """向后兼容的别名函数，调用新的核心清理函数"""
    return clean_punctuation_core(text, source_lang, target_lang)

def apply_fallback_punctuation_cleaning(text: str, source_lang: str) -> str:
    """向后兼容的别名函数，调用新的核心清理函数"""
    return clean_punctuation_core(text, source_lang)

def detect_and_clean_residual_punctuation(text: str, source_lang: str) -> tuple[str, dict]:
    """向后兼容的别名函数，调用新的主接口函数"""
    return clean_text_with_analysis(text, source_lang)

def clean_text_with_fallback(text: str, source_lang: str, target_lang: str) -> tuple[str, dict]:
    """向后兼容的别名函数，调用新的主接口函数"""
    return clean_text_with_analysis(text, source_lang, target_lang)

# 使用示例和测试函数
if __name__ == "__main__":
    # 测试用例：中文翻译为意大利语
    source_lang = "zh-CN"
    target_lang = "it"  # 意大利语，不在配置中
    
    print("=== 测试重构后的标点符号处理机制 ===")
    print(f"源语言: {source_lang}")
    print(f"目标语言: {target_lang}")
    print()
    
    # 1. 生成prompt
    prompt = generate_punctuation_prompt(source_lang, target_lang)
    print("生成的Prompt:")
    print(prompt)
    print()
    
    # 2. 模拟AI翻译后的文本（仍包含中文标点）
    ai_translated_text = "Ciao, mondo! Questo è un test：punteggiatura.（importante）informazione"
    print("AI翻译后的文本（包含残留中文标点）:")
    print(ai_translated_text)
    print()
    
    # 3. 测试新的清理方法
    print("=== 新的清理方法测试 ===")
    
    # 使用主接口函数
    cleaned_text, stats = clean_text_with_analysis(ai_translated_text, source_lang, target_lang)
    print("清理结果:")
    print(f"原文: {ai_translated_text}")
    print(f"清理后: {cleaned_text}")
    print(f"统计信息: {stats}")
    print()
    
    # 4. 测试英文格式语法保护
    print("=== 测试英文格式语法保护 ===")
    test_text_with_formats = "这是一个测试：[Root.GetName] 和 $variable$ 还有 §Ytext§! 以及 (important)"
    print("包含游戏格式语法的测试文本:")
    print(test_text_with_formats)
    
    # 清理中文标点，但保护英文格式
    cleaned_formats, format_stats = clean_text_with_analysis(test_text_with_formats, source_lang, target_lang)
    print("清理后（英文格式应该被保护）:")
    print(cleaned_formats)
    print(f"格式保护统计: {format_stats}")
    print()
    
    # 5. 测试英文标点完全不被处理
    print("=== 测试英文标点完全不被处理 ===")
    test_english_punctuation = "Hello, world! This is a test: [Root.GetName] and $variable$ with §Ytext§!"
    print("包含英文标点的测试文本:")
    print(test_english_punctuation)
    
    # 尝试清理英文标点（应该完全跳过）
    cleaned_english, english_stats = clean_text_with_analysis(test_english_punctuation, source_lang, target_lang)
    print("清理后（英文标点应该完全不被处理）:")
    print(cleaned_english)
    print(f"英文标点处理统计: {english_stats}")
    print()
    
    # 6. 验证源语言标点映射
    print("=== 验证源语言标点映射 ===")
    source_punct = get_source_language_punctuation(source_lang)
    print(f"源语言 {source_lang} 的标点符号映射:")
    for zh_punct, en_punct in list(source_punct.items())[:5]:  # 只显示前5个
        print(f"  {zh_punct} → {en_punct}")
    print(f"  总共 {len(source_punct)} 个源语言标点符号")
    print()
    print("注意：英文标点符号（如 [, ], $, §, ! 等）根本不在这个映射中，所以不会被处理！")
    print()
    
    print("=== 函数职责说明 ===")
    print("1. clean_punctuation_core: 核心清理函数，唯一的'工人'，负责执行替换")
    print("2. analyze_punctuation: 分析函数，纯粹的'分析师'，只分析不修改")
    print("3. clean_text_with_analysis: 主接口函数，'项目经理'，协调清理和分析")
    print()
    print("=== 使用建议 ===")
    print("- 一般使用: clean_text_with_analysis() - 清理并获取统计信息")
    print("- 只需要清理: clean_punctuation_core() - 只执行清理，不返回统计")
    print("- 只需要分析: analyze_punctuation() - 只分析，不修改文本")
    print()
    print("=== 重构优势 ===")
    print("✓ 消除了重复代码，遵循DRY原则")
    print("✓ 每个函数职责单一，遵循单一职责原则")
    print("✓ 清晰的调用层次，易于理解和维护")
    print("✓ 向后兼容，不破坏现有代码")
    print("✓ 保护英文格式语法，不会破坏游戏格式")
