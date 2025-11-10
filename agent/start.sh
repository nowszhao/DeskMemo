#!/bin/bash

echo "Starting DeskMemo Screenshot Agent..."


# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖
echo "Installing agent dependencies..."
pip3 install -r requirements.txt


# 启动 Agent
echo "Screenshot Agent is running..."
echo "Press Ctrl+C to stop"
python3 screenshot_agent.py
