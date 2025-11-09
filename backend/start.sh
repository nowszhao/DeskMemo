#!/bin/bash

echo "Starting DeskMemo Backend..."

# 获取脚本所在目录（backend 目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 项目根目录
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# 检查配置文件
if [ ! -f "backend/.env" ]; then
    echo "Creating backend .env file..."
    cp backend/.env.example backend/.env
    echo ""
    echo "⚠️  IMPORTANT: Please edit backend/.env and configure:"
    echo "   - AI_IMAGE_SERVER (for production deployment)"
    echo ""
fi

# 启动后端
echo "Starting backend server..."
# 禁用 ChromaDB 遥测
export ANONYMIZED_TELEMETRY=False
python -m backend.main
