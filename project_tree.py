#!/usr/bin/env python3
"""
项目结构可视化工具 - 生成项目树形结构图
"""

import os
import argparse
from pathlib import Path


def tree(directory, ignore=None, level=0, max_level=None, prefix=""):
    """生成目录树形结构"""
    if ignore is None:
        ignore = [".git", "__pycache__", "face_recog_env", "venv", "node_modules", ".vscode"]

    if max_level is not None and level > max_level:
        return ""

    space = "│   " * level
    branch = "├── "
    tee = "│   "
    last = "└── "

    result = ""
    
    # 获取目录中的项目并排序
    items = os.listdir(directory)
    items = sorted([item for item in items if item not in ignore])
    
    # 计算非隐藏目录和文件
    visible_items = [item for item in items if not item.startswith('.')]

    # 遍历目录中的项目
    for i, item in enumerate(visible_items):
        path = Path(directory) / item
        
        # 确定是否为最后一项
        is_last = i == len(visible_items) - 1
        curr_prefix = prefix + (last if is_last else branch)
        next_prefix = prefix + ("    " if is_last else tee)
        
        # 输出当前项
        result += f"{curr_prefix}{item}\n"
        
        # 如果是目录，递归生成子目录树
        if path.is_dir() and item not in ignore:
            result += tree(path, ignore, level + 1, max_level, next_prefix)
    
    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生成项目目录树')
    parser.add_argument('-d', '--directory', default='.', help='要生成树形图的目录路径')
    parser.add_argument('-l', '--level', type=int, default=3, help='最大深度级别')
    parser.add_argument('-i', '--ignore', nargs='+', default=None, help='要忽略的目录或文件')
    parser.add_argument('-o', '--output', help='输出文件路径，若不指定则打印到控制台')
    
    args = parser.parse_args()
    
    directory = os.path.abspath(args.directory)
    base_name = os.path.basename(directory)
    
    # 生成树形结构
    result = f"# {base_name}\n\n```\n{base_name}\n{tree(directory, args.ignore, max_level=args.level)}\n```"
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"项目结构已保存到 {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
