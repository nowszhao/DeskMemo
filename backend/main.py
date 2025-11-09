import os
# 禁用 ChromaDB 遥测（必须在导入任何 chromadb 相关模块之前设置）
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import logging

from backend.config import settings
from backend.database import init_db
from backend.api import routes
from backend.api.manual_trigger import trigger_router
from backend.api.auth import auth_router, verify_token
from backend.tasks.processor import screenshot_processor, report_generator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建调度器
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting DeskMemo backend...")
    
    # 初始化数据库
    init_db()
    logger.info("Database initialized")
    
    # 确保存储目录存在
    os.makedirs(settings.storage_path, exist_ok=True)
    os.makedirs(settings.screenshot_path, exist_ok=True)
    
    # 启动截屏处理器（异步队列模式）
    await screenshot_processor.start()
    logger.info("Screenshot processor started")
    
    # 启动定时任务（仅保留报告生成）
    # 每小时生成一次小时报告（在每小时的第5分钟）
    scheduler.add_job(
        report_generator.generate_hourly_report,
        'cron',
        minute=5,
        id='hourly_report'
    )
    
    # 每天凌晨1点生成日报
    scheduler.add_job(
        report_generator.generate_daily_report,
        'cron',
        hour=1,
        minute=0,
        id='daily_report'
    )
    
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # 关闭时
    await screenshot_processor.stop()
    logger.info("Screenshot processor stopped")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


# 创建应用
app = FastAPI(
    title="DeskMemo API",
    description="桌面记忆系统 - 后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
if os.path.exists(settings.screenshot_path):
    app.mount("/files", StaticFiles(directory=settings.screenshot_path), name="files")

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
# 需要认证的路由（如果启用了密码保护）
app.include_router(routes.router, prefix="/api", tags=["api"], dependencies=[Depends(verify_token)])
app.include_router(trigger_router, prefix="/api", tags=["trigger"], dependencies=[Depends(verify_token)])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "DeskMemo API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "scheduler": scheduler.running
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
