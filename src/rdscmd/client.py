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

    def describe_instances_overview(self, instance_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例基础详情

        Args:
            instance_id (str): 实例ID (prodInstId)
            region_id (str): 区域ID，如果不提供则使用默认区域

        Returns:
            Optional[Dict[str, Any]]: 实例详情信息
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询Redis实例详情: prodInstId={instance_id}, regionId={target_region_id}")

        try:
            # 使用正确的API路径
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeInstancesOverview'

            # Query参数只包含 prodInstId
            query_params = {
                'prodInstId': instance_id
            }

            # regionId 作为header参数
            extra_headers = {
                'regionId': target_region_id
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

    def describe_db_instance_net_info(self, prod_inst_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例网络信息

        Args:
            prod_inst_id (str): 实例ID
            region_id (str): 资源池ID，如果为None则使用默认区域

        Returns:
            Optional[Dict[str, Any]]: 网络信息（连接地址、弹性IP、VPC网络、过期时间、架构类型等）
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询Redis实例网络信息: prodInstId={prod_inst_id}, regionId={target_region_id}")

        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeDBInstanceNetInfo'

            query_params = {
                'prodInstId': prod_inst_id
            }

            extra_headers = {
                'regionId': target_region_id
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

    def describe_logic_instance_topology(self, prod_inst_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询Redis实例的逻辑拓扑

        Args:
            prod_inst_id (str): 实例ID
            region_id (str): 资源池ID，如果为None则使用默认区域

        Returns:
            Optional[Dict[str, Any]]: 逻辑拓扑信息（Redis节点集合、接入机节点集合）
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询Redis实例逻辑拓扑: prodInstId={prod_inst_id}, regionId={target_region_id}")

        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeLogicInstanceTopology'

            query_params = {
                'prodInstId': prod_inst_id
            }

            extra_headers = {
                'regionId': target_region_id
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
            logger.error(f"查询实例逻辑拓扑失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_instances_cluster_member_info(self, region_id: str = None, project_id: str = None,
                                                page_index: int = None, page_size: int = None) -> Optional[Dict[str, Any]]:
        """
        批量查询实例节点信息

        Args:
            region_id (str): 资源池ID，如果为None则使用默认区域
            project_id (str): 企业项目ID，默认0
            page_index (int): 当前页码
            page_size (int): 每页大小

        Returns:
            Optional[Dict[str, Any]]: 实例节点信息（实例列表及每个实例的集群节点详情）
        """
        target_region_id = region_id or self.region_id
        logger.info(f"批量查询实例节点信息: regionId={target_region_id}")

        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeInstancesClusterMemberInfo'

            query_params = {}
            if project_id:
                query_params['projectId'] = project_id
            if page_index is not None:
                query_params['pageIndex'] = str(page_index)
            if page_size is not None:
                query_params['pageSize'] = str(page_size)

            extra_headers = {
                'regionId': target_region_id
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
            logger.error(f"批量查询实例节点信息失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def get_redis_node_list(self, prod_inst_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        获取Redis节点名列表

        Args:
            prod_inst_id (str): 实例ID
            region_id (str): 资源池ID，如果为None则使用默认区域

        Returns:
            Optional[Dict[str, Any]]: 节点列表（nodeName, role, nodeVpcIp, nodePort）
        """
        target_region_id = region_id or self.region_id
        logger.info(f"获取Redis节点列表: prodInstId={prod_inst_id}, regionId={target_region_id}")

        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/getRedisNodeList'

            query_params = {
                'prodInstId': prod_inst_id
            }

            extra_headers = {
                'regionId': target_region_id
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
            logger.error(f"获取Redis节点列表失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def get_log_download_url(self, prod_inst_id: str, node_name: str, date: str,
                             log_type: str = None, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        获取日志下载链接

        Args:
            prod_inst_id (str): 实例ID
            node_name (str): 节点名称
            date (str): 日期，格式YYYY-MM-DD，仅支持最近14天
            log_type (str): 日志级别（INFO/WARNING/ERROR/FATAL），仅云盘型缓存支持
            region_id (str): 资源池ID

        Returns:
            Optional[Dict[str, Any]]: 下载链接（fileName, downloadUrl）
        """
        target_region_id = region_id or self.region_id
        logger.info(f"获取Redis日志下载链接: prodInstId={prod_inst_id}, node={node_name}, date={date}")

        try:
            url = f'{self.service_endpoint}/v2/logMgr/downloadRedisRunLog'

            query_params = {
                'prodInstId': prod_inst_id,
                'nodeName': node_name,
                'date': date
            }

            if log_type:
                query_params['logType'] = log_type

            extra_headers = {
                'regionId': target_region_id
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
            logger.error(f"获取Redis日志下载链接失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def query_fragment_replication_state(self, prod_inst_id: str, fragment_name: str,
                                        region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        获取副本状态

        Args:
            prod_inst_id (str): 实例ID
            fragment_name (str): 分片名称（如redis-0）
            region_id (str): 资源池ID

        Returns:
            Optional[Dict[str, Any]]: 副本状态列表（role, vpcIp, status, azName）
        """
        target_region_id = region_id or self.region_id
        logger.info(f"获取副本状态: prodInstId={prod_inst_id}, fragment={fragment_name}")

        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/queryFragmentReplicationState'

            query_params = {
                'prodInstId': prod_inst_id,
                'fragmentName': fragment_name
            }

            extra_headers = {
                'regionId': target_region_id
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
            logger.error(f"获取副本状态失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def query_labels(self, region_id: str = None, page_index: int = 1,
                     page_size: int = 10, label_key: str = None,
                     label_val: str = None) -> Optional[Dict[str, Any]]:
        """
        查询租户所有标签

        Args:
            region_id (str): 资源池ID
            page_index (int): 页码，默认1
            page_size (int): 每页数量，默认10，范围1-50
            label_key (str): 标签键（可选）
            label_val (str): 标签值（可选）

        Returns:
            Optional[Dict[str, Any]]: 标签列表
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询租户标签: regionId={target_region_id}")

        try:
            url = f'{self.service_endpoint}/v2/label/pageList'

            query_params = {
                'pageIndex': str(page_index),
                'pageSize': str(page_size)
            }

            if label_key:
                query_params['labelKey'] = label_key
            if label_val:
                query_params['labelVal'] = label_val

            extra_headers = {
                'regionId': target_region_id
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
            logger.error(f"查询租户标签失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def query_running_logs(self, prod_inst_id: str, node_name: str,
                           region_id: str = None, page_index: int = 1,
                           page_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        查询运行日志

        Args:
            prod_inst_id (str): 实例ID
            node_name (str): 节点名称
            region_id (str): 资源池ID
            page_index (int): 页码，默认1
            page_size (int): 每页数量，默认10

        Returns:
            Optional[Dict[str, Any]]: 运行日志列表
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询运行日志: prodInstId={prod_inst_id}, node={node_name}")

        try:
            url = f'{self.service_endpoint}/v2/logMgr/describeRunningLogRecords'

            query_params = {
                'prodInstId': prod_inst_id,
                'nodeName': node_name,
                'pageIndex': str(page_index),
                'pageSize': str(page_size)
            }

            extra_headers = {
                'regionId': target_region_id
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
            logger.error(f"查询运行日志失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_accounts(self, prod_inst_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询实例账号

        Args:
            prod_inst_id (str): 实例ID
            region_id (str): 资源池ID

        Returns:
            Optional[Dict[str, Any]]: 实例账号列表
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询实例账号: prodInstId={prod_inst_id}")

        try:
            url = f'{self.service_endpoint}/v2/userMgr/describeAccounts'

            query_params = {
                'prodInstId': prod_inst_id
            }

            extra_headers = {
                'regionId': target_region_id
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
            logger.error(f"查询实例账号失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_price(self, order_type: str, region_id: str = None,
                      prod_inst_id: str = None, charge_type: str = None,
                      period: str = None, size: int = None, version: str = None,
                      edition: str = None, engine_version: str = None,
                      host_type: str = None, shard_mem_size: str = None,
                      mem_unit: str = None, shard_count: int = None,
                      capacity: str = None, copies_count: int = None,
                      data_disk_type: str = None) -> Optional[Dict[str, Any]]:
        """
        费用查询

        Args:
            order_type (str): 订单类型 (BUY/RENEW/UPGRADE/EXPANSION/CONTRACTION/INCREASE_SHARDS/DECREASE_SHARDS/INCREASE_REPLICAS/DECREASE_REPLICAS)
            region_id (str): 资源池ID
            prod_inst_id (str): 实例ID（BUY无需填写，其他必填）
            charge_type (str): 计费模式 PrePaid/PostPaid
            period (str): 订购时长(月)，PrePaid时必填，取值1~6,12
            size (int): 数量，仅订购询价，1-100，默认1
            version (str): 版本类型 BASIC/PLUS
            edition (str): 实例类型（BUY/UPGRADE必填）
            engine_version (str): Redis引擎版本（BUY必填）
            host_type (str): 主机类型
            shard_mem_size (str): 分片规格GB
            mem_unit (str): 内存规格单位 M/G
            shard_count (int): 分片数
            capacity (str): 存储容量GB
            copies_count (int): 副本数2~10
            data_disk_type (str): 磁盘类型 SSD/SAS

        Returns:
            Optional[Dict[str, Any]]: 价格信息
        """
        target_region_id = region_id or self.region_id
        logger.info(f"费用查询: orderType={order_type}, regionId={target_region_id}")

        try:
            url = f'{self.service_endpoint}/v2/lifeCycleServant/describePrice'

            request_body = {
                'orderType': order_type
            }

            if prod_inst_id:
                request_body['prodInstId'] = prod_inst_id
            if charge_type:
                request_body['chargeType'] = charge_type
            if period:
                request_body['period'] = period
            if size is not None:
                request_body['size'] = size
            if version:
                request_body['version'] = version
            if edition:
                request_body['edition'] = edition
            if engine_version:
                request_body['engineVersion'] = engine_version
            if host_type:
                request_body['hostType'] = host_type
            if shard_mem_size:
                request_body['shardMemSize'] = shard_mem_size
            if mem_unit:
                request_body['memUnit'] = mem_unit
            if shard_count is not None:
                request_body['shardCount'] = shard_count
            if capacity:
                request_body['capacity'] = capacity
            if copies_count is not None:
                request_body['copiesCount'] = copies_count
            if data_disk_type:
                request_body['dataDiskType'] = data_disk_type

            extra_headers = {
                'regionId': target_region_id,
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
            logger.error(f"费用查询失败: {e}")
            return {
                "error": True,
                "message": f"请求异常: {str(e)}",
                "exception": str(e)
            }

    def describe_proxy_history_monitor_values(self, prod_inst_id: str, node_name: str,
                                                start_time: str, end_time: str,
                                                monitor_type: str,
                                                region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询代理节点性能监控指标历史数据

        Args:
            prod_inst_id (str): 实例ID
            node_name (str): Proxy节点名称（从逻辑拓扑AccessNode.proxyName获取）
            start_time (str): 开始时间（格式：yyyy-MM-dd HH:mm:ss），最大查询范围30天
            end_time (str): 结束时间（格式：yyyy-MM-dd HH:mm:ss）
            monitor_type (str): 监控类型（从性能监控指标列表proxyNodeMonitorList的type字段获取）
            region_id (str): 资源池ID

        Returns:
            Optional[Dict[str, Any]]: 监控数据（returnObj.rows[].metric, returnObj.rows[].values[]）
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询Proxy节点监控历史: prodInstId={prod_inst_id}, node={node_name}, type={monitor_type}")

        try:
            from urllib.parse import urlencode, quote
            url = f'{self.service_endpoint}/v2/resourceMonitor/describeProxyHistoryMonitorValues'

            query_params = {
                'prodInstId': prod_inst_id,
                'nodeName': node_name,
                'startTime': start_time,
                'endTime': end_time,
                'type': monitor_type
            }

            extra_headers = {
                'regionId': target_region_id
            }

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers=extra_headers
            )

            encoded_qs = urlencode(query_params, quote_via=quote)
            response = self.client.session.get(f"{url}?{encoded_qs}", headers=headers, timeout=self.timeout)
            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()

        except Exception as e:
            logger.error(f"查询Proxy节点监控历史失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def query_rw_sep(self, prod_inst_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询读写分离状态

        Args:
            prod_inst_id (str): 实例ID
            region_id (str): 资源池ID

        Returns:
            Optional[Dict[str, Any]]: returnObj.isRWSep (true=开启, false=关闭)
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询读写分离状态: prodInstId={prod_inst_id}, regionId={target_region_id}")

        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/queryRWSep'

            query_params = {'prodInstId': prod_inst_id}
            extra_headers = {'regionId': target_region_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()

        except Exception as e:
            logger.error(f"查询读写分离状态失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def describe_db_group(self, prod_inst_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询分组列表

        Args:
            prod_inst_id (str): 实例ID
            region_id (str): 资源池ID

        Returns:
            Optional[Dict[str, Any]]: returnObj.total, returnObj.rows[] (groupName, groupInfo, dborder, redisSetName等)
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询分组列表: prodInstId={prod_inst_id}, regionId={target_region_id}")

        try:
            url = f'{self.service_endpoint}/v2/groupManageMgrServant/describeDbGroup'

            query_params = {'prodInstId': prod_inst_id}
            extra_headers = {'regionId': target_region_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()

        except Exception as e:
            logger.error(f"查询分组列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def describe_cluster_member_info(self, prod_inst_id: str, region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询集群节点信息

        Args:
            prod_inst_id (str): 实例ID
            region_id (str): 资源池ID

        Returns:
            Optional[Dict[str, Any]]: returnObj.rows[] (redisSetName, nodes[master/slave], slotInfo, isAuth, type)
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询集群节点信息: prodInstId={prod_inst_id}, regionId={target_region_id}")

        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeClusterMemberInfo'

            query_params = {'prodInstId': prod_inst_id}
            extra_headers = {'regionId': target_region_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()

        except Exception as e:
            logger.error(f"查询集群节点信息失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def describe_memory_info(self, prod_inst_id: str, ip: str, port: str,
                              region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询节点内存

        Args:
            prod_inst_id (str): 实例ID
            ip (str): Redis节点IP
            port (str): Redis节点端口
            region_id (str): 资源池ID

        Returns:
            Optional[Dict[str, Any]]: returnObj.freeMemory, returnObj.maxMemory
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询节点内存: prodInstId={prod_inst_id}, ip={ip}, port={port}")

        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeMemoryInfo'

            query_params = {
                'prodInstId': prod_inst_id,
                'ip': ip,
                'port': port
            }
            extra_headers = {'regionId': target_region_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()

        except Exception as e:
            logger.error(f"查询节点内存失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def describe_node_running_state(self, prod_inst_id: str, node_type: str, vpc_url: str,
                                     region_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询节点状态

        Args:
            prod_inst_id (str): 实例ID
            node_type (str): 节点类型（redis/proxy）
            vpc_url (str): 节点地址（从逻辑拓扑获取vpcUrl字段）
            region_id (str): 资源池ID

        Returns:
            Optional[Dict[str, Any]]: returnObj.status (0=运行中, 1=停止)
        """
        target_region_id = region_id or self.region_id
        logger.info(f"查询节点状态: prodInstId={prod_inst_id}, nodeType={node_type}, vpcUrl={vpc_url}")

        try:
            url = f'{self.service_endpoint}/v2/redisMgr/describeNodeRunningState'

            query_params = {
                'prodInstId': prod_inst_id,
                'nodeType': node_type,
                'vpcUrl': vpc_url
            }
            extra_headers = {'regionId': target_region_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers=extra_headers
            )

            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()

        except Exception as e:
            logger.error(f"查询节点状态失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def get_available_region(self, res_pool_code: str = None) -> Optional[Dict[str, Any]]:
        """
        查询可用的资源池

        Args:
            res_pool_code (str): 资源池ID（可选，不传则查询全部）

        Returns:
            Optional[Dict[str, Any]]: returnObj[] (resPoolCode, resPoolName, products[])
        """
        logger.info(f"查询可用的资源池: resPoolCode={res_pool_code}")

        try:
            url = f'{self.service_endpoint}/v2/region/getAvailableRegion'

            query_params = {}
            if res_pool_code:
                query_params['resPoolCode'] = res_pool_code

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={}
            )

            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()

        except Exception as e:
            logger.error(f"查询可用的资源池失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def get_label_list_by_resources(self, region_id: str, prod_inst_ids: list) -> Optional[Dict[str, Any]]:
        """查询资源绑定的标签列表 - POST /v2/label/getLabelListByResources"""
        logger.info(f"查询Redis资源标签: instCount={len(prod_inst_ids)}")
        try:
            url = f'{self.service_endpoint}/v2/label/getLabelListByResources'
            request_body = {'prodInstIds': prod_inst_ids}
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=json.dumps(request_body),
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.post(url, json=request_body, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询资源标签失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    # ==================== 批量新增查询类 API（10个） ====================

    def describe_recycle_bin_instances(self, region_id: str, page_index: int = 1,
                                       page_size: int = 10,
                                       instance_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """查询回收站实例列表 - GET /v2/instanceManageMgrServant/describeCycleBinInstances"""
        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeCycleBinInstances'
            query_params = {'pageIndex': str(page_index), 'pageSize': str(page_size)}
            if instance_name:
                query_params['instanceName'] = instance_name
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询回收站实例列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_running_instances_statistics(self, region_id: str,
                                              include_failure: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """查询运行中实例的统计信息 - GET /v2/instanceManageMgrServant/statistic"""
        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/statistic'
            query_params = {}
            if include_failure:
                query_params['includeFailure'] = include_failure
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询运行中实例统计失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_tenant_quota(self, region_id: str) -> Optional[Dict[str, Any]]:
        """查询租户配额 - GET /v2/quota/queryQuotaTotalAndUsed"""
        try:
            url = f'{self.service_endpoint}/v2/quota/queryQuotaTotalAndUsed'
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params={}, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询租户配额失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_instance_maintain_time(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询实例维护时间 - GET /v2/instanceManageMgrServant/describeInstanceMaintainTime"""
        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeInstanceMaintainTime'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询实例维护时间失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_backups(self, region_id: str, prod_inst_id: str,
                         restore_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """查询备份文件信息 - GET /v2/redisMgr/describeBackups"""
        try:
            url = f'{self.service_endpoint}/v2/redisMgr/describeBackups'
            query_params = {'prodInstId': prod_inst_id}
            if restore_name:
                query_params['restoreName'] = restore_name
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询备份文件信息失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_backup_policy(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询自动备份策略 - GET /v2/redisMgr/describeBackupPolicy"""
        try:
            url = f'{self.service_endpoint}/v2/redisMgr/describeBackupPolicy'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询自动备份策略失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def get_rdb_download_url(self, region_id: str, prod_inst_id: str,
                             restore_name: str, ip_type: str) -> Optional[Dict[str, Any]]:
        """获取备份文件下载链接 - GET /v2/redisMgr/getRdbDownLoadUrl"""
        try:
            url = f'{self.service_endpoint}/v2/redisMgr/getRdbDownLoadUrl'
            query_params = {
                'prodInstId': prod_inst_id,
                'restoreName': restore_name,
                'ipType': ip_type,
            }
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"获取备份下载链接失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_instance_ssl(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询SSL信息 - GET /v2/securityMgrServant/describeInstanceSSL"""
        try:
            url = f'{self.service_endpoint}/v2/securityMgrServant/describeInstanceSSL'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询SSL信息失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_security_ips(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询指定实例的IP白名单分组 - GET /v2/securityMgrServant/describeSecurityIps"""
        try:
            url = f'{self.service_endpoint}/v2/securityMgrServant/describeSecurityIps'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询IP白名单分组失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_top_slow_logs(self, region_id: str, prod_inst_id: str, node_name: str,
                               size: Optional[int] = None,
                               min_cost: Optional[int] = None,
                               max_cost: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """查询慢日志 - GET /v2/logMgr/describeTopSlowLogRecords"""
        try:
            url = f'{self.service_endpoint}/v2/logMgr/describeTopSlowLogRecords'
            query_params = {'prodInstId': prod_inst_id, 'nodeName': node_name}
            if size is not None:
                query_params['size'] = str(size)
            if min_cost is not None:
                query_params['minCost'] = str(min_cost)
            if max_cost is not None:
                query_params['maxCost'] = str(max_cost)
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询慢日志失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    # ==================== 批量新增查询类 API（第2批，5个） ====================

    def describe_instance_experiments(self, region_id: str, prod_inst_id: str,
                                      page: Optional[int] = None,
                                      size: Optional[int] = None,
                                      action_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """查询实例故障列表 - GET /v2/inject/listInstanceExperiments"""
        try:
            url = f'{self.service_endpoint}/v2/inject/listInstanceExperiments'
            query_params = {'prodInstId': prod_inst_id}
            if page is not None:
                query_params['page'] = str(page)
            if size is not None:
                query_params['size'] = str(size)
            if action_code:
                query_params['actionCode'] = action_code
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询实例故障列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def check_instance_operate(self, region_id: str, prod_inst_id: str,
                               operate: str = 'upgrade',
                               shard_mem_size: Optional[int] = None,
                               shard_count: Optional[int] = None,
                               mem_size: Optional[int] = None,
                               copies_count: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """查询实例是否可以扩容 - POST /v2/check/checkInstanceOperate"""
        try:
            url = f'{self.service_endpoint}/v2/check/checkInstanceOperate'
            request_body = {'operate': operate, 'prodInstId': prod_inst_id}
            if shard_mem_size is not None:
                request_body['shardMemSize'] = shard_mem_size
            if shard_count is not None:
                request_body['shardCount'] = shard_count
            if mem_size is not None:
                request_body['memSize'] = mem_size
            if copies_count is not None:
                request_body['copiesCount'] = copies_count
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=json.dumps(request_body),
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.post(url, json=request_body, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询实例是否可以扩容失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def query_instance_auto_renew_status(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """自动续费查询 - GET /v2/res/spuInst/queryInstAutoRenewStatus"""
        try:
            url = f'{self.service_endpoint}/v2/res/spuInst/queryInstAutoRenewStatus'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"自动续费查询失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def query_data_flashback_status(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询数据闪回状态 - GET /v2/redisMgr/queryDataFlashBack"""
        try:
            url = f'{self.service_endpoint}/v2/redisMgr/queryDataFlashBack'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询数据闪回状态失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def query_rename_command_status(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询危险命令重命名状态 - GET /v2/securityMgrServant/queryRenameCommand"""
        try:
            url = f'{self.service_endpoint}/v2/securityMgrServant/queryRenameCommand'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询危险命令重命名状态失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    # ==================== 批量新增查询类 API（第3批，5个） ====================

    def describe_backup_tasks(self, region_id: str, prod_inst_id: str,
                              restore_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """查询备份任务执行情况 - GET /v2/redisMgr/describeBackupTasks"""
        try:
            url = f'{self.service_endpoint}/v2/redisMgr/describeBackupTasks'
            query_params = {'prodInstId': prod_inst_id}
            if restore_name:
                query_params['restoreName'] = restore_name
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询备份任务执行情况失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def get_client_map_by_ip(self, region_id: str, prod_inst_id: str,
                             node_name: str) -> Optional[Dict[str, Any]]:
        """按照客户端IP统计客户端会话数量 - GET /v2/resourceMonitor/getClientMap"""
        try:
            url = f'{self.service_endpoint}/v2/resourceMonitor/getClientMap'
            query_params = {'prodInstId': prod_inst_id, 'nodeName': node_name}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"按客户端IP统计会话数量失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def query_maintain_az(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询主节点可用区锁定设置 - GET /v2/instanceManageMgrServant/queryMaintainAz"""
        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/queryMaintainAz'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询主节点可用区锁定设置失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_dedicated_cluster_instances(self, region_id: str,
                                             page_index: int = 1,
                                             page_size: int = 10,
                                             instance_name: Optional[str] = None,
                                             prod_inst_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """查询专属集群产品实例列表 - GET /v2/instanceManageMgrServant/describeDedicatedClusterInstanceList"""
        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeDedicatedClusterInstanceList'
            query_params = {'pageIndex': str(page_index), 'pageSize': str(page_size)}
            if instance_name:
                query_params['instanceName'] = instance_name
            if prod_inst_id:
                query_params['prodInstId'] = prod_inst_id
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询专属集群产品实例列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_db_key_count(self, region_id: str, prod_inst_id: str,
                              groups: str) -> Optional[Dict[str, Any]]:
        """查询dbkey的数量 - GET /v2/instanceManageMgrServant/describeDbKeyCount"""
        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/describeDbKeyCount'
            query_params = {'prodInstId': prod_inst_id, 'groups': groups}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询dbkey数量失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    # ==================== 批量新增查询类 API（第4批，10个） ====================

    def describe_node_monitor_items(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询命令调用类族 - GET /v2/monitorManageMgrServant/describeNodeMonitorItems"""
        try:
            url = f'{self.service_endpoint}/v2/monitorManageMgrServant/describeNodeMonitorItems'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询命令调用类族失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_node_monitor_values(self, region_id: str, prod_inst_id: str,
                                     type_: str, node_name: str,
                                     start_time: str, end_time: str) -> Optional[Dict[str, Any]]:
        """查询类簇的调用次数 - GET /v2/monitorManageMgrServant/describeNodeMonitorValues"""
        try:
            from urllib.parse import urlencode, quote
            url = f'{self.service_endpoint}/v2/monitorManageMgrServant/describeNodeMonitorValues'
            query_params = {
                'prodInstId': prod_inst_id, 'type': type_,
                'nodeName': node_name, 'startTime': start_time, 'endTime': end_time,
            }
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            encoded_qs = urlencode(query_params, quote_via=quote)
            response = self.client.session.get(f"{url}?{encoded_qs}", headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询类簇调用次数失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def find_history_slow_log(self, region_id: str, prod_inst_id: str,
                              node_name: str, start_time: str, end_time: str,
                              page: Optional[int] = None,
                              rows: Optional[int] = None,
                              min_cost: Optional[int] = None,
                              max_cost: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """按时间段查询慢日志历史数据 - GET /v2/resourceMonitor/findHistorySlowLog"""
        try:
            from urllib.parse import urlencode, quote
            url = f'{self.service_endpoint}/v2/resourceMonitor/findHistorySlowLog'
            query_params = {
                'prodInstId': prod_inst_id, 'nodeName': node_name,
                'startTime': start_time, 'endTime': end_time,
            }
            if page is not None:
                query_params['page'] = str(page)
            if rows is not None:
                query_params['rows'] = str(rows)
            if min_cost is not None:
                query_params['minCost'] = str(min_cost)
            if max_cost is not None:
                query_params['maxCost'] = str(max_cost)
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            encoded_qs = urlencode(query_params, quote_via=quote)
            response = self.client.session.get(f"{url}?{encoded_qs}", headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询慢日志历史数据失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_command_audit_log_status(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询命令审计日志开启状态 - GET /v2/logMgr/describeCommandAuditLog"""
        try:
            url = f'{self.service_endpoint}/v2/logMgr/describeCommandAuditLog'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询命令审计日志状态失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_node_command_list(self, region_id: str, prod_inst_id: str,
                                   node_name: str, start_time: str, end_time: str) -> Optional[Dict[str, Any]]:
        """查询节点命令列表 - GET /v2/resourceMonitor/describeNodeCommandList"""
        try:
            from urllib.parse import urlencode, quote
            url = f'{self.service_endpoint}/v2/resourceMonitor/describeNodeCommandList'
            query_params = {
                'prodInstId': prod_inst_id, 'nodeName': node_name,
                'startTime': start_time, 'endTime': end_time,
            }
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            encoded_qs = urlencode(query_params, quote_via=quote)
            response = self.client.session.get(f"{url}?{encoded_qs}", headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询节点命令列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_node_command_monitor_values(self, region_id: str, prod_inst_id: str,
                                             node_name: str, start_time: str, end_time: str,
                                             type_: str, cmd: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """查询节点命令监控历史数据 - GET /v2/resourceMonitor/describeNodeCommandMonitorValues"""
        try:
            from urllib.parse import urlencode, quote
            url = f'{self.service_endpoint}/v2/resourceMonitor/describeNodeCommandMonitorValues'
            query_params = {
                'prodInstId': prod_inst_id, 'nodeName': node_name,
                'startTime': start_time, 'endTime': end_time, 'type': type_,
            }
            if cmd:
                query_params['cmd'] = cmd
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            encoded_qs = urlencode(query_params, quote_via=quote)
            response = self.client.session.get(f"{url}?{encoded_qs}", headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询节点命令监控历史数据失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_instance_config_v3(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询实例配置参数(V3) - GET /v3/instanceParam/describeInstanceConfig"""
        try:
            url = f'{self.service_endpoint}/v3/instanceParam/describeInstanceConfig'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询实例配置参数V3失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_parameter_modification_history(self, region_id: str, prod_inst_id: str,
                                                start_time: Optional[str] = None,
                                                end_time: Optional[str] = None,
                                                history_id: Optional[str] = None,
                                                page: Optional[int] = None,
                                                rows: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """查询配置参数修改历史 - GET /v2/instanceParam/describeParameterModificationHistory"""
        try:
            from urllib.parse import urlencode, quote
            url = f'{self.service_endpoint}/v2/instanceParam/describeParameterModificationHistory'
            query_params = {'prodInstId': prod_inst_id}
            if start_time:
                query_params['startTime'] = start_time
            if end_time:
                query_params['endTime'] = end_time
            if history_id:
                query_params['historyId'] = history_id
            if page is not None:
                query_params['page'] = str(page)
            if rows is not None:
                query_params['rows'] = str(rows)
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            encoded_qs = urlencode(query_params, quote_via=quote)
            response = self.client.session.get(f"{url}?{encoded_qs}", headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询配置参数修改历史失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_redis_templates(self, region_id: str, type_: str,
                                 page_num: Optional[int] = None,
                                 page_size: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """查询参数模板列表 - GET /v2/redisTemplate/describeRedisTemplate"""
        try:
            url = f'{self.service_endpoint}/v2/redisTemplate/describeRedisTemplate'
            query_params = {'type': type_}
            if page_num is not None:
                query_params['pageNum'] = str(page_num)
            if page_size is not None:
                query_params['pageSize'] = str(page_size)
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询参数模板列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_redis_template_detail(self, region_id: str, template_id: str) -> Optional[Dict[str, Any]]:
        """查询参数模板详情 - GET /v2/redisTemplate/describeRedisTemplateDetail"""
        try:
            url = f'{self.service_endpoint}/v2/redisTemplate/describeRedisTemplateDetail'
            query_params = {'templateId': template_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询参数模板详情失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    # ==================== 批量新增查询类 API（第5批，10个） ====================

    def query_auto_scan_conf_setting(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询过期key扫描配置 - GET /v2/redisMgr/queryAutoScanConfSetting"""
        try:
            url = f'{self.service_endpoint}/v2/redisMgr/queryAutoScanConfSetting'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询过期key扫描配置失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def query_scan_logs(self, region_id: str, prod_inst_id: str,
                        page_index: int, page_size: int) -> Optional[Dict[str, Any]]:
        """查询过期Key扫描记录 - GET /v2/redisDataMgr/queryScanLogs"""
        try:
            url = f'{self.service_endpoint}/v2/redisDataMgr/queryScanLogs'
            query_params = {'prodInstId': prod_inst_id, 'pageIndex': str(page_index), 'pageSize': str(page_size)}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询过期key扫描记录失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_big_and_hot_keys(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询Redis实例的热Key/大key - GET /v2/keyAnalysisMgrServant/describeBigAndHotKeys"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/describeBigAndHotKeys'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询热Key/大key失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_instance_strategy(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询Redis实例的淘汰策略 - GET /v2/keyAnalysisMgrServant/describeInstanceStrategy"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/describeInstanceStrategy'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询淘汰策略失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def get_key_misslog(self, region_id: str, prod_inst_id: str,
                        node_name: str) -> Optional[Dict[str, Any]]:
        """命中率分析查询 - GET /v2/resourceMonitor/getKeyMisslog"""
        try:
            from urllib.parse import urlencode, quote
            url = f'{self.service_endpoint}/v2/resourceMonitor/getKeyMisslog'
            query_params = {'prodInstId': prod_inst_id, 'nodeName': node_name}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            encoded_qs = urlencode(query_params, quote_via=quote)
            response = self.client.session.get(f"{url}?{encoded_qs}", headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询命中率分析失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def query_analysis_instance_tasks(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询实例诊断分析报告列表 - GET /v2/keyAnalysisMgrServant/queryAnalysisInstanceTasks"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/queryAnalysisInstanceTasks'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询诊断分析报告列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_big_key_tasks(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询大key分析任务列表 - GET /v2/keyAnalysisMgrServant/describeBigKeyTasks"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/describeBigKeyTasks'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询大key分析任务列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_hot_key_tasks(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询热key分析任务列表 - GET /v2/keyAnalysisMgrServant/describeHotKeyTasks"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/describeHotKeyTasks'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询热key分析任务列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_key_task_record(self, region_id: str, prod_inst_id: str,
                                 task_id: str) -> Optional[Dict[str, Any]]:
        """查询大key/热key任务结果 - GET /v2/keyAnalysisMgrServant/describeKeyTaskRecord"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/describeKeyTaskRecord'
            query_params = {'prodInstId': prod_inst_id, 'taskId': task_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询大key/热key任务结果失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_top_big_keys_policy(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询大key自动分析配置 - GET /v2/keyAnalysisMgrServant/describeTopBigKeysPolicy"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/describeTopBigKeysPolicy'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询大key自动分析配置失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    # ==================== 批量新增查询类 API（第6批，10个） ====================

    def describe_top_hot_keys_policy(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询热key自动分析配置 - GET /v2/keyAnalysisMgrServant/describeTopHotKeysPolicy"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/describeTopHotKeysPolicy'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询热key自动分析配置失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_offline_key_analysis_task_list(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询离线全量key分析报告列表 - GET /v2/keyAnalysisMgrServant/describeOffLineKeyAnalysisTaskList"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/describeOffLineKeyAnalysisTaskList'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询离线全量key分析报告列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def describe_offline_key_analysis_task_info(self, region_id: str, prod_inst_id: str,
                                                task_id: str) -> Optional[Dict[str, Any]]:
        """查询离线全量key分析报告详情 - GET /v2/keyAnalysisMgrServant/describeOffLineKeyAnalysisTaskInfo"""
        try:
            url = f'{self.service_endpoint}/v2/keyAnalysisMgrServant/describeOffLineKeyAnalysisTaskInfo'
            query_params = {'prodInstId': prod_inst_id, 'taskId': task_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询离线全量key分析报告详情失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def find_history_big_and_hot_key(self, region_id: str, prod_inst_id: str,
                                     start_time: str, end_time: str,
                                     node_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """按时间段查询大key热key历史数据 - GET /v2/resourceMonitor/findHistoryBigAndHotKey"""
        try:
            from urllib.parse import urlencode, quote
            url = f'{self.service_endpoint}/v2/resourceMonitor/findHistoryBigAndHotKey'
            query_params = {'prodInstId': prod_inst_id, 'startTime': start_time, 'endTime': end_time}
            if node_name:
                query_params['nodeName'] = node_name
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            encoded_qs = urlencode(query_params, quote_via=quote)
            response = self.client.session.get(f"{url}?{encoded_qs}", headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询大key热key历史数据失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def get_cache_port_modify_range(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """查询实例端口的可修改范围 - GET /v2/component/getCachePortModifyRange"""
        try:
            url = f'{self.service_endpoint}/v2/component/getCachePortModifyRange'
            query_params = {'prodInstId': prod_inst_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询实例端口可修改范围失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def query_export_instance_task(self, region_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """查询实例列表导出任务详情 - GET /v2/instanceManageMgrServant/queryExportInstanceTask"""
        try:
            url = f'{self.service_endpoint}/v2/instanceManageMgrServant/queryExportInstanceTask'
            query_params = {'taskId': task_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询实例列表导出任务详情失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def list_task_center_tasks(self, region_id: str, start_time: str, end_time: str,
                               status: int, start_time_desc: int = 0,
                               page_index: Optional[int] = None,
                               page_size: Optional[int] = None,
                               task_type_str: Optional[str] = None,
                               prod_inst_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """查询任务列表 - POST /v2/taskCenter/listTasks"""
        try:
            url = f'{self.service_endpoint}/v2/taskCenter/listTasks'
            condition = {'status': status, 'startTimeDesc': start_time_desc}
            if task_type_str:
                condition['taskTypeStr'] = task_type_str
            if prod_inst_id:
                condition['prodInstId'] = prod_inst_id
            request_body = {
                'startTime': start_time, 'endTime': end_time, 'condition': condition,
            }
            if page_index is not None:
                request_body['pageIndex'] = page_index
            if page_size is not None:
                request_body['pageSize'] = page_size
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=json.dumps(request_body),
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.post(url, json=request_body, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询任务列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def get_task_center_task_info(self, region_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """查询后台任务详细信息 - GET /v2/taskCenter/getTaskInfo"""
        try:
            url = f'{self.service_endpoint}/v2/taskCenter/getTaskInfo'
            query_params = {'taskId': task_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询后台任务详细信息失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def list_transfer_tasks(self, region_id: str, page_num: int, page_size: int,
                            status: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """查询数据迁移任务列表 - GET /v2/transfer/listTaskInfo"""
        try:
            url = f'{self.service_endpoint}/v2/transfer/listTaskInfo'
            query_params = {'pageNum': str(page_num), 'pageSize': str(page_size)}
            if status is not None:
                query_params['status'] = str(status)
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询数据迁移任务列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def get_transfer_task_info(self, region_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """查询迁移任务详情 - GET /v2/transfer/getTaskInfo"""
        try:
            url = f'{self.service_endpoint}/v2/transfer/getTaskInfo'
            query_params = {'taskId': task_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询迁移任务详情失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    # ==================== 批量新增查询类 API（第7批，2个 - 完成） ====================

    def get_transfer_task_progress_detail(self, region_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """查询在线迁移进度明细 - GET /v2/transfer/getTaskProgressDetailInfo"""
        try:
            url = f'{self.service_endpoint}/v2/transfer/getTaskProgressDetailInfo'
            query_params = {'taskId': task_id}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params, body='',
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询在线迁移进度明细失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def get_transfer_task_running_log(self, region_id: str, task_id: str,
                                      search_date: str) -> Optional[Dict[str, Any]]:
        """查询迁移日志列表 - POST /v2/transfer/uploadSyncRunningLog"""
        try:
            url = f'{self.service_endpoint}/v2/transfer/uploadSyncRunningLog'
            request_body = {'taskId': task_id, 'searchDate': search_date}
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=json.dumps(request_body),
                extra_headers={'regionId': region_id}
            )
            response = self.client.session.post(url, json=request_body, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"查询迁移日志列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}"}

    def _create_error_response(self, status_code: int, response_text: str) -> Dict[str, Any]:
        """创建标准错误响应"""
        return {
            "error": True,
            "status_code": status_code,
            "message": f"HTTP {status_code}: {response_text}",
            "response": response_text
        }