import sqlite3
import os

DB_PATH = r"j:\V3_Mod_Localization_Factory\data\projects.sqlite"
TARGET_PATH = r"J:\V3_Mod_Localization_Factory\source_mod\Test_Project_Remis_Vic3"

def clean_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print(f"Cleaning up records for path: {TARGET_PATH}")
        
        # 1. Find all project_ids associated with this path (or subpaths)
        # Check projects table source_path
        cursor.execute("SELECT project_id, name FROM projects WHERE source_path LIKE ?", (f"%{TARGET_PATH}%",))
        projects = cursor.fetchall()
        
        project_ids = set([p[0] for p in projects])
        
        # 2. Find all project_ids associated with files in this path
        cursor.execute("SELECT DISTINCT project_id FROM project_files WHERE file_path LIKE ?", (f"%{TARGET_PATH}%",))
        file_project_ids = cursor.fetchall()
        for pid in file_project_ids:
            project_ids.add(pid[0])
            
        print(f"Found {len(project_ids)} related project IDs: {project_ids}")
        
        for pid in project_ids:
            print(f"Deleting project_id: {pid}")
            
            # Delete files
            cursor.execute("DELETE FROM project_files WHERE project_id = ?", (pid,))
            print(f"  - Deleted {cursor.rowcount} files")
            
            # Delete project
            cursor.execute("DELETE FROM projects WHERE project_id = ?", (pid,))
            print(f"  - Deleted {cursor.rowcount} project record")
            
        conn.commit()
        print("Cleanup complete.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_db()
