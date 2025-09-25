#!/usr/bin/env python3
"""
简单测试并行CLI处理器
"""

import sys
import os

# 添加项目路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from scripts.core.api_handler import initialize_client

def test_parallel_cli_simple():
    """简单测试并行CLI处理器"""
    print("🚀 简单测试并行CLI处理器")
    print("=" * 50)
    
    try:
        # 初始化并行CLI客户端
        print("初始化并行CLI客户端...")
        client, provider_name = initialize_client("gemini_cli")
        
        if not client:
            print("❌ 并行CLI客户端初始化失败")
            return False
            
        print(f"✅ CLI客户端初始化成功，提供商: {provider_name}")
        print(f"支持并行处理: 是")
        
        # 测试单个翻译
        print("\n🧪 测试单个翻译...")
        test_text = "Hello, this is a test message."
        print(f"测试文本: {test_text}")
        
        translated_text = client.translate_text(
            text=test_text,
            source_lang="English",
            target_lang="Chinese (Simplified)",
            context="Test"
        )
        
        print(f"翻译结果: {translated_text}")
        
        # 测试小批量翻译
        print("\n🧪 测试小批量翻译...")
        small_batch = [
            "Hello, this is test message 1.",
            "Hello, this is test message 2.",
            "Hello, this is test message 3."
        ]
        
        print(f"测试文本数量: {len(small_batch)}")
        
        translated_batch = client.translate_batch(
            texts=small_batch,
            source_lang="English",
            target_lang="Chinese (Simplified)",
            context="Test"
        )
        
        print(f"\n📊 批量翻译结果:")
        print(f"  期望数量: {len(small_batch)}")
        print(f"  实际数量: {len(translated_batch)}")
        
        for i, text in enumerate(translated_batch):
            print(f"  结果{i+1}: {text}")
        
        # 获取使用统计
        stats = client.get_usage_stats()
        print(f"\n📈 使用统计:")
        print(f"  本次会话调用次数: {stats['daily_calls']}")
        
        print("\n✅ 简单并行CLI测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parallel_cli_simple()
    if success:
        print("\n🎉 简单并行CLI测试成功！")
    else:
        print("\n❌ 简单并行CLI测试失败")
        sys.exit(1)
