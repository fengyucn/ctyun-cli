"""
镜像管理服务 (IMS) API客户端
"""

import json
import logging
from typing import Any, Dict, Optional

from auth.eop_signature import CTYUNEOPAuth

logger = logging.getLogger('ctyun_cli')


class IMSClient:
    """镜像管理服务API客户端"""

    def __init__(self, client):
        self.base_endpoint = 'ctimage-global.ctapi.ctyun.cn'
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
        import urllib.parse
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

    # ========== 查询可以使用的镜像资源 ==========

    def list_available_images(self, region_id: str,
                              az_name: Optional[str] = None,
                              cwai_type: Optional[str] = None,
                              flavor_name: Optional[str] = None,
                              image_name: Optional[str] = None,
                              image_scene: Optional[str] = None,
                              image_status: Optional[str] = None,
                              image_subcategory: Optional[str] = None,
                              image_type: Optional[str] = None,
                              image_visibility_code: Optional[int] = None,
                              os_type_code: Optional[int] = None,
                              page_no: Optional[int] = None,
                              page_size: Optional[int] = None,
                              project_id: Optional[str] = None,
                              query_content: Optional[str] = None) -> Dict[str, Any]:
        """
        查询可以使用的镜像资源 (API ID: 4763)
        GET /v4/image/list
        """
        logger.info(f"查询可以使用的镜像资源: regionId={region_id}")
        try:
            url = f'https://{self.base_endpoint}/v4/image/list'
            extra_headers = self._make_extra_headers(region_id=region_id)

            query_params: Dict[str, Any] = {'regionID': region_id}
            if az_name:
                query_params['azName'] = az_name
            if cwai_type:
                query_params['cwaiType'] = cwai_type
            if flavor_name:
                query_params['flavorName'] = flavor_name
            if image_name:
                query_params['imageName'] = image_name
            if image_scene:
                query_params['imageScene'] = image_scene
            if image_status:
                query_params['imageStatus'] = image_status
            if image_subcategory:
                query_params['imageSubcategory'] = image_subcategory
            if image_type:
                query_params['imageType'] = image_type
            if image_visibility_code is not None:
                query_params['imageVisibilityCode'] = image_visibility_code
            if os_type_code is not None:
                query_params['osTypeCode'] = os_type_code
            if page_no is not None:
                query_params['pageNo'] = page_no
            if page_size is not None:
                query_params['pageSize'] = page_size
            if project_id:
                query_params['projectID'] = project_id
            if query_content:
                query_params['queryContent'] = query_content

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params,
                body='', extra_headers=extra_headers
            )
            full_url = self._build_get_url(url, query_params)
            self._log_request(full_url, 'GET', headers=headers)
            response = self.client.session.get(full_url, headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"查询可以使用的镜像资源失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))

    # ========== 查询镜像详细信息 ==========

    def get_image_detail(self, region_id: str,
                         image_id: str,
                         error_free: Optional[bool] = None) -> Dict[str, Any]:
        """
        查询镜像详细信息 (API ID: 4764)
        GET /v4/image/detail
        """
        logger.info(f"查询镜像详细信息: regionId={region_id}, imageId={image_id}")
        try:
            url = f'https://{self.base_endpoint}/v4/image/detail'
            extra_headers = self._make_extra_headers(region_id=region_id)

            query_params: Dict[str, Any] = {
                'imageID': image_id,
                'regionID': region_id
            }
            if error_free is not None:
                query_params['errorFree'] = str(error_free).lower()

            headers = self.eop_auth.sign_request(
                method='GET', url=url, query_params=query_params,
                body='', extra_headers=extra_headers
            )
            full_url = self._build_get_url(url, query_params)
            self._log_request(full_url, 'GET', headers=headers)
            response = self.client.session.get(full_url, headers=headers, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"查询镜像详细信息失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return self._create_error_response(str(e))
