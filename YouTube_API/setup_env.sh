#!/bin/bash

# 这个脚本用于设置 YouTube API 应用程序的环境变量

# 检查是否提供了 API 密钥参数
if [ -z "$1" ]; then
  echo "请提供 YouTube API 密钥作为参数"
  echo "用法: source setup_env.sh YOUR_API_KEY"
  return 1
fi

# 设置环境变量
export YOUTUBE_API_KEY="$1"
echo "已设置 YOUTUBE_API_KEY 环境变量"

# 如果提供了第二个参数作为 ngrok 令牌，也设置它
if [ -n "$2" ]; then
  export NGROK_AUTH_TOKEN="$2"
  echo "已设置 NGROK_AUTH_TOKEN 环境变量"
fi

echo "环境已配置完成！您可以通过运行 'python run_server.py' 来启动应用程序。"
