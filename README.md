# 多媒体Web应用集合

这是一个包含三个独立Web应用的集合项目，每个应用都专注于特定的多媒体和机器学习功能。这些应用均使用Flask作为后端框架，结合现代前端技术提供直观的用户界面。

## 项目结构

本项目包含以下三个主要子项目：

1. **人脸识别应用** - 使用MediaPipe进行实时人脸检测与识别
2. **YouTube API视频内容搜索** - 利用YouTube Data API搜索和展示视频内容  
3. **YOLOv8对象检测** - 使用YOLOv8模型进行实时图像对象检测

## 环境要求

本项目要求使用Python 3.6+，并为每个子项目提供了独立的依赖项。您可以选择为每个应用创建单独的虚拟环境，或者使用根目录中的统一依赖文件。

## 子项目说明

### 1. 人脸识别应用 (FaceRecog)

基于MediaPipe构建的人脸识别Web应用，能够通过浏览器访问摄像头，进行人脸检测和识别。

**主要功能：**
- 人脸检测与关键点提取
- 人脸特征向量存储与比对
- 实时摄像头图像处理
- 用户人脸注册与识别

**技术栈：**
- 后端：Flask, MediaPipe
- 前端：HTML, JavaScript
- 数据存储：JSON文件系统

**启动方法：**
```bash
cd FaceRecog
# 创建并激活虚拟环境
python -m venv face_recog_env
source face_recog_env/bin/activate  # Linux/Mac
# face_recog_env\Scripts\activate  # Windows
# 安装依赖并启动
python app.py
```

### 2. YouTube API视频内容搜索 (YouTube_API)

使用YouTube Data API v3构建的视频搜索应用，提供友好的用户界面进行视频内容检索。

**主要功能：**
- 关键词视频搜索
- 详细视频信息显示
- 视频缩略图和预览
- API配额监控

**技术栈：**
- 后端：Flask, Google API Client
- 前端：React
- 外部访问：ngrok (可选)

**启动方法：**
```bash
cd YouTube_API
# 设置环境
source setup_env.sh  # 或 bash setup_env.sh
# 安装依赖
bash install_deps.sh
# 启动应用
bash start_app.sh
```

### 3. YOLOv8对象检测 (yolov8_detection)

基于YOLOv8模型的实时对象检测Web应用，支持图像上传和实时检测。

**主要功能：**
- 图像中对象检测与识别
- 实时对象定位
- 检测结果可视化
- 支持多种物体类别识别

**技术栈：**
- 后端：Flask, Ultralytics YOLOv8
- 前端：HTML, JavaScript
- 深度学习：YOLOv8预训练模型

**启动方法：**
```bash
cd yolov8_detection
# 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
# 启动应用
bash start_app.sh  # 或 ./start_app.sh
```

## 统一依赖安装

如果您希望一次性安装所有子项目的依赖，可以使用根目录下的统一依赖文件：

```bash
# 创建全局虚拟环境
python -m venv multimedia_apps_env
source multimedia_apps_env/bin/activate  # Linux/Mac
# multimedia_apps_env\Scripts\activate  # Windows

# 生成并安装统一依赖
python -c "import os; open('unified_requirements.txt', 'w').writelines(line for file in ['FaceRecog/requirements.txt', 'YouTube_API/requirements.txt', 'yolov8_detection/requirements.txt'] if os.path.exists(file) for line in open(file))"
pip install -r unified_requirements.txt
```

## 开发与贡献

1. Fork 本项目
2. 创建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 许可证

本项目根据MIT许可证发布 - 查看 `LICENSE` 文件了解详情。

## 致谢

- 感谢 Google MediaPipe 提供的人脸识别技术
- 感谢 YouTube Data API 提供的视频搜索功能
- 感谢 Ultralytics 提供的 YOLOv8 模型