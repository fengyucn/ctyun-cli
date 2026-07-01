"""
关系数据库MySQL版(RDS)管理模块 - OpenAPI
端点: rds2-global.ctapi.ctyun.cn
注意: RDS2 API 成功码为 0，teledb-dcp API 成功码为 200，header 中需传 regionId
"""

from typing import Dict, Any, Optional, List
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger
import json


class RDSClient:
    """关系数据库MySQL版客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.service = 'rds'
        self.base_endpoint = 'rds2-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def _post(self, path: str, region_id: str, body_data: Dict[str, Any],
              desc: str, project_id: Optional[str] = None,
              success_code: int = 0) -> Dict[str, Any]:
        """
        RDS POST 请求统一入口

        Args:
            path: API路径，如 /RDS2/v1/open-api/instance/instance-list
            region_id: 资源池ID (放入header)
            body_data: 请求体dict
            desc: 操作描述(用于日志)
            project_id: 企业项目ID (可选，放入header)
            success_code: 成功状态码 (RDS2=0, teledb-dcp=200)
        """
        url = f'https://{self.base_endpoint}{path}'
        body = json.dumps(body_data)

        extra_headers: Dict[str, str] = {'regionId': region_id}
        if project_id:
            extra_headers['project-id'] = project_id

        headers = self.eop_auth.sign_request(
            method='POST', url=url, query_params=None, body=body,
            extra_headers=extra_headers
        )

        try:
            response = self.client.session.post(
                url, data=body, headers=headers, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != success_code:
                error_code = data.get('error', 'UNKNOWN_ERROR')
                error_msg = data.get('message', '未知错误')
                raise Exception(f"RDS API错误 [{error_code}]: {error_msg}")

            logger.info(f"成功{desc}")
            return data
        except Exception as e:
            logger.error(f"{desc}失败: {str(e)}")
            raise

    def _get(self, path: str, region_id: str, query_params: Dict[str, Any],
             desc: str, success_code: int = 0) -> Dict[str, Any]:
        """RDS GET 请求统一入口"""
        url = f'https://{self.base_endpoint}{path}'
        extra_headers: Dict[str, str] = {'regionId': region_id}
        headers = self.eop_auth.sign_request(
            method='GET', url=url, query_params=query_params, body=None,
            extra_headers=extra_headers
        )
        try:
            response = self.client.session.get(
                url, params=query_params, headers=headers, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get('statusCode') != success_code:
                error_code = data.get('error', 'UNKNOWN_ERROR')
                error_msg = data.get('message', '未知错误')
                raise Exception(f"RDS API错误 [{error_code}]: {error_msg}")
            logger.info(f"成功{desc}")
            return data
        except Exception as e:
            logger.error(f"{desc}失败: {str(e)}")
            raise

    def list_instances(self, region_id: str, page_now: int = 1, page_size: int = 10,
                       prod_inst_name: Optional[str] = None,
                       res_db_engine: Optional[str] = None,
                       vip: Optional[str] = None,
                       project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询实例列表 - POST /RDS2/v1/open-api/instance/instance-list

        Args:
            region_id: 资源池ID
            page_now: 当前页，默认1
            page_size: 每页条数，默认10
            prod_inst_name: 实例名称(模糊查询)
            res_db_engine: 数据库引擎，如 "5.7" "8.0"
            vip: 连接IP
            project_id: 企业项目ID
        """
        logger.info(f"查询RDS实例列表: regionId={region_id}, pageNow={page_now}")

        body_data: Dict[str, Any] = {
            'pageNow': page_now,
            'pageSize': page_size,
        }
        if prod_inst_name:
            body_data['prodInstName'] = prod_inst_name
        if res_db_engine:
            body_data['resDbEngine'] = res_db_engine
        if vip:
            body_data['vip'] = vip

        return self._post(
            '/RDS2/v1/open-api/instance/instance-list',
            region_id, body_data, '查询RDS实例列表', project_id
        )

    def batch_label(self, region_id: str, action: str,
                    outer_prod_inst_ids: List[str],
                    labels: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        批量实例绑定解绑标签 - POST /RDS2/v2/open-api/tag/batch-label

        Args:
            region_id: 资源池ID
            action: 操作类型 bind(绑定) / unbind(解绑)
            outer_prod_inst_ids: 实例ID列表
            labels: 标签列表 [{'key': 'k1', 'value': 'v1'}, ...]
        """
        logger.info(f"批量{action}标签: {len(outer_prod_inst_ids)}个实例, {len(labels)}个标签")

        body_data = {
            'action': action,
            'outerProdInstIds': outer_prod_inst_ids,
            'labels': labels,
        }
        return self._post(
            '/RDS2/v2/open-api/tag/batch-label',
            region_id, body_data, f'批量{action}标签'
        )

    def batch_metric_data(self, region_id: str, prod_engine_name: str,
                          inst_ids: List[str], metrics_type: str,
                          period: int, start_time: int, end_time: int,
                          agg_func: str) -> Dict[str, Any]:
        """
        批量查询实例监控数据 - POST /teledb-dcp/v2/openapi/monitor/instMetricData/batch

        Args:
            region_id: 资源池ID
            prod_engine_name: 实例类型 Mysql / PostgreSQL
            inst_ids: 实例ID列表(最多20个)
            metrics_type: 监控指标名
            period: 周期 15/60/900/3600
            start_time: 开始时间戳(秒)
            end_time: 结束时间戳(秒)
            agg_func: 聚合函数 avg/max/min
        """
        logger.info(f"批量查询监控数据: {len(inst_ids)}个实例, 指标={metrics_type}, period={period}")

        body_data = {
            'prodEngineName': prod_engine_name,
            'instIds': inst_ids,
            'metricsType': metrics_type,
            'period': period,
            'startTime': start_time,
            'endTime': end_time,
            'aggFunc': agg_func,
        }
        return self._post(
            '/teledb-dcp/v2/openapi/monitor/instMetricData/batch',
            region_id, body_data, '批量查询监控数据', success_code=200
        )

    # ==================== 询价 API ====================

    def inquiry(self, region_id: str, project_id: str, bill_mode: str,
                prod_version: str, host_type: str, period: int, count: int,
                auto_renew_status: int, prod_id: int,
                mysql_node_info_list: List[Dict[str, Any]],
                vpc_id: Optional[str] = None, subnet_id: Optional[str] = None,
                security_group_id: Optional[str] = None,
                inst_id: Optional[str] = None,
                cpu_type: Optional[int] = None,
                os_type: Optional[int] = None,
                backup_storage_type: Optional[str] = None) -> Dict[str, Any]:
        """
        新建实例询价(v2) - POST /teledb-acceptor/v2/openapi/accept-order-info/inquiry
        成功码: 200
        """
        logger.info(f"新建实例询价: regionId={region_id}, prodVersion={prod_version}")
        body_data: Dict[str, Any] = {
            'billMode': bill_mode,
            'regionId': region_id,
            'prodVersion': prod_version,
            'hostType': host_type,
            'period': period,
            'count': count,
            'autoRenewStatus': auto_renew_status,
            'prodId': prod_id,
            'mysqlNodeInfoList': mysql_node_info_list,
        }
        for k, v in {'vpcId': vpc_id, 'subnetId': subnet_id,
                     'securityGroupId': security_group_id, 'instId': inst_id,
                     'cpuType': cpu_type, 'osType': os_type,
                     'backupStorageType': backup_storage_type}.items():
            if v is not None:
                body_data[k] = v
        return self._post(
            '/teledb-acceptor/v2/openapi/accept-order-info/inquiry',
            region_id, body_data, '新建实例询价', project_id, success_code=200
        )

    def inquiry_upgrade(self, region_id: str, project_id: str, inst_id: str,
                        node_type: Optional[str] = None, prod_id: Optional[str] = None,
                        disk_volume: Optional[str] = None,
                        prod_performance_spec: Optional[str] = None,
                        az_list: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        变更实例询价(v2) - POST /teledb-acceptor/v2/openapi/accept-order-info/inquiryForUpgrade
        成功码: 200
        """
        logger.info(f"变更实例询价: instId={inst_id}")
        body_data: Dict[str, Any] = {'instId': inst_id}
        for k, v in {'nodeType': node_type, 'prodId': prod_id,
                     'diskVolume': disk_volume,
                     'prodPerformanceSpec': prod_performance_spec,
                     'azList': az_list}.items():
            if v is not None:
                body_data[k] = v
        return self._post(
            '/teledb-acceptor/v2/openapi/accept-order-info/inquiryForUpgrade',
            region_id, body_data, '变更实例询价', project_id, success_code=200
        )

    def inquiry_renew(self, region_id: str, inst_id: str, month: int) -> Dict[str, Any]:
        """
        续费询价 - GET /teledb-acceptor/v1/openapi/accept-order-info/inquiryForRenewOrder
        注意: 此API响应结构为 {code:0, data:{...}} 而非 {statusCode:200, returnObj:{...}}
        为统一_display_price解析，将响应包装为 {statusCode:200, returnObj:{data:{...}}}
        """
        logger.info(f"续费询价: instId={inst_id}, month={month}")
        url = f'https://{self.base_endpoint}/teledb-acceptor/v1/openapi/accept-order-info/inquiryForRenewOrder'
        query_params = {'instId': inst_id, 'month': month}
        extra_headers = {'regionId': region_id}
        headers = self.eop_auth.sign_request(
            method='GET', url=url, query_params=query_params, body=None,
            extra_headers=extra_headers
        )
        try:
            response = self.client.session.get(
                url, params=query_params, headers=headers, timeout=30
            )
            response.raise_for_status()
            raw = response.json()
            if raw.get('code') != 0:
                error_code = raw.get('error', 'UNKNOWN_ERROR')
                error_msg = raw.get('message', '未知错误')
                raise Exception(f"RDS API错误 [{error_code}]: {error_msg}")
            # 标准化响应结构: {code, data} -> {statusCode:200, returnObj:{data}}
            logger.info(f"成功续费询价")
            return {
                'statusCode': 200,
                'message': raw.get('message', 'SUCCESS'),
                'returnObj': {'data': raw.get('data', {})},
            }
        except Exception as e:
            logger.error(f"续费询价失败: {str(e)}")
            raise

    # ==================== 标签查询 ====================

    def list_tag_resources(self, region_id: str, outer_prod_inst_id_list: str,
                           tag_vo_list: str = '') -> Dict[str, Any]:
        """查询标签列表 - GET /v1/open-api/tag/list-tag-resources"""
        logger.info(f"查询RDS标签列表: instIds={outer_prod_inst_id_list}")
        query_params = {'outerProdInstIdList': outer_prod_inst_id_list}
        if tag_vo_list:
            query_params['tagVOList'] = tag_vo_list
        return self._get(
            '/RDS2/v1/open-api/tag/list-tag-resources',
            region_id, query_params, '查询RDS标签列表'
        )

    def get_instance_labels(self, region_id: str, outer_prod_inst_id: str,
                            page_now: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """获取实例所绑定的标签 - GET /RDS2/v2/open-api/tag/label"""
        logger.info(f"获取实例标签: instId={outer_prod_inst_id}")
        query_params = {'outerProdInstId': outer_prod_inst_id, 'pageNow': page_now, 'pageSize': page_size}
        return self._get(
            '/RDS2/v2/open-api/tag/label',
            region_id, query_params, '获取实例标签'
        )

    def get_all_labels(self, region_id: str, page_now: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """获取用户的所有标签 - GET /RDS2/v2/open-api/tag/all-label"""
        logger.info(f"获取用户所有标签: regionId={region_id}")
        query_params = {'pageNow': page_now, 'pageSize': page_size}
        return self._get(
            '/RDS2/v2/open-api/tag/all-label',
            region_id, query_params, '获取用户所有标签'
        )
