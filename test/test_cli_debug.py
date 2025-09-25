#!/usr/bin/env python3
"""
测试Gemini CLI修复后的功能
"""

import sys
import os

# 添加项目路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from scripts.core.api_handler import initialize_client, translate_single_text

def test_cli_debug():
    """测试修复后的CLI功能"""
    print("🔧 测试Gemini CLI修复")
    print("=" * 50)
    
    try:
        # 初始化CLI客户端
        print("初始化CLI客户端...")
        client, provider_name = initialize_client("gemini_cli")
        
        if not client:
            print("❌ CLI客户端初始化失败")
            return False
        
        print(f"✅ CLI客户端初始化成功: {provider_name}")
        
        # 测试单个翻译
        print("\n🌐 测试单个翻译...")
        test_text = "Hello, this is a test message."
        
        # 模拟语言和游戏配置
        source_lang = {"name": "English", "code": "en"}
        target_lang = {"name": "简体中文", "code": "zh-CN"}
        game_profile = {"game_name": "Victoria 3"}
        
        translated = translate_single_text(
            client=client,
            provider_name=provider_name,
            text=test_text,
            task_description="test translation",
            mod_name="Test Mod",
            source_lang=source_lang,
            target_lang=target_lang,
            mod_context="This is a test context",
            game_profile=game_profile
        )
        
        print(f"原文: {test_text}")
        print(f"译文: {translated}")
        
        # 获取使用统计
        stats = client.get_usage_stats()
        print(f"\n📊 使用统计:")
        print(f"   今日调用次数: {stats['daily_calls']}")
        print(f"   剩余调用次数: {stats['remaining_calls']}")
        print(f"   成功率: {stats['success_rate']:.2%}")
        
        print("\n✅ 测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cli_debug()
    if success:
        print("\n🎉 CLI修复验证成功！")
    else:
        print("\n❌ CLI修复验证失败")
        sys.exit(1)
