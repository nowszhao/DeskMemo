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

source venv/bin/activate

# 安装依赖
echo "Installing backend dependencies..."

# 启动后端
echo "Starting backend server..."
# 禁用 ChromaDB 遥测
export ANONYMIZED_TELEMETRY=False
python -m backend.main
