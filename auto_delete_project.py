#!/usr/bin/env python3
"""
自动删除指定项目的所有数据库记录
"""
import sqlite3
import os

DB_PATH = r"j:\V3_Mod_Localization_Factory\data\projects.sqlite"
PROJECT_NAME = "蕾姆丝计划演示mod：最后的罗马人"

print(f"数据库路径: {DB_PATH}")
print(f"要删除的项目: {PROJECT_NAME}\n")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查找项目
    cursor.execute("SELECT project_id, name FROM projects WHERE name = ?", (PROJECT_NAME,))
    projects = cursor.fetchall()
    
    if not projects:
        print(f"❌ 未找到项目 '{PROJECT_NAME}'")
        conn.close()
        exit(1)
    
    for project_id, name in projects:
        print(f"找到项目: {name}")
        print(f"项目ID: {project_id}\n")
        
        # 删除关联的文件记录
        cursor.execute("SELECT COUNT(*) FROM project_files WHERE project_id = ?", (project_id,))
        file_count = cursor.fetchone()[0]
        print(f"关联文件记录数: {file_count}")
        
        if file_count > 0:
            cursor.execute("DELETE FROM project_files WHERE project_id = ?", (project_id,))
            print(f"✅ 已删除 {file_count} 个文件记录")
        
        # 删除项目记录
        cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
        print(f"✅ 已删除项目记录")
    
    conn.commit()
    print(f"\n🎉 成功删除项目 '{PROJECT_NAME}' 的所有记录！")
    print("现在可以重新创建该项目了。")
    
except Exception as e:
    print(f"❌ 删除失败: {e}")
    conn.rollback()
finally:
    conn.close()
