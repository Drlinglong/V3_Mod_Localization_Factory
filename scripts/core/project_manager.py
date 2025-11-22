import sqlite3
import os
import shutil
import uuid
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from scripts.app_settings import PROJECTS_DB_PATH, SOURCE_DIR

# Configure logger
logger = logging.getLogger(__name__)

@dataclass
class Project:
    project_id: str
    name: str
    game_id: str
    source_path: str
    target_path: str
    status: str  # 'active', 'archived', etc.
    created_at: str

@dataclass
class ProjectFile:
    file_id: str
    project_id: str
    file_path: str  # Relative path within the project source
    status: str  # 'todo', 'proofreading', 'done'
    original_key_count: int

class ProjectManager:
    def __init__(self, db_path: str = PROJECTS_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize the projects database tables."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                game_id TEXT NOT NULL,
                source_path TEXT NOT NULL,
                target_path TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create ProjectFiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_files (
                file_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT DEFAULT 'todo',
                original_key_count INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                UNIQUE(project_id, file_path)
            )
        ''')

        conn.commit()
        conn.close()

    def create_project(self, name: str, folder_path: str, game_id: str) -> Project:
        """
        Creates a new project.
        1. Moves folder to SOURCE_DIR if not already there.
        2. Scans for files.
        3. Creates DB records.
        """
        logger.info(f"Creating project '{name}' from '{folder_path}' for game '{game_id}'")

        # 1. Handle Folder Movement/Validation
        source_root = os.path.abspath(SOURCE_DIR)
        abs_folder_path = os.path.abspath(folder_path)

        final_source_path = abs_folder_path

        # Check if folder is inside SOURCE_DIR
        if not abs_folder_path.startswith(source_root):
            logger.info(f"Folder {abs_folder_path} is not in {source_root}. Moving...")
            target_dir_name = os.path.basename(abs_folder_path)
            final_source_path = os.path.join(source_root, target_dir_name)

            # Handle naming collision
            counter = 1
            base_name = target_dir_name
            while os.path.exists(final_source_path):
                target_dir_name = f"{base_name}_{counter}"
                final_source_path = os.path.join(source_root, target_dir_name)
                counter += 1

            try:
                shutil.move(abs_folder_path, final_source_path)
                logger.info(f"Moved to {final_source_path}")
            except Exception as e:
                logger.error(f"Failed to move folder: {e}")
                raise RuntimeError(f"Failed to move folder to source directory: {e}")
        else:
            logger.info("Folder is already in source directory.")

        # 2. Generate IDs and Data
        project_id = str(uuid.uuid4())
        # Target path defaults to a sibling folder with _translation suffix, or whatever convention
        # User said: "translation flow is reading from source directory (source_mod), generating to target directory (my_translation)"
        # We'll define target_path relative to source or a fixed output dir?
        # Usually output is in 'outputs' or similar.
        # For now, let's assume a standard output directory pattern or just store the name.
        # Let's stick to the user's example: source_mod -> my_translation.
        # But multiple projects might collide if they all map to "my_translation".
        # I will use `{final_source_path}_translation` as a default distinct target for now to avoid collision,
        # or just `outputs/{project_name}`.
        # Let's use a safe default: 'outputs/<project_name>' relative to app root or just the full path.
        # App Settings usually has an OUTPUT_DIR? checking...
        # I'll assume an 'outputs' folder sibling to 'source' or similar.
        # checking app_settings.py in next step to confirm if OUTPUT_DIR exists.
        # defaulting to a subdirectory in the project for now or a sibling.
        target_path = f"{final_source_path}_translation"

        project = Project(
            project_id=project_id,
            name=name,
            game_id=game_id,
            source_path=final_source_path,
            target_path=target_path,
            status='active',
            created_at='' # DB handles this
        )

        # 3. DB Insertion
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO projects (project_id, name, game_id, source_path, target_path, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project.project_id, project.name, project.game_id, project.source_path, project.target_path, project.status))

        # 4. Scan Files
        files_to_insert = []
        for root, dirs, files in os.walk(final_source_path):
            for file in files:
                if file.endswith('.yml') or file.endswith('.yaml') or file.endswith('.txt') or file.endswith('.csv') or file.endswith('.json'):
                    # Only track potentially localizable files.
                    # User mainly mentioned .yml for Paradox games but "txt/csv/json" might be valid too.
                    # I'll stick to a broad filter or just all files?
                    # "Scan all files" was the prompt.
                    # But for translation, we usually care about text files.
                    # I will include all files for the manifest, but status 'todo' applies to localizable ones.
                    # For now, let's just grab everything, but maybe flag extension.
                    # Actually, `initial_translate` filters by extension.
                    # I'll scan all, but `initial_translate` will only pick up what it supports.
                    # Let's just scan everything to be safe as a "File Manifest".

                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, final_source_path)
                    file_id = str(uuid.uuid4())

                    # Simple key count estimation (can be refined later or updated by parser)
                    # For now 0.
                    files_to_insert.append((file_id, project_id, rel_path, 'todo', 0))

        if files_to_insert:
            cursor.executemany('''
                INSERT INTO project_files (file_id, project_id, file_path, status, original_key_count)
                VALUES (?, ?, ?, ?, ?)
            ''', files_to_insert)

        conn.commit()
        conn.close()

        return project

    def get_projects(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM project_files WHERE project_id = ? ORDER BY file_path", (project_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_file_status(self, project_id: str, file_path: str, status: str):
        """Updates the status of a file in a project."""
        conn = self._get_connection()
        cursor = conn.cursor()
        # Use file_path + project_id to identify
        cursor.execute('''
            UPDATE project_files
            SET status = ?
            WHERE project_id = ? AND file_path = ?
        ''', (status, project_id, file_path))
        conn.commit()
        conn.close()

    def update_file_status_by_id(self, file_id: str, status: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE project_files SET status = ? WHERE file_id = ?", (status, file_id))
        conn.commit()
        conn.close()
