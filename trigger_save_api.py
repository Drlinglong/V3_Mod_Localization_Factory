import sys
import os
from scripts.routers.proofreading import save_proofreading_db
from scripts.schemas.proofreading import SaveProofreadingRequest
from scripts.shared.services import project_manager

# Setup
projects = project_manager.get_projects()
if not projects:
    print("No projects found")
    exit()

project = projects[0]
print(f"Project: {project['name']}")

# Find an English file
files = project_manager.get_project_files(project['project_id'])
target_file = None
for f in files:
    if "_l_english.yml" in f['file_path'].lower():
        target_file = f
        break

if not target_file:
    print("No English file found")
    exit()

print(f"Testing Save for File: {target_file['file_path']}")

# Create Mock Request
entries = [
    {"key": "remis_event.1.t", "translation": "Test Save Value 1"},
    {"key": "remis_event.1.d", "translation": "Test Save Value 2"}
]

request = SaveProofreadingRequest(
    project_id=project['project_id'],
    file_id=target_file['file_id'],
    entries=entries,
    target_language="l_simp_chinese" # Should be ignored by backend
)

try:
    result = save_proofreading_db(request)
    print(f"Save Result: {result}")
except Exception as e:
    print(f"Save Failed: {e}")
