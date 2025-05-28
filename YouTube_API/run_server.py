import subprocess
import time
import os
from pyngrok import ngrok
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 尝试从配置文件导入 ngrok 认证令牌
try:
    from config import NGROK_AUTH_TOKEN
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    print("已使用配置文件中的 ngrok 认证令牌")
except (ImportError, AttributeError):
    # 尝试从环境变量获取
    token = os.environ.get('NGROK_AUTH_TOKEN')
    if token:
        ngrok.set_auth_token(token)
        print("已使用环境变量中的 ngrok 认证令牌")
    else:
        print("未找到 ngrok 认证令牌，将使用免费版限制")

# 定义端口（修改为 3001 避免冲突）
PORT = 3001

# Flask 服务器开始
server_process = subprocess.Popen(["python", "app.py", "--port", str(PORT)])
print("Flask 서버가 시작되었습니다.")

# 尝试创建 ngrok 隧道
try:
    http_tunnel = ngrok.connect(PORT)
    print(f"ngrok 터널이 생성되었습니다: {http_tunnel.public_url}")
    ngrok_enabled = True
except Exception as e:
    print(f"ngrok 터널 생성 실패: {str(e)}")
    print(f"您可以直接访问本地地址: http://localhost:{PORT}")
    ngrok_enabled = False

try:
    # 앱이 계속 실행되도록 대기
    print(f"应用正在运行。访问：http://localhost:{PORT}")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # 종료 시 프로세스 정리
    server_process.terminate()
    if ngrok_enabled:
        ngrok.kill()
    print("服务已终止")

if __name__ == "__main__":
    # 主程序入口点，当脚本直接运行时执行
    print("正在启动 YouTube API 搜索应用...")
    # 主程序逻辑已经在全局范围内实现
