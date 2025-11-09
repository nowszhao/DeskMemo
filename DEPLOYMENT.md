# 部署指南

本文档说明如何在不同场景下部署 DeskMemo 系统。

## 场景说明

DeskMemo 包含三个组件：
1. **后端服务**：处理数据、调用 AI、生成报告
2. **前端界面**：Web UI
3. **Agent 客户端**：定期截屏并上传

## 部署场景

### 场景一：本地开发（推荐新手）

所有组件都在本地 macOS 上运行。

**启动方式**：

```bash
# 一键启动
./start_all.sh

# 或分别启动
cd backend && ./start.sh   # 终端 1
cd frontend && ./start.sh  # 终端 2
cd agent && ./start.sh     # 终端 3
```

启动脚本会自动安装依赖和创建配置文件。

---

### 场景二：生产部署（Agent 在客户端，后端在服务器）

**架构**：
- Agent：运行在用户的 macOS 上
- 后端 + 前端：运行在服务器上
- AI 服务：独立的服务器

#### 步骤 1：部署后端服务（在服务器上）

```bash
# 1. 上传代码到服务器
scp -r DeskMemo user@your-server:/path/to/

# 2. SSH 到服务器
ssh user@your-server

# 3. 创建后端配置
cd /path/to/DeskMemo
cp backend/.env.example backend/.env

# 4. 编辑配置
nano backend/.env
```

**关键配置**（`backend/.env`）：
```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

AI_API_URL=http://9.208.244.74:8080/v1/chat/completions
AI_MODEL_NAME=Qwen3-VL-2B-Instruct

# 重要：AI 服务访问图片的 URL
# 替换为你的服务器公网 IP 或域名
AI_IMAGE_SERVER=http://YOUR_SERVER_IP:8000/files
```

```bash
# 5. 安装依赖并启动
cd backend
./start.sh

# 或手动启动
cd /path/to/DeskMemo
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
python -m backend.main

# 或使用 nohup 后台运行
nohup python -m backend.main > backend.log 2>&1 &
```

#### 步骤 2：部署前端（在服务器上）

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 构建生产版本
npm run build

# 3. 使用 Nginx 或其他 Web 服务器托管
# 将 build/ 目录配置到 Nginx
```

**Nginx 配置示例**：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        root /path/to/DeskMemo/frontend/build;
        try_files $uri /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态文件（截图）
    location /files {
        proxy_pass http://localhost:8000;
    }
}
```

#### 步骤 3：配置 Agent（在客户端 macOS 上）

```bash
# 1. 在 macOS 上克隆项目（只需要 agent 目录）
git clone <repo> DeskMemo
cd DeskMemo

# 2. 创建 Agent 配置
cp agent/.env.example agent/.env

# 3. 编辑配置，指向服务器地址
nano agent/.env
```

**Agent 配置**（`agent/.env`）：
```env
# 替换为你的服务器地址
AGENT_SERVER_URL=http://YOUR_SERVER_IP:8000
# 或使用域名
# AGENT_SERVER_URL=http://your-domain.com

SCREENSHOT_INTERVAL=60
SCREENSHOT_QUALITY=85
SCREENSHOT_MAX_WIDTH=1920
SCREENSHOT_MAX_HEIGHT=1080
```

```bash
# 4. 安装依赖并启动
cd agent
./start.sh

# 或手动安装
pip install -r agent/requirements.txt

# 5. 运行 Agent
python agent/screenshot_agent.py

# 6. 设置开机自启（可选，见下文）
```

---

### 场景三：AI 服务图片访问配置

AI 服务需要能访问到截图。有以下几种方案：

#### 方案 A：后端服务器有公网 IP（推荐）

**配置**（`.env`）：
```env
# AI 通过公网 IP 访问
AI_IMAGE_SERVER=http://YOUR_PUBLIC_IP:8000/files
```

确保防火墙开放 8000 端口。

#### 方案 B：使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /files {
        alias /path/to/DeskMemo/storage/screenshots;
        autoindex off;
    }
}
```

**配置**（`backend/.env`）：
```env
AI_IMAGE_SERVER=http://your-domain.com/files
```

#### 方案 C：上传图片到 AI 服务器

如果 AI 服务器（`9.208.244.74`）提供了文件上传接口：

1. 修改 `backend/services/image_service.py`，添加上传到 AI 服务器的逻辑
2. 配置（`backend/.env`）：
```env
AI_IMAGE_SERVER=http://9.208.244.74:9876
```

---

## 环境变量配置总结

配置文件已分散到各子项目目录，更加模块化：

### `backend/.env` - 后端服务器配置
- 位置：`backend/.env`
- 模板：`backend/.env.example`
- 关键配置：`AI_IMAGE_SERVER=http://YOUR_SERVER_IP:8000/files`

### `agent/.env` - Agent 客户端配置
- 位置：`agent/.env`
- 模板：`agent/.env.example`
- 关键配置：`AGENT_SERVER_URL=http://YOUR_SERVER_IP:8000`

### `frontend/.env.local` - 前端配置（可选）
- 位置：`frontend/.env.local`
- 模板：`frontend/.env.example`
- 关键配置：`REACT_APP_API_URL=http://YOUR_SERVER_IP:8000/api`

---

## 使用 systemd 管理后端服务（Linux）

创建 `/etc/systemd/system/deskmemo-backend.service`：

```ini
[Unit]
Description=DeskMemo Backend Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/DeskMemo
Environment="PATH=/path/to/DeskMemo/venv/bin"
ExecStart=/path/to/DeskMemo/venv/bin/python -m backend.main
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable deskmemo-backend
sudo systemctl start deskmemo-backend
sudo systemctl status deskmemo-backend
```

---

## macOS Agent 开机自启（launchd）

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
        <string>/usr/local/bin/python3</string>
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

加载：
```bash
launchctl load ~/Library/LaunchAgents/com.deskmemo.agent.plist
```

---

## 安全建议

1. **HTTPS**：生产环境使用 HTTPS（Let's Encrypt）
2. **认证**：添加 API 认证（JWT、API Key）
3. **防火墙**：只开放必要端口
4. **数据备份**：定期备份 `storage/` 目录
5. **隐私**：考虑添加敏感内容过滤

---

## 监控和日志

### 查看后端日志
```bash
# 如果使用 systemd
sudo journalctl -u deskmemo-backend -f

# 如果使用 nohup
tail -f backend.log
```

### 查看 Agent 日志
```bash
# macOS launchd
tail -f /tmp/deskmemo-agent.log
```

---

## 故障排除

### Agent 无法连接后端
```bash
# 测试连接
curl http://YOUR_SERVER_IP:8000/health

# 检查防火墙
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS
```

### AI 无法访问图片
```bash
# 从 AI 服务器测试
ssh user@9.208.244.74
curl http://YOUR_SERVER_IP:8000/files/screenshot_xxx.jpg
```

### 数据库锁定
```bash
# SQLite 并发问题，考虑升级到 PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/deskmemo
```

---

## 性能优化

1. **使用 PostgreSQL** 替代 SQLite（高并发）
2. **使用 Redis** 缓存频繁查询
3. **CDN** 分发静态资源
4. **负载均衡** 多个后端实例
5. **定期清理** 旧数据和图片

---

## 总结

- **本地开发**：运行 `./start_all.sh`，自动使用各子项目的配置文件
- **生产部署**：
  - 服务器：配置 `backend/.env`，设置 `AI_IMAGE_SERVER`
  - 客户端：配置 `agent/.env`，设置 `AGENT_SERVER_URL`
  - 前端：配置 `frontend/.env.local`（可选）
- **关键点**：确保 AI 服务能访问到图片 URL



# FAQ

# 创建临时目录
mkdir -p /data/tmp
mkdir -p /data/pip-cache

# 设置环境变量并安装
export TMPDIR=/data/tmp
export PIP_CACHE_DIR=/data/pip-cache

# 然后再安装
pip install -r requirements.txt
