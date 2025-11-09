from pydantic_settings import BaseSettings
from typing import Optional
import os


class ServerSettings(BaseSettings):
    """后端服务器配置"""
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # AI Model
    ai_api_url: str = "http://9.208.244.74:8080/v1/chat/completions"
    ai_model_name: str = "Qwen3-VL-2B-Instruct"
    ai_max_tokens: int = 500
    ai_image_server: str = "http://localhost:8000/files"  # AI 访问图片的 URL
    
    # Storage (使用绝对路径)
    storage_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
    screenshot_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "screenshots")
    database_url: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage', 'deskmemo.db')}"
    
    # Vector Database
    chroma_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "chroma_data")
    
    # Image Processing
    screenshot_quality: int = 85
    screenshot_max_width: int = 1920
    screenshot_max_height: int = 1080
    similarity_threshold: int = 10
    
    # Retention
    retain_original_days: int = 7
    retain_compressed_days: int = 30
    
    # Authentication
    auth_password: Optional[str] = None
    
    class Config:
        # 从 backend 目录下的 .env 文件读取
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        case_sensitive = False


# 后端服务配置实例
settings = ServerSettings()

print(f"Config: {settings.dict()}")