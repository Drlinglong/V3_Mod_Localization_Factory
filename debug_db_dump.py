import sqlite3
from scripts.app_settings import PROJECTS_DB_PATH

def dump_projects():
    conn = sqlite3.connect(PROJECTS_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()
    
    print(f"--- Dumping Projects ({len(rows)}) ---")
    for row in rows:
        d = dict(row)
        print(f"Project: {d.get('name')} (ID: {d.get('project_id')})")
        print(f"  - game_id: '{d.get('game_id')}' (Type: {type(d.get('game_id'))})")
        print(f"  - source_language: '{d.get('source_language')}' (Type: {type(d.get('source_language'))})")
        print("-" * 20)

    conn.close()

if __name__ == "__main__":
    dump_projects()
