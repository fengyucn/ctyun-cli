"""
模型推理服务(AIServer) API客户端
"""

import json
from typing import Dict, List, Optional, Any
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class AIServerClient:
    """天翼云模型推理服务(AIServer)客户端"""

    def __init__(self, client: CTYUNClient):
        self.client = client
        self.base_endpoint = 'ctinfer-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
        self.timeout = 30

    def set_timeout(self, timeout: int):
        self.timeout = timeout

    def _create_error_response(self, status_code: int, response_text: str) -> Dict[str, Any]:
        return {
            "error": True,
            "status_code": status_code,
            "message": f"HTTP {status_code}: {response_text}",
            "response": response_text
        }

    def _post(self, path: str, body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """通用 POST 请求"""
        try:
            url = f'https://{self.base_endpoint}{path}'
            body_json = json.dumps(body)
            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=body_json, extra_headers={'Content-Type': 'application/json'}
            )
            response = self.client.session.post(
                url, data=body_json, headers=headers, timeout=self.timeout
            )
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"请求失败 ({path}): {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def _get(self, path: str, query_params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """通用 GET 请求"""
        try:
            url = f'https://{self.base_endpoint}{path}'
            params = {k: v for k, v in (query_params or {}).items() if v is not None}
            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=params,
                body='', extra_headers={}
            )
            response = self.client.session.get(
                url, params=params, headers=headers, timeout=self.timeout
            )
            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)
            return response.json()
        except Exception as e:
            logger.error(f"请求失败 ({path}): {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    # ========== 计费查询 ==========

    def billing_preset_models(self, product_type: str = None) -> Optional[Dict[str, Any]]:
        """计费查询预置模型列表"""
        params = {}
        if product_type:
            params['productType'] = product_type
        return self._get('/maas/modelService/billing/presetModelList', params)

    def billing_product_details(self, model_id: str) -> Optional[Dict[str, Any]]:
        """获取指定模型的售卖销售品信息"""
        return self._get('/maas/modelService/billing/productDetails', {'modelId': model_id})

    # ========== 订单管理 ==========

    def create_order(self, model_id: str, token_by_use: Dict = None,
                     token_quantities: List = None, tpm: Dict = None) -> Optional[Dict[str, Any]]:
        """创建订单"""
        body = {'modelId': model_id}
        if token_by_use is not None:
            body['tokenByUse'] = token_by_use
        if token_quantities is not None:
            body['tokenQuantities'] = token_quantities
        if tpm is not None:
            body['tpm'] = tpm
        return self._post('/maas/modelService/billing/createOrder', body)

    def page_query_orders(self, model_id: str = None, order_id: str = None,
                          page_num: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """分页查询订单"""
        body = {'pageNum': page_num, 'pageSize': page_size}
        if model_id:
            body['modelId'] = model_id
        if order_id:
            body['orderId'] = order_id
        return self._post('/maas/modelService/billing/userOrders', body)

    def unsubscribe_order(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """订单退订（单个）"""
        return self._post('/maas/modelService/billing/unsubscribe', {'resourceId': resource_id})

    # ========== 服务组管理 ==========

    def query_service_group(self, user_ids: List[str], model_id: str) -> Optional[Dict[str, Any]]:
        """查询服务组"""
        return self._post('/maas/modelService/monitor/appGroup', {
            'userIds': user_ids, 'modelId': model_id
        })

    def query_service_group_models(self, app_id: str) -> Optional[Dict[str, Any]]:
        """查询服务组的模型列表"""
        return self._get('/maas/modelService/serviceGroup/queryModel', {'appId': app_id})

    def add_or_update_service_group(self, name: str, public_model_id_list: List[str],
                                     app_id: str = None, description: str = None,
                                     expire_at_str: str = None) -> Optional[Dict[str, Any]]:
        """添加或更新服务组"""
        body = {'name': name, 'publicModelIdList': public_model_id_list}
        if app_id:
            body['appId'] = app_id
        if description:
            body['description'] = description
        if expire_at_str:
            body['expireAtStr'] = expire_at_str
        return self._post('/maas/modelService/serviceGroup/addOrUpdateServiceGroup', body)

    def delete_service_group(self, app_id: str) -> Optional[Dict[str, Any]]:
        """删除服务组"""
        return self._post('/maas/modelService/serviceGroup/deleteServiceGroup', {'appId': app_id})

    def public_and_my_models(self, user_ids: List[str]) -> Optional[Dict[str, Any]]:
        """查询预置模型和我的模型"""
        return self._post('/maas/modelService/monitor/publicAndMyModelList', {'userIds': user_ids})

    def list_child_accounts(self) -> Optional[Dict[str, Any]]:
        """根据主账号id获取系统可使用的子账号信息"""
        return self._get('/maas/modelService/account/listChildren')

    # ========== 服务监控 ==========

    def _monitor_report(self, path: str, user_ids: List[str], model_id: str,
                        start_time: str, end_time: str, type_: str,
                        application_id: str = None) -> Optional[Dict[str, Any]]:
        """监控数据报告通用方法"""
        body = {
            'userIds': user_ids, 'modelId': model_id,
            'startTime': start_time, 'endTime': end_time, 'type': type_
        }
        if application_id:
            body['applicationId'] = application_id
        return self._post(path, body)

    def report_call(self, user_ids: List[str], model_id: str,
                    start_time: str, end_time: str, type_: str,
                    application_id: str = None) -> Optional[Dict[str, Any]]:
        """模型调用次数"""
        return self._monitor_report('/maas/modelService/monitor/report/call',
                                    user_ids, model_id, start_time, end_time, type_, application_id)

    def report_fail(self, user_ids: List[str], model_id: str,
                    start_time: str, end_time: str, type_: str,
                    application_id: str = None) -> Optional[Dict[str, Any]]:
        """模型调用失败率"""
        return self._monitor_report('/maas/modelService/monitor/report/fail',
                                    user_ids, model_id, start_time, end_time, type_, application_id)

    def report_qps(self, user_ids: List[str], model_id: str,
                   start_time: str, end_time: str, type_: str,
                   application_id: str = None) -> Optional[Dict[str, Any]]:
        """模型调用QPS"""
        return self._monitor_report('/maas/modelService/monitor/report/qps',
                                    user_ids, model_id, start_time, end_time, type_, application_id)

    def report_average_response_time(self, user_ids: List[str], model_id: str,
                                      start_time: str, end_time: str, type_: str,
                                      application_id: str = None) -> Optional[Dict[str, Any]]:
        """模型调用平均响应时延"""
        return self._monitor_report('/maas/modelService/monitor/report/averageResponseTime',
                                    user_ids, model_id, start_time, end_time, type_, application_id)

    def report_first_token_latency(self, user_ids: List[str], model_id: str,
                                    start_time: str, end_time: str, type_: str,
                                    application_id: str = None) -> Optional[Dict[str, Any]]:
        """模型调用首token延迟"""
        return self._monitor_report('/maas/modelService/monitor/report/firstTokenLatency',
                                    user_ids, model_id, start_time, end_time, type_, application_id)

    def report_non_first_token_latency(self, user_ids: List[str], model_id: str,
                                        start_time: str, end_time: str, type_: str,
                                        application_id: str = None) -> Optional[Dict[str, Any]]:
        """模型调用非首token时延"""
        return self._monitor_report('/maas/modelService/monitor/report/nonFirstTokenLatency',
                                    user_ids, model_id, start_time, end_time, type_, application_id)

    def report_talk_time(self, user_ids: List[str], model_id: str,
                          start_time: str, end_time: str, type_: str,
                          application_id: str = None) -> Optional[Dict[str, Any]]:
        """模型调用整句Token时延"""
        return self._monitor_report('/maas/modelService/monitor/report/talkTime',
                                    user_ids, model_id, start_time, end_time, type_, application_id)

    def report_tokens_usage(self, user_ids: List[str], model_id: str,
                             start_time: str, end_time: str, type_: str,
                             application_id: str = None) -> Optional[Dict[str, Any]]:
        """查询模型服务Token调用量"""
        return self._monitor_report('/maas/modelService/monitor/report/tokensUsage',
                                    user_ids, model_id, start_time, end_time, type_, application_id)
