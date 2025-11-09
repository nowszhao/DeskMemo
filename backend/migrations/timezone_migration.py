#!/usr/bin/env python3
"""
时区迁移脚本
将现有数据库中的 UTC 时间转换为北京时间

注意：这个脚本假设现有数据是 UTC 时间，将其转换为北京时间（UTC+8）
如果现有数据已经是北京时间，请不要运行此脚本！
"""
import sys
import os
from datetime import datetime, timezone, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import Screenshot, Activity, Report

# 北京时区
BEIJING_TZ = timezone(timedelta(hours=8))


def convert_utc_to_beijing_naive(utc_dt: datetime) -> datetime:
    """将 UTC 时间转换为北京时间的 naive datetime"""
    if utc_dt is None:
        return None
    
    # 假设输入是 UTC 时间
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    # 转换为北京时间
    beijing_dt = utc_dt.astimezone(BEIJING_TZ)
    
    # 返回 naive datetime
    return beijing_dt.replace(tzinfo=None)


def migrate_timezone():
    """执行时区迁移"""
    db = SessionLocal()
    
    try:
        print("开始时区迁移...")
        
        # 迁移 Screenshot 表
        print("迁移 Screenshot 表...")
        screenshots = db.query(Screenshot).all()
        screenshot_count = 0
        
        for screenshot in screenshots:
            old_timestamp = screenshot.timestamp
            old_created_at = screenshot.created_at
            
            screenshot.timestamp = convert_utc_to_beijing_naive(old_timestamp)
            screenshot.created_at = convert_utc_to_beijing_naive(old_created_at)
            
            screenshot_count += 1
            
            if screenshot_count % 100 == 0:
                print(f"已处理 {screenshot_count} 个截图记录...")
        
        print(f"Screenshot 表迁移完成，共处理 {screenshot_count} 条记录")
        
        # 迁移 Activity 表
        print("迁移 Activity 表...")
        activities = db.query(Activity).all()
        activity_count = 0
        
        for activity in activities:
            old_timestamp = activity.timestamp
            old_created_at = activity.created_at
            
            activity.timestamp = convert_utc_to_beijing_naive(old_timestamp)
            activity.created_at = convert_utc_to_beijing_naive(old_created_at)
            
            activity_count += 1
            
            if activity_count % 100 == 0:
                print(f"已处理 {activity_count} 个活动记录...")
        
        print(f"Activity 表迁移完成，共处理 {activity_count} 条记录")
        
        # 迁移 Report 表
        print("迁移 Report 表...")
        reports = db.query(Report).all()
        report_count = 0
        
        for report in reports:
            old_start_time = report.start_time
            old_end_time = report.end_time
            old_created_at = report.created_at
            
            report.start_time = convert_utc_to_beijing_naive(old_start_time)
            report.end_time = convert_utc_to_beijing_naive(old_end_time)
            report.created_at = convert_utc_to_beijing_naive(old_created_at)
            
            report_count += 1
        
        print(f"Report 表迁移完成，共处理 {report_count} 条记录")
        
        # 提交更改
        db.commit()
        print("时区迁移完成！所有时间已转换为北京时间。")
        
        # 显示示例
        if screenshots:
            sample = screenshots[0]
            print(f"\n示例转换结果：")
            print(f"第一个截图的时间戳：{sample.timestamp}")
        
    except Exception as e:
        print(f"迁移过程中发生错误：{e}")
        db.rollback()
        raise
    finally:
        db.close()


def check_timezone_status():
    """检查数据库中的时区状态"""
    db = SessionLocal()
    
    try:
        # 检查最新的几条记录
        latest_screenshot = db.query(Screenshot).order_by(Screenshot.id.desc()).first()
        latest_activity = db.query(Activity).order_by(Activity.id.desc()).first()
        
        print("当前数据库时间状态：")
        
        if latest_screenshot:
            print(f"最新截图时间：{latest_screenshot.timestamp}")
            print(f"当前北京时间：{datetime.now()}")
            
            # 简单判断：如果截图时间比当前时间晚8小时以上，可能是UTC时间
            time_diff = datetime.now() - latest_screenshot.timestamp
            if time_diff.total_seconds() > 8 * 3600:
                print("⚠️  数据可能仍为 UTC 时间，建议运行迁移")
            else:
                print("✅ 数据可能已为北京时间")
        
        if latest_activity:
            print(f"最新活动时间：{latest_activity.timestamp}")
        
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_timezone_status()
    elif len(sys.argv) > 1 and sys.argv[1] == "--migrate":
        response = input("确认要执行时区迁移吗？这将修改所有现有数据的时间戳。(y/N): ")
        if response.lower() == 'y':
            migrate_timezone()
        else:
            print("迁移已取消")
    else:
        print("用法：")
        print("  python timezone_migration.py --check    # 检查当前时区状态")
        print("  python timezone_migration.py --migrate  # 执行时区迁移")
        print("")
        print("⚠️  警告：迁移会修改所有现有数据，请先备份数据库！")