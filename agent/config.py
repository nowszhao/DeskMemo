from pydantic_settings import BaseSettings
from typing import Optional
import os


class AgentSettings(BaseSettings):
    """Agent 客户端配置"""
    # 后端服务器地址
    agent_server_url: str = "http://localhost:8000"
    
    # Authentication
    agent_auth_password: Optional[str] = None
    
    # Screenshot
    screenshot_interval: int = 60
    # 优化压缩参数：quality=60 + progressive + optimize
    screenshot_quality: int = 60
    # 降低分辨率以减小文件（对 AI 分析足够）
    screenshot_max_width: int = 1024
    screenshot_max_height: int = 640
    
    class Config:
        # 从 agent 目录下的 .env 文件读取
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        case_sensitive = False


agent_settings = AgentSettings()
