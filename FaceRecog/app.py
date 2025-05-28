# pyright: reportUnknownMemberType=false
# pyright: reportAttributeAccessIssue=false

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mediapipe as mp
import cv2
import numpy as np
import base64
import io
import os
import json
from typing import Any, Dict, List, Optional, Union

app = Flask(__name__, template_folder='./static/www', static_folder='./static', static_url_path='/static')
CORS(app) # 启用 CORS

# MediaPipe 初始化 (MediaPipe Initialization)
# 使用 mp.solutions.face_detection 进行人脸检测
mp_face_detection = mp.solutions.face_detection  # pyright: ignore[reportAttributeAccessIssue]
# 使用 mp.solutions.face_mesh 进行人脸网格 (Face Mesh) 关键点提取
mp_face_mesh = mp.solutions.face_mesh  # pyright: ignore[reportAttributeAccessIssue]
# 绘图工具 (Drawing Utilities) (虽然这里主要在前端绘制，但后端也可以用于调试)
mp_drawing = mp.solutions.drawing_utils  # pyright: ignore[reportAttributeAccessIssue]

# 脸部数据存储 (Face Data Storage) (在实际生产环境中，推荐使用数据库如 MongoDB 或 PostgreSQL)
face_database = {}

# 创建数据目录 (Create Data Directory) 用于持久化存储注册的人脸特征
os.makedirs('face_data', exist_ok=True)

# 根路由 (Root Route) - 提供前端页面
@app.route('/')
def index():
    return send_from_directory('static/www', 'index.html')

# 解码 Base64 图像数据为 OpenCV 图像格式
def decode_image(image_data):
    # 移除 Base64 字符串前缀 (e.g., 'data:image/jpeg;base64,')
    image_data = image_data.split(',')[1]
    # 解码 Base64 字符串为字节
    image_bytes = base64.b64decode(image_data)
    # 将字节转换为 NumPy 数组
    nparr = np.frombuffer(image_bytes, np.uint8)
    # 使用 OpenCV 解码图像
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

# 使用 MediaPipe 提取人脸特征
def extract_face_features(image):
    # 使用 MediaPipe 的人脸检测模型 (Face Detection Model)
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        # 将图像从 BGR (OpenCV 默认) 转换为 RGB (MediaPipe 偏好)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 处理图像，进行人脸检测
        results = face_detection.process(rgb_image)

        if results.detections: # 如果检测到人脸
            faces = []
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box # 相对边界框信息
                ih, iw, _ = image.shape # 图像高度、宽度
                # 将相对坐标转换为绝对像素坐标
                x = int(bboxC.xmin * iw)
                y = int(bboxC.ymin * ih)
                w = int(bboxC.width * iw)
                h = int(bboxC.height * ih)

                # 裁剪出人脸区域 (Crop Face Region)
                face_crop = image[y:y+h, x:x+w]

                # 使用 MediaPipe 的人脸网格模型 (Face Mesh Model) 提取特征点
                with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
                    face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB) # 再次转换为 RGB
                    face_results = face_mesh.process(face_rgb) # 处理裁剪后的人脸图像

                    features = []
                    if face_results.multi_face_landmarks: # 如果检测到人脸关键点
                        for face_landmarks in face_results.multi_face_landmarks:
                            # 提取每个关键点的 x, y, z 坐标作为特征 (Features)
                            for landmark in face_landmarks.landmark:
                                features.extend([landmark.x, landmark.y, landmark.z])

                    faces.append({
                        'bbox': {'x': x, 'y': y, 'width': w, 'height': h}, # 边界框信息
                        'features': features # 提取的特征向量
                    })
            return faces # 返回检测到的人脸列表 (包含边界框和特征)
    return None # 未检测到人脸则返回 None

# 计算特征向量之间的相似度 (Calculate Similarity between Feature Vectors)
def calculate_similarity(features1, features2):
    # 使用欧氏距离 (Euclidean Distance) 计算相似度
    if not features1 or not features2 or len(features1) != len(features2):
        return 0.0

    distance = np.linalg.norm(np.array(features1) - np.array(features2)) # 计算欧氏距离
    # 将距离转换为相似度分数 (0 到 1 之间，距离越小相似度越高)
    # 这里的 10 是一个经验值，用于将距离标准化到相似度范围
    similarity = max(0, 1 - distance / 10)
    return similarity

# 人脸注册 API (Face Registration API)
@app.route('/register', methods=['POST'])
def register_face():
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': '无效的请求数据 (Invalid request data)'
            })
        
        image = decode_image(data.get('image', ''))
        name = data.get('name', '')
        
        if image is None or name == '':
            return jsonify({
                'success': False,
                'message': '缺少图像或姓名数据 (Image or name data missing)'
            })

        # 提取图像中的人脸特征
        faces = extract_face_features(image)

        if not faces:
            return jsonify({
                'success': False,
                'message': '얼굴을 찾을 수 없습니다. (No face found in the image.)'
            })

        # 检查是否已存在高度相似的已注册人脸 (Check for Existing Highly Similar Faces)
        # 防止重复注册，相似度阈值设为 95% (0.95)
        for db_name, db_features in face_database.items():
            for face in faces:
                similarity = calculate_similarity(face['features'], db_features)
                if similarity > 0.95: # 如果相似度高于 95%
                    return jsonify({
                        'success': False,
                        'message': f'이미 등록된 얼굴입니다 (유사도: {similarity*100:.1f}%). (This face is already registered (Similarity: {similarity*100:.1f}%).)'
                    })

        # 注册新人脸 (Register New Face) - 只取第一个检测到的人脸
        # 在实际应用中，您可能需要处理一张图片中有多张人脸的情况
        face_database[name] = faces[0]['features']

        # 将注册的人脸特征保存到文件，以便持久化 (Save features to file for persistence)
        with open(f'face_data/{name}.json', 'w') as f:
            json.dump(faces[0]['features'], f)

        return jsonify({
            'success': True,
            'message': f'"{name}" 등록 완료. ("{name}" registration complete.)'
        })

    except Exception as e:
        # 错误处理 (Error Handling)
        return jsonify({
            'success': False,
            'message': str(e)
        })

# 人脸识别 API (Face Recognition API)
@app.route('/recognize', methods=['POST'])
def recognize_face():
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': '无效的请求数据 (Invalid request data)'
            })
        
        image = decode_image(data.get('image', ''))
        
        if image is None:
            return jsonify({
                'success': False,
                'message': '缺少图像数据 (Image data missing)'
            })

        # 提取图像中的人脸特征
        faces = extract_face_features(image)

        if not faces:
            return jsonify({
                'success': False,
                'message': '얼굴을 찾을 수 없습니다. (No face found in the image.)'
            })

        result = {'faces': []}

        for face in faces:
            best_match = None
            best_similarity = 0

            # 与数据库中所有已注册人脸进行比对
            for name, db_features in face_database.items():
                similarity = calculate_similarity(face['features'], db_features)
                # 如果相似度高于当前最佳匹配且高于识别阈值 70% (0.7)
                if similarity > best_similarity and similarity > 0.7:
                    best_similarity = similarity
                    best_match = name

            face_result = {
                'x': face['bbox']['x'],
                'y': face['bbox']['y'],
                'width': face['bbox']['width'],
                'height': face['bbox']['height'],
                'name': best_match, # 识别到的名字，如果没有匹配到则为 None
                'confidence': best_similarity # 相似度作为置信度 (Confidence)
            }
            result['faces'].append(face_result)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        # 错误处理
        return jsonify({
            'success': False,
            'message': str(e)
        })

# 启动时加载已注册的人脸数据 (Load Registered Face Data on Startup)
def load_face_data():
    global face_database
    face_data_dir = 'face_data'

    if os.path.exists(face_data_dir):
        for filename in os.listdir(face_data_dir):
            if filename.endswith('.json'):
                name = filename[:-5]  # 移除 .json 扩展名获取名字
                with open(os.path.join(face_data_dir, filename), 'r') as f:
                    face_database[name] = json.load(f)

# 应用启动时调用加载数据函数
load_face_data()

if __name__ == '__main__':
    print("Flask服务器已启动 - 访问 http://localhost:5000 使用人脸识别系统")
    # 0.0.0.0 允许外部访问，端口设为5000
    # debug=True 可以在开发时看到更详细的错误信息
    app.run(host='0.0.0.0', port=5000, debug=True)
