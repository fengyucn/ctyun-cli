"""
天翼云云日志服务(LTS)客户端
"""

from typing import Dict, Any
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class LTSClient:
    """天翼云云日志服务(LTS)客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.base_endpoint = 'ctlts-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
