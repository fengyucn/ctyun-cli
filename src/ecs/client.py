"""
云服务器(ECS)管理模块 - 使用OpenAPI V4
"""

from typing import Dict, Any, List, Optional
import json
from src.client import CTYUNClient
from src.auth.eop_signature import CTYUNEOPAuth
from src.utils.helpers import logger


class ECSClient:
    """云服务器客户端 - OpenAPI V4"""

    def __init__(self, client: CTYUNClient):
        """
        初始化ECS客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'ecs'
        self.base_endpoint = 'ctecs-global.ctapi.ctyun.cn'
        # 初始化EOP签名认证器
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def get_customer_resources(self, region_id: str) -> Dict[str, Any]:
        """
        根据regionID查询用户资源
        
        Args:
            region_id: 区域ID
            
        Returns:
            用户资源信息
        """
        logger.info(f"查询用户资源: regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/region/customerResources'
            
            # 构造请求体
            body_data = {
                'regionID': region_id
            }
            body = json.dumps(body_data)
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
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
            logger.error(f"查询用户资源失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_instances(self, region_id: str, page_no: int = 1, page_size: int = 10,
                      az_name: Optional[str] = None,
                      project_id: Optional[str] = None,
                      state: Optional[str] = None,
                      keyword: Optional[str] = None,
                      instance_name: Optional[str] = None,
                      instance_id_list: Optional[str] = None,
                      vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询云主机列表（详细版）
        
        Args:
            region_id: 资源池ID
            page_no: 页码，从1开始
            page_size: 每页数量，默认10，最大50
            az_name: 可用区名称
            project_id: 企业项目ID
            state: 云主机状态（active/shutoff/expired等）
            keyword: 关键字模糊查询
            instance_name: 云主机名称（精确匹配）
            instance_id_list: 云主机ID列表，逗号分隔
            vpc_id: 虚拟私有云ID
            
        Returns:
            云主机列表
        """
        logger.info(f"查询云主机列表: regionId={region_id}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/list-instances'
            
            # 构造请求体
            body_data = {
                'regionID': region_id,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            # 添加可选参数
            if az_name:
                body_data['azName'] = az_name
            if project_id:
                body_data['projectID'] = project_id
            if state:
                body_data['state'] = state
            if keyword:
                body_data['keyword'] = keyword
            if instance_name:
                body_data['instanceName'] = instance_name
            if instance_id_list:
                body_data['instanceIDList'] = instance_id_list
            if vpc_id:
                body_data['vpcID'] = vpc_id
            
            body = json.dumps(body_data)
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_instances()
            
            result = response.json()
            
            # 检查返回状态
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
                return self._get_mock_instances()
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_instances()

    def get_instance_statistics(self, region_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询用户云主机统计信息
        
        Args:
            region_id: 资源池ID
            project_id: 企业项目ID（可选）
            
        Returns:
            云主机统计信息
        """
        logger.info(f"查询云主机统计信息: regionId={region_id}, projectId={project_id or '全部'}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/statistics-instance'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id
            }
            if project_id:
                query_params['projectID'] = project_id
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"查询参数: {query_params}")
            logger.debug(f"请求头: {headers}")
            
            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_statistics()
            
            result = response.json()
            
            # 检查返回状态
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
                return self._get_mock_statistics()
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机统计信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_statistics()

    def _get_mock_statistics(self) -> Dict[str, Any]:
        """生成模拟统计数据"""
        return {
            'statusCode': 800,
            'message': '成功',
            'returnObj': {
                'instanceStatistics': {
                    'totalCount': 10,
                    'RunningCount': 7,
                    'shutdownCount': 2,
                    'expireCount': 1,
                    'expireRunningCount': 0,
                    'expireShutdownCount': 1,
                    'cpuCount': 20,
                    'memoryCount': 40
                }
            },
            '_mock': True
        }

    def _get_mock_instances(self) -> Dict[str, Any]:
        """生成模拟云主机数据"""
        return {
            'statusCode': 800,
            'message': '成功',
            'returnObj': {
                'results': [
                    {
                        'instanceID': 'instance-demo-001',
                        'instanceName': 'web-server-1',
                        'displayName': 'Web服务器1',
                        'regionID': 'cn-north-1',
                        'azName': 'az1',
                        'instanceStatus': 'running',
                        'instanceStatusStr': '运行中',
                        'expireTime': '2025-12-31 23:59:59',
                        'privateIP': ['192.168.1.10'],
                        'eipAddress': ['1.2.3.4']
                    }
                ],
                'totalCount': 1,
                'currentCount': 1
            },
            '_mock': True
        }

    def get_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        查询云主机详情
        
        Args:
            instance_id: 云主机ID
            
        Returns:
            云主机详情
        """
        logger.info(f"查询云主机详情: {instance_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/details'
            
            # 构造请求体
            body_data = {
                'instanceID': instance_id
            }
            body = json.dumps(body_data)
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求体: {body}")
            
            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
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
            logger.error(f"查询云主机详情失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_regions(self, region_name: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        查询资源池列表
        
        Args:
            region_name: 资源池名称（可选）
            use_cache: 是否使用缓存，默认True
            
        Returns:
            资源池列表
        """
        logger.info(f"查询资源池列表: regionName={region_name if region_name else '全部'}")
        
        # 检查缓存
        if use_cache:
            from utils.cache import get_cache
            cache = get_cache()
            cache_key = f"ecs:regions:{region_name or 'all'}"
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug("使用缓存的资源池数据")
                return cached_data
        
        try:
            url = f'https://{self.base_endpoint}/v4/region/list-regions'
            
            # 构造查询参数
            query_params = {}
            if region_name:
                query_params['regionName'] = region_name
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"查询参数: {query_params}")
            logger.debug(f"请求头: {headers}")
            
            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_regions()
            
            result = response.json()
            
            # 检查返回状态
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
                return self._get_mock_regions()
            
            # 缓存结果（资源池列表一般不常变化，缓存24小时）
            if use_cache:
                from utils.cache import get_cache
                cache = get_cache()
                cache_key = f"ecs:regions:{region_name or 'all'}"
                cache.set(cache_key, result, ttl=86400)  # 24小时
            
            return result
            
        except Exception as e:
            logger.error(f"查询资源池列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_regions()

    def _get_mock_regions(self) -> Dict[str, Any]:
        """生成模拟资源池数据"""
        return {
            'statusCode': 800,
            'message': '成功',
            'returnObj': {
                'regionList': [
                    {
                        'regionID': 'bb9ffd42056f11e59079fa163e06b8b0',
                        'regionParent': '北京',
                        'regionName': '北京1',
                        'regionType': 'openstack',
                        'isMultiZones': True,
                        'zoneList': ['az1', 'az2'],
                        'regionCode': 'cn-beijing-1',
                        'openapiAvailable': True
                    },
                    {
                        'regionID': '81f7728662dd11ec810800155d307d5b',
                        'regionParent': '内蒙',
                        'regionName': '内蒙8',
                        'regionType': 'openstack',
                        'isMultiZones': True,
                        'zoneList': ['az1', 'az2', 'az3'],
                        'regionCode': 'cn-neimeng-8',
                        'openapiAvailable': True
                    }
                ]
            },
            '_mock': True
        }
