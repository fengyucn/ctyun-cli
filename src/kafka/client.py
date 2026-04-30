"""
分布式消息服务Kafka API客户端
"""

from typing import Dict, List, Optional, Any
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class KafkaClient:
    """天翼云分布式消息服务Kafka客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化Kafka客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.base_endpoint = 'ctgkafka-global.ctapi.ctyun.cn'
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

    def inst_query(self, region_id: str, prod_inst_id: str = None, name: str = None,
                   exact_match_name: bool = None, status: int = None,
                   outer_project_id: str = None, page_num: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        查询Kafka实例

        Args:
            region_id: 资源池ID (header参数)
            prod_inst_id: 实例ID
            name: 实例名称
            exact_match_name: 是否精确匹配
            status: 实例状态
            outer_project_id: 企业项目ID
            page_num: 页码
            page_size: 每页大小

        Returns:
            Optional[Dict[str, Any]]: 实例列表
        """
        logger.info(f"查询Kafka实例: regionId={region_id}, name={name}")

        try:
            url = f'https://{self.base_endpoint}/v3/instances/query'

            query_params = {}
            if prod_inst_id:
                query_params['prodInstId'] = prod_inst_id
            if name:
                query_params['name'] = name
            if exact_match_name is not None:
                query_params['exactMatchName'] = 'true' if exact_match_name else 'false'
            if status is not None:
                query_params['status'] = str(status)
            if outer_project_id:
                query_params['outerProjectId'] = outer_project_id
            if page_num is not None:
                query_params['pageNum'] = str(page_num)
            if page_size is not None:
                query_params['pageSize'] = str(page_size)

            extra_headers = {'regionId': region_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params,
                body='', extra_headers=extra_headers
            )

            response = self.client.session.get(
                url, params=query_params, headers=headers, timeout=self.timeout
            )

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询Kafka实例失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def node_status(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """
        查看实例节点状态

        Args:
            region_id: 资源池ID
            prod_inst_id: 实例ID

        Returns:
            Optional[Dict[str, Any]]: 节点状态列表
        """
        logger.info(f"查看Kafka实例节点状态: regionId={region_id}, prodInstId={prod_inst_id}")

        try:
            url = f'https://{self.base_endpoint}/v3/instances/nodeStatus'

            query_params = {'prodInstId': prod_inst_id}
            extra_headers = {'regionId': region_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params,
                body='', extra_headers=extra_headers
            )

            response = self.client.session.get(
                url, params=query_params, headers=headers, timeout=self.timeout
            )

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查看节点状态失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def page_query_floatingips(self, region_id: str, page_num: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        查询弹性IP列表

        Args:
            region_id: 资源池ID
            page_num: 页码
            page_size: 每页大小

        Returns:
            Optional[Dict[str, Any]]: 弹性IP列表
        """
        logger.info(f"查询Kafka弹性IP列表: regionId={region_id}")

        try:
            url = f'https://{self.base_endpoint}/v3/instances/pageQueryFloatingips'

            query_params = {}
            if page_num is not None:
                query_params['pageNum'] = str(page_num)
            if page_size is not None:
                query_params['pageSize'] = str(page_size)

            extra_headers = {'regionId': region_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params,
                body='', extra_headers=extra_headers
            )

            response = self.client.session.get(
                url, params=query_params, headers=headers, timeout=self.timeout
            )

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"查询弹性IP列表失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}

    def get_instance_config(self, region_id: str, prod_inst_id: str) -> Optional[Dict[str, Any]]:
        """
        获取实例配置

        Args:
            region_id: 资源池ID
            prod_inst_id: 实例ID

        Returns:
            Optional[Dict[str, Any]]: 实例配置列表
        """
        logger.info(f"获取Kafka实例配置: regionId={region_id}, prodInstId={prod_inst_id}")

        try:
            url = f'https://{self.base_endpoint}/v3/instances/getInstanceConfig'

            query_params = {'prodInstId': prod_inst_id}
            extra_headers = {'regionId': region_id}

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params,
                body='', extra_headers=extra_headers
            )

            response = self.client.session.get(
                url, params=query_params, headers=headers, timeout=self.timeout
            )

            if response.status_code != 200:
                return self._create_error_response(response.status_code, response.text)

            return response.json()

        except Exception as e:
            logger.error(f"获取实例配置失败: {e}")
            return {"error": True, "message": f"请求异常: {str(e)}", "exception": str(e)}
