# DeskMemo Frontend

基于 React + DaisyUI 的 Web 用户界面。

## 快速启动

```bash
# 方式一：使用启动脚本（推荐）
./start.sh

# 方式二：手动启动
npm install
npm start
```

## 配置

开发环境使用 `package.json` 中的 proxy 配置，无需额外配置。

生产环境：
```bash
cp .env.example .env.local
nano .env.local
```

配置后端 API 地址：
```env
REACT_APP_API_URL=http://YOUR_SERVER_IP:8000/api
# 或使用域名
# REACT_APP_API_URL=https://your-domain.com/api
```

## 开发

```bash
npm start        # 启动开发服务器
npm run build    # 构建生产版本
npm test         # 运行测试
```

## 生产部署

### 构建

```bash
npm run build
```

构建产物在 `build/` 目录。

### 使用 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }

    # 后端 API 代理
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

### 使用静态文件服务器

```bash
# 使用 serve
npm install -g serve
serve -s build -p 3000

# 使用 Python
cd build
python -m http.server 3000
```

## 技术栈

- React 18
- React Router 6
- DaisyUI
- Tailwind CSS
- Recharts
- Axios

## 页面

- **仪表盘**：今日统计、活动分布
- **时间轴**：截屏浏览、图片预览
- **报告**：小时报告、日报
- **搜索**：关键词 + 语义搜索

## 目录结构

```
frontend/
├── public/           # 静态资源
├── src/
│   ├── pages/       # 页面组件
│   │   ├── Dashboard.js
│   │   ├── Timeline.js
│   │   ├── Reports.js
│   │   └── Search.js
│   ├── services/    # API 服务
│   │   └── api.js
│   ├── App.js       # 主应用
│   └── index.js     # 入口
├── package.json
└── tailwind.config.js
```
