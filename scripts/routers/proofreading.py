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

    # Fallback: If DB returns no entries, try to parse the file directly
    if not entries and os.path.exists(file_path):
        from scripts.core.loc_parser import parse_loc_file
        from pathlib import Path
        try:
            parsed_entries = parse_loc_file(Path(file_path))
            entries = [
                {"key": k, "original": v, "translation": v} 
                for k, v in parsed_entries
            ]
        except Exception as e:
            print(f"Fallback parsing failed for {file_path}: {e}")

    # --- Source File Resolution Logic ---
    try:
        project = project_manager.get_project_by_file_id(file_id)
        if project:
            # Try to determine the base filename pattern to find the counterpart
            # e.g. remis_demo_l_english.yml -> remis_demo_l_
            # We look for other files in the same project that share the prefix but have different lang
            
            filename = os.path.basename(file_path)
            # Regex to capture base name before l_language
            # Paradox files usually: name_l_language.yml
            import re
            match = re.match(r"(.+)_l_([a-z_]+)\.yml", filename)
            
            source_file_path = None
            
            if match:
                base_name = match.group(1)
                current_lang = match.group(2)
                
                # Query DB for other files with same base_name
                conn = project_manager._get_connection()
                cursor = conn.cursor()
                # Search for files ending with .yml and containing base_name_l_
                # We use LIKE %base_name_l_%.yml
                pattern = f"%{base_name}_l_%.yml"
                cursor.execute("SELECT file_path FROM project_files WHERE project_id = ? AND file_path LIKE ? AND file_path != ?", 
                               (project['project_id'], pattern, project['project_id'])) 
                               # Note: file_path in DB is full path, so != check needs full path or file_id. 
                               # Let's check file_id instead if we had it in the query, but we don't.
                               # We can filter in python.
                
                rows = cursor.fetchall()
                conn.close()
                
                candidates = []
                for r in rows:
                    cand_path = r[0]
                    # Exclude self
                    if os.path.normpath(cand_path) == os.path.normpath(file_path):
                        continue
                    candidates.append(cand_path)
                
                if candidates:
                    # If multiple candidates, prefer simp_chinese if current is english, or vice versa
                    # Or use config if available
                    from scripts.core.project_json_manager import ProjectJsonManager
                    json_manager = ProjectJsonManager(project['source_path'])
                    config = json_manager.get_config()
                    source_lang = config.get('source_language', 'simp_chinese') # Default to simp_chinese as source
                    
                    best_candidate = None
                    for cand in candidates:
                        if f"l_{source_lang}" in os.path.basename(cand):
                            best_candidate = cand
                            break
                    
                    if not best_candidate:
                        best_candidate = candidates[0] # Fallback to first found
                    
                    source_file_path = best_candidate

            if source_file_path and os.path.exists(source_file_path):
                from scripts.core.loc_parser import parse_loc_file
                from pathlib import Path
                source_parsed = parse_loc_file(Path(source_file_path))
                source_map = {k: v for k, v in source_parsed}
                
                # Update entries with real original text
                for entry in entries:
                    if entry['key'] in source_map:
                        entry['original'] = source_map[entry['key']]
    except Exception as e:
        print(f"Source resolution failed: {e}")

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
