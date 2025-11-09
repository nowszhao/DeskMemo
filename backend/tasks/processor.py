import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List
import json
import os

from backend.database import SessionLocal
from backend.models import Screenshot, Activity, Report
from backend.services.ai_service import ai_service
from backend.services.vector_service import vector_service
from backend.config import settings
from backend.utils.timezone import beijing_naive, get_hour_range_beijing, get_day_range_beijing

logger = logging.getLogger(__name__)


class ScreenshotProcessor:
    """截屏处理器 - 基于异步队列的持续处理"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processing_task = None
        self.running = False
        self.worker_lock = asyncio.Lock()
    
    async def start(self):
        """启动处理器"""
        if self.running:
            logger.warning("Processor is already running")
            return
        
        self.running = True
        
        # 扫描未分析的截图加入队列
        await self._scan_pending_screenshots()
        
        # 启动工作协程
        self.processing_task = asyncio.create_task(self._process_worker())
        
        # 启动定期扫描协程
        asyncio.create_task(self._periodic_scan())
        
        logger.info("Screenshot processor started")
    
    async def stop(self):
        """停止处理器"""
        self.running = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        logger.info("Screenshot processor stopped")
    
    async def add_to_queue(self, screenshot_id: int):
        """添加截图到处理队列"""
        await self.queue.put(screenshot_id)
        logger.info(f"Added screenshot {screenshot_id} to processing queue (queue size: {self.queue.qsize()})")
    
    async def _scan_pending_screenshots(self):
        """扫描未分析的截图（同时检查文件系统）"""
        db = SessionLocal()
        try:
            # 1. 查找数据库中未分析的截图
            screenshots = db.query(Screenshot).filter(
                Screenshot.is_analyzed == False,
                Screenshot.is_similar == False
            ).order_by(Screenshot.timestamp).all()
            
            valid_count = 0
            invalid_count = 0
            
            for screenshot in screenshots:
                # 检查文件是否存在
                if os.path.exists(screenshot.filepath):
                    await self.queue.put(screenshot.id)
                    valid_count += 1
                else:
                    # 文件不存在，标记为已分析避免重复检查
                    logger.warning(f"Screenshot file not found: {screenshot.filepath}, marking as analyzed")
                    screenshot.is_analyzed = True
                    invalid_count += 1
            
            if valid_count > 0:
                logger.info(f"Found {valid_count} pending screenshots (skipped {invalid_count} missing files)")
            elif screenshots:
                logger.info(f"Found {len(screenshots)} pending records, but all files are missing")
            else:
                logger.info("No pending screenshots found")
            
            # 提交数据库变更（标记缺失文件）
            if invalid_count > 0:
                db.commit()
                
        finally:
            db.close()
    
    async def _periodic_scan(self):
        """定期扫描未分析的截图（每5秒）"""
        while self.running:
            try:
                await asyncio.sleep(5)
                
                # 只在队列为空时扫描
                if self.queue.empty():
                    await self._scan_pending_screenshots()
            except Exception as e:
                logger.error(f"Error in periodic scan: {e}")
    
    async def _process_worker(self):
        """工作协程 - 串行处理队列中的截图"""
        logger.info("Processing worker started")
        
        while self.running:
            try:
                # 从队列获取任务（超时等待）
                try:
                    screenshot_id = await asyncio.wait_for(
                        self.queue.get(),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    # 超时继续循环
                    continue
                
                # 处理截图
                async with self.worker_lock:
                    db = SessionLocal()
                    try:
                        screenshot = db.query(Screenshot).filter(
                            Screenshot.id == screenshot_id
                        ).first()
                        
                        if screenshot:
                            logger.info(f"Processing screenshot {screenshot_id} (queue remaining: {self.queue.qsize()})")
                            await self._process_screenshot(db, screenshot)
                            db.commit()
                        else:
                            logger.warning(f"Screenshot {screenshot_id} not found")
                    except Exception as e:
                        logger.error(f"Error processing screenshot {screenshot_id}: {e}", exc_info=True)
                        db.rollback()
                    finally:
                        db.close()
                        self.queue.task_done()
                
            except asyncio.CancelledError:
                logger.info("Processing worker cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in worker: {e}", exc_info=True)
        
        logger.info("Processing worker stopped")
    
    async def _process_screenshot(self, db: Session, screenshot: Screenshot):
        """处理单个截屏"""
        try:
            # 构建图片 URL - AI 服务可以访问的地址
            image_url = f"{settings.ai_image_server}/{screenshot.filename}"
            
            logger.info(f"Analyzing screenshot: {screenshot.filename}, URL: {image_url}")
            
            # 调用 AI 分析
            result = await ai_service.analyze_screenshot(image_url)
            
            if result:
                # 创建活动记录
                activity = Activity(
                    screenshot_id=screenshot.id,
                    screenshot_filename=screenshot.filename,
                    timestamp=screenshot.timestamp,
                    activity_type=result.get("activity_type", "其他"),
                    description=result.get("description", ""),
                    application=result.get("application", "未知"),
                    content_summary=result.get("content_summary", ""),
                    vector_id=f"activity_{screenshot.id}"
                )
                
                db.add(activity)
                
                # 构建高质量的嵌入文本（增强语义信息）
                text_parts = []
                if activity.activity_type:
                    text_parts.append(f"活动类型：{activity.activity_type}")
                if activity.application:
                    text_parts.append(f"应用程序：{activity.application}")
                if activity.description:
                    text_parts.append(f"描述：{activity.description}")
                if activity.content_summary:
                    text_parts.append(f"内容：{activity.content_summary}")
                
                text_for_embedding = " ".join(text_parts)
                
                vector_service.add_activity(
                    activity.vector_id,
                    text_for_embedding,
                    {
                        "activity_id": screenshot.id,
                        "timestamp": screenshot.timestamp.isoformat(),
                        "activity_type": activity.activity_type
                    }
                )
                
                # 标记为已分析，清除失败记录
                screenshot.is_analyzed = True
                screenshot.analysis_failed_count = 0
                screenshot.last_analysis_error = None
                
                logger.info(f"Successfully analyzed: {screenshot.filename}")
            else:
                # 分析失败：增加失败计数
                screenshot.analysis_failed_count += 1
                screenshot.last_analysis_error = "AI returned no result"
                
                # 最多重试 3 次，超过后标记为已分析（放弃）
                if screenshot.analysis_failed_count >= 3:
                    screenshot.is_analyzed = True
                    logger.error(f"AI analysis failed {screenshot.analysis_failed_count} times, giving up: {screenshot.filename}")
                else:
                    logger.warning(f"AI analysis failed for: {screenshot.filename} (attempt {screenshot.analysis_failed_count}/3, will retry)")
                
        except Exception as e:
            # 异常处理：记录错误并增加失败计数
            error_msg = str(e)
            screenshot.analysis_failed_count += 1
            screenshot.last_analysis_error = error_msg[:500]  # 限制长度
            
            # 最多重试 3 次
            if screenshot.analysis_failed_count >= 3:
                screenshot.is_analyzed = True
                logger.error(f"Error processing screenshot {screenshot.filename} after {screenshot.analysis_failed_count} attempts, giving up: {error_msg}", exc_info=True)
            else:
                logger.error(f"Error processing screenshot {screenshot.filename} (attempt {screenshot.analysis_failed_count}/3): {error_msg}", exc_info=True)
    
    async def process_pending_screenshots(self):
        """兼容旧接口 - 立即扫描并加入队列"""
        await self._scan_pending_screenshots()
        return {"message": f"Queued {self.queue.qsize()} screenshots for processing"}


class ReportGenerator:
    """报告生成器 - 生成小时报告和日报"""
    
    async def generate_hourly_report(self, target_hour: datetime = None):
        """生成小时报告"""
        db = SessionLocal()
        try:
            # 使用北京时间计算小时范围
            start_time, end_time = get_hour_range_beijing(target_hour)
            
            # 检查是否已生成
            existing = db.query(Report).filter(
                Report.report_type == "hourly",
                Report.start_time == start_time
            ).first()
            
            if existing:
                logger.info(f"Hourly report already exists for {start_time}")
                return existing
            
            # 获取该小时的活动
            activities = db.query(Activity).filter(
                Activity.timestamp >= start_time,
                Activity.timestamp < end_time
            ).all()
            
            if not activities:
                logger.info(f"No activities for hour {start_time}")
                return None
            
            # 统计
            type_minutes = {"工作": 0, "学习": 0, "娱乐": 0, "其他": 0}
            for activity in activities:
                t = activity.activity_type or "其他"
                type_minutes[t] = type_minutes.get(t, 0) + 1  # 每个活动约1分钟
            
            # 生成摘要
            summary = await ai_service.generate_hourly_report(activities)
            
            # 创建报告
            report = Report(
                report_type="hourly",
                start_time=start_time,
                end_time=end_time,
                summary=summary,
                screenshot_count=len(activities),
                work_minutes=type_minutes.get("工作", 0),
                study_minutes=type_minutes.get("学习", 0),
                entertainment_minutes=type_minutes.get("娱乐", 0),
                other_minutes=type_minutes.get("其他", 0)
            )
            
            db.add(report)
            db.commit()
            db.refresh(report)
            
            logger.info(f"Generated hourly report for {start_time}")
            return report
            
        finally:
            db.close()
    
    async def generate_daily_report(self, target_date: datetime = None):
        """生成日报"""
        db = SessionLocal()
        try:
            if target_date is None:
                # 生成昨天的报告
                target_date = (datetime.now() - timedelta(days=1)).date()
            elif isinstance(target_date, datetime):
                target_date = target_date.date()
            
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = start_time + timedelta(days=1)
            
            # 检查是否已生成
            existing = db.query(Report).filter(
                Report.report_type == "daily",
                Report.start_time == start_time
            ).first()
            
            if existing:
                logger.info(f"Daily report already exists for {target_date}")
                return existing
            
            # 获取当天的活动
            activities = db.query(Activity).filter(
                Activity.timestamp >= start_time,
                Activity.timestamp < end_time
            ).all()
            
            if not activities:
                logger.info(f"No activities for date {target_date}")
                return None
            
            # 统计
            type_minutes = {"工作": 0, "学习": 0, "娱乐": 0, "其他": 0}
            type_counts = {}
            for activity in activities:
                t = activity.activity_type or "其他"
                type_minutes[t] = type_minutes.get(t, 0) + 1
                type_counts[t] = type_counts.get(t, 0) + 1
            
            # 生成摘要
            summary = await ai_service.generate_daily_report(activities)
            
            # 时间分布
            time_distribution = json.dumps(type_counts, ensure_ascii=False)
            
            # 创建报告
            report = Report(
                report_type="daily",
                start_time=start_time,
                end_time=end_time,
                summary=summary,
                screenshot_count=len(activities),
                work_minutes=type_minutes.get("工作", 0),
                study_minutes=type_minutes.get("学习", 0),
                entertainment_minutes=type_minutes.get("娱乐", 0),
                other_minutes=type_minutes.get("其他", 0),
                time_distribution=time_distribution
            )
            
            db.add(report)
            db.commit()
            db.refresh(report)
            
            logger.info(f"Generated daily report for {start_time.date()}")
            return report
            
        finally:
            db.close()


# 全局实例
screenshot_processor = ScreenshotProcessor()
report_generator = ReportGenerator()
