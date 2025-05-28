#!/bin/bash

# 打印欢迎信息
echo "======================================"
echo "YouTube API 视频搜索应用程序启动脚本"
echo "======================================"

# 检查是否安装了必要的 Python 包
echo "检查依赖项..."
packages=("flask" "google-api-python-client" "pyngrok" "flask-cors" "python-dotenv")
missing_packages=()

for package in "${packages[@]}"; do
  if ! pip show "$package" > /dev/null 2>&1; then
    missing_packages+=("$package")
  fi
done

# 安装缺失的包
if [ ${#missing_packages[@]} -ne 0 ]; then
  echo "正在安装缺失的依赖项: ${missing_packages[*]}"
  pip install "${missing_packages[@]}"
fi

# 检查配置
api_key=""

# 方法1: 检查 .env 文件
if [ -f ".env" ]; then
  echo "找到 .env 文件"
  api_key=$(grep -oP 'YOUTUBE_API_KEY=\K[^$]+' .env 2>/dev/null)
fi

# 方法2: 检查 config.py 文件
if [ -z "$api_key" ] && [ -f "config.py" ]; then
  echo "找到 config.py 文件"
  api_key=$(grep -oP 'YOUTUBE_API_KEY\s*=\s*"\K[^"]+' config.py 2>/dev/null)
fi

# 方法3: 检查环境变量
if [ -z "$api_key" ] && [ -n "$YOUTUBE_API_KEY" ]; then
  echo "找到环境变量中的 API 密钥"
  api_key=$YOUTUBE_API_KEY
fi

# 如果仍然没有 API 密钥，提示用户
if [ "$api_key" = "YOUR_YOUTUBE_API_KEY" ] || [ -z "$api_key" ]; then
  echo "未找到有效的 YouTube API 密钥"
  echo "请提供 YouTube API 密钥:"
  read -r api_key
  
  # 将提供的密钥写入配置文件
  if [ -n "$api_key" ]; then
    # 优先写入 .env 文件
    if [ ! -f ".env" ]; then
      echo '# YouTube API 和 ngrok 环境变量' > .env
      echo "YOUTUBE_API_KEY=$api_key" >> .env
    else
      # 如果文件已存在，更新或添加密钥
      if grep -q "YOUTUBE_API_KEY" .env; then
        sed -i "s/YOUTUBE_API_KEY=.*/YOUTUBE_API_KEY=$api_key/" .env
      else
        echo "YOUTUBE_API_KEY=$api_key" >> .env
      fi
    fi
    
    echo "API 密钥已保存到 .env 文件"
    
    # 同时也更新 config.py 以保持兼容性
    if [ ! -f "config.py" ]; then
      echo '# config.py - YouTube API 配置文件' > config.py
      echo '' >> config.py
      echo '# YouTube API 密钥' >> config.py
    fi
    
    # 检查文件中是否已经有密钥行
    if grep -q "YOUTUBE_API_KEY" config.py; then
      sed -i "s/YOUTUBE_API_KEY *= *\".*\"/YOUTUBE_API_KEY = \"$api_key\"/" config.py
    else
      echo "YOUTUBE_API_KEY = \"$api_key\"" >> config.py
    fi
    
    echo "API 密钥也已保存到 config.py 文件"
  else
    echo "未提供 API 密钥，应用程序可能无法正常工作"
  fi
fi

# 启动应用程序
echo "正在启动应用程序..."
python run_server.py
