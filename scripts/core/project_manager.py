import sqlite3
import os
import shutil
import uuid
import datetime
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from scripts.app_settings import PROJECTS_DB_PATH, SOURCE_DIR, GAME_ID_ALIASES

# Configure logger
logger = logging.getLogger(__name__)

from scripts.core.project_json_manager import ProjectJsonManager
# from scripts.services import kanban_service # Circular import if we import instance here? 
# project_manager is imported in services.py. 
# So we should probably import the instance inside methods OR import class and instantiated?
# Better: Import the service instance at the top of the file if possible, or inside methods if circular.
# services.py imports ProjectManager. So importing services here is Circular.
# Solution: Import the CLASS here, or inject it? 
# Or just import services inside the methods?
# Let's import inside methods for now to be safe, or import the module scripts.core.services.kanban_service
from scripts.core.services.kanban_service import KanbanService

@dataclass
class Project:
    project_id: str
    name: str
    game_id: str
    source_path: str
    target_path: str
    status: str  # 'active', 'archived', 'deleted'
    created_at: str
    notes: str = "" # Added notes field

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
    def __init__(self, file_service=None, project_repository=None, db_path: str = PROJECTS_DB_PATH):
        """
        Args:
            file_service: Injected FileService instance. 
            project_repository: Injected ProjectRepository instance.
        """
        self.db_path = db_path
        self.file_service = file_service
        self.repository = project_repository

        # Fallback injection logic
        if self.file_service:
            self.kanban_service = self.file_service.kanban_service
        else:
            from scripts.core.services.kanban_service import KanbanService
            self.kanban_service = KanbanService()
        
        if not self.repository:
            # Fallback for tests/legacy
            from scripts.core.repositories.project_repository import ProjectRepository
            self.repository = ProjectRepository(db_path)

    def create_project(self, name: str, folder_path: str, game_id: str, source_language: str) -> Dict[str, Any]:
        """
        Creates a new project.
        1. Moves folder to SOURCE_DIR if not already there.
        2. Scans for files.
        3. Creates DB records.
        4. Initializes JSON sidecar.
        """
        # Normalize game_id
        game_id = GAME_ID_ALIASES.get(game_id.lower(), game_id)
        
        logger.info(f"Creating project '{name}' from '{folder_path}' for game '{game_id}' (Source: {source_language})")

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

        project_id = str(uuid.uuid4())
        now = datetime.datetime.now().isoformat()
        
        from scripts.schemas.project import Project as PydanticProject # Renamed to avoid conflict with dataclass Project
        
        new_project = PydanticProject(
            project_id=project_id,
            name=name,
            game_id=game_id,
            source_path=final_source_path,
            source_language=source_language,
            status='active',
            created_at=now,
            last_modified=now
        )
        
        saved_project = self.repository.create_project(new_project)
        
        # Initialize JSON sidecar with empty translation_dirs
        # User will add translation directories via Manage Paths UI
        json_manager = ProjectJsonManager(final_source_path)
        json_manager.update_config({
            "translation_dirs": [],
            "source_language": source_language
        })

        # Scan files (Initial Scan)
        self.refresh_project_files(project_id)
        
        return saved_project.model_dump()

    def get_project_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves project details associated with a specific file ID."""
        project_data = self.repository.get_project_by_file_id(file_id)
        if project_data:
             # Fetch source_language from JSON if source_path exists in data
             # The repo returns p.*, so source_path is there.
             try:
                 source_path = project_data.get('source_path')
                 if source_path:
                    json_manager = ProjectJsonManager(source_path)
                    config = json_manager.get_config()
                    project_data['source_language'] = config.get('source_language', 'english')
             except Exception:
                 pass
             return project_data
        return None

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
        except Exception as e:
            logger.error(f"Failed to load translation_dirs from JSON: {e}")
            translation_dirs = []

        # Delegate to FileService
        if self.file_service:
            self.file_service.scan_and_sync_files(project_id, source_path, translation_dirs, project['name'])
        else:
            logger.error("FileService not initialized in ProjectManager!")


    # Removed _sync_kanban_with_files (Logic moved to KanbanService)

    def get_projects(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns a list of projects, ordered by last_modified."""
        projects = self.repository.list_projects(status)
        # Convert Pydantic models to dicts for API compatibility
        return [p.model_dump() for p in projects]

    def get_non_active_projects(self) -> List[Dict[str, Any]]:
        """Fetches all projects that are not 'active' (e.g., archived, deleted)."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE status != 'active' ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        p = self.repository.get_project(project_id)
        return p.model_dump() if p else None

    def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """Returns all files for a project."""
        files = self.repository.get_project_files(project_id)
        return [f.model_dump() for f in files]

    def update_project_status(self, project_id: str, status: str):
        self.repository.update_project_status(project_id, status)
        self.repository.add_activity_log(
            project_id=project_id,
            activity_type='status_change',
            description=f"Status updated to: {status}"
        )

    def update_project_notes(self, project_id: str, notes: str):
        """Updates the notes for a project."""
        self.repository.update_project_notes(project_id, notes)
        self.repository.add_activity_log(
            project_id=project_id,
            activity_type='note_added',
            description="Added a new note"
        )
        logger.info(f"Updated notes for project {project_id}")

    def save_project_kanban(self, project_id: str, kanban_data: Dict[str, Any]):
        """Saves kanban board, updates file statuses in DB, and logs activity."""
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # 1. Get Old Board for Diff (Read before save)
        try:
            old_board = self.kanban_service.get_board(project['source_path'])
            old_tasks = old_board.get("tasks", {})
        except Exception:
            old_tasks = {}

        # 2. Save NEW Board to disk
        self.kanban_service.save_board(project['source_path'], kanban_data)
        
        # 3. Process Diff and Log
        try:
            new_tasks = kanban_data.get("tasks", {})
            moved_tasks = []
            for tid, new_task in new_tasks.items():
                old_task = old_tasks.get(tid)
                if old_task and old_task.get('status') != new_task.get('status'):
                    moved_tasks.append(new_task)
            
            # Update DB for moved files
            for task in moved_tasks:
                if task.get('type') == 'file':
                    self.repository.update_file_status_by_id(task['id'], task['status'])
            
            # Log with De-duplication check
            if moved_tasks:
                first = moved_tasks[0]
                desc = f"Moved '{first.get('title')}' to {first.get('status')}"
                if len(moved_tasks) > 1:
                    desc += f" (and {len(moved_tasks)-1} others)"
                
                # Check for recent identical log (within last 3 logs) to prevent race-induced doubles
                recent_logs = self.repository.get_recent_logs(limit=3)
                is_dupe = any(l['project_id'] == project_id and l['type'] == 'file_update' and l['description'] == desc for l in recent_logs)
                
                if not is_dupe:
                    self.repository.add_activity_log(project_id, 'file_update', desc)
                else:
                    logger.info(f"Suppressed duplicate file_update log for {project_id}")
            else:
                # Layout update de-dupe
                recent_logs = self.repository.get_recent_logs(limit=5)
                is_dupe = any(l['project_id'] == project_id and l['type'] == 'kanban_update' for l in recent_logs)
                if not is_dupe:
                    self.repository.add_activity_log(project_id, 'kanban_update', "Updated Kanban board layout")
                
        except Exception as e:
            logger.error(f"Error during kanban diff/sync: {e}")

        # 4. Final Touch
        self.repository.touch_project(project_id)
        logger.info(f"Saved kanban and synchronized status for project {project_id}")

    def update_file_status(self, project_id: str, file_path: str, status: str):
        """Updates the status of a file in a project."""
        # Find file_id or update by path via repo if repo supports it
        # Current repo doesn't have update_file_status_by_path, but Manager had it.
        # Let's add it to repo or just use SQL here for one last time (not recommended).
        # Better: use repository.update_file_status_by_id if we have the ID.
        # For simplicity and isolation, I'll update the repo to handle this or use the safer path.
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE project_files
                SET status = ?
                WHERE project_id = ? AND file_path = ?
            ''', (status, project_id, file_path))
            conn.commit()
            
            # Log activity
            self.repository.add_activity_log(
                project_id=project_id,
                activity_type='file_update',
                description=f"File {os.path.basename(file_path)} status updated to {status}"
            )
            self.repository.touch_project(project_id) # Trigger last_modified
        finally:
            conn.close()

    def update_file_status_by_id(self, file_id: str, status: str):
        self.repository.update_file_status_by_id(file_id, status)

    def delete_project(self, project_id: str, delete_source_files: bool = False):
        try:
            project = self.get_project(project_id)
            if not project:
                return False

            # Remove config file from disk first if exists
            if 'source_path' in project and os.path.exists(project['source_path']):
                config_path = os.path.join(project['source_path'], '.remis_project.json')
                if os.path.exists(config_path):
                    try:
                        os.remove(config_path)
                    except Exception as e:
                        logger.error(f"Failed to delete JSON sidecar: {e}")
            
            # Delete from DB via Repository
            self.repository.delete_project(project_id)
            
            # Optional: Delete source folder
            if delete_source_files and 'source_path' in project and os.path.exists(project['source_path']):
                try:
                    shutil.rmtree(project['source_path'])
                    logger.info(f"Deleted source directory: {project['source_path']}")
                except Exception as e:
                    logger.error(f"Failed to delete source directory {project['source_path']}: {e}")

            return True
                
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            raise e

    def add_translation_path(self, project_id: str, translation_path: str):
        """
        Adds a translation directory to the project's configuration and refreshes files.
        """
        project = self.get_project(project_id)
        if not project:
            logger.error(f"Project {project_id} not found")
            return

        source_path = project['source_path']
        json_manager = ProjectJsonManager(source_path)
        config = json_manager.get_config()
        translation_dirs = config.get('translation_dirs', [])

        # Normalize path
        abs_path = os.path.abspath(translation_path)

        if abs_path not in translation_dirs:
            translation_dirs.append(abs_path)
            json_manager.update_config({"translation_dirs": translation_dirs})
            logger.info(f"Added translation path {abs_path} to project {project_id}")
            
            # Log activity
            self.repository.add_activity_log(
                project_id=project_id,
                activity_type='path_registered',
                description="Auto-registered translation output path"
            )

            # Refresh files to include new translation files
            self.refresh_project_files(project_id)
        else:
            logger.info(f"Translation path {abs_path} already exists for project {project_id}")

    def update_project_metadata(self, project_id: str, game_id: str, source_language: str):
        """
        Updates the project's metadata (game_id and source_language).
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Normalize game_id
        game_id = GAME_ID_ALIASES.get(game_id.lower(), game_id)

        # Update DB (game_id and source_language)
        # Note: repository.update_project_metadata updates both game_id and source_language
        self.repository.update_project_metadata(project_id, game_id, source_language)

        # Update JSON sidecar (source_language)
        try:
            json_manager = ProjectJsonManager(project['source_path'])
            json_manager.update_config({"source_language": source_language})
        except Exception as e:
            logger.error(f"Failed to update source_language in JSON for project {project_id}: {e}")
            # Non-fatal, but should be noted
        
        logger.info(f"Updated metadata for project {project_id}: game_id={game_id}, source_language={source_language}")
