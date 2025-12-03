import sqlite3
import os

DB_PATH = r"j:\V3_Mod_Localization_Factory\data\projects.sqlite"

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check total counts
        cursor.execute("SELECT COUNT(*) FROM projects")
        p_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM project_files")
        f_count = cursor.fetchone()[0]
        
        print(f"Total Projects: {p_count}")
        print(f"Total Files: {f_count}")
        
        # Check for any files that might be related to the path
        target_path = r"J:\V3_Mod_Localization_Factory\source_mod\Test_Project_Remis_Vic3"
        print(f"\nChecking for files with path like: {target_path}")
        
        cursor.execute("SELECT file_id, file_path, project_id FROM project_files WHERE file_path LIKE ?", (f"%{target_path}%",))
        rows = cursor.fetchall()
        
        if rows:
            print(f"Found {len(rows)} lingering files!")
            for row in rows[:5]:
                print(row)
        else:
            print("No files found matching that path.")

        # Check for any projects with the name
        name = "蕾姆丝计划演示mod：最后的罗马人"
        cursor.execute("SELECT * FROM projects WHERE name = ?", (name,))
        p_rows = cursor.fetchall()
        if p_rows:
            print(f"\nFound project record: {p_rows}")
        else:
            print(f"\nNo project record found for name: {name}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
