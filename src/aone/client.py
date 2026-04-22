"""边缘安全加速平台(Aone)客户端"""

from typing import Dict, Any, Optional
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class AoneClient:
    """天翼云边缘安全加速平台(Aone)客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化边缘安全加速平台客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'aone'
        self.base_endpoint = 'aone-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
