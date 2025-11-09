"""手动触发 API - 用于测试和调试"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.tasks.processor import screenshot_processor
from backend.database import get_db
from backend.models import Screenshot

trigger_router = APIRouter()


@trigger_router.post("/trigger-analysis")
async def trigger_analysis():
    """手动触发截屏分析处理"""
    try:
        await screenshot_processor.process_pending_screenshots()
        return {"success": True, "message": "AI analysis triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trigger_router.post("/retry-failed")
async def retry_failed_screenshots(db: Session = Depends(get_db)):
    """重试失败的截图分析（重置失败计数）"""
    try:
        # 查找分析失败但未放弃的截图（failed_count > 0 且 is_analyzed = False）
        failed_screenshots = db.query(Screenshot).filter(
            Screenshot.is_analyzed == False,
            Screenshot.analysis_failed_count > 0
        ).all()
        
        # 重置失败计数，让它们重新尝试
        reset_count = 0
        for screenshot in failed_screenshots:
            screenshot.analysis_failed_count = 0
            screenshot.last_analysis_error = None
            reset_count += 1
        
        db.commit()
        
        # 触发分析
        if reset_count > 0:
            await screenshot_processor.process_pending_screenshots()
        
        return {
            "success": True,
            "message": f"Reset {reset_count} failed screenshots and triggered analysis"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trigger_router.get("/failed-screenshots")
async def get_failed_screenshots(db: Session = Depends(get_db)):
    """获取分析失败的截图列表"""
    try:
        # 查找所有失败过的截图
        failed = db.query(Screenshot).filter(
            Screenshot.analysis_failed_count > 0
        ).order_by(Screenshot.timestamp.desc()).limit(50).all()
        
        return {
            "total": len(failed),
            "items": [
                {
                    "id": s.id,
                    "filename": s.filename,
                    "timestamp": s.timestamp.isoformat(),
                    "failed_count": s.analysis_failed_count,
                    "last_error": s.last_analysis_error,
                    "is_analyzed": s.is_analyzed,
                    "status": "abandoned" if s.is_analyzed else "will_retry"
                }
                for s in failed
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
