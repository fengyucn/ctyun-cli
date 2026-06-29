"""对象存储(ZOS)客户端"""

import json
from typing import Dict, Any
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class ZOSClient:
    """天翼云对象存储(ZOS)客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.service = 'zos'
        self.base_endpoint = 'zos-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def query_resource_package_price(
        self,
        region_id: str,
        pkg_type: str,
        pkg_spec_type: str,
        pkg_spec: int,
        cycle_cnt: int,
        cycle_type: str,
        order_num: int,
        storage_class: str,
    ) -> Dict[str, Any]:
        """
        询价ZOS资源包 - POST /v4/oss/new-order/query-price

        Args:
            region_id: 区域ID
            pkg_type: 资源包类型 (zosSize/zosMzSize/zosBytesSend/zosRequest/zosRetrievalFlow/zosRetrievalFrequency)
            pkg_spec_type: 资源包规格类型 (fixed/defined)
            pkg_spec: 资源包规格大小(GB)，请求次数包和数据取回次数包单位为万次
            cycle_cnt: 订购周期 (month最大36, year最大3)
            cycle_type: 订购周期类型 (month/year)
            order_num: 订购数量(最大50)
            storage_class: 存储类型 (STANDARD/STANDARD_IA/GLACIER)

        Returns:
            询价结果，包含 totalPrice / discountPrice / finalPrice / subOrderPrices
        """
        logger.info(f"询价ZOS资源包: regionID={region_id}, pkgType={pkg_type}, "
                    f"pkgSpec={pkg_spec}, cycleType={cycle_type}, cycleCnt={cycle_cnt}")

        url = f'https://{self.base_endpoint}/v4/oss/new-order/query-price'
        body_data = {
            'regionID': region_id,
            'pkgType': pkg_type,
            'pkgSpecType': pkg_spec_type,
            'pkgSpec': pkg_spec,
            'cycleCnt': cycle_cnt,
            'cycleType': cycle_type,
            'orderNum': order_num,
            'storageClass': storage_class,
        }
        body = json.dumps(body_data)

        headers = self.eop_auth.sign_request(
            method='POST', url=url, query_params=None, body=body, extra_headers={}
        )

        try:
            response = self.client.session.post(url, data=body, headers=headers, timeout=30)

            if response.status_code != 200:
                return {'statusCode': response.status_code,
                        'message': f'HTTP {response.status_code}: {response.text}',
                        'returnObj': None}

            result = response.json()
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")

            return result

        except Exception as e:
            logger.error(f"询价ZOS资源包失败: {str(e)}")
            raise
