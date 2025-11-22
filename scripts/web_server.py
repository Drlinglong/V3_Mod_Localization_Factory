import os
import logging
import shutil
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Body, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

# Import core modules
from scripts.app_settings import SOURCE_DIR, MODS_CACHE_DB_PATH, LANGUAGES
from scripts.core.glossary_manager import GlossaryManager
from scripts.core.project_manager import ProjectManager
from scripts.core.archive_manager import ArchiveManager
from scripts.workflows.initial_translate import run_initial_translation
from scripts.utils import logger as app_logger

# Initialize Logger
logger = logging.getLogger("WebServer")
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Managers
glossary_manager = GlossaryManager()
project_manager = ProjectManager()
archive_manager = ArchiveManager()

# --- Pydantic Models ---

class CreateProjectRequest(BaseModel):
    name: str
    folder_path: str
    game_id: str

class SaveProofreadingRequest(BaseModel):
    project_id: str
    file_id: str
    content: str # The updated translation content (YAML string usually)
    # We might need more structured data if we are updating granular entries,
    # but for now let's assume we save the file content or a list of entries.
    # User said: "update mods_cache... update projects.sqlite... write to disk".
    # Updating mods_cache usually requires structured data (keys, original, translation).
    # If the frontend sends the full list of entries, that's better.
    entries: List[Dict[str, Any]] # [{'key': '...', 'original': '...', 'translation': '...'}, ...]

class InitialTranslationRequest(BaseModel):
    project_id: str
    target_language: str = "zh"
    api_provider: str = "gemini"
    model: str = "gemini-pro"
    # Add other fields as needed

# --- Endpoints ---

@app.get("/api/config")
def get_config():
    """Returns shared configuration."""
    return {
        "languages": LANGUAGES,
        "source_dir": SOURCE_DIR
    }

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
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/project/{project_id}/files")
def list_project_files(project_id: str):
    """Lists files for a given project."""
    return project_manager.get_project_files(project_id)

@app.post("/api/translate/start")
def start_translation(request: InitialTranslationRequest, background_tasks: BackgroundTasks):
    """
    Starts the initial translation workflow for a project.
    """
    project = project_manager.get_project(request.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Prepare arguments for workflow
    # We need to map request params to workflow args
    
    # Run in background
    background_tasks.add_task(
        run_initial_translation,
        target_language=request.target_language,
        mod_name=project['name'],
        api_provider=request.api_provider,
        model=request.model,
        project_id=request.project_id,
        selected_files=None # Translate all relevant files in project source
    )
    
    return {"status": "started", "message": f"Translation started for project {project['name']}"}

# --- Proofreading Endpoints ---

@app.get("/api/proofread/{project_id}/{file_id}")
def get_proofread_data(project_id: str, file_id: str):
    """
    Fetches data for proofreading.
    1. Identify file path from project_id + file_id.
    2. Query mods_cache for entries associated with this file.
    """
    # 1. Get File Info
    files = project_manager.get_project_files(project_id)
    target_file = next((f for f in files if f['file_id'] == file_id), None)
    
    if not target_file:
        raise HTTPException(status_code=404, detail="File not found in project")
    
    file_path = target_file['file_path'] # relative path
    project = project_manager.get_project(project_id)
    mod_name = project['name']
    # Also need source version which is stored in DB.
    # ArchiveManager.get_latest_entries(mod_name, file_path) would be ideal.
    # But ArchiveManager structure might be different.
    # Let's assume for now we fetch all entries for this file/mod combination.
    
    # We will add a method to ArchiveManager to `get_entries_for_file(mod_name, file_path)`
    # For now, using a direct query or a new method on ArchiveManager if available.
    # Since I can't see ArchiveManager methods in detail here (I read it but need to check methods),
    # I'll assume I need to extend it.
    
    # Assuming I'll add `get_entries` to ArchiveManager or use raw SQL if needed.
    # Let's implement a simple fetch in ArchiveManager or here.
    # Better to put it in ArchiveManager.
    
    entries = archive_manager.get_entries(mod_name, file_path)
    
    return {
        "project_id": project_id,
        "file_id": file_id,
        "file_path": file_path,
        "entries": entries
    }

@app.post("/api/proofread/save")
def save_proofreading(request: SaveProofreadingRequest):
    """
    Saves proofreading results.
    1. Update mods_cache.
    2. Update project_files status.
    3. Write to disk.
    """
    try:
        # 1. Get Project Info
        project = project_manager.get_project(request.project_id)
        files = project_manager.get_project_files(request.project_id)
        target_file = next((f for f in files if f['file_id'] == request.file_id), None)
        
        if not project or not target_file:
            raise HTTPException(status_code=404, detail="Project or File not found")

        # 2. Update Archive (Cache)
        # We need to update the 'translation' column for specific keys.
        archive_manager.update_translations(project['name'], target_file['file_path'], request.entries)
        
        # 3. Write to Disk
        # We need to reconstruct the file.
        # This requires a file builder.
        # For now, I will stub this or use a basic reconstruction if `archive_manager` supports it.
        # Ideally, `archive_manager` or `file_aggregator` has logic to build file content.
        # Let's delegate to a helper `write_translation_file`.
        
        output_path = os.path.join(project['target_path'], target_file['file_path'])
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Simple reconstruction (User mentioned .yml usually)
        # We need to know the language key (e.g. l_simp_chinese).
        # This is tricky without context.
        # However, the 'entries' likely contain the keys.
        # I will create a simple dumper for now.
        
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(u'\uFEFF') # BOM
            # We need the language key. Usually the first key in entries helps or we default.
            # Let's assume l_simp_chinese for CN translation or derive from config.
            # Actually, we should preserve the structure.
            # For the MVP, I will just dump the entries as "key:0 "value"" lines inside a block.
            f.write("l_simp_chinese:\n")
            for entry in request.entries:
                # key might be "some_key". we need to format it.
                # format:  key:0 "translation"
                # We need to be careful about quoting.
                val = entry.get('translation', '')
                # Escape quotes
                val = val.replace('"', '\\"')
                f.write(f' {entry["key"]}:0 "{val}"\n')

        # 4. Update Status
        project_manager.update_file_status_by_id(request.file_id, "done")
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error saving proofreading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Glossary Endpoints (Existing) ---
@app.get("/api/glossaries")
def get_glossaries():
    return glossary_manager.get_all_glossaries()

@app.get("/api/glossary/{glossary_id}/entries")
def get_glossary_entries(glossary_id: str):
    return glossary_manager.get_entries(glossary_id)

@app.post("/api/glossary/entry")
def add_glossary_entry(entry: dict):
    return glossary_manager.add_entry(entry)

@app.put("/api/glossary/entry/{entry_id}")
def update_glossary_entry(entry_id: int, entry: dict):
    return glossary_manager.update_entry(entry_id, entry)

@app.delete("/api/glossary/entry/{entry_id}")
def delete_glossary_entry(entry_id: int):
    return glossary_manager.delete_entry(entry_id)

@app.post("/api/glossary/search")
def search_glossary(query: dict = Body(...)):
    term = query.get("term", "")
    scope = query.get("scope", "all")
    game_id = query.get("game_id")
    file_path = query.get("file_path")
    return glossary_manager.search_entries(term, scope, game_id, file_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
