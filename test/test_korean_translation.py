#!/usr/bin/env python3
"""
测试韩语翻译过程
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from scripts.core.api_handler import initialize_client
from scripts.config import LANGUAGES, GAME_PROFILES

def test_korean_translation():
    print("=== 测试韩语翻译过程 ===")
    
    # 获取语言配置
    english_lang = LANGUAGES["1"]  # English
    korean_lang = LANGUAGES["7"]   # Korean
    
    print(f"源语言: {english_lang['name']} (code: {english_lang['code']})")
    print(f"目标语言: {korean_lang['name']} (code: {korean_lang['code']})")
    
    # 获取Victoria 3游戏配置
    vic3_profile = GAME_PROFILES["1"]
    
    # 测试单个翻译
    print(f"\n=== 测试单个翻译 ===")
    test_text = "Hello World"
    
    try:
        # 初始化CLI客户端
        client, provider_name = initialize_client("gemini_cli")
        if not client:
            print("❌ 无法初始化CLI客户端")
            return
            
        print(f"✅ CLI客户端初始化成功: {provider_name}")
        
        # 调用单个翻译
        result = client.translate_single_text(
            text=test_text,
            task_description="test translation",
            mod_name="Test Mod",
            source_lang=english_lang,
            target_lang=korean_lang,
            mod_context="Test Context",
            game_profile=vic3_profile
        )
        
        print(f"翻译结果: '{result}'")
        
        # 检查结果是否为韩语
        if "안녕" in result or "세계" in result or "헬로" in result:
            print("✅ 翻译结果包含韩语字符")
        elif "你好" in result or "世界" in result or "你好世界" in result:
            print("❌ 翻译结果是中文，不是韩语!")
        else:
            print("⚠️ 翻译结果既不是韩语也不是中文")
            
    except Exception as e:
        print(f"❌ 翻译失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_korean_translation()
