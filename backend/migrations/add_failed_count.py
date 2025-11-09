#!/usr/bin/env python3
"""
数据库迁移：添加失败计数字段

运行方式:
  python backend/migrations/add_failed_count.py
"""
import sqlite3
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config import settings

def migrate():
    """执行迁移"""
    # 从配置中提取数据库路径
    db_url = settings.database_url
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
    else:
        print(f"错误: 不支持的数据库类型: {db_url}")
        return False
    
    # 使数据库路径绝对化
    if not os.path.isabs(db_path):
        # 相对路径，相对于项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(project_root, db_path)
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    print(f"数据库路径: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(screenshots)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'analysis_failed_count' in columns:
            print("字段 'analysis_failed_count' 已存在，跳过迁移")
        else:
            print("添加字段 'analysis_failed_count'...")
            cursor.execute("ALTER TABLE screenshots ADD COLUMN analysis_failed_count INTEGER DEFAULT 0")
            print("✓ 字段 'analysis_failed_count' 添加成功")
        
        if 'last_analysis_error' in columns:
            print("字段 'last_analysis_error' 已存在，跳过迁移")
        else:
            print("添加字段 'last_analysis_error'...")
            cursor.execute("ALTER TABLE screenshots ADD COLUMN last_analysis_error TEXT")
            print("✓ 字段 'last_analysis_error' 添加成功")
        
        conn.commit()
        conn.close()
        
        print("\n迁移完成！")
        return True
        
    except Exception as e:
        print(f"迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
