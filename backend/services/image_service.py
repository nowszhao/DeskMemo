import os
import shutil
from datetime import datetime
from PIL import Image
import imagehash
from typing import Optional, Tuple
from backend.config import settings


class ImageService:
    """图片处理服务"""
    
    def __init__(self):
        os.makedirs(settings.screenshot_path, exist_ok=True)
        os.makedirs(os.path.join(settings.screenshot_path, "thumbnails"), exist_ok=True)
    
    def save_screenshot(self, file_content: bytes, original_filename: str) -> Tuple[str, str, dict]:
        """
        保存截屏并生成缩略图
        
        Returns:
            (filename, filepath, metadata)
        """
        # 生成唯一文件名（统一使用 JPEG 格式，兼容 AI 服务）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}.jpg"
        filepath = os.path.join(settings.screenshot_path, filename)
        
        # 打开图片（可能是 WebP 或 JPEG）
        from io import BytesIO
        img = Image.open(BytesIO(file_content))
        
        # 转换 RGBA 到 RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        
        # 调整大小
        if width > settings.screenshot_max_width or height > settings.screenshot_max_height:
            img.thumbnail((settings.screenshot_max_width, settings.screenshot_max_height), Image.Resampling.LANCZOS)
            width, height = img.size
        
        # 保存为 JPEG（兼容 AI 服务）
        img.save(filepath, format='JPEG', quality=settings.screenshot_quality, optimize=True)
        
        # 生成缩略图
        thumbnail_path = self.create_thumbnail(img, filename)
        
        # 计算感知哈希
        phash = str(imagehash.phash(img))
        
        # 获取文件大小
        file_size = os.path.getsize(filepath)
        
        metadata = {
            "width": width,
            "height": height,
            "file_size": file_size,
            "phash": phash
        }
        
        return filename, filepath, metadata
    
    def create_thumbnail(self, img: Image.Image, filename: str) -> str:
        """创建缩略图（使用 JPEG 格式保持兼容性）"""
        thumbnail = img.copy()
        thumbnail.thumbnail((300, 200), Image.Resampling.LANCZOS)
        
        # 缩略图使用 JPEG（兼容性更好）
        thumbnail_filename = f"thumb_{filename}"
        thumbnail_path = os.path.join(settings.screenshot_path, "thumbnails", thumbnail_filename)
        thumbnail.save(thumbnail_path, format='JPEG', quality=70, optimize=True)
        
        return thumbnail_path
    
    def calculate_similarity(self, hash1: str, hash2: str) -> int:
        """计算两个感知哈希的差异度"""
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        return h1 - h2
    
    def compress_image(self, filepath: str, quality: int = 60) -> None:
        """压缩图片（用于长期存储）"""
        img = Image.open(filepath)
        img.save(filepath, quality=quality, optimize=True)
    
    def delete_image(self, filepath: str, thumbnail_path: Optional[str] = None) -> None:
        """删除图片文件"""
        if os.path.exists(filepath):
            os.remove(filepath)
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)


image_service = ImageService()
