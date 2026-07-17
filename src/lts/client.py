"""天翼云云日志服务(LTS)客户端"""

from typing import Dict, Any, Optional, List
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class LTSClient:
    """天翼云云日志服务(LTS)客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化云日志服务客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'lts'
        self.base_endpoint = 'ctlts-global.ctapi.ctyun.cn'
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

        try:
            if method == 'GET':
                response = self.client.session.get(
                    url, params=query_params, headers=headers, timeout=30
                )
            elif method == 'DELETE':
                response = self.client.session.delete(
                    url, params=query_params, headers=headers, timeout=30
                )
            elif method == 'PUT':
                response = self.client.session.put(
                    url, data=body, headers=headers, timeout=30
                )
            else:
                response = self.client.session.post(
                    url, data=body, headers=headers, timeout=30
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
            return {
                'statusCode': 500,
                'error': 'Exception',
                'message': str(e)
            }

    # ==================== 1. 日志项目管理 ====================

    def create_project(self, region_id: str, project_name: str,
                       description: Optional[str] = None) -> Dict[str, Any]:
        """项目创建 - POST /v1/lts/project"""
        raise NotImplementedError

    def delete_project(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """项目删除 - DELETE /v1/lts/project"""
        raise NotImplementedError

    def list_projects(self, region_id: str) -> Dict[str, Any]:
        """项目列表 - GET /v1/lts/project/list"""
        raise NotImplementedError

    def list_projects_page(self, region_id: str, page_no: int = 1,
                           page_size: int = 10) -> Dict[str, Any]:
        """项目分页列表 - GET /v1/lts/project/page"""
        raise NotImplementedError

    def update_project(self, region_id: str, project_id: str,
                       project_name: Optional[str] = None,
                       description: Optional[str] = None) -> Dict[str, Any]:
        """编辑日志项目 - PUT /v1/lts/project"""
        raise NotImplementedError

    def get_project_detail(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """获取项目详情 - GET /v1/lts/project/detail"""
        raise NotImplementedError

    def get_project_count(self, region_id: str) -> Dict[str, Any]:
        """查看日志项目数量 - GET /v1/lts/project/count"""
        raise NotImplementedError

    def rename_project(self, region_id: str, project_id: str,
                       new_name: str) -> Dict[str, Any]:
        """重命名项目 - PUT /v1/lts/project/rename"""
        raise NotImplementedError

    def update_project_description(self, region_id: str, project_id: str,
                                    description: str) -> Dict[str, Any]:
        """更新项目描述 - PUT /v1/lts/project/description"""
        raise NotImplementedError

    def get_project_description(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """获取项目描述 - GET /v1/lts/project/description"""
        raise NotImplementedError

    def get_project_id_by_name(self, region_id: str, project_name: str) -> Dict[str, Any]:
        """通过名称获得项目ID - GET /v1/lts/project/id-by-name"""
        raise NotImplementedError

    def check_project_exists(self, region_id: str, project_name: str) -> Dict[str, Any]:
        """检查项目是否存在 - GET /v1/lts/project/exists"""
        raise NotImplementedError

    def list_project_alias(self, region_id: str) -> Dict[str, Any]:
        """查询日志项目别名列表 - GET /v1/lts/project/alias-list"""
        raise NotImplementedError

    def list_project_original_names(self, region_id: str) -> Dict[str, Any]:
        """查询日志项目原始名称列表 - GET /v1/lts/project/original-name-list"""
        raise NotImplementedError

    def get_project_unit_count(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """查询指定日志项目的单元数量 - GET /v1/lts/project/unit-count"""
        raise NotImplementedError

    def list_project_obs_tasks(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """列出指定项目下的对象存储投递任务 - GET /v1/lts/project/obs-tasks"""
        raise NotImplementedError

    def list_project_kafka_tasks(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """列出指定项目下的kafka投递任务 - GET /v1/lts/project/kafka-tasks"""
        raise NotImplementedError

    def list_project_process_tasks(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """列出指定Project下的加工任务 - GET /v1/lts/project/process-tasks"""
        raise NotImplementedError

    def update_project_tags(self, region_id: str, project_id: str,
                            tags: List[Dict]) -> Dict[str, Any]:
        """修改项目标签 - PUT /v1/lts/project/tags"""
        raise NotImplementedError

    def list_project_tag_keys(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """根据日志项目ID查询标签键名列表 - GET /v1/lts/project/tag-keys"""
        raise NotImplementedError

    def get_project_tag_value(self, region_id: str, project_id: str,
                               tag_key: str) -> Dict[str, Any]:
        """根据日志项目ID查询指定标签键名字对应的值 - GET /v1/lts/project/tag-value"""
        raise NotImplementedError

    def list_project_ids_by_tag(self, region_id: str, tag_key: str,
                                 tag_value: str) -> Dict[str, Any]:
        """根据标签键值查询日志项目ID列表 - GET /v1/lts/project/ids-by-tag"""
        raise NotImplementedError

    def get_project_usage(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """获取项目用量 - GET /v1/lts/project/usage"""
        raise NotImplementedError

    # ==================== 2. 日志单元管理 ====================

    def create_log_unit(self, region_id: str, project_id: str,
                        unit_name: str, **kwargs) -> Dict[str, Any]:
        """日志单元创建 - POST /v1/lts/unit"""
        raise NotImplementedError

    def delete_log_unit(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """日志单元删除 - DELETE /v1/lts/unit"""
        raise NotImplementedError

    def update_log_unit(self, region_id: str, unit_id: str,
                        **kwargs) -> Dict[str, Any]:
        """日志单元更新 - PUT /v1/lts/unit"""
        raise NotImplementedError

    def list_log_units(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """日志单元列表 - GET /v1/lts/unit/list"""
        raise NotImplementedError

    def list_log_units_page(self, region_id: str, project_id: str,
                            page_no: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """日志单元分页列表 - GET /v1/lts/unit/page"""
        raise NotImplementedError

    def get_log_unit_by_id(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """通过日志单元ID获取日志单元 - GET /v1/lts/unit/detail"""
        raise NotImplementedError

    def rename_log_unit(self, region_id: str, unit_id: str,
                        new_name: str) -> Dict[str, Any]:
        """重命名日志单元 - PUT /v1/lts/unit/rename"""
        raise NotImplementedError

    def update_log_unit_description(self, region_id: str, unit_id: str,
                                     description: str) -> Dict[str, Any]:
        """更新日志单元描述 - PUT /v1/lts/unit/description"""
        raise NotImplementedError

    def get_log_unit_remark(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """查询日志单元备注信息 - GET /v1/lts/unit/remark"""
        raise NotImplementedError

    def get_log_unit_alias(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """查询日志单元别名 - GET /v1/lts/unit/alias"""
        raise NotImplementedError

    def get_log_unit_original_name(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """查询日志单元原始名称 - GET /v1/lts/unit/original-name"""
        raise NotImplementedError

    def list_log_unit_alias(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """日志单元别名列表 - GET /v1/lts/unit/alias-list"""
        raise NotImplementedError

    def list_log_unit_original_names(self, region_id: str, project_id: str) -> Dict[str, Any]:
        """日志单元原始名称列表查询 - GET /v1/lts/unit/original-name-list"""
        raise NotImplementedError

    def check_log_unit_exists(self, region_id: str, project_id: str,
                               unit_name: str) -> Dict[str, Any]:
        """检查日志单元是否存在 - GET /v1/lts/unit/exists"""
        raise NotImplementedError

    def get_log_unit_storage_duration(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """查询日志单元日志存储时长 - GET /v1/lts/unit/storage-duration"""
        raise NotImplementedError

    def update_log_unit_storage_duration(self, region_id: str, unit_id: str,
                                          duration: int) -> Dict[str, Any]:
        """更新日志单元存储时长 - PUT /v1/lts/unit/storage-duration"""
        raise NotImplementedError

    def list_log_unit_tags(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """查询日志单元标签列表 - GET /v1/lts/unit/tags"""
        raise NotImplementedError

    def get_unit_index_count(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """获取单元索引数量 - GET /v1/lts/unit/index-count"""
        raise NotImplementedError

    def create_unit_index(self, region_id: str, unit_id: str,
                          index_config: Dict) -> Dict[str, Any]:
        """为指定日志单元创建索引 - POST /v1/lts/unit/index"""
        raise NotImplementedError

    def get_unit_index(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """查询指定日志单元的索引信息 - GET /v1/lts/unit/index"""
        raise NotImplementedError

    def update_unit_index(self, region_id: str, unit_id: str,
                          index_config: Dict) -> Dict[str, Any]:
        """更新指定日志单元的索引信息（覆盖更新） - PUT /v1/lts/unit/index"""
        raise NotImplementedError

    def delete_unit_index(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """删除指定日志单元的索引（包括全文索引） - DELETE /v1/lts/unit/index"""
        raise NotImplementedError

    def get_recommended_index_fields(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """获取推荐索引字段 - GET /v1/lts/unit/recommended-index-fields"""
        raise NotImplementedError

    def get_collection_rule_unit(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """查询采集规则所属日志单元 - GET /v1/lts/unit/by-collection-rule"""
        raise NotImplementedError

    def list_unit_download_tasks(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """获取指定单元下载任务列表 - GET /v1/lts/unit/download-tasks"""
        raise NotImplementedError

    def list_consumer_group_units(self, region_id: str, group_id: str) -> Dict[str, Any]:
        """列出某个消费组的日志单元列表 - GET /v1/lts/unit/by-consumer-group"""
        raise NotImplementedError

    def add_consumer_group_unit(self, region_id: str, group_id: str,
                                 unit_id: str) -> Dict[str, Any]:
        """新增消费组关联日志单元 - POST /v1/lts/unit/consumer-group"""
        raise NotImplementedError

    def remove_consumer_group_unit(self, region_id: str, group_id: str,
                                    unit_id: str) -> Dict[str, Any]:
        """删除消费组关联日志单元 - DELETE /v1/lts/unit/consumer-group"""
        raise NotImplementedError

    def list_unit_tag_keys(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """根据日志单元ID查询标签键名列表 - GET /v1/lts/unit/tag-keys"""
        raise NotImplementedError

    def get_unit_tag_value(self, region_id: str, unit_id: str,
                            tag_key: str) -> Dict[str, Any]:
        """根据日志单元ID查询指定标签键名字对应的值 - GET /v1/lts/unit/tag-value"""
        raise NotImplementedError

    def list_unit_ids_by_tag(self, region_id: str, tag_key: str,
                              tag_value: str) -> Dict[str, Any]:
        """根据标签键值查询日志单元ID列表 - GET /v1/lts/unit/ids-by-tag"""
        raise NotImplementedError

    def get_unit_usage(self, region_id: str, unit_id: str) -> Dict[str, Any]:
        """获取单元用量 - GET /v1/lts/unit/usage"""
        raise NotImplementedError

    # ==================== 3. 主机组管理 ====================

    def create_host_group(self, region_id: str, group_name: str,
                          **kwargs) -> Dict[str, Any]:
        """创建主机组 - POST /v1/lts/host-group"""
        raise NotImplementedError

    def delete_host_group(self, region_id: str, group_id: str) -> Dict[str, Any]:
        """删除主机组 - DELETE /v1/lts/host-group"""
        raise NotImplementedError

    def get_host_group(self, region_id: str, group_id: str) -> Dict[str, Any]:
        """主机组详情 - GET /v1/lts/host-group/detail"""
        raise NotImplementedError

    def list_host_groups(self, region_id: str) -> Dict[str, Any]:
        """主机组列表 - GET /v1/lts/host-group/list"""
        raise NotImplementedError

    def list_host_group_rules(self, region_id: str, group_id: str) -> Dict[str, Any]:
        """主机组下采集规则列表 - GET /v1/lts/host-group/rules"""
        raise NotImplementedError

    def get_host_group_by_name(self, region_id: str, group_name: str) -> Dict[str, Any]:
        """根据名称查询主机组 - GET /v1/lts/host-group/by-name"""
        raise NotImplementedError

    def update_host_group_description(self, region_id: str, group_id: str,
                                       description: str) -> Dict[str, Any]:
        """更新主机组描述 - PUT /v1/lts/host-group/description"""
        raise NotImplementedError

    def get_host_group_description(self, region_id: str, group_id: str) -> Dict[str, Any]:
        """获取主机组描述 - GET /v1/lts/host-group/description"""
        raise NotImplementedError

    def check_host_group_exists(self, region_id: str, group_name: str) -> Dict[str, Any]:
        """检查主机组是否存在 - GET /v1/lts/host-group/exists"""
        raise NotImplementedError

    def get_host_group_count(self, region_id: str) -> Dict[str, Any]:
        """获取主机组数量 - GET /v1/lts/host-group/count"""
        raise NotImplementedError

    def add_hosts_to_group(self, region_id: str, group_id: str,
                           host_ids: List[str]) -> Dict[str, Any]:
        """添加主机到指定主机组 - POST /v1/lts/host-group/hosts"""
        raise NotImplementedError

    def remove_hosts_from_group(self, region_id: str, group_id: str,
                                 host_ids: List[str]) -> Dict[str, Any]:
        """从指定主机组中移除主机 - DELETE /v1/lts/host-group/hosts"""
        raise NotImplementedError

    def get_host_group_rule_count(self, region_id: str, group_id: str) -> Dict[str, Any]:
        """查询主机组关联的采集规则数量 - GET /v1/lts/host-group/rule-count"""
        raise NotImplementedError

    def list_host_group_original_names(self, region_id: str) -> Dict[str, Any]:
        """查询主机组原始名称列表 - GET /v1/lts/host-group/original-name-list"""
        raise NotImplementedError

    def list_connected_hosts(self, region_id: str, group_id: str) -> Dict[str, Any]:
        """列出目标机器组中与日志服务连接正常的机器列表 - GET /v1/lts/host-group/connected-hosts"""
        raise NotImplementedError

    def get_agent_install_command(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """采集器安装命令 - GET /v1/lts/host-group/agent-install-command"""
        raise NotImplementedError

    def get_host_group_host_count(self, region_id: str, group_id: str) -> Dict[str, Any]:
        """获取主机组下主机数量 - GET /v1/lts/host-group/host-count"""
        raise NotImplementedError

    # ==================== 4. 采集配置管理 ====================

    def create_collection_rule(self, region_id: str, rule_config: Dict) -> Dict[str, Any]:
        """创建采集规则 - POST /v1/lts/collection-rule"""
        raise NotImplementedError

    def delete_collection_rule(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """删除采集规则 - DELETE /v1/lts/collection-rule"""
        raise NotImplementedError

    def get_collection_rule(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """采集规则详情 - GET /v1/lts/collection-rule/detail"""
        raise NotImplementedError

    def list_collection_rules(self, region_id: str) -> Dict[str, Any]:
        """采集规则列表 - GET /v1/lts/collection-rule/list"""
        raise NotImplementedError

    def list_collection_rules_page(self, region_id: str, page_no: int = 1,
                                    page_size: int = 10) -> Dict[str, Any]:
        """采集规则分页列表 - GET /v1/lts/collection-rule/page"""
        raise NotImplementedError

    def update_collection_rule(self, region_id: str, rule_id: str,
                                rule_config: Dict) -> Dict[str, Any]:
        """更新采集规则 - PUT /v1/lts/collection-rule"""
        raise NotImplementedError

    def apply_rule_to_host_group(self, region_id: str, rule_id: str,
                                  group_id: str) -> Dict[str, Any]:
        """将日志采集规则应用于目标主机组 - POST /v1/lts/collection-rule/apply"""
        raise NotImplementedError

    def remove_rule_from_host_group(self, region_id: str, rule_id: str,
                                     group_id: str) -> Dict[str, Any]:
        """从目标主机组中移除关联的日志采集规则 - DELETE /v1/lts/collection-rule/apply"""
        raise NotImplementedError

    def list_bound_host_groups(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """获取已绑定指定采集规则的机器组列表 - GET /v1/lts/collection-rule/bound-groups"""
        raise NotImplementedError

    def list_collection_rule_original_names(self, region_id: str) -> Dict[str, Any]:
        """查询采集规则原始名称列表 - GET /v1/lts/collection-rule/original-name-list"""
        raise NotImplementedError

    def get_collection_config_status(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """查询采集配置状态 - GET /v1/lts/collection-rule/status"""
        raise NotImplementedError

    def check_collection_config_exists(self, region_id: str, rule_name: str) -> Dict[str, Any]:
        """检查采集配置是否存在 - GET /v1/lts/collection-rule/exists"""
        raise NotImplementedError

    def get_collection_config_detail(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """获取采集配置详情 - GET /v1/lts/collection-rule/config-detail"""
        raise NotImplementedError

    # ==================== 5. 检索分析 ====================

    def search_logs(self, region_id: str, unit_id: str,
                    query: str, **kwargs) -> Dict[str, Any]:
        """日志检索 - POST /v1/lts/search"""
        raise NotImplementedError

    def update_search_condition(self, region_id: str, search_id: str,
                                 condition: Dict) -> Dict[str, Any]:
        """更新检索条件 - PUT /v1/lts/search/condition"""
        raise NotImplementedError

    # ==================== 6. 日志投递 ====================

    def get_kafka_transfer_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """获取指定的kafka投递任务 - GET /v1/lts/transfer/kafka/detail"""
        raise NotImplementedError

    def start_kafka_transfer_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """启动指定的Kafka投递任务 - POST /v1/lts/transfer/kafka/start"""
        raise NotImplementedError

    def stop_kafka_transfer_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """停止指定的Kafka投递任务 - POST /v1/lts/transfer/kafka/stop"""
        raise NotImplementedError

    def delete_kafka_transfer_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """删除指定的Kafka投递任务 - DELETE /v1/lts/transfer/kafka"""
        raise NotImplementedError

    def get_obs_transfer_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """获取指定的对象存储投递任务 - GET /v1/lts/transfer/obs/detail"""
        raise NotImplementedError

    def start_obs_transfer_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """启动指定的对象存储投递任务 - POST /v1/lts/transfer/obs/start"""
        raise NotImplementedError

    def stop_obs_transfer_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """停止指定的对象存储投递任务 - POST /v1/lts/transfer/obs/stop"""
        raise NotImplementedError

    def update_obs_transfer_task(self, region_id: str, task_id: str,
                                  task_config: Dict) -> Dict[str, Any]:
        """更新指定的对象存储投递任务 - PUT /v1/lts/transfer/obs"""
        raise NotImplementedError

    def delete_obs_transfer_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """删除指定的对象存储投递任务 - DELETE /v1/lts/transfer/obs"""
        raise NotImplementedError

    def get_transfer_failed_lines(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """查询投递任务投递失败行数 - GET /v1/lts/transfer/failed-lines"""
        raise NotImplementedError

    def get_transfer_read_bytes(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """查询投递任务读取字节数 - GET /v1/lts/transfer/read-bytes"""
        raise NotImplementedError

    def get_transfer_read_lines(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """查询任务读取行数 - GET /v1/lts/transfer/read-lines"""
        raise NotImplementedError

    def get_transfer_success_bytes(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """查询任务投递成功字节数 - GET /v1/lts/transfer/success-bytes"""
        raise NotImplementedError

    def get_transfer_success_lines(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """查询任务投递成功行数 - GET /v1/lts/transfer/success-lines"""
        raise NotImplementedError

    def get_transfer_traffic_trend(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """获取投递流量趋势 - GET /v1/lts/transfer/traffic-trend"""
        raise NotImplementedError

    def get_transfer_total_traffic(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """获取投递总流量 - GET /v1/lts/transfer/total-traffic"""
        raise NotImplementedError

    # ==================== 7. 日志加工 ====================

    def start_process_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """启动加工任务 - POST /v1/lts/process/start"""
        raise NotImplementedError

    def stop_process_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """停止加工任务 - POST /v1/lts/process/stop"""
        raise NotImplementedError

    def delete_process_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """删除加工任务 - DELETE /v1/lts/process"""
        raise NotImplementedError

    def get_process_task_detail(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """获取加工任务详细信息 - GET /v1/lts/process/detail"""
        raise NotImplementedError

    def get_process_traffic_trend(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """获取加工流量趋势 - GET /v1/lts/process/traffic-trend"""
        raise NotImplementedError

    def get_process_total_traffic(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """获取加工总流量 - GET /v1/lts/process/total-traffic"""
        raise NotImplementedError

    # ==================== 8. 日志下载 ====================

    def get_download_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """获取指定下载任务信息 - GET /v1/lts/download/detail"""
        raise NotImplementedError

    def get_download_task_url(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """获取指定下载任务的下载链接 - GET /v1/lts/download/url"""
        raise NotImplementedError

    def delete_download_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """删除下载任务 - DELETE /v1/lts/download"""
        raise NotImplementedError

    # ==================== 9. 日志导入 ====================

    def delete_import_task(self, region_id: str, task_id: str) -> Dict[str, Any]:
        """删除导入任务 - DELETE /v1/lts/import"""
        raise NotImplementedError

    def list_import_tasks(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """导入任务列表查询 - GET /v1/lts/import/list"""
        raise NotImplementedError

    # ==================== 10. 消费组管理 ====================

    def create_consumer_group(self, region_id: str, group_name: str,
                               **kwargs) -> Dict[str, Any]:
        """创建消费组 - POST /v1/lts/consumer-group"""
        raise NotImplementedError

    def delete_consumer_group(self, region_id: str, group_id: str) -> Dict[str, Any]:
        """删除消费组 - DELETE /v1/lts/consumer-group"""
        raise NotImplementedError

    def update_consumer_group(self, region_id: str, group_id: str,
                               **kwargs) -> Dict[str, Any]:
        """更新消费组 - PUT /v1/lts/consumer-group"""
        raise NotImplementedError

    def list_consumer_groups(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """消费组查询列表 - GET /v1/lts/consumer-group/list"""
        raise NotImplementedError

    # ==================== 11. 告警管理 ====================

    def create_alarm_rule(self, region_id: str, rule_config: Dict) -> Dict[str, Any]:
        """创建告警规则 - POST /v1/lts/alarm"""
        raise NotImplementedError

    def delete_alarm_rule(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """删除指定告警规则 - DELETE /v1/lts/alarm"""
        raise NotImplementedError

    def update_alarm_rule(self, region_id: str, rule_id: str,
                           rule_config: Dict) -> Dict[str, Any]:
        """更新指定告警规则 - PUT /v1/lts/alarm"""
        raise NotImplementedError

    def get_alarm_rule(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """获取指定告警规则 - GET /v1/lts/alarm/detail"""
        raise NotImplementedError

    def list_alarm_rules(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """获取告警规则列表 - GET /v1/lts/alarm/list"""
        raise NotImplementedError

    def enable_alarm_rule(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """开启指定告警规则 - POST /v1/lts/alarm/enable"""
        raise NotImplementedError

    def disable_alarm_rule(self, region_id: str, rule_id: str) -> Dict[str, Any]:
        """停用指定告警规则 - POST /v1/lts/alarm/disable"""
        raise NotImplementedError

    def rename_alarm_rule(self, region_id: str, rule_id: str,
                           new_name: str) -> Dict[str, Any]:
        """重命名告警规则 - PUT /v1/lts/alarm/rename"""
        raise NotImplementedError

    def batch_enable_alarm_rules(self, region_id: str, rule_ids: List[str]) -> Dict[str, Any]:
        """批量启动告警规则 - POST /v1/lts/alarm/batch-enable"""
        raise NotImplementedError

    def batch_disable_alarm_rules(self, region_id: str, rule_ids: List[str]) -> Dict[str, Any]:
        """批量停止告警规则 - POST /v1/lts/alarm/batch-disable"""
        raise NotImplementedError

    def batch_delete_alarm_rules(self, region_id: str, rule_ids: List[str]) -> Dict[str, Any]:
        """批量删除告警规则 - POST /v1/lts/alarm/batch-delete"""
        raise NotImplementedError

    def get_alarm_template_variables(self, region_id: str) -> Dict[str, Any]:
        """获取告警模板变量 - GET /v1/lts/alarm/template-variables"""
        raise NotImplementedError

    def check_alarm_name_available(self, region_id: str, rule_name: str) -> Dict[str, Any]:
        """检查告警规则名称是否可用 - GET /v1/lts/alarm/name-available"""
        raise NotImplementedError

    def update_alarm_trigger(self, region_id: str, rule_id: str,
                              trigger_config: Dict) -> Dict[str, Any]:
        """更新触发条件 - PUT /v1/lts/alarm/trigger"""
        raise NotImplementedError

    def update_alarm_notification(self, region_id: str, rule_id: str,
                                   notification_config: Dict) -> Dict[str, Any]:
        """更新通知策略 - PUT /v1/lts/alarm/notification"""
        raise NotImplementedError

    def update_alarm_check_frequency(self, region_id: str, rule_id: str,
                                      frequency: int) -> Dict[str, Any]:
        """更新检查频率 - PUT /v1/lts/alarm/check-frequency"""
        raise NotImplementedError

    # ==================== 12. 仪表盘管理 ====================

    def create_dashboard(self, region_id: str, dashboard_config: Dict) -> Dict[str, Any]:
        """创建仪表盘 - POST /v1/lts/dashboard"""
        raise NotImplementedError

    def delete_dashboard(self, region_id: str, dashboard_id: str) -> Dict[str, Any]:
        """删除仪表盘 - DELETE /v1/lts/dashboard"""
        raise NotImplementedError

    def list_dashboards(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """仪表盘列表 - GET /v1/lts/dashboard/list"""
        raise NotImplementedError

    def get_dashboard_code(self, region_id: str, dashboard_id: str) -> Dict[str, Any]:
        """获取仪表盘编码 - GET /v1/lts/dashboard/code"""
        raise NotImplementedError

    def get_dashboard_by_name(self, region_id: str, dashboard_name: str) -> Dict[str, Any]:
        """根据名称查询仪表盘 - GET /v1/lts/dashboard/by-name"""
        raise NotImplementedError

    def check_dashboard_exists(self, region_id: str, dashboard_name: str) -> Dict[str, Any]:
        """检查仪表盘是否存在 - GET /v1/lts/dashboard/exists"""
        raise NotImplementedError

    def rename_dashboard(self, region_id: str, dashboard_id: str,
                          new_name: str) -> Dict[str, Any]:
        """重命名仪表盘 - PUT /v1/lts/dashboard/rename"""
        raise NotImplementedError

    def update_dashboard_description(self, region_id: str, dashboard_id: str,
                                      description: str) -> Dict[str, Any]:
        """更新仪表盘描述 - PUT /v1/lts/dashboard/description"""
        raise NotImplementedError

    def get_dashboard_description(self, region_id: str, dashboard_id: str) -> Dict[str, Any]:
        """获取仪表盘描述 - GET /v1/lts/dashboard/description"""
        raise NotImplementedError

    def list_dashboard_subscriptions_page(self, region_id: str, page_no: int = 1,
                                           page_size: int = 10) -> Dict[str, Any]:
        """分页获取订阅 - GET /v1/lts/dashboard/subscription/page"""
        raise NotImplementedError

    def list_dashboard_subscriptions(self, region_id: str) -> Dict[str, Any]:
        """列取仪表盘订阅 - GET /v1/lts/dashboard/subscription/list"""
        raise NotImplementedError

    def list_dashboard_subscribers(self, region_id: str, dashboard_id: str) -> Dict[str, Any]:
        """列取订阅指定仪表盘的联系人 - GET /v1/lts/dashboard/subscribers"""
        raise NotImplementedError

    def delete_dashboard_subscription(self, region_id: str, subscription_id: str) -> Dict[str, Any]:
        """删除仪表盘订阅 - DELETE /v1/lts/dashboard/subscription"""
        raise NotImplementedError

    def update_dashboard_subscription_name(self, region_id: str, subscription_id: str,
                                            new_name: str) -> Dict[str, Any]:
        """更新仪表盘订阅名称 - PUT /v1/lts/dashboard/subscription/name"""
        raise NotImplementedError

    # ==================== 13. 快速查询管理 ====================

    def create_quick_query(self, region_id: str, query_config: Dict) -> Dict[str, Any]:
        """创建一个快速查询 - POST /v1/lts/quick-query"""
        raise NotImplementedError

    def delete_quick_query(self, region_id: str, query_id: str) -> Dict[str, Any]:
        """删除快速查询 - DELETE /v1/lts/quick-query"""
        raise NotImplementedError

    def update_quick_query(self, region_id: str, query_id: str,
                            query_config: Dict) -> Dict[str, Any]:
        """更新快速查询 - PUT /v1/lts/quick-query"""
        raise NotImplementedError

    def get_quick_query(self, region_id: str, query_id: str) -> Dict[str, Any]:
        """获取指定的快速查询 - GET /v1/lts/quick-query/detail"""
        raise NotImplementedError

    def list_quick_queries(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """查询快速查询列表 - GET /v1/lts/quick-query/list"""
        raise NotImplementedError

    def get_quick_query_by_name(self, region_id: str, query_name: str) -> Dict[str, Any]:
        """根据名称查询快速查询 - GET /v1/lts/quick-query/by-name"""
        raise NotImplementedError

    def check_quick_query_exists(self, region_id: str, query_name: str) -> Dict[str, Any]:
        """检查快速查询是否存在 - GET /v1/lts/quick-query/exists"""
        raise NotImplementedError

    def rename_quick_query(self, region_id: str, query_id: str,
                            new_name: str) -> Dict[str, Any]:
        """重命名快速查询 - PUT /v1/lts/quick-query/rename"""
        raise NotImplementedError

    # ==================== 14. 标签管理 ====================

    def list_resource_tags(self, region_id: str, resource_type: str,
                            resource_id: str) -> Dict[str, Any]:
        """列出所查询资源的标签列表 - GET /v1/lts/tag/list"""
        raise NotImplementedError

    def bind_resource_tags(self, region_id: str, resource_type: str,
                            resource_id: str, tags: List[Dict]) -> Dict[str, Any]:
        """为指定资源绑定标签 - POST /v1/lts/tag/bind"""
        raise NotImplementedError

    def unbind_resource_tags(self, region_id: str, resource_type: str,
                              resource_id: str, tag_keys: List[str]) -> Dict[str, Any]:
        """为指定资源解绑标签 - POST /v1/lts/tag/unbind"""
        raise NotImplementedError

    # ==================== 15. 用量管理 ====================

    def get_read_write_usage_trend(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """获取读写用量趋势 - GET /v1/lts/usage/read-write-trend"""
        raise NotImplementedError

    def get_storage_usage_trend(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """获取存储用量趋势 - GET /v1/lts/usage/storage-trend"""
        raise NotImplementedError

    def get_read_write_total_usage(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """获取读写总用量 - GET /v1/lts/usage/read-write-total"""
        raise NotImplementedError

    def get_storage_total_usage(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """获取存储总用量 - GET /v1/lts/usage/storage-total"""
        raise NotImplementedError

    # ==================== 16. 服务开通与授权管理 ====================

    def open_lts_service(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """云日志服务开通 - POST /v1/lts/service/open"""
        raise NotImplementedError

    def check_instance_license(self, region_id: str) -> Dict[str, Any]:
        """检查实例License - GET /v1/lts/service/license"""
        raise NotImplementedError

    def get_instance_open_status(self, region_id: str) -> Dict[str, Any]:
        """获取实例的开通状态 - GET /v1/lts/service/status"""
        raise NotImplementedError

    def create_product_agency(self, region_id: str, **kwargs) -> Dict[str, Any]:
        """创建产品委托授权 - POST /v1/lts/service/agency"""
        raise NotImplementedError

    def check_product_agency_created(self, region_id: str) -> Dict[str, Any]:
        """检查产品委托授权是否创建 - GET /v1/lts/service/agency-status"""
        raise NotImplementedError
