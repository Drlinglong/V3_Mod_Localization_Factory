# scripts/core/archive_manager.py
import sqlite3
import os
import logging
import hashlib
from typing import Dict, List, Optional, Tuple, Any
import re
import json

from scripts.utils import i18n
from scripts.app_settings import PROJECT_ROOT, SOURCE_DIR

MODS_CACHE_DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'mods_cache.sqlite')

class ArchiveManager:
    """
    管理模组翻译结果的归档，与 mods_cache.sqlite 数据库交互。
    """
    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None

    def initialize_database(self) -> bool:
        """Initializes the database connection. Returns True on success, False on failure."""
        if self.conn:
            return True
        try:
            self.conn = sqlite3.connect(MODS_CACHE_DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._create_tables(self.conn)
            logging.info(i18n.t("log_info_db_connected", path=MODS_CACHE_DB_PATH))
            return True
        except Exception as e:
            logging.error(i18n.t("log_error_db_connect", error=e))
            self.conn = None
            return False

    def _create_tables(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS mods (mod_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS mod_identities (identity_id INTEGER PRIMARY KEY AUTOINCREMENT, mod_id INTEGER NOT NULL, remote_file_id TEXT NOT NULL UNIQUE, FOREIGN KEY (mod_id) REFERENCES mods (mod_id))")
        cursor.execute("CREATE TABLE IF NOT EXISTS source_versions (version_id INTEGER PRIMARY KEY AUTOINCREMENT, mod_id INTEGER NOT NULL, snapshot_hash TEXT NOT NULL UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (mod_id) REFERENCES mods (mod_id))")
        cursor.execute("CREATE TABLE IF NOT EXISTS source_entries (source_entry_id INTEGER PRIMARY KEY AUTOINCREMENT, version_id INTEGER NOT NULL, entry_key TEXT NOT NULL, source_text TEXT NOT NULL, UNIQUE(version_id, entry_key), FOREIGN KEY (version_id) REFERENCES source_versions (version_id))")
        cursor.execute("CREATE TABLE IF NOT EXISTS translated_entries (translated_entry_id INTEGER PRIMARY KEY AUTOINCREMENT, source_entry_id INTEGER NOT NULL, language_code TEXT NOT NULL, translated_text TEXT NOT NULL, last_translated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(source_entry_id, language_code), FOREIGN KEY (source_entry_id) REFERENCES source_entries (source_entry_id))")
        conn.commit()

    def get_or_create_mod_entry(self, mod_name: str, remote_file_id: str) -> Optional[int]:
        """阶段一: 根据 remote_file_id 查询或创建 mod 记录，返回内部 mod_id"""
        if not self.conn: return None

        cursor = self.conn.cursor()
        try:
            # 检查 remote_file_id 是否已存在
            cursor.execute("SELECT mod_id FROM mod_identities WHERE remote_file_id = ?", (remote_file_id,))
            result = cursor.fetchone()
            if result:
                return result['mod_id']

            # 如果不存在，则创建新 mod 和 identity
            cursor.execute("INSERT OR IGNORE INTO mods (name) VALUES (?)", (mod_name,))
            # 获取刚刚插入或已存在的 mod_id
            cursor.execute("SELECT mod_id FROM mods WHERE name = ?", (mod_name,))
            mod_id_result = cursor.fetchone()
            if not mod_id_result:
                 raise Exception("Failed to retrieve mod_id after insertion.")
            mod_id = mod_id_result['mod_id']

            cursor.execute("INSERT INTO mod_identities (mod_id, remote_file_id) VALUES (?, ?)", (mod_id, remote_file_id))
            self.conn.commit()
            logging.info(i18n.t("log_info_archive_entry_created", mod_name=mod_name, mod_id=mod_id, remote_file_id=remote_file_id))
            return mod_id
        except sqlite3.IntegrityError:
             # This can happen in a race condition, so we try to fetch the id again.
            cursor.execute("SELECT mod_id FROM mod_identities WHERE remote_file_id = ?", (remote_file_id,))
            result = cursor.fetchone()
            if result:
                return result['mod_id']
            logging.error(i18n.t("log_error_archive_integrity"))
            return None
        except Exception as e:
            logging.error(i18n.t("log_error_db_get_create_mod_id", error=e))
            self.conn.rollback()
            return None

    def create_source_version(self, mod_id: int, all_files_data: List[Dict]) -> Optional[int]:
        """阶段二: 计算哈希，如果不存在则创建源版本快照"""
        if not self.conn: return None

        # 1. 计算总哈希
        hasher = hashlib.sha256()
        # Sort by filename to ensure consistent hash
        sorted_files = sorted(all_files_data, key=lambda x: x['filename'])
        for file_data in sorted_files:
            for text in file_data['texts_to_translate']:
                hasher.update(text.encode('utf-8'))
        snapshot_hash = hasher.hexdigest()

        cursor = self.conn.cursor()
        try:
            # 2. 检查哈希是否存在
            cursor.execute("SELECT version_id FROM source_versions WHERE snapshot_hash = ?", (snapshot_hash,))
            result = cursor.fetchone()
            if result:
                logging.info(i18n.t("log_info_source_version_exists", hash=snapshot_hash[:7], version_id=result['version_id']))
                return result['version_id']

            # 3. 创建新版本
            cursor.execute("INSERT INTO source_versions (mod_id, snapshot_hash) VALUES (?, ?)", (mod_id, snapshot_hash))
            version_id = cursor.lastrowid
            logging.info(i18n.t("log_info_created_source_version", version_id=version_id, mod_id=mod_id, hash=snapshot_hash[:7]))

            # 4. 插入所有源条目
            source_entries = []
            for file_data in all_files_data:
                for key, text in zip(file_data['key_map'], file_data['texts_to_translate']):
                    source_entries.append((version_id, key, text))

            cursor.executemany("INSERT INTO source_entries (version_id, entry_key, source_text) VALUES (?, ?, ?)", source_entries)
            self.conn.commit()
            logging.info(i18n.t("log_info_archived_source_entries", count=len(source_entries), version_id=version_id))
            return version_id
        except Exception as e:
            logging.error(i18n.t("log_error_db_create_source_version", error=e))
            self.conn.rollback()
            return None

    def archive_translated_results(self, version_id: int, file_results: Dict[str, Any], all_files_data: List[Dict], target_lang_code: str):
        """阶段三: 将指定语言的翻译结果存入或更新到数据库"""
        if not self.conn or not version_id: return

        cursor = self.conn.cursor()
        try:
            # 1. 构建 key -> translated_text 的映射
            key_to_translation = {}
            for filename, translated_texts in file_results.items():
                # Find the corresponding file_data
                file_data = next((fd for fd in all_files_data if fd['filename'] == filename), None)
                if not file_data or not translated_texts: continue

                for key, translated_text in zip(file_data['key_map'], translated_texts):
                    key_to_translation[key] = translated_text

            if not key_to_translation:
                logging.warning(i18n.t("log_warn_no_translations_to_archive"))
                return

            # 2. 准备 UPSERT 数据
            upsert_data = []
            # Fetch all relevant source_entry_ids at once for efficiency
            keys = list(key_to_translation.keys())
            placeholders = ','.join('?' for _ in keys)
            cursor.execute(f"SELECT source_entry_id, entry_key FROM source_entries WHERE version_id = ? AND entry_key IN ({placeholders})", [version_id] + keys)
            source_entry_map = {row['entry_key']: row['source_entry_id'] for row in cursor.fetchall()}

            for key, translated_text in key_to_translation.items():
                source_entry_id = source_entry_map.get(key)
                if source_entry_id:
                    upsert_data.append((source_entry_id, target_lang_code, translated_text, translated_text))

            # 3. 执行 UPSERT
            cursor.executemany("""
                INSERT INTO translated_entries (source_entry_id, language_code, translated_text)
                VALUES (?, ?, ?)
                ON CONFLICT(source_entry_id, language_code) DO UPDATE SET
                translated_text = excluded.translated_text,
                last_translated_at = CURRENT_TIMESTAMP
            """, upsert_data)

            self.conn.commit()
            logging.info(i18n.t("log_info_archived_updated_translations", count=len(upsert_data), lang_code=target_lang_code))

        except Exception as e:
            logging.error(i18n.t("log_error_db_archive_results", lang_code=target_lang_code, error=e))
            self.conn.rollback()

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info(i18n.t("log_info_db_connection_closed"))

# 全局实例
archive_manager = ArchiveManager()
