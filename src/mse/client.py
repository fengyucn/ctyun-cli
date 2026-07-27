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

    # ==================== P2 Nacos 周边（8个） ====================

    def list_nacos_namespaces(self, region_id: str, instance_id: str,
                              page_num: Optional[int] = None,
                              page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos命名空间列表 - GET /rcc/v1/nacos/namespace/list"""
        return self._get('/rcc/v1/nacos/namespace/list', region_id, {
            'instanceId': instance_id, 'pageNum': page_num, 'pageSize': page_size,
        }, '查询Nacos命名空间列表')

    def get_nacos_namespace_detail(self, region_id: str, instance_id: str,
                                   namespace_id: str) -> Dict[str, Any]:
        """查询Nacos命名空间详情 - GET /rcc/v1/nacos/namespace/detail"""
        return self._get('/rcc/v1/nacos/namespace/detail', region_id, {
            'instanceId': instance_id, 'namespaceId': namespace_id,
        }, '查询Nacos命名空间详情')

    def get_nacos_blackwhite_list(self, region_id: str, instance_id: str) -> Dict[str, Any]:
        """查询Nacos黑白名单 - GET /rcc/v1/nacos/property/query"""
        return self._get('/rcc/v1/nacos/property/query', region_id, {
            'instanceId': instance_id,
        }, '查询Nacos黑白名单')

    def list_nacos_users(self, region_id: str, instance_id: str,
                         page_num: Optional[int] = None,
                         page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos实例用户列表 - GET /rcc/v1/nacos/user/list"""
        return self._get('/rcc/v1/nacos/user/list', region_id, {
            'instanceId': instance_id, 'pageNum': page_num, 'pageSize': page_size,
        }, '查询Nacos实例用户列表')

    def list_nacos_roles(self, region_id: str, instance_id: str,
                         username: Optional[str] = None,
                         page_num: Optional[int] = None,
                         page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos用户角色 - GET /rcc/v1/nacos/user/listRole"""
        return self._get('/rcc/v1/nacos/user/listRole', region_id, {
            'instanceId': instance_id, 'username': username,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询Nacos用户角色')

    def get_nacos_role_permission(self, region_id: str, instance_id: str,
                                  role: Optional[str] = None,
                                  page_num: Optional[int] = None,
                                  page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询Nacos用户角色权限 - GET /rcc/v1/nacos/user/getPermission"""
        return self._get('/rcc/v1/nacos/user/getPermission', region_id, {
            'instanceId': instance_id, 'role': role,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询Nacos用户角色权限')

    def list_nacos_aksk(self, region_id: str, instance_id: str,
                        page_num: Optional[int] = None,
                        page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询NacosAKSK认证 - GET /rcc/v1/nacos/aksk/list"""
        return self._get('/rcc/v1/nacos/aksk/list', region_id, {
            'instanceId': instance_id, 'pageNum': page_num, 'pageSize': page_size,
        }, '查询NacosAKSK认证')

    def get_nacos_aksk_permission(self, region_id: str, instance_id: str,
                                  access_key: str) -> Dict[str, Any]:
        """查询NacosAKSK权限 - GET /rcc/v1/nacos/aksk/getPermission"""
        return self._get('/rcc/v1/nacos/aksk/getPermission', region_id, {
            'instanceId': instance_id, 'accessKey': access_key,
        }, '查询NacosAKSK权限')

    # ==================== P3 云原生API网关（18个） ====================

    def list_gateways(self, region_id: str,
                      spu_inst_id: Optional[str] = None,
                      spu_inst_name: Optional[str] = None,
                      biz_state: Optional[str] = None,
                      page_num: Optional[int] = None,
                      page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询网关列表 - GET /cgw/v1/instance/list"""
        return self._get('/cgw/v1/instance/list', region_id, {
            'spuInstId': spu_inst_id, 'spuInstName': spu_inst_name,
            'bizState': biz_state, 'pageNum': page_num, 'pageSize': page_size,
        }, '查询网关列表')

    def get_gateway_detail(self, region_id: str, spu_inst_id: str) -> Dict[str, Any]:
        """查询网关详情 - GET /cgw/v1/instance/one"""
        return self._get('/cgw/v1/instance/one', region_id,
                         {'spuInstId': spu_inst_id}, '查询网关详情')

    def get_gateway_global_config(self, region_id: str, inst_id: str) -> Dict[str, Any]:
        """获取网关全局参数 - GET /cgw/v1/globalConfig/getTraceAnalysisStatus"""
        return self._get('/cgw/v1/globalConfig/getTraceAnalysisStatus', region_id,
                         {'instId': inst_id}, '获取网关全局参数')

    def get_gateway_base_config(self, region_id: str, gw_inst_id: str) -> Dict[str, Any]:
        """获取基础信息页配置信息 - GET /cgw/v1/globalConfig/getConfig"""
        return self._get('/cgw/v1/globalConfig/getConfig', region_id,
                         {'gwInstId': gw_inst_id}, '获取基础信息页配置信息')

    def query_async_task(self, region_id: str, code: str) -> Dict[str, Any]:
        """查询异步任务信息 - GET /cgw/v1/task/query"""
        return self._get('/cgw/v1/task/query', region_id,
                         {'code': code}, '查询异步任务信息')

    def list_gateway_routes(self, region_id: str, inst_id: str,
                            route_name: Optional[str] = None,
                            route_status: Optional[str] = None,
                            type_: Optional[str] = None,
                            destination_type: Optional[str] = None,
                            page_num: Optional[int] = None,
                            page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询网关路由列表 - GET /cgw/v1/route/list"""
        return self._get('/cgw/v1/route/list', region_id, {
            'instId': inst_id, 'routeName': route_name,
            'routeStatus': route_status, 'type': type_,
            'destinationType': destination_type,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询网关路由列表')

    def get_gateway_route_detail(self, region_id: str, inst_id: str, id_: str) -> Dict[str, Any]:
        """查询网关路由详情 - GET /cgw/v1/route/one"""
        return self._get('/cgw/v1/route/one', region_id,
                         {'instId': inst_id, 'id': id_}, '查询网关路由详情')

    def list_route_snapshots(self, region_id: str, inst_id: str, route_id: str,
                             operation_version: Optional[str] = None,
                             operation_id: Optional[str] = None,
                             page_num: Optional[int] = None,
                             page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询路由历史快照列表 - GET /cgw/v1/routeSnapshot/list"""
        return self._get('/cgw/v1/routeSnapshot/list', region_id, {
            'instId': inst_id, 'routeId': route_id,
            'operationVersion': operation_version, 'operationId': operation_id,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询路由历史快照列表')

    def get_route_snapshot(self, region_id: str, inst_id: str,
                           route_id: str, id_: str) -> Dict[str, Any]:
        """查询路由历史快照 - GET /cgw/v1/routeSnapshot/one"""
        return self._get('/cgw/v1/routeSnapshot/one', region_id,
                         {'instId': inst_id, 'routeId': route_id, 'id': id_},
                         '查询路由历史快照')

    def list_gateway_upstreams(self, region_id: str, inst_id: str,
                               service_name: Optional[str] = None,
                               service_source_type: Optional[str] = None,
                               page_num: Optional[int] = None,
                               page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询网关已订阅的服务列表 - GET /cgw/v1/upstream/list"""
        return self._get('/cgw/v1/upstream/list', region_id, {
            'instId': inst_id, 'serviceName': service_name,
            'serviceSourceType': service_source_type,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询网关已订阅的服务列表')

    def get_gateway_upstream_detail(self, region_id: str, inst_id: str,
                                    id_: str) -> Dict[str, Any]:
        """查询服务详情 - GET /cgw/v1/upstream/one"""
        return self._get('/cgw/v1/upstream/one', region_id,
                         {'instId': inst_id, 'id': id_}, '查询服务详情')

    def list_upstream_versions(self, region_id: str, inst_id: str,
                               upstream_id: str) -> Dict[str, Any]:
        """查询服务版本列表 - GET /cgw/v1/upstreamVersion/list"""
        return self._get('/cgw/v1/upstreamVersion/list', region_id,
                         {'instId': inst_id, 'upstreamId': upstream_id},
                         '查询服务版本列表')

    def list_upstream_sources(self, region_id: str, inst_id: str) -> Dict[str, Any]:
        """查询已关联来源列表 - GET /cgw/v1/upstreamSource/list"""
        return self._get('/cgw/v1/upstreamSource/list', region_id,
                         {'instId': inst_id}, '查询已关联来源列表')

    def list_gateway_domains(self, region_id: str, inst_id: str,
                             page_num: Optional[int] = None,
                             page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询网关域名列表 - GET /cgw/v1/domain/list"""
        return self._get('/cgw/v1/domain/list', region_id, {
            'instId': inst_id, 'pageNum': page_num, 'pageSize': page_size,
        }, '查询网关域名列表')

    def get_gateway_domain_detail(self, region_id: str, inst_id: str,
                                  id_: str) -> Dict[str, Any]:
        """查询网关域名详情 - GET /cgw/v1/domain/one"""
        return self._get('/cgw/v1/domain/one', region_id,
                         {'instId': inst_id, 'id': id_}, '查询网关域名详情')

    def list_routes_used_domain(self, region_id: str, inst_id: str,
                                domain_code: Optional[str] = None,
                                domain_name: Optional[str] = None,
                                page_num: Optional[int] = None,
                                page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询网关域名绑定的路由列表 - GET /cgw/v1/domain/listRoutesUsedDomain"""
        return self._get('/cgw/v1/domain/listRoutesUsedDomain', region_id, {
            'instId': inst_id, 'domainCode': domain_code,
            'domainName': domain_name,
            'pageNum': page_num, 'pageSize': page_size,
        }, '查询网关域名绑定的路由列表')

    def list_bound_elbs(self, region_id: str, inst_id: str) -> Dict[str, Any]:
        """查询网关绑定的ELB列表 - GET /cgw/v1/elb/boundElbInfoList"""
        return self._get('/cgw/v1/elb/boundElbInfoList', region_id,
                         {'instId': inst_id}, '查询网关绑定的ELB列表')

    def list_available_elbs(self, region_id: str, inst_id: str, region_code: str,
                            elb_instance_type: Optional[str] = None) -> Dict[str, Any]:
        """查询用户已有（启动中状态无监听）ELB - GET /cgw/v1/elb/elbList"""
        return self._get('/cgw/v1/elb/elbList', region_id, {
            'instId': inst_id, 'regionCode': region_code,
            'elbInstanceType': elb_instance_type,
        }, '查询可用ELB列表')
