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

    def _post_price(self, path: str, body: Dict[str, Any], desc: str) -> Dict[str, Any]:
        import json as _json
        url = f'https://{self.base_endpoint}{path}'
        body_str = _json.dumps(body)
        try:
            headers = self.eop_auth.sign_request(method='POST', url=url, query_params={}, body=body_str, extra_headers={})
            response = self.client.session.post(url, json=body, headers=headers, timeout=30)
            if response.status_code != 200:
                return {'statusCode': response.status_code, 'message': f'HTTP {response.status_code}', 'returnObj': None}
            return response.json()
        except Exception as e:
            logger.error(f"{desc}失败: {e}")
            return {'statusCode': 500, 'message': str(e), 'returnObj': None}

    def create_price(self, region_id, order_num, cycle_type, sfs_size, volume_type, cycle_cnt):
        return self._post_price('/v4/sfs/new-order/query-prices',
            {'regionID': region_id, 'orderNum': order_num, 'cycleType': cycle_type, 'sfsSize': sfs_size, 'volumeType': volume_type, 'cycleCnt': cycle_cnt}, 'SFS订购询价')

    def expand_price(self, region_id, sfs_uid, sfs_size):
        return self._post_price('/v4/sfs/upgrade-order/query-prices',
            {'regionID': region_id, 'sfsUID': sfs_uid, 'sfsSize': sfs_size}, 'SFS扩容询价')

    def renew_price(self, region_id, sfs_uid, cycle_type, cycle_cnt):
        return self._post_price('/v4/sfs/renew-order/query-prices',
            {'regionID': region_id, 'sfsUID': sfs_uid, 'cycleType': cycle_type, 'cycleCnt': cycle_cnt}, 'SFS续订询价')
