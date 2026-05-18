"""
云审计 (Cloud Audit) API客户端
终端节点: cloudaudit-global.ctapi.ctyun.cn
"""

import json
import uuid
import urllib.parse
import logging
from typing import Any, Dict, List, Optional

from auth.eop_signature import CTYUNEOPAuth

logger = logging.getLogger('ctyun_cli')


class AuditClient:
    """云审计API客户端"""

    def __init__(self, client):
        self.base_endpoint = 'cloudaudit-global.ctapi.ctyun.cn'
        self.client = client
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
        self.timeout = 30

    def _make_extra_headers(self, region_id: Optional[str] = None,
                            account_id: Optional[str] = None,
                            user_id: Optional[str] = None) -> Dict[str, str]:
        """构建额外的请求头"""
        headers = {}
        if region_id:
            headers['regionid'] = region_id
        if account_id:
            headers['accountid'] = account_id
        if user_id:
            headers['userid'] = user_id
        return headers

    def _create_error_response(self, message: str, status_code: int = 500) -> Dict[str, Any]:
        return {
            'statusCode': status_code,
            'message': message,
            'returnObj': None
        }

    def _log_request(self, url: str, method: str, body: Optional[str] = None,
                     headers: Optional[Dict] = None, query_params: Optional[Dict] = None):
        logger.debug(f"请求URL [{method}]: {url}")
        if query_params:
            logger.debug(f"查询参数: {query_params}")
        if body:
            logger.debug(f"请求体: {body}")
        if headers:
            safe_headers = {k: v for k, v in headers.items() if k.lower() != 'eop-authorization'}
            logger.debug(f"请求头: {safe_headers}")

    def _build_get_url(self, base_url: str, query_params: Optional[Dict[str, Any]] = None) -> str:
        """手动构造GET请求URL，避免requests对params编码与EOP签名不一致"""
        if not query_params:
            return base_url
        sorted_params = sorted(query_params.items())
        encoded = '&'.join(
            f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params
        )
        return f"{base_url}?{encoded}"

    def _handle_response(self, response) -> Dict[str, Any]:
        logger.debug(f"响应状态码: {response.status_code}")
        if response.status_code != 200:
            logger.warning(f"API调用失败 (HTTP {response.status_code}): {response.text}")
            return self._create_error_response(
                f'HTTP {response.status_code}', response.status_code
            )
        result = response.json()
        logger.debug(f"响应内容: {json.dumps(result, ensure_ascii=False)[:500]}")
        if result.get('statusCode') not in (0, '0', 800):
            logger.warning(f"API返回错误: {result.get('message', '未知错误')}")
        return result

    # ========== 资源池管理 ==========

    def get_available_regions(self, region_id: str,
                               account_id: str, user_id: str) -> Dict[str, Any]:
        """
        获取云审计支持的资源池列表 (API ID: 11799)
        POST /v2/region/available/getList
        """
        logger.info(f"获取云审计支持的资源池列表")
        try:
            url = f'https://{self.base_endpoint}/v2/region/available/getList'
            extra_headers = self._make_extra_headers(
                region_id=region_id, account_id=account_id, user_id=user_id
            )
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params=None,
                body='{}', extra_headers=extra_headers
            )
            self._log_request(url, 'POST', '{}', headers)
            response = self.client.session.post(url, data='{}', headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"获取资源池列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))

    # ========== 用户授权 & 服务状态 ==========

    def get_user_authority(self, region_id: str,
                            account_id: str, user_id: str) -> Dict[str, Any]:
        """
        获取用户授权的桶信息 (API ID: 11793)
        GET /v2/manager/user/authority
        """
        logger.info(f"获取用户授权的桶信息")
        try:
            url = f'https://{self.base_endpoint}/v2/manager/user/authority'
            extra_headers = self._make_extra_headers(
                region_id=region_id, account_id=account_id, user_id=user_id
            )
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=None,
                body='', extra_headers=extra_headers
            )
            response = self.client.session.get(url, headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"获取用户授权桶信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))

    def get_service_enable_status(self, region_id: str,
                                   account_id: str, user_id: str) -> Dict[str, Any]:
        """
        获取服务开通状态 (API ID: 11789)
        GET /v2/manager/user/enable
        """
        logger.info(f"获取服务开通状态")
        try:
            url = f'https://{self.base_endpoint}/v2/manager/user/enable'
            extra_headers = self._make_extra_headers(
                region_id=region_id, account_id=account_id, user_id=user_id
            )
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=None,
                body='', extra_headers=extra_headers
            )
            response = self.client.session.get(url, headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"获取服务开通状态失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))

    def get_storage_region_info(self, region_id: str,
                                 account_id: str, user_id: str) -> Dict[str, Any]:
        """
        获取操作事件存储的资源池信息 (API ID: 11800)
        POST /v2/region/storage/getInfo
        """
        logger.info(f"获取操作事件存储的资源池信息")
        try:
            url = f'https://{self.base_endpoint}/v2/region/storage/getInfo'
            extra_headers = self._make_extra_headers(
                region_id=region_id, account_id=account_id, user_id=user_id
            )
            body = '{}'
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params=None,
                body=body, extra_headers=extra_headers
            )
            response = self.client.session.post(url, data=body, headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"获取事件存储资源池信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))

    # ========== 事件查询 ==========

    def list_events(self, region_id: str, page_number: int, page_size: int,
                    event_act_type: Optional[int] = None,
                    time_label: Optional[str] = None,
                    from_time: Optional[str] = None,
                    to_time: Optional[str] = None,
                    event_level: Optional[int] = None,
                    user_id: Optional[str] = None,
                    src_service_type: Optional[str] = None,
                    src_prod_type_name: Optional[str] = None,
                    filter_key: Optional[str] = None,
                    filter_value: Optional[str] = None) -> Dict[str, Any]:
        """
        查询事件列表 (API ID: 11791)
        GET /v2/manager/event/list
        """
        logger.info(f"查询事件列表: regionId={region_id}, page={page_number}, size={page_size}")
        try:
            url = f'https://{self.base_endpoint}/v2/manager/event/list'
            extra_headers = self._make_extra_headers(region_id=region_id)

            query_params: Dict[str, Any] = {
                'pageNumber': page_number,
                'pageSize': page_size
            }
            if event_act_type is not None:
                query_params['eventActType'] = event_act_type
            if time_label:
                query_params['timeLabel'] = time_label
            if from_time:
                query_params['fromTime'] = from_time
            if to_time:
                query_params['toTime'] = to_time
            if event_level is not None:
                query_params['eventLevel'] = event_level
            if user_id:
                query_params['userId'] = user_id
            if src_service_type:
                query_params['srcServiceType'] = src_service_type
            if src_prod_type_name:
                query_params['srcProdTypeName'] = src_prod_type_name
            if filter_key and filter_value:
                query_params['filterKey'] = filter_key
                query_params['filterValue'] = filter_value

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params,
                body='', extra_headers=extra_headers
            )
            full_url = self._build_get_url(url, query_params)
            self._log_request(full_url, 'GET', headers=headers)
            response = self.client.session.get(full_url, headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"查询事件列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))

    def get_event_selection(self, region_id: str, account_id: str,
                             user_id: str, field_name: str) -> Dict[str, Any]:
        """
        查询筛选事件的条件列表 (API ID: 11790)
        GET /v2/manager/event/selection
        """
        logger.info(f"查询事件筛选条件: fieldName={field_name}")
        try:
            url = f'https://{self.base_endpoint}/v2/manager/event/selection'
            extra_headers = self._make_extra_headers(
                region_id=region_id, account_id=account_id, user_id=user_id
            )
            query_params = {'fieldName': field_name}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params,
                body='', extra_headers=extra_headers
            )
            full_url = self._build_get_url(url, query_params)
            self._log_request(full_url, 'GET', headers=headers)
            response = self.client.session.get(full_url, headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"查询事件筛选条件失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))

    # ========== 跟踪任务管理 ==========

    def get_audit_track(self, region_id: str, account_id: str,
                         user_id: str, task_name: str,
                         task_id: str) -> Dict[str, Any]:
        """
        查询跟踪任务详情 (API ID: 11798)
        POST /v2/manager/auditTrack/get
        """
        logger.info(f"查询跟踪任务详情: taskName={task_name}, taskId={task_id}")
        try:
            url = f'https://{self.base_endpoint}/v2/manager/auditTrack/get'
            extra_headers = self._make_extra_headers(
                region_id=region_id, account_id=account_id, user_id=user_id
            )
            body_data = {
                'taskName': task_name,
                'taskId': task_id
            }
            body = json.dumps(body_data)
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params=None,
                body=body, extra_headers=extra_headers
            )
            self._log_request(url, 'POST', body, headers)
            response = self.client.session.post(url, data=body, headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"查询跟踪任务详情失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))

    def list_audit_tracks(self, region_id: str, account_id: str,
                           user_id: str, page_number: int,
                           page_size: int) -> Dict[str, Any]:
        """
        查询跟踪任务列表 (API ID: 11797)
        POST /v2/manager/auditTrack/list
        """
        logger.info(f"查询跟踪任务列表: page={page_number}, size={page_size}")
        try:
            url = f'https://{self.base_endpoint}/v2/manager/auditTrack/list'
            extra_headers = self._make_extra_headers(
                region_id=region_id, account_id=account_id, user_id=user_id
            )
            body_data = {
                'pageNumber': page_number,
                'pageSize': page_size
            }
            body = json.dumps(body_data)
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params=None,
                body=body, extra_headers=extra_headers
            )
            self._log_request(url, 'POST', body, headers)
            response = self.client.session.post(url, data=body, headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"查询跟踪任务列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))
