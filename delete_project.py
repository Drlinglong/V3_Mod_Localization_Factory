#!/usr/bin/env python3
"""
删除指定项目的数据库记录
"""
import sqlite3
import sys

DB_PATH = r"j:\V3_Mod_Localization_Factory\data\database.sqlite"
PROJECT_NAME = "蕾姆丝计划演示mod：最后的罗马人"

def delete_project(project_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查找项目
        cursor.execute("SELECT project_id, name FROM projects WHERE name LIKE ?", (f"%{project_name}%",))
        projects = cursor.fetchall()
        
        if not projects:
            print(f"未找到名称包含 '{project_name}' 的项目")
            return
        
        for project_id, name in projects:
            print(f"找到项目: {name} (ID: {project_id})")
            
            # 删除相关文件记录
            cursor.execute("DELETE FROM project_files WHERE project_id = ?", (project_id,))
            deleted_files = cursor.rowcount
            print(f"  - 删除了 {deleted_files} 个文件记录")
            
            # 删除项目记录
            cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            print(f"  - 删除了项目记录")
        
        conn.commit()
        print(f"\n✅ 成功删除项目 '{project_name}' 的所有记录")
        
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"数据库路径: {DB_PATH}")
    print(f"要删除的项目: {PROJECT_NAME}\n")
    delete_project(PROJECT_NAME)
