import os
import sqlite3
import shutil
import sys

# Define Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')
GLOSSARY_DB = os.path.join(DATA_DIR, 'database.sqlite')
PROJECTS_DB = os.path.join(DATA_DIR, 'projects.sqlite')
OUTPUT_DB = os.path.join(ASSETS_DIR, 'skeleton.sqlite')

# Demo Projects to Keep
# 1. Project Remis Stellaris Demo Mod
# 2. 蕾姆丝计划演示mod：最后的罗马人 (Vic3)
KEEP_PROJECT_IDS = [
    'bbd299e7-694f-41d8-835c-0b9ef391d581', 
    'b53d8d2c-3b1f-4d3c-860e-f1bc4f680a5d'
]

DEMO_ROOT_PLACEHOLDER = "{{BUNDLED_DEMO_ROOT}}"

# Hardcoded replacement logic:
# Map the DEV path to the PLACEHOLDER path relative structure.
# Dev Path 1: J:\V3_Mod_Localization_Factory\source_mod\Test_Project_Remis_stellaris
# Dev Path 2: J:\V3_Mod_Localization_Factory\source_mod\Test_Project_Remis_Vic3
#
# Target Structure in EXE:
# resources/demo_mod/
#   |-- Test_Project_Remis_stellaris
#   |-- Test_Project_Remis_Vic3
#
# So we want:
# {{BUNDLED_DEMO_ROOT}}/Test_Project_Remis_stellaris
# {{BUNDLED_DEMO_ROOT}}/Test_Project_Remis_Vic3

def ensure_assets_dir():
    if not os.path.exists(ASSETS_DIR):
        print(f"[INFO] Creating assets directory: {ASSETS_DIR}")
        os.makedirs(ASSETS_DIR)

def create_skeleton():
    print(f"[INFO] Starting Skeleton Database Generation...")
    ensure_assets_dir()
    
    # 1. Start with Glossary DB (it's the biggest)
    if not os.path.exists(GLOSSARY_DB):
        print(f"[ERROR] Glossary DB not found at {GLOSSARY_DB}")
        sys.exit(1)
        
    print(f"[COPY] Copying {GLOSSARY_DB} -> {OUTPUT_DB}")
    shutil.copy2(GLOSSARY_DB, OUTPUT_DB)
    
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    # 2. Attach Projects DB
    if not os.path.exists(PROJECTS_DB):
        print(f"[ERROR] Projects DB not found at {PROJECTS_DB}")
        sys.exit(1)
        
    print(f"[ATTACH] Attaching {PROJECTS_DB}")
    cursor.execute("ATTACH DATABASE ? AS src", (PROJECTS_DB,))
    
    # 3. Create Tables (if not exist in Glossary DB, which they shouldn't)
    # Copied schema from db_initializer.py
    print("[SCHEMA] Creating Projects Schema...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            game_id TEXT NOT NULL,
            source_path TEXT NOT NULL,
            target_path TEXT,
            source_language TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            last_modified TEXT,
            last_activity_type TEXT,
            last_activity_desc TEXT,
            notes TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_files (
            file_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            status TEXT DEFAULT 'todo',
            original_key_count INTEGER DEFAULT 0,
            line_count INTEGER DEFAULT 0,
            file_type TEXT DEFAULT 'source',
            FOREIGN KEY (project_id) REFERENCES projects (project_id),
            UNIQUE(project_id, file_path)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            log_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (project_id)
        )
    ''')
    
    # 4. Migrate Data
    print("[MIGRATE] Copying Project Data...")
    
    # Projects
    # We need to handle potential missing columns in SRC by selecting literals if needed.
    
    # Check if columns exist in src
    src_columns = [row[1] for row in cursor.execute("PRAGMA src.table_info(projects)").fetchall()]
    
    cols_map = {
        'project_id': 'project_id',
        'name': 'name',
        'game_id': 'game_id',
        'source_path': 'source_path',
        'target_path': 'target_path' if 'target_path' in src_columns else "''",
        'source_language': "'english'" if 'source_language' not in src_columns else 'source_language',
        'status': 'status',
        'created_at': 'created_at',
        'last_modified': "'2025-01-01 00:00:00'" if 'last_modified' not in src_columns else 'last_modified',
        'last_activity_type': "'none'" if 'last_activity_type' not in src_columns else 'last_activity_type',
        'last_activity_desc': "''" if 'last_activity_desc' not in src_columns else 'last_activity_desc',
        'notes': "''" if 'notes' not in src_columns else 'notes'
    }
    
    select_clause = ", ".join([cols_map[c] for c in ['project_id', 'name', 'game_id', 'source_path', 'target_path', 'source_language', 'status', 'created_at', 'last_modified', 'last_activity_type', 'last_activity_desc', 'notes']])

    query = f"""
        INSERT INTO main.projects 
        (project_id, name, game_id, source_path, target_path, source_language, status, created_at, last_modified, last_activity_type, last_activity_desc, notes)
        SELECT 
            {select_clause}
        FROM src.projects
        WHERE project_id IN (?, ?)
    """
    
    print(query)
    cursor.execute(query, (KEEP_PROJECT_IDS[0], KEEP_PROJECT_IDS[1]))
    
    # Files
    cursor.execute("""
        INSERT INTO main.project_files
        SELECT * FROM src.project_files
        WHERE project_id IN (?, ?)
    """, (KEEP_PROJECT_IDS[0], KEEP_PROJECT_IDS[1]))
    
    # Logs - Do we keep them? Let's keep them for history or maybe clear them.
    # User said "Clean user data" - maybe clean logs?
    # Keeping logs for Demo might be nice to show "history". Let's keep them for these projects.
    
    # Check if activity_log exists in src
    src_tables = [row[0] for row in cursor.execute("SELECT name FROM src.sqlite_master WHERE type='table'").fetchall()]
    
    if 'activity_log' in src_tables:
        cursor.execute("""
            INSERT INTO main.activity_log
            SELECT * FROM src.activity_log
            WHERE project_id IN (?, ?)
        """, (KEEP_PROJECT_IDS[0], KEEP_PROJECT_IDS[1]))
    else:
        print("[WARN] activity_log table not found in source DB. Skipping logs.")

    conn.commit()
    
    # 5. Detach
    cursor.execute("DETACH DATABASE src")
    
    # 6. Apply Placeholders
    print("[SANITIZE] Applying path placeholders...")
    
    # We replace the common parent content.
    # Assuming standard structure: J:\V3_Mod_Localization_Factory\source_mod\xxxx
    # We want to replace everything up to the folder name with placeholder.
    
    # For Stellaris
    cursor.execute("""
        UPDATE projects 
        SET source_path = REPLACE(source_path, 'J:\\V3_Mod_Localization_Factory\\source_mod\\', ? || '/')
        WHERE project_id = ?
    """, (DEMO_ROOT_PLACEHOLDER, KEEP_PROJECT_IDS[0]))
    
    cursor.execute("""
        UPDATE projects 
        SET target_path = REPLACE(target_path, 'J:\\V3_Mod_Localization_Factory', ?)
        WHERE project_id = ?
    """, ("{{BUNDLED_USER_ROOT}}", KEEP_PROJECT_IDS[0])) # Maybe clear export path? Or use another placeholder?
    # Actually export path isn't critical for demo to work, but good to be safe.
    
    # For Vic3
    cursor.execute("""
        UPDATE projects 
        SET source_path = REPLACE(source_path, 'J:\\V3_Mod_Localization_Factory\\source_mod\\', ? || '/')
        WHERE project_id = ?
    """, (DEMO_ROOT_PLACEHOLDER, KEEP_PROJECT_IDS[1]))
    
    # Also update project_files file_path!!!
    # file_path in project_files is RELATIVE to project root usually? 
    # Let's check the dump or knowledge...
    # Usually file_path is relative in Remis? 
    # Let's check one record from project_files.
    
    conn.commit()
    
    # Check file paths
    print("[CHECK] Verifying file paths...")
    # If file paths are absolute, we must fix them.
    cursor.execute("SELECT file_path FROM project_files LIMIT 1")
    row = cursor.fetchone()
    if row:
        sample_path = row[0]
        print(f"Sample file path: {sample_path}")
        if "J:" in sample_path or ":" in sample_path:
             print("[SANITIZE] Fixing absolute file paths in project_files...")
             cursor.execute("""
                UPDATE project_files
                SET file_path = REPLACE(file_path, 'J:\\V3_Mod_Localization_Factory\\source_mod\\', ? || '/')
             """, (DEMO_ROOT_PLACEHOLDER,))
             conn.commit()
    
    # 7. Cleanup & Optimize
    print("[CLEAN] Vacuuming...")
    cursor.execute("VACUUM")
    conn.close()
    
    print(f"[SUCCESS] Skeleton Generated at {OUTPUT_DB}")

if __name__ == "__main__":
    create_skeleton()
