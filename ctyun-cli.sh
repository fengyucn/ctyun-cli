#!/bin/bash

# 天翼云CLI工具启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

# 检查依赖是否安装
if ! python3 -c "import requests, click, yaml" &> /dev/null; then
    echo "正在安装依赖..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

# 设置Python路径
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# 运行CLI工具
python3 -m ctyun-cli "$@"