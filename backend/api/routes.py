from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os

from backend.database import get_db
from backend.models import Screenshot, Activity, Report
from backend.services.image_service import image_service
from backend.services.vector_service import vector_service
from backend.tasks.processor import screenshot_processor
from backend.utils.timezone import beijing_naive, parse_date_beijing, get_day_range_beijing, format_beijing_time

router = APIRouter()


@router.post("/upload")
async def upload_screenshot(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传截屏"""
    try:
        # 读取文件内容
        content = await file.read()
        
        # 保存图片
        filename, filepath, metadata = image_service.save_screenshot(content, file.filename)
        
        # 检查相似度
        is_similar = False
        last_screenshot = db.query(Screenshot).order_by(Screenshot.timestamp.desc()).first()
        if last_screenshot and last_screenshot.phash:
            similarity = image_service.calculate_similarity(metadata["phash"], last_screenshot.phash)
            is_similar = similarity < settings.similarity_threshold
        
        # 保存到数据库
        screenshot = Screenshot(
            filename=filename,
            filepath=filepath,
            thumbnail_path=os.path.join(settings.screenshot_path, "thumbnails", f"thumb_{filename}"),
            width=metadata["width"],
            height=metadata["height"],
            file_size=metadata["file_size"],
            phash=metadata["phash"],
            is_similar=is_similar
        )
        
        db.add(screenshot)
        db.commit()
        db.refresh(screenshot)
        
        # 如果不是相似图片，立即加入分析队列
        if not is_similar:
            await screenshot_processor.add_to_queue(screenshot.id)
        
        return {
            "success": True,
            "screenshot_id": screenshot.id,
            "filename": filename,
            "is_similar": is_similar
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/screenshots")
async def get_screenshots(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取截屏列表"""
    query = db.query(Screenshot)
    
    if start_date:
        start = parse_date_beijing(start_date)
        query = query.filter(Screenshot.timestamp >= start)
    
    if end_date:
        end = parse_date_beijing(end_date)
        query = query.filter(Screenshot.timestamp <= end)
    
    total = query.count()
    screenshots = query.order_by(Screenshot.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": s.id,
                "filename": s.filename,
                "thumbnail_url": f"/files/thumbnails/thumb_{s.filename}",
                "timestamp": s.timestamp.isoformat(),
                "is_analyzed": s.is_analyzed,
                "is_similar": s.is_similar
            }
            for s in screenshots
        ]
    }


@router.get("/activities")
async def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    activity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取活动列表"""
    query = db.query(Activity)
    
    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)
    
    if start_date:
        start = parse_date_beijing(start_date)
        query = query.filter(Activity.timestamp >= start)
    
    if end_date:
        end = parse_date_beijing(end_date)
        query = query.filter(Activity.timestamp <= end)
    
    total = query.count()
    activities = query.order_by(Activity.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": a.id,
                "screenshot_id": a.screenshot_id,
                "screenshot_filename": a.screenshot_filename,
                "timestamp": a.timestamp.isoformat(),
                "activity_type": a.activity_type,
                "description": a.description,
                "application": a.application,
                "content_summary": a.content_summary
            }
            for a in activities
        ]
    }


@router.get("/search")
async def search_activities(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """搜索活动（关键词搜索为主，语义搜索为辅）"""
    
    # 关键词搜索（主要搜索方式）
    keyword_results = db.query(Activity).filter(
        (Activity.description.like(f"%{q}%")) |
        (Activity.content_summary.like(f"%{q}%")) |
        (Activity.application.like(f"%{q}%")) |
        (Activity.activity_type.like(f"%{q}%")) |
        (Activity.ocr_text.like(f"%{q}%"))
    ).order_by(Activity.timestamp.desc()).limit(limit * 2).all()
    
    # 语义搜索（辅助，用于发现相关内容）
    vector_results = vector_service.search_similar(q, limit=limit)
    
    # 合并结果
    results = []
    seen_ids = set()
    
    # 先添加关键词搜索结果（优先级高）
    for activity in keyword_results:
        if activity.id not in seen_ids:
            # 计算匹配度
            q_lower = q.lower()
            score = 0.0
            
            # 精确匹配加分
            if activity.description and q_lower in activity.description.lower():
                score += 0.4
            if activity.content_summary and q_lower in activity.content_summary.lower():
                score += 0.3
            if activity.application and q_lower in activity.application.lower():
                score += 0.2
            if activity.activity_type and q_lower in activity.activity_type.lower():
                score += 0.1
                
            results.append({
                "id": activity.id,
                "screenshot_id": activity.screenshot_id,
                "screenshot_filename": activity.screenshot_filename,
                "timestamp": activity.timestamp.isoformat(),
                "activity_type": activity.activity_type,
                "description": activity.description,
                "application": activity.application,
                "content_summary": activity.content_summary,
                "relevance": "keyword",
                "score": min(1.0, 0.6 + score)  # 基础分 0.6 + 匹配加分
            })
            seen_ids.add(activity.id)
    
    # 添加语义搜索结果（只添加未匹配的）
    for vr in vector_results:
        # cosine distance: 0 = 完全相同, 2 = 完全相反
        similarity = 1 - (vr["distance"] / 2)
        
        # 只保留较高相似度的语义结果
        if similarity < 0.5:
            continue
            
        activity_id = int(vr["id"].split("_")[1]) if "_" in vr["id"] else 0
        if activity_id and activity_id not in seen_ids:
            activity = db.query(Activity).filter(Activity.id == activity_id).first()
            if activity:
                results.append({
                    "id": activity.id,
                    "screenshot_id": activity.screenshot_id,
                    "screenshot_filename": activity.screenshot_filename,
                    "timestamp": activity.timestamp.isoformat(),
                    "activity_type": activity.activity_type,
                    "description": activity.description,
                    "application": activity.application,
                    "content_summary": activity.content_summary,
                    "relevance": "semantic",
                    "score": round(similarity * 0.8, 3)  # 语义搜索分数打折
                })
                seen_ids.add(activity_id)
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "query": q,
        "total": len(results),
        "items": results[:limit]
    }


@router.get("/reports/hourly")
async def get_hourly_reports(
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取小时报告"""
    query = db.query(Report).filter(Report.report_type == "hourly")
    
    if date:
        # 使用北京时间解析日期
        start_time, end_time = get_day_range_beijing(parse_date_beijing(date))
        query = query.filter(Report.start_time >= start_time, Report.start_time < end_time)
    else:
        # 默认获取今天的（北京时间）
        start_time, end_time = get_day_range_beijing()
        query = query.filter(Report.start_time >= start_time, Report.start_time < end_time)
    
    reports = query.order_by(Report.start_time.desc()).all()
    
    return {
        "total": len(reports),
        "items": [
            {
                "id": r.id,
                "start_time": r.start_time.isoformat(),
                "end_time": r.end_time.isoformat(),
                "summary": r.summary,
                "screenshot_count": r.screenshot_count,
                "work_minutes": r.work_minutes,
                "entertainment_minutes": r.entertainment_minutes,
                "study_minutes": r.study_minutes,
                "other_minutes": r.other_minutes
            }
            for r in reports
        ]
    }


@router.get("/reports/daily")
async def get_daily_reports(
    limit: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """获取日报"""
    reports = db.query(Report).filter(
        Report.report_type == "daily"
    ).order_by(Report.start_time.desc()).limit(limit).all()
    
    return {
        "total": len(reports),
        "items": [
            {
                "id": r.id,
                "date": r.start_time.date().isoformat(),
                "summary": r.summary,
                "screenshot_count": r.screenshot_count,
                "work_minutes": r.work_minutes,
                "entertainment_minutes": r.entertainment_minutes,
                "study_minutes": r.study_minutes,
                "other_minutes": r.other_minutes,
                "time_distribution": r.time_distribution
            }
            for r in reports
        ]
    }


@router.get("/stats/today")
async def get_today_stats(db: Session = Depends(get_db)):
    """获取今日统计"""
    start_time, end_time = get_day_range_beijing()
    
    # 截屏数量
    screenshot_count = db.query(Screenshot).filter(
        Screenshot.timestamp >= start_time,
        Screenshot.timestamp < end_time
    ).count()
    
    # 活动统计
    activities = db.query(Activity).filter(
        Activity.timestamp >= start_time,
        Activity.timestamp < end_time
    ).all()
    
    activity_type_counts = {}
    for a in activities:
        t = a.activity_type or "其他"
        activity_type_counts[t] = activity_type_counts.get(t, 0) + 1
    
    return {
        "date": start_time.date().isoformat(),
        "screenshot_count": screenshot_count,
        "activity_count": len(activities),
        "activity_distribution": activity_type_counts,
        "analyzed_count": db.query(Screenshot).filter(
            Screenshot.timestamp >= start_time,
            Screenshot.timestamp < end_time,
            Screenshot.is_analyzed == True
        ).count()
    }
