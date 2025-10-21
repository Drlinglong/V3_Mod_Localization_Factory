# scripts/developer_tools/generate_all_codexes.py
import sys
import os
import logging

# Add the project root to the Python path to allow importing from scripts
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.app_settings import GAME_PROFILES
from scripts.utils import tag_scanner

# --- DEVELOPER-SPECIFIC CONFIGURATION ---
# Please update these paths to match your local game installation directories.
# This is a developer tool, so it's okay to have hardcoded local paths here.
GAME_INSTALLATION_PATHS = {
    "victoria3": "I:\\SteamLibrary\\steamapps\\common\\Victoria 3\\game\\localization",
    "stellaris": "I:\\SteamLibrary\\steamapps\\common\\Stellaris\\localisation",
    "hoi4": "I:\\SteamLibrary\\steamapps\\common\\Hearts of Iron IV\\localisation",
    "eu4": "K:\\SteamLibrary\\steamapps\\common\\Europa Universalis IV\\localisation",
    "ck3": "K:\\SteamLibrary\\steamapps\\common\\Crusader Kings III\\game\\localization",
}

def main():
    """
    Main function to generate official tag codexes for all supported games.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting the process to generate official tag codexes for all supported games...")

    success_count = 0
    fail_count = 0

    for game_key, game_profile in GAME_PROFILES.items():
        game_id = game_profile.get("id")
        if not game_id:
            logging.warning(f"Skipping game profile with key '{game_key}' as it has no 'id'.")
            continue

        logging.info(f"--- Processing game: {game_profile.get('name', game_id)} ---")

        # 1. Get the game's installation path from our hardcoded dictionary
        game_loc_path = GAME_INSTALLATION_PATHS.get(game_id)
        if not game_loc_path:
            logging.error(f"  - ERROR: Local installation path for '{game_id}' not found in GAME_INSTALLATION_PATHS. Please add it.")
            fail_count += 1
            continue

        if not os.path.isdir(game_loc_path):
            logging.error(f"  - ERROR: The configured path for '{game_id}' does not exist or is not a directory: {game_loc_path}")
            fail_count += 1
            continue

        # 2. Get the target output path from the game profile in app_settings
        output_path = game_profile.get("official_tags_codex")
        if not output_path:
            logging.error(f"  - ERROR: 'official_tags_codex' path is not defined for '{game_id}' in app_settings.py.")
            fail_count += 1
            continue

        # Ensure the output path is absolute
        absolute_output_path = os.path.join(project_root, output_path)

        # 3. Call the scanner to generate the codex
        try:
            logging.info(f"  - Scanning: {game_loc_path}")
            logging.info(f"  - Output to: {absolute_output_path}")
            tag_scanner.generate_official_tag_whitelist(game_loc_path, absolute_output_path)
            success_count += 1
        except Exception as e:
            logging.error(f"  - FATAL: An unexpected error occurred while processing '{game_id}': {e}")
            fail_count += 1

    logging.info("--- Generation Complete ---")
    logging.info(f"Successfully generated codexes: {success_count}")
    logging.info(f"Failed to generate codexes: {fail_count}")
    if fail_count > 0:
        logging.warning("Please review the errors above and ensure all paths are configured correctly.")

if __name__ == "__main__":
    main()
