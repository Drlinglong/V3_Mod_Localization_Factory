# -*- coding: utf-8 -*-
#
# 功能: 将从 Paratranz.cn 词典页面直接复制的文本，解析成一个包含元数据和词条列表的结构化 JSON 文件。
#
import json
import re
from datetime import datetime
import pytz

def is_variant_line(line):
    """
    判断某一行是否是变体行。
    规则：基本上只包含英文字母、数字、逗号、空格和一些标点符号，
    且不包含中文字符。
    """
    if re.search(r'[\u4e00-\u9fff]', line):
        return False
    if re.search(r'[a-zA-Z]', line):
        return True
    return False

def parse_glossary_to_json(input_text):
    """
    将从网页复制的词汇表文本解析为词条列表。
    """
    pos_map = {
        "名词": "Noun",
        "形容词": "Adjective",
        "动词": "Verb"
    }
    entries_raw = re.split(r'\s+(?:创建于|修改于) \d{4}/\d{2}/\d{2}[\s\S]*?评论\s+\d+\s*', input_text)
    
    all_entries = []

    for block in entries_raw:
        if not block.strip():
            continue

        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if not lines:
            continue

        entry_data = {}
        remarks_list = []
        
        original_word = lines.pop(0)
        
        entry_data['translations'] = {"en": original_word}
        
        clean_id = re.sub(r'[\s\W]+', '_', original_word.lower()).strip('_')
        entry_data['id'] = f"stellaris_{clean_id}"
        
        entry_data['metadata'] = {}
        found_pos = False
        found_zh = False

        for line in lines:
            if not found_pos and line in pos_map:
                entry_data['metadata']['part_of_speech'] = pos_map[line]
                found_pos = True
                continue
            if found_pos and not found_zh:
                entry_data['translations']['zh-CN'] = line
                found_zh = True
                continue
            if not found_pos and is_variant_line(line):
                variants = [v.strip() for v in line.split(',') if v.strip()]
                entry_data['variants'] = {"en": variants}
                continue
            remarks_list.append(line)

        if remarks_list:
            entry_data['metadata']['remarks'] = "\n".join(remarks_list)
        
        all_entries.append(entry_data)

    return all_entries


def main():
    """
    主函数：读取输入文件，处理数据，添加元数据，并写入最终的JSON对象。
    """
    input_filename = 'input.txt'
    output_filename = 'glossary.json'

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
        # 1. 解析原始文本，获取词条列表
        entries_list = parse_glossary_to_json(raw_text)

        # 2. 创建元数据 (Metadata)
        # 获取当前澳大利亚东部时间
        aest = pytz.timezone('Australia/Sydney')
        last_updated_time = datetime.now(aest).isoformat()

        metadata = {
            "description": "群星 (Stellaris) 游戏及Mod社区汉化词典",
            "sources": [
                "鸽组汉化词典",
                "Shrouded Regions汉化词典",
                "L网群星mod汉化集词典"
            ],
            "last_updated": last_updated_time
        }
        
        # 3. 组合成最终的JSON顶层对象
        final_output_data = {
            "metadata": metadata,
            "entries": entries_list
        }

        # 4. 写入文件
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_output_data, f, ensure_ascii=False, indent=2)

        print(f"处理完成！包含元数据的词典已成功写入 '{output_filename}' 文件。")
        print(f"总共处理了 {len(entries_list)} 个词条。")

    except FileNotFoundError:
        print(f"错误：找不到输入文件 '{input_filename}'。")
        print("请确保在脚本相同目录下创建了该文件，并将原始文本粘贴进去。")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")


# 运行主函数
if __name__ == "__main__":
    main()