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
   http://localhost:3000
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
- 前端：React, Bootstrap
- 深度学习：YOLOv8预训练模型

## 项目文档

- [基于 YOLOv8 的实时对象检测.md](基于%20YOLOv8%20的实时对象检测.md) - 详细的实现指南
- [项目报告书.md](项目报告书.md) - 完整的项目技术报告
- [project_report.md](project_report.md) - Project technical report (English version)

## 开源许可

本项目采用MIT许可证。详情请查看项目根目录下的[LICENSE](/LICENSE)文件。
