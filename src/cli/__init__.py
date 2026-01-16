"""命令行界面模块"""

# 直接导入main模块，避免使用src路径
try:
    from .main import cli
except ImportError:
    # 如果相对导入失败，使用绝对导入
    from cli.main import cli

__all__ = ['cli']