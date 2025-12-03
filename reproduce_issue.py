import re
import sys
import os

# Mock the patch_file_content function from file_builder.py
def patch_file_content(
    original_lines: list[str],
    texts_to_translate: list[str],
    translated_texts: list[str],
    key_map: dict[int, dict],
    source_lang_key: str,
    target_lang_key: str,
) -> list[str]:
    
    new_lines = list(original_lines)

    for i, original_text in enumerate(texts_to_translate):
        if i >= len(translated_texts):
            break
            
        translated_text = translated_texts[i]
        line_info = key_map[i]
        line_num = line_info["line_num"]
        key_part = line_info["key_part"]
        
        original_line_content = original_lines[line_num]
        
        key_pos = original_line_content.find(key_part)
        if key_pos == -1: continue
            
        search_start_pos = key_pos + len(key_part)
        first_quote_pos = original_line_content.find('"', search_start_pos)
        if first_quote_pos == -1: continue
             
        comment_pos = original_line_content.find('#', first_quote_pos)
        if comment_pos != -1:
            search_end_pos = comment_pos
        else:
            search_end_pos = len(original_line_content)
            
        last_quote_pos = original_line_content.rfind('"', first_quote_pos + 1, search_end_pos)
        if last_quote_pos == -1: continue
            
        safe_translated_text = translated_text.replace('"', r'\"')
        prefix = original_line_content[:first_quote_pos + 1]
        suffix = original_line_content[last_quote_pos:]
        new_lines[line_num] = f"{prefix}{safe_translated_text}{suffix}"

    # --- Replace the language header ---
    header_pattern = re.compile(r"^\s*l_[\w-]+:\s*")
    
    first_header_index = -1
    indices_to_remove = []
    
    for i, line in enumerate(new_lines):
        if header_pattern.match(line):
            if first_header_index == -1:
                first_header_index = i
            else:
                indices_to_remove.append(i)
    
    for i in reversed(indices_to_remove):
        new_lines.pop(i)
        
    if first_header_index != -1:
        new_lines[first_header_index] = f"{target_lang_key}:\n"
    else:
        new_lines.insert(0, f"{target_lang_key}:\n")
        
    return new_lines

# Mock Data
original_lines = [
    "l_simp_chinese:\n",
    " # This is a comment line\n",
    " key_1:0 \"Chinese Value 1\" # Inline comment\n",
    "\n",
    " l_zh-CN: # Garbage header\n",
    " key_2:0 \"Chinese Value 2\"\n"
]

texts_to_translate = ["Chinese Value 1", "Chinese Value 2"]
translated_texts = ["English Value 1", "English Value 2"]
key_map = {
    0: {"line_num": 2, "key_part": "key_1"},
    1: {"line_num": 5, "key_part": "key_2"}
}
source_lang_key = "l_simp_chinese"
target_lang_key = "l_english"

# Run Patching
patched_lines = patch_file_content(
    original_lines,
    texts_to_translate,
    translated_texts,
    key_map,
    source_lang_key,
    target_lang_key
)

print("--- Patched Content ---")
print("".join(patched_lines))
print("-----------------------")
