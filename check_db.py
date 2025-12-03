#!/usr/bin/env python3
"""
查看数据库结构并删除指定项目
"""
import sqlite3

DB_PATH = r"j:\V3_Mod_Localization_Factory\data\database.sqlite"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

# 如果有项目相关的表，显示其记录
project_name = "蕾姆丝计划演示mod：最后的罗马人"
print(f"\n搜索包含 '{project_name}' 的记录...\n")

for table_name in [t[0] for t in tables]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    # 查找name列
    name_columns = [col[1] for col in columns if 'name' in col[1].lower()]
    
    if name_columns:
        for col_name in name_columns:
            try:
                cursor.execute(f"SELECT * FROM {table_name} WHERE {col_name} LIKE ?", (f"%{project_name}%",))
                rows = cursor.fetchall()
                if rows:
                    print(f"在表 '{table_name}' 的列 '{col_name}' 中找到 {len(rows)} 条记录:")
                    for row in rows:
                        print(f"  {row}")
            except:
                pass

conn.close()
