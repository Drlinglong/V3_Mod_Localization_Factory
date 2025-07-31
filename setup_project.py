import os
from pathlib import Path

def setup_project_structure():
    """
    一键创建项目所需的完整目录结构和空文件。
    """
    print("--- 开始搭建项目框架 ---")

    # 定义所有需要创建的文件夹路径
    directories = [
        "scripts/core",
        "scripts/workflows",
        "scripts/utils",
        "data/lang",
        "data/glossary"
    ]

    # 定义所有需要创建的空文件路径
    files = [
        "scripts/main.py",
        "scripts/config.py",
        "scripts/core/__init__.py",
        "scripts/core/api_handler.py",
        "scripts/core/file_parser.py",
        "scripts/core/file_builder.py",
        "scripts/core/directory_handler.py",
        "scripts/utils/__init__.py",
        "scripts/utils/i18n.py",
        "scripts/utils/report_generator.py",
        "scripts/workflows/__init__.py",
        "scripts/workflows/initial_translate.py",
        "scripts/workflows/update_translate.py",
        "scripts/workflows/scrape_paratranz.py",
        "scripts/workflows/publish_mod.py",
        "scripts/workflows/generate_workshop_desc.py",
        "data/lang/en_US.json",
        "data/lang/zh_CN.json",
        "data/glossary/glossary.json"
    ]

    # 创建文件夹
    for dir_path in directories:
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"  [创建文件夹] {dir_path}")
        except OSError as e:
            print(f"  [错误] 创建文件夹 {dir_path} 失败: {e}")

    # 创建空文件
    for file_path in files:
        try:
            Path(file_path).touch()
            print(f"  [创建文件]   {file_path}")
        except IOError as e:
            print(f"  [错误] 创建文件 {file_path} 失败: {e}")
            
    # 特别为.json文件写入一个空的json对象 {}
    json_files = [f for f in files if f.endswith('.json')]
    for json_file in json_files:
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write('{}\n')
        print(f"  [初始化JSON] {json_file}")


    print("\n--- 项目框架搭建完毕！ ---")

if __name__ == "__main__":
    setup_project_structure()