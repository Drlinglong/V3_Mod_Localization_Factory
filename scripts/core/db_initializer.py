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

def run_projects_db_migrations(conn):
    """
    Handles schema updates and migrations for the Projects database.
    """
    cursor = conn.cursor()
    
    # 1. Base Tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            game_id TEXT NOT NULL,
            source_path TEXT NOT NULL,
            source_language TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TEXT,
            last_modified TEXT
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
    
    # 2. Schema Migrations (Structural updates)
    cursor.execute("PRAGMA table_info(projects)")
    p_cols = [info[1] for info in cursor.fetchall()]
    
    migrations = [
        ('last_modified', 'TEXT'),
        ('source_language', "TEXT DEFAULT 'english'"),
        ('created_at', 'TEXT'),
        ('last_activity_type', 'TEXT'),
        ('last_activity_desc', 'TEXT'),
        ('notes', 'TEXT')
    ]
    
    for col_name, col_type in migrations:
        if col_name not in p_cols:
            cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")

    cursor.execute("PRAGMA table_info(project_files)")
    pf_cols = [info[1] for info in cursor.fetchall()]
    
    if 'line_count' not in pf_cols:
        cursor.execute("ALTER TABLE project_files ADD COLUMN line_count INTEGER DEFAULT 0")
    if 'file_type' not in pf_cols:
        cursor.execute("ALTER TABLE project_files ADD COLUMN file_type TEXT DEFAULT 'source'")

    # 3. Data Migrations (Fixing defaults/orphans)
    cursor.execute("UPDATE projects SET last_modified = datetime('now') WHERE last_modified IS NULL")
    cursor.execute("UPDATE projects SET created_at = datetime('now') WHERE created_at IS NULL")
    cursor.execute("UPDATE projects SET source_language = 'english' WHERE source_language IS NULL")
    
    conn.commit()

def initialize_database():
    """
    Checks if the database exists in AppData. If not, initializes it from seed_data.sql.
    Also handles structural migrations for existing databases.
    """
    db_path = app_settings.DATABASE_PATH
    projects_db_path = app_settings.PROJECTS_DB_PATH
    resource_dir = app_settings.RESOURCE_DIR
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # 1. Main Database (Static assets & Glossaries)
    if not os.path.exists(db_path):
        seed_main = os.path.join(resource_dir, "data", "seed_data_main.sql")
        if os.path.exists(seed_main):
            print(f"[INFO] Initializing Main DB from {seed_main}")
            try:
                conn = sqlite3.connect(db_path)
                with open(seed_main, 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
                conn.close()
            except Exception as e:
                print(f"[ERROR] Failed to initialize Main DB: {e}")
        else:
            print(f"[WARNING] Main DB seed data not found at {seed_main}")

    # 2. Projects Database (User projects & Kanban)
    # This DB always undergoes migration check even if its new
    try:
        is_new = not os.path.exists(projects_db_path)
        conn = sqlite3.connect(projects_db_path)
        
        if is_new:
            seed_projects = os.path.join(resource_dir, "data", "seed_data_projects.sql")
            if os.path.exists(seed_projects):
                print(f"[INFO] Initializing Projects DB from {seed_projects}")
                with open(seed_projects, 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
                fix_demo_paths(conn)
            else:
                print(f"[WARNING] Projects DB seed data not found at {seed_projects}. Creating empty tables.")
        
        # Always run migrations to ensure schema is up-to-date
        run_projects_db_migrations(conn)
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to initialize/migrate Projects DB: {e}")
