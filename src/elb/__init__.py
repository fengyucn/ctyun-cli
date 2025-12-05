"""
天翼云弹性负载均衡服务模块
提供负载均衡器、目标组、监听器等ELB资源的查询和管理功能
"""

from elb.client import ELBClient

__all__ = ['ELBClient']