#!/bin/bash
cd "$(dirname "$0")"  # 切换到脚本所在目录
source venv/bin/activate  # 激活虚拟环境
python app.py  # 运行 Flask 应用
