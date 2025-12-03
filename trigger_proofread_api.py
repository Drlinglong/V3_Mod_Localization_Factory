import sys
import os
from scripts.routers.proofreading import get_proofread_data
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

print(f"Testing File: {target_file['file_path']}")

try:
    data = get_proofread_data(project['project_id'], target_file['file_id'])
    print("API Call Success")
except Exception as e:
    print(f"API Call Failed: {e}")
