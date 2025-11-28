"""
容器引擎(CCE)服务模块

天翼云容器引擎（Cloud Container Engine，CCE）是基于Kubernetes的企业级容器化服务平台。
"""

from .client import CCEClient

__all__ = ['CCEClient']