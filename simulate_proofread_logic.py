from scripts.shared.services import project_manager, archive_manager
import scripts.routers.proofreading
import importlib
importlib.reload(scripts.routers.proofreading)
from scripts.routers.proofreading import get_proofread_data
import logging
import os

print(f"DEBUG: proofreading module file: {scripts.routers.proofreading.__file__}")

# Setup logging to see the debug messages I added
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

PROJECT_ID = "b53d8d2c-3b1f-4d3c-860e-f1bc4f680a5d" # 蕾姆丝计划演示mod：最后的罗马人

def run():
    print("--- Simulating Proofread Logic ---")
    
    # 1. Find File ID
    project = project_manager.get_project(PROJECT_ID)
    if not project:
        print(f"Project '{PROJECT_ID}' not found.")
        return
        
    print(f"Project Name: {project['name']}")
    print(f"Source Path: {project['source_path']}")
    mod_name_from_path = os.path.basename(project['source_path'])
    print(f"Derived Mod Name: {mod_name_from_path}")
    projects = project_manager.get_projects()
    if projects:
        print(f"Project keys: {projects[0].keys()}")
        
    project = next((p for p in projects if p.get('project_id') == PROJECT_ID or p.get('name') == PROJECT_ID), None)
    
    if not project:
        print(f"Project '{PROJECT_ID}' not found.")
        print("Available projects:")
        for p in projects:
            pid = p.get('project_id') or p.get('id')
            print(f"  ID: {pid}, Name: {p.get('name')}")
        return
    
    # Use the found project ID
    real_project_id = project.get('project_id') or project.get('id')
    print(f"Using Project ID: {real_project_id}")

    files = project_manager.get_project_files(real_project_id)
    target_file = None
    for f in files:
        if "l_english.yml" in f['file_path']:
            target_file = f
            break
            
    if not target_file:
        print("Could not find English file in project.")
        print("Available files:", [f['file_path'] for f in files])
        return

    file_id = target_file['file_id']
    print(f"Found File ID: {file_id}")
    print(f"File Path: {target_file['file_path']}")

    # 2. Call get_proofread_data
    try:
        data = get_proofread_data(PROJECT_ID, file_id)
        print("\n--- Result ---")
        ai_content = data.get('ai_content', '')
        print(f"AI Content Length: {len(ai_content)}")
        print(f"AI Content Preview:\n{ai_content[:500]}")
        
        # Check if it contains English
        if "Gift of the Storm" in ai_content:
            print("\nSUCCESS: Found English translation 'Gift of the Storm' in AI Content.")
        else:
            print("\nFAILURE: Did not find English translation in AI Content.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()
