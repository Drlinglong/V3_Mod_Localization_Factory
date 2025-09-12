#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试标点符号处理系统集成

验证所有三种API handler和文件构建器是否正确集成了标点符号处理功能
"""

import sys
import os

# 根据当前文件位置计算项目根目录并加入 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_punctuation_handler():
    """测试标点符号处理工具模块"""
    print("🧪 测试标点符号处理工具模块...")
    
    try:
        from scripts.utils.punctuation_handler import (
            generate_punctuation_prompt,
            clean_language_specific_punctuation,
            get_source_language_punctuation
        )
        
        # 测试中文标点符号提示词生成
        zh_prompt = generate_punctuation_prompt("zh-CN", "en")
        print(f"  ✅ 中文提示词生成成功: {len(zh_prompt)} 字符")
        
        # 测试日语标点符号提示词生成
        ja_prompt = generate_punctuation_prompt("ja", "en")
        print(f"  ✅ 日语提示词生成成功: {len(ja_prompt)} 字符")
        
        # 测试标点符号清理
        test_text = "你好，世界！这是一个测试：标点符号。"
        cleaned_text = clean_language_specific_punctuation(test_text, "zh-CN", "en")
        print(f"  ✅ 标点符号清理测试: '{test_text}' -> '{cleaned_text}'")
        
        # 测试获取源语言标点符号
        zh_punct = get_source_language_punctuation("zh-CN")
        print(f"  ✅ 中文标点符号映射: {len(zh_punct)} 个")
        
        print("  🎉 标点符号处理工具模块测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ 标点符号处理工具模块测试失败: {e}")
        return False

def test_api_handlers():
    """测试API handler的标点符号集成"""
    print("\n🧪 测试API Handler标点符号集成...")
    
    try:
        # 测试Gemini Handler
        from scripts.core.gemini_handler import generate_punctuation_prompt
        print("  ✅ Gemini Handler导入成功")
        
        # 测试OpenAI Handler
        from scripts.core.openai_handler import generate_punctuation_prompt
        print("  ✅ OpenAI Handler导入成功")
        
        # 测试Qwen Handler
        from scripts.core.qwen_handler import generate_punctuation_prompt
        print("  ✅ Qwen Handler导入成功")
        
        print("  🎉 所有API Handler标点符号集成测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ API Handler标点符号集成测试失败: {e}")
        return False

def test_file_builder():
    """测试文件构建器的标点符号集成"""
    print("\n🧪 测试文件构建器标点符号集成...")
    
    try:
        from scripts.core.file_builder import clean_language_specific_punctuation
        print("  ✅ 文件构建器标点符号集成成功")
        
        # 测试标点符号清理功能
        test_text = "测试文本：包含中文标点符号，句号。感叹号！问号？"
        cleaned_text = clean_language_specific_punctuation(test_text, "zh-CN", "en")
        print(f"  ✅ 文件构建器标点符号清理: '{test_text}' -> '{cleaned_text}'")
        
        print("  🎉 文件构建器标点符号集成测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ 文件构建器标点符号集成测试失败: {e}")
        return False

def test_config_integration():
    """测试配置文件集成"""
    print("\n🧪 测试配置文件集成...")
    
    try:
        from scripts.config import LANGUAGE_PUNCTUATION_CONFIG, TARGET_LANGUAGE_PUNCTUATION
        
        # 检查配置是否正确加载
        print(f"  ✅ 语言标点符号配置: {len(LANGUAGE_PUNCTUATION_CONFIG)} 种语言")
        print(f"  ✅ 目标语言标点符号配置: {len(TARGET_LANGUAGE_PUNCTUATION)} 种语言")
        
        # 检查具体语言配置
        if "zh-CN" in LANGUAGE_PUNCTUATION_CONFIG:
            zh_config = LANGUAGE_PUNCTUATION_CONFIG["zh-CN"]
            print(f"  ✅ 中文配置: {zh_config['name']}, {len(zh_config['punctuation'])} 个标点符号")
        
        if "ja" in LANGUAGE_PUNCTUATION_CONFIG:
            ja_config = LANGUAGE_PUNCTUATION_CONFIG["ja"]
            print(f"  ✅ 日语配置: {ja_config['name']}, {len(ja_config['punctuation'])} 个标点符号")
        
        print("  🎉 配置文件集成测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ 配置文件集成测试失败: {e}")
        return False

def test_end_to_end():
    """端到端测试"""
    print("\n🧪 端到端测试...")
    
    try:
        from scripts.utils.punctuation_handler import generate_punctuation_prompt, clean_language_specific_punctuation
        
        # 模拟完整的翻译流程
        source_lang = "zh-CN"
        target_lang = "en"
        original_text = "欢迎来到游戏世界！这是一个测试：标点符号转换。"
        
        # 1. 生成提示词
        prompt = generate_punctuation_prompt(source_lang, target_lang)
        print(f"  ✅ 提示词生成: {len(prompt)} 字符")
        
        # 2. 模拟AI翻译（这里只是示例）
        translated_text = "Welcome to the game world! This is a test: punctuation conversion."
        print(f"  ✅ 模拟翻译: '{original_text}' -> '{translated_text}'")
        
        # 3. 后处理清理
        cleaned_text = clean_language_specific_punctuation(translated_text, source_lang, target_lang)
        print(f"  ✅ 后处理清理: '{translated_text}' -> '{cleaned_text}'")
        
        print("  🎉 端到端测试通过！")
        return True
        
    except Exception as e:
        print(f"  ❌ 端到端测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试标点符号处理系统集成")
    print("=" * 60)
    
    tests = [
        test_punctuation_handler,
        test_api_handlers,
        test_file_builder,
        test_config_integration,
        test_end_to_end
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
        print("🎉 所有测试通过！标点符号处理系统集成成功！")
        return True
    else:
        print("❌ 部分测试失败，请检查相关代码")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
