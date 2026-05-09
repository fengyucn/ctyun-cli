"""边缘安全加速平台(Aone)客户端"""

from typing import Dict, Any, Optional, List
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class AoneClient:
    """天翼云边缘安全加速平台(Aone)客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化边缘安全加速平台客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'aone'
        self.base_endpoint = 'accessone-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def _request(self, method: str, path: str,
                 query_params: Optional[Dict] = None,
                 body_data: Optional[Dict] = None,
                 extra_headers: Optional[Dict] = None) -> Dict[str, Any]:
        """通用请求方法"""
        url = f"https://{self.base_endpoint}{path}"
        body = json.dumps(body_data) if body_data else ('' if method == 'POST' else None)

        headers = self.eop_auth.sign_request(
            method=method,
            url=url,
            query_params=query_params,
            body=body,
            extra_headers=extra_headers or {}
        )

        logger.debug(f"请求URL: {url}")
        logger.debug(f"请求体: {body}")
        logger.debug(f"查询参数: {query_params}")
        logger.debug(f"请求头: {headers}")

        try:
            if method == 'GET':
                response = self.client.session.get(
                    url, params=query_params, headers=headers, timeout=30, verify=False
                )
            else:
                response = self.client.session.post(
                    url, data=body, headers=headers, timeout=30, verify=False
                )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                return {
                    'statusCode': response.status_code,
                    'error': f'HTTP_{response.status_code}',
                    'message': response.text
                }

            return response.json()

        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            logger.debug("", exc_info=True)
            return {
                'statusCode': 500,
                'error': 'Exception',
                'message': str(e)
            }

    # ==================== 域名管理 ====================

    def query_domain_list(self, access_mode: Optional[int] = None,
                          domain: Optional[str] = None,
                          instance: Optional[List[str]] = None,
                          product_code: Optional[str] = None,
                          status: Optional[int] = None,
                          area_scope: Optional[int] = None,
                          page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """查询域名列表"""
        logger.info(f"查询域名列表: domain={domain}, page={page}")
        params = {'page': page, 'page_size': page_size}
        if access_mode is not None: params['access_mode'] = access_mode
        if domain: params['domain'] = domain
        if instance: params['instance'] = ','.join(instance) if isinstance(instance, list) else instance
        if product_code: params['product_code'] = product_code
        if status is not None: params['status'] = status
        if area_scope is not None: params['area_scope'] = area_scope
        return self._request('GET', '/v1/domain/query-domain-list', query_params=params)

    def query_domain_config(self, product_code: str, access_mode: Optional[int] = None,
                            domain: Optional[str] = None,
                            instance: Optional[str] = None) -> Dict[str, Any]:
        """查询域名配置信息"""
        logger.info(f"查询域名配置信息: domain={domain}, product_code={product_code}")
        body = {'product_code': product_code}
        if access_mode is not None: body['access_mode'] = access_mode
        if domain: body['domain'] = domain
        if instance: body['instance'] = instance
        return self._request('POST', '/v1/ipa/domain/query-domain-detail', body_data=body)

    def query_domain_basic_config(self, domain: str, product_code: str) -> Dict[str, Any]:
        """域名基础及加速配置查询"""
        logger.info(f"域名基础及加速配置查询: domain={domain}, product_code={product_code}")
        return self._request('POST', '/ctapi/v1/accessone/domain/config',
                             body_data={'domain': domain, 'product_code': product_code})

    def query_domain_status(self, domains: List[str], product_code: str,
                            page_index: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """域名状态查询"""
        logger.info(f"域名状态查询: domains={domains}, product_code={product_code}")
        return self._request('POST', '/ctapi/v1/accessone/domain/status/query',
                             body_data={
                                 'domains': domains,
                                 'productCode': product_code,
                                 'pageIndex': str(page_index),
                                 'pageSize': str(page_size)
                             })

    def query_domain_protocol(self, product_code: str, access_mode: Optional[int] = None,
                              domain: Optional[str] = None,
                              instance: Optional[str] = None) -> Dict[str, Any]:
        """查询域名协议类型"""
        logger.info(f"查询域名协议类型: domain={domain}, product_code={product_code}")
        body = {'product_code': product_code}
        if access_mode is not None: body['access_mode'] = access_mode
        if domain: body['domain'] = domain
        if instance: body['instance'] = instance
        return self._request('POST', '/v1/ipa/domain/query-domain-pro', body_data=body)

    def query_domain_list_basic(self, domain: Optional[str] = None,
                                product_code: Optional[str] = None,
                                status: Optional[int] = None,
                                area_scope: Optional[int] = None,
                                page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """查询域名列表基础信息"""
        logger.info(f"查询域名列表基础信息: domain={domain}, page={page}")
        params = {'page': page, 'page_size': page_size}
        if domain: params['domain'] = domain
        if product_code: params['product_code'] = product_code
        if status is not None: params['status'] = status
        if area_scope is not None: params['area_scope'] = area_scope
        return self._request('GET', '/ctapi/v2/domain/query', query_params=params)

    # ==================== 服务管理 ====================

    def query_service_detail(self, product_code: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询开通服务基本信息"""
        logger.info(f"查询开通服务基本信息: product_code={product_code}")
        body = {}
        if product_code: body['product_code'] = product_code
        return self._request('POST', '/v1/usage-management/query-service-detail', body_data=body)

    def query_resource_packages(self) -> Dict[str, Any]:
        """查询安全与加速资源包列表"""
        logger.info("查询安全与加速资源包列表")
        return self._request('POST', '/ctapi/v1/accessone/purchase/queryResourcePackagesDBT', body_data={})

    # ==================== 证书管理 ====================

    def query_cert_list(self, page: int = 1, per_page: int = 1000,
                        usage_mode: Optional[int] = None) -> Dict[str, Any]:
        """查询用户名下证书列表"""
        logger.info(f"查询用户名下证书列表: page={page}")
        params = {'page': page, 'per_page': per_page}
        if usage_mode is not None: params['usage_mode'] = usage_mode
        return self._request('GET', '/ctapi/v1/accessone/cert/list', query_params=params)

    def query_cert_detail(self, name: Optional[str] = None,
                          id: Optional[int] = None,
                          usage_mode: Optional[int] = None) -> Dict[str, Any]:
        """查询证书详情"""
        logger.info(f"查询证书详情: name={name}, id={id}")
        params = {}
        if name: params['name'] = name
        if id is not None: params['id'] = id
        if usage_mode is not None: params['usage_mode'] = usage_mode
        return self._request('GET', '/ctapi/v1/accessone/cert/query', query_params=params)

    def query_cert_domains(self, name: str) -> Dict[str, Any]:
        """查询证书关联域名列表"""
        logger.info(f"查询证书关联域名列表: name={name}")
        return self._request('GET', '/ctapi/v1/accessone/cert/list_domain_by_cert',
                             query_params={'name': name})

    # ==================== 缓存管理 ====================

    def query_refresh_tasks(self, type: int = 0, url: Optional[str] = None,
                            start_time: Optional[int] = None, end_time: Optional[int] = None,
                            submit_id: Optional[str] = None, task_id: Optional[str] = None,
                            task_type: Optional[int] = None,
                            page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """查询刷新任务"""
        logger.info(f"查询刷新任务: type={type}, page={page}")
        params = {'page': page, 'page_size': page_size}
        params['type'] = type
        if url: params['url'] = url
        if start_time is not None: params['start_time'] = start_time
        if end_time is not None: params['end_time'] = end_time
        if submit_id: params['submit_id'] = submit_id
        if task_id: params['task_id'] = task_id
        if task_type is not None: params['task_type'] = task_type
        return self._request('GET', '/ctapi/v1/accessone/refresh_task/query', query_params=params)

    def query_refresh_task_quota(self) -> Dict[str, Any]:
        """查询刷新任务额度"""
        logger.info("查询刷新任务额度")
        return self._request('GET', '/ctapi/v1/accessone/refresh_task_quota/query')

    def query_preload_tasks(self, type: int = 0, url: Optional[str] = None,
                            start_time: Optional[int] = None, end_time: Optional[int] = None,
                            submit_id: Optional[str] = None, task_id: Optional[str] = None,
                            page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """查询预取任务"""
        logger.info(f"查询预取任务: type={type}, page={page}")
        params = {'page': page, 'page_size': page_size}
        params['type'] = type
        if url: params['url'] = url
        if start_time is not None: params['start_time'] = start_time
        if end_time is not None: params['end_time'] = end_time
        if submit_id: params['submit_id'] = submit_id
        if task_id: params['task_id'] = task_id
        return self._request('GET', '/ctapi/v1/accessone/preload_task/Query', query_params=params)

    def query_preload_task_quota(self) -> Dict[str, Any]:
        """查询预取任务额度"""
        logger.info("查询预取任务额度")
        return self._request('GET', '/ctapi/v1/accessone/preload_task_quota/query')

    # ==================== 数据统计 ====================

    def query_bandwidth_data(self, start_time: int, end_time: int,
                             interval: Optional[str] = None,
                             product_type: Optional[List[str]] = None,
                             access_mode: Optional[int] = None,
                             domain: Optional[List[str]] = None,
                             instance: Optional[List[str]] = None,
                             province: Optional[List[int]] = None,
                             isp: Optional[List[str]] = None,
                             network_layer_protocol: Optional[str] = None,
                             abroad: Optional[int] = None,
                             group_by: Optional[List[str]] = None,
                             continent_code: Optional[List[int]] = None,
                             continent_region_code: Optional[List[int]] = None) -> Dict[str, Any]:
        """查询带宽数据"""
        logger.info(f"查询带宽数据: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if access_mode is not None: body['access_mode'] = access_mode
        if domain: body['domain'] = domain
        if instance: body['instance'] = instance
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if abroad is not None: body['abroad'] = abroad
        if group_by: body['group_by'] = group_by
        if continent_code: body['continent_code'] = continent_code
        if continent_region_code: body['continent_region_code'] = continent_region_code
        return self._request('POST', '/v1/statistics/query-bandwidth-data', body_data=body)

    def query_flow_data(self, start_time: int, end_time: int,
                        interval: Optional[str] = None,
                        product_type: Optional[List[str]] = None,
                        access_mode: Optional[int] = None,
                        domain: Optional[List[str]] = None,
                        instance: Optional[List[str]] = None,
                        province: Optional[List[int]] = None,
                        isp: Optional[List[str]] = None,
                        network_layer_protocol: Optional[str] = None,
                        abroad: Optional[int] = None,
                        group_by: Optional[List[str]] = None,
                        continent_code: Optional[List[int]] = None,
                        continent_region_code: Optional[List[int]] = None) -> Dict[str, Any]:
        """查询流量数据"""
        logger.info(f"查询流量数据: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if access_mode is not None: body['access_mode'] = access_mode
        if domain: body['domain'] = domain
        if instance: body['instance'] = instance
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if abroad is not None: body['abroad'] = abroad
        if group_by: body['group_by'] = group_by
        if continent_code: body['continent_code'] = continent_code
        if continent_region_code: body['continent_region_code'] = continent_region_code
        return self._request('POST', '/v1/statistics/query-flow-data', body_data=body)

    def query_qps_data(self, start_time: int, end_time: int,
                       interval: Optional[str] = None,
                       product_type: Optional[List[str]] = None,
                       domain: Optional[List[str]] = None,
                       province: Optional[List[int]] = None,
                       isp: Optional[List[str]] = None,
                       network_layer_protocol: Optional[str] = None,
                       application_layer_protocol: Optional[str] = None,
                       group_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询QPS/回源QPS数据"""
        logger.info(f"查询QPS数据: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if application_layer_protocol: body['application_layer_protocol'] = application_layer_protocol
        if group_by: body['group_by'] = group_by
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_qps_data', body_data=body)

    def query_request_num_data(self, start_time: int, end_time: int,
                               interval: Optional[str] = None,
                               product_type: Optional[List[str]] = None,
                               domain: Optional[List[str]] = None,
                               province: Optional[List[int]] = None,
                               isp: Optional[List[str]] = None,
                               network_layer_protocol: Optional[str] = None,
                               application_layer_protocol: Optional[str] = None,
                               group_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询请求数/回源请求数/请求命中率数据"""
        logger.info(f"查询请求数数据: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if application_layer_protocol: body['application_layer_protocol'] = application_layer_protocol
        if group_by: body['group_by'] = group_by
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_request_num_data', body_data=body)

    def query_miss_bandwidth_data(self, start_time: int, end_time: int,
                                  interval: Optional[str] = None,
                                  product_type: Optional[List[str]] = None,
                                  domain: Optional[List[str]] = None,
                                  province: Optional[List[int]] = None,
                                  isp: Optional[List[str]] = None,
                                  network_layer_protocol: Optional[str] = None,
                                  application_layer_protocol: Optional[str] = None,
                                  group_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询回源带宽数据"""
        logger.info(f"查询回源带宽数据: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if application_layer_protocol: body['application_layer_protocol'] = application_layer_protocol
        if group_by: body['group_by'] = group_by
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_miss_bandwidth_data', body_data=body)

    def query_pv_data(self, start_time: int, end_time: int,
                      domain: Optional[List[str]] = None,
                      http_protocol: Optional[int] = None) -> Dict[str, Any]:
        """查询PV数据"""
        logger.info(f"查询PV数据: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if domain: body['domain'] = domain
        if http_protocol is not None: body['httpProtocol'] = http_protocol
        return self._request('POST', '/ctapi/v1/pv', body_data=body)

    def query_uv_data(self, start_time: int, end_time: int,
                      domain: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询UV数据"""
        logger.info(f"查询UV数据: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if domain: body['domain'] = domain
        return self._request('POST', '/ctapi/v1/uv', body_data=body)

    def query_http_status_code_data(self, start_time: int, end_time: int,
                                    interval: Optional[str] = None,
                                    product_type: Optional[List[str]] = None,
                                    domain: Optional[List[str]] = None,
                                    province: Optional[List[int]] = None,
                                    isp: Optional[List[str]] = None,
                                    network_layer_protocol: Optional[str] = None,
                                    application_layer_protocol: Optional[str] = None,
                                    group_by: Optional[List[str]] = None,
                                    busi_type: Optional[List[int]] = None,
                                    abroad: Optional[int] = None,
                                    continent_code: Optional[List[int]] = None,
                                    continent_region_code: Optional[List[int]] = None) -> Dict[str, Any]:
        """查询状态码请求数/请求状态码占比"""
        logger.info(f"查询状态码请求数: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if application_layer_protocol: body['application_layer_protocol'] = application_layer_protocol
        if group_by: body['group_by'] = group_by
        if busi_type: body['busi_type'] = busi_type
        if abroad is not None: body['abroad'] = abroad
        if continent_code: body['continent_code'] = continent_code
        if continent_region_code: body['continent_region_code'] = continent_region_code
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_http_status_code_data', body_data=body)

    def query_miss_http_status_code_data(self, start_time: int, end_time: int,
                                         interval: Optional[str] = None,
                                         product_type: Optional[List[str]] = None,
                                         domain: Optional[List[str]] = None,
                                         province: Optional[List[int]] = None,
                                         isp: Optional[List[str]] = None,
                                         network_layer_protocol: Optional[str] = None,
                                         application_layer_protocol: Optional[str] = None,
                                         group_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询回源状态码请求数/回源状态码请求数占比"""
        logger.info(f"查询回源状态码请求数: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if application_layer_protocol: body['application_layer_protocol'] = application_layer_protocol
        if group_by: body['group_by'] = group_by
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_miss_http_status_code_data', body_data=body)

    def query_miss_request_num_data(self, start_time: int, end_time: int,
                                    interval: Optional[str] = None,
                                    product_type: Optional[List[str]] = None,
                                    domain: Optional[List[str]] = None,
                                    province: Optional[List[int]] = None,
                                    isp: Optional[List[str]] = None,
                                    network_layer_protocol: Optional[str] = None,
                                    application_layer_protocol: Optional[str] = None,
                                    group_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询回源请求数数据"""
        logger.info(f"查询回源请求数: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if application_layer_protocol: body['application_layer_protocol'] = application_layer_protocol
        if group_by: body['group_by'] = group_by
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_miss_request_num_data', body_data=body)

    def query_response_time_data(self, start_time: int, end_time: int,
                                 interval: Optional[str] = None,
                                 domain: Optional[List[str]] = None,
                                 province: Optional[List[int]] = None,
                                 isp: Optional[List[str]] = None,
                                 network_layer_protocol: Optional[str] = None,
                                 application_layer_protocol: Optional[str] = None) -> Dict[str, Any]:
        """查询平均响应时间"""
        logger.info(f"查询平均响应时间: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if application_layer_protocol: body['application_layer_protocol'] = application_layer_protocol
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_response_time_data', body_data=body)

    def query_request_success_rate_data(self, start_time: int, end_time: int,
                                        interval: Optional[str] = None,
                                        product_type: Optional[List[str]] = None,
                                        domain: Optional[List[str]] = None,
                                        province: Optional[List[int]] = None,
                                        isp: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询请求成功率数据"""
        logger.info(f"查询请求成功率: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_request_success_rate_data_by_domain',
                             body_data=body)

    def query_request_failure_rate_data(self, start_time: int, end_time: int,
                                        interval: Optional[str] = None,
                                        product_type: Optional[List[str]] = None,
                                        domain: Optional[List[str]] = None,
                                        province: Optional[List[int]] = None,
                                        isp: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询请求失败率数据"""
        logger.info(f"查询请求失败率: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_request_failure_rate_data_by_domain',
                             body_data=body)

    def query_miss_request_success_rate_data(self, start_time: int, end_time: int,
                                             interval: Optional[str] = None,
                                             product_type: Optional[List[str]] = None,
                                             domain: Optional[List[str]] = None,
                                             province: Optional[List[int]] = None,
                                             isp: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询回源请求成功率数据"""
        logger.info(f"查询回源请求成功率: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_miss_request_success_rate_data_by_domain',
                             body_data=body)

    def query_miss_request_failure_rate_data(self, start_time: int, end_time: int,
                                             interval: Optional[str] = None,
                                             product_type: Optional[List[str]] = None,
                                             domain: Optional[List[str]] = None,
                                             province: Optional[List[int]] = None,
                                             isp: Optional[List[str]] = None,
                                             network_layer_protocol: Optional[str] = None,
                                             application_layer_protocol: Optional[str] = None,
                                             group_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """查询回源请求失败率数据"""
        logger.info(f"查询回源请求失败率: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if application_layer_protocol: body['application_layer_protocol'] = application_layer_protocol
        if group_by: body['group_by'] = group_by
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_miss_request_failure_rate_data_by_domain',
                             body_data=body)

    def query_user_connection_num(self, start_time: int, end_time: int,
                                  interval: Optional[str] = None,
                                  product_type: Optional[List[str]] = None,
                                  access_mode: Optional[int] = None,
                                  domain: Optional[List[str]] = None,
                                  instance: Optional[List[str]] = None,
                                  province: Optional[List[int]] = None,
                                  isp: Optional[List[str]] = None,
                                  network_layer_protocol: Optional[str] = None,
                                  abroad: Optional[int] = None,
                                  group_by: Optional[List[str]] = None,
                                  continent_code: Optional[List[int]] = None,
                                  continent_region_code: Optional[List[int]] = None) -> Dict[str, Any]:
        """查询用户连接数"""
        logger.info(f"查询用户连接数: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if product_type: body['product_type'] = product_type
        if access_mode is not None: body['access_mode'] = access_mode
        if domain: body['domain'] = domain
        if instance: body['instance'] = instance
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if abroad is not None: body['abroad'] = abroad
        if group_by: body['group_by'] = group_by
        if continent_code: body['continent_code'] = continent_code
        if continent_region_code: body['continent_region_code'] = continent_region_code
        return self._request('POST', '/v1/statistics/query-request-num-data', body_data=body)

    def query_summary_data(self, start_time: int, end_time: int,
                           interval: Optional[str] = None,
                           busi_type: Optional[List[int]] = None,
                           domain: Optional[str] = None,
                           province: Optional[List[int]] = None,
                           isp: Optional[List[str]] = None,
                           network_layer_protocol: Optional[str] = None,
                           application_layer_protocol: Optional[str] = None,
                           abroad: Optional[int] = None,
                           group_by: Optional[str] = None) -> Dict[str, Any]:
        """查询整体统计数据"""
        logger.info(f"查询整体统计数据: start_time={start_time}, end_time={end_time}")
        body = {'start_time': start_time, 'end_time': end_time}
        if interval: body['interval'] = interval
        if busi_type: body['busi_type'] = busi_type
        if domain: body['domain'] = domain
        if province: body['province'] = province
        if isp: body['isp'] = isp
        if network_layer_protocol: body['network_layer_protocol'] = network_layer_protocol
        if application_layer_protocol: body['application_layer_protocol'] = application_layer_protocol
        if abroad is not None: body['abroad'] = abroad
        if group_by: body['group_by'] = group_by
        return self._request('POST', '/ctapi/v2/statisticsanalysis/query_summary_data', body_data=body)

    # ==================== 安全防护 ====================

    def query_cc_attack_report(self, product_code: str,
                               start_time: str, end_time: str,
                               domain: Optional[str] = None) -> Dict[str, Any]:
        """查询CC攻击报表"""
        logger.info(f"查询CC攻击报表: domain={domain}, start={start_time}, end={end_time}")
        body = {'productCode': product_code, 'startTime': start_time, 'endTime': end_time}
        if domain: body['domain'] = domain
        return self._request('POST', '/ctapi/soc-waf/api/ccAttack/query', body_data=body)

    def query_cc_attack_events(self, product_code: str,
                               start_time: str, end_time: str,
                               domain: Optional[str] = None,
                               page: int = 1, size: int = 50) -> Dict[str, Any]:
        """查询CC攻击事件"""
        logger.info(f"查询CC攻击事件: domain={domain}, start={start_time}, end={end_time}")
        body = {
            'productCode': product_code,
            'startTime': start_time,
            'endTime': end_time,
            'size': size,
            'page': page
        }
        if domain: body['domain'] = domain
        return self._request('POST', '/ctapi/v1/accessone/ccAttack/getCcAttackList', body_data=body)

    def query_cc_attack_region(self, domain_list: List[str], product_code: str,
                               start_time: str, end_time: str) -> Dict[str, Any]:
        """CC攻击报表攻击来源区域分布查询"""
        logger.info(f"CC攻击来源区域分布: domains={domain_list}")
        return self._request('POST', '/ctapi/api-common/api/ccAttack/getCcAttackAddr',
                             body_data={
                                 'domainList': domain_list,
                                 'productCode': product_code,
                                 'startTime': start_time,
                                 'endTime': end_time
                             })

    def query_ddos_attack_trend(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """DDoS攻击趋势查询"""
        logger.info(f"DDoS攻击趋势查询: start={start_time}, end={end_time}")
        return self._request('POST', '/ctapi/api-ddos/api/ddosAttack/getAttackTrend',
                             body_data={'startTime': start_time, 'endTime': end_time})

    def query_edge_attack_trend(self, domain: str, product_code: str,
                                start_time: str, end_time: str) -> Dict[str, Any]:
        """查询边缘接入攻击趋势图数据"""
        logger.info(f"边缘接入攻击趋势: domain={domain}, start={start_time}, end={end_time}")
        return self._request('POST', '/api/api-ddos/api/edge/getAttackTrend',
                             body_data={
                                 'domain': domain,
                                 'productCode': product_code,
                                 'startTime': start_time,
                                 'endTime': end_time
                             })

    def query_waf_config(self, domain: str, product_code: str) -> Dict[str, Any]:
        """查询Web应用防火墙基础配置信息"""
        logger.info(f"查询WAF配置: domain={domain}")
        return self._request('POST', '/ctapi/v1/scdn/domain/wafConfigQuery',
                             body_data={'domain': domain, 'product_code': product_code})

    def query_rule_engine_config(self, domain: str, product_code: str,
                                 rule_id: Optional[str] = None,
                                 page_index: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """查询防护规则引擎的配置信息"""
        logger.info(f"查询规则引擎配置: domain={domain}")
        body = {'domain': domain, 'productCode': product_code,
                'pageIndex': page_index, 'pageSize': page_size}
        if rule_id: body['ruleId'] = rule_id
        return self._request('POST', '/ctapi/v1/domainRule/get', body_data=body)

    def query_rule_engine_switch(self, domain: str, product_code: str) -> Dict[str, Any]:
        """查询域名的防护规则引擎总开关信息"""
        logger.info(f"查询规则引擎总开关: domain={domain}")
        return self._request('POST', '/ctapi/v1/domainRule/getDomainRuleAct',
                             body_data={'domain': domain, 'productCode': product_code})

    def query_access_control_switch(self, domain: str, product_code: str) -> Dict[str, Any]:
        """查询访问控制限流总开关"""
        logger.info(f"查询访问控制限流开关: domain={domain}")
        return self._request('POST', '/ctapi/v1/scdn/domain/queryAccessControlAct',
                             body_data={'domain': domain, 'product_code': product_code})

    def query_tamper_protect(self, domain: str, product_code: str,
                             page_index: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """网页防篡改查询接口"""
        logger.info(f"网页防篡改查询: domain={domain}")
        return self._request('POST', '/ctapi/v1/accessone/tamperProtect/query',
                             body_data={
                                 'domain': domain,
                                 'productCode': product_code,
                                 'pageIndex': page_index,
                                 'pageSize': page_size
                             })

    def query_ipv6_no_sup_links(self, request_id: int) -> Dict[str, Any]:
        """查询IPv6检测不支持链接详情"""
        logger.info(f"查询IPv6不支持链接: requestId={request_id}")
        return self._request('POST', '/ctapi/v1/ipv6/checkResult/getNoSupLink',
                             body_data={'requestId': request_id})

    # ==================== 辅助工具 ====================

    def query_ip_detail(self, ipv4: Optional[str] = None,
                        ipv6: Optional[str] = None) -> Dict[str, Any]:
        """查询IP地址归属详情"""
        logger.info(f"查询IP归属: ipv4={ipv4}, ipv6={ipv6}")
        params = {}
        if ipv4: params['ipv4'] = ipv4
        if ipv6: params['ipv6'] = ipv6
        return self._request('GET', '/v1/auxiliary-tools/query-ip-detail', query_params=params)

    def query_backorigin_ip(self, config_name: str) -> Dict[str, Any]:
        """查询回源IP"""
        logger.info(f"查询回源IP: config_name={config_name}")
        return self._request('GET', '/ctapi/v1/query_backorigin_ip',
                             query_params={'config_name': config_name})
