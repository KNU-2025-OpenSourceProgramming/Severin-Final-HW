#!/bin/bash
cd "$(dirname "$0")"  # 切换到脚本所在目录
source venv/bin/activate  # 激活虚拟环境

# 启动 Flask 应用 (后台运行)
python app.py &
FLASK_PID=$!
echo "Flask 应用已启动 (PID: $FLASK_PID)"
sleep 3  # 等待 Flask 应用完全启动

# 启动 ngrok 隧道
echo "正在启动 ngrok 隧道..."
ngrok http 3000

# 捕获 Ctrl+C 信号，优雅地停止服务
trap 'echo "正在停止服务..."; kill $FLASK_PID; exit' INT TERM
wait
