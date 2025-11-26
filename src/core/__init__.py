"""
天翼云API核心客户端
提供统一的API请求接口
"""

import json
import time
from typing import Dict, Any, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from auth.signature import CTYUNAuth
from config import config
from utils.helpers import logger


class CTYUNClient:
    """天翼云API客户端"""

    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None,
                 region: Optional[str] = None, endpoint: Optional[str] = None,
                 profile: str = 'default'):
        """
        初始化API客户端

        Args:
            access_key: 访问密钥
            secret_key: 密钥
            region: 区域
            endpoint: API端点
            profile: 配置文件名称
        """
        # 从参数或配置文件获取认证信息
        if not all([access_key, secret_key]):
            credentials = config.get_credentials(profile)
            access_key = access_key or credentials['access_key']
            secret_key = secret_key or credentials['secret_key']
            region = region or credentials['region']
            endpoint = endpoint or credentials['endpoint']

        if not all([access_key, secret_key]):
            raise ValueError("缺少认证信息，请设置access_key和secret_key")

        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region or 'cn-north-1'
        self.endpoint = endpoint or 'https://api.ctyun.cn'
        self.profile = profile

        # 初始化认证器
        self.auth = CTYUNAuth(access_key, secret_key)

        # 创建会话
        self.session = requests.Session()
        self._setup_session()

        # API版本
        self.api_version = 'v1'

        logger.info(f"初始化天翼云客户端: region={self.region}, endpoint={self.endpoint}")

    def _setup_session(self) -> None:
        """设置请求会话"""
        # 设置重试策略
        retry_strategy = Retry(
            total=config.get_retry_count(),
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'ctyun-cli/1.0.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _build_url(self, service: str, resource: str) -> str:
        """
        构建API URL

        Args:
            service: 服务名称
            resource: 资源路径

        Returns:
            完整的API URL
        """
        return f"{self.endpoint}/{self.api_version}/{service}/{resource}"

    def _make_request(self, method: str, url: str, params: Optional[Dict[str, Any]] = None,
                     data: Optional[Union[Dict[str, Any], str]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     sign: bool = True) -> requests.Response:
        """
        发送HTTP请求

        Args:
            method: HTTP方法
            url: 请求URL
            params: 查询参数
            data: 请求数据
            headers: 请求头
            sign: 是否需要签名

        Returns:
            响应对象

        Raises:
            CTYUNAPIError: API请求失败
        """
        if headers is None:
            headers = {}

        # 准备请求体
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)

        # 添加签名头
        if sign:
            uri = url.replace(self.endpoint, '')
            auth_headers = self.auth.sign_request(
                method=method,
                uri=uri,
                params=params or {},
                headers=headers,
                body=data or ''
            )
            headers.update(auth_headers)
        else:
            # 简单的Bearer Token认证
            headers['Authorization'] = self.auth.get_bearer_token()

        logger.debug(f"发送请求: {method} {url}")
        logger.debug(f"请求头: {headers}")
        if data:
            logger.debug(f"请求体: {data}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
                timeout=config.get_timeout()
            )

            # 记录响应信息
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")

            # 检查响应状态
            if not response.ok:
                self._handle_error(response)

            return response

        except requests.exceptions.Timeout as e:
            raise CTYUNAPIError(f"请求超时: {e}")
        except requests.exceptions.ConnectionError as e:
            raise CTYUNAPIError(f"连接错误: {e}")
        except requests.exceptions.RequestException as e:
            raise CTYUNAPIError(f"请求失败: {e}")

    def _handle_error(self, response: requests.Response) -> None:
        """
        处理API错误响应

        Args:
            response: 错误响应对象

        Raises:
            CTYUNAPIError: API错误
        """
        try:
            error_data = response.json()
            error_code = error_data.get('code', 'UNKNOWN')
            error_message = error_data.get('message', '未知错误')
            request_id = error_data.get('requestId', '')
        except (ValueError, json.JSONDecodeError):
            error_code = 'HTTP_ERROR'
            error_message = response.text or 'HTTP错误'
            request_id = ''

        error = CTYUNAPIError(
            message=error_message,
            code=error_code,
            status_code=response.status_code,
            request_id=request_id
        )
        logger.error(f"API错误: {error}")
        raise error

    def get(self, service: str, resource: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        发送GET请求

        Args:
            service: 服务名称
            resource: 资源路径
            params: 查询参数
            headers: 请求头

        Returns:
            响应数据
        """
        url = self._build_url(service, resource)
        response = self._make_request('GET', url, params=params, headers=headers)
        return response.json()

    def post(self, service: str, resource: str, data: Optional[Dict[str, Any]] = None,
             params: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        发送POST请求

        Args:
            service: 服务名称
            resource: 资源路径
            data: 请求数据
            params: 查询参数
            headers: 请求头

        Returns:
            响应数据
        """
        url = self._build_url(service, resource)
        response = self._make_request('POST', url, data=data, params=params, headers=headers)
        return response.json()

    def put(self, service: str, resource: str, data: Optional[Dict[str, Any]] = None,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        发送PUT请求

        Args:
            service: 服务名称
            resource: 资源路径
            data: 请求数据
            params: 查询参数
            headers: 请求头

        Returns:
            响应数据
        """
        url = self._build_url(service, resource)
        response = self._make_request('PUT', url, data=data, params=params, headers=headers)
        return response.json()

    def delete(self, service: str, resource: str, params: Optional[Dict[str, Any]] = None,
               headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        发送DELETE请求

        Args:
            service: 服务名称
            resource: 资源路径
            params: 查询参数
            headers: 请求头

        Returns:
            响应数据
        """
        url = self._build_url(service, resource)
        response = self._make_request('DELETE', url, params=params, headers=headers)
        return response.json()

    def list_resources(self, service: str, resource: str,
                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        列出资源

        Args:
            service: 服务名称
            resource: 资源路径
            params: 查询参数

        Returns:
            资源列表
        """
        return self.get(service, resource, params=params)

    def get_resource(self, service: str, resource_id: str,
                     params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取单个资源

        Args:
            service: 服务名称
            resource_id: 资源ID
            params: 查询参数

        Returns:
            资源详情
        """
        return self.get(service, resource_id, params=params)

    def create_resource(self, service: str, resource: str,
                       data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建资源

        Args:
            service: 服务名称
            resource: 资源路径
            data: 创建数据

        Returns:
            创建结果
        """
        return self.post(service, resource, data=data)

    def update_resource(self, service: str, resource_id: str,
                       data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新资源

        Args:
            service: 服务名称
            resource_id: 资源ID
            data: 更新数据

        Returns:
            更新结果
        """
        return self.put(service, resource_id, data=data)

    def delete_resource(self, service: str, resource_id: str) -> Dict[str, Any]:
        """
        删除资源

        Args:
            service: 服务名称
            resource_id: 资源ID

        Returns:
            删除结果
        """
        return self.delete(service, resource_id)

    def close(self) -> None:
        """关闭客户端会话"""
        if self.session:
            self.session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


class CTYUNAPIError(Exception):
    """天翼云API错误类"""

    def __init__(self, message: str, code: str = 'UNKNOWN',
                 status_code: int = 0, request_id: str = ''):
        """
        初始化错误

        Args:
            message: 错误消息
            code: 错误代码
            status_code: HTTP状态码
            request_id: 请求ID
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.request_id = request_id

    def __str__(self) -> str:
        """返回错误信息字符串"""
        return f"[{self.code}] {self.message} (HTTP {self.status_code})"

    def __repr__(self) -> str:
        """返回错误的详细表示"""
        return (f"CTYUNAPIError(code='{self.code}', message='{self.message}', "
                f"status_code={self.status_code}, request_id='{self.request_id}')")