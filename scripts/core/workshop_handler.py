# scripts/core/workshop_handler.py
import os
import json
import logging
import re
from typing import Dict, Optional

from scripts.utils import i18n
from scripts.app_settings import SOURCE_DIR

def try_auto_extract_workshop_id(mod_name: str, game_profile: dict) -> Dict:
    """
    Tries to automatically extract the workshop ID by checking metadata.json and then descriptor.mod.
    Logs the outcome and returns a dictionary with the ID and status.
    """
    # 优先检查 metadata.json (新格式)
    meta_json_path = os.path.join(SOURCE_DIR, mod_name, '.metadata', 'metadata.json')
    try:
        if os.path.exists(meta_json_path):
            with open(meta_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'remote_file_id' in data and data['remote_file_id']:
                    found_id = str(data['remote_file_id'])
                    logging.info(i18n.t("log_info_workshop_id_auto_found", id=found_id))
                    return {'id': found_id, 'status': 'auto'}
    except Exception as e:
        logging.error(i18n.t("log_error_parsing_mod_file", path=meta_json_path, error=e))

    # 回退检查 descriptor.mod (旧格式)
    descriptor_filename = game_profile.get('descriptor_filename', 'descriptor.mod')
    possible_mod_paths = [
        os.path.join(SOURCE_DIR, mod_name, descriptor_filename),
        os.path.join(SOURCE_DIR, mod_name, '.metadata', descriptor_filename)
    ]

    for mod_file_path in possible_mod_paths:
        if os.path.exists(mod_file_path):
            try:
                with open(mod_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'remote_file_id="(\d+)"', content)
                    if match:
                        found_id = match.group(1)
                        logging.info(i18n.t("log_info_workshop_id_auto_found", id=found_id))
                        return {'id': found_id, 'status': 'auto'}
                # Found a .mod file but it didn't contain the ID.
                logging.warning(i18n.t("log_warn_remote_id_not_in_file", path=mod_file_path))
            except Exception as e:
                logging.error(i18n.t("log_error_parsing_mod_file", path=mod_file_path, error=e))
    
    # If we reach here, no ID was found in any file.
    logging.warning(i18n.t("log_warn_workshop_id_auto_fail"))
    return {'id': None, 'status': 'not_found'}