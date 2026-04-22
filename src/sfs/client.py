"""弹性文件服务(SFS)客户端"""

from typing import Dict, Any, Optional
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class SFSClient:
    """天翼云弹性文件服务(SFS)客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化弹性文件服务客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'sfs'
        self.base_endpoint = 'ctsfs-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
