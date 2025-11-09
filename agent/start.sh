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

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "Installing agent dependencies..."
pip install -r agent/requirements.txt

# 检查配置文件
if [ ! -f "agent/.env" ]; then
    echo "Creating agent .env file..."
    cp agent/.env.example agent/.env
    echo ""
    echo "⚠️  IMPORTANT: Please edit agent/.env and configure:"
    echo "   - AGENT_SERVER_URL (backend server address)"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit and edit config..."
fi

# 启动 Agent
echo "Screenshot Agent is running..."
echo "Press Ctrl+C to stop"
python agent/screenshot_agent.py
