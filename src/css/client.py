"""
云搜索服务(CSS) API客户端
"""

import json
from typing import Dict, List, Optional, Any
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class CSSClient:
    """天翼云云搜索服务(CSS)客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化CSS客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.base_endpoint = 'ctcsx-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)
        self.timeout = 30

    def set_timeout(self, timeout: int):
        """
        设置请求超时时间

        Args:
            timeout: 超时时间（秒）
        """
        self.timeout = timeout

    def _create_error_response(self, status_code: int, response_text: str) -> Dict[str, Any]:
        """创建标准错误响应"""
        return {
            "error": True,
            "status_code": status_code,
            "message": f"HTTP {status_code}: {response_text}",
            "response": response_text
        }

    def select_instance_page(self, region_id: str, page_index: int = 1, page_size: int = 10,
                             cluster_name: str = None, cluster_type: int = None,
                             project_id: str = None, cluster_state_list: List[int] = None,
                             is_query_net: bool = None) -> Optional[Dict[str, Any]]:
        """
        查询实例列表信息

        Args:
            region_id: 资源池ID
            page_index: 当前页
            page_size: 每页大小
            cluster_name: 实例名称
            cluster_type: 实例类型 (1:OpenSearch 2:Elasticsearch)
            project_id: 企业项目编码
            cluster_state_list: 实例状态列表
            is_query_net: 是否查询公网地址

        Returns:
            Optional[Dict[str, Any]]: 实例列表
        """
        logger.info(f"查询CSS实例列表: regionId={region_id}, type={cluster_type}")

        try:
            url = f'https://{self.base_endpoint}/os/openapi/v1/cluster/selectInstancePage'

            request_body = {
                'regionId': region_id,
                'pageIndex': page_index,
                'pageSize': page_size,
            }
            if cluster_name:
                request_body['clusterName'] = cluster_name
            if cluster_type is not None:
                request_body['clusterType'] = cluster_type
            if project_id:
                request_body['projectId'] = project_id
            if cluster_state_list:
                request_body['clusterStateList'] = cluster_state_list
            if is_query_net is not None:
                request_body['isQueryNet'] = is_query_net

            extra_headers = {'Content-Type': 'application/json'}

            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=json.dumps(request_body), extra_headers=extra_headers
            )

            response = self.client.session.post(
                url, json=request_body, headers=headers, timeout=self.timeout
            )

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询CSS实例列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def get_cluster_by_id(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """
        查询实例详情

        Args:
            cluster_id: 实例ID

        Returns:
            Optional[Dict[str, Any]]: 实例详情
        """
        logger.info(f"查询CSS实例详情: clusterId={cluster_id}")

        try:
            url = f'https://{self.base_endpoint}/os/openapi/v1/cluster/getClusterById'

            query_params = {'clusterId': cluster_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params,
                body='', extra_headers={}
            )

            response = self.client.session.get(
                url, params=query_params, headers=headers, timeout=self.timeout
            )

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询CSS实例详情失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def select_logstash_page(self, region_id: str, page_index: int = 1, page_size: int = 10,
                             cluster_name: str = None, project_id: str = None,
                             cluster_state_list: List[int] = None) -> Optional[Dict[str, Any]]:
        """
        查询Logstash实例列表

        Args:
            region_id: 资源池ID
            page_index: 当前页
            page_size: 每页大小
            cluster_name: 实例名称
            project_id: 企业项目ID
            cluster_state_list: 实例状态列表

        Returns:
            Optional[Dict[str, Any]]: Logstash实例列表
        """
        logger.info(f"查询CSS Logstash实例列表: regionId={region_id}")

        try:
            url = f'https://{self.base_endpoint}/os/openapi/v1/cluster/selectLogstashInstancePage'

            request_body = {
                'regionId': region_id,
                'pageIndex': page_index,
                'pageSize': page_size,
            }
            if cluster_name:
                request_body['clusterName'] = cluster_name
            if project_id:
                request_body['projectId'] = project_id
            if cluster_state_list:
                request_body['clusterStateList'] = cluster_state_list

            extra_headers = {'Content-Type': 'application/json'}

            headers = self.eop_auth.sign_request(
                method='POST', url=url, query_params={},
                body=json.dumps(request_body), extra_headers=extra_headers
            )

            response = self.client.session.post(
                url, json=request_body, headers=headers, timeout=self.timeout
            )

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询CSS Logstash实例列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}
