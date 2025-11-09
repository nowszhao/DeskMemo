#!/bin/bash

echo "Starting DeskMemo Frontend..."

# 获取脚本所在目录（frontend 目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# 启动开发服务器
echo "Starting React development server..."
# 配置环境变量以允许所有主机访问（生产环境部署时使用）
export DANGEROUSLY_DISABLE_HOST_CHECK=true
export HOST=0.0.0.0
npm start
