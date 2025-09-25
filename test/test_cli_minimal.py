#!/usr/bin/env python3
"""
最小化CLI测试
"""

import subprocess
import tempfile
import os
import json

def test_minimal_cli():
    """最小化CLI测试"""
    print("🧪 最小化CLI测试")
    print("=" * 30)
    
    # 创建简单的测试prompt
    test_prompt = "请将'Hello'翻译为中文"
    
    try:
        # 使用临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_prompt)
            temp_file = f.name
        
        print(f"临时文件: {temp_file}")
        print(f"Prompt: {test_prompt}")
        
        # 调用Gemini CLI
        cmd = [
            "powershell", "-Command", 
            f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; Get-Content '{temp_file}' | gemini --model gemini-2.5-pro --output-format json"
        ]
        
        print("执行CLI命令...")
        print(f"命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # 30秒超时
            encoding='utf-8'
        )
        
        print(f"\n返回码: {result.returncode}")
        print(f"标准输出长度: {len(result.stdout)} 字符")
        print(f"错误输出长度: {len(result.stderr)} 字符")
        
        if result.stdout:
            print("\n标准输出:")
            print("-" * 40)
            print(result.stdout)
            print("-" * 40)
        
        if result.stderr:
            print("\n错误输出:")
            print("-" * 40)
            print(result.stderr)
            print("-" * 40)
        
        # 尝试解析JSON
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                print("\nJSON解析成功:")
                print(f"响应: {data.get('response', 'N/A')}")
                if 'stats' in data:
                    print(f"统计信息: {data['stats']}")
            except json.JSONDecodeError as e:
                print(f"\nJSON解析失败: {e}")
        
        # 清理临时文件
        try:
            os.unlink(temp_file)
        except OSError:
            pass
        
        if result.returncode == 0:
            print("\n✅ CLI调用成功！")
            return True
        else:
            print("\n❌ CLI调用失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n⏰ CLI调用超时")
        return False
    except Exception as e:
        print(f"\n❌ 测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_minimal_cli()
    if success:
        print("\n🎉 最小化测试成功！")
    else:
        print("\n❌ 最小化测试失败")
