"""容器镜像服务(SWR)客户端"""

from typing import Any, Dict, Optional
from urllib.parse import quote, urlencode

from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class SWRClient:
    """容器镜像服务客户端（终端节点 crs-global.ctapi.ctyun.cn）"""

    ENDPOINT = 'crs-global.ctapi.ctyun.cn'

    def __init__(self, client):
        self.client = client
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def _get(self, path: str, region_id: str, query_params: Optional[Dict[str, Any]] = None,
             desc: str = 'SWR查询') -> Dict[str, Any]:
        url = f'https://{self.ENDPOINT}{path}'
        qp = {k: str(v).lower() if isinstance(v, bool) else str(v)
              for k, v in (query_params or {}).items() if v is not None}
        try:
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=qp, body='',
                extra_headers={'regionId': region_id})
            # 与签名编码保持一致（quote 空格->%20），避免 requests params= 编码差异导致 403
            encoded_qs = urlencode(qp, quote_via=quote)
            response = self.client.session.get(f"{url}?{encoded_qs}", headers=headers,
                                               timeout=30)
            logger.debug(f"{desc}响应: {response.text[:500]}")
            if response.status_code != 200:
                return {'statusCode': response.status_code,
                        'message': f'HTTP {response.status_code}: {response.text[:200]}',
                        'returnObj': None}
            return response.json()
        except Exception as e:
            logger.error(f"{desc}失败: {e}")
            return {'statusCode': 500, 'message': str(e), 'returnObj': None}

    def list_instances(self, region_id: str, instance_name: Optional[str] = None,
                       all_region: bool = False, page_num: int = 1,
                       page_size: int = 50) -> Dict[str, Any]:
        """查询镜像实例列表 - GET /v2/listInstance

        Args:
            region_id: 资源池ID（header regionId）
            instance_name: 实例名称（包含匹配，可选）
            all_region: 是否查询所有资源池的实例
            page_num: 页码（默认1）
            page_size: 每页数量（默认50）
        """
        logger.info(f"查询SWR实例列表: regionId={region_id}, allRegion={all_region}")
        return self._get('/v2/listInstance', region_id, {
            'instanceName': instance_name, 'allRegion': all_region,
            'pageNum': page_num, 'pageSize': page_size}, desc='查询SWR实例列表')

    def list_repositories(self, region_id: str, instance_id: str,
                          page_num: int = 1,
                          page_size: int = 50) -> Dict[str, Any]:
        """查询镜像仓库列表 - GET /v2/listRepository

        Args:
            region_id: 实例所属资源池ID（header regionId，取实例列表返回的region）
            instance_id: 实例ID
            page_num: 页码（默认1）
            page_size: 每页数量（默认50）
        """
        logger.info(f"查询SWR镜像仓库列表: regionId={region_id}, instanceId={instance_id}")
        return self._get('/v2/listRepository', region_id, {
            'instanceId': instance_id, 'pageNum': page_num,
            'pageSize': page_size}, desc='查询SWR镜像仓库列表')
