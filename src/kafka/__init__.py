"""
分布式消息服务(Kafka)模块
"""

from .client import KafkaClient
from .commands import kafka

__all__ = ['KafkaClient', 'kafka']
