"""
天翼云CLI工具
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .client import CTYUNClient, CTYUNAPIError
from .config.settings import ConfigManager, config

__all__ = [
    'CTYUNClient',
    'CTYUNAPIError',
    'ConfigManager',
    'config'
]

def main():
    """CLI主入口函数"""
    from .cli.main import cli
    cli()