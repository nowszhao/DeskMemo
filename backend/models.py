from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from backend.utils.timezone import beijing_naive

Base = declarative_base()


class Screenshot(Base):
    """截屏记录模型"""
    __tablename__ = "screenshots"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), unique=True, nullable=False)
    filepath = Column(String(512), nullable=False)
    thumbnail_path = Column(String(512), nullable=True)
    timestamp = Column(DateTime, default=beijing_naive, index=True)
    width = Column(Integer)
    height = Column(Integer)
    file_size = Column(Integer)
    phash = Column(String(64), index=True)  # 感知哈希值
    is_similar = Column(Boolean, default=False)  # 是否与前一张相似
    is_analyzed = Column(Boolean, default=False, index=True)  # 是否已分析
    analysis_failed_count = Column(Integer, default=0)  # 分析失败次数
    last_analysis_error = Column(Text, nullable=True)  # 最后一次错误信息
    created_at = Column(DateTime, default=beijing_naive)


class Activity(Base):
    """活动解析结果模型"""
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    screenshot_id = Column(Integer, index=True)
    screenshot_filename = Column(String(255))
    timestamp = Column(DateTime, index=True)
    
    # AI 解析结果
    activity_type = Column(String(100))  # 工作/娱乐/学习/其他
    description = Column(Text)  # 活动描述
    application = Column(String(255))  # 应用程序
    content_summary = Column(Text)  # 内容摘要
    
    # OCR 文本
    ocr_text = Column(Text, nullable=True)
    
    # 向量ID（用于语义搜索）
    vector_id = Column(String(100), index=True)
    
    created_at = Column(DateTime, default=beijing_naive)


class Report(Base):
    """报告模型（小时报告、日报）"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(20), index=True)  # hourly/daily
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)
    
    # 报告内容
    summary = Column(Text)  # 总结
    main_activities = Column(Text)  # 主要活动（JSON格式）
    time_distribution = Column(Text)  # 时间分布（JSON格式）
    screenshot_count = Column(Integer)
    
    # 统计数据
    work_minutes = Column(Integer, default=0)
    entertainment_minutes = Column(Integer, default=0)
    study_minutes = Column(Integer, default=0)
    other_minutes = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=beijing_naive)
