import subprocess
import time
import os
from pyngrok import ngrok
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 获取 ngrok 认证令牌
ngrok_auth_token = os.getenv('NGROK_AUTHTOKEN')

# 设置 ngrok 认证令牌
if ngrok_auth_token:
    ngrok.set_auth_token(ngrok_auth_token)
else:
    print("警告：未找到 NGROK_AUTHTOKEN 环境变量，ngrok 可能无法正常工作")

# Flask 服务器启动
# 使用 `subprocess.Popen` 在单独的进程中运行 `app.py`
server_process = subprocess.Popen(["python", "app.py"])
print("Flask 服务器已启动。")

# ngrok 隧道创建
# 连接到本地 3000 端口，并创建一个 HTTP 隧道
http_tunnel = ngrok.connect(3000)
print(f"ngrok 隧道已创建: {http_tunnel.public_url}")

try:
    # 应用程序将持续运行，直到被中断
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # 捕获 `Ctrl+C` 中断信号，终止服务器进程并关闭 ngrok
    server_process.terminate()
    ngrok.kill()
