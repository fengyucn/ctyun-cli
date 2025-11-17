"""
天翼云API签名认证模块
实现AK/SK签名认证机制
"""

import hashlib
import hmac
import time
import uuid
from urllib.parse import quote
from typing import Dict, Any


class CTYUNAuth:
    """天翼云API签名认证类"""

    def __init__(self, access_key: str, secret_key: str):
        """
        初始化认证器

        Args:
            access_key: 访问密钥
            secret_key: 密钥
        """
        self.access_key = access_key
        self.secret_key = secret_key

    def _create_string_to_sign(self, method: str, uri: str, params: Dict[str, Any],
                              headers: Dict[str, str], timestamp: str) -> str:
        """
        创建待签名字符串

        Args:
            method: HTTP方法
            uri: 请求URI
            params: 查询参数
            headers: 请求头
            timestamp: 时间戳

        Returns:
            待签名字符串
        """
        # 规范化URI
        canonical_uri = quote(uri, safe='/')

        # 规范化查询字符串
        canonical_query = self._canonicalize_query(params)

        # 规范化请求头
        canonical_headers, signed_headers = self._canonicalize_headers(headers)

        # 创建哈希载荷（如果有body）
        payload_hash = hashlib.sha256(''.encode()).hexdigest()

        # 构建待签名字符串
        string_to_sign = f"{method.upper()}\n{canonical_uri}\n{canonical_query}\n"
        string_to_sign += f"{canonical_headers}\n{signed_headers}\n{payload_hash}"

        return string_to_sign

    def _canonicalize_query(self, params: Dict[str, Any]) -> str:
        """
        规范化查询参数

        Args:
            params: 查询参数字典

        Returns:
            规范化的查询字符串
        """
        if not params:
            return ""

        # 对参数名进行编码和排序
        encoded_params = []
        for key in sorted(params.keys()):
            encoded_key = quote(str(key), safe='')
            encoded_value = quote(str(params[key]), safe='')
            encoded_params.append(f"{encoded_key}={encoded_value}")

        return "&".join(encoded_params)

    def _canonicalize_headers(self, headers: Dict[str, str]) -> tuple:
        """
        规范化请求头

        Args:
            headers: 请求头字典

        Returns:
            (规范化请求头字符串, 已签名头列表)
        """
        # 过滤和规范化请求头
        canonical_headers = {}
        signed_headers = []

        # 天翼云API要求包含的头
        required_headers = ['host', 'x-ctyun-date', 'x-ctyun-nonce']

        for key, value in headers.items():
            lower_key = key.lower().strip()
            if lower_key in required_headers or lower_key.startswith('x-ctyun-'):
                canonical_headers[lower_key] = value.strip()
                signed_headers.append(lower_key)

        # 排序已签名头
        signed_headers.sort()

        # 构建规范化请求头字符串
        header_lines = []
        for header in signed_headers:
            header_lines.append(f"{header}:{canonical_headers[header]}")

        canonical_headers_str = "\n".join(header_lines) + "\n"
        signed_headers_str = ";".join(signed_headers)

        return canonical_headers_str, signed_headers_str

    def sign_request(self, method: str, uri: str, params: Dict[str, Any] = None,
                    headers: Dict[str, str] = None, body: str = None) -> Dict[str, str]:
        """
        为请求添加签名

        Args:
            method: HTTP方法
            uri: 请求URI
            params: 查询参数
            headers: 请求头
            body: 请求体

        Returns:
            包含签名信息的请求头
        """
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if body is None:
            body = ""

        # 生成时间戳和随机数
        timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        nonce = str(uuid.uuid4()).replace('-', '')

        # 添加必要的请求头
        headers['X-CTYUN-Date'] = timestamp
        headers['X-CTYUN-Nonce'] = nonce

        # 创建待签名字符串
        string_to_sign = self._create_string_to_sign(method, uri, params, headers, timestamp)

        # 计算签名
        signature = self._calculate_signature(string_to_sign, timestamp)

        # 添加认证头
        auth_headers = {
            'X-CTYUN-Signature': signature,
            'X-CTYUN-SignedHeaders': self._get_signed_headers(headers),
            'X-CTYUN-Date': timestamp,
            'X-CTYUN-Nonce': nonce,
            'X-CTYUN-Algorithm': 'CTYUN-HMAC-SHA256'
        }

        return auth_headers

    def _calculate_signature(self, string_to_sign: str, timestamp: str) -> str:
        """
        计算签名

        Args:
            string_to_sign: 待签名字符串
            timestamp: 时间戳

        Returns:
            签名值
        """
        # 创建签名密钥
        date_key = hmac.new(
            f'CTYUN{self.secret_key}'.encode(),
            timestamp[:8].encode(),
            hashlib.sha256
        ).digest()

        signature_key = hmac.new(
            date_key,
            'ctyun_request'.encode(),
            hashlib.sha256
        ).digest()

        # 计算最终签名
        signature = hmac.new(
            signature_key,
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _get_signed_headers(self, headers: Dict[str, str]) -> str:
        """
        获取已签名头列表

        Args:
            headers: 请求头字典

        Returns:
            已签名头列表字符串
        """
        signed_headers = []
        for key in headers:
            lower_key = key.lower()
            if lower_key in ['host', 'x-ctyun-date', 'x-ctyun-nonce'] or lower_key.startswith('x-ctyun-'):
                signed_headers.append(lower_key)

        signed_headers.sort()
        return ";".join(signed_headers)

    def get_bearer_token(self) -> str:
        """
        获取Bearer Token（简化认证方式）

        Returns:
            Bearer Token字符串
        """
        return f"Bearer {self.access_key}"