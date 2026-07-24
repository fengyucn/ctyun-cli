"""微服务引擎(MSE)客户端"""

from typing import Dict, Any, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class MSEClient:
    """天翼云微服务引擎(MSE)客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.base_endpoint = 'mse-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
        self.timeout = 30

    def _post(self, path: str, body: Dict[str, Any], desc: str,
              region_id: Optional[str] = None) -> Dict[str, Any]:
        """通用 POST 请求"""
        url = f'https://{self.base_endpoint}{path}'
        body_str = json.dumps(body)
        extra_headers = {}
        if region_id:
            extra_headers['regionID'] = region_id
        try:
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={}, body=body_str,
                extra_headers=extra_headers)
            response = self.client.session.post(url, json=body, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return {'statusCode': response.status_code,
                        'message': f'HTTP {response.status_code}: {response.text}',
                        'returnObj': None}
            return response.json()
        except Exception as e:
            logger.error(f"{desc}失败: {e}")
            return {'statusCode': 500, 'message': str(e), 'returnObj': None}

    # ==================== 询价 API（1个） ====================

    def query_create_price(self, auto_pay: str, engine_type: str,
                           cycle_type: str, cycle_cnt: str,
                           auto_renew_cycle_type: str, auto_renew_cycle_count: str,
                           instance_num: int, cpu_num: int,
                           region_id: Optional[str] = None,
                           auto_renew_status: Optional[str] = None) -> Dict[str, Any]:
        """订购询价 - POST /rcc/v1/order/queryPrice"""
        body = {
            'autoPay': auto_pay,
            'engineType': engine_type,
            'cycleType': cycle_type,
            'cycleCnt': cycle_cnt,
            'autoRenewCycleType': auto_renew_cycle_type,
            'autoRenewCycleCount': auto_renew_cycle_count,
            'instanceNum': instance_num,
            'cpuNum': cpu_num,
        }
        if auto_renew_status:
            body['autoRenewStatus'] = auto_renew_status
        return self._post('/rcc/v1/order/queryPrice', body, 'MSE订购询价', region_id)
