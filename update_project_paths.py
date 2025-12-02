#!/usr/bin/env python3
"""
Update project file paths after folder rename.
Changes all paths from 'simp_chinese' to 'english' in the database.
"""

import sqlite3
from pathlib import Path

def update_file_paths(db_path, project_id):
    """Update file paths in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all files for this project
    cursor.execute("SELECT file_id, file_path FROM project_files WHERE project_id = ?", (project_id,))
    files = cursor.fetchall()
    
    print(f"Found {len(files)} files in project {project_id}")
    
    updated = 0
    for file_id, file_path in files:
        if 'simp_chinese' in file_path:
            new_path = file_path.replace('simp_chinese', 'english')
            # Also update the language suffix if needed
            if '_l_english.yml' in new_path and 'english\\remis' in new_path:
                # Already correct
                cursor.execute("UPDATE project_files SET file_path = ? WHERE file_id = ?", (new_path, file_id))
                print(f"  Updated: {Path(file_path).name} -> {Path(new_path).name}")
                updated += 1
    
    conn.commit()
    conn.close()
    
    print(f"\nUpdated {updated} file paths")
    return updated

if __name__ == '__main__':
    db_path = Path(__file__).parent / 'data' / 'projects.sqlite'
    project_id = 'bbd299e7-694f-41d8-835c-0b9ef391d581'
    
    update_file_paths(db_path, project_id)
