#!/usr/bin/env python3
"""
桌面截屏 Agent
定期截取活动窗口并上传到后端服务器
"""
import time
import sys
import os
import subprocess
import tempfile
from datetime import datetime
from io import BytesIO
import logging

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mss import mss
from PIL import Image
import httpx
from agent.config import agent_settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScreenshotAgent:
    """截屏代理"""
    
    def __init__(self):
        self.server_url = agent_settings.agent_server_url
        self.auth_password = agent_settings.agent_auth_password
        self.interval = agent_settings.screenshot_interval
        self.quality = agent_settings.screenshot_quality
        self.max_width = agent_settings.screenshot_max_width
        self.max_height = agent_settings.screenshot_max_height
        self.running = False
        # macOS 默认支持 AppleScript
        self.use_active_window = sys.platform == 'darwin'
        # 认证 token
        self.auth_token = None
        
        logger.info(f"Screenshot Agent initialized")
        logger.info(f"Server: {self.server_url}")
        logger.info(f"Interval: {self.interval}s")
        logger.info(f"Auth enabled: {bool(self.auth_password)}")
        logger.info(f"Capture mode: {'Active Window (AppleScript)' if self.use_active_window else 'Full Screen'}")
    
    def get_active_window_id(self) -> tuple[int, str]:
        """获取当前活动窗口 ID 和应用名称（使用 AppleScript）"""
        try:
            script = '''
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set appName to name of frontApp
                set windowID to id of front window of frontApp
            end tell
            return appName & "|" & windowID
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if '|' in output:
                    app_name, window_id = output.split('|', 1)
                    return int(window_id), app_name
        except Exception as e:
            logger.warning(f"Failed to get active window info: {e}")
        return None, None
    
    def capture_active_window_applescript(self) -> tuple[BytesIO, str]:
        """使用 macOS screencapture 工具捕获活动窗口（非交互式）"""
        window_id, app_name = self.get_active_window_id()
        
        if not window_id or not app_name:
            logger.warning("No active window found, capturing full screen")
            return self.capture_full_screen()
        
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            # 使用 screencapture -l <window_id> 直接截取指定窗口（非交互式）
            result = subprocess.run(
                ['screencapture', '-o', '-x', '-l', str(window_id), tmp_path],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0 and os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                # 读取并处理图片
                img = Image.open(tmp_path)
                
                # 删除临时文件
                os.unlink(tmp_path)
                
                # 转换为 RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 调整大小
                if img.width > self.max_width or img.height > self.max_height:
                    img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)
                
                # 保存到内存（优化压缩）
                buffer = BytesIO()
                # Progressive JPEG + optimize = 更小文件
                img.save(buffer, format='JPEG', quality=self.quality, optimize=True, progressive=True)
                buffer.seek(0)
                
                logger.info(f"Captured active window: {app_name} ({img.width}x{img.height})")
                return buffer, app_name
            else:
                logger.warning(f"screencapture failed (window_id: {window_id}), falling back to full screen")
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return self.capture_full_screen()
                
        except Exception as e:
            logger.error(f"Error capturing active window: {e}")
            # 清理临时文件
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return self.capture_full_screen()
    
    def capture_full_screen(self) -> tuple[BytesIO, str]:
        """捕获全屏（备用方案）"""
        with mss() as sct:
            # 捕获主显示器
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            
            # 转换为 PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            
            # 调整大小
            if img.width > self.max_width or img.height > self.max_height:
                img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)
            
            # 保存到内存（使用 JPEG 格式，但优化压缩参数）
            buffer = BytesIO()
            # Progressive JPEG + 优化 = 更小文件
            img.save(buffer, format='JPEG', quality=self.quality, optimize=True, progressive=True)
            buffer.seek(0)
            
            logger.info(f"Captured full screen ({img.width}x{img.height})")
            return buffer, "Desktop"
    
    def capture_screenshot(self) -> tuple[BytesIO, str]:
        """捕获屏幕截图"""
        if self.use_active_window:
            return self.capture_active_window_applescript()
        else:
            return self.capture_full_screen()
    
    async def login(self) -> bool:
        """登录并获取 token"""
        if not self.auth_password:
            # 未配置密码，不需要登录
            return True
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.server_url}/api/auth/login",
                    json={"password": self.auth_password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.auth_token = data.get("token")
                        logger.info("Authentication successful")
                        return True
                    else:
                        logger.error(f"Login failed: {data.get('message')}")
                        return False
                else:
                    logger.error(f"Login failed: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False
    
    def get_auth_headers(self) -> dict:
        """获取认证请求头"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def upload_screenshot(self, image_buffer: BytesIO, app_name: str = None) -> bool:
        """上传截图到服务器"""
        try:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {'file': (filename, image_buffer, 'image/jpeg')}
                data = {}
                if app_name:
                    data['app_name'] = app_name
                
                response = await client.post(
                    f"{self.server_url}/api/upload",
                    files=files,
                    data=data,
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Upload successful: {result.get('filename')} (similar: {result.get('is_similar')}, app: {app_name})")
                    return True
                elif response.status_code == 401:
                    logger.warning("Authentication expired, attempting to re-login...")
                    # 尝试重新登录
                    if await self.login():
                        # 重试上传
                        response = await client.post(
                            f"{self.server_url}/api/upload",
                            files=files,
                            data=data,
                            headers=self.get_auth_headers()
                        )
                        if response.status_code == 200:
                            result = response.json()
                            logger.info(f"Upload successful after re-login: {result.get('filename')}")
                            return True
                    logger.error(f"Upload failed after re-login: {response.status_code} - {response.text}")
                    return False
                else:
                    logger.error(f"Upload failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error uploading screenshot: {str(e)}")
            return False
    
    async def run_once(self):
        """执行一次截屏和上传"""
        try:
            logger.info("Capturing screenshot...")
            image_buffer, app_name = self.capture_screenshot()
            
            logger.info(f"Uploading screenshot (app: {app_name})...")
            success = await self.upload_screenshot(image_buffer, app_name)
            
            return success
            
        except Exception as e:
            logger.error(f"Error in screenshot cycle: {str(e)}")
            return False
    
    async def run(self):
        """运行代理（持续模式）"""
        self.running = True
        logger.info("Screenshot Agent started")
        
        try:
            while self.running:
                await self.run_once()
                
                # 等待下一次截屏
                logger.info(f"Waiting {self.interval} seconds until next screenshot...")
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.running = False
            logger.info("Screenshot Agent stopped")
    
    def stop(self):
        """停止代理"""
        self.running = False


async def main():
    """主函数"""
    agent = ScreenshotAgent()
    
    # 测试连接
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{agent.server_url}/health")
            if response.status_code == 200:
                logger.info("Server connection OK")
            else:
                logger.warning(f"Server returned status {response.status_code}")
    except Exception as e:
        logger.error(f"Cannot connect to server: {str(e)}")
        logger.error("Please make sure the backend server is running")
        return
    
    # 如果启用认证，先登录
    if agent.auth_password:
        logger.info("Authentication required, logging in...")
        if not await agent.login():
            logger.error("Login failed, cannot start agent")
            return
    
    # 运行代理
    await agent.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
