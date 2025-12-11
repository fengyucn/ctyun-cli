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

    def list_listeners(self, region_id: str, ids: Optional[str] = None,
                       name: Optional[str] = None, load_balancer_id: Optional[str] = None,
                       access_control_id: Optional[str] = None, project_id: Optional[str] = '0',
                       client_token: Optional[str] = None) -> Dict[str, Any]:
        """
        查看监听器列表

        Args:
            region_id: 区域ID (必填)
            ids: 监听器ID列表，以,分隔
            name: 监听器名称
            load_balancer_id: 负载均衡实例ID
            access_control_id: 访问控制ID
            project_id: 企业项目ID，默认为'0'
            client_token: 客户端存根，用于保证订单幂等性

        Returns:
            监听器列表信息
        """
        logger.info(f"查询监听器列表: regionId={region_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/list-listener'

            query_params = {
                'regionID': region_id
            }

            # 添加可选查询参数
            if ids:
                query_params['IDs'] = ids
            if name:
                query_params['name'] = name
            if load_balancer_id:
                query_params['loadBalancerID'] = load_balancer_id
            if access_control_id:
                query_params['accessControlID'] = access_control_id
            if project_id:
                query_params['projectID'] = project_id
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

            logger.info(f"成功获取监听器列表，返回{len(data.get('returnObj', []))}条记录")
            return data

        except Exception as e:
            logger.error(f"查询监听器列表失败: {str(e)}")
            raise

    def get_listener(self, region_id: str, listener_id: str, id_param: Optional[str] = None) -> Dict[str, Any]:
        """
        查看监听器详情

        Args:
            region_id: 区域ID (必填)
            listener_id: 监听器ID (必填，推荐使用)
            id_param: 监听器ID (即将废弃，不推荐使用)

        Returns:
            监听器详细信息
        """
        logger.info(f"查询监听器详情: regionId={region_id}, listenerId={listener_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/show-listener'

            query_params = {
                'regionID': region_id
            }

            # 优先使用listenerID参数
            if listener_id:
                query_params['listenerID'] = listener_id
            elif id_param:
                query_params['ID'] = id_param
            else:
                raise Exception("必须提供listenerID参数")

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
                raise Exception("未找到指定的监听器")

            logger.info("成功获取监听器详情")
            return data

        except Exception as e:
            logger.error(f"查询监听器详情失败: {str(e)}")
            raise

    def query_realtime_monitor(self, region_id: str, device_ids: Optional[list] = None,
                               page_no: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        新查看负载均衡实时监控

        Args:
            region_id: 区域ID (必填)
            device_ids: 负载均衡ID列表 (可选)
            page_no: 页码，默认为1
            page_size: 每页数据量，1-50，默认为10

        Returns:
            实时监控数据
        """
        logger.info(f"查询负载均衡实时监控: regionId={region_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/new-query-realtime-monitor'

            # 构建请求体
            request_body = {
                'regionID': region_id,
                'pageNo': page_no,
                'pageSize': page_size
            }

            # 添加可选参数
            if device_ids:
                request_body['deviceIDs'] = device_ids

            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=json.dumps(request_body)
            )

            response = self.client.session.post(
                url,
                json=request_body,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_code = data.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = data.get('description', '未知错误')
                raise Exception(f"ELB API错误 [{error_code}]: {error_msg}")

            monitors = data.get('returnObj', {}).get('monitors', [])
            logger.info(f"成功获取负载均衡实时监控数据，返回{len(monitors)}条记录")
            return data

        except Exception as e:
            logger.error(f"查询负载均衡实时监控失败: {str(e)}")
            raise

    def query_history_monitor(self, region_id: str, device_ids: list, metric_names: list,
                               start_time: str, end_time: str, period: int = 60,
                               page_no: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        新查看负载均衡历史监控

        Args:
            region_id: 区域ID (必填)
            device_ids: 负载均衡ID列表 (必填)
            metric_names: 监控指标列表 (必填)
            start_time: 开始时间，格式: YYYY-mmm-dd HH:MM:SS
            end_time: 结束时间，格式: YYYY-mmm-dd HH:MM:SS
            period: 聚合周期，单位秒，默认60
            page_no: 页码，默认为1
            page_size: 每页数据量，1-50，默认为10

        Returns:
            历史监控数据
        """
        logger.info(f"查询负载均衡历史监控: regionId={region_id}, 设备数量={len(device_ids)}, 指标数量={len(metric_names)}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/new-query-history-monitor'

            # 构建请求体
            request_body = {
                'regionID': region_id,
                'deviceIDs': device_ids,
                'metricNames': metric_names,
                'startTime': start_time,
                'endTime': end_time,
                'period': period,
                'pageNo': page_no,
                'pageSize': page_size
            }

            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=json.dumps(request_body)
            )

            response = self.client.session.post(
                url,
                json=request_body,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 800:
                error_code = data.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = data.get('description', '未知错误')
                raise Exception(f"ELB API错误 [{error_code}]: {error_msg}")

            monitors = data.get('returnObj', {}).get('monitors', [])
            logger.info(f"成功获取负载均衡历史监控数据，返回{len(monitors)}条记录")
            return data

        except Exception as e:
            logger.error(f"查询负载均衡历史监控失败: {str(e)}")
            raise

    def get_health_check(self, region_id: str, health_check_id: str,
                        id_param: Optional[str] = None) -> Dict[str, Any]:
        """
        查看健康检查详情

        Args:
            region_id: 区域ID (必填)
            health_check_id: 健康检查ID (必填，推荐使用)
            id_param: 健康检查ID (即将废弃，不推荐使用)

        Returns:
            健康检查详细信息
        """
        logger.info(f"查询健康检查详情: regionId={region_id}, healthCheckId={health_check_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/elb/show-health-check'

            query_params = {
                'regionID': region_id
            }

            # 优先使用healthCheckID参数
            if health_check_id:
                query_params['healthCheckID'] = health_check_id
            elif id_param:
                query_params['id'] = id_param
            else:
                raise Exception("必须提供healthCheckID参数")

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

            logger.info("成功获取健康检查详情")
            return data

        except Exception as e:
            logger.error(f"查询健康检查详情失败: {str(e)}")
            raise