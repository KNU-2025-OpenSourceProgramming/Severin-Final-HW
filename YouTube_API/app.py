from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import os
import time
import threading
from search_utils import search_with_retry
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

app = Flask(__name__, template_folder='./www', static_folder='./www', static_url_path='/' )
CORS(app)

# 简单的配额追踪
api_calls = {
    "count": 0,
    "last_reset": time.time()
}

# 24小时每天重置计数器
def reset_counter():
    while True:
        # 86400 秒 = 24 小时
        time.sleep(86400)
        api_calls["count"] = 0
        api_calls["last_reset"] = time.time()
        print("API 配额计数器已重置！")

# 后台运行重置线程
counter_thread = threading.Thread(target=reset_counter, daemon=True)
counter_thread.start()

# YouTube API 密钥设置
# 优先使用环境变量中的密钥
API_KEY = os.environ.get('YOUTUBE_API_KEY')

# 如果环境变量中没有，尝试从 config.py 文件中获取
if not API_KEY:
    try:
        from config import YOUTUBE_API_KEY
        API_KEY = YOUTUBE_API_KEY
    except ImportError:
        API_KEY = "YOUR_YOUTUBE_API_KEY"
        print("警告：未找到 .env 文件或 config.py 文件中的 YOUTUBE_API_KEY。请设置有效的 API 密钥！")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/quota', methods=['GET'])
def get_quota():
    return jsonify({
        "api_calls_count": api_calls["count"],
        "last_reset_time_unix": api_calls["last_reset"],
        "last_reset_time_human": time.ctime(api_calls["last_reset"])
    })

@app.route('/api/search', methods=['GET'])
def search_videos():
    query = request.args.get('query', '')
    max_results = request.args.get('max_results', 10, type=int)

    if not query:
        return jsonify({"error": "검색어를 입력해주세요."}), 400
    
    # 在尝试调用 API 之前增加计数器
    api_calls["count"] += 1
    print(f"当前 API 调用次数: {api_calls['count']}")

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=API_KEY
    )

    try:
        # 调用带重试的搜索函数
        search_response = search_with_retry(youtube, query, max_results)

        videos = []
        for item in search_response.get("items", []):
            video_data = {
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "thumbnailUrl": item["snippet"]["thumbnails"]["medium"]["url"],
                "channelTitle": item["snippet"]["channelTitle"],
                "publishedAt": item["snippet"]["publishedAt"]
            }
            videos.append(video_data)

        return jsonify({"videos": videos})
    except HttpError as e:
        # 详细的错误日志
        print(f"YouTube API HttpError: {e.resp.status} - {e.content}")
        return jsonify({"error": f"YouTube API HttpError: {e.resp.status} - {e.content.decode('utf-8')}"}), e.resp.status
    except Exception as e:
        # 详细的错误日志
        print(f"YouTube API 오류: {str(e)}")
        return jsonify({"error": f"YouTube API 오류: {str(e)}"}), 500

if __name__ == '__main__':
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='启动 YouTube API 搜索 Flask 应用')
    parser.add_argument('--port', type=int, default=3000, help='指定运行端口 (默认: 3000)')
    args = parser.parse_args()
    
    app.run(host='0.0.0.0', port=args.port, debug=True)
