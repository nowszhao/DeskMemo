# 桌面记忆 DeskMemo

基于 AI 的桌面活动追踪和分析系统，自动记录、分析你的桌面活动，生成智能报告。

## 功能特性

- 🖥️ **自动截屏**：定时捕获桌面画面（默认每分钟一次）
- 🤖 **AI 分析**：使用视觉大模型解析截屏内容，识别活动类型
- 📊 **智能报告**：自动生成小时报告和日报
- 🔍 **语义搜索**：支持关键词和语义搜索历史活动
- 📈 **数据可视化**：直观展示时间分配和活动统计
- 💾 **本地存储**：数据完全本地化，保护隐私

## 技术栈

### 后端
- **FastAPI**：高性能 Python Web 框架
- **SQLAlchemy**：ORM 数据库管理
- **ChromaDB**：轻量级向量数据库，支持语义搜索
- **APScheduler**：定时任务调度
- **Pillow & ImageHash**：图片处理和相似度检测

### 前端
- **React 18**：现代化前端框架
- **DaisyUI**：基于 Tailwind CSS 的组件库
- **Recharts**：数据可视化图表库
- **Axios**：HTTP 客户端

### AI 服务
- **Qwen3-VL-2B-Instruct**：视觉语言大模型（已部署）

## 项目结构

```
DeskMemo/
├── agent/                    # 桌面截屏客户端 ⭐
│   ├── screenshot_agent.py
│   ├── config.py
│   ├── requirements.txt     # Agent 依赖
│   ├── start.sh            # Agent 启动脚本
│   ├── .env                # Agent 配置
│   ├── .env.example
│   ├── .gitignore
│   └── README.md           # Agent 文档
├── backend/                 # 后端服务 ⭐
│   ├── api/                # API 路由
│   ├── services/           # 业务逻辑
│   ├── tasks/              # 定时任务
│   ├── config.py           # 配置加载
│   ├── database.py         # 数据库
│   ├── models.py           # 数据模型
│   ├── main.py            # 入口
│   ├── requirements.txt    # 后端依赖
│   ├── start.sh           # 后端启动脚本
│   ├── .env               # 后端配置
│   ├── .env.example
│   ├── .gitignore
│   └── README.md          # 后端文档
├── frontend/               # Web 界面 ⭐
│   ├── public/
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API 服务
│   │   └── App.js
│   ├── package.json       # 前端依赖
│   ├── start.sh          # 前端启动脚本
│   ├── .env.example      # 前端配置示例
│   └── README.md         # 前端文档
├── storage/               # 数据存储（自动创建）
│   ├── screenshots/
│   ├── chroma_data/
│   └── deskmemo.db
├── requirements.txt       # 根目录说明文件
├── start_all.sh          # 一键启动所有服务
├── README.md             # 项目总文档
├── DEPLOYMENT.md         # 部署指南
└── QUICKSTART.md         # 快速开始
```

## 快速开始

### 1. 环境准备

**系统要求**：
- Python 3.8+
- Node.js 14+
- macOS / Linux / Windows

**克隆项目**：
```bash
git clone <repo> DeskMemo
cd DeskMemo
```

各子项目的依赖将在启动时自动安装。

### 2. 配置

**本地开发环境**（所有组件在本地运行）：

启动脚本会自动创建默认配置文件，无需手动配置。

如需自定义配置：
```bash
# 后端配置
cp backend/.env.example backend/.env
nano backend/.env

# Agent 配置
cp agent/.env.example agent/.env
nano agent/.env
```

**生产环境部署**（Agent 在客户端，后端在服务器）：

请参考 `DEPLOYMENT.md` 文档了解详细的部署配置。配置文件位于：
- 服务器端：`backend/.env`
- 客户端（macOS）：`agent/.env`
- 前端：`frontend/.env.local`（可选）

### 3. 启动服务

**方式一：一键启动所有服务（推荐）**
```bash
chmod +x start_all.sh
./start_all.sh
```

**方式二：分别启动各服务**
```bash
# 终端 1 - 后端
cd backend && ./start.sh

# 终端 2 - 前端
cd frontend && ./start.sh

# 终端 3 - Agent
cd agent && ./start.sh
```

启动脚本会自动：
- 创建虚拟环境
- 安装依赖
- 生成配置文件
- 启动服务

### 4. 访问应用

打开浏览器访问 http://localhost:3000

## 使用说明

### 仪表盘
- 查看今日活动统计
- 活动类型分布饼图
- 最近活动时间线

### 时间轴
- 浏览所有截屏记录
- 按日期筛选
- 点击查看大图

### 报告
- 查看小时报告和日报
- AI 生成的工作总结
- 时间分配统计

### 搜索
- 关键词搜索：搜索活动描述、应用名称
- 语义搜索：根据含义查找相关活动
- 查看匹配的截屏

## 工作原理

1. **截屏 Agent** 每隔设定时间（默认 1 分钟）自动截取桌面
2. 截图上传到后端，计算感知哈希值检测相似度
3. **后台处理器** 定期（每 5 分钟）扫描未分析的截图
4. 将图片发送给 AI 模型进行分析，识别活动类型和内容
5. 解析结果保存到数据库和向量数据库
6. **报告生成器** 定时生成小时报告（每小时第 5 分钟）和日报（每天凌晨 1 点）
7. 前端通过 API 查询和展示数据

## API 文档

后端服务启动后，访问 http://localhost:8000/docs 查看完整的 API 文档（Swagger UI）

## 注意事项

### 隐私保护
- 所有数据完全存储在本地
- 建议定期清理敏感截图
- 可以在工作时暂停 Agent 避免记录私密内容

### 性能优化
- 相似截图会被自动标记，减少 AI 分析次数
- 图片会自动压缩，节省存储空间
- 向量数据库支持快速语义搜索

### 存储管理
- 默认保留策略：
  - 7 天内：原始质量
  - 7-30 天：压缩图片
  - 30 天后：建议手动清理或仅保留报告

## 故障排除

**Agent 无法连接后端**：
- 确保后端服务已启动
- 检查 `.env` 中的 `AGENT_SERVER_URL` 配置

**AI 分析失败**：
- 确认 AI 服务可访问：`curl http://9.208.244.74:8080/v1/models`
- 检查图片是否成功上传到后端
- 查看后端日志：`python -m backend.main` 的输出

**前端无法加载数据**：
- 检查浏览器控制台错误信息
- 确认后端 API 正常：访问 http://localhost:8000/health
- 检查 CORS 配置

## 开发

**后端热重载**：
```bash
uvicorn backend.main:app --reload
```

**前端开发模式**：
```bash
cd frontend
npm start
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
