import sqlite3
from scripts.app_settings import PROJECTS_DB_PATH

def fix_db():
    conn = sqlite3.connect(PROJECTS_DB_PATH)
    cursor = conn.cursor()
    
    # fix game_id: victoria3 -> vic3
    cursor.execute("UPDATE projects SET game_id = 'vic3' WHERE game_id = 'victoria3'")
    
    # fix source_language: zh-CN -> simp_chinese
    cursor.execute("UPDATE projects SET source_language = 'simp_chinese' WHERE source_language = 'zh-CN'")
    
    conn.commit()
    print(f"Updates committed. Rows affected: {conn.total_changes}")
    conn.close()

if __name__ == "__main__":
    fix_db()
