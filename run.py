#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3_Mod_Localization_Factory 启动脚本
确保程序在正确的目录下运行，避免路径问题
"""

import os
import sys
import subprocess

def main():
    # 获取脚本所在目录（项目根目录）
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    print(f"项目根目录: {project_root}")
    
    # 检查必要的目录是否存在
    source_dir = os.path.join(project_root, 'source_mod')
    if not os.path.exists(source_dir):
        print(f"错误: source_mod 目录不存在: {source_dir}")
        print("请确保项目结构完整，或手动创建 source_mod 目录")
        return 1
    
    # 检查是否有mod文件
    try:
        mod_folders = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
        if not mod_folders:
            print(f"警告: source_mod 目录为空，请添加要翻译的mod文件夹")
            print(f"支持的mod类型: Victoria 3, Stellaris, EU4, HOI4, CK3")
    except Exception as e:
        print(f"检查 source_mod 目录时出错: {e}")
        return 1
    
    # 运行主程序
    main_script = os.path.join(project_root, 'scripts', 'main.py')
    if not os.path.exists(main_script):
        print(f"错误: 主程序文件不存在: {main_script}")
        return 1
    
    print("启动本地化工厂...")
    print("=" * 50)
    
    try:
        # 使用 subprocess 运行主程序，保持当前环境
        result = subprocess.run([sys.executable, main_script], cwd=project_root)
        return result.returncode
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        return 0
    except Exception as e:
        print(f"运行程序时出错: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
