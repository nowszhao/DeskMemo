#!/usr/bin/env python3
"""调试今日统计数据问题"""

import sys
sys.path.insert(0, '.')

from backend.database import SessionLocal
from backend.models import Screenshot, Activity
from backend.utils.timezone import get_day_range_beijing, beijing_naive
from datetime import datetime

def debug_stats():
    db = SessionLocal()
    
    print("=" * 60)
    print("调试今日统计数据")
    print("=" * 60)
    
    # 当前北京时间
    now_beijing = beijing_naive()
    print(f"\n当前北京时间: {now_beijing}")
    
    # 今日时间范围（北京时间）
    start_time, end_time = get_day_range_beijing()
    print(f"今日范围: {start_time} ~ {end_time}")
    
    # 数据库中所有截图
    all_screenshots = db.query(Screenshot).all()
    print(f"\n数据库总截图数: {len(all_screenshots)}")
    
    if all_screenshots:
        print("\n最近5条截图时间:")
        for s in all_screenshots[-5:]:
            print(f"  - ID: {s.id}, 时间: {s.timestamp}, 文件: {s.filename}")
    
    # 今日截图
    today_screenshots = db.query(Screenshot).filter(
        Screenshot.timestamp >= start_time,
        Screenshot.timestamp < end_time
    ).all()
    print(f"\n今日截图数: {len(today_screenshots)}")
    
    if today_screenshots:
        print("今日截图:")
        for s in today_screenshots:
            print(f"  - ID: {s.id}, 时间: {s.timestamp}")
    
    # 所有活动
    all_activities = db.query(Activity).all()
    print(f"\n数据库总活动数: {len(all_activities)}")
    
    if all_activities:
        print("\n最近5条活动时间:")
        for a in all_activities[-5:]:
            print(f"  - ID: {a.id}, 时间: {a.timestamp}, 类型: {a.activity_type}")
    
    # 今日活动
    today_activities = db.query(Activity).filter(
        Activity.timestamp >= start_time,
        Activity.timestamp < end_time
    ).all()
    print(f"\n今日活动数: {len(today_activities)}")
    
    if today_activities:
        print("今日活动:")
        for a in today_activities:
            print(f"  - ID: {a.id}, 时间: {a.timestamp}, 类型: {a.activity_type}")
    
    # 分析时区问题
    if all_screenshots and not today_screenshots:
        print("\n⚠️  问题分析:")
        print("数据库有截图但查询不到今日数据，可能是时区问题！")
        print("\n建议:")
        print("1. 运行时区迁移脚本: python backend/migrations/timezone_migration.py")
        print("2. 或者等待 agent 上传新的截图（新截图会使用正确的北京时间）")
    
    db.close()

if __name__ == "__main__":
    debug_stats()
