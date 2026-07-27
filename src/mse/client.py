"""微服务引擎(MSE)客户端"""

from typing import Dict, Any, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class MSEClient:
    """天翼云微服务引擎(MSE)客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.base_endpoint = 'mse-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
        self.timeout = 30

    def _get(self, path: str, region_id: str,
             query_params: Optional[Dict[str, Any]] = None,
             desc: str = 'MSE查询') -> Dict[str, Any]:
        """通用 GET 请求（regionId 通过 header 传递）"""
        url = f'https://{self.base_endpoint}{path}'
        qp = {k: v for k, v in (query_params or {}).items() if v is not None}
        try:
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=qp, body='',
                extra_headers={'regionId': region_id})
            logger.debug(f"GET {url} | 参数: {qp}")
            response = self.client.session.get(url, params=qp, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return {'statusCode': response.status_code,
                        'message': f'HTTP {response.status_code}: {response.text}',
                        'returnObj': None}
            return response.json()
        except Exception as e:
            logger.error(f"{desc}失败: {e}")
            return {'statusCode': 500, 'message': str(e), 'returnObj': None}

    def _post(self, path: str, body: Dict[str, Any], desc: str,
              region_id: Optional[str] = None) -> Dict[str, Any]:
        """通用 POST 请求（regionId 通过 header 传递）"""
        url = f'https://{self.base_endpoint}{path}'
        bd = {k: v for k, v in body.items() if v is not None}
        body_str = json.dumps(bd)
        extra_headers = {}
        if region_id:
            extra_headers['regionId'] = region_id
        try:
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={}, body=body_str,
                extra_headers=extra_headers)
            logger.debug(f"POST {url} | body: {bd}")
            response = self.client.session.post(url, json=bd, headers=headers, timeout=self.timeout)
            if response.status_code != 200:
                return {'statusCode': response.status_code,
                        'message': f'HTTP {response.status_code}: {response.text}',
                        'returnObj': None}
            return response.json()
        except Exception as e:
            logger.error(f"{desc}失败: {e}")
            return {'statusCode': 500, 'message': str(e), 'returnObj': None}

    # ==================== 询价 API（1个） ====================

    def query_create_price(self, auto_pay: str, engine_type: str,
                           cycle_type: str, cycle_cnt: str,
                           auto_renew_cycle_type: str, auto_renew_cycle_count: str,
                           instance_num: int, cpu_num: int,
                           region_id: Optional[str] = None,
                           auto_renew_status: Optional[str] = None) -> Dict[str, Any]:
        """订购询价 - POST /rcc/v1/order/queryPrice"""
        body = {
            'autoPay': auto_pay,
            'engineType': engine_type,
            'cycleType': cycle_type,
            'cycleCnt': cycle_cnt,
            'autoRenewCycleType': auto_renew_cycle_type,
            'autoRenewCycleCount': auto_renew_cycle_count,
            'instanceNum': instance_num,
            'cpuNum': cpu_num,
        }
        if auto_renew_status:
            body['autoRenewStatus'] = auto_renew_status
        return self._post('/rcc/v1/order/queryPrice', body, 'MSE订购询价', region_id)

    # ==================== P0 实例管理（4个） ====================

    def list_instances(self, region_id: str,
                       instance_id: Optional[str] = None,
                       inst_name: Optional[str] = None,
                       engine_type: Optional[str] = None,
                       status: Optional[int] = None,
                       page_num: Optional[int] = None,
                       page_size: Optional[int] = None) -> Dict[str, Any]:
        """获取实例列表 - GET /rcc/v1/cluster/list"""
        return self._get('/rcc/v1/cluster/list', region_id, {
            'instanceId': instance_id, 'instName': inst_name,
            'engineType': engine_type, 'status': status,
            'pageNum': page_num, 'pageSize': page_size,
        }, '获取实例列表')

    def get_instance_detail(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """获取实例详情 - GET /rcc/v1/cluster/detail"""
        return self._get('/rcc/v1/cluster/detail', region_id,
                         {'instanceId': instance_id}, '获取实例详情')

    def get_cluster_node_status(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """获取实例节点状态 - GET /rcc/v1/cluster/getClusterNodeStatus"""
        return self._get('/rcc/v1/cluster/getClusterNodeStatus', region_id,
                         {'instanceId': instance_id}, '获取实例节点状态')

    def get_cluster_metrics(self, region_id: str, spu_inst_id: str,
                            region_code: str, start_time: int, end_time: int,
                            type_: str) -> Dict[str, Any]:
        """获取集群监控指标数据 - POST /rcc/v1/monitor/getMetrics"""
        return self._post('/rcc/v1/monitor/getMetrics', {
            'spuInstId': spu_inst_id, 'regionCode': region_code,
            'startTime': start_time, 'endTime': end_time, 'type': type_,
        }, '获取集群监控指标数据', region_id)

    # ==================== P1 Nacos 服务管理（9个） ====================

    def list_nacos_services(self, region_id: str, instance_id: str,
                            namespace_id: Optional[str] = None,
                            service_name: Optional[str] = None,
                            group_name: Optional[str] = None,
                            has_ip_count: Optional[bool] = None,
                            with_instances: Optional[bool] = None,
                            page_num: Optional[int] = None,
                            page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos服务列表 - GET /rcc/v1/nacos/service/list"""
        return self._get('/rcc/v1/nacos/service/list', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'serviceNameParam': service_name, 'groupNameParam': group_name,
            'hasIpCount': has_ip_count, 'withInstances': with_instances,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询Nacos服务列表')

    def get_nacos_service_detail(self, region_id: str, instance_id: str,
                                 service_name: str,
                                 namespace_id: Optional[str] = None,
                                 group_name: Optional[str] = None) -> Dict[str, Any]:
        """查询Nacos服务详情 - GET /rcc/v1/nacos/service/detail"""
        return self._get('/rcc/v1/nacos/service/detail', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'serviceName': service_name, 'groupName': group_name,
        }, '查询Nacos服务详情')

    def get_nacos_service_and_group(self, region_id: str, instance_id: str,
                                    namespace_id: Optional[str] = None) -> Dict[str, Any]:
        """查询Nacos服务和分组 - GET /rcc/v1/nacos/service/getServiceAndGroup"""
        return self._get('/rcc/v1/nacos/service/getServiceAndGroup', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
        }, '查询Nacos服务和分组')

    def get_nacos_instance_list(self, region_id: str, instance_id: str,
                                service_name: str, group_name: str,
                                namespace_id: Optional[str] = None,
                                client_ip: Optional[str] = None,
                                clusters: Optional[str] = None,
                                healthy_only: Optional[bool] = None,
                                app: Optional[str] = None) -> Dict[str, Any]:
        """查询Nacos服务实例列表 - GET /rcc/v1/nacos/service/getInstanceList"""
        return self._get('/rcc/v1/nacos/service/getInstanceList', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'serviceName': service_name, 'groupName': group_name,
            'clientIP': client_ip, 'clusters': clusters,
            'healthyOnly': healthy_only, 'app': app,
        }, '查询Nacos服务实例列表')

    def get_nacos_instance_detail(self, region_id: str, instance_id: str,
                                  service_name: str, group_name: str,
                                  ip: str, port: int,
                                  namespace_id: Optional[str] = None,
                                  cluster_name: Optional[str] = None) -> Dict[str, Any]:
        """查询Nacos服务实例详情 - GET /rcc/v1/nacos/service/getInstanceDetail"""
        return self._get('/rcc/v1/nacos/service/getInstanceDetail', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'serviceName': service_name, 'groupName': group_name,
            'ip': ip, 'port': port, 'clusterName': cluster_name,
        }, '查询Nacos服务实例详情')

    def get_nacos_clusters(self, region_id: str, instance_id: str,
                           service_name: str, group_name: str,
                           namespace_id: Optional[str] = None) -> Dict[str, Any]:
        """查询Nacos服务集群 - GET /rcc/v1/nacos/service/getClusters"""
        return self._get('/rcc/v1/nacos/service/getClusters', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'serviceName': service_name, 'groupName': group_name,
        }, '查询Nacos服务集群')

    def get_nacos_cluster_instances(self, region_id: str, instance_id: str,
                                    service_name: str, group_name: str,
                                    namespace_id: Optional[str] = None,
                                    cluster_name: Optional[str] = None,
                                    page_num: Optional[int] = None,
                                    page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos服务集群实例 - GET /rcc/v1/nacos/service/getClusterInstances"""
        return self._get('/rcc/v1/nacos/service/getClusterInstances', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'serviceName': service_name, 'groupName': group_name,
            'clusterName': cluster_name,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询Nacos服务集群实例')

    def list_service_push_trace(self, region_id: str, spu_inst_id: str,
                                query_type: str, start_time: str, end_time: str,
                                service_name: Optional[str] = None,
                                group: Optional[str] = None,
                                ip: Optional[str] = None,
                                namespace: Optional[str] = None,
                                page_number: Optional[int] = None,
                                page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos服务推送轨迹 - POST /rcc/v1/nacos/service/listServicePushTrace"""
        return self._post('/rcc/v1/nacos/service/listServicePushTrace', {
            'spuInstId': spu_inst_id, 'queryType': query_type,
            'serviceName': service_name, 'group': group, 'ip': ip,
            'namespace': namespace,
            'startTime': start_time, 'endTime': end_time,
            'pageNumber': page_number, 'pageSize': page_size,
        }, '查询Nacos服务推送轨迹', region_id)

    def list_nacos_properties(self, region_id: str, instance_id: str,
                              page_num: Optional[int] = None,
                              page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos属性列表 - GET /rcc/v1/nacos/property/list"""
        return self._get('/rcc/v1/nacos/property/list', region_id, {
            'instanceId': instance_id,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询Nacos属性列表')

    # ==================== P1 Nacos 配置管理（8个） ====================

    def list_nacos_configs(self, region_id: str, instance_id: str,
                           namespace_id: Optional[str] = None,
                           data_id: Optional[str] = None,
                           group: Optional[str] = None,
                           app_name: Optional[str] = None,
                           config_tags: Optional[str] = None,
                           page_num: Optional[int] = None,
                           page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos配置列表 - GET /rcc/v1/nacos/config/list"""
        return self._get('/rcc/v1/nacos/config/list', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'dataId': data_id, 'group': group, 'appName': app_name,
            'configTags': config_tags,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询Nacos配置列表')

    def get_nacos_config_detail(self, region_id: str, instance_id: str,
                                data_id: str, group: str,
                                namespace_id: Optional[str] = None,
                                beta: Optional[bool] = None) -> Dict[str, Any]:
        """查询Nacos配置详情 - GET /rcc/v1/nacos/config/detail"""
        return self._get('/rcc/v1/nacos/config/detail', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'dataId': data_id, 'group': group, 'beta': beta,
        }, '查询Nacos配置详情')

    def get_nacos_config_content(self, region_id: str, instance_id: str,
                                 data_id: str, group: str,
                                 namespace_id: Optional[str] = None) -> Dict[str, Any]:
        """查询Nacos配置内容 - GET /rcc/v1/nacos/config/getContent"""
        return self._get('/rcc/v1/nacos/config/getContent', region_id, {
            'instanceId': instance_id, 'dataId': data_id,
            'group': group, 'namespaceId': namespace_id,
        }, '查询Nacos配置内容')

    def get_nacos_dataid_and_group(self, region_id: str, instance_id: str,
                                   namespace_id: Optional[str] = None) -> Dict[str, Any]:
        """查询Nacos配置的数据和分组 - GET /rcc/v1/nacos/config/getDataIdAndGroup"""
        return self._get('/rcc/v1/nacos/config/getDataIdAndGroup', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
        }, '查询Nacos配置的数据和分组')

    def get_nacos_config_history_list(self, region_id: str, instance_id: str,
                                      data_id: str, group: str,
                                      namespace_id: Optional[str] = None,
                                      page_num: Optional[int] = None,
                                      page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos配置的历史列表 - GET /rcc/v1/nacos/config/getHistoryList"""
        return self._get('/rcc/v1/nacos/config/getHistoryList', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'dataId': data_id, 'group': group,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询Nacos配置的历史列表')

    def get_nacos_config_history_detail(self, region_id: str, instance_id: str,
                                        data_id: str, group: str, id_: str,
                                        namespace_id: Optional[str] = None) -> Dict[str, Any]:
        """查询Nacos配置的历史详情 - GET /rcc/v1/nacos/config/getHistoryDetail"""
        return self._get('/rcc/v1/nacos/config/getHistoryDetail', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'dataId': data_id, 'group': group, 'id': id_,
        }, '查询Nacos配置的历史详情')

    def list_config_trace(self, region_id: str, spu_inst_id: str,
                          namespace: str, query_type: str,
                          start_time: str, end_time: str,
                          data_id: Optional[str] = None,
                          group: Optional[str] = None,
                          ip: Optional[str] = None,
                          page_number: Optional[int] = None,
                          page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos配置轨迹 - POST /rcc/v1/nacos/config/listConfigTrace"""
        return self._post('/rcc/v1/nacos/config/listConfigTrace', {
            'spuInstId': spu_inst_id, 'namespace': namespace,
            'queryType': query_type, 'dataId': data_id, 'group': group,
            'ip': ip, 'startTime': start_time, 'endTime': end_time,
            'pageNumber': page_number, 'pageSize': page_size,
        }, '查询Nacos配置轨迹', region_id)

    def get_nacos_config_listeners(self, region_id: str, instance_id: str,
                                   data_id: str, group: str, type_: str,
                                   namespace_id: Optional[str] = None,
                                   ip: Optional[str] = None) -> Dict[str, Any]:
        """查询Nacos配置监听列表 - GET /rcc/v1/nacos/config/getListeners"""
        return self._get('/rcc/v1/nacos/config/getListeners', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
            'dataId': data_id, 'group': group, 'ip': ip, 'type': type_,
        }, '查询Nacos配置监听列表')
