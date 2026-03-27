"""命令行界面模块"""

import sys
import os

# 确保 src/ 目录排在 sys.path 最前面，避免系统级同名包（如 redis）覆盖项目包
_src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)
elif sys.path[0] != _src_path:
    sys.path.remove(_src_path)
    sys.path.insert(0, _src_path)

try:
    from .main import cli
except ImportError:
    from cli.main import cli

__all__ = ['cli']