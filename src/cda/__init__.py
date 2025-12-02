"""
云专线CDA (Cloud Dedicated Access) 服务模块

提供天翼云专线资源的CLI管理功能，包括：
- 专线网关管理
- 物理专线管理
- VPC管理
- 静态路由管理
- BGP路由管理
- 跨账号授权
- 健康检查
- 链路探测

服务端点: cda-global.ctapi.ctyun.cn
"""

from .client import CDA_CLIENT, init_cda_client, get_cda_client

__all__ = ['CDA_CLIENT', 'init_cda_client', 'get_cda_client']