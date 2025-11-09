# 快速启动指南

## 一键启动（推荐）

### macOS / Linux

```bash
# 给脚本执行权限（首次运行）
chmod +x start_all.sh

# 启动所有服务
./start_all.sh
```

这将自动启动：
1. 后端服务（端口 8000）
2. 前端界面（端口 3000）
3. 截屏 Agent

启动脚本会自动创建虚拟环境、安装依赖、生成配置文件。

## 手动启动

如果一键启动失败，可以分别在三个终端中运行：

### 终端 1 - 后端服务

```bash
cd backend
./start.sh
```

首次运行会自动：
- 创建虚拟环境
- 安装依赖（从 `backend/requirements.txt`）
- 从 `backend/.env.example` 创建 `backend/.env`

### 终端 2 - 前端界面

```bash
cd frontend
./start.sh
```

首次运行会自动安装 npm 依赖。

### 终端 3 - 截屏 Agent

```bash
cd agent
./start.sh
```

首次运行会自动：
- 安装依赖（从 `agent/requirements.txt`）
- 从 `agent/.env.example` 创建 `agent/.env`

## 配置文件位置

配置文件已模块化，分散在各子项目目录：

- **后端**：`backend/.env`（从 `backend/.env.example` 复制）
- **Agent**：`agent/.env`（从 `agent/.env.example` 复制）
- **前端**：`frontend/.env.local`（可选，从 `frontend/.env.example` 复制）

## 验证服务

**后端服务**：
```bash
curl http://localhost:8000/health
```
应返回：`{"status":"healthy","scheduler":true}`

**前端界面**：
浏览器访问 http://localhost:3000

**AI 服务**：
```bash
curl http://9.208.244.74:8080/v1/models
```

## 常见问题

### 1. 端口被占用

修改 `backend/.env`：
```env
BACKEND_PORT=8001
```

前端端口在 `frontend/package.json` 中修改 `proxy` 字段。

### 2. Python 依赖安装失败

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 前端依赖安装失败

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 4. 截屏权限问题（macOS）

macOS 需要授予屏幕录制权限：
1. 系统设置 -> 隐私与安全性 -> 屏幕录制
2. 添加终端或 Python 应用
3. 重启 Agent

### 5. 配置文件位置错误

确保配置文件在正确的位置：
- ✅ `backend/.env`（不是根目录的 `.env`）
- ✅ `agent/.env`（不是根目录的 `.env`）

### 6. AI 分析不工作

检查 `backend/.env` 中的 `AI_IMAGE_SERVER` 配置：
- 本地开发：`http://localhost:8000/files`
- 生产环境：`http://YOUR_SERVER_IP:8000/files`

## 停止服务

**使用 tmux 启动的**：
```bash
tmux kill-session -t deskmemo
```

**手动启动的**：
在每个终端按 `Ctrl+C`

## 下一步

1. 访问 http://localhost:3000 查看界面
2. 等待 Agent 开始截屏（默认每分钟一次）
3. 等待后台处理器分析图片（每 5 分钟扫描一次）
4. 在仪表盘查看统计数据
5. 使用搜索功能查找历史活动

## 生产部署

请参考 `DEPLOYMENT.md` 获取详细的生产环境部署指南。

## 数据目录

所有数据存储在 `storage/` 目录（相对于项目根目录）：
```
storage/
├── screenshots/        # 截屏图片
│   └── thumbnails/    # 缩略图
├── chroma_data/       # 向量数据库
└── deskmemo.db       # SQLite 数据库
```

定期备份此目录即可保存所有数据。
