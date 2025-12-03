import os
from scripts.utils.quote_extractor import QuoteExtractor
from scripts.routers.proofreading import find_source_template
from scripts.shared.services import project_manager

# Setup
projects = project_manager.get_projects()
if not projects:
    print("No projects found")
    exit()

project = projects[0]
print(f"Project: {project['name']}")
source_lang = project.get('source_language', 'simp_chinese')

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

target_path = target_file['file_path']
print(f"Target File: {target_path}")

# Find Source File
source_path = find_source_template(target_path, source_lang, "english", project['project_id'])
print(f"Source File: {source_path}")

if not source_path or not os.path.exists(source_path):
    print("Source file not found!")
    exit()

# Extract Keys
print("\n--- Extracting Source Keys (Chinese) ---")
_, source_texts, source_map = QuoteExtractor.extract_from_file(source_path)
source_keys = set()
for i in source_map:
    k = source_map[i]['key_part'].strip()
    source_keys.add(k)
    if len(source_keys) <= 5:
        print(f"Source Key Sample: '{k}'")

print(f"Total Source Keys: {len(source_keys)}")

print("\n--- Extracting Target Keys (English) ---")
_, target_texts, target_map = QuoteExtractor.extract_from_file(target_path)
target_keys = set()
for i in target_map:
    k = target_map[i]['key_part'].strip()
    target_keys.add(k)
    if len(target_keys) <= 5:
        print(f"Target Key Sample: '{k}'")

print(f"Total Target Keys: {len(target_keys)}")

# Compare
common = source_keys.intersection(target_keys)
missing_in_target = source_keys - target_keys
missing_in_source = target_keys - source_keys

print(f"\nCommon Keys: {len(common)}")
print(f"Missing in Target: {len(missing_in_target)}")
print(f"Missing in Source: {len(missing_in_source)}")

if missing_in_target:
    print(f"\nExample Missing in Target: {list(missing_in_target)[:5]}")
