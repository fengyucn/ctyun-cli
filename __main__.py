#!/usr/bin/env python3
"""
天翼云CLI工具主入口
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli.main import cli

if __name__ == '__main__':
    cli()