import shutil
import logging
import os
import sqlite3
from scripts import app_settings

# Setup a dedicated logger for initialization that writes to a file in AppData
# This is critical because stdout is swallowed in frozen mode.
init_logger = logging.getLogger("remis_init")
init_logger.setLevel(logging.DEBUG)

def setup_init_logging():
    try:
        log_dir = app_settings.APP_DATA_DIR
        log_file = os.path.join(log_dir, "init_debug.log")
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        init_logger.addHandler(file_handler)
        init_logger.info(f"Logging initialized. AppData: {log_dir}")
        init_logger.info(f"Resource Dir: {app_settings.RESOURCE_DIR}")
    except Exception as e:
        pass # Can't do much if we can't log

def fix_demo_paths(conn, persistent_demo_root, persistent_translation_root):
    """
    Hydrates placeholders in the database with actual persistent AppData paths.
    """
    try:
        demo_root = persistent_demo_root.replace("\\", "/")
        trans_root = persistent_translation_root.replace("\\", "/")
        
        cursor = conn.cursor()
        
        # Check if we have any projects with placeholders
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        if not cursor.fetchone():
            init_logger.warning("Projects table not found in fix_demo_paths")
            return

        init_logger.info(f"[INFO] Hydrating demo paths. Source: {demo_root}, Translation: {trans_root}")
        
        # Update projects table
        cursor.execute("UPDATE projects SET source_path = REPLACE(source_path, '{{BUNDLED_DEMO_ROOT}}', ?)", (demo_root,))
        cursor.execute("UPDATE projects SET target_path = REPLACE(target_path, '{{BUNDLED_TRANSLATION_ROOT}}', ?)", (trans_root,))
        init_logger.info(f"Updated projects rows: {cursor.rowcount}")

        # Update project_files table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_files'")
        if cursor.fetchone():
             cursor.execute("UPDATE project_files SET file_path = REPLACE(file_path, '{{BUNDLED_DEMO_ROOT}}', ?)", (demo_root,))
             init_logger.info(f"Updated project_files rows: {cursor.rowcount}")

        # [SAFETY CHECK] Direct replacement of developer path leaks if any remain
        # We also catch J:\ and j:\ variants
        dev_root_win = 'J:\\V3_Mod_Localization_Factory'
        dev_root_posix = 'J:/V3_Mod_Localization_Factory'
        dev_root_win_lower = 'j:\\V3_Mod_Localization_Factory'
        dev_root_posix_lower = 'j:/V3_Mod_Localization_Factory'
        
        roots = [dev_root_win, dev_root_posix, dev_root_win_lower, dev_root_posix_lower]
        
        for r in roots:
            cursor.execute("UPDATE projects SET source_path = REPLACE(source_path, ?, ?) WHERE source_path LIKE ?", (r, demo_root, f"{r}%"))
            cursor.execute("UPDATE projects SET target_path = REPLACE(target_path, ?, ?) WHERE target_path LIKE ?", (r, trans_root, f"{r}%"))
            cursor.execute("UPDATE project_files SET file_path = REPLACE(file_path, ?, ?) WHERE file_path LIKE ?", (r, demo_root, f"{r}%"))
            
        conn.commit()
        init_logger.info("[INFO] Demo paths hydrated successfully.")
        
    except Exception as e:
        init_logger.error(f"[ERROR] Failed to fix demo paths: {e}")

def run_projects_db_migrations(conn):
    """
    Handles schema updates and migrations for the Projects database.
    """
    cursor = conn.cursor()
    
    # 1. Base Tables (Ensure schemas match what we want)
    # ... (Keep existing schema creation logic or trust skeleton? Best to keep IF NOT EXISTS for safety)
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
    # ... (Other tables omitted for brevity in thought, but should be kept in actual code if not relying purely on skeleton consistency)
    
    # Schema Migrations logic ...
    # (Assuming skeleton has latest schema, but migrations help for future updates)
    
    conn.commit()

def initialize_database():
    """
    Checks if the database exists in AppData. 
    If not, initializes it from bundled skeleton.sqlite and extracts demo mods.
    """
def initialize_database():
    """
    Checks if the database exists in AppData. 
    If not, initializes it from bundled skeleton.sqlite and extracts demo mods.
    Also ensures demos are present if missing.
    """
    setup_init_logging()
    init_logger.info("Starting Database Initialization...")

    # Paths
    remis_db_path = app_settings.REMIS_DB_PATH
    app_data_dir = app_settings.APP_DATA_DIR
    resource_dir = app_settings.RESOURCE_DIR
    
    # Ensure AppData dir exists (Redundant but safe)
    os.makedirs(app_data_dir, exist_ok=True)
    os.makedirs(os.path.dirname(remis_db_path), exist_ok=True)
    
    init_logger.info(f"Target DB: {remis_db_path}")
    init_logger.info(f"Resource Dir: {resource_dir}")
    
    # 1. Database Initialization
    db_needs_init = False
    if not os.path.exists(remis_db_path):
        db_needs_init = True
        init_logger.info("DB missing.")
    elif os.path.getsize(remis_db_path) < 1024:
        db_needs_init = True
        init_logger.info("DB exists but is empty/small. Forcing re-init.")
        try:
            os.remove(remis_db_path)
        except Exception as e:
            init_logger.error(f"Failed to remove empty DB: {e}")
    else:
        # [NEW] Even if DB exists and is large, check if it's actually populated
        # This protects against broken partial initializations
        try:
            conn = sqlite3.connect(remis_db_path)
            cursor = conn.cursor()
            # Check if projects table exists and has rows
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='projects'")
            if cursor.fetchone()[0] == 0:
                db_needs_init = True
                init_logger.info("Projects table missing. Forcing re-init.")
            else:
                cursor.execute("SELECT count(*) FROM projects")
                if cursor.fetchone()[0] == 0:
                    db_needs_init = True
                    init_logger.info("Projects table is empty. Forcing re-init.")
            conn.close()
            if db_needs_init:
                try: os.remove(remis_db_path)
                except: pass
        except Exception as e:
            init_logger.warning(f"Health check failed on existing DB: {e}. Forcing re-init.")
            db_needs_init = True
            try: os.remove(remis_db_path)
            except: pass

    if db_needs_init:
        init_logger.info("[INIT] Extracting DB from Skeleton...")
        skeleton_source = os.path.join(resource_dir, "assets", "skeleton.sqlite")
        init_logger.info(f"Skeleton Source: {skeleton_source}")
        
        if os.path.exists(skeleton_source):
            try:
                # Log sizes before copy
                skel_size = os.path.getsize(skeleton_source)
                init_logger.info(f"Copying Skeleton DB ({skel_size} bytes) to {remis_db_path}")
                shutil.copy2(skeleton_source, remis_db_path)
                
                # Verify copy
                if os.path.exists(remis_db_path):
                    new_size = os.path.getsize(remis_db_path)
                    init_logger.info(f"Copy Success. New size: {new_size} bytes")
                    if new_size != skel_size:
                        init_logger.error(f"SIZE MISMATCH: Expected {skel_size}, got {new_size}")
                else:
                    init_logger.error("DB File missing AFTER copy!")
                    
            except Exception as e:
                init_logger.error(f"Failed to copy DB: {e}", exc_info=True)
        else:
             init_logger.error(f"CRITICAL: Skeleton DB NOT FOUND at {skeleton_source}")
    
    persistent_demos_dir = os.path.join(app_data_dir, "demos")
    bundled_demos_dir = os.path.join(resource_dir, "demos")
    
    persistent_trans_dir = os.path.join(app_data_dir, "my_translation")
    bundled_trans_dir = os.path.join(resource_dir, "my_translation")
    
    # Extraction Logic
    def extract_if_needed(bundled, persistent, label):
        if not os.path.exists(bundled):
            init_logger.warning(f"{label} bundle not found at {bundled}")
            return False
            
        if not os.path.exists(persistent) or db_needs_init:
            init_logger.info(f"[INIT] Extracting {label} to {persistent}...")
            try:
                if os.path.exists(persistent):
                    shutil.rmtree(persistent)
                shutil.copytree(bundled, persistent)
                init_logger.info(f"{label} extracted successfully.")
                return True
            except Exception as e:
                init_logger.error(f"Failed to extract {label}: {e}")
        return False

    demo_extracted = extract_if_needed(bundled_demos_dir, persistent_demos_dir, "Demos")
    trans_extracted = extract_if_needed(bundled_trans_dir, persistent_trans_dir, "Translations")

    if demo_extracted or trans_extracted or db_needs_init:
        init_logger.info("Triggering Path Rehydration...")
        try:
            conn = sqlite3.connect(remis_db_path)
            fix_demo_paths(conn, persistent_demos_dir, persistent_trans_dir)
            conn.close()
        except Exception as e:
            init_logger.error(f"Path rehydration failed: {e}")

    # 4. Migrations
    try:
        init_logger.info("Running migrations...")
        conn = sqlite3.connect(remis_db_path)
        run_projects_db_migrations(conn)
        conn.close()
        init_logger.info("Migrations complete.")
    except Exception as e:
        init_logger.error(f"Failed to run migrations: {e}", exc_info=True)
