# -*- coding: utf-8 -*-
#
# 功能: 验证 glossary.json 文件，检查重复、冲突和其他潜在问题。
#
import json
from collections import defaultdict

def validate_glossary(filepath='glossary.json'):
    """
    读取并验证词典文件。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到词典文件 '{filepath}'。请先运行 parser.py 生成它。")
        return
    except json.JSONDecodeError:
        print(f"错误: '{filepath}' 文件格式不正确，无法解析。")
        return

    entries = data.get('entries', [])
    if not entries:
        print("词典中没有任何条目，无需验证。")
        return

    print(f"--- 开始验证 '{filepath}' ({len(entries)} 个条目) ---\n")

    # --- 数据结构准备 ---
    # 用于检查ID冲突
    seen_ids = defaultdict(list)
    # 用于检查翻译冲突 (en -> [zh1, zh2])
    en_to_zh_map = defaultdict(list)
    # 用于检查潜在的同义词问题 (zh -> [en1, en2])
    zh_to_en_map = defaultdict(list)

    # --- 第一轮: 数据收集 ---
    for entry in entries:
        entry_id = entry.get('id')
        en_term = entry.get('translations', {}).get('en')
        zh_term = entry.get('translations', {}).get('zh-CN')

        if not all([entry_id, en_term, zh_term]):
            print(f"警告: 发现残缺条目，缺少id或翻译: {entry}")
            continue

        seen_ids[entry_id].append(en_term)
        en_to_zh_map[en_term].append(zh_term)
        zh_to_en_map[zh_term].append(en_term)

    # --- 第二轮: 分析并报告问题 ---
    found_issues = False

    # 1. 检查ID冲突
    print("--- 1. 检查ID冲突 ---")
    id_conflicts = {id: terms for id, terms in seen_ids.items() if len(terms) > 1}
    if id_conflicts:
        found_issues = True
        print("错误: 发现以下ID被多个词条共用，这会导致数据覆盖！")
        for id, terms in id_conflicts.items():
            print(f"  - ID: '{id}'")
            print(f"    - 对应词条: {terms}")
    else:
        print("恭喜！未发现ID冲突。")
    print("-" * 20)

    # 2. 检查翻译冲突 (1个英文 -> 多个中文)
    print("--- 2. 检查翻译冲突 ---")
    translation_conflicts = {en: list(set(zh_list)) for en, zh_list in en_to_zh_map.items() if len(set(zh_list)) > 1}
    if translation_conflicts:
        found_issues = True
        print("错误: 发现同一个英文原文有多个不同的中文翻译！请统一。")
        for en, zh_list in translation_conflicts.items():
            print(f"  - 英文: '{en}'")
            print(f"    - 存在翻译: {zh_list}")
    else:
        print("恭喜！未发现直接的翻译冲突。")
    print("-" * 20)

    # 3. 检查潜在的同义词问题 (1个中文 -> 多个英文)
    print("--- 3. 检查潜在的同义词问题 ---")
    potential_issues = {zh: list(set(en_list)) for zh, en_list in zh_to_en_map.items() if len(set(en_list)) > 1}
    if potential_issues:
        found_issues = True
        print("注意: 发现同一个中文词被用于翻译多个不同的英文原文。这不一定是错，但建议审查。")
        for zh, en_list in potential_issues.items():
            print(f"  - 中文: '{zh}'")
            print(f"    - 用于翻译: {en_list}")
    else:
        print("未发现明显的同义词问题。")
    print("-" * 20)
    
    # --- 总结 ---
    print("\n--- 验证完毕 ---")
    if not found_issues:
        print("太棒了！你的词典文件看起来非常干净，没有发现任何冲突。")
    else:
        print("验证发现了一些潜在问题，请根据上面的报告进行修正。")


# 运行主函数
if __name__ == "__main__":
    validate_glossary()