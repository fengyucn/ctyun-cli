"""命令行界面模块"""

import sys
import os

# 修复与系统 redis 包的导入冲突
# 获取当前包（cli）的安装位置，确保同目录下的 redis 包优先被导入
_current_dir = os.path.dirname(os.path.abspath(__file__))
_site_packages = os.path.dirname(_current_dir)

# 将 site-packages 插入到 sys.path 最前面，确保项目的 redis 包优先于系统 redis
if _site_packages in sys.path:
    sys.path.remove(_site_packages)
sys.path.insert(0, _site_packages)

try:
    from .main import cli
except ImportError:
    from cli.main import cli

__all__ = ['cli']