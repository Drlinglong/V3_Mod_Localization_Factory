import os
import logging
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any

from scripts.shared.services import project_manager
from scripts.core.project_json_manager import ProjectJsonManager
from scripts.schemas.project import CreateProjectRequest, UpdateProjectStatusRequest, UpdateProjectNotesRequest
from scripts.schemas.config import UpdateConfigRequest

router = APIRouter()

@router.get("/api/projects")
def list_projects(status: Optional[str] = None):
    """Returns a list of all projects, optionally filtered by status."""
    return project_manager.get_projects(status)

@router.post("/api/project/create")
def create_project(request: CreateProjectRequest):
    """Creates a new project."""
    try:
        if not os.path.exists(request.folder_path):
             raise HTTPException(status_code=404, detail=f"Path not found: {request.folder_path}")

        project = project_manager.create_project(request.name, request.folder_path, request.game_id, request.source_language)
        return {"status": "success", "project": project}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/project/{project_id}/files")
def list_project_files(project_id: str):
    """Lists files for a given project."""
    return project_manager.get_project_files(project_id)

@router.post("/api/project/{project_id}/status")
def update_project_status(project_id: str, request: UpdateProjectStatusRequest):
    """Updates a project's status."""
    try:
        project_manager.update_project_status(project_id, request.status)
        return {"status": "success", "message": f"Project status updated to {request.status}"}
    except Exception as e:
        logging.error(f"Error updating project status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/project/{project_id}/notes")
def update_project_notes(project_id: str, request: UpdateProjectNotesRequest):
    """Adds a new note to the project."""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        # Also update the summary in DB for backward compatibility
        project_manager.update_project_notes(project_id, request.notes)
        
        # Add to JSON history
        json_manager = ProjectJsonManager(project['source_path'])
        json_manager.add_note(request.notes)
        
        return {"status": "success", "message": "Note added"}
    except Exception as e:
        logging.error(f"Error updating project notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/project/{project_id}/notes")
def list_project_notes(project_id: str):
    """Lists all notes for a project."""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        return json_manager.get_notes()
    except Exception as e:
        logging.error(f"Error listing project notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/project/{project_id}/notes/{note_id}")
def delete_project_note(project_id: str, note_id: str):
    """Deletes a note from a project."""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        json_manager.delete_note(note_id)
        return {"status": "success", "message": "Note deleted"}
    except Exception as e:
        logging.error(f"Error deleting project note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/project/{project_id}/kanban")
def get_project_kanban(project_id: str):
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        json_manager = ProjectJsonManager(project['source_path'])
        return json_manager.get_kanban_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/project/{project_id}/kanban")
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

@router.post("/api/project/{project_id}/refresh")
def refresh_project_files(project_id: str):
    try:
        project_manager.refresh_project_files(project_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/project/{project_id}/config")
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

@router.post("/api/project/{project_id}/config")
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
