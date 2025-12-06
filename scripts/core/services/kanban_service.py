import os
import logging
from typing import List, Dict, Any, Optional
from scripts.core.project_json_manager import ProjectJsonManager

logger = logging.getLogger(__name__)

class KanbanService:
    """
    Service to manage Kanban board state and logic.
    Strictly handles data manipulation (JSON Sidecar) and does NOT perform disk scanning.
    """

    def __init__(self):
        pass

    def get_board(self, source_path: str) -> Dict[str, Any]:
        """
        Retrieves the Kanban board data from the project's JSON sidecar.
        """
        try:
            json_manager = ProjectJsonManager(source_path)
            return json_manager.get_kanban_data()
        except Exception as e:
            logger.error(f"Failed to get kanban board for {source_path}: {e}")
            raise

    def save_board(self, source_path: str, kanban_data: Dict[str, Any]) -> None:
        """
        Saves the Kanban board data to the project's JSON sidecar.
        """
        try:
            json_manager = ProjectJsonManager(source_path)
            json_manager.save_kanban_data(kanban_data)
        except Exception as e:
            logger.error(f"Failed to save kanban board for {source_path}: {e}")
            raise

    def sync_files_to_board(self, source_path: str, files: List[Dict[str, Any]]) -> None:
        """
        Syncs a list of files (provided by an external scanner) to the Kanban board.
        
        Args:
            source_path: The root path of the project source (for ProjectJsonManager).
            files: A list of file dictionaries (from ProjectManager/DB). 
                   Must contain 'file_type', 'file_path', 'file_id', 'line_count'.
        """
        try:
            json_manager = ProjectJsonManager(source_path)
            kanban_data = json_manager.get_kanban_data()
            tasks = kanban_data.get("tasks", {})
            columns = kanban_data.get("columns", [])
            
            # Ensure 'todo' column exists
            if "todo" not in columns:
                columns.insert(0, "todo")

            # 1. Separate Source, Translation, and Metadata files
            source_files = [f for f in files if f.get('file_type') == 'source']
            translation_files = [f for f in files if f.get('file_type') == 'translation']
            metadata_files = [f for f in files if f.get('file_type') in ['metadata', 'config']]
            
            # 2. Process Source Files (Create Main Tasks)
            # Map valid source file paths (relative) to Task IDs for linking
            rel_path_to_task_id = {}
            source_file_count = 0

            for f in source_files:
                source_file_count += 1
                file_path = f['file_path']
                
                # Calculate relative path
                if file_path.startswith(source_path):
                    rel_path = os.path.relpath(file_path, source_path)
                else:
                    rel_path = os.path.basename(file_path)
                
                # Use file_id as Task ID
                task_id = f['file_id']
                rel_path_to_task_id[rel_path.lower()] = task_id  # Case-insensitive mapping attempt
                
                if task_id not in tasks:
                    # Create new task
                    tasks[task_id] = {
                        "id": task_id,
                        "type": "file",
                        "title": os.path.basename(file_path),
                        "filePath": file_path,
                        "status": "todo",
                        "comments": "",
                        "priority": "medium",
                        "meta": {
                            "source_lines": f.get('line_count', 0),
                            "file_type": "source",
                            "translation_status": {},
                            "rel_path": rel_path
                        }
                    }
                else:
                    # Update existing task meta
                    if "meta" not in tasks[task_id]: tasks[task_id]["meta"] = {}
                    tasks[task_id]["meta"]["source_lines"] = f.get('line_count', 0)
                    tasks[task_id]["meta"]["rel_path"] = rel_path
                    tasks[task_id]["meta"]["file_type"] = "source" # Ensure file_type is updated
                    tasks[task_id]["title"] = os.path.basename(file_path) # Update title just in case

            # 3. Process Translation Files (Link to Source)
            import re
            for tf in translation_files:
                t_path = tf['file_path']
                t_name = os.path.basename(t_path)
                
                # Identify Language
                # Assume standard naming: ..._l_{lang}.yml
                lang_match = re.search(r"_l_(\w+)\.yml$", t_name, re.IGNORECASE)
                if not lang_match:
                    continue # Skip if not following naming convention
                
                lang = lang_match.group(1).lower()
                
                # Attempt to find parent source file
                # Strategy: Replace _l_{lang}.yml with _l_{source_lang}.yml ?? 
                # Problem: We don't strictly know source_lang here easily without PROJECT info passed in.
                # However, usually the keys match. 
                # Let's try to match by removing the lang suffix and looking for a source file 
                # that has a similar prefix? 
                # Better: Iterate source_files and see if t_path matches s_path pattern?
                
                # Let's assume the standard Paradox structure:
                # Source: /localization/simp_chinese/foo_l_simp_chinese.yml
                # Target: /localization/english/foo_l_english.yml
                
                # Heuristic: Replace "english" folder with "simp_chinese"?
                # But we don't know the exact source language folder name here.
                
                # Reverse lookup:
                # Get the "stem" of the translation file (foo)
                t_stem = t_name.replace(f"_l_{lang}.yml", "") # simplistic
                
                # Look for a source task whose file name starts with this stem?
                # This is O(N*M) but N is small.
                parent_task_id = None
                
                # Improved Heuristic: Check if there is a task where the filename matches except the lang part.
                for s_rel_path, tid in rel_path_to_task_id.items():
                    # s_rel_path: localization/simp_chinese/foo_l_simp_chinese.yml
                    # t_path:     localization/english/foo_l_english.yml
                    
                    # Just checking basename match is risky if multiple files have same name in different folders.
                    # But usually acceptable.
                    s_name = os.path.basename(s_rel_path)
                    
                    # Try to match patterns
                    # If we strip _l_... from both?
                    s_base = re.sub(r"_l_(\w+)\.yml$", "", s_name, flags=re.IGNORECASE)
                    
                    if s_base.lower() == t_stem.lower():
                        parent_task_id = tid
                        break
                
                if parent_task_id:
                     # Create a Linked Task (Child Task)
                     # Instead of updating meta, we create a new task that refers to the parent.
                     # But Kanban usually is flat.
                     # We create a new task for the translation file itself.
                     
                     task_id = tf['file_id']
                     
                     if task_id not in tasks:
                         tasks[task_id] = {
                             "id": task_id,
                             "type": "file",
                             "title": t_name,
                             "filePath": t_path,
                             "status": "todo", # Or inherit from DB status if available?
                             "comments": "",
                             "priority": "medium",
                             "meta": {
                                 "lines": tf.get('line_count', 0),
                                 "file_type": "translation",
                                 "lang": lang,
                                 "parent_task_id": parent_task_id, # Link back to source
                                 "rel_path": os.path.relpath(t_path, source_path) if t_path.startswith(source_path) else t_name
                             }
                         }
                     else:
                        # Update existing
                        if "meta" not in tasks[task_id]: tasks[task_id]["meta"] = {}
                        tasks[task_id]["meta"]["lines"] = tf.get('line_count', 0)
                        tasks[task_id]["meta"]["parent_task_id"] = parent_task_id
                        tasks[task_id]["meta"]["file_type"] = "translation"
                        tasks[task_id]["meta"]["lang"] = lang
                        
                     # Note: we do NOT remove it. It stands alone.
                else:
                    # Orphan translation file, still create task
                    task_id = tf['file_id']
                    if task_id not in tasks:
                         tasks[task_id] = {
                             "id": task_id,
                             "type": "file",
                             "title": t_name,
                             "filePath": t_path,
                             "status": "todo",
                             "comments": "Orphan translation file",
                             "priority": "low",
                             "meta": {
                                 "lines": tf.get('line_count', 0),
                                 "file_type": "translation",
                                 "lang": lang,
                                 "orphan": True
                             }
                         }

            # 4. Process Metadata Files
            for mf in metadata_files:
                task_id = mf['file_id']
                if task_id not in tasks:
                    tasks[task_id] = {
                        "id": task_id,
                        "type": "file",
                        "title": os.path.basename(mf['file_path']),
                        "filePath": mf['file_path'],
                        "status": "todo",
                        "comments": "Configuration/Metadata File",
                        "priority": "low",
                        "meta": {
                             "lines": mf.get('line_count', 0),
                             "file_type": mf.get('file_type'),
                             "rel_path": os.path.relpath(mf['file_path'], source_path) if mf['file_path'].startswith(source_path) else os.path.basename(mf['file_path'])
                        }
                    }
                else:
                    # Update meta
                    if "meta" not in tasks[task_id]: tasks[task_id]["meta"] = {}
                    tasks[task_id]["meta"]["file_type"] = mf.get('file_type')

            logger.info(f"KanbanService: Synced {source_file_count} source files to board.")
            
            json_manager.save_kanban_data({
                "columns": columns,
                "tasks": tasks,
                "column_order": kanban_data.get("column_order", columns)
            })
            
        except Exception as e:
            logger.error(f"Failed to sync files to kanban: {e}")
            # Don't raise, just log error to avoid crashing the whole refresh process?
            # Or raise to let upper layer know? 
            # In PM code it was implicit. Let's log and re-raise.
            raise
