"""
Redis分布式缓存服务API客户端
使用ctyun-cli的EOP签名认证和Redis实例可用区查询功能
"""

import json
from typing import Dict, List, Optional, Any
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class RedisClient:
    """天翼云Redis分布式缓存服务客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化Redis客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.region_id = getattr(client, 'region_id', "200000001852")  # 确保region_id不为None

        # 初始化EOP签名认证器
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

        # Redis服务端点 - 使用正确的API端点
        self.service_endpoint = 'https://dcs2-global.ctapi.ctyun.cn'
        self.api_path = "/v2/lifeCycleServant"
        self.timeout = 30

    def describe_instances(self, region_id: str = None, instance_name: str = None,
                         status: str = None, page_num: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例列表

        Args:
            region_id (str): 区域ID，如果为None则使用默认区域
            instance_name (str): 实例名称，支持模糊查询
            status (str): 实例状态 (Creating, Running, Configuring, Restarting, Stopping, Stopped, Deleting, Error)
            page_num (int): 页码，默认1
            page_size (int): 每页数量，默认20，最大100

        Returns:
            Optional[Dict[str, Any]]: 查询结果
        """
        target_region_id = region_id or self.region_id or "200000001852"

        logger.info(f"查询Redis实例列表: regionId={target_region_id}, name={instance_name}, status={status}")

        try:
            # 构建请求URL - 使用正确的API端点
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeInstances'

            # 查询参数 - 使用正确的参数名
            query_params = {
                'pageIndex': str(page_num or 1),
                'pageSize': str(min(page_size or 20, 100))  # 限制最大100
            }

            # 可选参数
            if instance_name:
                query_params['instanceName'] = instance_name
            # 注意：status参数在新API中不存在，需要移除

            extra_headers = {
                'regionId': target_region_id or '200000001852'
            }

            # 生成签名请求头
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url=url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') == 800:
                return data
            else:
                logger.error(f"查询Redis实例列表失败: {data}")
                return None

        except Exception as e:
            logger.error(f"查询Redis实例列表异常: {str(e)}")
            return None


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
            url = f'{self.service_endpoint}{self.api_path}/getZones'

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

    # ========== 查询类API方法 ==========

    def describe_instances_overview(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例基础详情

        Args:
            instance_id (str): 实例ID

        Returns:
            Optional[Dict[str, Any]]: 实例详情信息
        """
        logger.info(f"查询Redis实例详情: instanceId={instance_id}")

        try:
            url = f'{self.service_endpoint}{self.api_path}/describeInstancesOverview'

            query_params = {
                'instanceId': instance_id,
                'regionId': self.region_id
            }

            extra_headers = {}

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询实例详情失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_instance_config(self, instance_id: str, param_name: str = None) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例配置参数

        Args:
            instance_id (str): 实例ID
            param_name (str, optional): 参数名称，查询单个参数

        Returns:
            Optional[Dict[str, Any]]: 配置参数信息
        """
        logger.info(f"查询Redis实例配置: instanceId={instance_id}, param={param_name}")

        try:
            url = f'{self.service_endpoint}/v2/configServant/describeInstanceConfig'

            query_params = {
                'instanceId': instance_id
            }

            if param_name:
                query_params['paramName'] = param_name

            extra_headers = {
                'regionId': self.region_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询实例配置失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_history_monitor_items(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例性能监控指标列表

        Args:
            instance_id (str): 实例ID

        Returns:
            Optional[Dict[str, Any]]: 监控指标列表
        """
        logger.info(f"查询Redis监控指标列表: instanceId={instance_id}")

        try:
            url = f'{self.service_endpoint}/v2/monitorServant/describeHistoryMonitorItems'

            query_params = {
                'instanceId': instance_id
            }

            extra_headers = {
                'regionId': self.region_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询监控指标列表失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_instance_history_monitor_values(
        self,
        instance_id: str,
        metric_name: str,
        start_time: str,
        end_time: str,
        period: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例性能监控历史数据

        Args:
            instance_id (str): 实例ID
            metric_name (str): 指标名称（如memory_fragmentation, memory_usage等）
            start_time (str): 开始时间（格式：2025-11-21T09:26:08Z）
            end_time (str): 结束时间（格式：2025-11-25T09:26:08Z）
            period (int): 数据聚合周期（秒）

        Returns:
            Optional[Dict[str, Any]]: 监控历史数据
        """
        logger.info(f"查询Redis监控历史数据: instanceId={instance_id}, metric={metric_name}")

        try:
            url = f'{self.service_endpoint}/v2/monitorServant/describeInstanceHistoryMonitorValues'

            query_params = {
                'instanceId': instance_id,
                'metricName': metric_name,
                'startTime': start_time,
                'endTime': end_time,
                'period': period
            }

            extra_headers = {
                'regionId': self.region_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询监控历史数据失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_node_history_monitor_values(
        self,
        instance_id: str,
        node_id: str,
        metric_name: str,
        start_time: str,
        end_time: str,
        period: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        查询Redis节点性能监控历史数据

        Args:
            instance_id (str): 实例ID
            node_id (str): 节点ID
            metric_name (str): 指标名称
            start_time (str): 开始时间
            end_time (str): 结束时间
            period (int): 数据聚合周期

        Returns:
            Optional[Dict[str, Any]]: 节点监控历史数据
        """
        logger.info(f"查询Redis节点监控数据: instanceId={instance_id}, nodeId={node_id}, metric={metric_name}")

        try:
            url = f'{self.service_endpoint}/v2/monitorServant/describeNodeHistoryMonitorValues'

            query_params = {
                'instanceId': instance_id,
                'nodeId': node_id,
                'metricName': metric_name,
                'startTime': start_time,
                'endTime': end_time,
                'period': period
            }

            extra_headers = {
                'regionId': self.region_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询节点监控数据失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def do_analysis_instance_tasks(self, instance_id: str, node_name: str = None) -> Optional[Dict[str, Any]]:
        """
        执行Redis实例诊断分析

        Args:
            instance_id (str): 实例ID
            node_name (str, optional): 节点名称

        Returns:
            Optional[Dict[str, Any]]: 诊断任务结果
        """
        logger.info(f"启动Redis实例诊断: instanceId={instance_id}, node={node_name}")

        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/doAnalysisInstanceTasks'

            request_body = {
                'prodInstId': instance_id
            }

            if node_name:
                request_body['nodeName'] = node_name

            extra_headers = {
                'regionId': self.region_id,
                'Content-Type': 'application/json'
            }

            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params={},
                body=json.dumps(request_body),
                extra_headers=extra_headers
            )

            response = self.client.session.post(
                url,
                json=request_body,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"启动实例诊断失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def query_analysis_instance_tasks_info(self, instance_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例诊断分析报告详情

        Args:
            instance_id (str): 实例ID
            task_id (str): 任务ID

        Returns:
            Optional[Dict[str, Any]]: 诊断分析报告详情
        """
        logger.info(f"查询Redis诊断报告: instanceId={instance_id}, taskId={task_id}")

        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/queryAnalysisInstanceTasksInfo'

            query_params = {
                'prodInstId': instance_id,
                'taskId': task_id
            }

            extra_headers = {
                'regionId': self.region_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询诊断报告失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def get_client_ip_info(self, instance_id: str, node_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例客户端会话列表

        Args:
            instance_id (str): 实例ID
            node_id (str, optional): 节点ID

        Returns:
            Optional[Dict[str, Any]]: 客户端会话信息
        """
        logger.info(f"查询Redis客户端会话: instanceId={instance_id}, nodeId={node_id}")

        try:
            url = f'{self.service_endpoint}/v2/monitorServant/getClientIPInfo'

            query_params = {
                'instanceId': instance_id
            }

            if node_id:
                query_params['nodeId'] = node_id

            extra_headers = {
                'regionId': self.region_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询客户端会话失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_instance_version(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例版本信息

        Args:
            instance_id (str): 实例ID

        Returns:
            Optional[Dict[str, Any]]: 版本信息
        """
        logger.info(f"查询Redis实例版本: instanceId={instance_id}")

        try:
            url = f'{self.service_endpoint}/v2/instanceServant/describeInstanceVersion'

            query_params = {
                'instanceId': instance_id
            }

            extra_headers = {
                'regionId': self.region_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询实例版本失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_db_instance_net_info(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例网络信息

        Args:
            instance_id (str): 实例ID

        Returns:
            Optional[Dict[str, Any]]: 网络信息
        """
        logger.info(f"查询Redis实例网络信息: instanceId={instance_id}")

        try:
            url = f'{self.service_endpoint}/v2/networkServant/describeDBInstanceNetInfo'

            query_params = {
                'instanceId': instance_id
            }

            extra_headers = {
                'regionId': self.region_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询网络信息失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def create_instance(self, instance_name: str, edition: str, version: str, capacity: int,
                       shard_count: int, copies_count: int, region_id: str, availability_zone: str,
                       vpc_id: str, subnet_id: str, password: str, product_type: str = "PayPerUse",
                       charge_mode: str = "PayPerUse", period: int = None, period_unit: str = "Month",
                       auto_renew: bool = False, enterprise_project_id: str = "0",
                       description: str = None) -> Optional[Dict[str, Any]]:
        """
        创建Redis实例

        Args:
            instance_name (str): 实例名称，长度不超过60个字符
            edition (str): 实例版本类型，可选值：Basic(基础版), Enhance(增强版), Classic(经典版)
            version (str): Redis版本号
            capacity (int): 实例容量，单位GB
            shard_count (int): 分片数量
            copies_count (int): 副本数量
            region_id (str): 区域ID
            availability_zone (str): 可用区
            vpc_id (str): VPC网络ID
            subnet_id (str): 子网ID
            password (str): 访问密码，长度8-32位字符
            product_type (str): 产品类型，默认PayPerUse（按需付费）
            charge_mode (str): 计费模式
            period (int): 购买时长（包年包月时需要）
            period_unit (str): 购买时长单位，默认Month
            auto_renew (bool): 是否自动续费，默认false
            enterprise_project_id (str): 企业项目ID，默认0
            description (str): 实例描述

        Returns:
            Optional[Dict[str, Any]]: 创建结果
        """
        logger.info(f"创建Redis实例: {instance_name}")

        try:
            # 构建请求URL
            url = f'{self.service_endpoint}{self.api_path}/createInstance'

            # 构建请求体
            request_body = {
                "instanceName": instance_name,
                "edition": edition,
                "version": version,
                "capacity": capacity,
                "shardCount": shard_count,
                "copiesCount": copies_count,
                "regionId": region_id,
                "availabilityZone": availability_zone,
                "vpcId": vpc_id,
                "subnetId": subnet_id,
                "password": password,
                "productType": product_type,
                "chargeMode": charge_mode,
                "autoRenew": auto_renew,
                "enterpriseProjectId": enterprise_project_id
            }

            # 可选参数
            if period:
                request_body["period"] = period
                request_body["periodUnit"] = period_unit

            if description:
                request_body["description"] = description

            extra_headers = {
                'regionId': region_id,
                'Content-Type': 'application/json'
            }

            # 生成签名请求头
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params={},
                body=json.dumps(request_body),
                extra_headers=extra_headers
            )

            # 发送请求
            response = self.client.session.post(
                url,
                json=request_body,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            result = response.json()

            # 检查API响应状态
            if result.get("statusCode") == 800:
                logger.info(f"Redis实例创建成功: {instance_name}")
                return result
            else:
                error_msg = result.get("message", "未知错误")
                error_code = result.get("statusCode", "N/A")
                logger.error(f"Redis实例创建失败 (错误码: {error_code}): {error_msg}")
                return {
                    "error": True,
                    "error_code": error_code,
                    "message": error_msg,
                    "response": result
                }

        except Exception as e:
            logger.error(f"创建Redis实例异常: {str(e)}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def create_instance_v2(self, **kwargs) -> Optional[Dict[str, Any]]:
        """
        创建Redis实例 - 支持完整的API v270参数

        Args:
            **kwargs: 支持以下25+个参数
                计费相关:
                    chargeType (str): 计费模式 PrePaid/PostPaid
                    period (int): 购买时长月数
                    autoPay (bool): 是否自动付费
                    size (int): 购买数量
                    autoRenew (bool): 是否自动续订
                    autoRenewPeriod (str): 自动续费时长

                实例配置:
                    version (str): 版本类型 BASIC/PLUS/Classic
                    edition (str): 实例类型 (必需)
                    engineVersion (str): Redis引擎版本 (必需)
                    zoneName (str): 主可用区名称 (必需)
                    secondaryZoneName (str): 备可用区名称
                    hostType (str): 主机类型
                    shardMemSize (str): 分片规格GB
                    shardCount (int): 分片数
                    capacity (str): 存储容量GB (仅Classic版本)
                    copiesCount (int): 副本数
                    dataDiskType (str): 磁盘类型 SSD/SAS

                网络配置:
                    vpcId (str): 虚拟私有云ID (必需)
                    subnetId (str): 所在子网ID (必需)
                    secgroups (str): 安全组ID (必需)
                    cacheServerPort (int): 实例端口

                实例信息:
                    instanceName (str): 实例名称 (必需)
                    password (str): 实例密码 (必需)

                企业项目:
                    projectID (str): 企业项目ID

                Header参数:
                    regionId (str): 资源池ID (必需，使用此参数指定要创建实例的资源池)

        Returns:
            Optional[Dict[str, Any]]: 创建结果
        """
        logger.info(f"创建Redis实例 v2: {kwargs.get('instanceName', 'unknown')}")

        try:
            # 构建请求URL - 使用API文档中的正确端点
            url = f'{self.service_endpoint}{self.api_path}/createInstance'

            # 从kwargs中提取所有参数，只传递非None值
            request_body = {}

            # 计费相关参数
            charge_type = kwargs.get('chargeType', 'PostPaid')
            request_body['chargeType'] = charge_type

            if kwargs.get('period'):
                request_body['period'] = kwargs['period']

            if kwargs.get('autoPay') is not None:
                request_body['autoPay'] = kwargs['autoPay']

            if kwargs.get('size') and kwargs['size'] != 1:
                request_body['size'] = kwargs['size']

            if kwargs.get('autoRenew') is not None:
                request_body['autoRenew'] = kwargs['autoRenew']

            if kwargs.get('autoRenewPeriod'):
                request_body['autoRenewPeriod'] = kwargs['autoRenewPeriod']

            # 实例配置参数
            if kwargs.get('version'):
                request_body['version'] = kwargs['version']

            if kwargs.get('edition'):
                request_body['edition'] = kwargs['edition']

            if kwargs.get('engineVersion'):
                request_body['engineVersion'] = kwargs['engineVersion']

            if kwargs.get('zoneName'):
                request_body['zoneName'] = kwargs['zoneName']

            if kwargs.get('secondaryZoneName'):
                request_body['secondaryZoneName'] = kwargs['secondaryZoneName']

            if kwargs.get('hostType'):
                request_body['hostType'] = kwargs['hostType']

            if kwargs.get('shardMemSize'):
                request_body['shardMemSize'] = kwargs['shardMemSize']

            if kwargs.get('shardCount'):
                request_body['shardCount'] = kwargs['shardCount']

            if kwargs.get('capacity'):
                request_body['capacity'] = kwargs['capacity']

            if kwargs.get('copiesCount'):
                request_body['copiesCount'] = kwargs['copiesCount']

            if kwargs.get('dataDiskType'):
                request_body['dataDiskType'] = kwargs['dataDiskType']

            # 网络配置参数
            if kwargs.get('vpcId'):
                request_body['vpcId'] = kwargs['vpcId']

            if kwargs.get('subnetId'):
                request_body['subnetId'] = kwargs['subnetId']

            if kwargs.get('secgroups'):
                request_body['secgroups'] = kwargs['secgroups']

            if kwargs.get('cacheServerPort') and kwargs['cacheServerPort'] != 6379:
                request_body['cacheServerPort'] = kwargs['cacheServerPort']

            # 实例信息参数
            if kwargs.get('instanceName'):
                request_body['instanceName'] = kwargs['instanceName']

            if kwargs.get('password'):
                request_body['password'] = kwargs['password']

            # 企业项目参数
            if kwargs.get('projectID') and kwargs['projectID'] != '0':
                request_body['projectID'] = kwargs['projectID']

            logger.info(f"请求参数: {json.dumps(request_body, ensure_ascii=False)}")

            extra_headers = {
                'Content-Type': 'application/json'
            }

            # 添加regionId到header（如果提供）
            if kwargs.get('regionId'):
                extra_headers['regionId'] = kwargs['regionId']

            # 生成签名请求头
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params={},
                body=json.dumps(request_body),
                extra_headers=extra_headers
            )

            # 发送请求
            response = self.client.session.post(
                url,
                json=request_body,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            result = response.json()

            # 检查API响应状态
            if result.get("statusCode") == 800:
                logger.info(f"Redis实例创建成功: {kwargs.get('instanceName')}")
                return result
            else:
                error_msg = result.get("message", "未知错误")
                error_code = result.get("statusCode", "N/A")
                logger.error(f"Redis实例创建失败 (错误码: {error_code}): {error_msg}")
                return {
                    "error": True,
                    "error_code": error_code,
                    "message": error_msg,
                    "response": result
                }

        except Exception as e:
            logger.error(f"创建Redis实例异常: {str(e)}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_available_resources(self, region_id: str, edition: str, version: str) -> Optional[Dict[str, Any]]:
        """
        查询资源池可创建规格

        Args:
            region_id (str): 区域ID
            edition (str): 实例版本类型（Basic/Enhance/Classic）
            version (str): Redis版本号

        Returns:
            Optional[Dict[str, Any]]: 可用规格信息
        """
        logger.info(f"查询Redis可用规格: regionId={region_id}, edition={edition}, version={version}")

        try:
            # 构建请求URL
            url = f'{self.service_endpoint}{self.api_path}/describeAvailableResource'

            # 查询参数
            query_params = {
                'regionId': region_id,
                'edition': edition,
                'version': version
            }

            extra_headers = {
                'regionId': region_id
            }

            # 生成签名请求头
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers=extra_headers
            )

            # 发送请求
            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=self.timeout
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            result = response.json()

            # 检查API响应状态
            if result.get("statusCode") == 800:
                logger.info(f"查询Redis可用规格成功")
                return result
            else:
                error_msg = result.get("message", "未知错误")
                error_code = result.get("statusCode", "N/A")
                logger.error(f"查询可用规格失败 (错误码: {error_code}): {error_msg}")
                return {
                    "error": True,
                    "error_code": error_code,
                    "message": error_msg,
                    "response": result
                }

        except Exception as e:
            logger.error(f"查询可用规格异常: {str(e)}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_engine_version(self, prod_inst_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例引擎版本信息

        Args:
            prod_inst_id (str): 实例ID
            region_id (str): 区域ID，如果为None则使用默认区域

        Returns:
            Optional[Dict[str, Any]]: 引擎版本信息
        """
        target_region_id = region_id or self.region_id

        logger.info(f"查询Redis实例引擎版本信息: prodInstId={prod_inst_id}, regionId={target_region_id}")

        try:
            # 构建请求URL
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeEngineVersion'

            # 查询参数
            query_params = {
                'prodInstId': prod_inst_id
            }

            # 请求头header参数
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
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }

            return response.json()

        except Exception as e:
            logger.error(f"查询Redis实例引擎版本失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def describe_instance_version(self, prod_inst_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例详细版本信息

        Args:
            prod_inst_id (str): 实例ID
            region_id (str): 区域ID，如果为None则使用默认区域

        Returns:
            Optional[Dict[str, Any]]: 详细版本信息，包含引擎大版本、小版本和代理版本信息
        """
        target_region_id = region_id or self.region_id

        logger.info(f"查询Redis实例详细版本信息: prodInstId={prod_inst_id}, regionId={target_region_id}")

        try:
            # 构建请求URL
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeInstanceVersion'

            # 查询参数
            query_params = {
                'prodInstId': prod_inst_id
            }

            # 请求头header参数
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
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }

            return response.json()

        except Exception as e:
            logger.error(f"查询Redis实例详细版本失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def _create_error_response(self, status_code: int, response_text: str) -> Dict[str, Any]:
        """创建标准错误响应"""
        return {
            "error": True,
            "status_code": status_code,
            "message": f"HTTP {status_code}: {response_text}",
            "response": response_text
        }