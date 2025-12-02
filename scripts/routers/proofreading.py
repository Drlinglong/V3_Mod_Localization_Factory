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

    # Strategy:
    # 1. Always parse the file on disk to get the "Skeleton" (Keys, Values, Line Numbers).
    #    This ensures we have the correct line numbers for patching.
    # 2. Fetch translations from DB (AI results).
    # 3. Merge: Use DB translation if available, otherwise use File value.
    
    file_entries = []
    if os.path.exists(file_path):
        from scripts.core.loc_parser import parse_loc_file_with_lines
        from pathlib import Path
        try:
            parsed_entries = parse_loc_file_with_lines(Path(file_path))
            # parsed_entries is list of (key, value, line_number)
            file_entries = parsed_entries
        except Exception as e:
            print(f"File parsing failed for {file_path}: {e}")
            # If file parsing fails, we are in trouble for patching.
            # But we might still show DB data.

    # Fetch DB entries (Key, Original, Translation)
    # archive_manager.get_entries returns list of dicts
    db_entries = archive_manager.get_entries(mod_name, file_path)
    db_map = {e['key']: e.get('translation', '') for e in db_entries}

    # Construct final entries list
    entries = []
    if file_entries:
        for key, val, ln in file_entries:
            # If key exists in DB, use DB translation (AI result)
            # Otherwise use the value from file (which might be empty or original)
            translation = db_map.get(key, val)
            entries.append({
                "key": key,
                "original": val, # Initially use file value as original (will be updated by source resolution)
                "translation": translation,
                "line_number": ln
            })
    else:
        # Fallback: If file is missing or empty, use DB entries (but line_number will be None)
        # This prevents "Explosion" but Patching won't work for these.
        entries = db_entries
        for e in entries:
            e['line_number'] = None

    # --- Source File Resolution Logic ---
    source_file_path = None
    try:
        project = project_manager.get_project_by_file_id(file_id)
        if project:
            filename = os.path.basename(file_path)
            import re
            match = re.match(r"(.+)_l_([a-z_]+)\.yml", filename)
            
            if match:
                base_name = match.group(1)
                
                # Query DB for other files with same base_name
                conn = project_manager._get_connection()
                cursor = conn.cursor()
                pattern = f"%{base_name}_l_%.yml"
                cursor.execute("SELECT file_path FROM project_files WHERE project_id = ? AND file_path LIKE ? AND file_path != ?", 
                               (project['project_id'], pattern, project['project_id'])) 
                rows = cursor.fetchall()
                conn.close()
                
                candidates = []
                for r in rows:
                    cand_path = r[0]
                    if os.path.normpath(cand_path) == os.path.normpath(file_path):
                        continue
                    candidates.append(cand_path)
                
                if candidates:
                    from scripts.core.project_json_manager import ProjectJsonManager
                    json_manager = ProjectJsonManager(project['source_path'])
                    config = json_manager.get_config()
                    source_lang = config.get('source_language', 'simp_chinese')
                    
                    best_candidate = None
                    for cand in candidates:
                        if f"l_{source_lang}" in os.path.basename(cand):
                            best_candidate = cand
                            break
                    
                    if not best_candidate:
                        best_candidate = candidates[0]
                    
                    source_file_path = best_candidate

            # Fallback: If DB didn't find source file, try filesystem heuristic
            if not source_file_path and match:
                base_name = match.group(1)
                current_lang = match.group(2)
                # Try to find english file in same directory
                # This assumes standard structure
                dir_path = os.path.dirname(file_path)
                
                # Common source languages
                for lang in ['english', 'simp_chinese', 'french', 'german', 'russian']:
                    if lang == current_lang: continue
                    
                    potential_path = os.path.join(dir_path, f"{base_name}_l_{lang}.yml")
                    if os.path.exists(potential_path):
                        source_file_path = potential_path
                        break

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

    # --- Helper: Inject Values into Structure ---
    def inject_values(lines, val_map, target_lang_code=None):
        merged = []
        # Regex to find keys in source lines:  key:0 "value"
        line_regex = re.compile(r'^(\s*)([\w\.]+):0\s*"(.*)"(.*)$')
        
        for line in lines:
            # Handle Language Declaration
            if line.strip().startswith("l_"):
                if target_lang_code:
                    merged.append(f"l_{target_lang_code}:\n")
                else:
                    merged.append(line)
                continue

            match = line_regex.match(line)
            if match:
                indent = match.group(1)
                key = match.group(2)
                # val = match.group(3) 
                comment = match.group(4) 
                
                if key in val_map:
                    new_val = val_map[key]
                    if new_val is None: new_val = ""
                    # Escape quotes
                    new_val = new_val.replace('"', '\\"')
                    merged.append(f'{indent}{key}:0 "{new_val}"{comment}\n')
                else:
                    # Key not in map? Keep original line
                    merged.append(line)
            else:
                merged.append(line)
        return "".join(merged)

    # --- Construct Full File Content (with Comments) ---
    original_file_content = ""
    ai_file_content = "" # Current translation
    
    # We need the "Skeleton" lines. 
    # Prefer Source File for structure as it's the "Truth".
    skeleton_lines = []
    
    if source_file_path and os.path.exists(source_file_path):
        try:
            with open(source_file_path, 'r', encoding='utf-8-sig') as f:
                skeleton_lines = f.readlines()
        except:
            pass
    elif os.path.exists(file_path):
        # Fallback to target file itself if no source
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                skeleton_lines = f.readlines()
        except:
            pass

    if skeleton_lines:
        # 1. Original Content (Source Values)
        # We can just use the source file content directly, BUT we want to ensure keys match?
        # Actually, raw source file content is best for "Original" column.
        # But wait, if we want to align them line-by-line, injecting is safer.
        # Let's use the source map we built earlier.
        
        # Re-read source map if needed, but we have entries['original']
        original_map = {e['key']: e.get('original', '') for e in entries}
        original_file_content = inject_values(skeleton_lines, original_map, None) # Keep source lang header? Or maybe not.

        # 2. AI/Final Content (Translation Values)
        trans_map = {e['key']: e.get('translation', '') for e in entries}
        
        # Infer target lang
        target_lang = "simp_chinese"
        target_lang_match = re.search(r"_l_([a-z_]+)\.yml", os.path.basename(file_path))
        if target_lang_match:
            target_lang = target_lang_match.group(1)

        ai_file_content = inject_values(skeleton_lines, trans_map, target_lang)

    return {
        "file_id": file_id,
        "file_path": file_path,
        "mod_name": mod_name,
        "entries": entries,
        "original_content": original_file_content,
        "file_content": ai_file_content # This is the "Final/AI" one
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
