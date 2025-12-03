import os
import json
import shutil
import logging
from scripts.app_settings import get_appdata_config_path

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages reading and writing to the AppData config.json file.
    Includes automatic backup functionality.
    """

    @staticmethod
    def get_config_path():
        return get_appdata_config_path()

    @staticmethod
    def load_config() -> dict:
        """Loads the AppData config.json."""
        config_path = ConfigManager.get_config_path()
        if not os.path.exists(config_path):
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}

    @staticmethod
    def save_config(new_config: dict) -> bool:
        """
        Saves the config to AppData config.json with automatic backup.
        Returns True if successful, raises Exception otherwise.
        """
        config_path = ConfigManager.get_config_path()
        
        # 1. Backup existing config if it exists
        if os.path.exists(config_path):
            try:
                backup_path = config_path + ".bak"
                shutil.copy2(config_path, backup_path)
                logger.info(f"Backed up config to {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to backup config: {e}. Proceeding with save.")
        
        # 2. Save new config
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
            logger.info(f"Config saved successfully to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise e

    @staticmethod
    def get_value(key: str, default=None):
        """Retrieves a specific key from the config."""
        config = ConfigManager.load_config()
        return config.get(key, default)

    @staticmethod
    def set_value(key: str, value):
        """Sets a specific key in the config and saves it."""
        config = ConfigManager.load_config()
        config[key] = value
        ConfigManager.save_config(config)

    @staticmethod
    def update_nested_value(parent_key: str, child_key: str, value):
        """Updates a value inside a nested dictionary (e.g., api_providers -> openai)."""
        config = ConfigManager.load_config()
        if parent_key not in config:
            config[parent_key] = {}
        
        if not isinstance(config[parent_key], dict):
             # If it exists but isn't a dict, we have a problem, but let's overwrite for now or log warning
             logger.warning(f"Config key {parent_key} is not a dict, overwriting.")
             config[parent_key] = {}

        config[parent_key][child_key] = value
        ConfigManager.save_config(config)

config_manager = ConfigManager()
