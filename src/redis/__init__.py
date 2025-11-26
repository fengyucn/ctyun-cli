"""
Redis分布式缓存服务模块
提供Redis实例管理、可用区查询等功能
"""

from redis.client import RedisClient
from redis.commands import redis_group

__all__ = ['RedisClient', 'redis_group']