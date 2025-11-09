#!/bin/bash

echo "Starting DeskMemo Screenshot Agent..."

# 获取脚本所在目录（agent 目录）
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
echo "Installing agent dependencies..."


# 启动 Agent
echo "Screenshot Agent is running..."
echo "Press Ctrl+C to stop"
python agent/screenshot_agent.py
