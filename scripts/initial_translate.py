import os
import re
import time
import json
import shutil
from google import genai

# --- 配置区 ---
SOURCE_DIR = 'source_mod'
DEST_DIR = 'my_translation'
MODEL_NAME = 'gemini-2.5-flash'
CHUNK_SIZE = 150 # 定义每个翻译批次的大小

# --- 主逻辑 ---

def initialize_client():
    """初始化genai客户端。"""
    if not os.getenv('GEMINI_API_KEY'):
        print("错误：环境变量 'GEMINI_API_KEY' 未设置。")
        return None
    try:
        client = genai.Client()
        print(f"Gemini客户端初始化成功，准备使用模型: {MODEL_NAME}")
        return client
    except Exception as e:
        print(f"初始化Gemini客户端时出错: {e}")
        return None

def select_mod_directory():
    """扫描并让用户选择一个mod文件夹。"""
    print(f"\n--- 正在扫描源文件夹 [{SOURCE_DIR}] ---")
    try:
        mod_folders = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
        if not mod_folders:
            print(f"错误：在 '{SOURCE_DIR}' 目录下没有找到任何mod文件夹。")
            return None
        print("请选择要汉化的Mod：")
        for i, folder_name in enumerate(mod_folders):
            print(f"  [{i + 1}] {folder_name}")
        while True:
            try:
                choice = int(input("请输入选项的数字: ")) - 1
                if 0 <= choice < len(mod_folders):
                    selected_mod = mod_folders[choice]
                    print(f"\n你选择了: {selected_mod}")
                    return selected_mod
                else:
                    print("无效的输入，请输入列表中的数字。")
            except ValueError:
                print("无效的输入，请输入数字。")
    except FileNotFoundError:
        print(f"错误：源文件夹 '{SOURCE_DIR}' 不存在。")
        return None

def translate_single_text(client, text, task_description):
    """
    【核心修正】调用API翻译单条文本，使用更严格的Prompt。
    """
    if not text:
        return "" # 如果原文是空的，直接返回空字符串
        
    print(f"正在翻译 {task_description}: \"{text[:30]}...\"")

    # 新的、更严格的Prompt，明确禁止任何额外内容
    prompt = (
        "You are a direct, one-to-one translation engine. Your only function is to translate the text provided. "
        "Translate the following English text into Simplified Chinese.\n"
        "CRITICAL: Your response MUST ONLY contain the translated Chinese text. "
        "DO NOT include explanations, pinyin, English, or any other conversational text or formatting.\n"
        "For example, if the input is 'Flavor Pack', your output must be '风味包' and nothing else.\n\n"
        f"Translate this: \"{text}\""
    )
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        # 增加一步清理，以防万一AI还是返回了带引号的文本
        return response.text.strip().strip('"')
    except Exception as e:
        print(f"API调用失败: {e}")
        return text # 翻译失败则返回原文

def process_metadata(mod_name, client):
    """处理 metadata.json 文件。"""
    print("\n--- 正在处理 metadata.json ---")
    source_meta_file = os.path.join(SOURCE_DIR, mod_name, '.metadata', 'metadata.json')
    dest_meta_dir = os.path.join(DEST_DIR, f"汉化-{mod_name}", '.metadata')
    if not os.path.exists(source_meta_file):
        print("未找到 metadata.json，跳过此步骤。")
        return
    with open(source_meta_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    original_name = data.get('name', '')
    translated_name = translate_single_text(client, original_name, "mod name")
    data['name'] = f"{translated_name} (中文汉化)"
    original_desc = data.get('short_description', '')
    data['short_description'] = translate_single_text(client, original_desc, "mod short description")
    os.makedirs(dest_meta_dir, exist_ok=True)
    dest_meta_file = os.path.join(dest_meta_dir, 'metadata.json')
    with open(dest_meta_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("metadata.json 汉化完成。")

def copy_thumbnail(mod_name):
    """复制 thumbnail.png 文件。"""
    print("\n--- 正在处理 thumbnail.png ---")
    source_thumb_file = os.path.join(SOURCE_DIR, mod_name, 'thumbnail.png')
    dest_dir = os.path.join(DEST_DIR, f"汉化-{mod_name}")
    if not os.path.exists(source_thumb_file):
        print("未找到 thumbnail.png，跳过此步骤。")
        return
    shutil.copy2(source_thumb_file, dest_dir)
    print("thumbnail.png 复制完成。")

def create_fallback_file(source_path, dest_dir, original_filename):
    """【新】翻译失败时的安全网，复制并重命名英文原文件。"""
    print("警告：翻译失败或结果不匹配，将创建英文原文作为备用文件。")
    try:
        with open(source_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        lines[0] = "l_simp_chinese:\n" # 修改文件头
        
        new_filename = original_filename.replace('_l_english.yml', '_l_simp_chinese.yml') if original_filename.endswith('_l_english.yml') else original_filename
        dest_file_path = os.path.join(dest_dir, new_filename)
        
        with open(dest_file_path, 'w', encoding='utf-8-sig') as f:
            f.writelines(lines)
        print(f"已创建备用文件: {new_filename}")
    except Exception as e:
        print(f"创建备用文件时出错: {e}")

def process_yml_files(mod_name, client):
    """【V2.5】处理所有本地化文件，集成“化整为零”翻译策略和“安全网”机制。"""
    print("\n--- 开始处理本地化 .yml 文件 ---")
    source_localization_path = os.path.join(SOURCE_DIR, mod_name, 'localization', 'english')
    dest_localization_path = os.path.join(DEST_DIR, f"汉化-{mod_name}", 'localization', 'simp_chinese')

    if not os.path.isdir(source_localization_path):
        print(f"错误：在 {mod_name} 目录下找不到 'localization/english' 文件夹。")
        return

    for root, _, files in os.walk(source_localization_path):
        for filename in files:
            if not filename.endswith('.yml'):
                continue
            
            relative_path = os.path.relpath(root, source_localization_path)
            source_file_path = os.path.join(root, filename)
            dest_dir_path = os.path.join(dest_localization_path, relative_path)
            os.makedirs(dest_dir_path, exist_ok=True)

            print(f"\n--- 正在处理文件: {os.path.join(relative_path, filename)} ---")

            with open(source_file_path, 'r', encoding='utf-8-sig') as f:
                original_lines = f.readlines()

            texts_to_translate = []
            key_map = {}
            # ... (文件解析逻辑无变化) ...
            for line_num, line in enumerate(original_lines):
                stripped_line = line.strip()
                if not stripped_line or stripped_line.startswith('#') or stripped_line.startswith('l_english'): continue
                quote_start_index = stripped_line.find('"')
                quote_end_index = stripped_line.rfind('"')
                if quote_start_index == -1 or quote_end_index == -1 or quote_start_index >= quote_end_index: continue
                key_part = stripped_line[:quote_start_index]
                value = stripped_line[quote_start_index + 1 : quote_end_index]
                # 【玲珑的修正思路 1】不对key做任何处理，保留其原始样貌（包括缩进）
                key = key_part
                if (value.startswith('$') and value.endswith('$')) or not value: continue
                texts_to_translate.append(value)
                key_map[len(texts_to_translate) - 1] = {'key': key, 'line_num': line_num}
            
            if not texts_to_translate:
                create_fallback_file(source_file_path, dest_dir_path, filename)
                continue
            
            print(f"提取到 {len(texts_to_translate)} 条待翻译文本。")

            all_translated_texts = []
            translation_failed = False
            
            # 【核心升级】化整为零 (Chunking)
            for i in range(0, len(texts_to_translate), CHUNK_SIZE):
                chunk = texts_to_translate[i:i + CHUNK_SIZE]
                print(f"正在处理批次 {i//CHUNK_SIZE + 1} (包含 {len(chunk)} 条文本)...")

                numbered_list = "\n".join([f"{j+1}. \"{text}\"" for j, text in enumerate(chunk)])
                prompt = (
                    "You are a professional translator for the game Victoria 3. "
                    "Translate the following numbered list of English texts into Simplified Chinese.\n"
                    "CRITICAL: Your response MUST be a numbered list with the EXACT same number of items, from 1 to "
                    f"{len(chunk)}. "
                    "Each item in your list MUST be the translation of the corresponding item in the input list.\n"
                    "DO NOT merge, add, or omit lines. DO NOT add any explanations. "
                    "Preserve all special placeholders like $...$ or [...] and internal newlines (\\n).\n\n"
                    "--- INPUT LIST ---\n"
                    f"{numbered_list}\n"
                    "--- END OF INPUT LIST ---"
                )

                try:
                    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                    translated_chunk = re.findall(r'^\s*\d+\.\s*"?(.+?)"?$', response.text, re.DOTALL | re.MULTILINE)

                    if len(translated_chunk) != len(chunk):
                        print(f"错误：批次翻译结果数量不匹配！原文: {len(chunk)}, 译文: {len(translated_chunk)}。")
                        translation_failed = True
                        break # 中断后续批次

                    all_translated_texts.extend(translated_chunk)
                    # 避免过于频繁地调用API
                    if len(texts_to_translate) > CHUNK_SIZE:
                        time.sleep(1) 

                except Exception as e:
                    print(f"处理批次时发生严重错误: {e}")
                    translation_failed = True
                    break

            # 【核心升级】安全网
            if translation_failed:
                create_fallback_file(source_file_path, dest_dir_path, filename)
                continue # 处理下一个文件

            # ... (文件重建与写入逻辑无变化) ...
            new_lines = list(original_lines)
            for i, translated_text in enumerate(all_translated_texts):
                line_info = key_map[i]
                original_line_num = line_info['line_num']
                original_key = line_info['key']
                indent = original_lines[original_line_num][:original_lines[original_line_num].find(original_key)]
                safe_translated_text = translated_text.strip().replace('"', '\\"')
                 # 【玲珑的修正思路 2】重建行时，不再画蛇添足地添加冒号
                new_lines[original_line_num] = f'{indent}{original_key} "{safe_translated_text}"\n'
            new_lines[0] = "l_simp_chinese:\n"
            new_filename = filename.replace('_l_english.yml', '_l_simp_chinese.yml') if filename.endswith('_l_english.yml') else filename
            dest_file_path = os.path.join(dest_dir_path, new_filename)
            with open(dest_file_path, 'w', encoding='utf-8-sig') as f:
                f.writelines(new_lines)
            print(f"文件 '{os.path.join(relative_path, new_filename)}' 汉化完成。")


def cleanup_source_directory(mod_name):
    """清理源mod文件夹，只保留核心汉化文件。"""
    print(f"\n--- 开始精简源Mod文件夹: {mod_name} ---")
    
    # 这是一个危险操作，增加一个确认环节
    confirm = input("警告：此操作将删除源Mod文件夹中除必要文件外的所有内容！\n"
                    "请确认是否继续？ (输入 'y' 或 'yes' 以确认): ")
    if confirm.lower() not in ['y', 'yes']:
        print("操作已取消。")
        return

    mod_path = os.path.join(SOURCE_DIR, mod_name)
    # 定义需要保留的文件和文件夹
    protected_items = {'.metadata', 'localization', 'thumbnail.png'}

    print("正在删除非必要文件和文件夹...")
    try:
        for item in os.listdir(mod_path):
            if item not in protected_items:
                item_path = os.path.join(mod_path, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        print(f"  已删除文件夹: {item}")
                    else:
                        os.remove(item_path)
                        print(f"  已删除文件: {item}")
                except Exception as e:
                    print(f"删除 {item_path} 时出错: {e}")
        print("源文件夹精简完成！")
    except Exception as e:
        print(f"清理过程中发生错误: {e}")

if __name__ == '__main__':
    print("--- 维多利亚3 Mod 汉化自动化脚本 v2.4 ---")
    gemini_client = initialize_client()
    if gemini_client:
        selected_mod_name = select_mod_directory()
        if selected_mod_name:
            # 你可以取消注释来运行所有功能
            process_metadata(selected_mod_name, gemini_client)
            copy_thumbnail(selected_mod_name)
            process_yml_files(selected_mod_name, gemini_client)
            cleanup_source_directory(selected_mod_name)
    print("\n--- 脚本执行完毕 ---")