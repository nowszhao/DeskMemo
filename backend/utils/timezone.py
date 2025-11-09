"""
时区工具模块
统一使用北京时间（UTC+8）
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

# 北京时区
BEIJING_TZ = timezone(timedelta(hours=8))


def now_beijing() -> datetime:
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)


def utc_to_beijing(utc_dt: datetime) -> datetime:
    """将 UTC 时间转换为北京时间"""
    if utc_dt.tzinfo is None:
        # 如果没有时区信息，假设是 UTC
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(BEIJING_TZ)


def beijing_to_utc(beijing_dt: datetime) -> datetime:
    """将北京时间转换为 UTC 时间"""
    if beijing_dt.tzinfo is None:
        # 如果没有时区信息，假设是北京时间
        beijing_dt = beijing_dt.replace(tzinfo=BEIJING_TZ)
    return beijing_dt.astimezone(timezone.utc)


def naive_to_beijing(naive_dt: datetime) -> datetime:
    """将 naive datetime 转换为北京时间（假设输入是北京时间）"""
    return naive_dt.replace(tzinfo=BEIJING_TZ)


def beijing_naive() -> datetime:
    """获取当前北京时间的 naive datetime（用于数据库存储）"""
    return now_beijing().replace(tzinfo=None)


def format_beijing_time(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化北京时间"""
    if dt.tzinfo is None:
        # 假设是北京时间
        dt = naive_to_beijing(dt)
    else:
        # 转换为北京时间
        dt = dt.astimezone(BEIJING_TZ)
    return dt.strftime(format_str)


def parse_date_beijing(date_str: str) -> datetime:
    """解析日期字符串为北京时间"""
    try:
        # 尝试解析 ISO 格式
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.astimezone(BEIJING_TZ)
        else:
            # 假设是日期格式 YYYY-MM-DD
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return naive_to_beijing(dt)
    except ValueError:
        # 回退到当前时间
        return now_beijing()


def get_hour_range_beijing(target_hour: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """获取指定小时的开始和结束时间（北京时间）"""
    if target_hour is None:
        # 获取上一小时
        current = now_beijing()
        target_hour = current.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    
    start_time = target_hour.replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    # 返回 naive datetime（用于数据库查询）
    return start_time.replace(tzinfo=None), end_time.replace(tzinfo=None)


def get_day_range_beijing(target_date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """获取指定日期的开始和结束时间（北京时间）"""
    if target_date is None:
        # 获取昨天
        target_date = (now_beijing() - timedelta(days=1)).date()
    elif isinstance(target_date, datetime):
        target_date = target_date.date()
    
    start_time = datetime.combine(target_date, datetime.min.time())
    end_time = start_time + timedelta(days=1)
    
    # 返回 naive datetime（用于数据库查询）
    return start_time, end_time