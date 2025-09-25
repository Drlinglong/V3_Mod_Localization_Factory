#!/usr/bin/env python3
"""
简单测试Gemini CLI调用
"""

import subprocess
import tempfile
import os

def test_simple_cli_call():
    """测试简单的CLI调用"""
    print("🧪 测试简单CLI调用")
    print("=" * 40)
    
    # 创建测试prompt
    test_prompt = "请将以下英文翻译为中文：Hello, this is a test message."
    
    try:
        # 使用临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_prompt)
            temp_file = f.name
        
        print(f"临时文件: {temp_file}")
        print(f"Prompt长度: {len(test_prompt)} 字符")
        
        # 调用Gemini CLI
        cmd = [
            "powershell", "-Command", 
            f"Set-ExecutionPolicy RemoteSigned -Scope Process -Force; Get-Content '{temp_file}' | gemini --model gemini-2.5-pro --output-format json"
        ]
        
        print("执行命令...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8'
        )
        
        print(f"返回码: {result.returncode}")
        print(f"标准输出: {result.stdout[:200]}...")
        if result.stderr:
            print(f"错误输出: {result.stderr}")
        
        # 清理临时文件
        try:
            os.unlink(temp_file)
        except OSError:
            pass
        
        if result.returncode == 0:
            print("✅ CLI调用成功！")
            return True
        else:
            print("❌ CLI调用失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_cli_call()
    if success:
        print("\n🎉 简单测试成功！")
    else:
        print("\n❌ 简单测试失败")
