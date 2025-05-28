# YOLOv8对象检测应用

基于YOLOv8模型的实时对象检测Web应用，支持图像上传和实时检测。

## 功能特点

- 图像中对象检测与识别
- 实时对象定位与边界框绘制
- 支持80+类别的物体识别
- 上传图片和摄像头实时检测两种模式

## 快速开始

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 运行应用：
   ```bash
   bash start_app.sh
   # 或直接运行
   python app.py
   ```

3. 在浏览器中访问：
   ```
   http://localhost:5000
   ```

4. 通过ngrok暴露服务（可选）：
   ```bash
   bash start_with_ngrok.sh
   ```

## 使用方法

1. **上传图片模式**：选择图片上传，系统将自动检测并显示识别结果
2. **摄像头模式**：允许访问摄像头，系统将实时检测视频流中的对象

## 技术栈

- 后端：Flask, Ultralytics YOLOv8
- 前端：HTML, JavaScript
- 深度学习：YOLOv8预训练模型

更多详细信息请参考[基于 YOLOv8 的实时对象检测.md](基于%20YOLOv8%20的实时对象检测.md)文档。
