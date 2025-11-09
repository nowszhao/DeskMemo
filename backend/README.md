# DeskMemo Backend

后端服务，提供 API、AI 解析、数据存储等功能。

## 快速启动

```bash
# 方式一：使用启动脚本（推荐）
./start.sh

# 方式二：手动启动
cd ..  # 回到项目根目录
python -m backend.main
```

## 配置

复制配置文件并编辑：
```bash
cp .env.example .env
nano .env
```

### 关键配置项

**本地开发**：
```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
AI_IMAGE_SERVER=http://localhost:8000/files
```

**生产环境**：
```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
AI_IMAGE_SERVER=http://YOUR_SERVER_IP:8000/files
# 或使用域名
# AI_IMAGE_SERVER=http://your-domain.com/files
```

## 依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- FastAPI - Web 框架
- SQLAlchemy - 数据库 ORM
- ChromaDB - 向量数据库
- APScheduler - 定时任务

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 目录结构

```
backend/
├── api/              # API 路由
├── services/         # 业务逻辑
├── tasks/            # 后台任务
├── config.py         # 配置
├── database.py       # 数据库
├── models.py         # 数据模型
├── main.py          # 入口
├── requirements.txt  # 依赖
└── .env             # 配置文件
```

## 开发

```bash
# 热重载模式
uvicorn backend.main:app --reload

# 指定端口
uvicorn backend.main:app --port 8001
```

## 生产部署

参考根目录的 `DEPLOYMENT.md` 文档。
