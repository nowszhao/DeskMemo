# DeskMemo Agent

桌面截屏客户端，**自动捕获活动窗口**并上传到后端服务器进行 AI 分析。

## ✨ 特性

- 🎯 **智能截图**：自动捕获当前活动窗口（而非整个桌面）
- 📱 **应用识别**：自动识别并记录正在使用的应用程序
- 🔄 **自动上传**：定期上传到后端进行 AI 分析
- 🎨 **图片优化**：自动压缩和调整尺寸
- 💾 **相似度检测**：避免重复上传相同内容

## 快速启动

```bash
# 方式一：使用启动脚本（推荐）
./start.sh

# 方式二：手动启动
cd ..  # 回到项目根目录
python agent/screenshot_agent.py
```

## 配置

复制配置文件并编辑：
```bash
cp .env.example .env
nano .env
```

### 配置项

**本地开发**（后端在本机）：
```env
AGENT_SERVER_URL=http://localhost:8000
SCREENSHOT_INTERVAL=60
```

**生产环境**（后端在服务器）：
```env
AGENT_SERVER_URL=http://YOUR_SERVER_IP:8000
# 或使用域名
# AGENT_SERVER_URL=http://your-domain.com

SCREENSHOT_INTERVAL=60
SCREENSHOT_QUALITY=85
SCREENSHOT_MAX_WIDTH=1920
SCREENSHOT_MAX_HEIGHT=1080
```

## 依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- mss - 高性能截屏（用于备用全屏模式）
- pyobjc-framework-Quartz - macOS 窗口捕获（活动窗口模式）
- Pillow - 图片处理
- httpx - HTTP 客户端

## 截图模式

### macOS - 活动窗口模式（默认）

在 macOS 上，Agent 会：
1. 自动检测当前活动的应用程序
2. 仅截取活动窗口（而非整个桌面）
3. 记录应用名称（如 Chrome、VSCode、Terminal 等）
4. 上传窗口截图及应用信息到后端

这样能更准确地反映你的实际工作内容。

### 其他系统 - 全屏模式

在非 macOS 系统上，会回退到全屏截图模式。

## macOS 权限

macOS 需要授予屏幕录制权限：

1. 系统设置 -> 隐私与安全性 -> 屏幕录制
2. 添加 终端 或 Python 应用
3. 重启 Agent

## 仅部署 Agent

如果只需要在客户端部署 Agent：

```bash
# 1. 只复制 agent 目录
scp -r agent user@client:/path/to/

# 2. 在客户端上
cd /path/to/agent
pip install -r requirements.txt
cp .env.example .env
nano .env  # 配置 AGENT_SERVER_URL

# 3. 运行
./start.sh
```

## 开机自启（macOS）

创建 `~/Library/LaunchAgents/com.deskmemo.agent.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.deskmemo.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/DeskMemo/agent/screenshot_agent.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/deskmemo-agent.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/deskmemo-agent-error.log</string>
</dict>
</plist>
```

加载服务：
```bash
launchctl load ~/Library/LaunchAgents/com.deskmemo.agent.plist
```

## 故障排除

### 无法连接后端
```bash
# 测试连接
curl http://YOUR_SERVER_IP:8000/health
```

### 权限问题
检查系统设置 -> 隐私与安全性 -> 屏幕录制

### 查看日志
如果使用 launchd：
```bash
tail -f /tmp/deskmemo-agent.log
```
