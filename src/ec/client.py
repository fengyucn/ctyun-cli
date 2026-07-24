"""云间高速(EC)客户端"""

from typing import Dict, Any, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class ECClient:
    """天翼云云间高速(EC)客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.base_endpoint = 'ec-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
        self.timeout = 30

    def _post(self, path: str, body: Dict[str, Any], desc: str) -> Dict[str, Any]:
        """通用 POST 请求"""
        url = f'https://{self.base_endpoint}{path}'
        body_str = json.dumps(body)
        try:
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={}, body=body_str, extra_headers={})
            response = self.client.session.post(url, json=body, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return {'statusCode': response.status_code,
                        'message': f'HTTP {response.status_code}: {response.text}',
                        'returnObj': None}
            return response.json()
        except Exception as e:
            logger.error(f"{desc}失败: {e}")
            return {'statusCode': 500, 'message': str(e), 'returnObj': None}

    # ==================== 询价 API（3个） ====================

    def packet_query_price_new(self, region_id: str, ec_id: str,
                               bandwidth: int, cycle_type: str,
                               cycle_count: int, on_demand: bool = False) -> Dict[str, Any]:
        """云间高速带宽包询价 - POST /v4/ec/packet/query-price-new"""
        return self._post('/v4/ec/packet/query-price-new',
                          {'regionID': region_id, 'ecID': ec_id,
                           'bandwidth': bandwidth, 'cycleType': cycle_type,
                           'cycleCount': cycle_count, 'onDemand': on_demand},
                          '云间高速带宽包询价')

    def packet_query_price_upgrade(self, region_id: str, ec_id: str,
                                   bandwidth: int, resource_id: str) -> Dict[str, Any]:
        """云间高速带宽包升配询价 - POST /v4/ec/packet/query-price-upgrade"""
        return self._post('/v4/ec/packet/query-price-upgrade',
                          {'regionID': region_id, 'ecID': ec_id,
                           'bandwidth': bandwidth, 'resourceID': resource_id},
                          '云间高速带宽包升配询价')

    def packet_query_price_renew(self, region_id: str, ec_id: str,
                                 resource_id: str,
                                 cycle_type: str, cycle_count: int) -> Dict[str, Any]:
        """云间高速带宽包续订询价 - POST /v4/ec/packet/query-price-renew"""
        return self._post('/v4/ec/packet/query-price-renew',
                          {'regionID': region_id, 'ecID': ec_id,
                           'resourceID': resource_id,
                           'cycleType': cycle_type, 'cycleCount': cycle_count},
                          '云间高速带宽包续订询价')
