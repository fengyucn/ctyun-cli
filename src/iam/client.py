"""
天翼云统一身份认证(IAM)服务客户端
提供企业项目查询功能
"""

from typing import Dict, Any, Optional
import json
from core import CTYUNClient
from auth.eop_signature import CTYUNEOPAuth
from utils import logger


class IAMClient:
    """天翼云统一身份认证(IAM)服务客户端"""

    def __init__(self, client: CTYUNClient):
        """
        初始化IAM服务客户端

        Args:
            client: 天翼云API客户端
        """
        self.client = client
        self.service = 'iam'
        self.base_endpoint = 'ctiam-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

    def list_enterprise_projects(
            self,
            account_id: str,
            current_page: int = 1,
            page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业项目列表

        Args:
            account_id: 账号ID
            current_page: 当前页，默认1
            page_size: 每页显示条数，默认10

        Returns:
            企业项目列表
        """
        logger.info(f"查询企业项目列表: accountId={account_id}, page={current_page}, size={page_size}")

        try:
            url = f"https://{self.base_endpoint}/v1/project/getEpPageList"

            body_data = {
                'accountId': account_id,
                'currentPage': current_page,
                'pageSize': page_size
            }
            body = json.dumps(body_data)

            # IAM API需要在请求头中传递账号ID
            extra_headers = {
                'accountId': account_id
            }

            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers=extra_headers
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            logger.debug(f"请求头: {headers}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30,
                verify=False
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'statusCode': response.status_code,
                    'error': f'HTTP_{response.status_code}',
                    'message': response.text
                }

            result = response.json()
            return result

        except Exception as e:
            logger.error(f"查询企业项目列表失败: {str(e)}")
            logger.debug("", exc_info=True)
            return {
                'statusCode': 500,
                'error': 'Exception',
                'message': str(e)
            }

    def get_enterprise_project(self, project_id: str) -> Dict[str, Any]:
        """
        查询企业项目详情

        Args:
            project_id: 企业项目ID

        Returns:
            企业项目详情
        """
        logger.info(f"查询企业项目详情: projectId={project_id}")

        try:
            url = f"https://{self.base_endpoint}/v1/project/getEnterpriseProjectById"

            query_params = {
                'id': project_id
            }

            # 需要通过账号ID
            extra_headers = {
                'accountId': self.client.access_key
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body=None,
                extra_headers=extra_headers
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"查询参数: {query_params}")
            logger.debug(f"请求头: {headers}")

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30,
                verify=False
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'statusCode': response.status_code,
                    'error': f'HTTP_{response.status_code}',
                    'message': response.text
                }

            result = response.json()
            return result

        except Exception as e:
            logger.error(f"查询企业项目详情失败: {str(e)}")
            logger.debug("", exc_info=True)
            return {
                'statusCode': 500,
                'error': 'Exception',
                'message': str(e)
            }

    def list_resources(
            self,
            project_set_id: str,
            page_num: int = 1,
            page_size: int = 10) -> Dict[str, Any]:
        """
        分页查询资源信息

        Args:
            project_set_id: 企业项目id
            page_num: 页码，默认1
            page_size: 每页条数，默认10

        Returns:
            资源信息列表
        """
        logger.info(f"分页查询资源信息: projectSetId={project_set_id}, pageNum={page_num}, pageSize={page_size}")

        try:
            url = f"https://{self.base_endpoint}/v1/resource/getResourcePageList"

            body_data = {
                'projectSetId': project_set_id,
                'pageNum': page_num,
                'pageSize': page_size
            }
            body = json.dumps(body_data)

            # IAM API需要在请求头中传递账号ID
            extra_headers = {
                'accountId': self.client.access_key
            }

            headers = self.eop_auth.sign_request(
                method='POST',
                url=url,
                query_params=None,
                body=body,
                extra_headers=extra_headers
            )

            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求体: {body}")
            logger.debug(f"请求头: {headers}")

            response = self.client.session.post(
                url,
                data=body,
                headers=headers,
                timeout=30,
                verify=False
            )

            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")

            if response.status_code != 200:
                logger.error(f"API调用失败 (HTTP {response.status_code}): {response.text}")
                return {
                    'statusCode': response.status_code,
                    'error': f'HTTP_{response.status_code}',
                    'message': response.text
                }

            result = response.json()
            return result

        except Exception as e:
            logger.error(f"分页查询资源信息失败: {str(e)}")
            logger.debug("", exc_info=True)
            return {
                'statusCode': 500,
                'error': 'Exception',
                'message': str(e)
            }
