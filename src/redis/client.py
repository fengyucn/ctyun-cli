"""
Redis分布式缓存服务API客户端
使用ctyun-cli的EOP签名认证和Redis实例可用区查询功能
"""

import json
from typing import Dict, List, Optional, Any
from src.client import CTYUNClient
from src.auth.eop_signature import CTYUNEOPAuth
from src.utils.helpers import logger


class RedisClient:
    """天翼云Redis分布式缓存服务客户端"""

    def __init__(self, access_key: str, secret_key: str, region_id: str = "200000001852"):
        """
        初始化Redis客户端

        Args:
            access_key (str): 天翼云Access Key
            secret_key (str): 天翼云Secret Key
            region_id (str): 区域ID，默认为200000001852
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.region_id = region_id

        # 使用ctyun-cli的客户端和认证系统
        self.client = CTYUNClient(access_key, secret_key)
        self.eop_auth = CTYUNEOPAuth(access_key, secret_key)

        # Redis服务端点 - 使用正确的API端点
        self.service_endpoint = 'dcs2-global.ctapi.ctyun.cn'
        self.api_path = "/v2/lifeCycleServant"
        self.timeout = 30

    
    def get_zones(self, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例可用区

        Args:
            region_id (str): 区域ID，如果为None则使用默认区域

        Returns:
            Optional[Dict[str, Any]]: 查询结果
        """
        target_region_id = region_id or self.region_id

        logger.info(f"查询Redis可用区: regionId={target_region_id}")

        try:
            # 构建请求URL - 使用正确的Redis API端点
            url = f'https://{self.service_endpoint}{self.api_path}/getZones'

            # 查询参数 - 使用API文档中的参数格式
            query_params = {
                'regionId': target_region_id
            }

            # 额外的请求头 - 根据API文档只需regionId
            extra_headers = {
                'regionId': target_region_id
            }

            # 生成签名请求头
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"查询参数: {query_params}")
            logger.debug(f"请求头: {headers}")

            # 发送请求
            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": f"HTTP {response.status_code}: {response.text}",
                    "response": response.text,
                    "response_headers": dict(response.headers)
                }

            try:
                return response.json()
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {str(e)}")
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": f"JSON解析错误: {str(e)}",
                    "response_text": response.text,
                    "response_headers": dict(response.headers)
                }

        except Exception as e:
            logger.error(f"查询Redis可用区失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def get_zones_summary(self, region_id: str = None) -> Dict[str, Any]:
        """
        获取可用区信息摘要

        Args:
            region_id (str): 区域ID

        Returns:
            Dict[str, Any]: 可用区信息摘要
        """
        result = self.get_zones(region_id)

        if not result:
            return {
                "success": False,
                "message": "查询失败",
                "region_id": region_id or self.region_id,
                "zones_count": 0,
                "zones": []
            }

        if result.get("error"):
            return {
                "success": False,
                "message": result.get("message", "未知错误"),
                "region_id": region_id or self.region_id,
                "zones_count": 0,
                "zones": [],
                "error_details": result
            }

        if result.get("statusCode") == 800:
            # 成功响应，从returnObj.zoneList中获取数据
            return_obj = result.get("returnObj", {})
            zone_list_data = return_obj.get("zoneList", [])
            zone_list = []

            for zone_info in zone_list_data:
                if isinstance(zone_info, dict):
                    zone_list.append({
                        "zone_id": zone_info.get("name", ""),
                        "zone_name": zone_info.get("azDisplayName", zone_info.get("name", "")),
                        "zone_status": "available",  # Redis可用区通常都是可用的
                        "region_id": region_id or self.region_id
                    })

            return {
                "success": True,
                "message": "查询成功",
                "region_id": region_id or self.region_id,
                "zones_count": len(zone_list),
                "zones": zone_list,
                "full_result": result
            }
        else:
            return {
                "success": False,
                "message": result.get("message", f"API返回错误 (statusCode: {result.get('statusCode')})"),
                "region_id": region_id or self.region_id,
                "zones_count": 0,
                "zones": [],
                "error_code": result.get("statusCode"),
                "full_result": result
            }

    def set_timeout(self, timeout: int):
        """
        设置请求超时时间

        Args:
            timeout (int): 超时时间（秒）
        """
        self.timeout = timeout

    def set_region(self, region_id: str):
        """
        设置默认区域ID

        Args:
            region_id (str): 区域ID
        """
        self.region_id = region_id