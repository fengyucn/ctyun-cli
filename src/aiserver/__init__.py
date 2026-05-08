"""
模型推理服务(AIServer)模块
"""

from .client import AIServerClient
from .commands import aiserver

__all__ = ['AIServerClient', 'aiserver']
