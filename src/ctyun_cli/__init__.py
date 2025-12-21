"""
ctyun-cli 包入口点
"""

__version__ = "1.7.12"

# 创建一个简单的CLI入口点
try:
    from cli.main import cli
except ImportError:
    # 如果直接导入失败，创建一个fallback
    import sys
    import os

    # 添加当前包路径到sys.path
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from cli.main import cli

__all__ = ['cli']