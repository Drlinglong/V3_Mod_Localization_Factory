import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional
from scripts.app_settings import MODS_CACHE_DB_PATH

logger = logging.getLogger(__name__)

class ArchiveManager:
    def __init__(self, db_path: str = MODS_CACHE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = self._get_connection()
        cursor = conn.cursor()

        # Mod Identities (to link ID to Name/Version)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mods (
                mod_id INTEGER PRIMARY KEY AUTOINCREMENT,
                mod_name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Source Versions (Snapshots of the source files)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS source_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                mod_id INTEGER,
                file_path TEXT NOT NULL,
                key TEXT NOT NULL,
                original_text TEXT,
                version_hash TEXT, -- Hash of the text/context to track changes
                FOREIGN KEY(mod_id) REFERENCES mods(mod_id),
                UNIQUE(mod_id, file_path, key)
            )
        ''')

        # Translated Entries (Linked to Source)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translated_entries (
                translation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_entry_id INTEGER,
                language TEXT NOT NULL,
                translated_text TEXT,
                provider TEXT,
                model TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(source_entry_id) REFERENCES source_entries(entry_id),
                UNIQUE(source_entry_id, language)
            )
        ''')

        conn.commit()
        conn.close()

    def get_mod_id(self, mod_name: str, create: bool = False) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT mod_id FROM mods WHERE mod_name = ?", (mod_name,))
        row = cursor.fetchone()

        if row:
            conn.close()
            return row[0]

        if create:
            cursor.execute("INSERT INTO mods (mod_name) VALUES (?)", (mod_name,))
            mod_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return mod_id

        conn.close()
        return None

    def store_translation_snapshot(self, mod_name: str, file_results: List[Dict[str, Any]], language: str = "zh"):
        """
        Stores a batch of translation results.
        file_results expected format:
        [
            {
                "file_path": "common/file.yml",
                "entries": [
                    {"key": "KEY_1", "original": "Text", "translation": "Translated"}
                ]
            }
        ]
        """
        mod_id = self.get_mod_id(mod_name, create=True)
        conn = self._get_connection()
        cursor = conn.cursor()

        for file_data in file_results:
            file_path = file_data['file_path']
            for entry in file_data['entries']:
                key = entry['key']
                original = entry['original']
                translation = entry['translation']

                # 1. Upsert Source Entry
                cursor.execute('''
                    INSERT INTO source_entries (mod_id, file_path, key, original_text)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(mod_id, file_path, key) DO UPDATE SET
                    original_text=excluded.original_text
                ''', (mod_id, file_path, key, original))

                # Get source_entry_id
                cursor.execute("SELECT entry_id FROM source_entries WHERE mod_id=? AND file_path=? AND key=?",
                               (mod_id, file_path, key))
                source_entry_id = cursor.fetchone()[0]

                # 2. Upsert Translation
                cursor.execute('''
                    INSERT INTO translated_entries (source_entry_id, language, translated_text)
                    VALUES (?, ?, ?)
                    ON CONFLICT(source_entry_id, language) DO UPDATE SET
                    translated_text=excluded.translated_text,
                    updated_at=CURRENT_TIMESTAMP
                ''', (source_entry_id, language, translation))

        conn.commit()
        conn.close()

    def get_entries(self, mod_name: str, file_path: str, language: str = "zh") -> List[Dict[str, Any]]:
        """
        Retrieves merged source and translation entries for a specific file.
        """
        mod_id = self.get_mod_id(mod_name)
        if not mod_id:
            return []

        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = '''
            SELECT
                s.key,
                s.original_text as original,
                t.translated_text as translation
            FROM source_entries s
            LEFT JOIN translated_entries t ON s.entry_id = t.source_entry_id AND t.language = ?
            WHERE s.mod_id = ? AND s.file_path = ?
        '''

        cursor.execute(query, (language, mod_id, file_path))
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_translations(self, mod_name: str, file_path: str, entries: List[Dict[str, Any]], language: str = "zh"):
        """
        Updates translations for specific keys.
        entries: [{"key": "...", "translation": "..."}]
        """
        mod_id = self.get_mod_id(mod_name)
        if not mod_id:
            return # Or raise error

        conn = self._get_connection()
        cursor = conn.cursor()

        for entry in entries:
            key = entry['key']
            translation = entry.get('translation', '')

            # Find source entry ID
            cursor.execute("SELECT entry_id FROM source_entries WHERE mod_id=? AND file_path=? AND key=?",
                           (mod_id, file_path, key))
            row = cursor.fetchone()

            if row:
                source_entry_id = row[0]
                # Upsert translation
                cursor.execute('''
                    INSERT INTO translated_entries (source_entry_id, language, translated_text)
                    VALUES (?, ?, ?)
                    ON CONFLICT(source_entry_id, language) DO UPDATE SET
                    translated_text=excluded.translated_text,
                    updated_at=CURRENT_TIMESTAMP
                ''', (source_entry_id, language, translation))

        conn.commit()
        conn.close()
