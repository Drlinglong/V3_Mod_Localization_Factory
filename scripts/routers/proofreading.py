import os
from fastapi import APIRouter, HTTPException

from scripts.shared.services import project_manager, archive_manager
from scripts.schemas.proofreading import SaveProofreadingRequest

router = APIRouter()

@router.get("/api/proofread/{project_id}/{file_id}")
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

@router.post("/api/proofread/save")
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
