#!/usr/bin/env python3
"""
测试并行CLI处理器
"""

import sys
import os

# 添加项目路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from scripts.core.api_handler import initialize_client

def test_parallel_cli():
    """测试并行CLI处理器"""
    print("🚀 测试并行CLI处理器")
    print("=" * 50)
    
    try:
        # 初始化并行CLI客户端
        print("初始化并行CLI客户端...")
        client, provider_name = initialize_client("gemini_cli_parallel")
        
        if not client:
            print("❌ 并行CLI客户端初始化失败")
            return False
            
        print(f"✅ 并行CLI客户端初始化成功，提供商: {provider_name}")
        print(f"最大并行实例数: {client.max_parallel_instances}")
        
        # 测试单个翻译
        print("\n🧪 测试单个翻译...")
        test_text = "Hello, this is a single test message."
        print(f"测试文本: {test_text}")
        
        translated_text = client.translate_text(
            text=test_text,
            source_lang="English",
            target_lang="Chinese (Simplified)",
            context="This is a test for parallel CLI"
        )
        
        print(f"翻译结果: {translated_text}")
        
        # 测试批量翻译（小批量）
        print("\n🧪 测试小批量翻译...")
        small_batch = [
            "Hello, this is test message 1.",
            "Hello, this is test message 2.",
            "Hello, this is test message 3."
        ]
        
        print(f"测试文本数量: {len(small_batch)}")
        for i, text in enumerate(small_batch):
            print(f"  文本{i+1}: {text}")
        
        translated_batch = client.translate_batch(
            texts=small_batch,
            source_lang="English",
            target_lang="Chinese (Simplified)",
            context="This is a test for parallel CLI batch translation"
        )
        
        print(f"\n📊 批量翻译结果:")
        print(f"  期望数量: {len(small_batch)}")
        print(f"  实际数量: {len(translated_batch)}")
        
        for i, text in enumerate(translated_batch):
            print(f"  结果{i+1}: {text}")
        
        # 测试大批量翻译（触发并行处理）
        print("\n🧪 测试大批量翻译（触发并行处理）...")
        large_batch = [
            f"Hello, this is test message {i+1} for parallel processing test." 
            for i in range(200)  # 200个文本，会触发并行处理
        ]
        
        print(f"测试文本数量: {len(large_batch)}")
        print("开始大批量翻译...")
        
        translated_large_batch = client.translate_batch(
            texts=large_batch,
            source_lang="English",
            target_lang="Chinese (Simplified)",
            context="This is a test for parallel CLI large batch translation"
        )
        
        print(f"\n📊 大批量翻译结果:")
        print(f"  期望数量: {len(large_batch)}")
        print(f"  实际数量: {len(translated_large_batch)}")
        print(f"  成功率: {len(translated_large_batch)/len(large_batch)*100:.1f}%")
        
        # 显示前5个结果
        print("\n前5个翻译结果:")
        for i in range(min(5, len(translated_large_batch))):
            print(f"  结果{i+1}: {translated_large_batch[i]}")
        
        # 获取使用统计
        stats = client.get_usage_stats()
        print(f"\n📈 使用统计:")
        print(f"  今日调用次数: {stats['daily_calls']}")
        print(f"  剩余调用次数: {stats['remaining_calls']}")
        
        # 显示调试文件信息
        history = client.get_call_history()
        print(f"\n📁 调试文件:")
        for call in history:
            if 'debug_file' in call:
                print(f"  {call['debug_file']}")
        
        print("\n✅ 并行CLI测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parallel_cli()
    if success:
        print("\n🎉 并行CLI测试成功！")
    else:
        print("\n❌ 并行CLI测试失败")
        sys.exit(1)
