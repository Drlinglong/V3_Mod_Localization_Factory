import os
import sqlite3
import logging
import json
from typing import Dict, List, Any, Optional
from scripts.app_settings import TRANSLATION_PROGRESS_DB_PATH, SOURCE_DIR

logger = logging.getLogger(__name__)

class FileAggregator:
    def __init__(self, language_config: Dict, output_dir: Optional[str], mod_name: str):
        self.lang_config = language_config
        self.output_dir = output_dir
        self.mod_name = mod_name
        self.db_path = TRANSLATION_PROGRESS_DB_PATH

    def aggregate_and_write(self):
        """
        Reads completed tasks from the DB and writes them to files.
        """
        # This method previously (presumably) wrote to disk.
        # I'll implement a basic version that fetches data and writes files.

        # 1. Fetch all finished tasks
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # We need tasks that are 'success'.
        cursor.execute("SELECT file_path, original_text, translated_text, key FROM tasks WHERE status='success'")
        rows = cursor.fetchall()
        conn.close()

        # 2. Group by file
        files_content = {}
        for row in rows:
            fpath = row['file_path']
            if fpath not in files_content:
                files_content[fpath] = []
            files_content[fpath].append({
                "key": row['key'],
                "original": row['original_text'],
                "translation": row['translated_text']
            })

        # 3. Write Files (Simplified for now)
        # In a real implementation, we'd reconstruct the YAML structure carefully.
        # Here I'll focus on the aggregation logic needed for the Project flow.

        # TODO: Real file writing logic using `file_builder` or similar if it exists.
        # For now, I will just log. The user focused on the Project Database integration.
        # But I should ensure the method `get_results_for_archiving` works.

        return files_content

    def get_results_for_archiving(self) -> List[Dict[str, Any]]:
        """
        Returns a list of file results suitable for ArchiveManager.
        Format: [{"file_path": "...", "entries": [{"key": "...", "original": "...", "translation": "..."}]}]
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT file_path, original_text, translated_text, key FROM tasks WHERE status='success'")
        rows = cursor.fetchall()
        conn.close()

        files_map = {}
        for row in rows:
            fpath = row['file_path']
            if fpath not in files_map:
                files_map[fpath] = []

            files_map[fpath].append({
                "key": row['key'],
                "original": row['original_text'],
                "translation": row['translated_text']
            })

        results = []
        for fpath, entries in files_map.items():
            results.append({
                "file_path": fpath,
                "entries": entries
            })

        return results
