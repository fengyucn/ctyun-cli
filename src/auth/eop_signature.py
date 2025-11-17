"""
天翼云EOP签名认证模块
实现基于EOP规范的AK/SK签名认证机制
"""

import hashlib
import hmac
import base64
import uuid
from datetime import datetime
from urllib.parse import quote
from typing import Dict, Any, Optional


class CTYUNEOPAuth:
    """天翼云EOP签名认证类"""

    def __init__(self, access_key: str, secret_key: str):
        """
        初始化认证器

        Args:
            access_key: 访问密钥（AK）
            secret_key: 密钥（SK）
        """
        self.access_key = access_key
        self.secret_key = secret_key

    def sign_request(self, method: str, url: str, query_params: Optional[Dict[str, Any]] = None,
                    body: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        对请求进行签名，返回完整的请求头

        Args:
            method: HTTP方法
            url: 请求URL
            query_params: 查询参数
            body: 请求体
            extra_headers: 额外的请求头

        Returns:
            包含签名的请求头字典
        """
        # 生成必需的请求头
        request_id = str(uuid.uuid4())
        eop_date = self._get_eop_date()

        # 构建基础请求头
        headers = {
            'Content-Type': 'application/json',
            'ctyun-eop-request-id': request_id,
            'Eop-date': eop_date
        }

        # 添加额外的请求头
        if extra_headers:
            headers.update(extra_headers)

        # 步骤一：构造待签名字符串 signature
        signature_string = self._build_signature_string(
            headers, query_params, body
        )

        # 步骤二：构造动态密钥 kdate
        kdate = self._build_kdate(eop_date)

        # 步骤三：构造 signature
        signature = self._build_signature(signature_string, kdate)

        # 步骤四：构造 Eop-Authorization
        eop_authorization = self._build_eop_authorization(signature, headers)

        # 添加认证头
        headers['Eop-Authorization'] = eop_authorization

        return headers

    def _get_eop_date(self) -> str:
        """
        获取EOP格式的日期时间
        格式：yyyyMMdd'T'HHmmss'Z'
        注意：实际传时间为北京东八区UTC+8时间，TZ仅为格式，非UTC时间

        Returns:
            EOP格式的日期时间字符串
        """
        # 获取当前北京时间（UTC+8）
        now = datetime.now()
        return now.strftime('%Y%m%dT%H%M%SZ')

    def _build_signature_string(self, headers: Dict[str, str],
                                query_params: Optional[Dict[str, Any]] = None,
                                body: Optional[str] = None) -> str:
        """
        构造待签名字符串
        sigture = 需要进行签名的Header排序后的组合列表 + "\n" + encode的query + "\n" + toHex(sha256(原封的body))

        Args:
            headers: 请求头字典
            query_params: 查询参数
            body: 请求体

        Returns:
            待签名字符串
        """
        # 1. 构造需要签名的Header排序后的组合列表
        # EOP强制要求 ctyun-eop-request-id、eop-date 必须进行签名
        signed_header_names = ['ctyun-eop-request-id', 'eop-date']
        
        # 按字母顺序排序
        signed_header_names.sort()
        
        # 构造 header_name:header_value\n 格式
        header_list = []
        for header_name in signed_header_names:
            # 注意：查找header时不区分大小写，但构造签名字符串时必须用小写
            header_value = None
            for k, v in headers.items():
                if k.lower() == header_name.lower():
                    header_value = v
                    break
            
            if header_value:
                header_list.append(f"{header_name.lower()}:{header_value}\n")
        
        header_string = ''.join(header_list)

        # 2. 构造编码后的query字符串
        query_string = ''
        if query_params:
            # 对参数按key排序
            sorted_params = sorted(query_params.items())
            encoded_params = []
            for key, value in sorted_params:
                # 值需要进行URL编码
                encoded_value = quote(str(value), safe='')
                encoded_params.append(f"{key}={encoded_value}")
            query_string = '&'.join(encoded_params)

        # 3. 对body进行SHA256摘要并转十六进制
        if body is None or body == '':
            body = ''
        body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()

        # 拼接最终的待签名字符串
        # 格式：header_string + "\n" + query_string + "\n" + body_hash
        signature_string = f"{header_string}\n{query_string}\n{body_hash}"

        return signature_string

    def _build_kdate(self, eop_date: str) -> bytes:
        """
        构造动态密钥 kdate

        步骤：
        1. ktime = hmacSHA256(eop_date, sk)
        2. kAk = hmacSHA256(ak, ktime)
        3. kdate = hmacSHA256(eop_date的年月日值, kAk)

        Args:
            eop_date: EOP格式的日期时间

        Returns:
            动态密钥 kdate
        """
        # 1. 使用eop_date作为数据，sk作为密钥，算出ktime
        ktime = hmac.new(
            self.secret_key.encode('utf-8'),
            eop_date.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # 2. 使用ak作为数据，ktime作为密钥，算出kAk
        kAk = hmac.new(
            ktime,
            self.access_key.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # 3. 使用eop_date的年月日值作为数据，kAk作为密钥，算出kdate
        # eop_date格式：20221107T093029Z，提取年月日：20221107
        date_part = eop_date.split('T')[0]
        kdate = hmac.new(
            kAk,
            date_part.encode('utf-8'),
            hashlib.sha256
        ).digest()

        return kdate

    def _build_signature(self, signature_string: str, kdate: bytes) -> str:
        """
        构造 signature
        使用kdate作为密钥、signature_string作为数据，进行HMAC-SHA256，然后Base64编码

        Args:
            signature_string: 待签名字符串
            kdate: 动态密钥

        Returns:
            Base64编码的签名
        """
        signature_bytes = hmac.new(
            kdate,
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # Base64编码
        signature = base64.b64encode(signature_bytes).decode('utf-8')

        return signature

    def _build_eop_authorization(self, signature: str, headers: Dict[str, str]) -> str:
        """
        构造 Eop-Authorization 请求头
        格式：ak Headers=header1;header2 Signature=xxx

        Args:
            signature: 签名
            headers: 请求头字典

        Returns:
            Eop-Authorization 字符串
        """
        # 构造 Headers 部分（需要签名的header，按字母排序，用分号分隔）
        signed_header_names = ['ctyun-eop-request-id', 'eop-date']
        signed_header_names.sort()
        headers_part = ';'.join(signed_header_names)

        # 构造完整的 Eop-Authorization
        # 格式：ak Headers=xxx Signature=xxx
        eop_authorization = f"{self.access_key} Headers={headers_part} Signature={signature}"

        return eop_authorization
