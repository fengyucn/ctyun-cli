"""
服务器安全卫士(原生版)管理模块
端点: ctcsscn-global.ctapi.ctyun.cn
成功码: error == 'CTCSSCN_000000' (非 0/800/200)
"""

from typing import Dict, Any, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class CSSCNClient:
    """服务器安全卫士(原生版)客户端"""

    SUCCESS_CODE = 'CTCSSCN_000000'

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.service = 'csscn'
        self.base_endpoint = 'ctcsscn-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def _post(self, path: str, body_data: Dict[str, Any], desc: str) -> Dict[str, Any]:
        """
        安全卫士 POST 请求统一入口

        Args:
            path: API路径，如 /v1/host/all
            body_data: 请求体dict
            desc: 操作描述(用于日志)
        """
        url = f'https://{self.base_endpoint}{path}'
        body = json.dumps(body_data)

        headers = self.eop_auth.sign_request(
            method='POST', url=url, query_params=None, body=body,
            extra_headers={'Content-Type': 'application/json'}
        )

        try:
            response = self.client.session.post(
                url, data=body, headers=headers, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if data.get('error') != self.SUCCESS_CODE:
                error_code = data.get('error', 'UNKNOWN')
                error_msg = data.get('message', '未知错误')
                raise Exception(f"安全卫士API错误 [{error_code}]: {error_msg}")

            logger.info(f"成功{desc}")
            return data
        except Exception as e:
            logger.error(f"{desc}失败: {str(e)}")
            raise

    def _get(self, path: str, desc: str) -> Dict[str, Any]:
        """安全卫士 GET 请求统一入口"""
        url = f'https://{self.base_endpoint}{path}'
        headers = self.eop_auth.sign_request(
            method='GET', url=url, query_params=None, body=None,
            extra_headers={'Content-Type': 'application/json'}
        )
        try:
            response = self.client.session.get(
                url, headers=headers, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get('error') != self.SUCCESS_CODE:
                error_code = data.get('error', 'UNKNOWN')
                error_msg = data.get('message', '未知错误')
                raise Exception(f"安全卫士API错误 [{error_code}]: {error_msg}")
            logger.info(f"成功{desc}")
            return data
        except Exception as e:
            logger.error(f"{desc}失败: {str(e)}")
            raise

    def list_servers(self, current_page: int = 1, page_size: int = 10,
                     guard_status: Optional[int] = None,
                     agent_state: Optional[int] = None,
                     risk_level: Optional[int] = None,
                     param: Optional[str] = None,
                     param_type: Optional[int] = None,
                     quota_version: Optional[int] = None,
                     bg_group_id: Optional[str] = None,
                     server_status: Optional[int] = None,
                     agent_need_upgrade: Optional[int] = None) -> Dict[str, Any]:
        """
        查询服务器列表 - POST /v1/host/all

        Args:
            current_page: 当前页码
            page_size: 每页大小
            guard_status: 防护状态 1-防护中 4-未防护
            agent_state: agent状态 1-在线 2-离线
            risk_level: 风险状态 1-无风险 2-未知 3-风险
            param: 查询参数(配合param_type使用)
            param_type: 查询参数类型 1-实例名称 2-服务器IP 5-agentGuid 15-代理地址IP
            quota_version: 配额版本 1-基础版 2-企业版
            bg_group_id: 业务分组ID
            server_status: 服务器状态 4-已关机 5-运行中 40-其他
            agent_need_upgrade: agent是否需要升级 0-否 1-是
        """
        logger.info(f"查询服务器列表: page={current_page}, pageSize={page_size}")

        body_data: Dict[str, Any] = {
            'currentPage': current_page,
            'pageSize': page_size,
        }
        optional = {
            'guardStatus': guard_status, 'agentState': agent_state,
            'riskLevel': risk_level, 'param': param, 'paramType': param_type,
            'quotaVersion': quota_version, 'bgGroupId': bg_group_id,
            'serverStatus': server_status, 'agentNeedUpgrade': agent_need_upgrade,
        }
        for k, v in optional.items():
            if v is not None:
                body_data[k] = v

        return self._post('/v1/host/all', body_data, '查询服务器列表')

    # ==================== 总览统计 ====================

    def server_detail(self, agent_guid: str) -> Dict[str, Any]:
        """查询服务器详情 - GET /v1/host/detail/{agentGuid}"""
        logger.info(f"查询服务器详情: agentGuid={agent_guid}")
        return self._get(f'/v1/host/detail/{agent_guid}', '查询服务器详情')

    def untreated_risk_stats(self) -> Dict[str, Any]:
        """查询待处理风险统计数据 - GET /v1/index/untreated"""
        return self._get('/v1/index/untreated', '查询待处理风险统计数据')

    def server_total_stats(self) -> Dict[str, Any]:
        """查询服务器统计数据 - GET /v1/host/totalCount"""
        return self._get('/v1/host/totalCount', '查询服务器统计数据')

    def agent_guard_stats(self) -> Dict[str, Any]:
        """查询Agent防护状态统计数据 - GET /v1/index/status"""
        return self._get('/v1/index/status', '查询Agent防护状态统计')

    def agent_status_distribution(self) -> Dict[str, Any]:
        """查询Agent在线离线等状态分布数据 - GET /v1/index/agentStatus"""
        return self._get('/v1/index/agentStatus', '查询Agent状态分布')

    # ==================== 漏洞 ====================

    def vulnerability_stats(self) -> Dict[str, Any]:
        """查询漏洞统计数据 - POST /v1/vulnerability/statics"""
        return self._post('/v1/vulnerability/statics', {}, '查询漏洞统计数据')

    def host_vulnerability_list(self, agent_guid: str,
                                vul_type: list,
                                current_page: int = 1, page_size: int = 10,
                                title: Optional[str] = None,
                                cve: Optional[str] = None,
                                fix_level: Optional[str] = None,
                                handle_status: Optional[str] = None) -> Dict[str, Any]:
        """查询服务器漏洞列表 - POST /v1/host/vulList"""
        logger.info(f"查询服务器漏洞列表: agentGuid={agent_guid}")
        body_data: Dict[str, Any] = {
            'agentGuid': agent_guid, 'vulType': vul_type,
            'currentPage': current_page, 'pageSize': page_size,
        }
        for k, v in {'title': title, 'cve': cve,
                     'fixLevel': fix_level, 'handleStatus': handle_status}.items():
            if v is not None:
                body_data[k] = v
        return self._post('/v1/host/vulList', body_data, '查询服务器漏洞列表')

    # ==================== 告警 ====================

    def alarm_list(self, time_type: str, current_page: int = 1, page_size: int = 10,
                   severity_code: Optional[int] = None, status: Optional[int] = None,
                   attck_type: Optional[str] = None,
                   like_query_type: Optional[int] = None,
                   like_query_param: Optional[str] = None,
                   agent_guid: Optional[str] = None,
                   alarm_type: Optional[str] = None,
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None) -> Dict[str, Any]:
        """查询告警中心告警列表 - POST /v1/instrusion/event/list"""
        logger.info(f"查询告警列表: timeType={time_type}, page={current_page}")
        body_data: Dict[str, Any] = {
            'timeType': time_type,
            'currentPage': current_page,
            'pageSize': page_size,
        }
        for k, v in {'severityCode': severity_code, 'status': status,
                     'attckType': attck_type, 'likeQueryType': like_query_type,
                     'likeQueryParam': like_query_param, 'agentGuid': agent_guid,
                     'alarmType': alarm_type, 'startTime': start_time,
                     'endTime': end_time}.items():
            if v is not None:
                body_data[k] = v
        return self._post('/v1/instrusion/event/list', body_data, '查询告警列表')

    # ==================== 病毒 ====================

    def virus_list(self, os_type: int, time_type: str,
                   current_page: int = 1, page_size: int = 10,
                   param_type: Optional[int] = None,
                   param: Optional[str] = None,
                   status: Optional[int] = None,
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None) -> Dict[str, Any]:
        """查询病毒事件列表 - POST /v1/virus/list"""
        logger.info(f"查询病毒事件列表: osType={os_type}, timeType={time_type}")
        body_data: Dict[str, Any] = {
            'osType': os_type, 'timeType': time_type,
            'currentPage': current_page, 'pageSize': page_size,
        }
        for k, v in {'paramType': param_type, 'param': param,
                     'status': status, 'startTime': start_time,
                     'endTime': end_time}.items():
            if v is not None:
                body_data[k] = v
        return self._post('/v1/virus/list', body_data, '查询病毒事件列表')

    # ==================== 配额 ====================

    def quota_list(self, current_num: int = 1, page_size: int = 10,
                   quota_version: Optional[int] = None,
                   server_ip: Optional[str] = None,
                   cust_name: Optional[str] = None,
                   quota_status: Optional[int] = None,
                   quota_id: Optional[str] = None) -> Dict[str, Any]:
        """查询配额列表 - POST /v1/quota/quotaList/{currentNum}/{pageSize}"""
        logger.info(f"查询配额列表: page={current_num}, size={page_size}")
        body_data: Dict[str, Any] = {}
        for k, v in {'quotaId': quota_id, 'quotaVersion': quota_version,
                     'serverIp': server_ip, 'custName': cust_name,
                     'quotaStatus': quota_status}.items():
            if v is not None:
                body_data[k] = v
        return self._post(
            f'/v1/quota/quotaList/{current_num}/{page_size}',
            body_data, '查询配额列表'
        )
