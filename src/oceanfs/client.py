"""海量文件服务(OceanFS)客户端"""

import json
from typing import Dict, Any, Optional
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class OceanFSClient:
    """天翼云海量文件服务(OceanFS)客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化海量文件服务客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'oceanfs'
        self.base_endpoint = 'oceanfs-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def renew_order_query_prices(self, region_id: str, sfs_uid: str,
                                  cycle_type: str, cycle_cnt: int) -> Dict[str, Any]:
        """
        续订文件系统询价 - POST /v4/oceanfs/renew-order/query-prices

        Args:
            region_id: 资源池ID
            sfs_uid: 文件系统ID
            cycle_type: 订购周期类型 year(年) / month(月)
            cycle_cnt: 周期数量 (year:1-3, month:1-36)

        Returns:
            询价结果，包含 totalPrice / finalPrice / subOrderPrices
        """
        logger.info(f"续订文件系统询价: regionID={region_id}, sfsUID={sfs_uid}, "
                    f"cycleType={cycle_type}, cycleCnt={cycle_cnt}")

        url = f'https://{self.base_endpoint}/v4/oceanfs/renew-order/query-prices'
        body_data = {
            'regionID': region_id,
            'sfsUID': sfs_uid,
            'cycleType': cycle_type,
            'cycleCnt': cycle_cnt,
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
            logger.error(f"续订文件系统询价失败: {str(e)}")
            raise

    def upgrade_order_query_prices(self, region_id: str, sfs_uid: str,
                                    sfs_size: int) -> Dict[str, Any]:
        """
        扩容文件系统询价 - POST /v4/oceanfs/upgrade-order/query-prices

        Args:
            region_id: 资源池ID
            sfs_uid: 文件系统ID
            sfs_size: 扩容后的文件系统容量大小(GB)

        Returns:
            询价结果，包含 totalPrice / finalPrice / subOrderPrices
        """
        logger.info(f"扩容文件系统询价: regionID={region_id}, sfsUID={sfs_uid}, sfsSize={sfs_size}")

        url = f'https://{self.base_endpoint}/v4/oceanfs/upgrade-order/query-prices'
        body_data = {
            'regionID': region_id,
            'sfsUID': sfs_uid,
            'sfsSize': sfs_size,
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
            logger.error(f"扩容文件系统询价失败: {str(e)}")
            raise
