import os
import sys
import uvicorn
import uuid
import shutil
import zipfile
import logging
import json
import re
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form, Query
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv, set_key, find_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import using absolute imports from project root
from scripts.app_settings import GAME_PROFILES, LANGUAGES, API_PROVIDERS, SOURCE_DIR, DEST_DIR, MODS_CACHE_DB_PATH
from scripts.workflows import initial_translate
from scripts.utils import logger, i18n
from scripts.core import workshop_formatter
from scripts.core.glossary_manager import GlossaryManager
from scripts.core.project_manager import ProjectManager
from scripts.core.project_json_manager import ProjectJsonManager
from scripts.core.archive_manager import ArchiveManager

# Setup logger
logger.setup_logger()
i18n.load_language() # Load default language

# Initialize Managers
glossary_manager = GlossaryManager()
project_manager = ProjectManager()
archive_manager = ArchiveManager() # Needs to be initialized

# In-memory storage for task status.
# In a real production app, this should be replaced with a more robust solution like Redis.
tasks: Dict[str, Dict] = {}


def run_translation_workflow(task_id: str, mod_name: str, game_profile_id: str, source_lang_code: str, target_lang_codes: List[str], api_provider: str, mod_context: str):
    """
    A wrapper for the core translation logic to be run in the background.
    """
    # Initialize i18n for the background task
    i18n.load_language('en_US')

    tasks[task_id]["status"] = "processing"
    tasks[task_id]["log"].append("背景翻译任务开始...")

    try:
        # 1. Retrieve full config objects from IDs/codes
        game_profile = GAME_PROFILES.get(game_profile_id)
        source_lang = next((lang for lang in LANGUAGES.values() if lang["code"] == source_lang_code), None)
        target_languages = [lang for lang in LANGUAGES.values() if lang["code"] in target_lang_codes]

        if not all([game_profile, source_lang, target_languages]):
            raise ValueError("无效的游戏配置、源语言或目标语言。")

        # 2. Call the core translation function
        initial_translate.run(
            mod_name=mod_name,
            game_profile=game_profile,
            source_lang=source_lang,
            target_languages=target_languages,
            selected_provider=api_provider,
            mod_context=mod_context,
        )

        # 3. Once done, update status and prepare result
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["log"].append("翻译流程成功完成！")

        # Prepare the result for download
        output_folder_name = f"{target_languages[0]['folder_prefix']}{mod_name}"
        if len(target_languages) > 1:
            output_folder_name = f"Multilanguage-{mod_name}"

        result_dir = os.path.join(DEST_DIR, output_folder_name)

        # Hyper-detailed logging for debugging
        logging.info(f"--- ZIPPING LOGS for Task {task_id} ---")
        logging.info(f"Final check before zipping. Target directory: {result_dir}")
        logging.info(f"Does it exist? {os.path.exists(result_dir)}")
        logging.info(f"Is it a directory? {os.path.isdir(result_dir)}")
        if os.path.exists(result_dir) and os.path.isdir(result_dir):
            logging.info(f"Contents: {os.listdir(result_dir)}")
        logging.info(f"------------------------------------")

        zip_path = shutil.make_archive(result_dir, 'zip', result_dir)
        tasks[task_id]["result_path"] = zip_path

    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        error_message = f"工作流执行失败 (Workflow execution failed): {e}\n{tb_str}"
        logging.error(f"任务 {task_id} 失败: {error_message}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["log"].append(error_message)
        # 确保失败的任务没有可下载的结果路径
        if "result_path" in tasks[task_id]:
            del tasks[task_id]["result_path"]


app = FastAPI(
    title="P社Mod本地化工厂 API",
    description="为P社Mod本地化工厂提供Web UI的后端API。",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- New Pydantic Models for Project/Proofreading ---
class CreateProjectRequest(BaseModel):
    name: str
    folder_path: str
    game_id: str

class SaveProofreadingRequest(BaseModel):
    project_id: str
    file_id: str
    entries: List[Dict[str, Any]]
    content: str = "" # Legacy support

class InitialTranslationRequest(BaseModel):
    project_id: str
    target_language: str = "zh"
    api_provider: str = "gemini"
    model: str = "gemini-pro"

# --- New Project Endpoints ---
@app.get("/api/projects")
def list_projects():
    """Returns a list of all projects."""
    return project_manager.get_projects()

@app.post("/api/project/create")
def create_project(request: CreateProjectRequest):
    """Creates a new project."""
    try:
        if not os.path.exists(request.folder_path):
             raise HTTPException(status_code=404, detail=f"Path not found: {request.folder_path}")

        project = project_manager.create_project(request.name, request.folder_path, request.game_id)
        return {"status": "success", "project": project}
    except Exception as e:
        logging.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/project/{project_id}/files")
def list_project_files(project_id: str):
    """Lists files for a given project."""
    return project_manager.get_project_files(project_id)

@app.delete("/api/project/{project_id}")
def delete_project(project_id: str, delete_files: bool = False):
    """Deletes a project. Set delete_files=true to also delete source directory."""
    try:
        success = project_manager.delete_project(project_id, delete_source_files=delete_files)
        if success:
            return {"status": "success", "message": "Project deleted"}
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logging.error(f"Error deleting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate/start")
def start_translation_project(request: InitialTranslationRequest, background_tasks: BackgroundTasks):
    """
    Starts the initial translation workflow for a project.
    """
    project = project_manager.get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Map request to workflow args
    # We need to fetch game profile etc.
    # This is a simplified integration.

    # TODO: Full integration with run_initial_translation using project context

    return {"status": "started", "message": f"Translation started for project {project['name']}"}

@app.get("/api/proofread/{project_id}/{file_id}")
def get_proofread_data(project_id: str, file_id: str):
    files = project_manager.get_project_files(project_id)
    target_file = next((f for f in files if f['file_id'] == file_id), None)

    if not target_file:
        raise HTTPException(status_code=404, detail="File not found in project")

    file_path = target_file['file_path']
    project = project_manager.get_project(project_id)
    mod_name = project['name']

    entries = archive_manager.get_entries(mod_name, file_path)

    return {
        "file_id": file_id,
        "file_path": file_path,
        "mod_name": mod_name,
        "entries": entries
    }

# --- Kanban & Config Endpoints ---

@app.get("/api/project/{project_id}/kanban")
def get_project_kanban(project_id: str):
    """Gets the Kanban board state from the JSON sidecar."""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        return json_manager.get_kanban_data()
    except Exception as e:
        logging.error(f"Error loading Kanban data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/project/{project_id}/kanban")
def save_project_kanban(project_id: str, kanban_data: Dict[str, Any]):
    """Saves the Kanban board state to the JSON sidecar."""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        json_manager.save_kanban_data(kanban_data)
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error saving Kanban data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/project/{project_id}/refresh")
def refresh_project_files(project_id: str):
    """Rescans the project files and updates the DB and Kanban."""
    try:
        project_manager.refresh_project_files(project_id)
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error refreshing project files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/project/{project_id}/config")
def get_project_config(project_id: str):
    """Gets the project configuration (e.g. translation dirs)."""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        config = json_manager.get_config()
        # Also return source_path for reference
        config['source_path'] = project['source_path']
        return config
    except Exception as e:
        logging.error(f"Error loading project config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class UpdateConfigRequest(BaseModel):
    action: str # 'add_dir', 'remove_dir'
    path: str

@app.post("/api/project/{project_id}/config")
def update_project_config(project_id: str, request: UpdateConfigRequest):
    """Updates project configuration."""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        
        if request.action == 'add_dir':
            if not os.path.exists(request.path):
                 raise HTTPException(status_code=404, detail="Directory not found")
            json_manager.add_translation_dir(request.path)
        elif request.action == 'remove_dir':
            json_manager.remove_translation_dir(request.path)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
        # Refresh files after config change
        project_manager.refresh_project_files(project_id)
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating project config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Existing Endpoints (Restored) ---

@app.post("/api/proofread/save")
def save_proofreading_db(request: SaveProofreadingRequest):
    try:
        project = project_manager.get_project(request.project_id)
        files = project_manager.get_project_files(request.project_id)
        target_file = next((f for f in files if f['file_id'] == request.file_id), None)

        if not project or not target_file:
            raise HTTPException(status_code=404, detail="Project or File not found")

        archive_manager.update_translations(project['name'], target_file['file_path'], request.entries)

        # Write to disk
        output_path = os.path.join(project['target_path'], target_file['file_path'])
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(u'\uFEFF')
            f.write("l_simp_chinese:\n")
            for entry in request.entries:
                val = entry.get('translation', '')
                val = val.replace('"', '\\"')
                f.write(f' {entry["key"]}:0 "{val}"\n')

        project_manager.update_file_status_by_id(request.file_id, "done")

        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error saving proofreading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Existing Endpoints (Restored) ---

@app.post("/api/translate")
async def start_translation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    game_profile_id: str = Form(...),
    source_lang_code: str = Form(...),
    target_lang_codes: str = Form(...), # Received as a comma-separated string
    api_provider: str = Form(...),
    mod_context: str = Form("")
):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "log": []}

    # Save and extract the uploaded file
    try:
        mod_name = file.filename.replace(".zip", "")

        # Clean up old source and dest dirs for this mod
        source_path = os.path.join(SOURCE_DIR, mod_name)
        if os.path.exists(source_path):
            shutil.rmtree(source_path)

        temp_zip_path = os.path.join(SOURCE_DIR, file.filename)
        with open(temp_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(source_path)

        # Smartly handle "double folder" zip files where all content is inside a single sub-directory.
        extracted_items = os.listdir(source_path)
        if len(extracted_items) == 1:
            potential_inner_folder = os.path.join(source_path, extracted_items[0])
            if os.path.isdir(potential_inner_folder):
                logging.info(f"Detected single sub-directory '{extracted_items[0]}', promoting its contents.")
                # Move all contents from the sub-directory to the parent (source_path)
                for item_name in os.listdir(potential_inner_folder):
                    src = os.path.join(potential_inner_folder, item_name)
                    dst = os.path.join(source_path, item_name)
                    try:
                        # Remove destination if it already exists
                        if os.path.exists(dst):
                            if os.path.isdir(dst):
                                shutil.rmtree(dst)
                            else:
                                os.remove(dst)
                        shutil.move(src, dst)
                    except Exception as move_error:
                        logging.warning(f"Failed to move '{item_name}': {move_error}, attempting direct copy")
                        if os.path.isdir(src):
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                        else:
                            shutil.copy2(src, dst)
                # Remove the now-empty sub-directory
                try:
                    os.rmdir(potential_inner_folder)
                except Exception as rmdir_error:
                    logging.warning(f"Failed to remove sub-directory: {rmdir_error}")

        os.remove(temp_zip_path) # Clean up the zip file

        tasks[task_id]["status"] = "starting"
        tasks[task_id]["log"].append(f"Mod '{mod_name}' 已上传并解压。")
    except Exception as e:
        logging.exception("File upload/unzip failed")
        raise HTTPException(status_code=500, detail=f"文件处理失败: {e}")

    # Add the long-running task to the background
    target_codes = target_lang_codes.split(',')
    background_tasks.add_task(
        run_translation_workflow,
        task_id,
        mod_name,
        game_profile_id,
        source_lang_code,
        target_codes,
        api_provider,
        mod_context
    )

    return {"task_id": task_id, "message": "翻译任务已开始"}

class TranslationRequestV2(BaseModel):
    project_path: str
    game_profile_id: str
    source_lang_code: str
    target_lang_codes: List[str]
    api_provider: str
    mod_context: Optional[str] = ""
    selected_glossary_ids: Optional[List[int]] = []
    model_name: Optional[str] = None
    use_main_glossary: bool = True
    clean_source: bool = False
    is_existing_source: bool = False

@app.get("/api/source-mods")
def get_source_mods():
    """
    Returns a list of directories in the SOURCE_DIR.
    """
    if not os.path.exists(SOURCE_DIR):
        return []

    mods = []
    for item in os.listdir(SOURCE_DIR):
        item_path = os.path.join(SOURCE_DIR, item)
        if os.path.isdir(item_path):
            mods.append({
                "name": item,
                "path": item_path,
                "mtime": os.path.getmtime(item_path)
            })

    # Sort by modification time (newest first)
    mods.sort(key=lambda x: x["mtime"], reverse=True)
    return mods

@app.post("/api/translate_v2")
async def start_translation_v2(
    background_tasks: BackgroundTasks,
    payload: TranslationRequestV2
):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "log": []}

    # Validate project path
    if not os.path.exists(payload.project_path) or not os.path.isdir(payload.project_path):
        raise HTTPException(status_code=400, detail="Invalid project path.")

    mod_name = os.path.basename(payload.project_path)
    source_path = os.path.join(SOURCE_DIR, mod_name)

    try:
        if payload.is_existing_source:
            # Case: Using an existing mod in SOURCE_DIR
            # Verify that the payload path matches the expected source path
            # Normalize paths to compare safely
            if os.path.normpath(payload.project_path) != os.path.normpath(source_path):
                # If they don't match, it might be an "existing" mod but from a different location?
                # No, "existing source" implies it is ALREADY in SOURCE_DIR.
                # But let's be flexible: if it claims to be existing, we assume it's in place.
                # However, for safety, if it's NOT in SOURCE_DIR, we should probably copy it?
                # Let's trust the flag but log a warning if paths differ significantly.
                pass

            tasks[task_id]["status"] = "starting"
            tasks[task_id]["log"].append(f"使用现有的源文件: '{mod_name}'")

        else:
            # Case: Importing a new folder (Copy logic)
            if os.path.exists(source_path):
                if os.path.isdir(source_path):
                    shutil.rmtree(source_path)
                else:
                    os.remove(source_path)

            # Copy from local path to SOURCE_DIR
            shutil.copytree(payload.project_path, source_path)
            tasks[task_id]["status"] = "starting"
            tasks[task_id]["log"].append(f"Mod '{mod_name}' 已从本地路径导入并复制。")

        # --- Clean Source Logic ---
        if payload.clean_source:
            game_profile = GAME_PROFILES.get(payload.game_profile_id)
            if game_profile:
                protected = game_profile.get("protected_items", set())
                # Add standard protected items if not present
                protected.add("customizable_localization")

                tasks[task_id]["log"].append("正在清理源文件 (Clean Source)...")
                for item in os.listdir(source_path):
                    if item not in protected:
                        item_path = os.path.join(source_path, item)
                        try:
                            if os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                            else:
                                os.remove(item_path)
                        except Exception as e:
                            logging.warning(f"Failed to delete {item}: {e}")
                tasks[task_id]["log"].append("源文件清理完成。")


    except Exception as e:
        logging.exception("File processing failed")
        raise HTTPException(status_code=500, detail=f"文件处理失败: {e}")

    background_tasks.add_task(
        run_translation_workflow_v2,
        task_id,
        mod_name,
        payload.game_profile_id,
        payload.source_lang_code,
        payload.target_lang_codes,
        payload.api_provider,
        payload.mod_context,
        payload.selected_glossary_ids,
        payload.model_name,
        payload.use_main_glossary
    )

    return {"task_id": task_id, "message": "翻译任务已开始"}

def run_translation_workflow_v2(
    task_id: str,
    mod_name: str,
    game_profile_id: str,
    source_lang_code: str,
    target_lang_codes: List[str],
    api_provider: str,
    mod_context: str,
    selected_glossary_ids: List[int],
    model_name: Optional[str],
    use_main_glossary: bool
):
    """
    V2 wrapper for the core translation logic.
    """
    # Initialize i18n for the background task
    i18n.load_language('en_US')

    tasks[task_id]["status"] = "processing"
    tasks[task_id]["log"].append("背景翻译任务开始 (V2)...")

    try:
        # 1. Retrieve full config objects from IDs/codes
        game_profile = GAME_PROFILES.get(game_profile_id)
        source_lang = next((lang for lang in LANGUAGES.values() if lang["code"] == source_lang_code), None)
        target_languages = [lang for lang in LANGUAGES.values() if lang["code"] in target_lang_codes]

        if not all([game_profile, source_lang, target_languages]):
            raise ValueError("无效的游戏配置、源语言或目标语言。")

        # --- Glossary Logic: Merge Main Glossary if requested ---
        final_glossary_ids = list(selected_glossary_ids) if selected_glossary_ids else []

        if use_main_glossary:
            from scripts.core.glossary_manager import glossary_manager
            # We need to find the main glossary ID for this game
            # Since glossary_manager doesn't have a direct 'get_main_id' method exposed efficiently without querying all,
            # we can reuse get_available_glossaries or add a helper.
            # For now, let's use get_available_glossaries as it's cached/fast enough usually.
            available = glossary_manager.get_available_glossaries(game_profile["id"])
            main_glossary = next((g for g in available if g.get('is_main')), None)
            if main_glossary:
                main_id = main_glossary['glossary_id']
                if main_id not in final_glossary_ids:
                    final_glossary_ids.append(main_id)
                    tasks[task_id]["log"].append(f"已自动包含主词典: {main_glossary['name']}")
            else:
                 tasks[task_id]["log"].append("未找到该游戏的主词典。")

        # 2. Call the core translation function
        initial_translate.run(
            mod_name=mod_name,
            game_profile=game_profile,
            source_lang=source_lang,
            target_languages=target_languages,
            selected_provider=api_provider,
            mod_context=mod_context,
            selected_glossary_ids=final_glossary_ids,
            model_name=model_name,
            use_glossary=True # Always true if we are passing specific IDs
        )

        # 3. Once done, update status and prepare result
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["log"].append("翻译流程成功完成！")

        # Prepare the result for download
        output_folder_name = f"{target_languages[0]['folder_prefix']}{mod_name}"
        if len(target_languages) > 1:
            output_folder_name = f"Multilanguage-{mod_name}"

        result_dir = os.path.join(DEST_DIR, output_folder_name)
        zip_path = shutil.make_archive(result_dir, 'zip', result_dir)
        tasks[task_id]["result_path"] = zip_path

    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        error_message = f"工作流执行失败: {e}\n{tb_str}"
        logging.error(f"任务 {task_id} 失败: {error_message}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["log"].append(error_message)

@app.get("/api/glossaries/{game_id}")
def get_game_glossaries(game_id: str):
    from scripts.core.glossary_manager import glossary_manager
    return glossary_manager.get_available_glossaries(game_id)

@app.get("/api/status/{task_id}")
def get_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return task

@app.get("/api/result/{task_id}")
def get_result(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    result_path = task.get("result_path")
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="结果文件未找到")

    return FileResponse(result_path, media_type='application/zip', filename=os.path.basename(result_path))


@app.get("/api/config")
def get_config():
    """
    Provide frontend with necessary configuration data.
    """
    return {
        "game_profiles": GAME_PROFILES,
        "languages": LANGUAGES,
        "api_providers": list(API_PROVIDERS.keys()),
        "source_dir": SOURCE_DIR # Shared config needs this
    }

@app.get("/api/docs-languages")
def get_docs_languages():
    """
    Scans the root 'docs' directory and returns a list of available languages (directories).
    """
    docs_dir = os.path.join(project_root, 'docs')
    languages = []
    if not os.path.isdir(docs_dir):
        logging.warning("The 'docs' directory does not exist.")
        return []

    for item in os.listdir(docs_dir):
        if os.path.isdir(os.path.join(docs_dir, item)):
            languages.append(item)
    return sorted(languages)

def _scan_docs_recursive(directory, parent_key=''):
    """
    Recursively scans a directory to build a tree structure for Ant Design.
    """
    nodes = []
    if not os.path.isdir(directory):
        return []

    for item in sorted(os.listdir(directory)):
        path = os.path.join(directory, item)
        key = os.path.join(parent_key, item)

        if os.path.isdir(path):
            children = _scan_docs_recursive(path, key)
            if children: # Only add directory if it's not empty
                nodes.append({
                    "title": item,
                    "key": key,
                    "children": children,
                })
        elif item.endswith(".md"):
            nodes.append({
                "title": item.replace(".md", ""),
                "key": key,
                "isLeaf": True,
            })
    return nodes

@app.get("/api/docs-tree")
def get_docs_tree():
    """
    Scans the root 'docs' directory and returns a language-keyed dictionary
    of recursively scanned file trees for the Ant Design Tree component.
    """
    docs_dir = os.path.join(project_root, 'docs')
    tree_data = {}

    if not os.path.isdir(docs_dir):
        logging.warning("The 'docs' directory does not exist.")
        return {}

    for lang in os.listdir(docs_dir):
        lang_path = os.path.join(docs_dir, lang)
        if os.path.isdir(lang_path):
            # Start scanning from the language directory itself
            tree_data[lang] = _scan_docs_recursive(lang_path, lang)

    return tree_data

# --- API Key Management ---

class ApiKeyUpdate(BaseModel):
    provider_id: str
    api_key: str

@app.get("/api/api-keys")
def get_api_keys():
    """
    Returns a list of API providers with their current key status (masked).
    """
    providers_status = []

    for provider_id, config in API_PROVIDERS.items():
        env_var_name = config.get("api_key_env")
        masked_key = None
        has_key = False

        if env_var_name:
            current_key = os.environ.get(env_var_name)
            if current_key:
                has_key = True
                if len(current_key) > 8:
                    masked_key = f"{current_key[:4]}****{current_key[-4:]}"
                else:
                    masked_key = "****" # Too short to show parts

        providers_status.append({
            "id": provider_id,
            "name": provider_id.replace("_", " ").title(), # Simple formatting
            "description": config.get("description", ""),
            "env_var": env_var_name,
            "has_key": has_key,
            "masked_key": masked_key,
            "is_keyless": env_var_name is None # e.g. gemini_cli, ollama might not need a key in the same way, or handled differently
        })

    return providers_status

@app.post("/api/api-keys")
def update_api_key(payload: ApiKeyUpdate):
    """
    Updates the API key for a specific provider in the .env file and current environment.
    """
    provider_id = payload.provider_id
    new_key = payload.api_key

    if provider_id not in API_PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")

    config = API_PROVIDERS[provider_id]
    env_var_name = config.get("api_key_env")

    if not env_var_name:
         raise HTTPException(status_code=400, detail="This provider does not require an API key.")

    # 1. Update current process environment
    os.environ[env_var_name] = new_key

    # 2. Update .env file
    dotenv_file = find_dotenv()
    if not dotenv_file:
        # If no .env file found, create one in project root
        dotenv_file = os.path.join(project_root, ".env")

    try:
        set_key(dotenv_file, env_var_name, new_key)
        return {"status": "success", "message": f"Key for {provider_id} updated successfully."}
    except Exception as e:
        logging.error(f"Failed to write to .env file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save key to .env file: {e}")

#<-- Glossar-API-Endpunkte -->
GLOSSARY_DIR = os.path.join(project_root, "data", "glossary")
DOCS_DIR = os.path.join(project_root, "docs")

# --- Pydantic Models for Glossary ---
# Model for data COMING FROM the frontend for updates
class GlossaryEntryIn(BaseModel):
    id: str
    source: str
    translations: Dict[str, str]
    notes: Optional[str] = ""
    variants: Optional[Dict[str, List[str]]] = {}
    abbreviations: Optional[Dict[str, str]] = {}
    # metadata can be flexible, so we accept a dict
    metadata: Optional[Dict] = {}

class SearchGlossaryRequest(BaseModel):
    scope: str = Field(..., description="Search scope: 'file', 'game', or 'all'")
    query: str = Field(..., description="Search query string")
    game_id: Optional[str] = None
    file_name: Optional[str] = None
    page: int = 1
    pageSize: int = 25

class CreateGlossaryFileRequest(BaseModel):
    game_id: str
    file_name: str


@app.post("/api/glossary/file")
def create_glossary_file(payload: CreateGlossaryFileRequest):
    """
    Creates a new, empty glossary JSON file for a given game.
    """
    game_id = payload.game_id
    file_name = payload.file_name

    if not file_name.endswith(".json"):
        raise HTTPException(status_code=400, detail="File name must end with .json")

    if ".." in file_name or "/" in file_name or "\\" in file_name:
        raise HTTPException(status_code=400, detail="Invalid characters in file name.")

    game_path = os.path.join(GLOSSARY_DIR, game_id)
    if not os.path.isdir(game_path):
        raise HTTPException(status_code=404, detail=f"Game '{game_id}' not found.")

    file_path = os.path.join(game_path, file_name)
    if os.path.exists(file_path):
        raise HTTPException(status_code=409, detail=f"File '{file_name}' already exists in game '{game_id}'.")

    try:
        default_content = {
            "metadata": {
                "description": f"New glossary file: {file_name}",
                "last_updated": ""
            },
            "entries": []
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, ensure_ascii=False, indent=2)

        return {"status": "success", "message": f"Successfully created '{file_name}' for game '{game_id}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create glossary file: {e}")


@app.get("/api/glossary/tree")
def get_glossary_tree():
    """
    Scans the data/glossary directory and returns a tree structure
    for the Ant Design Tree component.
    """
    tree_data = []
    for game_id in os.listdir(GLOSSARY_DIR):
        game_path = os.path.join(GLOSSARY_DIR, game_id)
        if os.path.isdir(game_path):
            game_node = {
                "title": game_id,
                "key": game_id,
                "children": []
            }
            for filename in os.listdir(game_path):
                if filename.endswith(".json"):
                    game_node["children"].append({
                        "title": filename,
                        "key": f"{game_id}|{filename}", # Use a separator for easy splitting on the frontend
                        "isLeaf": True
                    })
            # Only add games that have at least one JSON file
            if game_node["children"]:
                tree_data.append(game_node)
    return tree_data

def _transform_storage_to_frontend_format(entry: Dict, game_id: str = None, file_name: str = None) -> Dict:
    new_entry = entry.copy()
    new_entry['source'] = new_entry.get('translations', {}).get('en', '')

    variants_dict = new_entry.get('variants', {})
    if isinstance(variants_dict, dict):
        new_entry['variants'] = variants_dict.get('en', [])
    else:
        new_entry['variants'] = variants_dict if isinstance(variants_dict, list) else []

    if 'translations' not in new_entry or not isinstance(new_entry['translations'], dict):
        new_entry['translations'] = {}

    new_entry['notes'] = new_entry.get('metadata', {}).get('remarks', '')
    new_entry['variants'] = entry.get('variants', {})
    new_entry['abbreviations'] = entry.get('abbreviations', {})

    if game_id:
        new_entry['game_id'] = game_id
    if file_name:
        new_entry['file_name'] = file_name

    return new_entry

@app.get("/api/glossary/content")
def get_glossary_content(
    game_id: str,
    file_name: str,
    page: int = Query(1, alias="page"),
    pageSize: int = Query(25, alias="pageSize")
):
    """
    Reads, sanitizes, and returns a paginated list of entries from a specific glossary file.
    """
    file_path = os.path.join(GLOSSARY_DIR, game_id, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Glossary file not found.")
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        transformed_entries = []
        raw_entries = data.get("entries", [])
        for entry in raw_entries:
            transformed_entries.append(_transform_storage_to_frontend_format(entry, game_id, file_name))

        # --- Pagination Logic ---
        total_count = len(transformed_entries)
        start_index = (page - 1) * pageSize
        end_index = start_index + pageSize
        paginated_entries = transformed_entries[start_index:end_index]

        return {
            "entries": paginated_entries,
            "totalCount": total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read or parse glossary file: {e}")

@app.post("/api/glossary/search")
def search_glossary(payload: SearchGlossaryRequest):
    """
    Searches across glossary files based on the provided scope.
    """
    results = []
    query_lower = payload.query.lower()

    # Determine which files to search
    files_to_search = []

    if payload.scope == 'file':
        if not payload.game_id or not payload.file_name:
            raise HTTPException(status_code=400, detail="game_id and file_name are required for file scope search.")
        files_to_search.append((payload.game_id, payload.file_name))

    elif payload.scope == 'game':
        if not payload.game_id:
            raise HTTPException(status_code=400, detail="game_id is required for game scope search.")
        game_path = os.path.join(GLOSSARY_DIR, payload.game_id)
        if os.path.isdir(game_path):
            for f in os.listdir(game_path):
                if f.endswith(".json"):
                    files_to_search.append((payload.game_id, f))

    elif payload.scope == 'all':
        if os.path.isdir(GLOSSARY_DIR):
            for g_id in os.listdir(GLOSSARY_DIR):
                game_path = os.path.join(GLOSSARY_DIR, g_id)
                if os.path.isdir(game_path):
                    for f in os.listdir(game_path):
                        if f.endswith(".json"):
                            files_to_search.append((g_id, f))

    # Perform search
    for g_id, f_name in files_to_search:
        file_path = os.path.join(GLOSSARY_DIR, g_id, f_name)
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                entries = data.get("entries", [])
                for entry in entries:
                    match = False
                    translations = entry.get("translations", {})
                    for text in translations.values():
                        if query_lower in text.lower():
                            match = True
                            break

                    if not match:
                        remarks = entry.get("metadata", {}).get("remarks", "")
                        if query_lower in remarks.lower():
                            match = True

                    if match:
                        results.append(_transform_storage_to_frontend_format(entry, g_id, f_name))

        except Exception as e:
            logging.error(f"Error reading file {file_path} during search: {e}")
            continue

    # Pagination
    total_count = len(results)
    start_index = (payload.page - 1) * payload.pageSize
    end_index = start_index + payload.pageSize
    paginated_results = results[start_index:end_index]

    return {
        "entries": paginated_results,
        "totalCount": total_count
    }


class GlossaryEntryCreate(BaseModel):
    source: str
    translations: Dict[str, str]
    notes: Optional[str] = ""
    variants: Optional[Dict[str, List[str]]] = {}
    abbreviations: Optional[Dict[str, str]] = {}
    metadata: Optional[Dict] = {}

def _read_glossary_file(file_path: str) -> Dict:
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Glossary file not found.")
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read or parse glossary file: {e}")

def _write_glossary_file(file_path: str, data: Dict):
    from datetime import datetime
    try:
        data["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Failed to write glossary file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to write glossary file: {e}")

def _transform_entry_to_storage_format(entry: Dict) -> Dict:
    entry['translations'] = entry.get('translations', {})
    entry['translations']['en'] = entry.get('source', '')
    if 'variants' not in entry: entry['variants'] = {}
    if 'abbreviations' not in entry: entry['abbreviations'] = {}
    if 'source' in entry: del entry['source']
    if 'notes' in entry:
        if 'metadata' not in entry: entry['metadata'] = {}
        entry['metadata']['remarks'] = entry['notes']
        del entry['notes']
    elif 'metadata' in entry and 'remarks' in entry['metadata']:
        entry['metadata']['remarks'] = ''
    return entry

@app.post("/api/glossary/entry", status_code=201)
def create_glossary_entry(game_id: str, file_name: str, payload: GlossaryEntryCreate):
    file_path = os.path.join(GLOSSARY_DIR, game_id, file_name)
    data = _read_glossary_file(file_path)

    new_entry_dict = payload.dict()
    new_entry_dict['id'] = str(uuid.uuid4())

    storage_entry = _transform_entry_to_storage_format(new_entry_dict)

    data["entries"].append(storage_entry)
    _write_glossary_file(file_path, data)

    return storage_entry

@app.put("/api/glossary/entry/{entry_id}")
def update_glossary_entry(game_id: str, file_name: str, entry_id: str, payload: GlossaryEntryIn):
    if entry_id != payload.id:
        raise HTTPException(status_code=400, detail="Entry ID in URL and payload must match.")

    file_path = os.path.join(GLOSSARY_DIR, game_id, file_name)
    data = _read_glossary_file(file_path)

    entry_found = False
    for i, entry in enumerate(data["entries"]):
        if entry.get("id") == entry_id:
            updated_entry_dict = payload.dict()
            data["entries"][i] = _transform_entry_to_storage_format(updated_entry_dict)
            entry_found = True
            break

    if not entry_found:
        raise HTTPException(status_code=404, detail=f"Entry with ID '{entry_id}' not found.")

    _write_glossary_file(file_path, data)
    return payload

@app.delete("/api/glossary/entry/{entry_id}", status_code=204)
def delete_glossary_entry(game_id: str, file_name: str, entry_id: str):
    file_path = os.path.join(GLOSSARY_DIR, game_id, file_name)
    data = _read_glossary_file(file_path)

    original_count = len(data["entries"])
    data["entries"] = [entry for entry in data["entries"] if entry.get("id") != entry_id]

    if len(data["entries"]) == original_count:
        raise HTTPException(status_code=404, detail=f"Entry with ID '{entry_id}' not found.")

    _write_glossary_file(file_path, data)
    return {}

@app.get("/api/doc-content", response_class=PlainTextResponse)
def get_doc_content(path: str = Query(...)):
    if ".." in path:
        raise HTTPException(status_code=400, detail="Invalid path.")
    docs_dir = os.path.abspath(os.path.join(project_root, 'docs'))
    requested_path = os.path.abspath(os.path.join(docs_dir, path))
    if not requested_path.startswith(docs_dir):
        raise HTTPException(status_code=403, detail="Access forbidden.")
    if not os.path.isfile(requested_path) or not requested_path.endswith(".md"):
        raise HTTPException(status_code=404, detail="File not found or not a markdown file.")
    try:
        with open(requested_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")


# --- Models for Workshop Generator ---
class WorkshopRequest(BaseModel):
    item_id: str
    user_template: str
    target_language: str
    project_id: Optional[str] = "" # Can be empty if using manual item ID
    custom_language: Optional[str] = ""
    api_provider: str # Added new field

# --- API Endpoints for Workshop Generator ---

@app.post("/api/tools/generate_workshop_description")
def generate_workshop_description(payload: WorkshopRequest):
    """
    Handles the full workflow for generating a Steam Workshop description.
    """
    # 1. Get original description from Steam
    original_desc = workshop_formatter.get_workshop_item_details(payload.item_id)
    if original_desc is None:
        raise HTTPException(status_code=502, detail="Failed to fetch description from Steam Workshop. The Workshop ID might be invalid or the service may be down.")

    # 2. Format description with AI
    formatted_bbcode = workshop_formatter.format_description_with_ai(
        original_description=original_desc,
        user_template=payload.user_template,
        target_language=payload.target_language,
        custom_language=payload.custom_language,
        project_id=payload.project_id,
        selected_provider=payload.api_provider
    )
    if "[AI Formatting Failed" in formatted_bbcode or "[AI Formatting Skipped" in formatted_bbcode:
         raise HTTPException(status_code=500, detail=f"AI processing failed. Details: {formatted_bbcode}")

    # 3. Archive the generated description
    saved_path = workshop_formatter.archive_generated_description(
        project_id=payload.project_id,
        bbcode_content=formatted_bbcode,
        workshop_id=payload.item_id
    )
    if saved_path is None:
        return {
            "bbcode": formatted_bbcode,
            "saved_path": None,
            "message": "BBCode generated successfully, but failed to save the archive file."
        }

    return {"bbcode": formatted_bbcode, "saved_path": saved_path}


@app.get("/")
def read_root():
    return {"message": "欢迎使用P社Mod本地化工厂API"}

# --- Validation API ---

class ValidationRequest(BaseModel):
    game_id: str
    content: str
    source_lang_code: Optional[str] = "en_US" # Default to checking against English rules or just generic

@app.post("/api/validate/localization")
def validate_localization(payload: ValidationRequest):
    """
    Validates a snippet of localization text (YAML format).
    """
    from scripts.utils.post_process_validator import PostProcessValidator

    validator = PostProcessValidator()
    results = []

    lines = payload.content.split('\n')

    # Regex to capture: (key) (optional :version) " (value) "
    pair_pattern = re.compile(r'^\s*([a-zA-Z0-9_\.]+)\s*(?::\d*)?\s*"(.*)"\s*(?:#.*)?$')

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        if not stripped or stripped.startswith('#') or stripped.startswith('l_'):
            continue

        match = pair_pattern.match(line)
        if match:
            key = match.group(1)
            value = match.group(2)

            # Validate Entry
            entry_results = validator.validate_entry(
                game_id=payload.game_id,
                key=key,
                value=value,
                line_number=line_num,
                source_lang={"code": payload.source_lang_code}
            )
            results.extend(entry_results)

    # Transform results to simple dicts for JSON response
    json_results = []
    for r in results:
        json_results.append({
            "is_valid": r.is_valid,
            "level": r.level.value,
            "message": r.message,
            "details": r.details,
            "line_number": r.line_number,
            "key": r.key
        })

    return json_results

if __name__ == "__main__":
    uvicorn.run("scripts.web_server:app", host="0.0.0.0", port=8000, reload=True)
