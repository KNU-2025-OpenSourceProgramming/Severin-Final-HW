from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import time
import base64
import numpy as np
import cv2
from ultralytics import YOLO
import json

# Flask 应用初始化
# `__name__` 是当前模块的名称。
# `template_folder='./www'` 指定了 HTML 模板文件的位置。
# `static_folder='./www'` 和 `static_url_path='/'` 指定了静态文件（如 CSS、JS）的位置。
app = Flask(__name__, template_folder='./www', static_folder='./www', static_url_path='/')
CORS(app)  # 启用 CORS (Cross-Origin Resource Sharing)，允许跨域请求

# YOLOv8 模型加载
# `yolov8n.pt` 是 YOLOv8 的一个预训练模型文件，'n' 代表 nano 版本，文件大小较小，适用于快速原型开发。
model = YOLO('yolov8n.pt')

# 临时图片保存路径
UPLOAD_FOLDER = './uploads'
# 如果目录不存在，则创建
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 根路由，用于提供前端 HTML 页面
@app.route('/')
def index():
    # 渲染并返回 `www/index.html` 文件
    return render_template('index.html')

# `/api/detect` 路由，用于处理对象检测请求
@app.route('/api/detect', methods=['POST'])
def detect_objects():
    # 检查请求中是否包含 'image' 键
    if 'image' not in request.json:
        return jsonify({'error': 'No image data provided'}), 400 # 返回错误信息和 HTTP 400 Bad Request 状态码

    try:
        # 图像数据解析
        img_data = request.json['image']
        # 移除 Base64 数据的头部 (e.g., "data:image/jpeg;base64,")
        if ',' in img_data:
            img_data = img_data.split(',')[1]

        # Base64 解码，将 Base64 编码的字符串转换回字节（bytes）
        img_bytes = base64.b64decode(img_data)
        # 将字节流转换为 NumPy 数组
        nparr = np.frombuffer(img_bytes, np.uint8)
        # 使用 OpenCV 从 NumPy 数组解码图像
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 保存图像 (用于调试)
        timestamp = int(time.time()) # 获取当前时间戳
        img_path = f"{UPLOAD_FOLDER}/image_{timestamp}.jpg" # 构建图像保存路径
        cv2.imwrite(img_path, image) # 将图像写入文件

        # 使用 YOLOv8 进行对象检测
        results = model(image)

        # 处理检测结果
        detections = []
        # 遍历每个检测结果
        for r in results:
            boxes = r.boxes # 获取检测到的边界框
            for box in boxes:
                # 获取边界框的坐标 (x1, y1, x2, y2)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0]) # 获取置信度 (Confidence)
                cls = int(box.cls[0])     # 获取类别 ID (Class ID)
                name = model.names[cls]   # 根据类别 ID 获取类别名称

                detections.append({
                    'bbox': [x1, y1, x2, y2],       # 边界框坐标
                    'confidence': conf,             # 置信度
                    'class': cls,                   # 类别 ID
                    'name': name                    # 类别名称
                })

        # 返回成功响应和检测到的对象列表
        return jsonify({
            'success': True,
            'detections': detections
        })

    except Exception as e:
        # 捕获异常并返回错误信息和 HTTP 500 Internal Server Error 状态码
        return jsonify({'error': str(e)}), 500

# 当脚本直接运行时，启动 Flask 应用程序
if __name__ == '__main__':
    # 应用程序在所有网络接口上运行 (host='0.0.0.0')，监听 3000 端口，并启用调试模式
    app.run(host='0.0.0.0', port=3000, debug=True)
