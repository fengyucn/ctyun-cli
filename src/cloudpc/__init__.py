"""
云电脑(CloudPC)模块
"""

from .client import CloudPCClient
from .commands import cloudpc

__all__ = ['CloudPCClient', 'cloudpc']
