"""
弹性负载均衡(ELB)管理模块 - 使用OpenAPI V4
"""

from typing import Dict, Any, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class ELBClient:
    """弹性负载均衡客户端 - OpenAPI V4"""

    def __init__(self, client: CTYUNClient):
        """
        初始化ELB客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'elb'
        self.base_endpoint = 'ctelb-global.ctapi.ctyun.cn'
        # 初始化EOP签名认证器
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def list_load_balancers(self, region_id: str, ids: Optional[str] = None,
                          resource_type: Optional[str] = None, name: Optional[str] = None,
                          subnet_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查看负载均衡实例列表

        Args:
            region_id: 区域ID (必填)
            ids: 负载均衡ID列表，以,分隔
            resource_type: 资源类型。internal：内网负载均衡，external：公网负载均衡
            name: 负载均衡器名称
            subnet_id: 子网ID

        Returns:
            负载均衡器列表信息
        """
        logger.info(f"查询负载均衡实例列表: regionId={region_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/list-loadbalancer'

            query_params = {
                'regionID': region_id
            }

            # 添加可选查询参数
            if ids:
                query_params['IDs'] = ids
            if resource_type:
                query_params['resourceType'] = resource_type
            if name:
                query_params['name'] = name
            if subnet_id:
                query_params['subnetID'] = subnet_id

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body=None
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_code = data.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = data.get('description', '未知错误')
                raise Exception(f"ELB API错误 [{error_code}]: {error_msg}")

            logger.info(f"成功获取负载均衡实例列表，返回{len(data.get('returnObj', []))}条记录")
            return data

        except Exception as e:
            logger.error(f"查询负载均衡实例列表失败: {str(e)}")
            raise

    def get_load_balancer(self, region_id: str, elb_id: str) -> Dict[str, Any]:
        """
        查看负载均衡实例详情

        Args:
            region_id: 区域ID
            elb_id: 负载均衡器ID

        Returns:
            负载均衡器详细信息
        """
        logger.info(f"查询负载均衡实例详情: regionId={region_id}, elbId={elb_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/show-loadbalancer'

            query_params = {
                'regionID': region_id,
                'elbID': elb_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body=None
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_code = data.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = data.get('description', '未知错误')
                raise Exception(f"ELB API错误 [{error_code}]: {error_msg}")

            # 从returnObj数组中获取第一个元素（详情API返回的是单元素数组）
            return_obj = data.get('returnObj', [])
            if not return_obj:
                raise Exception("未找到指定的负载均衡实例")

            logger.info("成功获取负载均衡实例详情")
            return data

        except Exception as e:
            logger.error(f"查询负载均衡实例详情失败: {str(e)}")
            raise

    def list_target_groups(self, region_id: str, ids: Optional[str] = None,
                           vpc_id: Optional[str] = None, health_check_id: Optional[str] = None,
                           name: Optional[str] = None, client_token: Optional[str] = None) -> Dict[str, Any]:
        """
        查看后端主机组列表

        Args:
            region_id: 区域ID (必填)
            ids: 后端主机组ID列表，以,分隔
            vpc_id: VPC ID
            health_check_id: 健康检查ID
            name: 后端主机组名称
            client_token: 客户端存根，用于保证订单幂等性

        Returns:
            后端主机组列表信息
        """
        logger.info(f"查询后端主机组列表: regionId={region_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/list-target-group'

            query_params = {
                'regionID': region_id
            }

            # 添加可选查询参数
            if ids:
                query_params['IDs'] = ids
            if vpc_id:
                query_params['vpcID'] = vpc_id
            if health_check_id:
                query_params['healthCheckID'] = health_check_id
            if name:
                query_params['name'] = name
            if client_token:
                query_params['clientToken'] = client_token

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body=None
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_code = data.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = data.get('description', '未知错误')
                raise Exception(f"ELB API错误 [{error_code}]: {error_msg}")

            logger.info(f"成功获取后端主机组列表，返回{len(data.get('returnObj', []))}条记录")
            return data

        except Exception as e:
            logger.error(f"查询后端主机组列表失败: {str(e)}")
            raise

    def list_targets(self, region_id: str, target_group_id: Optional[str] = None,
                     ids: Optional[str] = None) -> Dict[str, Any]:
        """
        查看后端主机列表

        Args:
            region_id: 区域ID (必填)
            target_group_id: 后端主机组ID
            ids: 后端主机ID列表，以,分隔

        Returns:
            后端主机列表信息
        """
        logger.info(f"查询后端主机列表: regionId={region_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/list-target'

            query_params = {
                'regionID': region_id
            }

            # 添加可选查询参数
            if target_group_id:
                query_params['targetGroupID'] = target_group_id
            if ids:
                query_params['IDs'] = ids

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body=None
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_code = data.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = data.get('description', '未知错误')
                raise Exception(f"ELB API错误 [{error_code}]: {error_msg}")

            logger.info(f"成功获取后端主机列表，返回{len(data.get('returnObj', []))}条记录")
            return data

        except Exception as e:
            logger.error(f"查询后端主机列表失败: {str(e)}")
            raise

    def get_target_group(self, region_id: str, target_group_id: str) -> Dict[str, Any]:
        """
        查看后端主机组详情

        Args:
            region_id: 区域ID (必填)
            target_group_id: 后端主机组ID (必填)

        Returns:
            后端主机组详细信息
        """
        logger.info(f"查询后端主机组详情: regionId={region_id}, targetGroupId={target_group_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/show-target-group'

            query_params = {
                'regionID': region_id,
                'targetGroupID': target_group_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body=None
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_code = data.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = data.get('description', '未知错误')
                raise Exception(f"ELB API错误 [{error_code}]: {error_msg}")

            # 从returnObj数组中获取第一个元素（详情API返回的是单元素数组）
            return_obj = data.get('returnObj', [])
            if not return_obj:
                raise Exception("未找到指定的后端主机组")

            logger.info("成功获取后端主机组详情")
            return data

        except Exception as e:
            logger.error(f"查询后端主机组详情失败: {str(e)}")
            raise