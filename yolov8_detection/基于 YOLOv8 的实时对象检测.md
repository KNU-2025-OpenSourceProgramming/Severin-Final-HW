# 基于 YOLOv8 的实时对象检测

## **基于 YOLOv8 的实时对象检测 Web 服务构建指南**

本指南将帮助您在本地计算机上部署一个使用 YOLOv8 模型进行实时对象检测的 Flask Web 服务，并通过网络将其公开，以便您可以通过手机或其他设备访问。

---

### **1. 环境设置（Environment Setup）**

首先，您需要在计算机上创建一个新的工作目录，并设置一个 Python 虚拟环境来安装所需的依赖项。

#### **1.1 创建工作目录和虚拟环境**

打开终端（Windows 上的命令提示符或 PowerShell），然后运行以下命令：

**Linux/macOS:**
```bash
# 创建项目目录
mkdir yolov8_detection
cd yolov8_detection

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

**Windows:**
```cmd
# 创建项目目录
mkdir yolov8_detection
cd yolov8_detection

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

#### **1.2 安装必要的依赖项**

激活虚拟环境后，安装以下所需的 Python 库：

```### **5. 服务接入（Access）**

根据您选择的运行方式，可以通过不同的方法访问服务：

#### **5.1 本地网络访问（直接运行 Flask 应用）**

如果您使用第一种方式运行（直接运行 Flask 应用），终端输出将显示如下内容：

```
 * Running on http://0.0.0.0:3000/ (Press CTRL+C to quit)
```

**访问步骤：**

1. **查找本地 IP 地址：** 
   - 在 Windows 上运行 `ipconfig` 命令
   - 在 Linux/macOS 上运行 `ifconfig` 或 `ip addr` 命令

2. **从同一网络设备访问：** 在任何连接到同一网络的设备（包括手机）的浏览器中，输入 `http://你的IP地址:3000`，例如 `http://192.168.1.100:3000`。

#### **5.2 互联网访问（使用 ngrok）**

如果您使用第二种方式运行（使用 ngrok），终端输出将显示如下内容：

```
Flask 服务器已启动。
ngrok 隧道已创建: https://xxxx-xx-xx-xxx-xx.ngrok.io
```

**访问步骤：**

1. **复制 ngrok URL：** 从终端输出中复制 `https://xxxx-xx-xx-xxx-xx.ngrok.io` 这样的完整 URL。
2. **在任何设备上访问：** 在任何设备（即使不在同一网络）的浏览器中粘贴此 URL 并访问。

无论使用哪种方法，您都将看到一个带有视频预览、摄像头切换按钮和对象检测结果列表的网页界面。点击"객체 감지 (Detect Objects)"按钮或等待大约 10 秒，服务就会开始检测摄像头捕获到的对象。p install flask flask-cors ultralytics
pip install opencv-python numpy
pip install watchdog  # 用于文件更改检测
```

对于本地开发，如果您想让手机访问您的应用程序，我们有两种选择：
1. 使用内网 IP 地址（只适用于同一局域网内）
2. 使用 ngrok 等工具创建公共隧道（适用于互联网访问）

如果需要使用 ngrok，请安装：
```bash
pip install pyngrok
# 或者从 https://ngrok.com/ 下载并安装 ngrok 客户端
```

---

### **2. 后端（Backend）开发 (Flask)**

接下来，我们将创建 Flask 应用程序和服务器启动脚本。

### **2.1 Flask 应用程序（Application）创建**

这个 Flask 应用程序会接收来自前端的图像数据，使用 YOLOv8 模型进行对象检测，并将检测结果返回。

在项目目录中创建 `app.py` 文件，并添加以下代码：

**Python**

```python
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
```

### **2.2 服务器（Server）运行选项**

在本地计算机上，您有两种方式运行 Flask 服务器：直接运行或通过 ngrok 创建公共访问链接。

#### **2.2.1 直接运行（本地网络访问）**

对于本地网络内的访问（例如，同一 Wi-Fi 网络内的设备），您可以直接运行 Flask 应用程序。

```bash
# 直接运行 Flask 应用
python app.py
```

启动后，您可以通过计算机的 IP 地址和端口（3000）来访问应用程序，例如：`http://192.168.1.100:3000`。

要找到您的计算机在局域网中的 IP 地址：
- **Windows:** 在命令提示符中运行 `ipconfig`
- **Linux/macOS:** 在终端中运行 `ifconfig` 或 `ip addr`

#### **2.2.2 使用 ngrok 创建公共访问（互联网访问）**

如果您想从互联网访问（例如，不在同一网络的设备），可以使用 ngrok 创建一个公共隧道。

创建 `run_server.py` 文件，添加以下代码：

```python
import subprocess
import time
from pyngrok import ngrok

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
```

然后运行这个脚本：

```bash
python run_server.py
```

注意：如果您使用的是 ngrok 客户端而不是 pyngrok 库，可以使用以下命令：

```bash
# 先运行 Flask 应用
python app.py

# 然后在另一个终端窗口中运行 ngrok（根据您的安装方式调整路径）
ngrok http 3000
```

---

### **3. 前端（Frontend）开发 (React)**

为了提供一个用户界面（User Interface），我们将使用 React.js 来构建前端。

### **3.1 目录（Directory）结构创建**

首先，创建前端所需的目录结构：

```bash
# 创建必要的目录
mkdir -p www/js
```

### **3.2 HTML 模板（Template）创建**

这是前端应用程序的主 HTML 文件。它加载 React 库和我们的 React 应用程序。

创建 `www/index.html` 文件，并添加以下内容：

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YOLOv8 객체 인식 (Object Detection)</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.2.3/css/bootstrap.min.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        .camera-container {
            position: relative;
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
        }
        #videoElement {
            width: 100%;
            background-color: #666;
        }
        #canvasElement {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        .controls {
            margin: 20px 0;
            display: flex;
            justify-content: space-between;
        }
        .detection-list {
            margin-top: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
        }
        .detection-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #dee2e6;
        }
        .spinner-border {
            display: none;
        }
    </style>
</head>
<body>
    <div id="app"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.21.2/babel.min.js"></script>
    <script type="text/babel" src="js/app.js"></script>
</body>
</html>
```

### **3.3 React 应用程序（Application）开发**

这个 React 组件负责处理摄像头的选择（前置/后置）、视频流（Video Stream）显示、图像捕获以及向后端 API 发送图像进行对象检测，并显示检测结果。

创建 `www/js/app.js` 文件，并添加以下代码：

```javascript
const { useState, useEffect, useRef } = React; // 引入 React 钩子 (Hooks)

const App = () => {
    // `cameraMode` 状态：'environment' (后置摄像头) 或 'user' (前置摄像头)
    const [cameraMode, setCameraMode] = useState('environment');
    // `detections` 状态：存储检测到的对象列表
    const [detections, setDetections] = useState([]);
    // `isProcessing` 状态：表示是否正在处理图像
    const [isProcessing, setIsProcessing] = useState(false);
    // `errorMessage` 状态：存储错误信息
    const [errorMessage, setErrorMessage] = useState('');

    // `useRef` 用于直接访问 DOM 元素，例如 <video> 和 <canvas>
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null); // 存储媒体流对象
    const timerRef = useRef(null);   // 存储 setInterval 的 ID

    // `useEffect` 钩子用于在组件加载和 `cameraMode` 变化时启动/停止摄像头
    useEffect(() => {
        startCamera(); // 启动摄像头
        // 返回一个清理函数，在组件卸载或 `cameraMode` 变化前执行
        return () => {
            stopCamera(); // 停止摄像头
            if (timerRef.current) {
                clearInterval(timerRef.current); // 清除定时器
            }
        };
    }, [cameraMode]); // 依赖数组，当 `cameraMode` 变化时重新运行此 effect

    // 启动摄像头功能
    const startCamera = async () => {
        try {
            if (streamRef.current) {
                stopCamera(); // 如果已有流，则先停止
            }
            // 摄像头约束，设置 `facingMode` 来选择前置或后置摄像头
            const constraints = {
                video: {
                    facingMode: cameraMode
                }
            };
            // 获取用户媒体设备 (摄像头) 的视频流
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            streamRef.current = stream; // 保存流对象

            if (videoRef.current) {
                videoRef.current.srcObject = stream; // 将视频流设置到 <video> 元素
                videoRef.current.play(); // 播放视频

                // 当视频元数据加载完成后 (获取到视频的真实宽度和高度)
                videoRef.current.onloadedmetadata = () => {
                    if (canvasRef.current) {
                        // 设置 canvas 的宽度和高度与视频保持一致
                        canvasRef.current.width = videoRef.current.videoWidth;
                        canvasRef.current.height = videoRef.current.videoHeight;
                    }

                    // 周期性地执行对象检测
                    timerRef.current = setInterval(() => {
                        // 只有当前没有正在处理的请求时才进行检测
                        if (!isProcessing) {
                            detectObjects();
                        }
                    }, 10000); // 每 10 秒 (10000 毫秒) 执行一次
                };
            }
        } catch (err) {
            setErrorMessage(`카메라 접근 오류 (Camera Access Error): ${err.message}`);
            console.error('카메라 접근 오류 (Camera Access Error):', err);
        }
    };

    // 停止摄像头功能
    const stopCamera = () => {
        if (streamRef.current) {
            // 遍历所有媒体轨道（Track）并停止
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null; // 清空流对象
        }
    };

    // 切换摄像头功能 (前置 <-> 后置)
    const switchCamera = () => {
        setCameraMode(prev => prev === 'environment' ? 'user' : 'environment');
    };

    // 捕获图像，将当前视频帧绘制到 canvas 并转换为 Base64 格式的 JPEG 图像数据
    const captureImage = () => {
        if (!videoRef.current || !canvasRef.current) return null;

        const canvas = document.createElement('canvas'); // 创建一个离屏 canvas
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;

        const ctx = canvas.getContext('2d'); // 获取 2D 渲染上下文
        // 将视频当前帧绘制到 canvas 上
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

        // 将 canvas 内容转换为 Base64 编码的 JPEG 图像数据 URL
        return canvas.toDataURL('image/jpeg');
    };

    // 对象检测功能，向后端 API 发送图像数据
    const detectObjects = async () => {
        if (!videoRef.current || !canvasRef.current) return;

        try {
            setIsProcessing(true); // 设置处理状态为真
            const imageData = captureImage(); // 捕获图像数据

            if (!imageData) {
                console.error('이미지 캡처 실패 (Image Capture Failed)');
                return;
            }

            // 发送 POST 请求到 `/api/detect`
            const response = await fetch('/api/detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // 设置请求头为 JSON
                },
                body: JSON.stringify({ image: imageData }), // 将图像数据作为 JSON 发送
            });

            const result = await response.json(); // 解析 JSON 响应

            if (result.success) {
                console.log('감지 결과 (Detection Results):', result.detections);
                setDetections(result.detections);     // 更新检测结果状态
                drawDetections(result.detections);    // 在 canvas 上绘制检测框
            } else {
                console.error('객체 감지 오류 (Object Detection Error):', result.error);
                setErrorMessage(`객체 감지 오류 (Object Detection Error): ${result.error}`);
            }
        } catch (err) {
            console.error('API 요청 오류 (API Request Error):', err);
            setErrorMessage(`API 요청 오류 (API Request Error): ${err.message}`);
        } finally {
            setIsProcessing(false); // 无论成功或失败，都将处理状态设为假
        }
    };

    // 在 canvas 上绘制检测到的对象边界框和标签
    const drawDetections = (detectionResults) => {
        if (!canvasRef.current || !videoRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        // 清空 canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 计算缩放比例，以便在 canvas 上正确绘制
        const scaleX = canvas.width / videoRef.current.videoWidth;
        const scaleY = canvas.height / videoRef.current.videoHeight;

        // 遍历每个检测结果并绘制
        detectionResults.forEach(detection => {
            const [x1, y1, x2, y2] = detection.bbox; // 获取边界框坐标
            // 根据缩放比例调整坐标
            const scaledX1 = x1 * scaleX;
            const scaledY1 = y1 * scaleY;
            const scaledWidth = (x2 - x1) * scaleX;
            const scaledHeight = (y2 - y1) * scaleY;

            // 绘制边界框
            ctx.strokeStyle = '#00FF00'; // 绿色边框
            ctx.lineWidth = 2;
            ctx.strokeRect(scaledX1, scaledY1, scaledWidth, scaledHeight);

            // 绘制文本背景
            const label = `${detection.name} ${Math.round(detection.confidence * 100)}%`; // 标签 (名称 + 置信度)
            const textWidth = ctx.measureText(label).width;
            ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'; // 半透明黑色背景
            ctx.fillRect(scaledX1, scaledY1 - 20, textWidth + 10, 20);

            // 绘制文本
            ctx.fillStyle = '#FFFFFF'; // 白色文字
            ctx.font = '16px Arial';
            ctx.fillText(label, scaledX1 + 5, scaledY1 - 5);
        });
    };

    // 渲染检测到的对象列表
    const renderDetectionList = () => {
        if (detections.length === 0) {
            return <p>감지된 객체가 없습니다 (No objects detected).</p>;
        }

        // 按类别分组检测结果
        const groupedDetections = {};
        detections.forEach(detection => {
            const name = detection.name;
            if (!groupedDetections[name]) {
                groupedDetections[name] = 0;
            }
            groupedDetections[name]++;
        });

        return (
            <div>
                <h5>감지된 객체 (Detected Objects)</h5>
                {/* 渲染每个类别的计数 */}
                {Object.entries(groupedDetections).map(([name, count], index) => (
                    <div key={index} className="detection-item">
                        <span>{name}</span>
                        <span className="badge bg-primary">{count}</span>
                    </div>
                ))}
                <p className="mt-2">총 {detections.length}개 객체 감지됨 (Total {detections.length} objects detected)</p>
            </div>
        );
    };

    // 组件的渲染内容
    return (
        <div className="container">
            <h1 className="text-center mb-4">YOLOv8 객체 인식 (Object Detection)</h1>

            {/* 显示错误信息 */}
            {errorMessage && (
                <div className="alert alert-danger" role="alert">
                    {errorMessage}
                </div>
            )}

            <div className="camera-container">
                <video ref={videoRef} id="videoElement" autoPlay playsInline></video>
                <canvas ref={canvasRef} id="canvasElement"></canvas>
            </div>

            <div className="controls mt-3">
                {/* 切换摄像头按钮 */}
                <button
                    className="btn btn-primary"
                    onClick={switchCamera}
                >
                    {cameraMode === 'environment' ? '전면 카메라로 전환 (Switch to Front Camera)' : '후면 카메라로 전환 (Switch to Rear Camera)'}
                </button>

                {/* 对象检测按钮，正在处理时禁用 */}
                <button
                    className="btn btn-success"
                    onClick={detectObjects}
                    disabled={isProcessing}
                >
                    객체 감지 (Detect Objects)
                    {/* 正在处理时显示加载动画 */}
                    {isProcessing && (
                        <span className="spinner-border spinner-border-sm ms-2" role="status" aria-hidden="true"></span>
                    )}
                </button>
            </div>

            {/* 显示检测到的对象列表 */}
            <div className="detection-list mt-3">
                {renderDetectionList()}
            </div>
        </div>
    );
};

// 将 App 组件渲染到 ID 为 'app' 的 DOM 元素中
ReactDOM.render(<App />, document.getElementById('app'));
```

---

### **4. 服务部署（Deployment）及接入（Access）**

现在所有文件都已准备就绪，我们可以启动服务并从您的手机上访问它。

### **4.1 YOLOv8 模型下载**

当您第一次运行应用程序时，系统会自动下载 YOLOv8 模型。但您也可以预先下载模型，尤其是在网络连接不稳定的环境中：

```bash
# 创建所需的目录
mkdir -p uploads

# 下载 YOLOv8 模型（可选，第一次运行时会自动下载）
python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt')"
```

### **4.2 运行服务器**

根据您的需求，有两种方式运行服务器：

#### **4.2.1 直接运行 Flask 应用（本地网络访问）**

```bash
# 直接运行 Flask 应用
python app.py
```

#### **4.2.2 使用 ngrok 运行（互联网访问）**

如果您需要从互联网访问应用（例如，不在同一网络的设备），可以使用之前创建的 `run_server.py` 脚本：

```bash
# 使用 ngrok 启动服务
python run_server.py
```

---

### **5. 服务接入（Access）**

在您运行了上述“4.2 Google Colab 中运行服务器”的代码后，Colab 的输出中会显示 ngrok 生成的公共 URL（Public URL）。

输出将类似以下内容：

`Flask 服务器已启动。
ngrok 隧道已创建: https://xxxx-xx-xx-xxx-xx.ngrok.io`

**现在，您可以通过以下步骤从手机访问服务：**

1. **复制（Copy） ngrok URL：** 从 Colab 输出中复制 `https://xxxx-xx-xx-xxx-xx.ngrok.io` 这样的完整 URL。
2. **在手机浏览器中打开：** 在您的手机浏览器（例如 Chrome、Safari）中粘贴此 URL 并访问。

您将看到一个带有视频预览、摄像头切换按钮和对象检测结果列表的网页界面。点击“객체 감지 (Detect Objects)”按钮或等待大约 10 秒，服务就会开始检测摄像头捕获到的对象。

---

### **附加提示（Additional Tips）**

- **性能提升（Performance Improvement）：** 如果您需要更高的检测精度（Accuracy），可以尝试使用更大的 YOLOv8 模型，例如 `yolov8s.pt` (small) 或 `yolov8m.pt` (medium)。但请注意，更大的模型需要更多的计算资源，可能会导致在性能较低的计算机上推理速度变慢。
    
    ```python
    # 例如，在 app.py 中使用 'small' 模型
    model = YOLO('yolov8s.pt')
    ```
    
- **调整检测周期（Adjust Detection Frequency）：** 在 `www/js/app.js` 文件中，您可以修改 `setInterval` 函数中的时间（当前设置为 `10000` 毫秒，即 10 秒），以调整对象检测的频率。例如，将其更改为 `5000` 毫秒 (5 秒) 可以更频繁地进行检测。
    
    ```javascript
    // www/js/app.js 文件中
    timerRef.current = setInterval(() => {
        if (!isProcessing) {
            detectObjects();
        }
    }, 5000); // 更改为 5 秒
    ```
    
- **系统资源优化（System Resource Optimization）：** 如果您的计算机性能有限，可以尝试以下优化：
    - 使用较小的 YOLOv8 模型（例如 nano 或 small）
    - 减少检测频率
    - 关闭调试模式（在 app.py 中设置 `debug=False`）
    - 降低前端视频质量（调整 video constraints）

- **跨平台访问（Cross-platform Access）：** 如果您希望从多种设备访问应用程序：
    - 对于本地网络访问：确保所有设备连接到同一个 Wi-Fi 网络
    - 对于互联网访问：使用 ngrok 或类似服务，但请注意 ngrok 的免费版有连接时长限制

- **调试（Debugging）：** 如果服务未能按预期工作，请检查以下内容：
    - **浏览器开发者工具：** 在手机浏览器（或电脑浏览器）中打开开发者工具（通常按 F12），查看控制台是否有错误信息
    - **服务器日志：** 检查运行 Flask 应用时的终端输出，查看是否有错误信息
    - **网络连接：** 确认客户端（手机或其他设备）可以访问服务器（使用 ping 测试）
    - **防火墙设置：** 确保您的防火墙允许 3000 端口的流量

通过遵循本指南，您将能够在本地计算机上成功部署一个功能齐全的实时 YOLOv8 对象检测 Web 服务，并通过手机或其他设备进行访问和交互。