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
from scripts.app_settings import GAME_PROFILES, LANGUAGES, API_PROVIDERS, SOURCE_DIR, DEST_DIR, MODS_CACHE_DB_PATH, get_api_key, load_api_keys_to_env, get_appdata_config_path
from scripts.workflows import initial_translate
from scripts.utils import logger, i18n

# Load API keys from keyring into environment variables
load_api_keys_to_env()

# Setup logger and i18n BEFORE importing managers that use them
logger.setup_logger()
i18n.load_language() # Load default language

from scripts.core import workshop_formatter
from scripts.core.glossary_manager import GlossaryManager
from scripts.core.project_manager import ProjectManager
from scripts.core.project_json_manager import ProjectJsonManager
from scripts.core.checkpoint_manager import CheckpointManager
from scripts.core.archive_manager import ArchiveManager
from scripts.core.neologism_manager import neologism_manager

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

class UpdateProjectStatusRequest(BaseModel):
    status: str

class UpdateProjectNotesRequest(BaseModel):
    notes: str

class SaveProofreadingRequest(BaseModel):
    project_id: str
    file_id: str
    entries: List[Dict[str, Any]]
    content: str = "" # Legacy support

# --- New Project Endpoints ---
@app.get("/api/projects")
def list_projects(status: Optional[str] = None):
    """Returns a list of all projects, optionally filtered by status."""
    return project_manager.get_projects(status)

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

@app.post("/api/project/{project_id}/status")
def update_project_status(project_id: str, request: UpdateProjectStatusRequest):
    """Updates a project's status."""
    try:
        project_manager.update_project_status(project_id, request.status)
        return {"status": "success", "message": f"Project status updated to {request.status}"}
    except Exception as e:
        logging.error(f"Error updating project status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/project/{project_id}/notes")
def update_project_notes(project_id: str, request: UpdateProjectNotesRequest):
    """Updates a project's notes."""
    try:
        project_manager.update_project_notes(project_id, request.notes)
        return {"status": "success", "message": "Project notes updated"}
    except Exception as e:
        logging.error(f"Error updating project notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class CustomLangConfig(BaseModel):
    name: str
    code: str
    key: str
    folder_prefix: str

class InitialTranslationRequest(BaseModel):
    project_id: str
    source_lang_code: str
    target_lang_codes: List[str] = ["zh-CN"]
    api_provider: str = "gemini"
    model: str = "gemini-pro"
    mod_context: Optional[str] = ""
    selected_glossary_ids: Optional[List[int]] = []
    use_main_glossary: bool = True
    clean_source: bool = False
    custom_lang_config: Optional[CustomLangConfig] = None

@app.post("/api/translate/start")
def start_translation_project(request: InitialTranslationRequest, background_tasks: BackgroundTasks):
    """
    Starts the initial translation workflow for a project.
    """
    project = project_manager.get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "log": []}

    # Prepare arguments for the workflow
    mod_name = project['name']
    # Ensure source path exists
    if not os.path.exists(project['source_path']):
         raise HTTPException(status_code=400, detail=f"Project source path not found: {project['source_path']}")

    tasks[task_id]["status"] = "starting"
    tasks[task_id]["log"].append(f"Starting translation for project: '{mod_name}'")

    background_tasks.add_task(
        run_translation_workflow_v2,
        task_id,
        mod_name,
        project['game_id'], # Assuming game_id maps to game_profile_id
        request.source_lang_code,
        request.target_lang_codes,
        request.api_provider,
        request.mod_context,
        request.selected_glossary_ids,
        request.model,
        request.use_main_glossary,
        request.custom_lang_config
    )

    return {"task_id": task_id, "status": "started", "message": f"Translation started for project {project['name']}"}

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
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        return json_manager.get_kanban_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/project/{project_id}/kanban")
def save_project_kanban(project_id: str, kanban_data: Dict[str, Any]):
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        json_manager.save_kanban_data(kanban_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/project/{project_id}/refresh")
def refresh_project_files(project_id: str):
    try:
        project_manager.refresh_project_files(project_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/project/{project_id}/config")
def get_project_config(project_id: str):
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        config = json_manager.get_config()
        return {
            "source_path": project['source_path'],
            "translation_dirs": config.get("translation_dirs", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class UpdateConfigRequest(BaseModel):
    action: str
    path: str

@app.post("/api/project/{project_id}/config")
def update_project_config(project_id: str, request: UpdateConfigRequest):
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
        project_manager.refresh_project_files(project_id)
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
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

        output_path = os.path.join(project['target_path'], target_file['file_path'])
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(u'\ufeff')
            f.write("l_simp_chinese:\n")
            for entry in request.entries:
                val = entry.get('translation', '')
                val = val.replace('"', '\"')
                f.write(f' {entry["key"]}:0 "{val}"\n')

        project_manager.update_file_status_by_id(request.file_id, "done")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    try:
        mod_name = file.filename.replace(".zip", "")
        source_path = os.path.join(SOURCE_DIR, mod_name)
        if os.path.exists(source_path):
            shutil.rmtree(source_path)
        temp_zip_path = os.path.join(SOURCE_DIR, file.filename)
        with open(temp_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(source_path)
        extracted_items = os.listdir(source_path)
        if len(extracted_items) == 1:
            potential_inner_folder = os.path.join(source_path, extracted_items[0])
            if os.path.isdir(potential_inner_folder):
                for item_name in os.listdir(potential_inner_folder):
                    shutil.move(os.path.join(potential_inner_folder, item_name), os.path.join(source_path, item_name))
                os.rmdir(potential_inner_folder)
        os.remove(temp_zip_path) # Clean up the zip file
        tasks[task_id]["status"] = "starting"
        tasks[task_id]["log"].append(f"Mod '{mod_name}' 已上传并解压。")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {e}")

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
    custom_lang_config: Optional[CustomLangConfig] = None

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

    if not os.path.exists(payload.project_path) or not os.path.isdir(payload.project_path):
        raise HTTPException(status_code=400, detail="Invalid project path.")

    mod_name = os.path.basename(payload.project_path)
    source_path = os.path.join(SOURCE_DIR, mod_name)

    try:
        if not payload.is_existing_source:
            if os.path.exists(source_path):
                shutil.rmtree(source_path)
            shutil.copytree(payload.project_path, source_path)
        
        tasks[task_id]["status"] = "starting"
        tasks[task_id]["log"].append(f"Using source: '{mod_name}'")

    except Exception as e:
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
        payload.use_main_glossary,
        payload.custom_lang_config
    )

    return {"task_id": task_id, "message": "翻译任务已开始"}

def run_translation_workflow_v2(
    task_id: str, mod_name: str, game_profile_id: str, source_lang_code: str,
    target_lang_codes: List[str], api_provider: str, mod_context: str,
    selected_glossary_ids: List[int], model_name: Optional[str], use_main_glossary: bool,
    custom_lang_config: Optional[CustomLangConfig] = None
):
    i18n.load_language('en_US')
    tasks[task_id]["status"] = "processing"
    tasks[task_id]["log"].append("背景翻译任务开始 (V2)...")
    try:
        game_profile = GAME_PROFILES.get(game_profile_id)
        source_lang = next((lang for lang in LANGUAGES.values() if lang["code"] == source_lang_code), None)
        target_languages = [lang for lang in LANGUAGES.values() if lang["code"] in target_lang_codes]
        
        # If custom language is provided, use it instead (or in addition? For now, let's assume it replaces if target_lang_codes contains 'custom')
        if custom_lang_config:
             # Convert Pydantic model to dict
             custom_lang = custom_lang_config.dict()
             # Ensure it has necessary fields
             if not custom_lang.get('name_en'): custom_lang['name_en'] = custom_lang['name']
             target_languages = [custom_lang]

        if not all([game_profile, source_lang]) or (not target_languages and not custom_lang_config):
            raise ValueError("无效的游戏配置、源语言或目标语言。")
        
        final_glossary_ids = list(selected_glossary_ids) if selected_glossary_ids else []
        if use_main_glossary:
            available = glossary_manager.get_available_glossaries(game_profile["id"])
            main_glossary = next((g for g in available if g.get('is_main')), None)
            if main_glossary and main_glossary['glossary_id'] not in final_glossary_ids:
                final_glossary_ids.append(main_glossary['glossary_id'])
        
        initial_translate.run(
            mod_name=mod_name, game_profile=game_profile, source_lang=source_lang,
            target_languages=target_languages, selected_provider=api_provider,
            mod_context=mod_context, selected_glossary_ids=final_glossary_ids,
            model_name=model_name, use_glossary=True
        )
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["log"].append("翻译流程成功完成！")
        output_folder_name = f"{target_languages[0]['folder_prefix']}{mod_name}"
        if len(target_languages) > 1:
            output_folder_name = f"Multilanguage-{mod_name}"
        result_dir = os.path.join(DEST_DIR, output_folder_name)
        zip_path = shutil.make_archive(result_dir, 'zip', result_dir)
        tasks[task_id]["result_path"] = zip_path
    except Exception as e:
        tb_str = traceback.format_exc()
        error_message = f"工作流执行失败: {e}\n{tb_str}"
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["log"].append(error_message)

@app.get("/api/glossaries/{game_id}")
def get_game_glossaries(game_id: str):
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
    if not task or task["status"] != "completed":
        raise HTTPException(status_code=404, detail="任务未完成或结果文件未找到")
    return FileResponse(task["result_path"], media_type='application/zip', filename=os.path.basename(task["result_path"]))

@app.get("/api/config")
def get_config():
    return {
        "game_profiles": GAME_PROFILES,
        "languages": LANGUAGES,
        "api_providers": list(API_PROVIDERS.keys()),
        "source_dir": SOURCE_DIR
    }

#<-- Glossar-API-Endpunkte -->
DOCS_DIR = os.path.join(project_root, "docs")

class GlossaryEntryIn(BaseModel):
    id: str
    source: str
    translations: Dict[str, str]
    notes: Optional[str] = ""
    variants: Optional[Dict[str, List[str]]] = {}
    abbreviations: Optional[Dict[str, str]] = {}
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
    raise HTTPException(status_code=501, detail="This endpoint is deprecated.")

@app.get("/api/glossary/tree")
def get_glossary_tree():
    return glossary_manager.get_glossary_tree_data()

def _transform_storage_to_frontend_format(entry: Dict) -> Dict:
    """
    Transforms a glossary entry from the database storage format to the format
    expected by the frontend.
    """
    new_entry = entry.copy()
    
    # Extract 'en' translation as the source term
    new_entry['source'] = new_entry.get('translations', {}).get('en', '')

    # Extract notes from remarks inside raw_metadata
    new_entry['notes'] = new_entry.get('raw_metadata', {}).get('remarks', '')

    # Pass the full raw_metadata object to the frontend as 'metadata'
    new_entry['metadata'] = new_entry.get('raw_metadata', {})

    # Ensure variants and abbreviations are present
    if 'variants' not in new_entry: new_entry['variants'] = {}
    if 'abbreviations' not in new_entry: new_entry['abbreviations'] = {}
    
    return new_entry

@app.get("/api/glossary/content")
def get_glossary_content(glossary_id: int, page: int = Query(1, alias="page"), pageSize: int = Query(25, alias="pageSize")):
    data = glossary_manager.get_glossary_entries_paginated(glossary_id, page, pageSize)
    transformed_entries = [_transform_storage_to_frontend_format(entry) for entry in data.get("entries", [])]
    return {"entries": transformed_entries, "totalCount": data.get("totalCount", 0)}

@app.post("/api/glossary/search")
def search_glossary(payload: SearchGlossaryRequest):
    glossary_ids_to_search = []
    if payload.scope == 'file':
        if not payload.file_name:
            raise HTTPException(status_code=400, detail="file_name (as key 'game|id|name') is required.")
        try:
            glossary_ids_to_search.append(int(payload.file_name.split('|')[1]))
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid key format.")
    elif payload.scope == 'game':
        if not payload.game_id:
            raise HTTPException(status_code=400, detail="game_id is required.")
        game_glossaries = glossary_manager.get_available_glossaries(payload.game_id)
        glossary_ids_to_search = [g['glossary_id'] for g in game_glossaries]
    elif payload.scope == 'all':
        tree = glossary_manager.get_glossary_tree_data()
        for game_node in tree:
            for file_node in game_node.get('children', []):
                try:
                    glossary_ids_to_search.append(int(file_node['key'].split('|')[1]))
                except (ValueError, IndexError):
                    continue
    if not glossary_ids_to_search:
        return {"entries": [], "totalCount": 0}
    result_data = glossary_manager.search_glossary_entries_paginated(
        query=payload.query, glossary_ids=glossary_ids_to_search,
        page=payload.page, page_size=payload.pageSize
    )
    transformed_entries = [_transform_storage_to_frontend_format(entry) for entry in result_data.get("entries", [])]
    return {"entries": transformed_entries, "totalCount": result_data.get("totalCount", 0)}

class GlossaryEntryCreate(BaseModel):
    source: str
    translations: Dict[str, str]
    notes: Optional[str] = ""
    variants: Optional[Dict[str, List[str]]] = {}
    abbreviations: Optional[Dict[str, str]] = {}
    metadata: Optional[Dict] = {}

def _transform_entry_to_storage_format(entry: Dict) -> Dict:
    if 'translations' not in entry: entry['translations'] = {}
    if entry.get('source'):
        entry['translations']['en'] = entry['source']
    if 'notes' in entry:
        if 'raw_metadata' not in entry: entry['raw_metadata'] = {}
        entry['raw_metadata']['remarks'] = entry['notes']
        del entry['notes']
    if 'source' in entry: del entry['source']
    return entry

@app.post("/api/glossary/entry", status_code=201)
def create_glossary_entry(glossary_id: int, payload: GlossaryEntryCreate):
    new_entry_dict = payload.dict()
    new_entry_dict['id'] = str(uuid.uuid4())
    storage_entry = _transform_entry_to_storage_format(new_entry_dict)
    if not glossary_manager.add_entry(glossary_id, storage_entry):
        raise HTTPException(status_code=500, detail="Failed to create glossary entry.")
    return new_entry_dict

@app.put("/api/glossary/entry/{entry_id}")
def update_glossary_entry(entry_id: str, payload: GlossaryEntryIn):
    if entry_id != payload.id:
        raise HTTPException(status_code=400, detail="Entry ID mismatch.")
    updated_entry_dict = payload.dict()
    storage_entry = _transform_entry_to_storage_format(updated_entry_dict)
    if not glossary_manager.update_entry(entry_id, storage_entry):
        raise HTTPException(status_code=404, detail=f"Entry with ID '{entry_id}' not found or failed to update.")
    return payload

@app.delete("/api/glossary/entry/{entry_id}", status_code=204)
def delete_glossary_entry(entry_id: str):
    if not glossary_manager.delete_entry(entry_id):
        raise HTTPException(status_code=404, detail=f"Entry with ID '{entry_id}' not found.")
    return {}

# --- Docs Endpoints ---
@app.get("/api/docs-languages")
def get_docs_languages():
    docs_dir = os.path.join(project_root, 'docs')
    if not os.path.isdir(docs_dir): return []
    return sorted([item for item in os.listdir(docs_dir) if os.path.isdir(os.path.join(docs_dir, item))])

def _scan_docs_recursive(directory, parent_key=''):
    nodes = []
    if not os.path.isdir(directory): return []
    for item in sorted(os.listdir(directory)):
        path = os.path.join(directory, item)
        key = os.path.join(parent_key, item)
        if os.path.isdir(path):
            children = _scan_docs_recursive(path, key)
            if children:
                nodes.append({"title": item, "key": key, "children": children})
        elif item.endswith(".md"):
            nodes.append({"title": item.replace(".md", ""), "key": key, "isLeaf": True})
    return nodes

@app.get("/api/docs-tree")
def get_docs_tree():
    docs_dir = os.path.join(project_root, 'docs')
    tree_data = {}
    if not os.path.isdir(docs_dir): return {}
    for lang in os.listdir(docs_dir):
        lang_path = os.path.join(docs_dir, lang)
        if os.path.isdir(lang_path):
            tree_data[lang] = _scan_docs_recursive(lang_path, lang)
    return tree_data

@app.get("/api/doc-content", response_class=PlainTextResponse)
def get_doc_content(path: str = Query(...)):
    if ".." in path:
        raise HTTPException(status_code=400, detail="Invalid path.")
    docs_dir = os.path.abspath(os.path.join(project_root, 'docs'))
    requested_path = os.path.abspath(os.path.join(docs_dir, path))
    if not requested_path.startswith(docs_dir):
        raise HTTPException(status_code=403, detail="Access forbidden.")
    if not os.path.isfile(requested_path) or not requested_path.endswith(".md"):
        raise HTTPException(status_code=404, detail="File not found.")
    with open(requested_path, 'r', encoding='utf-8') as f:
        return f.read()

# --- Workshop Generator Endpoints ---
class WorkshopRequest(BaseModel):
    item_id: str
    user_template: str
    target_language: str
    project_id: Optional[str] = ""
    custom_language: Optional[str] = ""
    api_provider: str

@app.post("/api/tools/generate_workshop_description")
def generate_workshop_description(payload: WorkshopRequest):
    original_desc = workshop_formatter.get_workshop_item_details(payload.item_id)
    if original_desc is None:
        raise HTTPException(status_code=502, detail="Failed to fetch from Steam Workshop.")
    formatted_bbcode = workshop_formatter.format_description_with_ai(
        original_description=original_desc, **payload.dict()
    )
    if "[AI Formatting Failed" in formatted_bbcode:
         raise HTTPException(status_code=500, detail=f"AI processing failed: {formatted_bbcode}")
    saved_path = workshop_formatter.archive_generated_description(
        project_id=payload.project_id, bbcode_content=formatted_bbcode, workshop_id=payload.item_id
    )
    return {"bbcode": formatted_bbcode, "saved_path": saved_path}

# --- Neologism API ---
class ApproveNeologismRequest(BaseModel):
    project_id: str
    final_translation: str
    glossary_id: int

class UpdateNeologismRequest(BaseModel):
    project_id: str
    suggestion: str

class MineNeologismsRequest(BaseModel):
    project_id: str
    api_provider: str
    target_lang: str = "zh-CN"
    file_paths: Optional[List[str]] = None

@app.get("/api/projects/{project_id}/files")
def list_project_files(project_id: str):
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = []
    source_path = project['source_path']
    for root, _, filenames in os.walk(source_path):
        for filename in filenames:
            if filename.endswith(('.txt', '.yml', '.yaml', '.csv', '.json')):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, source_path)
                files.append({"path": full_path, "name": filename, "rel_path": rel_path})
    return files

@app.get("/api/neologisms")
def list_neologisms(project_id: Optional[str] = None):
    """List neologism candidates, optionally filtered by project."""
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id query parameter is required")
    return neologism_manager.get_pending_candidates(project_id)

@app.post("/api/neologisms/{candidate_id}/approve")
def approve_neologism(candidate_id: str, payload: ApproveNeologismRequest):
    """Approve a neologism candidate and add to glossary."""
    if neologism_manager.approve_candidate(payload.project_id, candidate_id, payload.final_translation, payload.glossary_id):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Candidate not found or failed to approve")

@app.post("/api/neologisms/{candidate_id}/reject")
def reject_neologism(candidate_id: str, payload: dict):
    """Reject a neologism candidate."""
    project_id = payload.get('project_id')
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id is required")
    if neologism_manager.reject_candidate(project_id, candidate_id):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Candidate not found")

@app.patch("/api/neologisms/{candidate_id}")
def update_neologism_suggestion(candidate_id: str, payload: UpdateNeologismRequest):
    """Update a candidate's suggestion."""
    if neologism_manager.update_candidate_suggestion(payload.project_id, candidate_id, payload.suggestion):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Candidate not found")

@app.post("/api/neologisms/mine")
def trigger_mining(payload: MineNeologismsRequest, background_tasks: BackgroundTasks):
    """Trigger neologism mining for a project."""
    project = project_manager.get_project(payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all text files in project
    if payload.file_paths:
        files = payload.file_paths
    else:
        # Get all text files in project
        files = []
        for root, _, filenames in os.walk(project['source_path']):
            for filename in filenames:
                if filename.endswith(('.txt', '.yml', '.yaml', '.csv')):
                    files.append(os.path.join(root, filename))
    
    background_tasks.add_task(
        neologism_manager.run_mining_workflow,
        payload.project_id,
        files,
        payload.api_provider,
        "en", # source_lang
        payload.target_lang # target_lang
    )
    return {"status": "started", "message": "Mining started in background"}


@app.get("/")
def read_root():
    return {"message": "欢迎使用P社Mod本地化工厂API"}

# --- Validation API ---
class ValidationRequest(BaseModel):
    game_id: str
    content: str
    source_lang_code: Optional[str] = "en_US"


class CheckpointStatusRequest(BaseModel):
    mod_name: str
    target_lang_codes: List[str]

@app.post("/api/translation/checkpoint-status")
def check_checkpoint_status(payload: CheckpointStatusRequest):
    """Checks if a checkpoint exists for the given configuration."""
    try:
        # Determine output folder name logic (duplicated from initial_translate, ideally shared)
        # NOTE: This logic must match initial_translate.py exactly
        is_batch_mode = len(payload.target_lang_codes) > 1
        if is_batch_mode:
            output_folder_name = f"Multilanguage-{payload.mod_name}"
        else:
            # We need the folder prefix. This is tricky without the full language object.
            # Assuming standard prefix or we need to look it up.
            # Let's look up the language object from LANGUAGES
            target_code = payload.target_lang_codes[0]
            target_lang = next((l for l in LANGUAGES.values() if l["code"] == target_code), None)
            if target_lang:
                prefix = target_lang.get("folder_prefix", f"{target_lang['code']}-")
                output_folder_name = f"{prefix}{payload.mod_name}"
            else:
                # Fallback if lang not found (shouldn't happen if frontend sends valid codes)
                output_folder_name = f"{target_code}-{payload.mod_name}"

        output_dir = os.path.join(DEST_DIR, output_folder_name)
        cm = CheckpointManager(output_dir)
        info = cm.get_checkpoint_info()
        
        total_files = 0
        if info["exists"]:
            source_path = os.path.join(SOURCE_DIR, payload.mod_name)
            # Quick count
            for root, _, files in os.walk(source_path):
                for f in files:
                    if f.endswith(".yml") or f.endswith(".txt"):
                        total_files += 1
        
        return {
            "exists": info["exists"],
            "completed_count": info["completed_count"],
            "total_files_estimate": total_files,
            "metadata": info["metadata"]
        }
    except Exception as e:
        logging.error(f"Error checking checkpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/translation/checkpoint")
def delete_checkpoint(payload: CheckpointStatusRequest):
    """Deletes the checkpoint file for the given configuration."""
    try:
        # Determine output folder name logic (duplicated)
        is_batch_mode = len(payload.target_lang_codes) > 1
        if is_batch_mode:
            output_folder_name = f"Multilanguage-{payload.mod_name}"
        else:
            target_code = payload.target_lang_codes[0]
            target_lang = next((l for l in LANGUAGES.values() if l["code"] == target_code), None)
            if target_lang:
                prefix = target_lang.get("folder_prefix", f"{target_lang['code']}-")
                output_folder_name = f"{prefix}{payload.mod_name}"
            else:
                output_folder_name = f"{target_code}-{payload.mod_name}"

        output_dir = os.path.join(DEST_DIR, output_folder_name)
        cm = CheckpointManager(output_dir)
        cm.clear_checkpoint()
        return {"status": "success", "message": "Checkpoint deleted."}
    except Exception as e:
        logging.error(f"Error deleting checkpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- API Key Management ---

class UpdateApiKeyRequest(BaseModel):
    provider_id: str
    api_key: str

@app.get("/api/api-keys")
def get_api_keys():
    providers = []
    # Reload env to ensure we have the latest keys if they were changed externally
    load_dotenv(override=True)
    
    for provider_id, config in API_PROVIDERS.items():
        env_var = config.get("api_key_env")
        is_keyless = env_var is None
        
        api_key = get_api_key(provider_id, env_var) if env_var else None
        has_key = bool(api_key)
        
        masked_key = None
        if has_key and len(api_key) > 8:
            masked_key = f"{api_key[:4]}...{api_key[-4:]}"
        elif has_key:
            masked_key = "***"
            
        providers.append({
            "id": provider_id,
            "name": provider_id.replace("_", " ").title(),
            "description": config.get("description", ""),
            "is_keyless": is_keyless,
            "has_key": has_key,
            "masked_key": masked_key
        })
    return providers

@app.post("/api/api-keys")
def update_api_key(payload: UpdateApiKeyRequest):
    provider_id = payload.provider_id
    new_key = payload.api_key
    
    if provider_id not in API_PROVIDERS:
        raise HTTPException(status_code=400, detail="Invalid provider ID")
        
    config = API_PROVIDERS[provider_id]
    env_var = config.get("api_key_env")
    
    if not env_var:
        raise HTTPException(status_code=400, detail="This provider does not require an API key")
        
    # Save to AppData config.json
    try:
        config_path = get_appdata_config_path()
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError:
                    config = {} # Corrupt file, overwrite
        
        if "api_keys" not in config:
            config["api_keys"] = {}
            
        config["api_keys"][provider_id] = new_key
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
            
    except Exception as e:
        logging.error(f"Failed to save to AppData config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save API key to config file: {str(e)}")
    
    # Update current environment variable immediately
    os.environ[env_var] = new_key
    
    return {"status": "success"}


if __name__ == "__main__":
    port = int(os.environ.get("BACKEND_PORT", 9000))
    uvicorn.run("scripts.web_server:app", host="0.0.0.0", port=port, reload=True)