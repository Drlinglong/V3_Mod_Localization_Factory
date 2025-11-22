import sqlite3
import os
import shutil
import uuid
import datetime
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from scripts.app_settings import PROJECTS_DB_PATH, SOURCE_DIR

# Configure logger
logger = logging.getLogger(__name__)

from scripts.core.project_json_manager import ProjectJsonManager

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
    line_count: int = 0 # Added line count
    file_type: str = 'source' # 'source' or 'translation'

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
                target_path TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create ProjectFiles table
        # Added line_count and file_type columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_files (
                file_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT DEFAULT 'todo',
                original_key_count INTEGER DEFAULT 0,
                line_count INTEGER DEFAULT 0,
                file_type TEXT DEFAULT 'source',
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                UNIQUE(project_id, file_path)
            )
        ''')
        
        # Migration: Check if new columns exist, if not add them
        cursor.execute("PRAGMA table_info(project_files)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'line_count' not in columns:
            cursor.execute("ALTER TABLE project_files ADD COLUMN line_count INTEGER DEFAULT 0")
        if 'file_type' not in columns:
            cursor.execute("ALTER TABLE project_files ADD COLUMN file_type TEXT DEFAULT 'source'")

        conn.commit()
        conn.close()

    def create_project(self, name: str, folder_path: str, game_id: str) -> Project:
        """
        Creates a new project.
        1. Moves folder to SOURCE_DIR if not already there.
        2. Scans for files.
        3. Creates DB records.
        4. Initializes JSON sidecar.
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
                shutil.copytree(abs_folder_path, final_source_path)
                logger.info(f"Copied to {final_source_path}")
            except Exception as e:
                logger.error(f"Failed to copy folder: {e}")
                raise RuntimeError(f"Failed to copy folder to source directory: {e}")
        else:
            logger.info("Folder is already in source directory.")

        # Initialize JSON sidecar with empty translation_dirs
        # User will add translation directories via Manage Paths UI
        json_manager = ProjectJsonManager(final_source_path)
        json_manager.update_config({
            "translation_dirs": []
        })

        # Create project record in database
        project_id = str(uuid.uuid4())
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (project_id, name, game_id, source_path, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_id, name, game_id, final_source_path, 'active', datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()

        # Create project object for return
        project = {
            'project_id': project_id,
            'name': name,
            'game_id': game_id,
            'source_path': final_source_path,
            'status': 'active'
        }

        # Scan files (Initial Scan)
        self.refresh_project_files(project_id)

        return project

    def refresh_project_files(self, project_id: str):
        """Rescans source and translation directories and updates the DB and JSON sidecar."""
        project = self.get_project(project_id)
        if not project:
            logger.error(f"Project {project_id} not found")
            return

        source_path = project['source_path']
        
        # Get translation_dirs from JSON sidecar
        try:
            json_manager = ProjectJsonManager(source_path)
            config = json_manager.get_config()
            translation_dirs = config.get('translation_dirs', [])
            logger.info(f"Loaded {len(translation_dirs)} translation directories from config")
        except Exception as e:
            logger.error(f"Failed to load translation_dirs from JSON: {e}")
            translation_dirs = []

        # Collect all files to upsert
        files_to_upsert = []
        
        # Helper to scan a directory
        def scan_dir(root_path, file_type):
            if not os.path.exists(root_path):
                logger.warning(f"Directory not found: {root_path}")
                return
            for root, dirs, files in os.walk(root_path):
                for file in files:
                    if file.endswith(('.yml', '.yaml', '.txt', '.csv', '.json')):
                        full_path = os.path.join(root, file)
                        
                        # Count lines
                        line_count = 0
                        try:
                            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                                line_count = sum(1 for _ in f)
                        except Exception as e:
                            logger.error(f"Failed to count lines for {full_path}: {e}")

                        files_to_upsert.append({
                            'file_id': str(uuid.uuid5(uuid.NAMESPACE_URL, full_path)),
                            'project_id': project_id,
                            'file_path': full_path,
                            'status': 'todo',
                            'original_key_count': 0,
                            'line_count': line_count,
                            'file_type': file_type
                        })

        # Scan source directory
        scan_dir(source_path, 'source')
        
        # Scan translation directories
        for trans_dir in translation_dirs:
            scan_dir(trans_dir, 'translation')

        logger.info(f"Found {len(files_to_upsert)} total files to upsert")

        # Upsert into DB
        conn = self._get_connection()
        cursor = conn.cursor()

        for f in files_to_upsert:
            # Upsert logic
            cursor.execute('''
                INSERT INTO project_files (file_id, project_id, file_path, status, original_key_count, line_count, file_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id, file_path) DO UPDATE SET
                    line_count = excluded.line_count,
                    file_type = excluded.file_type
            ''', (f['file_id'], f['project_id'], f['file_path'], f['status'], f['original_key_count'], f['line_count'], f['file_type']))
        
        conn.commit()
        conn.close()

        # Update Kanban (Sync tasks)
        self._sync_kanban_with_files(project_id, files_to_upsert)

        # --- Archive Integration (Populate Source DB) ---
        # Only process source files for now to enable Proofreading
        from scripts.core.archive_manager import archive_manager
        from scripts.core.loc_parser import parse_loc_file
        from pathlib import Path

        source_files_data = []
        for f in files_to_upsert:
            if f['file_type'] == 'source' and f['file_path'].endswith(('.yml', '.yaml')):
                try:
                    entries = parse_loc_file(Path(f['file_path']))
                    if entries:
                        source_files_data.append({
                            'filename': os.path.basename(f['file_path']),
                            'key_map': [e[0] for e in entries],
                            'texts_to_translate': [e[1] for e in entries]
                        })
                except Exception as e:
                    logger.error(f"Failed to parse {f['file_path']} for archiving: {e}")

        if source_files_data:
            # We need a mod_id. Use project name as mod name?
            # Or use project_id? archive_manager uses 'name' as unique key for mods table.
            # Let's use project.name.
            mod_id = archive_manager.get_or_create_mod_entry(project['name'], project_id)
            if mod_id:
                archive_manager.create_source_version(mod_id, source_files_data)


    def _sync_kanban_with_files(self, project_id: str, files: List[Dict]):
        """
        Syncs the file list with the Kanban board in JSON sidecar.
        Creates a task for each SOURCE file.
        Translation files are tracked as metadata on the source file task.
        """
        project = self.get_project(project_id)
        if not project:
            return
            
        json_manager = ProjectJsonManager(project['source_path'])
        kanban_data = json_manager.get_kanban_data()
        tasks = kanban_data.get("tasks", {})
        columns = kanban_data.get("columns", [])
        
        # Ensure 'todo' column exists
        if "todo" not in columns:
            columns.insert(0, "todo")

        # Group files by relative path (ignoring language prefix/suffix if possible, 
        # but for now, we assume source files are the master).
        # Strategy:
        # 1. Iterate over SOURCE files to create/update tasks.
        # 2. Iterate over TRANSLATION files to update status/metadata of corresponding source task.
        
        # Helper to get relative path from full path
        # We need to know which root it came from.
        # But `files` list doesn't explicitly say which root.
        # However, we know source files come from project['source_path'].
        
        source_path = project['source_path']
        
        # 1. Process Source Files
        source_file_count = 0
        for f in files:
            if f['file_type'] == 'source':
                source_file_count += 1
                # Determine relative path for ID stability
                # If file is inside source_path
                if f['file_path'].startswith(source_path):
                    rel_path = os.path.relpath(f['file_path'], source_path)
                else:
                    # Should not happen for source files based on create_project logic,
                    # but if it does, use basename or full path hash
                    rel_path = os.path.basename(f['file_path'])
                
                # Task ID based on relative path (stable across machines if relative)
                # But we used uuid5(full_path) for file_id.
                # Let's use file_id of the SOURCE file as the Task ID.
                task_id = f['file_id'] 
                
                if task_id not in tasks:
                    # Create new task
                    tasks[task_id] = {
                        "id": task_id,
                        "type": "file",
                        "title": os.path.basename(f['file_path']),
                        "filePath": f['file_path'], # Source file path
                        "status": "todo",
                        "comments": "",
                        "priority": "medium",
                        "meta": {
                            "source_lines": f['line_count'],
                            "translation_status": {}, # Lang code -> status
                            "rel_path": rel_path
                        }
                    }
                else:
                    # Update existing task meta
                    if "meta" not in tasks[task_id]: tasks[task_id]["meta"] = {}
                    tasks[task_id]["meta"]["source_lines"] = f['line_count']
                    tasks[task_id]["meta"]["rel_path"] = rel_path
                    # Update title
                    tasks[task_id]["title"] = os.path.basename(f['file_path'])

        # 2. Process Translation Files (Update Status)
        # We need to link translation files to source files.
        # Assumption: Translation file has same relative path structure or same basename?
        # Usually:
        # Source: localization/english/foo_l_english.yml
        # Target: localization/simp_chinese/foo_l_simp_chinese.yml
        # This mapping is complex to reverse engineer perfectly without strict conventions.
        # FOR NOW: We will just list source files as tasks.
        # Future: We can try to match them, but it's risky.
        # Let's stick to: Kanban manages SOURCE files (which represent the "content" to be translated).
        # The status of the task represents the overall progress.
        
        # If we want to show translation progress, we need to know which languages are done.
        # This requires the `refresh_project_files` to be smarter about matching.
        # For this iteration, let's just ensure Source files are on the board.
        
        logger.info(f"Syncing Kanban: Found {source_file_count} source files. Saving {len(tasks)} tasks.")
        json_manager.save_kanban_data({
            "columns": columns,
            "tasks": tasks,
            "column_order": kanban_data.get("column_order", columns)
        })

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

    def delete_project(self, project_id: str, delete_source_files: bool = False):
        """Deletes a project from the database and optionally deletes source files."""
        project = self.get_project(project_id)
        if not project:
            return False
        
        # Delete from database (CASCADE will handle project_files)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
        conn.commit()
        conn.close()
        
        # Optionally delete source directory
        if delete_source_files:
            source_path = project['source_path']
            if os.path.exists(source_path):
                try:
                    shutil.rmtree(source_path)
                    logger.info(f"Deleted source directory: {source_path}")
                except Exception as e:
                    logger.error(f"Failed to delete source directory {source_path}: {e}")
            
            # Also delete JSON sidecar
            json_path = os.path.join(source_path, '.remis_project.json')
            if os.path.exists(json_path):
                try:
                    os.remove(json_path)
                except Exception as e:
                    logger.error(f"Failed to delete JSON sidecar: {e}")
        
        return True
