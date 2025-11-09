#!/bin/bash

echo "========================================="
echo "  Starting DeskMemo - All Services"
echo "========================================="
echo ""

# 检查是否在 macOS 或 Linux
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # 使用 tmux 在后台运行（如果可用）
    if command -v tmux &> /dev/null; then
        echo "Using tmux to manage services..."
        
        # 创建新的 tmux 会话
        tmux new-session -d -s deskmemo
        
        # 后端
        tmux rename-window -t deskmemo:0 'backend'
        tmux send-keys -t deskmemo:0 'cd backend && ./start.sh' C-m
        
        # 前端
        tmux new-window -t deskmemo:1 -n 'frontend'
        tmux send-keys -t deskmemo:1 'cd frontend && ./start.sh' C-m
        
        # Agent (等待后端启动)
        tmux new-window -t deskmemo:2 -n 'agent'
        tmux send-keys -t deskmemo:2 'sleep 5 && cd agent && ./start.sh' C-m
        
        echo ""
        echo "All services started in tmux session 'deskmemo'"
        echo ""
        echo "Commands:"
        echo "  - View services: tmux attach -t deskmemo"
        echo "  - Switch window: Ctrl+B then 0/1/2"
        echo "  - Detach: Ctrl+B then D"
        echo "  - Stop all: tmux kill-session -t deskmemo"
        echo ""
        echo "Attaching to tmux session in 2 seconds..."
        sleep 2
        tmux attach -t deskmemo
        
    else
        echo "tmux not found. Starting services in separate terminals..."
        echo ""
        echo "Please run the following commands in separate terminals:"
        echo "  1. cd backend && ./start.sh"
        echo "  2. cd frontend && ./start.sh"
        echo "  3. cd agent && ./start.sh"
    fi
else
    echo "Windows detected. Please run services manually:"
    echo "  1. cd backend && python -m backend.main"
    echo "  2. cd frontend && npm start"
    echo "  3. cd agent && python screenshot_agent.py"
fi
