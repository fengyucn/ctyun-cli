"""命令行界面模块"""

try:
    from .main import cli
except ImportError:
    from cli.main import cli

__all__ = ['cli']
