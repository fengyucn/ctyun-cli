"""天翼云应用性能监控(APM)客户端"""

from typing import Dict, Any, Optional, List
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class APMClient:
    """天翼云应用性能监控(APM)客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化应用性能监控客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'apm'
        self.base_endpoint = 'arms-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def _request(self, method: str, path: str,
                 query_params: Optional[Dict] = None,
                 body_data: Optional[Dict] = None,
                 region_id: Optional[str] = None) -> Dict[str, Any]:
        """通用请求方法。regionId 通过 header 传递"""
        url = f"https://{self.base_endpoint}{path}"
        if query_params:
            query_params = {k: v for k, v in query_params.items() if v is not None}
        body = json.dumps(body_data) if body_data else ('' if method == 'POST' else None)

        extra_headers = {}
        if region_id:
            extra_headers['regionId'] = region_id

        headers = self.eop_auth.sign_request(
            method=method,
            url=url,
            query_params=query_params,
            body=body,
            extra_headers=extra_headers
        )

        logger.debug(f"请求URL: {url}")
        logger.debug(f"请求体: {body}")
        logger.debug(f"查询参数: {query_params}")

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
            return {'statusCode': 500, 'error': 'Exception', 'message': str(e)}

    def _get(self, path: str, region_id: str, query_params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('GET', path, query_params=query_params, region_id=region_id)

    def _post(self, path: str, region_id: str,
              body_data: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('POST', path, body_data=body_data, region_id=region_id)

    # ==================== 1. 基础配置与元数据 ====================

    def query_project_metadata(self, region_id: str, env_uuid: Optional[str] = None) -> Dict[str, Any]:
        """查询项目元数据信息 - GET /v1/namespace/project/list"""
        return self._get('/v1/namespace/project/list', region_id, {'envUuid': env_uuid})

    def query_env_types(self, region_id: str) -> Dict[str, Any]:
        """查询环境类型信息 - GET /v1/namespace/envType/list"""
        return self._get('/v1/namespace/envType/list', region_id)

    def query_envs(self, region_id: str) -> Dict[str, Any]:
        """查询环境信息 - GET /v1/namespace/env/list"""
        return self._get('/v1/namespace/env/list', region_id)

    def query_app_conf(self, region_id: str, service_name: str,
                       project_code: str, deployment: str) -> Dict[str, Any]:
        """查询应用配置接口 - GET /v1/app/conf/list"""
        return self._get('/v1/app/conf/list', region_id, {
            'serviceName': service_name,
            'projectCode': project_code,
            'deployment': deployment,
        })

    def list_license_key(self, region_id: str) -> Dict[str, Any]:
        """列出LicenseKey - POST /v1/clicense/query"""
        return self._post('/v1/clicense/query', region_id)

    def query_monitor_open_status(self, region_id: str, environment_code: str) -> Dict[str, Any]:
        """查询采集服务开启状态 - GET /v1/monitortarget/queryMonitorOpenStatus"""
        return self._get('/v1/monitortarget/queryMonitorOpenStatus', region_id, {
            'environmentCode': environment_code,
        })

    def query_default_job_list(self, region_id: str, environment_code: str) -> Dict[str, Any]:
        """查询默认Job列表 - POST /v1/env/queryDefaultJobList"""
        return self._post('/v1/env/queryDefaultJobList', region_id, {
            'environmentCode': environment_code,
        })

    def query_common_label(self, region_id: str, environment_code: str) -> Dict[str, Any]:
        """查询全局标签 - POST /v1/env/queryCommonLabel"""
        return self._post('/v1/env/queryCommonLabel', region_id, {
            'environmentCode': environment_code,
        })

    # ==================== 2. 应用与实例管理 ====================

    def list_apps(self, region_id: str, env_uuid: Optional[str] = None) -> Dict[str, Any]:
        """获取应用列表 - GET /v1/app/list"""
        return self._get('/v1/app/list', region_id, {'envUuid': env_uuid})

    def list_transaction_types(self, region_id: str) -> Dict[str, Any]:
        """查询接口调用类型列表 - GET /v1/transactions/types/list"""
        return self._get('/v1/transactions/types/list', region_id)

    def list_agents_page(self, region_id: str,
                         service_name: Optional[str] = None,
                         deployment: Optional[str] = None,
                         agent_ip: Optional[str] = None,
                         access_type: Optional[int] = None,
                         agent_status: Optional[int] = None,
                         version: Optional[str] = None,
                         page_num: Optional[int] = None,
                         page_size: Optional[int] = None) -> Dict[str, Any]:
        """分页查询agent列表 - GET /v1/agent/page"""
        return self._get('/v1/agent/page', region_id, {
            'serviceName': service_name, 'deployment': deployment, 'agentIp': agent_ip,
            'accessType': access_type, 'agentStatus': agent_status, 'version': version,
            'pageNum': page_num, 'pageSize': page_size,
        })

    def query_env_instance_list(self, region_id: str,
                                addon_template_id: Optional[str] = None,
                                env_type: Optional[str] = None,
                                resource_id: Optional[str] = None,
                                resource_name: Optional[str] = None) -> Dict[str, Any]:
        """查询环境实例列表 - POST /v1/env/queryEnvInstanceList"""
        return self._post('/v1/env/queryEnvInstanceList', region_id, {
            'addonTemplateId': addon_template_id, 'envType': env_type,
            'resourceId': resource_id, 'resourceName': resource_name,
        })

    def list_app_tasks_page(self, region_id: str,
                            start_time: int, end_time: int,
                            deployment: str, env_uuid: str,
                            service_name: Optional[str] = None,
                            project_code: Optional[str] = None,
                            project_uuid: Optional[str] = None,
                            page_num: Optional[int] = None,
                            page_size: Optional[int] = None) -> Dict[str, Any]:
        """分页查询应用监控任务 - GET /v1/app/page"""
        return self._get('/v1/app/page', region_id, {
            'startTime': start_time, 'endTime': end_time,
            'deployment': deployment, 'envUuid': env_uuid,
            'serviceName': service_name, 'projectCode': project_code,
            'projectUuid': project_uuid, 'pageNum': page_num, 'pageSize': page_size,
        })

    def list_instances_stat(self, region_id: str,
                            start_time: int, end_time: int, service_name: str,
                            project_code: Optional[str] = None,
                            deployment: Optional[str] = None,
                            sort: Optional[str] = None) -> Dict[str, Any]:
        """查询实例统计列表 - GET /v1/instances/stat/list"""
        return self._get('/v1/instances/stat/list', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment, 'sort': sort,
        })

    # ==================== 3. 调用链与拓扑 ====================

    def get_trace(self, region_id: str, trace_id: str,
                  timestamp: Optional[int] = None,
                  project_code: Optional[str] = None) -> Dict[str, Any]:
        """获取调用链详情 - GET /v1/transactions/trace"""
        return self._get('/v1/transactions/trace', region_id, {
            'traceId': trace_id, 'timestamp': timestamp, 'projectCode': project_code,
        })

    def get_trace_span_detail(self, region_id: str, trace_id: str, span_id: str,
                              timestamp: Optional[int] = None) -> Dict[str, Any]:
        """调用链span详情查询 - GET /v1/transactions/traceSpanDetail"""
        return self._get('/v1/transactions/traceSpanDetail', region_id, {
            'traceId': trace_id, 'spanId': span_id, 'timestamp': timestamp,
        })

    def list_transactions_page(self, region_id: str,
                               start_time: int, end_time: int,
                               service_name: Optional[str] = None,
                               project_code: Optional[str] = None,
                               deployment: Optional[str] = None,
                               sort: Optional[str] = None,
                               duration: Optional[float] = None,
                               outcome: Optional[str] = None,
                               type_: Optional[str] = None,
                               span_kind: Optional[str] = None,
                               trace_id: Optional[str] = None,
                               transaction_name: Optional[str] = None,
                               query_filter: Optional[str] = None,
                               page_num: Optional[int] = None,
                               page_size: Optional[int] = None) -> Dict[str, Any]:
        """分页查询调用链列表信息 - GET /v1/transactions/page"""
        return self._get('/v1/transactions/page', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment, 'sort': sort,
            'duration': duration, 'outcome': outcome, 'type': type_, 'spanKind': span_kind,
            'traceId': trace_id, 'transactionName': transaction_name,
            'queryFilter': query_filter, 'pageNum': page_num, 'pageSize': page_size,
        })

    def query_topology_graph(self, region_id: str,
                             start_time: int, end_time: int, service_name: str,
                             project_code: Optional[str] = None,
                             deployment: Optional[str] = None) -> Dict[str, Any]:
        """查询拓扑图 - GET /v1/topology/graph/app"""
        return self._get('/v1/topology/graph/app', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment,
        })

    # ==================== 4. 性能监控数据 ====================

    def query_overview_statistics(self, region_id: str,
                                  start_time: int, end_time: int, service_name: str,
                                  project_code: Optional[str] = None,
                                  deployment: Optional[str] = None) -> Dict[str, Any]:
        """概览统计数据查询 - GET /v1/overview/statistics"""
        return self._get('/v1/overview/statistics', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment,
        })

    def get_request_curve_chart(self, region_id: str,
                                start_time: int, end_time: int, service_name: str,
                                project_code: Optional[str] = None,
                                deployment: Optional[str] = None,
                                query: Optional[str] = None) -> Dict[str, Any]:
        """调用曲线图 - GET /v1/request/getRequestCurveChart"""
        return self._get('/v1/request/getRequestCurveChart', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment, 'query': query,
        })

    def get_http_code_curve_chart(self, region_id: str,
                                  start_time: int, end_time: int, service_name: str,
                                  project_code: Optional[str] = None,
                                  deployment: Optional[str] = None) -> Dict[str, Any]:
        """http响应码曲线图 - GET /v1/request/getHttpCodeCurveChart"""
        return self._get('/v1/request/getHttpCodeCurveChart', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment,
        })

    def list_slow_transactions_page(self, region_id: str,
                                    start_time: int, end_time: int, service_name: str,
                                    project_code: Optional[str] = None,
                                    deployment: Optional[str] = None,
                                    page_num: Optional[int] = None,
                                    page_size: Optional[int] = None,
                                    span_kind: Optional[str] = None) -> Dict[str, Any]:
        """慢调用分页查询 - GET /v1/transactions/page/slow"""
        return self._get('/v1/transactions/page/slow', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment,
            'pageNum': page_num, 'pageSize': page_size, 'spanKind': span_kind,
        })

    def get_exception_list(self, region_id: str,
                           start_time: int, end_time: int, service_name: str,
                           transaction_name: Optional[str] = None,
                           project_code: Optional[str] = None,
                           deployment: Optional[str] = None,
                           page_num: Optional[int] = None,
                           page_size: Optional[int] = None) -> Dict[str, Any]:
        """查询异常事件列表 - GET /v1/exception/getExceptionList"""
        return self._get('/v1/exception/getExceptionList', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'transactionName': transaction_name, 'projectCode': project_code,
            'deployment': deployment, 'pageNum': page_num, 'pageSize': page_size,
        })

    def list_sql_stat_page(self, region_id: str,
                           start_time: int, end_time: int, service_name: str, db_types: str,
                           project_code: Optional[str] = None,
                           deployment: Optional[str] = None,
                           page_num: Optional[int] = None,
                           page_size: Optional[int] = None) -> Dict[str, Any]:
        """SQL调用统计分页查询 - GET /v1/spans/sql-stat/page"""
        return self._get('/v1/spans/sql-stat/page', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'dbTypes': db_types, 'projectCode': project_code, 'deployment': deployment,
            'pageNum': page_num, 'pageSize': page_size,
        })

    def list_sql_stat_histogram(self, region_id: str,
                                start_time: int, end_time: int, service_name: str,
                                project_code: Optional[str] = None,
                                deployment: Optional[str] = None,
                                db_types: Optional[str] = None) -> Dict[str, Any]:
        """SQL调用统计列表查询 - GET /v1/spans/sql-stat/histogram"""
        return self._get('/v1/spans/sql-stat/histogram', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment, 'dbTypes': db_types,
        })

    def list_nosql_stat_histogram(self, region_id: str,
                                  start_time: int, end_time: int, service_name: str,
                                  project_code: Optional[str] = None,
                                  deployment: Optional[str] = None,
                                  db_types: Optional[str] = None) -> Dict[str, Any]:
        """NoSQL调用统计列表查询 - GET /v1/spans/nosql-stat/histogram"""
        return self._get('/v1/spans/nosql-stat/histogram', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment, 'dbTypes': db_types,
        })

    def list_nosql_stat_page(self, region_id: str,
                             start_time: int, end_time: int, service_name: str,
                             project_code: Optional[str] = None,
                             deployment: Optional[str] = None,
                             db_types: Optional[str] = None,
                             target_instance_id: Optional[str] = None,
                             page_num: Optional[int] = None,
                             page_size: Optional[int] = None) -> Dict[str, Any]:
        """NoSQL调用统计分页查询 - GET /v1/spans/nosql-stat/page"""
        return self._get('/v1/spans/nosql-stat/page', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment, 'dbTypes': db_types,
            'targetInstanceId': target_instance_id, 'pageNum': page_num, 'pageSize': page_size,
        })

    def list_mq_stat_page(self, region_id: str,
                          start_time: int, end_time: int, service_name: str,
                          project_code: Optional[str] = None,
                          deployment: Optional[str] = None,
                          instance_id: Optional[str] = None,
                          type_: Optional[str] = None,
                          message_system: Optional[str] = None,
                          page_num: Optional[int] = None,
                          page_size: Optional[int] = None) -> Dict[str, Any]:
        """mq调用统计分页查询 - GET /v1/mq/stat/pageList"""
        return self._get('/v1/mq/stat/pageList', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment, 'instanceId': instance_id,
            'type': type_, 'messageSystem': message_system,
            'pageNum': page_num, 'pageSize': page_size,
        })

    def list_transaction_stat(self, region_id: str,
                              start_time: int, end_time: int, service_name: str,
                              sort: Optional[str] = None,
                              project_code: Optional[str] = None,
                              deployment: Optional[str] = None) -> Dict[str, Any]:
        """查询接口调用统计列表 - GET /v1/transactions/stat/list"""
        return self._get('/v1/transactions/stat/list', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'sort': sort, 'projectCode': project_code, 'deployment': deployment,
        })

    def get_jvm_info(self, region_id: str,
                     start_time: int, end_time: int, service_name: str,
                     project_code: Optional[str] = None,
                     deployment: Optional[str] = None,
                     instance_id: Optional[str] = None) -> Dict[str, Any]:
        """获取JVM信息 - GET /v1/jvm/jvmInfo"""
        return self._get('/v1/jvm/jvmInfo', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment, 'instanceId': instance_id,
        })

    def get_app_instance_curve_chart(self, region_id: str,
                                     start_time: int, end_time: int, service_name: str,
                                     project_code: Optional[str] = None,
                                     deployment: Optional[str] = None) -> Dict[str, Any]:
        """应用实例数曲线图 - GET /v1/request/getAppInstanceCurveChart"""
        return self._get('/v1/request/getAppInstanceCurveChart', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment,
        })

    def get_jvm_gc_count(self, region_id: str,
                         start_time: int, end_time: int, service_name: str,
                         project_code: Optional[str] = None,
                         deployment: Optional[str] = None,
                         instance_id: Optional[str] = None,
                         type_: Optional[str] = None) -> Dict[str, Any]:
        """JVM的GC次数曲线图 - GET /v1/jvm/gcCount"""
        return self._get('/v1/jvm/gcCount', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment,
            'instanceId': instance_id, 'type': type_,
        })

    def get_jvm_thread_count(self, region_id: str,
                             start_time: int, end_time: int, service_name: str,
                             project_code: Optional[str] = None,
                             deployment: Optional[str] = None,
                             instance_id: Optional[str] = None) -> Dict[str, Any]:
        """JVM线程数曲线图 - GET /v1/jvm/threadCount"""
        return self._get('/v1/jvm/threadCount', region_id, {
            'startTime': start_time, 'endTime': end_time, 'serviceName': service_name,
            'projectCode': project_code, 'deployment': deployment, 'instanceId': instance_id,
        })

    # ==================== 5. 用量统计 ====================

    def usage_total_view(self, region_id: str,
                         start_time: int, end_time: int) -> Dict[str, Any]:
        """用量统计总览 - GET /v1/usage/totalView"""
        return self._get('/v1/usage/totalView', region_id, {
            'startTime': start_time, 'endTime': end_time,
        })

    def usage_span_report(self, region_id: str,
                          start_time: int, end_time: int, step: int) -> Dict[str, Any]:
        """用量统计Span上报量趋势图 - GET /v1/usage/spanReport"""
        return self._get('/v1/usage/spanReport', region_id, {
            'startTime': start_time, 'endTime': end_time, 'step': step,
        })

    def usage_agent_hour(self, region_id: str,
                         start_time: int, end_time: int, step: int) -> Dict[str, Any]:
        """用量统计agentHour趋势图 - GET /v1/usage/agentHour"""
        return self._get('/v1/usage/agentHour', region_id, {
            'startTime': start_time, 'endTime': end_time, 'step': step,
        })

    def usage_span_store(self, region_id: str,
                         start_time: int, end_time: int, step: int) -> Dict[str, Any]:
        """用量统计Span存储量趋势图 - GET /v1/usage/spanStore"""
        return self._get('/v1/usage/spanStore', region_id, {
            'startTime': start_time, 'endTime': end_time, 'step': step,
        })

    # ==================== 6. 告警管理 ====================

    def list_alert_rules(self, region_id: str, obj_type: str,
                         rule_name: Optional[str] = None,
                         group_id: Optional[int] = None,
                         rule_status: Optional[int] = None,
                         obj_id: Optional[str] = None,
                         page_num: Optional[int] = None,
                         page_size: Optional[int] = None) -> Dict[str, Any]:
        """分页查询告警规则 - GET /v1/alert/rule/list"""
        return self._get('/v1/alert/rule/list', region_id, {
            'objType': obj_type, 'ruleName': rule_name, 'groupId': group_id,
            'ruleStatus': rule_status, 'objId': obj_id,
            'pageNum': page_num, 'pageSize': page_size,
        })

    def list_alert_rule_templates(self, region_id: str, obj_type: str) -> Dict[str, Any]:
        """查询告警规则对象模板分组列表 - GET /v1/alert/ruleTemplate/list"""
        return self._get('/v1/alert/ruleTemplate/list', region_id, {'objType': obj_type})

    def list_alert_send_history(self, region_id: str,
                                page_num: Optional[int] = None,
                                page_size: Optional[int] = None,
                                alert_name: Optional[str] = None,
                                alert_status: Optional[int] = None,
                                start_time: Optional[int] = None,
                                end_time: Optional[int] = None,
                                strategy_id: Optional[int] = None) -> Dict[str, Any]:
        """分页查询告警发送历史 - GET /v1/alert/send/list"""
        return self._get('/v1/alert/send/list', region_id, {
            'pageNum': page_num, 'pageSize': page_size, 'alertName': alert_name,
            'alertStatus': alert_status, 'startTime': start_time, 'endTime': end_time,
            'strategyId': strategy_id,
        })

    # ==================== 7. 通知管理 ====================

    def list_contacts(self, region_id: str,
                      group_id: Optional[int] = None,
                      page_num: Optional[int] = None,
                      page_size: Optional[int] = None) -> Dict[str, Any]:
        """分页获取通知联系人详细信息 - GET /v1/alert/contact/list"""
        return self._get('/v1/alert/contact/list', region_id, {
            'groupId': group_id, 'pageNum': page_num, 'pageSize': page_size,
        })

    def list_contact_groups(self, region_id: str,
                            page_num: int, page_size: int) -> Dict[str, Any]:
        """通知组分页查询 - GET /v1/alert/contactGroup/list"""
        return self._get('/v1/alert/contactGroup/list', region_id, {
            'pageNum': page_num, 'pageSize': page_size,
        })

    def list_notify_strategies(self, region_id: str,
                               page_num: Optional[int] = None,
                               page_size: Optional[int] = None,
                               strategy_name: Optional[str] = None) -> Dict[str, Any]:
        """分页获取通知策略信息 - GET /v1/alert/notifyStrategy/list"""
        return self._get('/v1/alert/notifyStrategy/list', region_id, {
            'pageNum': page_num, 'pageSize': page_size, 'strategyName': strategy_name,
        })

    # ==================== 8. Webhook管理 ====================

    def list_webhooks(self, region_id: str,
                      page_num: Optional[int] = None,
                      page_size: Optional[int] = None,
                      name: Optional[str] = None) -> Dict[str, Any]:
        """webhook分页查询 - GET /v1/alert/webhook/list"""
        return self._get('/v1/alert/webhook/list', region_id, {
            'pageNum': page_num, 'pageSize': page_size, 'name': name,
        })
