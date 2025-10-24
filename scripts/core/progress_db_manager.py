# scripts/core/progress_db_manager.py
import sqlite3
import os
import logging
import json
from typing import Optional, List, Dict, Any

from scripts.utils import i18n
from scripts.app_settings import PROJECT_ROOT

PROGRESS_DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'translation_progress.sqlite')

class ProgressDBManager:
    """
    管理翻译任务的进度，与 translation_progress.sqlite 数据库交互。
    这个数据库是临时的，用于确保翻译过程的崩溃安全和可恢复性。
    """
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_db()

    def _initialize_db(self):
        """初始化数据库连接和表结构"""
        try:
            self.conn = sqlite3.connect(PROGRESS_DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._create_table()
            logging.info(i18n.t("log_info_progress_db_connected", path=PROGRESS_DB_PATH))
        except Exception as e:
            logging.error(i18n.t("log_error_db_connect", error=e))
            self.conn = None

    def _create_table(self):
        """创建用于存储已完成批次的表"""
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            # source_hash is optional but recommended for detecting file changes
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS translated_batches (
                job_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                batch_index INTEGER NOT NULL,
                source_hash TEXT,
                translated_text TEXT NOT NULL,
                PRIMARY KEY (job_id, file_path, batch_index)
            )
            """)
            self.conn.commit()
        except Exception as e:
            logging.error(i18n.t("log_error_db_create_table", error=e))

    def add_batch_result(self, file_path: str, batch_index: int, translated_texts: List[str], source_hash: Optional[str] = None):
        """将完成的批次结果写入数据库"""
        if not self.conn:
            return
        try:
            translated_text_json = json.dumps(translated_texts, ensure_ascii=False)
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO translated_batches (job_id, file_path, batch_index, translated_text, source_hash)
            VALUES (?, ?, ?, ?, ?)
            """, (self.job_id, file_path, batch_index, translated_text_json, source_hash))
            self.conn.commit()
            logging.debug(f"Successfully added batch result for job '{self.job_id}', file '{file_path}', batch {batch_index}")
        except Exception as e:
            logging.error(f"Failed to add batch result for job '{self.job_id}', file '{file_path}', batch {batch_index}: {e}")

    def is_batch_completed(self, file_path: str, batch_index: int) -> bool:
        """检查特定批次是否已存在于数据库中"""
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT 1 FROM translated_batches
            WHERE job_id = ? AND file_path = ? AND batch_index = ?
            """, (self.job_id, file_path, batch_index))
            return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"Failed to check batch completion for job '{self.job_id}', file '{file_path}', batch {batch_index}: {e}")
            return False

    def get_all_completed_batches_for_job(self) -> List[Dict[str, Any]]:
        """获取指定任务ID的所有已完成批次"""
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT file_path, batch_index, translated_text FROM translated_batches
            WHERE job_id = ?
            ORDER BY file_path, batch_index
            """, (self.job_id,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "file_path": row["file_path"],
                    "batch_index": row["batch_index"],
                    "translated_texts": json.loads(row["translated_text"])
                })
            return results
        except Exception as e:
            logging.error(f"Failed to get all completed batches for job '{self.job_id}': {e}")
            return []

    def cleanup_job_data(self):
        """在任务成功结束后，清理相关的数据库记录"""
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            DELETE FROM translated_batches WHERE job_id = ?
            """, (self.job_id,))
            self.conn.commit()
            logging.info(i18n.t("log_info_progress_db_cleaned", job_id=self.job_id, count=cursor.rowcount))
        except Exception as e:
            logging.error(f"Failed to clean up job data for job '{self.job_id}': {e}")

    def get_completed_batch_count(self) -> int:
        """获取当前任务已完成的批次数量"""
        if not self.conn:
            return 0
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM translated_batches WHERE job_id = ?", (self.job_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logging.error(f"Failed to get completed batch count for job '{self.job_id}': {e}")
            return 0


    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logging.info(i18n.t("log_info_progress_db_closed", job_id=self.job_id))
