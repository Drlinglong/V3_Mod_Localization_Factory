import os
import sqlite3
import sys
from scripts import app_settings

def fix_demo_paths(conn):
    """
    Hydrates {{DEMO_ROOT}} placeholders in the database with the actual path.
    """
    try:
        # Determine where the demos are.
        # In frozen mode, they should be in RESOURCE_DIR/demos
        # In dev mode, they are in PROJECT_ROOT/demos (if they exist)
        resource_dir = app_settings.RESOURCE_DIR
        demo_root = os.path.join(resource_dir, "demos")
        
        # Normalize path for SQL
        demo_root = demo_root.replace("\\", "/")
        
        cursor = conn.cursor()
        
        # Check if we have any projects with placeholders
        # We need to ensure the table exists first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        if not cursor.fetchone():
            return

        cursor.execute("SELECT count(*) FROM projects WHERE source_path LIKE '%{{DEMO_ROOT}}%'")
        if cursor.fetchone()[0] == 0:
            return

        print(f"[INFO] Hydrating demo paths to: {demo_root}")
        
        # Update projects table
        cursor.execute("UPDATE projects SET source_path = REPLACE(source_path, '{{DEMO_ROOT}}', ?)", (demo_root,))
        
        # Update project_files table (if it exists and has file_path)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_files'")
        if cursor.fetchone():
            cursor.execute("UPDATE project_files SET file_path = REPLACE(file_path, '{{DEMO_ROOT}}', ?)", (demo_root,))
            
        conn.commit()
        print("[INFO] Demo paths hydrated successfully.")
        
    except Exception as e:
        print(f"[ERROR] Failed to fix demo paths: {e}")

def initialize_database():
    """
    Checks if the database exists in AppData. If not, initializes it from seed_data.sql.
    """
    db_path = app_settings.DATABASE_PATH
    projects_db_path = app_settings.PROJECTS_DB_PATH
    resource_dir = app_settings.RESOURCE_DIR
    
    # 1. Main Database
    if not os.path.exists(db_path):
        seed_main = os.path.join(resource_dir, "data", "seed_data_main.sql")
        if os.path.exists(seed_main):
            print(f"[INFO] Initializing Main DB from {seed_main}")
            try:
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                conn = sqlite3.connect(db_path)
                with open(seed_main, 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
                conn.close()
            except Exception as e:
                print(f"[ERROR] Failed to initialize Main DB: {e}")
        else:
            print(f"[WARNING] Main DB not found and no seed data at {seed_main}")

    # 2. Projects Database
    if not os.path.exists(projects_db_path):
        seed_projects = os.path.join(resource_dir, "data", "seed_data_projects.sql")
        if os.path.exists(seed_projects):
            print(f"[INFO] Initializing Projects DB from {seed_projects}")
            try:
                os.makedirs(os.path.dirname(projects_db_path), exist_ok=True)
                conn = sqlite3.connect(projects_db_path)
                with open(seed_projects, 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
                
                # Fix paths
                fix_demo_paths(conn)
                conn.close()
            except Exception as e:
                print(f"[ERROR] Failed to initialize Projects DB: {e}")
        else:
             print(f"[WARNING] Projects DB not found and no seed data at {seed_projects}")
