import sqlite3
import json

try:
    conn = sqlite3.connect('data/database.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("--- All Glossaries ---")
    cursor.execute("SELECT glossary_id, game_id, name FROM glossaries")
    for row in cursor.fetchall():
        print(dict(row))
        
    print("\n--- Stellaris Glossaries ---")
    cursor.execute("SELECT * FROM glossaries WHERE game_id = 'stellaris'")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} glossaries for 'stellaris'")
    for row in rows:
        print(dict(row))
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
