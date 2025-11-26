"""
天翼云监控服务客户端
提供云专线流量等监控数据查询功能
"""

from typing import Dict, Any, List, Optional, Union
import json
from datetime import datetime, timedelta
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class MonitorClient:
    """天翼云监控服务客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化监控服务客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'monitor'
        self.base_endpoint = 'monitor-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def query_custom_item_trendmetricdata(
            self,
            region_id: str,
            custom_item_id: str,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None,
            period: int = 300,
            dimensions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        查询自定义监控项的时序指标趋势监控数据

        Args:
            region_id: 资源池ID
            custom_item_id: 自定义监控项ID
            start_time: 查询起始时间戳（Unix时间戳，秒），默认为24小时前
            end_time: 查询结束时间戳（Unix时间戳，秒），默认为当前时间
            period: 聚合周期（秒），默认300秒（5分钟）
            dimensions: 自定义监控项维度，格式：[{"name": "维度名", "value": ["值1", "值2"]}]

        Returns:
            监控数据结果
        """
        if not start_time:
            start_time = int((datetime.now() - timedelta(hours=24)).timestamp())
        if not end_time:
            end_time = int(datetime.now().timestamp())

        logger.info(f"查询自定义监控趋势数据: custom_item_id={custom_item_id}, "
                   f"start_time={start_time}, end_time={end_time}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-custom-item-trendmetricdata"
            
            body_data = {
                'regionID': region_id,
                'customItemID': custom_item_id,
                'startTime': start_time,
                'endTime': end_time,
                'period': period
            }
            
            if dimensions:
                body_data['dimensions'] = dimensions
            
            body = json.dumps(body_data)
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {}),
                    'custom_item_id': custom_item_id
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询自定义监控趋势数据失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_dcaas_traffic(self, device_id: str, region_id: str,
                           start_time: Optional[str] = None,
                           end_time: Optional[str] = None,
                           period: int = 300,
                           metric: str = 'network_incoming_bytes') -> Dict[str, Any]:
        """
        查询云专线流量监控数据

        Args:
            device_id: 云专线实例ID
            region_id: 资源池ID
            start_time: 开始时间（格式：2024-01-01T00:00:00Z），默认为24小时前
            end_time: 结束时间（格式：2024-01-01T00:00:00Z），默认为当前时间
            period: 统计周期（秒），默认300秒（5分钟）
            metric: 监控指标，可选值：
                   - network_incoming_bytes: 网络流入流量
                   - network_outgoing_bytes: 网络流出流量

        Returns:
            监控数据结果
        """
        if not start_time:
            start_time = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')
        if not end_time:
            end_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        logger.info(f"查询云专线流量: device_id={device_id}, metric={metric}, "
                   f"start_time={start_time}, end_time={end_time}")

        try:
            url = f"https://{self.base_endpoint}/v4.2/monitor/historical-data"
            
            body_data = {
                'regionID': region_id,
                'namespace': 'SYS.DCAAS',
                'metricName': metric,
                'dimensions': [
                    {
                        'name': 'deviceID',
                        'value': device_id
                    }
                ],
                'startTime': start_time,
                'endTime': end_time,
                'period': period
            }
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params={'regionID': region_id},
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {}),
                    'metric': metric,
                    'device_id': device_id,
                    'period': period
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('statusCode'),
                    'message': result.get('errorMessage', '未知错误')
                }
                
        except Exception as e:
            logger.error(f"查询云专线流量失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def list_dcaas_devices(self, region_id: str) -> Dict[str, Any]:
        """
        查询云专线设备列表

        Args:
            region_id: 资源池ID

        Returns:
            云专线设备列表
        """
        logger.info(f"查询云专线设备列表: region_id={region_id}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-dcaas-list"
            
            body_data = {
                'regionID': region_id
            }
            
            body = json.dumps(body_data)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params={'regionID': region_id},
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', [])
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('statusCode'),
                    'message': result.get('errorMessage', '未知错误')
                }
                
        except Exception as e:
            logger.error(f"查询云专线设备列表失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_cpu_top(self, region_id: str, number: int = 3) -> Dict[str, Any]:
        """
        查询云主机CPU使用率Top-N

        Args:
            region_id: 资源池ID
            number: 选取TOP值的数量，默认为3

        Returns:
            CPU使用率Top-N结果
        """
        logger.info(f"查询云主机CPU使用率Top-N: region_id={region_id}, number={number}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-cpu-top"
            
            body_data = {
                'regionID': region_id,
                'number': number
            }
            
            body = json.dumps(body_data)
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询CPU使用率Top-N失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_mem_top(self, region_id: str, number: int = 3) -> Dict[str, Any]:
        """
        查询云主机内存使用率Top-N

        Args:
            region_id: 资源池ID
            number: 选取TOP值的数量，默认为3

        Returns:
            内存使用率Top-N结果
        """
        logger.info(f"查询云主机内存使用率Top-N: region_id={region_id}, number={number}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-mem-top"
            
            body_data = {
                'regionID': region_id,
                'number': number
            }
            
            body = json.dumps(body_data)
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询内存使用率Top-N失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_disk_top(self, region_id: str, number: int = 3) -> Dict[str, Any]:
        """
        查询云主机磁盘使用率Top-N

        Args:
            region_id: 资源池ID
            number: 选取TOP值的数量，默认为3

        Returns:
            磁盘使用率Top-N结果
        """
        logger.info(f"查询云主机磁盘使用率Top-N: region_id={region_id}, number={number}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-disk-top"
            
            body_data = {
                'regionID': region_id,
                'number': number
            }
            
            body = json.dumps(body_data)
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询磁盘使用率Top-N失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_monitor_items(
            self,
            region_id: str,
            service: Optional[str] = None,
            dimension: Optional[str] = None,
            item_type: Optional[str] = None,
            is_enterprise_project: Optional[bool] = None,
            ignore_items: Optional[bool] = None) -> Dict[str, Any]:
        """
        查询服务维度及监控项

        Args:
            region_id: 资源池ID
            service: 服务（如：ecs）
            dimension: 维度（如：ecs）
            item_type: 监控项类型（series: 指标类型, event: 事件类型）
            is_enterprise_project: 是否支持企业项目
            ignore_items: 监控项过滤参数，为true时不展示监控项信息

        Returns:
            服务维度及监控项信息
        """
        logger.info(f"查询服务维度及监控项: region_id={region_id}, service={service}, dimension={dimension}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-items"
            
            query_params = {'regionID': region_id}
            
            if service:
                query_params['service'] = service
            if dimension:
                query_params['dimension'] = dimension
            if item_type:
                query_params['itemType'] = item_type
            if is_enterprise_project is not None:
                query_params['isEnterpriseProject'] = str(is_enterprise_project).lower()
            if ignore_items is not None:
                query_params['ignoreItems'] = str(ignore_items).lower()
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询服务维度及监控项失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_sys_services(self, region_id: str) -> Dict[str, Any]:
        """
        查询系统看板支持的服务维度

        Args:
            region_id: 资源池ID

        Returns:
            系统看板支持的服务维度信息
        """
        logger.info(f"查询系统看板支持的服务维度: region_id={region_id}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/monitor-board/query-sys-services"
            
            query_params = {'regionID': region_id}
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询系统看板支持的服务维度失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def describe_monitor_board(self, region_id: str, board_id: str) -> Dict[str, Any]:
        """
        查看监控看板详细信息

        Args:
            region_id: 资源池ID
            board_id: 监控看板ID

        Returns:
            监控看板详细信息
        """
        logger.info(f"查看监控看板详情: region_id={region_id}, board_id={board_id}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/monitor-board/describe"
            
            query_params = {
                'regionID': region_id,
                'boardID': board_id
            }
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                error_msg = result.get('msgDesc', result.get('message', '未知错误'))
                
                # 特殊处理看板不存在的情况
                if error_code == 'Monitor.MonitorBoard.NotExist':
                    return {
                        'success': False,
                        'error': 'MonitorBoardNotExist',
                        'message': error_msg
                    }
                
                return {
                    'success': False,
                    'error': error_code,
                    'message': error_msg
                }
                
        except Exception as e:
            logger.error(f"查看监控看板详情失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def list_monitor_boards(
            self,
            region_id: str,
            board_type: Optional[str] = None,
            name: Optional[str] = None,
            service: Optional[str] = None,
            dimension: Optional[str] = None,
            page_no: Optional[int] = None,
            page_size: Optional[int] = None) -> Dict[str, Any]:
        """
        查询监控看板列表

        Args:
            region_id: 资源池ID
            board_type: 看板类型（all/system/custom）
            name: 名称模糊搜索
            service: 服务（仅当boardType为system时有效）
            dimension: 维度（仅当boardType为system时有效）
            page_no: 页码，默认为1
            page_size: 页大小，默认为10

        Returns:
            监控看板列表
        """
        logger.info(f"查询监控看板列表: region_id={region_id}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/monitor-board/list"
            
            query_params = {'regionID': region_id}
            
            if board_type:
                query_params['boardType'] = board_type
            if name:
                query_params['name'] = name
            if service:
                query_params['service'] = service
            if dimension:
                query_params['dimension'] = dimension
            if page_no:
                query_params['pageNo'] = page_no
            if page_size:
                query_params['pageSize'] = page_size
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询监控看板列表失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def describe_monitor_view(self, region_id: str, view_id: str) -> Dict[str, Any]:
        """
        查看监控视图详细信息

        Args:
            region_id: 资源池ID
            view_id: 监控视图ID

        Returns:
            监控视图详细信息
        """
        logger.info(f"查看监控视图详情: region_id={region_id}, view_id={view_id}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/monitor-board/describe-view"
            
            query_params = {
                'regionID': region_id,
                'viewID': view_id
            }
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                error_msg = result.get('msgDesc', result.get('message', '未知错误'))
                
                # 特殊处理视图不存在的情况
                if error_code == 'Monitor.MonitorBoard.ViewNotExist':
                    return {
                        'success': False,
                        'error': 'MonitorViewNotExist',
                        'message': error_msg
                    }
                
                return {
                    'success': False,
                    'error': error_code,
                    'message': error_msg
                }
                
        except Exception as e:
            logger.error(f"查看监控视图详情失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_view_data(
            self,
            region_id: str,
            view_id: str,
            start_time: Optional[int] = None,
            end_time: Optional[int] = None,
            fun: Optional[str] = None,
            period: Optional[int] = None) -> Dict[str, Any]:
        """
        查询监控视图数据

        Args:
            region_id: 资源池ID
            view_id: 面板ID
            start_time: 查询起始Unix时间戳
            end_time: 查询结束Unix时间戳
            fun: 聚合类型（raw/avg/min/max/variance/sum）
            period: 聚合周期（秒）

        Returns:
            监控视图数据
        """
        logger.info(f"查询监控视图数据: region_id={region_id}, view_id={view_id}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/monitor-board/query-view-data"
            
            body_data = {
                'regionID': region_id,
                'viewID': view_id
            }
            
            if start_time:
                body_data['startTime'] = start_time
            if end_time:
                body_data['endTime'] = end_time
            if fun:
                body_data['fun'] = fun
            if period:
                body_data['period'] = period
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询监控视图数据失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_resource_groups(
            self,
            region_id: str,
            name: Optional[str] = None,
            res_group_id: Optional[str] = None,
            page_no: Optional[int] = None,
            page_size: Optional[int] = None) -> Dict[str, Any]:
        """
        查询资源分组列表

        Args:
            region_id: 资源池ID
            name: 名称模糊搜索
            res_group_id: 资源分组ID搜索
            page_no: 页码，默认为1
            page_size: 每页数量，默认10

        Returns:
            资源分组列表
        """
        logger.info(f"查询资源分组列表: region_id={region_id}")

        try:
            url = f"https://{self.base_endpoint}/v4.1/monitor/query-resource-groups"
            
            query_params = {'regionID': region_id}
            
            if name:
                query_params['name'] = name
            if res_group_id:
                query_params['resGroupID'] = res_group_id
            if page_no:
                query_params['pageNo'] = page_no
            if page_size:
                query_params['pageSize'] = page_size
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询资源分组列表失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def describe_resource_group(
            self,
            res_group_id: str,
            service: Optional[str] = None,
            dimension: Optional[str] = None,
            instance: Optional[str] = None) -> Dict[str, Any]:
        """
        查询指定资源分组详情

        Args:
            res_group_id: 资源分组ID
            service: 云监控服务
            dimension: 云监控维度
            instance: 对resource.value具体资源进行模糊查询

        Returns:
            资源分组详情信息
        """
        logger.info(f"查询资源分组详情: res_group_id={res_group_id}")

        try:
            url = f"https://{self.base_endpoint}/v4.1/monitor/describe-resource-group"
            
            query_params = {'resGroupID': res_group_id}
            
            if service:
                query_params['service'] = service
            if dimension:
                query_params['dimension'] = dimension
            if instance:
                query_params['instance'] = instance
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                # 特殊错误码处理
                error_code = result.get('errorCode', result.get('statusCode'))
                if error_code == 'Monitor.ResourceGroup.ResourceGroupNotExist':
                    logger.warning(f"资源分组不存在: {res_group_id}")
                    return {
                        'success': False,
                        'error': 'ResourceGroupNotExist',
                        'message': '资源分组不存在'
                    }
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询资源分组详情失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_latest_metric_data(
            self,
            region_id: str,
            service: str,
            dimension: str,
            item_name_list: List[str],
            dimensions: List[Dict[str, List[str]]]) -> Dict[str, Any]:
        """
        查询指定设备的实时监控数据

        Args:
            region_id: 资源池ID
            service: 云监控服务
            dimension: 云监控维度
            item_name_list: 待查监控项名称列表，单次请求长度限制为10
            dimensions: 查询设备标签列表，用于定位目标设备，多标签查询取交集，单次请求设备数量限制为10

        Returns:
            实时监控数据
        """
        logger.info(f"查询实时监控数据: region_id={region_id}, service={service}, dimension={dimension}")
        
        # 参数校验
        if len(item_name_list) > 10:
            logger.error("itemNameList长度超过限制(10)")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'itemNameList长度不能超过10'
            }
            
        if len(dimensions) > 10:
            logger.error("dimensions设备数量超过限制(10)")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'dimensions设备数量不能超过10'
            }
            
        # 检查dimensions中的value数量
        for dim in dimensions:
            if 'value' in dim and len(dim['value']) > 10:
                logger.error("dimensions中value数量超过限制(10)")
                return {
                    'success': False,
                    'error': 'ParameterError',
                    'message': 'dimensions中value数量不能超过10'
                }

        try:
            url = f"https://{self.base_endpoint}/v4.2/monitor/query-latest-metric-data"
            
            body_data = {
                'regionID': region_id,
                'service': service,
                'dimension': dimension,
                'itemNameList': item_name_list,
                'dimensions': dimensions
            }
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询实时监控数据失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_history_metric_data(
            self,
            region_id: str,
            service: str,
            dimension: str,
            item_name_list: List[str],
            start_time: int,
            end_time: int,
            dimensions: List[Dict[str, List[str]]],
            fun: str = 'avg',
            period: Optional[int] = None) -> Dict[str, Any]:
        """
        查询指定时间段内的设备时序指标监控数据

        Args:
            region_id: 资源池ID
            service: 云监控服务
            dimension: 云监控维度
            item_name_list: 待查监控项名称列表，单次请求长度限制为10
            start_time: 查询起始Unix时间戳，秒级
            end_time: 查询结束Unix时间戳，秒级
            dimensions: 查询设备标签列表，用于定位目标设备，多标签查询取交集，单次请求设备数量限制为10
            fun: 聚合类型，默认值为avg，取值范围:raw、avg、min、max、variance、sum
            period: 聚合周期，单位：秒，默认300，需不小于60，推荐使用60的整倍数。当fun为raw时本参数无效。

        Returns:
            历史监控数据
        """
        logger.info(f"查询历史监控数据: region_id={region_id}, service={service}, dimension={dimension}")
        
        # 参数校验
        if len(item_name_list) > 10:
            logger.error("itemNameList长度超过限制(10)")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'itemNameList长度不能超过10'
            }
            
        if len(dimensions) > 10:
            logger.error("dimensions设备数量超过限制(10)")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'dimensions设备数量不能超过10'
            }
            
        # 检查dimensions中的value数量
        for dim in dimensions:
            if 'value' in dim and len(dim['value']) > 10:
                logger.error("dimensions中value数量超过限制(10)")
                return {
                    'success': False,
                    'error': 'ParameterError',
                    'message': 'dimensions中value数量不能超过10'
                }
                
        # 校验时间参数
        if start_time >= end_time:
            logger.error("startTime必须小于endTime")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'startTime必须小于endTime'
            }
            
        # 校验fun参数
        valid_fun_values = ['raw', 'avg', 'min', 'max', 'variance', 'sum']
        if fun not in valid_fun_values:
            logger.error(f"fun参数必须在{valid_fun_values}范围内")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': f'fun参数必须在{valid_fun_values}范围内'
            }
            
        # 校验period参数
        if period is not None and period < 60:
            logger.error("period参数不能小于60")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'period参数不能小于60'
            }

        try:
            url = f"https://{self.base_endpoint}/v4.2/monitor/query-history-metric-data"
            
            body_data = {
                'regionID': region_id,
                'service': service,
                'dimension': dimension,
                'itemNameList': item_name_list,
                'startTime': start_time,
                'endTime': end_time,
                'dimensions': dimensions,
                'fun': fun
            }
            
            # 只有当fun不为raw且period不为None时才添加period参数
            if fun != 'raw' and period is not None:
                body_data['period'] = period
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询历史监控数据失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_event_services(
            self,
            region_id: str,
            service: Optional[str] = None,
            monitor_type: Optional[str] = None) -> Dict[str, Any]:
        """
        获取资源池下服务维度信息（事件监控）

        Args:
            region_id: 资源池ID
            service: 服务（可选）
            monitor_type: 监控类型，如果为event则表示事件类型（可选）

        Returns:
            服务维度信息
        """
        logger.info(f"查询事件服务维度信息: region_id={region_id}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/events/query-services"
            
            query_params = {'regionID': region_id}
            
            if service:
                query_params['service'] = service
            if monitor_type:
                query_params['monitorType'] = monitor_type
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询事件服务维度信息失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def count_event_data(
            self,
            region_id: str,
            event_name: str,
            service: str,
            dimension: str,
            start_time: int,
            end_time: int,
            period: int,
            res_group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        根据指定时间段统计指定事件发生情况

        Args:
            region_id: 资源池ID
            event_name: 事件指标
            service: 服务
            dimension: 维度
            start_time: 查询起始时间戳
            end_time: 查询截止时间戳
            period: 统计周期
            res_group_id: 资源分组ID（可选）

        Returns:
            事件统计数据
        """
        logger.info(f"统计事件数据: region_id={region_id}, event_name={event_name}, service={service}, dimension={dimension}")
        
        # 参数校验
        if start_time >= end_time:
            logger.error("startTime必须小于endTime")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'startTime必须小于endTime'
            }
            
        if period < 60:
            logger.error("period参数不能小于60")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'period参数不能小于60'
            }

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/events/count-data"
            
            body_data = {
                'regionID': region_id,
                'eventName': event_name,
                'service': service,
                'dimension': dimension,
                'startTime': start_time,
                'endTime': end_time,
                'period': period
            }
            
            if res_group_id:
                body_data['resGroupID'] = res_group_id
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                # 特殊错误码处理
                if error_code == 'Monitor.EventMonitor.DimensionNotSupport':
                    logger.warning(f"该维度的事件暂不支持: {dimension}")
                    return {
                        'success': False,
                        'error': 'DimensionNotSupport',
                        'message': '该维度的事件暂不支持'
                    }
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"统计事件数据失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_event_list(
            self,
            region_id: str,
            service: str,
            dimension: str,
            start_time: int,
            end_time: int,
            event_name_list: Optional[List[str]] = None,
            page_no: Optional[int] = None,
            page_size: Optional[int] = None,
            res_group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        根据指定时间段查询事件发生情况

        Args:
            region_id: 资源池ID
            service: 服务
            dimension: 维度
            start_time: 查询起始时间戳
            end_time: 查询截止时间戳
            event_name_list: 事件指标列表（可选，不传默认全部事件指标）
            page_no: 页码，默认为1
            page_size: 页大小，默认为20
            res_group_id: 资源分组ID（可选）

        Returns:
            事件列表数据
        """
        logger.info(f"查询事件列表: region_id={region_id}, service={service}, dimension={dimension}")
        
        # 参数校验
        if start_time >= end_time:
            logger.error("startTime必须小于endTime")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'startTime必须小于endTime'
            }

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/events/query-list"
            
            body_data = {
                'regionID': region_id,
                'service': service,
                'dimension': dimension,
                'startTime': start_time,
                'endTime': end_time
            }
            
            if event_name_list:
                body_data['eventNameList'] = event_name_list
            if page_no:
                body_data['pageNo'] = page_no
            if page_size:
                body_data['pageSize'] = page_size
            if res_group_id:
                body_data['resGroupID'] = res_group_id
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                # 特殊错误码处理
                if error_code == 'Monitor.EventMonitor.DimensionNotSupport':
                    logger.warning(f"该维度的事件暂不支持: {dimension}")
                    return {
                        'success': False,
                        'error': 'DimensionNotSupport',
                        'message': '该维度的事件暂不支持'
                    }
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询事件列表失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_event_detail(self, region_id: str, event_name: str, service: str, 
                          dimension: str, start_time: int, end_time: int,
                          page_no: Optional[int] = None, page_size: Optional[int] = None,
                          res_group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询事件详情
        
        Args:
            region_id: 资源池ID
            event_name: 事件指标名称
            service: 服务
            dimension: 维度
            start_time: 查询起始时间戳（秒）
            end_time: 查询截止时间戳（秒）
            page_no: 页码，默认为1
            page_size: 页大小，默认为20
            res_group_id: 资源分组ID（可选）
            
        Returns:
            事件详情数据
        """
        logger.info(f"查询事件详情: region_id={region_id}, event_name={event_name}, service={service}, dimension={dimension}")
        
        # 参数校验
        if start_time >= end_time:
            logger.error("startTime必须小于endTime")
            return {
                'success': False,
                'error': 'ParameterError',
                'message': 'startTime必须小于endTime'
            }

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/events/query-detail"
            
            body_data = {
                'regionID': region_id,
                'eventName': event_name,
                'service': service,
                'dimension': dimension,
                'startTime': start_time,
                'endTime': end_time
            }
            
            if page_no:
                body_data['pageNo'] = page_no
            if page_size:
                body_data['pageSize'] = page_size
            if res_group_id:
                body_data['resGroupID'] = res_group_id
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                # 特殊错误码处理
                if error_code == 'Monitor.EventMonitor.DimensionNotSupport':
                    logger.warning(f"该维度的事件暂不支持: {dimension}")
                    return {
                        'success': False,
                        'error': 'DimensionNotSupport',
                        'message': '该维度的事件暂不支持'
                    }
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询事件详情失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_events(self, region_id: str, service: str, dimension: str) -> Dict[str, Any]:
        """
        查询事件
        
        Args:
            region_id: 资源池ID
            service: 服务
            dimension: 维度
            
        Returns:
            事件列表数据
        """
        logger.info(f"查询事件: region_id={region_id}, service={service}, dimension={dimension}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/events/query-events"
            
            query_params = {
                'regionID': region_id,
                'service': service,
                'dimension': dimension
            }
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询事件失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_custom_events(self, region_id: str, custom_event_id: Optional[str] = None,
                           name: Optional[str] = None, page_no: Optional[int] = None,
                           page_size: Optional[int] = None) -> Dict[str, Any]:
        """
        查询自定义事件
        
        Args:
            region_id: 资源池ID
            custom_event_id: 自定义事件ID（可选）
            name: 事件名称，支持模糊搜索（可选）
            page_no: 页码，默认为1
            page_size: 每页大小，默认为20
            
        Returns:
            自定义事件列表数据
        """
        logger.info(f"查询自定义事件: region_id={region_id}, custom_event_id={custom_event_id}, name={name}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-custom-events"
            
            query_params = {'regionID': region_id}
            
            if custom_event_id:
                query_params['customEventID'] = custom_event_id
            if name:
                query_params['name'] = name
            if page_no:
                query_params['pageNo'] = page_no
            if page_size:
                query_params['pageSize'] = page_size
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询自定义事件失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_custom_event_data(self, region_id: str, custom_event_id_list: Optional[List[str]] = None,
                                start_time: Optional[int] = None, end_time: Optional[int] = None,
                                page_no: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """
        查询自定义事件监控详情
        
        Args:
            region_id: 资源池ID
            custom_event_id_list: 自定义事件ID列表（可选）
            start_time: 查询起始时间戳（秒），默认7天前
            end_time: 查询截止时间戳（秒），默认当前时间
            page_no: 页码，默认为1
            page_size: 每页大小，默认为20
            
        Returns:
            自定义事件监控详情数据
        """
        logger.info(f"查询自定义事件监控详情: region_id={region_id}, custom_event_id_list={custom_event_id_list}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-custom-event-data"
            
            body_data = {'regionID': region_id}
            
            if custom_event_id_list:
                body_data['customEventID'] = custom_event_id_list
            if start_time:
                body_data['startTime'] = start_time
            if end_time:
                body_data['endTime'] = end_time
            if page_no:
                body_data['pageNo'] = page_no
            if page_size:
                body_data['pageSize'] = page_size
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询自定义事件监控详情失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def describe_custom_event_alarm_rule(self, region_id: str, alarm_rule_id: str) -> Dict[str, Any]:
        """
        查看自定义事件告警规则详情
        
        Args:
            region_id: 资源池ID
            alarm_rule_id: 告警规则ID
            
        Returns:
            自定义事件告警规则详情数据
        """
        logger.info(f"查看自定义事件告警规则详情: region_id={region_id}, alarm_rule_id={alarm_rule_id}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/describe-custom-event-alarm-rule"
            
            query_params = {
                'regionID': region_id,
                'alarmRuleID': alarm_rule_id
            }
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                # 特殊错误码处理
                if error_code == 'Monitor.CustomAlarmRule.RuleNotFound':
                    logger.warning(f"告警规则不存在: {alarm_rule_id}")
                    return {
                        'success': False,
                        'error': 'RuleNotFound',
                        'message': '告警规则不存在'
                    }
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查看自定义事件告警规则详情失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_alert_history(self, region_id: str, status: int, 
                           resource_group_id: Optional[str] = None,
                           search_key: Optional[str] = None, search_value: Optional[str] = None,
                           service: Optional[List[str]] = None,
                           start_time: Optional[int] = None, end_time: Optional[int] = None,
                           page_no: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """
        查询告警历史
        
        Args:
            region_id: 资源池ID
            status: 状态（0：正在告警，1：告警历史）
            resource_group_id: 资源分组ID（可选）
            search_key: 搜索关键词（alarmRuleID/name）
            search_value: 搜索值
            service: 告警服务列表（可选）
            start_time: 起始时间戳（秒），status=1时使用
            end_time: 结束时间戳（秒），status=1时使用
            page_no: 页码，默认为1
            page_size: 页大小，默认为10
            
        Returns:
            告警历史数据
        """
        logger.info(f"查询告警历史: region_id={region_id}, status={status}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-alert-history"
            
            body_data = {
                'regionID': region_id,
                'status': status
            }
            
            if resource_group_id:
                body_data['resourceGroupID'] = resource_group_id
            if search_key:
                body_data['searchKey'] = search_key
            if search_value:
                body_data['searchValue'] = search_value
            if service:
                body_data['service'] = service
            if start_time:
                body_data['startTime'] = start_time
            if end_time:
                body_data['endTime'] = end_time
            if page_no:
                body_data['pageNo'] = page_no
            if page_size:
                body_data['pageSize'] = page_size
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询告警历史失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_alert_history_info(self, issue_id: str) -> Dict[str, Any]:
        """
        查询告警历史详情
        
        Args:
            issue_id: 告警历史ID
            
        Returns:
            告警历史详情数据
        """
        logger.info(f"查询告警历史详情: issue_id={issue_id}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-alert-history-info"
            
            query_params = {'issueID': issue_id}
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', [])
                }
            else:
                logger.error(f"API返回错误: {result}")
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询告警历史详情失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_alarm_top_dimension(self, region_id: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        """
        查询告警Top产品
        
        Args:
            region_id: 资源池ID
            time_range: 时间范围（7d/24h/6h），默认7d
            
        Returns:
            告警Top产品数据
        """
        logger.info(f"查询告警Top产品: region_id={region_id}, range={time_range}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-alarm-top-dimension"
            
            query_params = {'regionID': region_id}
            
            if time_range:
                query_params['range'] = time_range
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', {})
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                # 特殊错误码处理
                if error_code == 'Openapi.Overview.ParamValueOutOfRange':
                    logger.warning(f"参数取值超出范围: {time_range}")
                    return {
                        'success': False,
                        'error': 'ParamValueOutOfRange',
                        'message': '参数取值超出范围'
                    }
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询告警Top产品失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_alarm_top_resource(self, region_id: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        """
        查询告警Top实例
        
        Args:
            region_id: 资源池ID
            time_range: 时间范围（7d/24h/6h），默认7d
            
        Returns:
            告警Top实例数据
        """
        logger.info(f"查询告警Top实例: region_id={region_id}, range={time_range}")

        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-alarm-top-resource"
            
            query_params = {'regionID': region_id}
            
            if time_range:
                query_params['range'] = time_range
            
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
                timeout=30,
                verify=False
            )
            
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            result = response.json()
            
            if result.get('statusCode') == 800:
                return {
                    'success': True,
                    'data': result.get('returnObj', [])
                }
            else:
                logger.error(f"API返回错误: {result}")
                error_code = result.get('errorCode', result.get('statusCode'))
                if error_code == 'Openapi.Overview.ParamValueOutOfRange':
                    logger.warning(f"参数取值超出范围: {time_range}")
                    return {
                        'success': False,
                        'error': 'ParamValueOutOfRange',
                        'message': '参数取值超出范围'
                    }
                return {
                    'success': False,
                    'error': error_code,
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
                
        except Exception as e:
            logger.error(f"查询告警Top实例失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'Exception',
                'message': str(e)
            }

    def query_alarm_top_metric(self, region_id: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        """查询告警Top指标"""
        logger.info(f"查询告警Top指标: region_id={region_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-alarm-top-metric"
            query_params = {'regionID': region_id}
            if time_range:
                query_params['range'] = time_range
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', [])}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询告警Top指标失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_alarm_top_event(self, region_id: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        """查询告警Top事件"""
        logger.info(f"查询告警Top事件: region_id={region_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-alarm-top-event"
            query_params = {'regionID': region_id}
            if time_range:
                query_params['range'] = time_range
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', [])}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询告警Top事件失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_alarm_rules(self, region_id: str, service: str, alarm_status: Optional[int] = None,
                         status: Optional[int] = None, name: Optional[str] = None,
                         contact_group_name: Optional[str] = None, instance_name: Optional[str] = None,
                         sort_key: Optional[str] = None, sort_type: Optional[str] = None,
                         page_no: Optional[int] = None, page_size: Optional[int] = None,
                         res_group_id: Optional[str] = None) -> Dict[str, Any]:
        """查询告警规则列表"""
        logger.info(f"查询告警规则列表: region_id={region_id}, service={service}")
        try:
            url = f"https://{self.base_endpoint}/v4.1/monitor/query-alarm-rules"
            query_params = {'regionID': region_id, 'service': service}
            if alarm_status is not None: query_params['alarmStatus'] = alarm_status
            if status is not None: query_params['status'] = status
            if name: query_params['name'] = name
            if contact_group_name: query_params['contactGroupName'] = contact_group_name
            if instance_name: query_params['instanceName'] = instance_name
            if sort_key: query_params['sortKey'] = sort_key
            if sort_type: query_params['sortType'] = sort_type
            if page_no: query_params['pageNo'] = page_no
            if page_size: query_params['pageSize'] = page_size
            if res_group_id: query_params['resGroupID'] = res_group_id
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询告警规则列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def describe_alarm_rule(self, region_id: str, alarm_rule_id: str) -> Dict[str, Any]:
        """查询告警规则详情"""
        logger.info(f"查询告警规则详情: region_id={region_id}, alarm_rule_id={alarm_rule_id}")
        try:
            url = f"https://{self.base_endpoint}/v4.1/monitor/describe-alarm-rule"
            query_params = {
                'regionID': region_id,
                'alarmRuleID': alarm_rule_id
            }
            
            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body=None,
                extra_headers={}
            )
            
            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
        except Exception as e:
            logger.error(f"查询告警规则详情失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_contacts(self, name: Optional[str] = None, email: Optional[str] = None,
                      phone: Optional[str] = None, search: Optional[str] = None,
                      page_no: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询告警联系人列表"""
        logger.info(f"查询告警联系人列表: name={name}, search={search}")
        try:
            url = f"https://{self.base_endpoint}/v4.1/monitor/query-contacts"
            
            body = {}
            if name: body['name'] = name
            if email: body['email'] = email
            if phone: body['phone'] = phone
            if search: body['search'] = search
            if page_no: body['pageNo'] = page_no
            if page_size: body['pageSize'] = page_size
            
            body_json = json.dumps(body) if body else None
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body_json,
                extra_headers={'Content-Type': 'application/json'}
            )
            
            response = self.client.session.post(
                url,
                json=body if body else None,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
        except Exception as e:
            logger.error(f"查询告警联系人列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_contact_groups(self, name: Optional[str] = None, search: Optional[str] = None,
                            page_no: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询告警联系人组列表"""
        logger.info(f"查询告警联系人组列表: name={name}, search={search}")
        try:
            url = f"https://{self.base_endpoint}/v4.1/monitor/query-contact-groups"
            
            body = {}
            if name: body['name'] = name
            if search: body['search'] = search
            if page_no: body['pageNo'] = page_no
            if page_size: body['pageSize'] = page_size
            
            body_json = json.dumps(body) if body else None
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body_json,
                extra_headers={'Content-Type': 'application/json'}
            )
            
            response = self.client.session.post(
                url,
                json=body if body else None,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
        except Exception as e:
            logger.error(f"查询告警联系人组列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_custom_item_trendmetricdata(self, region_id: str, custom_item_id: str,
                                         start_time: int, end_time: int,
                                         period: Optional[int] = None,
                                         dimensions: Optional[list] = None) -> Dict[str, Any]:
        """查询自定义监控趋势数据"""
        logger.info(f"查询自定义监控趋势数据: region_id={region_id}, custom_item_id={custom_item_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-custom-item-trendmetricdata"
            
            body = {
                'regionID': region_id,
                'customItemID': custom_item_id,
                'startTime': start_time,
                'endTime': end_time
            }
            if period: body['period'] = period
            if dimensions: body['dimensions'] = dimensions
            
            body_json = json.dumps(body)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body_json,
                extra_headers={'Content-Type': 'application/json'}
            )
            
            response = self.client.session.post(
                url,
                json=body,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
        except Exception as e:
            logger.error(f"查询自定义监控趋势数据失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_custom_item_historymetricdata(self, region_id: str, custom_item_id: str,
                                           start_time: int, end_time: int,
                                           dimensions: Optional[list] = None) -> Dict[str, Any]:
        """查询自定义监控历史数据"""
        logger.info(f"查询自定义监控历史数据: region_id={region_id}, custom_item_id={custom_item_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-custom-item-historymetricdata"
            
            body = {
                'regionID': region_id,
                'customItemID': custom_item_id,
                'startTime': start_time,
                'endTime': end_time
            }
            if dimensions: body['dimensions'] = dimensions
            
            body_json = json.dumps(body)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body_json,
                extra_headers={'Content-Type': 'application/json'}
            )
            
            response = self.client.session.post(
                url,
                json=body,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
        except Exception as e:
            logger.error(f"查询自定义监控历史数据失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_custom_item_dimension_values(self, region_id: str, custom_item_id: str,
                                          dimension_name: str, filter_dims: Optional[list] = None) -> Dict[str, Any]:
        """查询自定义监控项维度值"""
        logger.info(f"查询自定义监控项维度值: region_id={region_id}, custom_item_id={custom_item_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-custom-item/dimension-values"
            
            body = {
                'regionID': region_id,
                'customItemID': custom_item_id,
                'dimensionName': dimension_name
            }
            if filter_dims: body['filter'] = filter_dims
            
            body_json = json.dumps(body)
            
            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body_json,
                extra_headers={'Content-Type': 'application/json'}
            )
            
            response = self.client.session.post(
                url,
                json=body,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {
                    'success': False,
                    'error': result.get('errorCode', result.get('statusCode')),
                    'message': result.get('msgDesc', result.get('message', '未知错误'))
                }
        except Exception as e:
            logger.error(f"查询自定义监控项维度值失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_custom_items(self, region_id: str, custom_item_id: Optional[str] = None,
                          name: Optional[str] = None, page_no: Optional[int] = None,
                          page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询自定义监控项列表"""
        logger.info(f"查询自定义监控项列表: region_id={region_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-custom-items"
            query_params = {'regionID': region_id}
            if custom_item_id: query_params['customItemID'] = custom_item_id
            if name: query_params['name'] = name
            if page_no: query_params['pageNo'] = page_no
            if page_size: query_params['pageSize'] = page_size
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询自定义监控项列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_custom_alarm_rules(self, region_id: str, status: Optional[int] = None,
                                 alarm_status: Optional[int] = None, sort: Optional[str] = None,
                                 name: Optional[str] = None, page_no: Optional[int] = None,
                                 page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询自定义监控告警规则列表"""
        logger.info(f"查询自定义监控告警规则列表: region_id={region_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-custom-alarm-rules"
            query_params = {'regionID': region_id}
            if status is not None: query_params['status'] = status
            if alarm_status is not None: query_params['alarmStatus'] = alarm_status
            if sort: query_params['sort'] = sort
            if name: query_params['name'] = name
            if page_no: query_params['pageNo'] = page_no
            if page_size: query_params['pageSize'] = page_size
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询自定义监控告警规则列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def describe_custom_alarm_rule(self, region_id: str, alarm_rule_id: str) -> Dict[str, Any]:
        """查询自定义监控告警规则详情"""
        logger.info(f"查询自定义监控告警规则详情: region_id={region_id}, alarm_rule_id={alarm_rule_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/describe-custom-alarm-rule"
            query_params = {'regionID': region_id, 'alarmRuleID': alarm_rule_id}
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询自定义监控告警规则详情失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_notice_templates(self, service: Optional[str] = None, dimension: Optional[str] = None,
                               name: Optional[str] = None, page_no: Optional[int] = None,
                               page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询通知模板列表"""
        logger.info(f"查询通知模板列表: service={service}, dimension={dimension}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-notice-templates"
            query_params = {}
            if service: query_params['service'] = service
            if dimension: query_params['dimension'] = dimension
            if name: query_params['name'] = name
            if page_no: query_params['pageNo'] = page_no
            if page_size: query_params['pageSize'] = page_size
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询通知模板列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def describe_notice_template(self, notice_template_id: str) -> Dict[str, Any]:
        """查询通知模板详情"""
        logger.info(f"查询通知模板详情: notice_template_id={notice_template_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/describe-notice-template"
            query_params = {'noticeTemplateID': notice_template_id}
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询通知模板详情失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_notice_template_variable(self, group: str, dimension: str) -> Dict[str, Any]:
        """查询通知模板变量"""
        logger.info(f"查询通知模板变量: group={group}, dimension={dimension}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-notice-template-variable"
            query_params = {'group': group, 'dimension': dimension}
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', [])}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询通知模板变量失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def describe_alarm_template(self, region_id: str, template_id: str) -> Dict[str, Any]:
        """查询告警模板详情"""
        logger.info(f"查询告警模板详情: region_id={region_id}, template_id={template_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/describe-alarm-template"
            query_params = {'regionID': region_id, 'templateID': template_id}
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询告警模板详情失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_alarm_templates(self, region_id: str, query_content: Optional[str] = None,
                             services: Optional[list] = None, template_type: Optional[str] = None,
                             page_no: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询告警模板列表"""
        logger.info(f"查询告警模板列表: region_id={region_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-alarm-templates"
            
            body = {'regionID': region_id}
            if query_content: body['queryContent'] = query_content
            if services: body['services'] = services
            if template_type: body['templateType'] = template_type
            if page_no: body['pageNo'] = page_no
            if page_size: body['pageSize'] = page_size
            
            body_json = json.dumps(body)
            
            headers = self.eop_auth.sign_request(method='POST', url=url, query_params=None, body=body_json,
                                                extra_headers={'Content-Type': 'application/json'})
            response = self.client.session.post(url, json=body, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询告警模板列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def describe_contact(self, contact_id: str) -> Dict[str, Any]:
        """查询告警联系人详情"""
        logger.info(f"查询告警联系人详情: contact_id={contact_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/describe-contact"
            query_params = {'contactID': contact_id}
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询告警联系人详情失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def describe_contact_group(self, contact_group_id: str) -> Dict[str, Any]:
        """查询告警联系人组详情"""
        logger.info(f"查询告警联系人组详情: contact_group_id={contact_group_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/describe-contact-group"
            query_params = {'contactGroupID': contact_group_id}
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询告警联系人组详情失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_alarm_blacklists(self, region_id: str, device_uuid: Optional[str] = None,
                               name: Optional[str] = None, service: Optional[str] = None,
                               dimension: Optional[str] = None, contact_group_id: Optional[str] = None,
                               contact_group_name: Optional[str] = None, create_time_from: Optional[int] = None,
                               create_time_till: Optional[int] = None, page_no: Optional[int] = None,
                               page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询告警黑名单列表"""
        logger.info(f"查询告警黑名单列表: region_id={region_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-alarm-blacklists"
            query_params = {'regionID': region_id}
            if device_uuid: query_params['deviceUUID'] = device_uuid
            if name: query_params['name'] = name
            if service: query_params['service'] = service
            if dimension: query_params['dimension'] = dimension
            if contact_group_id: query_params['contactGroupID'] = contact_group_id
            if contact_group_name: query_params['contactGroupName'] = contact_group_name
            if create_time_from: query_params['createTimeFrom'] = create_time_from
            if create_time_till: query_params['createTimeTill'] = create_time_till
            if page_no: query_params['pageNo'] = page_no
            if page_size: query_params['pageSize'] = page_size
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询告警黑名单列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_message_records(self, receiver: Optional[str] = None, record_type: Optional[int] = None,
                             method: Optional[str] = None, record_status: Optional[int] = None,
                             start_time: Optional[int] = None, end_time: Optional[int] = None,
                             page_no: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询通知记录列表"""
        logger.info(f"查询通知记录列表: receiver={receiver}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/query-message-records"
            query_params = {}
            if receiver: query_params['receiver'] = receiver
            if record_type is not None: query_params['recordType'] = record_type
            if method: query_params['method'] = method
            if record_status is not None: query_params['recordStatus'] = record_status
            if start_time: query_params['startTime'] = start_time
            if end_time: query_params['endTime'] = end_time
            if page_no: query_params['pageNo'] = page_no
            if page_size: query_params['pageSize'] = page_size
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询通知记录列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_inspection_task_overview(self, region_id: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """查询巡检任务结果总览"""
        logger.info(f"查询巡检任务结果总览: region_id={region_id}, task_id={task_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/intelligent-inspection/query-task-overview"
            body = {'regionID': region_id}
            if task_id: body['taskID'] = task_id
            body_json = json.dumps(body)
            
            headers = self.eop_auth.sign_request(method='POST', url=url, query_params=None, body=body_json,
                                                extra_headers={'Content-Type': 'application/json'})
            response = self.client.session.post(url, json=body, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询巡检任务结果总览失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_inspection_task_detail(self, task_id: str, inspection_type: int,
                                     page_no: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询巡检任务结果详情"""
        logger.info(f"查询巡检任务结果详情: task_id={task_id}, inspection_type={inspection_type}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/intelligent-inspection/query-task-detail"
            body = {'taskID': task_id, 'inspectionType': inspection_type}
            if page_no: body['pageNo'] = page_no
            if page_size: body['pageSize'] = page_size
            body_json = json.dumps(body)
            
            headers = self.eop_auth.sign_request(method='POST', url=url, query_params=None, body=body_json,
                                                extra_headers={'Content-Type': 'application/json'})
            response = self.client.session.post(url, json=body, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询巡检任务结果详情失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_inspection_items(self, inspection_type: Optional[int] = None, search: Optional[str] = None) -> Dict[str, Any]:
        """查询巡检项"""
        logger.info(f"查询巡检项: inspection_type={inspection_type}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/intelligent-inspection/query-inspection-item"
            query_params = {}
            if inspection_type is not None: query_params['inspectionType'] = inspection_type
            if search: query_params['search'] = search
            
            headers = self.eop_auth.sign_request(method='GET', url=url, query_params=query_params, body=None, extra_headers={})
            response = self.client.session.get(url, params=query_params, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询巡检项失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_inspection_history_list(self, region_id: str, start_time: Optional[int] = None,
                                      end_time: Optional[int] = None, page_no: Optional[int] = None,
                                      page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询巡检历史列表"""
        logger.info(f"查询巡检历史列表: region_id={region_id}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/intelligent-inspection/query-history-list"
            body = {'regionID': region_id}
            if start_time: body['startTime'] = start_time
            if end_time: body['endTime'] = end_time
            if page_no: body['pageNo'] = page_no
            if page_size: body['pageSize'] = page_size
            body_json = json.dumps(body)
            
            headers = self.eop_auth.sign_request(method='POST', url=url, query_params=None, body=body_json,
                                                extra_headers={'Content-Type': 'application/json'})
            response = self.client.session.post(url, json=body, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询巡检历史列表失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}

    def query_inspection_history_detail(self, task_id: str, inspection_item: int,
                                        page_no: Optional[int] = None, page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询巡检历史详情"""
        logger.info(f"查询巡检历史详情: task_id={task_id}, inspection_item={inspection_item}")
        try:
            url = f"https://{self.base_endpoint}/v4/monitor/intelligent-inspection/query-history-detail"
            body = {'taskID': task_id, 'inspectionItem': inspection_item}
            if page_no: body['pageNo'] = page_no
            if page_size: body['pageSize'] = page_size
            body_json = json.dumps(body)
            
            headers = self.eop_auth.sign_request(method='POST', url=url, query_params=None, body=body_json,
                                                extra_headers={'Content-Type': 'application/json'})
            response = self.client.session.post(url, json=body, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}', 'message': response.text}
            
            result = response.json()
            if result.get('statusCode') == 800:
                return {'success': True, 'data': result.get('returnObj', {})}
            else:
                return {'success': False, 'error': result.get('errorCode', result.get('statusCode')), 
                       'message': result.get('msgDesc', result.get('message', '未知错误'))}
        except Exception as e:
            logger.error(f"查询巡检历史详情失败: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'Exception', 'message': str(e)}
