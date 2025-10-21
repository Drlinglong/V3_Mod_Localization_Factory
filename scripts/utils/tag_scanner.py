# scripts/utils/tag_scanner.py
import os
import re
import json
import logging
from typing import Set, List, Dict

from scripts.utils import i18n

def _scan_directory_for_tags(path: str) -> Set[str]:
    """
    Helper function to scan all .yml/.txt files in a directory recursively for tags,
    following a precise 3-step logic to avoid commented-out keys.

    Args:
        path (str): The directory path to scan.

    Returns:
        Set[str]: A set of unique tags found.
    """
    tags: Set[str] = set()
    # Upgraded regex: requires a preceding space, and the character after # must be a letter/underscore.
    tag_pattern = re.compile(r"(?<=\s)#([a-zA-Z_][a-zA-Z0-9_]*)")
    value_pattern = re.compile(r'"(.*)"')

    if not os.path.isdir(path):
        logging.error(f"FATAL: Provided path for tag scanning is not a valid directory: {path}")
        return tags

    for root, _, files in os.walk(path):
        for filename in files:
            if filename.endswith((".yml", ".txt")):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
                        for line in f:
                            stripped_line = line.strip()

                            # 1. Skip empty lines or lines that are comments.
                            if not stripped_line or stripped_line.startswith('#'):
                                continue

                            # 2. Find content within double quotes.
                            value_match = value_pattern.search(stripped_line)
                            if value_match:
                                quoted_content = value_match.group(1)

                                # 3. Only search for tags within that quoted content.
                                found_tags = tag_pattern.findall(quoted_content)
                                for tag in found_tags:
                                    tags.add(tag)
                except Exception as e:
                    logging.warning(f"Warning: Error reading file {filepath}: {e}")
    return tags

def generate_official_tag_whitelist(game_loc_path: str, output_path: str):
    """
    "法典生成器" (Codex Generator)
    Scans official game localization files to extract all used formatting tags
    and create a definitive "Official Tag Codex".

    Args:
        game_loc_path (str): Path to the directory containing official game localization files.
        output_path (str): The file path to save the generated JSON codex.
    """
    logging.info(f"Starting official tag scan in: {game_loc_path}")

    official_tags = _scan_directory_for_tags(game_loc_path)

    if not official_tags:
        logging.warning(f"No tags found in {game_loc_path}. The output file will be empty.")

    sorted_tags = sorted(list(official_tags))

    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sorted_tags, f, indent=2, ensure_ascii=False)
        logging.info(f"Official tag codex successfully generated at: {output_path}")
        logging.info(f"Found {len(sorted_tags)} unique official tags.")
    except Exception as e:
        logging.error(f"Failed to write the official tag codex to {output_path}: {e}")

def analyze_mod_and_get_all_valid_tags(mod_loc_path: str, official_tags_json_path: str) -> List[str]:
    """
    "异端审判器" (Inquisition Judge)
    Scans a mod's localization files, compares them against the "Official Tag Codex",
    identifies any custom "heretic" tags, and returns a final, combined whitelist.

    Args:
        mod_loc_path (str): Path to the target mod's localization directory.
        official_tags_json_path (str): Path to the generated official tags JSON codex.

    Returns:
        List[str]: A final list of all valid tags for the session (official + custom).
    """
    logging.info(i18n.t("log.tag_analysis.starting_mod_validation"))

    # Load the official codex
    official_tags_set: Set[str] = set()
    try:
        with open(official_tags_json_path, 'r', encoding='utf-8') as f:
            official_tags_set = set(json.load(f))
        logging.info(i18n.t("log.tag_analysis.loaded_official_tags", count=len(official_tags_set), path=official_tags_json_path))
    except FileNotFoundError:
        logging.warning(f"Official tag codex not found at '{official_tags_json_path}'. The validation will only use tags found in the mod.")
    except Exception as e:
        logging.error(f"Error loading official tag codex '{official_tags_json_path}': {e}. Proceeding with an empty list.")

    # Scan the mod for its tags
    mod_tags_set = _scan_directory_for_tags(mod_loc_path)
    logging.info(i18n.t("log.tag_analysis.found_unique_tags", count=len(mod_tags_set)))

    # The Judgement: Find the "heretic" tags
    custom_tags_set = mod_tags_set - official_tags_set

    if custom_tags_set:
        logging.warning(f"Found {len(custom_tags_set)} custom tags (not in the official codex):")
        # Log only a few examples if the list is too long
        for i, tag in enumerate(sorted(list(custom_tags_set))):
            if i < 15:
                logging.warning(f"  - Found custom tag: '#{tag}'")
            elif i == 15:
                logging.warning("  - ... (and more)")
                break
    else:
        logging.info(i18n.t("log.tag_analysis.no_custom_tags"))

    # The Final Verdict: Combine official and custom tags
    final_valid_tags = sorted(list(official_tags_set.union(mod_tags_set)))
    logging.info(i18n.t("log.tag_analysis.final_whitelist", count=len(final_valid_tags)))

    return final_valid_tags
