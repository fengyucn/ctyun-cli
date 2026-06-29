"""物理机(DPS)管理模块"""

from .client import DPSClient
from .commands import dps

__all__ = ['DPSClient', 'dps']
