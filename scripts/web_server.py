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
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import using absolute imports from project root
from scripts.app_settings import GAME_PROFILES, LANGUAGES, API_PROVIDERS, SOURCE_DIR, DEST_DIR
from scripts.workflows import initial_translate
from scripts.utils import logger, i18n
from scripts.core import workshop_formatter

# Setup logger
logger.setup_logger()

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
        "api_providers": list(API_PROVIDERS.keys())
    }

@app.get("/api/docs-languages")
def get_docs_languages():
    """
    Scans the docs directory and returns a list of available language subdirectories.
    """
    languages = []
    if os.path.exists(DOCS_DIR) and os.path.isdir(DOCS_DIR):
        for item in os.listdir(DOCS_DIR):
            item_path = os.path.join(DOCS_DIR, item)
            # Check if it's a directory and not a hidden directory (e.g., .git)
            if os.path.isdir(item_path) and not item.startswith('.'):
                languages.append(item)
    return languages

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

#<-- Glossar-API-Endpunkte -->
import json
from pydantic import BaseModel, Field
from datetime import datetime

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

class UpdateGlossaryRequest(BaseModel):
    entries: List[GlossaryEntryIn]

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

    # --- Validation ---
    if not file_name.endswith(".json"):
        raise HTTPException(status_code=400, detail="File name must end with .json")

    # Basic security check for filename
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        raise HTTPException(status_code=400, detail="Invalid characters in file name.")

    game_path = os.path.join(GLOSSARY_DIR, game_id)
    if not os.path.isdir(game_path):
        raise HTTPException(status_code=404, detail=f"Game '{game_id}' not found.")

    file_path = os.path.join(game_path, file_name)
    if os.path.exists(file_path):
        raise HTTPException(status_code=409, detail=f"File '{file_name}' already exists in game '{game_id}'.")

    # --- File Creation ---
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

@app.get("/api/glossary/content")
def get_glossary_content(
    game_id: str,
    file_name: str,
    page: int = Query(1, alias="page"),
    pageSize: int = Query(25, alias="pageSize")
):
    """
    Reads, sanitizes, and returns a paginated list of entries from a specific glossary file.
    Transforms the data structure for frontend compatibility.
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
            new_entry = entry.copy()
            # 1. Create a top-level 'source' field from the 'en' translation.
            new_entry['source'] = new_entry.get('translations', {}).get('en', '')

            # 2. Create a top-level 'variants' array from the 'en' variants.
            variants_dict = new_entry.get('variants', {})
            if isinstance(variants_dict, dict):
                new_entry['variants'] = variants_dict.get('en', [])
            else:
                 # Handle cases where 'variants' might already be a list (though not expected from file)
                new_entry['variants'] = variants_dict if isinstance(variants_dict, list) else []

            # 3. Ensure 'translations' is always a dict
            if 'translations' not in new_entry or not isinstance(new_entry['translations'], dict):
                new_entry['translations'] = {}

            # 4. Extract 'remarks' from metadata and assign to top-level 'notes'
            new_entry['notes'] = new_entry.get('metadata', {}).get('remarks', '')

            # 5. Ensure variants is a dict (it should be from file, but for safety)
            new_entry['variants'] = entry.get('variants', {})

            # 6. Ensure abbreviations is a dict (it should be from file, but for safety)
            new_entry['abbreviations'] = entry.get('abbreviations', {})

            transformed_entries.append(new_entry)

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


# Model for creating a new entry, ID is generated by the backend.
class GlossaryEntryCreate(BaseModel):
    source: str
    translations: Dict[str, str]
    notes: Optional[str] = ""
    variants: Optional[Dict[str, List[str]]] = {}
    abbreviations: Optional[Dict[str, str]] = {}
    metadata: Optional[Dict] = {}

# --- Helper function to read/write glossary files ---
def _read_glossary_file(file_path: str) -> Dict:
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Glossary file not found.")
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read or parse glossary file: {e}")

def _write_glossary_file(file_path: str, data: Dict):
    try:
        data["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Failed to write glossary file: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to write glossary file: {e}")

def _transform_entry_to_storage_format(entry: Dict) -> Dict:

    """Transforms a frontend-formatted entry back to the storage format."""

    entry['translations'] = entry.get('translations', {})

    entry['translations']['en'] = entry.get('source', '')



    # Ensure variants is a dict (it should be from frontend payload)

    if 'variants' not in entry:

        entry['variants'] = {}



    # Ensure abbreviations is a dict (it should be from frontend payload)

    if 'abbreviations' not in entry:

        entry['abbreviations'] = {}



    if 'source' in entry:

        del entry['source']



    # Handle notes -> metadata.remarks

    if 'notes' in entry:

        if 'metadata' not in entry:

            entry['metadata'] = {}

        entry['metadata']['remarks'] = entry['notes']

        del entry['notes'] # Remove top-level notes after moving it

    elif 'metadata' in entry and 'remarks' in entry['metadata']:

        # If notes was not provided, but remarks exists, ensure it's cleared if notes was meant to be empty

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
    """
    Safely reads and returns the content of a specific markdown file from the root 'docs' directory.
    Includes security checks to prevent directory traversal.
    """
    if ".." in path:
        raise HTTPException(status_code=400, detail="Invalid path.")

    # Create a secure, absolute path to the requested file
    docs_dir = os.path.abspath(os.path.join(project_root, 'docs'))
    requested_path = os.path.abspath(os.path.join(docs_dir, path))

    # Security check: Ensure the requested path is still within the 'docs' directory
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

@app.get("/api/projects")
def get_projects():
    """
    Returns a list of available projects.
    TODO: This should eventually query a database or project config file.
    """
    # Mock data for now
    return [
        {"name": "My Awesome Mod", "id": "my_awesome_mod", "workshop_id": "123456789"},
        {"name": "Another Great Project", "id": "another_great_project", "workshop_id": "987654321"},
    ]

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
        # Even if saving fails, we should still return the generated content to the user.
        # We can add a warning or special status in the response.
        return {
            "bbcode": formatted_bbcode,
            "saved_path": None,
            "message": "BBCode generated successfully, but failed to save the archive file."
        }

    return {"bbcode": formatted_bbcode, "saved_path": saved_path}


@app.get("/")
def read_root():
    return {"message": "欢迎使用P社Mod本地化工厂API"}

if __name__ == "__main__":
    uvicorn.run("web_server:app", host="0.0.0.0", port=8000)
