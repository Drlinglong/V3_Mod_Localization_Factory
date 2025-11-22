import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ProjectJsonManager:
    """
    Manages the .remis_project.json sidecar file for project persistence.
    Stores Kanban state, configuration, and other metadata not suitable for SQLite.
    """

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.json_path = os.path.join(project_root, '.remis_project.json')
        self._ensure_json_exists()

    def _ensure_json_exists(self):
        """Creates the JSON file with default structure if it doesn't exist."""
        if not os.path.exists(self.json_path):
            default_data = {
                "version": "1.0",
                "config": {
                    "translation_dirs": [] # List of absolute paths
                },
                "kanban": {
                    "columns": ["todo", "in_progress", "proofreading", "paused", "done"],
                    "tasks": {}, # Map of taskId -> TaskObject
                    "column_order": ["todo", "in_progress", "proofreading", "paused", "done"]
                }
            }
            self._save_json(default_data)

    def _load_json(self) -> Dict[str, Any]:
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load project JSON: {e}")
            return {}

    def _save_json(self, data: Dict[str, Any]):
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save project JSON: {e}")

    def get_kanban_data(self) -> Dict[str, Any]:
        data = self._load_json()
        return data.get("kanban", {})

    def save_kanban_data(self, kanban_data: Dict[str, Any]):
        data = self._load_json()
        data["kanban"] = kanban_data
        self._save_json(data)

    def get_config(self) -> Dict[str, Any]:
        data = self._load_json()
        return data.get("config", {})

    def update_config(self, config_updates: Dict[str, Any]):
        data = self._load_json()
        if "config" not in data:
            data["config"] = {}
        data["config"].update(config_updates)
        self._save_json(data)

    def add_translation_dir(self, dir_path: str):
        config = self.get_config()
        dirs = config.get("translation_dirs", [])
        if dir_path not in dirs:
            dirs.append(dir_path)
            self.update_config({"translation_dirs": dirs})

    def remove_translation_dir(self, dir_path: str):
        config = self.get_config()
        dirs = config.get("translation_dirs", [])
        if dir_path in dirs:
            dirs.remove(dir_path)
            self.update_config({"translation_dirs": dirs})
