#!/usr/bin/env python3
"""
详细的Gemini CLI调试测试
"""

import sys
import os
import logging

# 添加项目路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from scripts.core.gemini_cli_handler import GeminiCLIHandler

def test_detailed_debug():
    """详细的调试测试"""
    print("🔍 详细调试测试")
    print("=" * 50)
    
    # 设置详细的日志级别
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # 初始化CLI客户端
        print("初始化CLI客户端...")
        client = GeminiCLIHandler()
        print("✅ CLI客户端初始化成功")
        
        # 测试批量翻译
        print("\n🧪 测试批量翻译...")
        test_texts = [
            "Hello, this is test message 1.",
            "Hello, this is test message 2.",
            "Hello, this is test message 3."
        ]
        
        print(f"测试文本数量: {len(test_texts)}")
        for i, text in enumerate(test_texts):
            print(f"  文本{i+1}: {text}")
        
        # 执行批量翻译
        translated_texts = client.translate_batch(
            texts=test_texts,
            source_lang="English",
            target_lang="简体中文",
            glossary=None,
            context="This is a debug test"
        )
        
        print(f"\n📊 翻译结果:")
        print(f"  期望数量: {len(test_texts)}")
        print(f"  实际数量: {len(translated_texts)}")
        
        for i, text in enumerate(translated_texts):
            print(f"  结果{i+1}: {text}")
        
        # 获取使用统计
        stats = client.get_usage_stats()
        print(f"\n📈 使用统计:")
        print(f"  今日调用次数: {stats['daily_calls']}")
        print(f"  剩余调用次数: {stats['remaining_calls']}")
        print(f"  成功率: {stats['success_rate']:.2%}")
        
        print("\n✅ 详细调试测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_detailed_debug()
    if success:
        print("\n🎉 详细调试测试成功！")
    else:
        print("\n❌ 详细调试测试失败")
        sys.exit(1)
