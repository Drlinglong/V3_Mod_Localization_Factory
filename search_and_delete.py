#!/usr/bin/env python3
"""
在所有数据库中搜索并删除指定项目
"""
import sqlite3
import os

DATA_DIR = r"j:\V3_Mod_Localization_Factory\data"
PROJECT_NAME = "蕾姆丝计划演示mod：最后的罗马人"

db_files = ["database.sqlite", "mods_cache.sqlite", "projects.db", "projects.sqlite"]

for db_file in db_files:
    db_path = os.path.join(DATA_DIR, db_file)
    if not os.path.exists(db_path):
        continue
    
    print(f"\n{'='*60}")
    print(f"检查数据库: {db_file}")
    print(f"{'='*60}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"表: {[t[0] for t in tables]}")
        
        # 搜索项目记录
        found_any = False
        for table_name in [t[0] for t in tables]:
            if table_name == 'sqlite_sequence':
                continue
                
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            
            # 查找可能包含项目名的列
            search_cols = [c for c in col_names if any(k in c.lower() for k in ['name', 'project', 'path'])]
            
            for col_name in search_cols:
                try:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE {col_name} LIKE ?", (f"%{PROJECT_NAME}%",))
                    rows = cursor.fetchall()
                    if rows:
                        found_any = True
                        print(f"\n找到 {len(rows)} 条记录在 '{table_name}.{col_name}':")
                        print(f"列: {col_names}")
                        for row in rows:
                            print(f"  {row}")
                        
                        # 询问是否删除
                        print(f"\n是否删除这些记录? (yes/no)")
                        response = input().strip().lower()
                        if response == 'yes':
                            # 假设第一列是主键
                            pk_col = col_names[0]
                            for row in rows:
                                pk_value = row[0]
                                cursor.execute(f"DELETE FROM {table_name} WHERE {pk_col} = ?", (pk_value,))
                            conn.commit()
                            print(f"✅ 已删除 {len(rows)} 条记录")
                except Exception as e:
                    pass
        
        if not found_any:
            print("未找到相关记录")
        
        conn.close()
    except Exception as e:
        print(f"错误: {e}")

print(f"\n{'='*60}")
print("搜索完成")
