# scripts/core/asset_handler.py
# ------------------------------------------------------------------
import os
import re
import json
import shutil
from pathlib import Path

from utils import i18n, read_text_bom, write_text_bom
from config import SOURCE_DIR, DEST_DIR
from .api_handler import translate_single_text


# ──────────────────────────────────────────────────────────────────
# VICTORIA 3
# ──────────────────────────────────────────────────────────────────
def _process_victoria3_metadata(mod_name, client, source_lang, target_lang,
                                output_folder_name, mod_context, game_profile):
    """【V3专用】处理 Victoria 3 的 .metadata/metadata.json 文件。"""
    source_meta_file = os.path.join(SOURCE_DIR, mod_name, game_profile['metadata_file'])
    dest_meta_dir = os.path.join(DEST_DIR, output_folder_name, '.metadata')

    if not os.path.exists(source_meta_file):
        print(i18n.t("metadata_not_found"))
        return

    with open(source_meta_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_name = data.get('name', '')
    translated_name = translate_single_text(
        client, original_name, "mod name", mod_name,
        source_lang, target_lang, mod_context, game_profile
    )

    is_batch_mode = "Multilanguage" in output_folder_name
    if is_batch_mode:
        suffix = " (Multilingual Patch)"
    elif target_lang['key'] == 'l_simp_chinese':
        suffix = " (中文汉化)"
    else:
        suffix = f" ({target_lang['name']} Translation)"
    data['name'] = f"{translated_name}{suffix}"

    original_desc = data.get('short_description', '')
    data['short_description'] = translate_single_text(
        client, original_desc, "mod short description", mod_name,
        source_lang, target_lang, mod_context, game_profile
    )

    os.makedirs(dest_meta_dir, exist_ok=True)
    dest_meta_file = os.path.join(dest_meta_dir, 'metadata.json')
    with open(dest_meta_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(i18n.t("metadata_success"))


# ──────────────────────────────────────────────────────────────────
# STELLARIS
# ──────────────────────────────────────────────────────────────────
def _process_stellaris_metadata(mod_name, client, source_lang, target_lang,
                                output_folder_name, mod_context, game_profile):
    """【群星专用】生成两份 .mod 文件。"""
    source_mod_file = os.path.join(SOURCE_DIR, mod_name, game_profile['metadata_file'])
    if not os.path.exists(source_mod_file):
        print(f"警告：未找到源 {game_profile['metadata_file']} 文件，跳过元数据处理。")
        return

    with open(source_mod_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # ── translate name ────────────────────────────────────────────
    original_name = ""
    for line in lines:
        if line.strip().startswith('name='):
            match = re.search(r'"(.*)"', line)
            if match:
                original_name = match.group(1)
            break

    translated_name = translate_single_text(
        client, original_name, "mod name", mod_name,
        source_lang, target_lang, mod_context, game_profile
    )

    is_batch_mode = "Multilanguage" in output_folder_name
    if is_batch_mode:
        suffix = " (Multilingual Patch)"
    elif target_lang['key'] == 'l_simp_chinese':
        suffix = " (汉化)"
    else:
        suffix = f" ({target_lang['name']} Translation)"
    final_name = f"{translated_name}{suffix}"

    # ── rewrite descriptor.mod ────────────────────────────────────
    new_content_lines, in_tags_block, tags_block_written = [], False, False
    for line in lines:
        stripped_line = line.strip()

        if in_tags_block:
            if '}' in stripped_line:
                in_tags_block = False
            continue

        if stripped_line.startswith('name='):
            new_content_lines.append(f'name="{final_name}"\n')

        elif stripped_line.startswith('tags={'):
            new_content_lines.append('tags={\n\t"Translation"\n}\n')
            if '}' not in stripped_line:
                in_tags_block = True
            tags_block_written = True

        elif stripped_line.startswith('remote_file_id='):
            continue  # usuń ID Workshopu

        else:
            new_content_lines.append(line)

    if not tags_block_written:
        insertion_point = next(
            (i + 1 for i, l in enumerate(new_content_lines) if l.strip().startswith('version=')), 0
        )
        new_content_lines.insert(insertion_point, 'tags={\n\t"Translation"\n}\n')

    dest_mod_dir = os.path.join(DEST_DIR, output_folder_name)
    os.makedirs(dest_mod_dir, exist_ok=True)

    with open(os.path.join(dest_mod_dir, 'descriptor.mod'), 'w', encoding='utf-8') as f:
        f.writelines(new_content_lines)

    launcher_mod_content = new_content_lines + [f'\npath="mod/{output_folder_name}"']
    with open(os.path.join(DEST_DIR, f"{output_folder_name}.mod"), 'w', encoding='utf-8') as f:
        f.writelines(launcher_mod_content)

    print(i18n.t("metadata_success"))


# ──────────────────────────────────────────────────────────────────
# EU4  (nowo dodane)
# ──────────────────────────────────────────────────────────────────
def _process_eu4_metadata(mod_name, client, source_lang, target_lang,
                           output_folder_name, mod_context, game_profile):
    """【EU4专用】处理 descriptor.mod (UTF-8 + BOM)."""
    source_mod_file = os.path.join(SOURCE_DIR, mod_name, game_profile['metadata_file'])
    if not os.path.exists(source_mod_file):
        print("Warning: descriptor.mod not found, skipping metadata.")
        return

    # Wczytaj z zachowaniem BOM
    lines = read_text_bom(Path(source_mod_file)).splitlines()

    # ── tłumaczenie nazwy ──────────────────────────────────────────
    original_name = ""
    for ln in lines:
        if ln.strip().startswith('name='):
            m = re.search(r'"(.*)"', ln)
            if m:
                original_name = m.group(1)
            break

    translated_name = translate_single_text(
        client, original_name, "mod name", mod_name,
        source_lang, target_lang, mod_context, game_profile
    )

    is_batch_mode = "Multilanguage" in output_folder_name
    if is_batch_mode:
        suffix = " (Multilingual Patch)"
    elif target_lang['key'] == 'l_simp_chinese':
        suffix = " (汉化)"
    else:
        suffix = f" ({target_lang['name']} Translation)"
    final_name = f"{translated_name}{suffix}"

    # ── składanie nowej zawartości ─────────────────────────────────
    new_lines = []
    tags_written = False
    for ln in lines:
        stripped = ln.strip()

        if stripped.startswith('name='):
            new_lines.append(f'name="{final_name}"')

        elif stripped.startswith('tags={'):
            tags_written = True
            new_lines.append('tags={')
            new_lines.append('\t"Translation"')
            new_lines.append('}')
            # pomiń oryginalne linie w bloku tags
            continue

        elif stripped.startswith('remote_file_id='):
            continue  # usuń ID Workshopu

        else:
            new_lines.append(ln)

    if not tags_written:
        idx = next(
            (i + 1 for i, l in enumerate(new_lines) if l.strip().startswith('version=')),
            len(new_lines)
        )
        new_lines.insert(idx, 'tags={\n\t"Translation"\n}')

    dest_mod_dir = os.path.join(DEST_DIR, output_folder_name)
    os.makedirs(dest_mod_dir, exist_ok=True)

    # Zapis z BOM-em
    write_text_bom(Path(os.path.join(dest_mod_dir, 'descriptor.mod')), "\n".join(new_lines))

    launcher_lines = new_lines + [f'\npath="mod/{output_folder_name}"']
    write_text_bom(Path(os.path.join(DEST_DIR, f"{output_folder_name}.mod")), "\n".join(launcher_lines))

    print(i18n.t("metadata_success"))


# ──────────────────────────────────────────────────────────────────
# GŁÓWNY DISPATCHER
# ──────────────────────────────────────────────────────────────────
def process_metadata(mod_name, client, source_lang, target_lang,
                     output_folder_name, mod_context, game_profile):
    """【总调度】元数据处理器，根据游戏档案调用对应的处理函数。"""
    print(i18n.t("processing_metadata"))

    if game_profile['id'] == 'stellaris':
        _process_stellaris_metadata(mod_name, client, source_lang, target_lang,
                                    output_folder_name, mod_context, game_profile)

    elif game_profile['id'] == 'victoria3':
        _process_victoria3_metadata(mod_name, client, source_lang, target_lang,
                                    output_folder_name, mod_context, game_profile)

    elif game_profile['id'] == 'eu4':                     # <── NOWE
        _process_eu4_metadata(mod_name, client, source_lang, target_lang,
                              output_folder_name, mod_context, game_profile)

    else:
        print(f"警告：暂不支持游戏 '{game_profile['name']}' 的元数据处理。")


# ──────────────────────────────────────────────────────────────────
# KOPIOWANIE DODATKOWYCH ASSETÓW (bez zmian)
# ──────────────────────────────────────────────────────────────────
def copy_assets(mod_name, output_folder_name, game_profile):
    """根据游戏档案中的保护名单，复制所有必要的资产文件。"""
    print(i18n.t("processing_assets"))
    source_dir = os.path.join(SOURCE_DIR, mod_name)
    dest_dir = os.path.join(DEST_DIR, output_folder_name)

    assets_to_copy = game_profile.get('protected_items', set())
    metadata_filename = os.path.basename(game_profile.get('metadata_file', ''))

    for item in assets_to_copy:
        if item == metadata_filename or (
            game_profile['id'] == 'victoria3' and item == '.metadata'
        ):
            continue

        source_path = os.path.join(source_dir, item)
        if os.path.isfile(source_path):
            try:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(source_path, dest_dir)
                print(i18n.t("asset_copied", asset_name=item))
            except FileNotFoundError:
                print(i18n.t("asset_not_found", asset_name=item))
            except Exception as e:
                print(f"Error copying asset {item}: {e}")
