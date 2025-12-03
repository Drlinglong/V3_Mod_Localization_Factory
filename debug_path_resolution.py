import os
import re
from pathlib import Path
from scripts.shared.services import project_manager

# Copy of the function from proofreading.py
def find_source_template(target_path: str, source_lang: str, current_lang: str, project_id: str = None) -> str:
    print(f"DEBUG: Finding source for {target_path}")
    print(f"DEBUG: Source Lang: {source_lang}, Current Lang: {current_lang}")
    
    try:
        path_obj = Path(target_path)
        parts = list(path_obj.parts)
        
        # --- Strategy 1: Path Manipulation ---
        lang_folder_index = -1
        for i, part in enumerate(parts):
            if part.lower() == current_lang.lower():
                lang_folder_index = i
                break
        
        if lang_folder_index != -1:
            parts[lang_folder_index] = source_lang 
            filename = parts[-1]
            current_suffix = f"_l_{current_lang}"
            source_suffix = f"_l_{source_lang}"
            
            if current_suffix.lower() in filename.lower():
                new_filename = re.sub(re.escape(current_suffix), source_suffix, filename, flags=re.IGNORECASE)
                parts[-1] = new_filename
                new_path = Path(*parts)
                print(f"DEBUG: Strategy 1 Path: {new_path}")
                if new_path.exists():
                    return str(new_path)
        else:
            print("DEBUG: Language folder not found in path parts")

        # Fallback for Strategy 1
        target_path_str = str(target_path)
        pattern_dir = re.compile(re.escape(os.sep + current_lang + os.sep), re.IGNORECASE)
        new_path_str = pattern_dir.sub(os.sep + source_lang + os.sep, target_path_str)
        pattern_suffix = re.compile(re.escape(f"_l_{current_lang}"), re.IGNORECASE)
        new_path_str = pattern_suffix.sub(f"_l_{source_lang}", new_path_str)
        
        print(f"DEBUG: Strategy 1 Fallback Path: {new_path_str}")
        if os.path.exists(new_path_str):
            return new_path_str
            
        # --- Strategy 2: Project-wide Search ---
        if project_id:
            print("DEBUG: Attempting Strategy 2 (Project Search)")
            filename = os.path.basename(target_path)
            current_suffix = f"_l_{current_lang}"
            source_suffix = f"_l_{source_lang}"
            
            if current_suffix.lower() in filename.lower():
                expected_source_filename = re.sub(re.escape(current_suffix), source_suffix, filename, flags=re.IGNORECASE)
                print(f"DEBUG: Looking for file: {expected_source_filename}")
                
                files = project_manager.get_project_files(project_id)
                print(f"DEBUG: Scanned {len(files)} files in project")
                for f in files:
                    # print(f"DEBUG: Checking {os.path.basename(f['file_path'])}")
                    if os.path.basename(f['file_path']).lower() == expected_source_filename.lower():
                        print(f"DEBUG: FOUND: {f['file_path']}")
                        return f['file_path']
            else:
                print(f"DEBUG: Suffix {current_suffix} not found in {filename}")

        return ""
        
    except Exception as e:
        print(f"Error finding source template: {e}")
        return ""

# Test with a real file from the project
# I need to get a project ID first
projects = project_manager.get_projects()
if not projects:
    print("No projects found")
    exit()

project = projects[0]
print(f"Testing with Project: {project['name']} ({project['project_id']})")
source_lang = project.get('source_language', 'simp_chinese')

# Find an English file to test
files = project_manager.get_project_files(project['project_id'])
target_file = None
for f in files:
    if "_l_english.yml" in f['file_path'].lower():
        target_file = f
        break

if target_file:
    print(f"Testing Target File: {target_file['file_path']}")
    result = find_source_template(target_file['file_path'], source_lang, "english", project['project_id'])
    print(f"RESULT: {result}")
else:
    print("No English file found to test")
