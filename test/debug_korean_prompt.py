#!/usr/bin/env python3
"""
直接测试韩语翻译的prompt构造
"""

import os
import sys
sys.path.append('scripts')

from scripts.core.gemini_cli_handler import GeminiCLIHandler
from scripts.config import LANGUAGES

def test_korean_prompt():
    """测试韩语翻译的prompt构造"""
    
    # 测试文本
    test_text = "Naval Convoy Contribution"
    
    # 韩语配置
    korean_lang = LANGUAGES["7"]  # 韩语
    english_lang = LANGUAGES["1"]  # 英语
    
    print(f"🔍 韩语Prompt构造测试")
    print(f"测试文本: {test_text}")
    print(f"源语言: {english_lang['name']} ({english_lang['code']})")
    print(f"目标语言: {korean_lang['name']} ({korean_lang['code']})")
    print("=" * 60)
    
    # 创建CLI handler
    cli_handler = GeminiCLIHandler()
    
    # 模拟游戏配置
    game_profile = {
        "1": {"name": "Victoria 3"},
        "single_prompt_template": (
            "You are a direct, one-to-one translation engine. "
            "The text you are translating is for a Victoria 3 game mod named '{mod_name}'. "
            "Translate the following text from {source_lang_name} to {target_lang_name}.\n\n"
            "Text to translate: {text}\n\n"
            "Translation:"
        )
    }
    
    try:
        # 构造prompt
        prompt = cli_handler._build_single_translation_prompt(
            test_text, english_lang, korean_lang, game_profile, "test_mod"
        )
        
        print("✅ Prompt构造成功")
        print(f"Prompt长度: {len(prompt)} 字符")
        print("\n📝 构造的Prompt内容:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)
        
        # 检查prompt中是否包含正确的语言信息
        print(f"\n🔍 Prompt分析:")
        print(f"包含源语言名称 '{english_lang['name']}': {'是' if english_lang['name'] in prompt else '否'}")
        print(f"包含目标语言名称 '{korean_lang['name']}': {'是' if korean_lang['name'] in prompt else '否'}")
        print(f"包含源语言代码 '{english_lang['code']}': {'是' if english_lang['code'] in prompt else '否'}")
        print(f"包含目标语言代码 '{korean_lang['code']}': {'是' if korean_lang['code'] in prompt else '否'}")
        
        # 检查是否有语言映射问题
        if "简体中文" in prompt and korean_lang['name'] == "한국어":
            print("⚠️  警告: Prompt中包含'简体中文'但目标语言是韩语！")
        if "Chinese" in prompt and korean_lang['name'] == "한국어":
            print("⚠️  警告: Prompt中包含'Chinese'但目标语言是韩语！")
            
    except Exception as e:
        print(f"❌ Prompt构造失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_korean_prompt()
