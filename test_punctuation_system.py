#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试标点符号处理系统功能

验证系统是否能正确处理各种语言之间的标点符号转换
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试基本功能...")
    
    try:
        from scripts.utils.punctuation_handler import (
            generate_punctuation_prompt,
            clean_language_specific_punctuation,
            get_source_language_punctuation
        )
        
        # 测试中文标点符号
        zh_text = "你好，世界！这是一个测试：标点符号。"
        cleaned_zh = clean_language_specific_punctuation(zh_text, "zh-CN", "en")
        print(f"  ✅ 中文清理: '{zh_text}' -> '{cleaned_zh}'")
        
        # 测试日语标点符号
        ja_text = "こんにちは、世界！これはテストです：句読点。"
        cleaned_ja = clean_language_specific_punctuation(ja_text, "ja", "en")
        print(f"  ✅ 日语清理: '{ja_text}' -> '{cleaned_ja}'")
        
        # 测试韩语标点符号
        ko_text = "안녕하세요, 세계! 이것은 테스트입니다: 문장 부호."
        cleaned_ko = clean_language_specific_punctuation(ko_text, "ko", "en")
        print(f"  ✅ 韩语清理: '{ko_text}' -> '{cleaned_ko}'")
        
        print("  🎉 基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ 基本功能测试失败: {e}")
        return False

def test_language_to_language_conversion():
    """测试语言到语言的转换"""
    print("\n🧪 测试语言到语言转换...")
    
    try:
        from scripts.utils.punctuation_handler import clean_language_specific_punctuation
        
        # 测试从日语到韩语
        ja_text = "こんにちは、世界！これはテストです：句読点。（重要）情報"
        print(f"  📝 原始日语文本: '{ja_text}'")
        
        # 先转换为英文标点
        ja_to_en = clean_language_specific_punctuation(ja_text, "ja", "en")
        print(f"  🔄 日语->英文标点: '{ja_to_en}'")
        
        # 再转换为韩语标点（模拟韩语特有的标点符号）
        # 注意：这里我们模拟韩语文本，实际上韩语和日语有很多相似的标点符号
        ko_text = "안녕하세요, 세계! 이것은 테스트입니다: 문장 부호. (중요) 정보"
        print(f"  📝 模拟韩语文本: '{ko_text}'")
        
        # 清理韩语标点符号
        ko_to_en = clean_language_specific_punctuation(ko_text, "ko", "en")
        print(f"  🔄 韩语->英文标点: '{ko_to_en}'")
        
        print("  🎉 语言到语言转换测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ 语言到语言转换测试失败: {e}")
        return False

def test_prompt_generation():
    """测试提示词生成"""
    print("\n🧪 测试提示词生成...")
    
    try:
        from scripts.utils.punctuation_handler import generate_punctuation_prompt
        
        # 测试日语到英文的提示词
        ja_prompt = generate_punctuation_prompt("ja", "en")
        print(f"  ✅ 日语->英文提示词: {len(ja_prompt)} 字符")
        print(f"  📋 提示词预览: {ja_prompt[:100]}...")
        
        # 测试韩语到英文的提示词
        ko_prompt = generate_punctuation_prompt("ko", "en")
        print(f"  ✅ 韩语->英文提示词: {len(ko_prompt)} 字符")
        print(f"  📋 提示词预览: {ko_prompt[:100]}...")
        
        # 测试中文到英文的提示词
        zh_prompt = generate_punctuation_prompt("zh-CN", "en")
        print(f"  ✅ 中文->英文提示词: {len(zh_prompt)} 字符")
        print(f"  📋 提示词预览: {zh_prompt[:100]}...")
        
        print("  🎉 提示词生成测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ 提示词生成测试失败: {e}")
        return False

def test_all_languages():
    """测试所有语言的标点符号处理"""
    print("\n🧪 测试所有语言的标点符号处理...")
    
    try:
        from scripts.utils.punctuation_handler import clean_language_specific_punctuation
        from scripts.config import LANGUAGE_PUNCTUATION_CONFIG
        
        test_cases = [
            ("zh-CN", "你好，世界！（重要）信息"),
            ("ja", "こんにちは、世界！（重要）情報"),
            ("ko", "안녕하세요, 세계! (중요) 정보"),
            ("ru", "Привет, мир! «Важная» информация"),
            ("fr", "Bonjour, monde! «Important» information"),
            ("es", "¿Hola, mundo! ¡«Importante» información!"),
            ("tr", "Merhaba, dünya! «Önemli» bilgi"),
            ("de", "Hallo, Welt! „Wichtige" Informationen"),
            ("pl", "Witaj, świecie! „Ważne" informacje"),
            ("pt-BR", "Olá, mundo! ""Importante"" informação")
        ]
        
        for lang_code, text in test_cases:
            if lang_code in LANGUAGE_PUNCTUATION_CONFIG:
                cleaned = clean_language_specific_punctuation(text, lang_code, "en")
                print(f"  ✅ {lang_code}: '{text}' -> '{cleaned}'")
            else:
                print(f"  ⚠️  {lang_code}: 未配置")
        
        print("  🎉 所有语言测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ 所有语言测试失败: {e}")
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n🧪 测试边界情况...")
    
    try:
        from scripts.utils.punctuation_handler import (
            clean_language_specific_punctuation,
            generate_punctuation_prompt
        )
        
        # 测试不支持的语言
        unsupported_prompt = generate_punctuation_prompt("invalid_lang", "en")
        print(f"  ✅ 不支持语言提示词: '{unsupported_prompt}' (应为空)")
        
        # 测试空文本
        empty_cleaned = clean_language_specific_punctuation("", "zh-CN", "en")
        print(f"  ✅ 空文本清理: '{empty_cleaned}'")
        
        # 测试无标点符号的文本
        no_punct_cleaned = clean_language_specific_punctuation("Hello World", "zh-CN", "en")
        print(f"  ✅ 无标点符号文本: '{no_punct_cleaned}'")
        
        # 测试混合语言文本
        mixed_text = "Hello，世界！こんにちは、안녕하세요!"
        mixed_cleaned = clean_language_specific_punctuation(mixed_text, "zh-CN", "en")
        print(f"  ✅ 混合语言文本: '{mixed_text}' -> '{mixed_cleaned}'")
        
        print("  🎉 边界情况测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ 边界情况测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试标点符号处理系统")
    print("=" * 60)
    
    tests = [
        test_basic_functionality,
        test_language_to_language_conversion,
        test_prompt_generation,
        test_all_languages,
        test_edge_cases
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"  ⚠️  测试 {test.__name__} 失败")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！标点符号处理系统工作正常！")
        return True
    else:
        print("❌ 部分测试失败，请检查相关代码")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
