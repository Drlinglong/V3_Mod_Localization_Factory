import sqlite3
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.app_settings import PROJECT_ROOT

DB_PATH = f"{PROJECT_ROOT}/data/database.sqlite"

def check_glossaries():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        game_id = 'stellaris'
        print(f"Checking glossaries for game_id: {game_id}")
        
        cursor.execute("SELECT glossary_id, name, is_main FROM glossaries WHERE game_id = ?", (game_id,))
        rows = cursor.fetchall()
        
        if not rows:
            print("No glossaries found for this game.")
        else:
            print(f"Found {len(rows)} glossaries:")
            for row in rows:
                print(f"  ID: {row['glossary_id']}, Name: {row['name']}, is_main: {row['is_main']} (Type: {type(row['is_main'])})")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_glossaries()
