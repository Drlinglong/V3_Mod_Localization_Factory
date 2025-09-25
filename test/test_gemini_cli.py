#!/usr/bin/env python3
"""
测试Gemini CLI集成
验证CLI处理器是否正常工作
"""

import sys
import os

# 添加项目路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from scripts.core.api_handler import initialize_client, translate_single_text
from scripts.config import API_PROVIDERS

def test_gemini_cli():
    """测试Gemini CLI集成"""
    print("=" * 60)
    print("🧪 测试Gemini CLI集成")
    print("=" * 60)
    
    # 检查配置
    cli_config = API_PROVIDERS.get("gemini_cli", {})
    print(f"CLI路径: {cli_config.get('cli_path', 'gemini')}")
    print(f"Chunk大小: {cli_config.get('chunk_size', 150)}")
    print(f"最大每日调用: {cli_config.get('max_daily_calls', 1000)}")
    print(f"启用思考功能: {cli_config.get('enable_thinking', True)}")
    print()
    
    try:
        # 初始化CLI客户端
        print("🔧 初始化CLI客户端...")
        client, provider_name = initialize_client("gemini_cli")
        
        if not client:
            print("❌ CLI客户端初始化失败")
            return False
        
        print(f"✅ CLI客户端初始化成功: {provider_name}")
        
        # 获取使用统计
        stats = client.get_usage_stats()
        print(f"📊 使用统计:")
        print(f"   今日调用次数: {stats['daily_calls']}")
        print(f"   剩余调用次数: {stats['remaining_calls']}")
        print(f"   成功率: {stats['success_rate']:.2%}")
        print()
        
        # 测试单个翻译
        print("🌐 测试单个翻译...")
        test_text = "Hello, this is a test message for Gemini CLI."
        
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
        print()
        
        # 更新统计信息
        stats = client.get_usage_stats()
        print(f"📊 翻译后统计:")
        print(f"   今日调用次数: {stats['daily_calls']}")
        print(f"   剩余调用次数: {stats['remaining_calls']}")
        print()
        
        print("✅ Gemini CLI集成测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_availability():
    """测试CLI是否可用"""
    print("🔍 检查Gemini CLI可用性...")
    
    import subprocess
    try:
        # 使用PowerShell执行策略启动Gemini CLI
        cmd = [
            "powershell", "-Command", 
            "Set-ExecutionPolicy RemoteSigned -Scope Process -Force; gemini --version"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ Gemini CLI可用: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Gemini CLI测试失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Gemini CLI未找到，请先安装:")
        print("   npm install -g @google/gemini-cli")
        print("   然后运行: gemini 进行初始配置")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Gemini CLI响应超时")
        return False

if __name__ == "__main__":
    print("🚀 开始Gemini CLI测试")
    print()
    
    # 首先检查CLI是否可用
    if not test_cli_availability():
        print("\n💡 请先安装和配置Gemini CLI:")
        print("   1. 安装Node.js (版本20.0.0+)")
        print("   2. 运行: npm install -g @google/gemini-cli")
        print("   3. 运行: gemini 进行初始配置")
        print("   4. 使用个人Google账户进行OAuth认证")
        sys.exit(1)
    
    print()
    
    # 测试集成
    success = test_gemini_cli()
    
    if success:
        print("\n🎉 所有测试通过！Gemini CLI集成成功！")
        print("\n💡 使用建议:")
        print("   - 在main.py中选择'gemini_cli'作为API供应商")
        print("   - 享受每天1000次免费Gemini 2.5 Pro调用")
        print("   - 利用大chunk策略发挥长上下文优势")
    else:
        print("\n❌ 测试失败，请检查配置")
        sys.exit(1)
