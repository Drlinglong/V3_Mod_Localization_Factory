import sqlite3
import os

DB_PATH = os.path.join("data", "mods_cache.sqlite")

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Checking translated_entries with JOIN ---")
    try:
        mod_name = "Test_Project_Remis_Vic3"
        
        # 1. Find Mod ID
        cursor.execute("SELECT mod_id FROM mods WHERE name = ?", (mod_name,))
        mod_row = cursor.fetchone()
        if not mod_row:
            print(f"Mod '{mod_name}' not found in DB.")
            return
        mod_id = mod_row[0]
        print(f"Mod ID: {mod_id}")

        # 2. Find Latest Version ID
        cursor.execute("SELECT version_id FROM source_versions WHERE mod_id = ? ORDER BY created_at DESC LIMIT 1", (mod_id,))
        ver_row = cursor.fetchone()
        if not ver_row:
            print("No source version found.")
            return
        version_id = ver_row[0]
        print(f"Version ID: {version_id}")

        # 3. Check entries
        # We want to see what languages are stored for the files in this version
        cursor.execute("""
            SELECT s.file_path, t.language_code, COUNT(*)
            FROM source_entries s
            LEFT JOIN translated_entries t ON s.source_entry_id = t.source_entry_id
            WHERE s.version_id = ?
            GROUP BY s.file_path, t.language_code
        """, (version_id,))
        
        rows = cursor.fetchall()
        print("\n--- Translation Counts per File/Lang ---")
        for row in rows:
            file_path = row[0]
            lang = row[1]
            count = row[2]
            print(f"File: {file_path}, Lang: {lang}, Count: {count}")
            
        # 4. Sample check for English
        print("\n--- Sample English Translations ---")
        cursor.execute("""
            SELECT s.entry_key, t.translated_text
            FROM source_entries s
            JOIN translated_entries t ON s.source_entry_id = t.source_entry_id
            WHERE s.version_id = ? AND t.language_code = 'en'
            LIMIT 3
        """, (version_id,))
        samples = cursor.fetchall()
        for s in samples:
            print(f"Key: {s[0]}, Trans: {s[1]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
