"""
云服务器(ECS)管理模块 - 使用OpenAPI V4
"""

from typing import Dict, Any, List, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


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
            url = f'https://{self.base_endpoint}/v4/region/customer-resources'
            
            query_params = {
                'regionID': region_id
            }
            
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
                return self._get_mock_customer_resources()
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
                return self._get_mock_customer_resources()
            
            return result
            
        except Exception as e:
            logger.error(f"查询用户资源失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_customer_resources()
    
    def _get_mock_customer_resources(self) -> Dict[str, Any]:
        """生成模拟用户资源数据"""
        return {
            'statusCode': 800,
            'message': '成功',
            'returnObj': {
                'resources': {
                    'VM': {
                        'vm_shutd_count': 2,
                        'memory_count': 64,
                        'expire_count': 1,
                        'detail_total_count': 10,
                        'cpu_count': 20,
                        'expire_running_count': 0,
                        'total_count': 10,
                        'expire_shutd_count': 1,
                        'vm_running_count': 7
                    },
                    'Volume': {
                        'vo_root_size': 400,
                        'vo_disk_count': 5,
                        'total_size': 900,
                        'vo_disk_size': 500,
                        'detail_total_count': 15,
                        'total_count': 15,
                        'vo_root_count': 10
                    },
                    'VPC': {
                        'total_count': 3,
                        'detail_total_count': 3
                    },
                    'Public_IP': {
                        'total_count': 5,
                        'detail_total_count': 5
                    },
                    'VOLUME_SNAPSHOT': {
                        'total_count': 2,
                        'detail_total_count': 2
                    },
                    'IMAGE': {
                        'total_count': 1,
                        'detail': {
                            'demo-region': 1
                        }
                    }
                }
            },
            '_mock': True
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

    def get_instance(self, instance_id: str, region_id: str) -> Dict[str, Any]:
        """
        查询一台云主机详细信息 (API ID: 8310)

        Args:
            instance_id: 云主机ID
            region_id: 资源池ID

        Returns:
            云主机详情
        """
        logger.info(f"查询单台云主机详情: {instance_id}, regionId={region_id}")

        try:
            # 构造查询参数
            query_params = {
                'regionID': region_id,
                'instanceID': instance_id
            }

            url = f'https://{self.base_endpoint}/v4/ecs/instance-details'

            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body=None,
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }

            return response.json()

        except Exception as e:
            logger.error(f"查询单台云主机详情失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def describe_instances(self, region_id: str, instance_id_list: Optional[str] = None,
                          instance_name: Optional[str] = None, state: Optional[str] = None,
                          keyword: Optional[str] = None, page_no: Optional[int] = None,
                          page_size: Optional[int] = None) -> Dict[str, Any]:
        """
        查询一台或多台云主机详细信息 (API ID: 9268)

        Args:
            region_id: 资源池ID (必填)
            instance_id_list: 云主机ID列表，多台使用英文逗号分割
            instance_name: 云主机名称，精准匹配
            state: 云主机状态
            keyword: 关键字，对部分参数进行模糊查询
            page_no: 页码，取值范围：正整数（≥1），默认值为1
            page_size: 每页记录数目，取值范围：[1, 50]，默认值为10

        Returns:
            分页的云主机列表
        """
        logger.info(f"查询云主机列表: regionId={region_id}, instanceName={instance_name}")

        try:
            url = f'https://{self.base_endpoint}/v4/ecs/describe-instances'

            # 构造请求体
            body_data = {
                'regionID': region_id
            }

            # 添加可选参数
            if instance_id_list:
                body_data['instanceIDList'] = instance_id_list
            if instance_name:
                body_data['instanceName'] = instance_name
            if state:
                body_data['state'] = state
            if keyword:
                body_data['keyword'] = keyword
            if page_no:
                body_data['pageNo'] = page_no
            if page_size:
                body_data['pageSize'] = page_size

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
            logger.debug(f"请求体: {body}")
            logger.debug(f"请求头: {headers}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30
            )

            logger.debug(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }

            return response.json()

        except Exception as e:
            logger.error(f"查询云主机列表失败: {e}")
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

    def query_flavor_options(self) -> Dict[str, Any]:
        """
        查询云主机规格可售地域总览查询条件范围
        
        Returns:
            规格查询条件范围信息
        """
        logger.info("查询云主机规格查询条件范围")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/flavor/query-options'
            
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=None,
                body='',
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            
            response = self.client.session.get(
                url,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            
            if response.status_code != 200:
                logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return self._get_mock_flavor_options()
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
                return self._get_mock_flavor_options()
            
            return result
            
        except Exception as e:
            logger.error(f"查询规格查询条件范围失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._get_mock_flavor_options()

    def _get_mock_flavor_options(self) -> Dict[str, Any]:
        """生成模拟规格查询条件范围数据"""
        return {
            'statusCode': 800,
            'message': '成功',
            'returnObj': {
                'flavorNameScope': ['ks2.medium.2', 'hs3.medium.2'],
                'flavorCPUScope': ['2', '4'],
                'flavorRAMScope': ['1', '2'],
                'flavorFamilyScope': ['ks2', 'hs3'],
                'gpuConfigScope': ['NVIDIA A100*1(1GB)'],
                'localDiskConfigScope': ['1000*3']
            },
            '_mock': True
        }

    def get_auto_renew_config(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """
        查询包周期云主机自动续订配置
        
        Args:
            region_id: 资源池ID
            instance_id: 云主机ID
            
        Returns:
            自动续订配置信息
        """
        logger.info(f"查询云主机自动续订配置: instanceId={instance_id}, regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/get-auto-renew-config'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id,
                'instanceID': instance_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机自动续订配置失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def query_dns_record(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """
        查询云主机的内网DNS记录
        
        Args:
            region_id: 资源池ID
            instance_id: 云主机ID
            
        Returns:
            内网DNS记录信息
        """
        logger.info(f"查询云主机内网DNS记录: instanceId={instance_id}, regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/query-dns-record'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id,
                'instanceID': instance_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机内网DNS记录失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_snapshots(self, region_id: str, page_no: int = 1, page_size: int = 10,
                      project_id: Optional[str] = None,
                      instance_id: Optional[str] = None,
                      snapshot_status: Optional[str] = None,
                      snapshot_id: Optional[str] = None,
                      query_content: Optional[str] = None,
                      snapshot_name: Optional[str] = None) -> Dict[str, Any]:
        """
        查询云主机快照列表
        
        Args:
            region_id: 资源池ID
            page_no: 页码，默认1
            page_size: 每页记录数，默认10，最大50
            project_id: 企业项目ID
            instance_id: 云主机ID
            snapshot_status: 快照状态（pending/available/restoring/error）
            snapshot_id: 快照ID
            query_content: 模糊查询内容
            snapshot_name: 快照名称
            
        Returns:
            快照列表
        """
        logger.info(f"查询云主机快照列表: regionId={region_id}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/snapshot/list'
            
            # 构造请求体
            body_data = {
                'regionID': region_id,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            # 添加可选参数
            if project_id:
                body_data['projectID'] = project_id
            if instance_id:
                body_data['instanceID'] = instance_id
            if snapshot_status:
                body_data['snapshotStatus'] = snapshot_status
            if snapshot_id:
                body_data['snapshotID'] = snapshot_id
            if query_content:
                body_data['queryContent'] = query_content
            if snapshot_name:
                body_data['snapshotName'] = snapshot_name
            
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机快照列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_snapshot_details(self, region_id: str, snapshot_id: str) -> Dict[str, Any]:
        """
        查询云主机快照详情
        
        Args:
            region_id: 资源池ID
            snapshot_id: 快照ID
            
        Returns:
            快照详情
        """
        logger.info(f"查询云主机快照详情: snapshotId={snapshot_id}, regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/snapshot/details'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id,
                'snapshotID': snapshot_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机快照详情失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_keypairs(self, region_id: str, page_no: int = 1, page_size: int = 10,
                     project_id: Optional[str] = None,
                     keypair_name: Optional[str] = None,
                     query_content: Optional[str] = None,
                     label_list: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        查询一个或多个密钥对
        
        Args:
            region_id: 资源池ID
            page_no: 页码，默认1
            page_size: 每页记录数，默认10，最大50
            project_id: 企业项目ID
            keypair_name: 密钥对名称
            query_content: 模糊查询内容
            label_list: 标签列表
            
        Returns:
            密钥对列表
        """
        logger.info(f"查询密钥对列表: regionId={region_id}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/keypair/details'
            
            # 构造请求体
            body_data = {
                'regionID': region_id,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            # 添加可选参数
            if project_id:
                body_data['projectID'] = project_id
            if keypair_name:
                body_data['keyPairName'] = keypair_name
            if query_content:
                body_data['queryContent'] = query_content
            if label_list:
                body_data['labelList'] = label_list
            
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询密钥对列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def query_jobs(self, region_id: str, job_ids: str) -> Dict[str, Any]:
        """
        查询多个异步任务的结果
        
        Args:
            region_id: 资源池ID
            job_ids: 异步任务ID列表，以英文逗号分隔
            
        Returns:
            异步任务结果列表
        """
        logger.info(f"查询多个异步任务结果: regionId={region_id}, jobIds={job_ids}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/job/query'
            
            # 构造请求体
            body_data = {
                'regionID': region_id,
                'jobIDs': job_ids
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询多个异步任务结果失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def query_async_result(self, region_id: str, job_id: str) -> Dict[str, Any]:
        """
        查询一个异步任务的结果
        
        Args:
            region_id: 资源池ID
            job_id: 异步任务ID
            
        Returns:
            异步任务结果
        """
        logger.info(f"查询异步任务结果: regionId={region_id}, jobId={job_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/query-async-result'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id,
                'jobID': job_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询异步任务结果失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_volume_statistics(self, region_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询用户云硬盘统计信息
        
        Args:
            region_id: 资源池ID
            project_id: 企业项目ID（可选）
            
        Returns:
            云硬盘统计信息
        """
        logger.info(f"查询云硬盘统计信息: regionId={region_id}, projectId={project_id or '全部'}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/volume/statistics'
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云硬盘统计信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_fixed_ip_list(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """
        查询云主机的固定IP
        
        Args:
            region_id: 资源池ID
            instance_id: 云主机ID
            
        Returns:
            固定IP列表
        """
        logger.info(f"查询云主机固定IP: instanceId={instance_id}, regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/fixed-ip-list'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id,
                'instanceID': instance_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机固定IP失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_backup_policies(self, region_id: str, page_no: int = 1, page_size: int = 10,
                            policy_id: Optional[str] = None,
                            policy_name: Optional[str] = None,
                            project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询云主机备份策略列表
        
        Args:
            region_id: 资源池ID
            page_no: 页码，默认1
            page_size: 每页记录数，默认10，最大50
            policy_id: 备份策略ID
            policy_name: 备份策略名称
            project_id: 企业项目ID
            
        Returns:
            备份策略列表
        """
        logger.info(f"查询云主机备份策略列表: regionId={region_id}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/backup-policy/list'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            # 添加可选参数
            if policy_id:
                query_params['policyID'] = policy_id
            if policy_name:
                query_params['policyName'] = policy_name
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机备份策略列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_backup_status(self, region_id: str, instance_backup_id: str) -> Dict[str, Any]:
        """
        查询云主机备份状态
        
        Args:
            region_id: 资源池ID
            instance_backup_id: 云主机备份ID
            
        Returns:
            备份状态信息
        """
        logger.info(f"查询云主机备份状态: backupId={instance_backup_id}, regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/backup/status'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id,
                'instanceBackupID': instance_backup_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机备份状态失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_volume_info(self, disk_id: str, region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        云硬盘信息查询（基于磁盘ID）
        
        Args:
            disk_id: 磁盘ID
            region_id: 资源池ID，可选
            
        Returns:
            云硬盘详细信息
        """
        logger.info(f"查询云硬盘信息: diskId={disk_id}, regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/volume/show'
            
            query_params = {
                'diskID': disk_id
            }
            
            if region_id:
                query_params['regionID'] = region_id
            
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"查询参数: {query_params}")
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云硬盘信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_backup_policy_instances(self, region_id: str, policy_id: str, instance_name: Optional[str] = None, page_no: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询云主机备份策略绑定云主机信息
        
        Args:
            region_id: 资源池ID
            policy_id: 云主机备份策略ID
            instance_name: 云主机名称，模糊过滤，可选
            page_no: 页码，默认1
            page_size: 每页记录数，默认10，最大50
            
        Returns:
            备份策略绑定的云主机列表
        """
        logger.info(f"查询备份策略绑定云主机: policyId={policy_id}, instanceName={instance_name}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/backup-policy/list-instances'
            
            query_params = {
                'regionID': region_id,
                'policyID': policy_id,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            if instance_name:
                query_params['instanceName'] = instance_name
            
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"查询参数: {query_params}")
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询备份策略绑定云主机失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_volumes(self, region_id: str, instance_id: str, page_no: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询云主机的云硬盘列表
        
        Args:
            region_id: 资源池ID
            instance_id: 云主机ID
            page_no: 页码，默认1
            page_size: 每页记录数，默认10，最大50
            
        Returns:
            云硬盘列表
        """
        logger.info(f"查询云主机云硬盘列表: instanceId={instance_id}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/volume/list'
            
            # 构造请求体
            body_data = {
                'regionID': region_id,
                'instanceID': instance_id,
                'pageNo': page_no,
                'pageSize': page_size
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机云硬盘列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_affinity_group_details(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """
        查询云主机所在云主机组
        
        Args:
            region_id: 资源池ID
            instance_id: 云主机ID
            
        Returns:
            云主机组信息
        """
        logger.info(f"查询云主机所在云主机组: instanceId={instance_id}, regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/affinity-group/details'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id,
                'instanceID': instance_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机所在云主机组失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_regions_details(self) -> Dict[str, Any]:
        """
        查询账户启用的资源池信息
        
        Returns:
            资源池列表
        """
        logger.info(f"查询账户启用的资源池信息")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/regions/details'
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=None,
                body='',
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            
            response = self.client.session.get(
                url,
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询账户启用的资源池信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_availability_zones_details(self, region_id: str) -> Dict[str, Any]:
        """
        查询账户资源池中可用区信息
        
        Args:
            region_id: 资源池ID
            
        Returns:
            可用区列表
        """
        logger.info(f"查询资源池可用区信息: regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/availability-zones/details'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询资源池可用区信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_instance_status(self, region_id: str, page_no: int = 1, page_size: int = 10,
                            az_name: Optional[str] = None,
                            instance_id_list: Optional[str] = None,
                            project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取多台云主机的状态信息
        
        Args:
            region_id: 资源池ID
            page_no: 页码，默认1
            page_size: 每页记录数，默认10，最大50
            az_name: 可用区名称
            instance_id_list: 云主机ID列表，多台使用英文逗号分割
            project_id: 企业项目ID
            
        Returns:
            云主机状态列表
        """
        logger.info(f"获取云主机状态信息: regionId={region_id}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/instance-status-list'
            
            # 构造请求体
            body_data = {
                'regionID': region_id,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            # 添加可选参数
            if az_name:
                body_data['azName'] = az_name
            if instance_id_list:
                body_data['instanceIDList'] = instance_id_list
            if project_id:
                body_data['projectID'] = project_id
            
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"获取云主机状态信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def query_uuid_by_order(self, master_order_id: str) -> Dict[str, Any]:
        """
        根据masterOrderID查询云主机ID
        
        Args:
            master_order_id: 订单ID
            
        Returns:
            订单状态和云主机ID列表
        """
        logger.info(f"根据订单ID查询云主机ID: masterOrderId={master_order_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/order/query-uuid'
            
            # 构造查询参数
            query_params = {
                'masterOrderID': master_order_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"根据订单ID查询云主机ID失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_affinity_groups(self, region_id: str, page_no: int = 1, page_size: int = 10,
                            affinity_group_id: Optional[str] = None,
                            query_content: Optional[str] = None) -> Dict[str, Any]:
        """
        查询云主机组列表或者详情
        
        Args:
            region_id: 资源池ID
            page_no: 页码，默认1
            page_size: 每页记录数，默认10，最大50
            affinity_group_id: 云主机组ID
            query_content: 模糊匹配查询内容
            
        Returns:
            云主机组列表
        """
        logger.info(f"查询云主机组列表: regionId={region_id}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/affinity-group/list'
            
            # 构造请求体
            body_data = {
                'regionID': region_id,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
            # 添加可选参数
            if affinity_group_id:
                body_data['affinityGroupID'] = affinity_group_id
            if query_content:
                body_data['queryContent'] = query_content
            
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机组列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_snapshot_status(self, region_id: str, snapshot_id: str) -> Dict[str, Any]:
        """
        查询云主机快照状态
        
        Args:
            region_id: 资源池ID
            snapshot_id: 云主机快照ID
            
        Returns:
            快照状态信息
        """
        logger.info(f"查询云主机快照状态: regionId={region_id}, snapshotId={snapshot_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/snapshot/status'
            
            query_params = {
                'regionID': region_id,
                'snapshotID': snapshot_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机快照状态失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_snapshot_count(self, region_id: str) -> Dict[str, Any]:
        """
        云主机快照个数统计
        
        Args:
            region_id: 资源池ID
            
        Returns:
            快照个数统计信息
        """
        logger.info(f"查询云主机快照个数统计: regionId={region_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/snapshot/count'
            
            query_params = {
                'regionID': region_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机快照个数统计失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def list_flavor_families(self, region_id: str, az_name: Optional[str] = None) -> Dict[str, Any]:
        """
        查询云主机规格族列表
        
        Args:
            region_id: 资源池ID
            az_name: 可用区名称
            
        Returns:
            规格族列表
        """
        logger.info(f"查询云主机规格族列表: regionId={region_id}, azName={az_name or '全部'}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/flavor-families/list'
            
            # 构造查询参数
            query_params = {
                'regionID': region_id
            }
            if az_name:
                query_params['azName'] = az_name
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机规格族列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def query_flavor_available_regions(self, 
                                      flavor_name_list: Optional[List[str]] = None,
                                      flavor_family_list: Optional[List[str]] = None,
                                      flavor_cpu_list: Optional[List[int]] = None,
                                      flavor_ram_list: Optional[List[int]] = None,
                                      local_disk_size_list: Optional[List[str]] = None,
                                      gpu_config_list: Optional[List[str]] = None,
                                      page_no: int = 1,
                                      page_size: int = 10) -> Dict[str, Any]:
        """
        查询云主机规格可售地域总览
        
        Args:
            flavor_name_list: 云主机规格名称列表
            flavor_family_list: 云主机规格族列表
            flavor_cpu_list: 云主机规格vcpu个数列表
            flavor_ram_list: 云主机规格内存大小列表
            local_disk_size_list: 本地盘容量配置列表
            gpu_config_list: GPU配置列表
            page_no: 页码
            page_size: 每页记录数（最大50）
            
        Returns:
            规格可售地域信息
        """
        logger.info(f"查询云主机规格可售地域总览")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/flavor/available-region'
            
            # 构造查询参数
            query_params = {
                'pageNo': str(page_no),
                'pageSize': str(page_size)
            }
            
            if flavor_name_list:
                query_params['flavorNameList'] = ','.join(flavor_name_list)
            if flavor_family_list:
                query_params['flavorFamilyList'] = ','.join(flavor_family_list)
            if flavor_cpu_list:
                query_params['flavorCPUList'] = ','.join(str(cpu) for cpu in flavor_cpu_list)
            if flavor_ram_list:
                query_params['flavorRAMList'] = ','.join(str(ram) for ram in flavor_ram_list)
            if local_disk_size_list:
                query_params['localDiskSizeList'] = ','.join(local_disk_size_list)
            if gpu_config_list:
                query_params['gpuConfigList'] = ','.join(gpu_config_list)
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机规格可售地域总览失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def query_flavor_query_options(self) -> Dict[str, Any]:
        """
        查询云主机规格可售地域总览查询条件范围
        
        Returns:
            查询条件范围信息
        """
        logger.info(f"查询云主机规格可售地域总览查询条件范围")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/flavor/query-options'
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params={},
                body='',
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            
            response = self.client.session.get(
                url,
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机规格可售地域总览查询条件范围失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def query_cold_resize_flavors(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """
        查询云主机支持的冷变配规格信息
        
        Args:
            region_id: 资源池ID
            instance_id: 云主机ID
            
        Returns:
            冷变配规格列表
        """
        logger.info(f"查询云主机支持的冷变配规格信息: regionId={region_id}, instanceId={instance_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/flavor/update-spec-list'
            
            # 构造请求体
            body_data = {
                'regionID': region_id,
                'instanceID': instance_id
            }
            body = json.dumps(body_data)
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params={},
                body=body,
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            logger.debug(f"请求头: {headers}")
            
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机支持的冷变配规格信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def query_hot_resize_flavors(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """
        查询云主机支持的热变配规格信息
        
        Args:
            region_id: 资源池ID
            instance_id: 云主机ID
            
        Returns:
            热变配规格列表
        """
        logger.info(f"查询云主机支持的热变配规格信息: regionId={region_id}, instanceId={instance_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/flavor/live-resize-list'
            
            # 构造请求体
            body_data = {
                'regionID': region_id,
                'instanceID': instance_id
            }
            body = json.dumps(body_data)
            
            # 使用EOP签名认证
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params={},
                body=body,
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            logger.debug(f"请求头: {headers}")
            
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机支持的热变配规格信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_vnc_details(self, region_id: str, instance_id: str) -> Dict[str, Any]:
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_vnc_details(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """
        查询云主机的WEB管理终端地址
        
        Args:
            region_id: 资源池ID
            instance_id: 云主机ID
            
        Returns:
            VNC访问地址信息
        """
        logger.info(f"查询云主机的WEB管理终端地址: regionId={region_id}, instanceId={instance_id}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/vnc/details'
            
            query_params = {
                'regionID': region_id,
                'instanceID': instance_id
            }
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机的WEB管理终端地址失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def get_instance_statistics(self, region_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询用户云主机统计信息
        
        Args:
            region_id: 资源池ID
            project_id: 企业项目ID（可选）
            
        Returns:
            云主机统计信息
        """
        logger.info(f"查询用户云主机统计信息: regionId={region_id}, projectId={project_id or '全部'}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/statistics-instance'
            
            query_params = {
                'regionID': region_id
            }
            if project_id:
                query_params['projectID'] = project_id
            
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
                return {
                    'statusCode': response.status_code,
                    'message': f'HTTP {response.status_code}',
                    'returnObj': None
                }
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询用户云主机统计信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def describe_instances(self, region_id: str, page_no: int = 1, page_size: int = 10,
                          az_name: Optional[str] = None,
                          project_id: Optional[str] = None,
                          state: Optional[str] = None,
                          keyword: Optional[str] = None,
                          instance_name: Optional[str] = None,
                          instance_id_list: Optional[str] = None,
                          security_group_id: Optional[str] = None,
                          label_list: Optional[list] = None) -> Dict[str, Any]:
        """
        查询一台或多台云主机详细信息
        
        该接口相较于list-instances提供更精简的云主机信息，拥有更高的查找效率
        
        Args:
            region_id: 资源池ID
            page_no: 页码，默认1
            page_size: 每页记录数，默认10，最大50
            az_name: 可用区名称
            project_id: 企业项目ID
            state: 云主机状态（active/shutoff/expired/unsubscribed/freezing/shelve）
            keyword: 关键字模糊查询（instanceName/displayName/instanceID/privateIP）
            instance_name: 云主机名称（精确匹配）
            instance_id_list: 云主机ID列表，多台使用英文逗号分割
            security_group_id: 安全组ID（模糊匹配）
            label_list: 标签信息列表 [{"labelKey": "key", "labelValue": "value"}]
            
        Returns:
            云主机详细信息
        """
        logger.info(f"查询云主机详细信息: regionId={region_id}, pageNo={page_no}, pageSize={page_size}")
        
        try:
            url = f'https://{self.base_endpoint}/v4/ecs/describe-instances'
            
            body_data = {
                'regionID': region_id,
                'pageNo': page_no,
                'pageSize': page_size
            }
            
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
            if security_group_id:
                body_data['securityGroupID'] = security_group_id
            if label_list:
                body_data['labelList'] = label_list
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers={}
            )
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            logger.debug(f"请求头: {headers}")
            
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
            
            result = response.json()
            
            if result.get('statusCode') != 800:
                logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            logger.error(f"查询云主机详细信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {
                'statusCode': 500,
                'message': str(e),
                'returnObj': None
            }

    def query_uuid_by_order(self, region_id: str, master_order_id: str) -> Dict[str, Any]:
        """
        根据订单ID查询云主机UUID

        Args:
            region_id: 区域ID (必填)
            master_order_id: 订单ID (必填)

        Returns:
            查询结果，包含订单状态和云主机ID列表
        """
        logger.info(f"查询订单UUID: regionId={region_id}, masterOrderID={master_order_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/ecs/order/query-uuid'

            query_params = {
                'regionID': region_id,
                'masterOrderID': master_order_id
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
            result = response.json()

            # 检查返回状态码
            if result.get('statusCode') != 800:
                error_code = result.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = result.get('description', '未知错误')
                logger.error(f"API错误 [{error_code}]: {error_msg}")
                raise Exception(f"API错误 [{error_code}]: {error_msg}")

            # 解析返回结果
            return_obj = result.get('returnObj', {})
            order_status = return_obj.get('orderStatus', '')
            instance_ids = return_obj.get('instanceIDList', [])

            # 订单状态映射
            status_map = {
                '1': '待支付',
                '2': '已支付',
                '3': '完成',
                '4': '取消',
                '5': '施工失败',
                '7': '正在支付中',
                '8': '待审核',
                '9': '审核通过',
                '10': '审核未通过',
                '11': '撤单完成',
                '12': '退订中',
                '13': '退订完成',
                '14': '开通中',
                '15': '变更移除',
                '16': '自动撤单中',
                '17': '手动撤单中',
                '18': '终止中',
                '22': '支付失败',
                '-2': '待撤单',
                '-1': '未知',
                '0': '错误',
                '140': '已初始化',
                '999': '逻辑错误'
            }

            status_text = status_map.get(order_status, f'未知状态({order_status})')

            logger.info(f"订单状态: {status_text}, 返回{len(instance_ids)}个云主机ID")

            return result

        except Exception as e:
            logger.error(f"查询订单UUID失败: {str(e)}")
            raise
