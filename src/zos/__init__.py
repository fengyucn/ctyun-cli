"""对象存储(ZOS)客户端"""

from .client import ZOSClient
from .commands import zos

__all__ = ['ZOSClient', 'zos']
