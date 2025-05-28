#!/bin/bash

# 多媒体Web应用集合安装脚本
# 受MIT许可证保护 - 详见LICENSE文件
# 版权所有 (c) 2025 OpenSource_class_linux FinalHW

echo "=== 多媒体Web应用集合安装脚本 ==="
echo "=== 受MIT许可证保护 ==="
echo

# 检查Python版本
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "检测到Python版本: $python_version"
if [[ $(echo "$python_version < 3.6" | bc) -eq 1 ]]; then
    echo "错误: 需要Python 3.6+版本"
    exit 1
fi
echo "Python版本检查通过"

# 创建全局虚拟环境
echo -n "是否创建全局虚拟环境? (y/n): "
read create_venv
if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo "创建全局虚拟环境..."
    python3 -m venv multimedia_apps_env
    echo "激活虚拟环境..."
    source multimedia_apps_env/bin/activate
fi

# 安装全局依赖
echo -n "是否安装全局依赖? (y/n): "
read install_deps
if [ "$install_deps" = "y" ] || [ "$install_deps" = "Y" ]; then
    echo "安装全局依赖..."
    pip install -r requirements.txt
fi

# 提示安装具体项目
echo
echo "请选择要安装的子项目:"
echo "1. 人脸识别应用 (FaceRecog)"
echo "2. YouTube API视频内容搜索 (YouTube_API)"
echo "3. YOLOv8对象检测 (yolov8_detection)"
echo "4. 全部安装"
echo -n "请输入选项 (1-4): "
read option

case $option in
    1)
        echo "安装人脸识别应用..."
        cd FaceRecog
        python -m venv face_recog_env
        source face_recog_env/bin/activate
        pip install -r requirements.txt
        echo "人脸识别应用安装完成。使用以下命令运行: cd FaceRecog && source face_recog_env/bin/activate && python app.py"
        ;;
    2)
        echo "安装YouTube API视频内容搜索应用..."
        cd YouTube_API
        source setup_env.sh
        bash install_deps.sh
        echo "请确保配置了config.py文件中的API密钥。"
        echo "YouTube API应用安装完成。使用以下命令运行: cd YouTube_API && bash start_app.sh"
        ;;
    3)
        echo "安装YOLOv8对象检测应用..."
        cd yolov8_detection
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        echo "YOLOv8对象检测应用安装完成。使用以下命令运行: cd yolov8_detection && bash start_app.sh"
        ;;
    4)
        echo "安装所有子项目..."
        
        echo "1. 安装人脸识别应用..."
        cd FaceRecog
        python -m venv face_recog_env
        source face_recog_env/bin/activate
        pip install -r requirements.txt
        deactivate
        cd ..
        
        echo "2. 安装YouTube API视频内容搜索应用..."
        cd YouTube_API
        source setup_env.sh
        bash install_deps.sh
        cd ..
        
        echo "3. 安装YOLOv8对象检测应用..."
        cd yolov8_detection
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
        cd ..
        
        echo "所有子项目安装完成。"
        echo "请参考各子项目的README文件了解如何运行各个应用。"
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

# 许可证提示
echo
echo "该项目采用MIT许可证。有关详细信息，请查阅LICENSE文件。"
echo "感谢使用多媒体Web应用集合！"