#!/usr/bin/env python3
"""
直接测试订单UUID查询API，不依赖commands模块
"""

import sys
import json
import hashlib
import hmac
import base64
import uuid
from datetime import datetime
from urllib.parse import quote
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(current_dir))

class CTYUNEOPAuth:
    """天翼云EOP签名认证类 - 基于项目中的实现"""

    def __init__(self, access_key: str, secret_key: str):
        """
        初始化认证器

        Args:
            access_key: 访问密钥（AK）
            secret_key: 密钥（SK）
        """
        self.access_key = access_key
        self.secret_key = secret_key

    def sign_request(self, method: str, url: str, query_params=None, body = None, extra_headers=None):
        """
        对请求进行签名，返回完整的请求头
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
        """
        # 获取当前北京时间（UTC+8）
        now = datetime.now()
        return now.strftime('%Y%m%dT%H%M%SZ')

    def _build_signature_string(self, headers, query_params=None, body=None) -> str:
        """
        构造待签名字符串
        sigture = 需要进行签名的Header排序后的组合列表 + "\n" + encode的query + "\n" + toHex(sha256(原封的body))
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
        """
        signature = hmac.new(
            kdate,
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # Base64编码
        signature_base64 = base64.b64encode(signature).decode('utf-8')

        return signature_base64

    def _build_eop_authorization(self, signature: str, headers) -> str:
        """
        构造 Eop-Authorization
        格式：EOP-AK 签名方法SignedHeaders=需要签名的header名Signature=签名

        注意：使用原始header名（不区分大小写），按字母排序
        """
        # 获取需要签名的header名，不区分大小写，按字母排序
        signed_header_names = ['ctyun-eop-request-id', 'eop-date']
        signed_header_names.sort(key=lambda x: x.lower())

        # 构造签名头字符串
        signed_headers = ';'.join(signed_header_names)

        # 构造完整的认证头
        eop_authorization = f"EOP-AK {self.access_key} SignMethod=HMAC-SHA256 SignedHeaders={signed_headers} Signature={signature}"

        return eop_authorization


class TestECSClient:
    """测试用的ECS客户端"""

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_endpoint = 'ctecs-global.ctapi.ctyun.cn'
        self.eop_auth = CTYUNEOPAuth(access_key, secret_key)
        # 创建requests session
        import requests
        self.session = requests.Session()

    def query_uuid_by_order(self, region_id: str, master_order_id: str):
        """
        根据订单ID查询云主机UUID
        """
        print(f"🔍 查询订单UUID: regionId={region_id}, masterOrderID={master_order_id}")

        try:
            url = f'https://{self.base_endpoint}/v4/ecs/order/query-uuid'

            query_params = {
                'regionID': region_id,
                'masterOrderID': master_order_id
            }

            headers = self.eop_auth.sign_request(
                method='GET',
                url=url,
                query_params=query_params,
                body='',
                extra_headers={}
            )

            print(f"📡 API URL: {url}")
            print(f"📋 查询参数: {query_params}")
            print(f"🔑 完整请求头:")
            for k, v in headers.items():
                print(f"   {k}: {v}")

            response = self.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )

            print(f"📊 HTTP状态码: {response.status_code}")
            print(f"📝 响应内容: {response.text}")

            response.raise_for_status()
            result = response.json()

            # 检查返回状态码
            if result.get('statusCode') != 800:
                error_code = result.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = result.get('description', '未知错误')
                print(f"❌ API错误 [{error_code}]: {error_msg}")
                raise Exception(f"API错误 [{error_code}]: {error_msg}")

            print(f"📋 API返回状态码: {result.get('statusCode')}")

            # 解析返回结果
            return_obj = result.get('returnObj', {})
            if return_obj:
                order_status = return_obj.get('orderStatus', '')
                instance_ids = return_obj.get('instanceIDList', [])
                print(f"📊 订单状态码: {order_status}")
                print(f"📊 云主机数量: {len(instance_ids)}")

            return result

        except Exception as e:
            print(f"❌ 查询订单UUID失败: {str(e)}")
            raise


def test_real_order():
    """使用真实订单ID测试API"""
    try:
        # 使用HX配置文件的认证信息
        print("🔑 使用HX配置文件认证:")
        access_key = "8199e3911a794a2587dfb7764601d4e0"
        secret_key = "0421ff3125fb42c182bfc732bf4dbf76"

        print(f"   Access Key: {access_key[:8]}...")
        print(f"   Secret Key: {secret_key[:8]}...")

        # 创建客户端
        ecs_client = TestECSClient(access_key, secret_key)

        # 真实订单ID
        real_order_id = "20251205041521460958"
        test_region_id = "200000001852"

        print(f"\n🧪 使用真实订单ID测试:")
        print(f"   订单ID: {real_order_id}")
        print(f"   区域ID: {test_region_id}")
        print(f"   配置文件: HX")

        # 调用真实API
        print(f"\n📡 调用天翼云API...")
        result = ecs_client.query_uuid_by_order(
            region_id=test_region_id,
            master_order_id=real_order_id
        )

        print(f"\n✅ API调用成功!")
        print(f"📊 返回结果:")
        print(f"   状态码: {result.get('statusCode')}")
        print(f"   消息: {result.get('message')}")
        print(f"   描述: {result.get('description')}")

        # 解析返回数据
        return_obj = result.get('returnObj', {})
        if return_obj:
            order_status = return_obj.get('orderStatus', '')
            instance_id_list = return_obj.get('instanceIDList', [])

            print(f"\n📋 订单详情:")
            print(f"   订单状态码: {order_status}")

            # 状态映射
            status_map = {
                '1': '待支付', '2': '已支付', '3': '完成', '4': '取消', '5': '施工失败',
                '7': '正在支付中', '8': '待审核', '9': '审核通过', '10': '审核未通过',
                '11': '撤单完成', '12': '退订中', '13': '退订完成', '14': '开通中',
                '15': '变更移除', '16': '自动撤单中', '17': '手动撤单中', '18': '终止中',
                '22': '支付失败', '-2': '待撤单', '-1': '未知', '0': '错误',
                '140': '已初始化', '999': '逻辑错误'
            }

            status_text = status_map.get(str(order_status), f'未知状态({order_status})')
            print(f"   订单状态: {status_text}")

            if instance_id_list:
                print(f"\n🖥️  云主机ID列表 (共{len(instance_id_list)}个):")
                print("-" * 100)
                for i, instance_id in enumerate(instance_id_list, 1):
                    print(f"   {i:3}. {instance_id}")
                    # 显示UUID格式信息
                    if len(instance_id) == 32:
                        formatted_uuid = f"{instance_id[:8]}-{instance_id[8:12]}-{instance_id[12:16]}-{instance_id[16:20]}-{instance_id[20:]}"
                        print(f"        格式化: {formatted_uuid}")

                if order_status == '3':  # 完成
                    print(f"\n✅ 订单已完成! 成功获取 {len(instance_id_list)} 个云主机ID")
                    print(f"   💡 这些ID可用于后续的云主机管理操作")
                else:
                    print(f"\n⏳ 订单状态: {status_text}")
                    if order_status == '14':
                        print("   💡 订单正在开通中，请稍后重试获取云主机ID")
                        print("   ⏰ 建议等待5-10分钟后再次查询")
                    elif order_status == '1':
                        print("   💳 订单待支付，请完成支付后再查询")
                        print("   💳 登录天翼云控制台完成支付")
                    elif order_status == '5':
                        print("   ❌ 订单施工失败")
                        print("   🔍 请检查订单参数或联系天翼云技术支持")
                    elif order_status in ['22', '0', '999']:
                        print(f"   ❌ 订单处理失败: {status_text}")
            else:
                print(f"\n📝 云主机ID列表: 无")
                if order_status == '3':
                    print("   ⚠️  订单已完成但未返回云主机ID")
                    print("   💡 可能原因: 订单不涉及云主机创建或创建失败")
                elif order_status == '14':
                    print("   ⏳ 订单正在开通中，完成后将返回云主机ID")
                    print("   💡 建议定期查询订单状态")
                else:
                    print(f"   💡 当前状态: {status_text}")
                    print("   💡 根据状态判断是否需要进一步操作")
        else:
            print(f"\n⚠️  返回数据为空")
            print(f"   可能原因: API返回异常或订单不存在")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 100)
    print("🧪 使用HX配置和真实订单ID测试查询云主机UUID API")
    print("=" * 100)

    print("🔑 认证信息:")
    print("   配置文件: HX")
    print("   区域ID: 200000001852 (华北2)")
    print("   订单ID: 20251205041521460958")
    print()

    # 测试真实订单
    if test_real_order():
        print("\n" + "=" * 100)
        print("✅ HX配置文件真实订单ID测试完成!")
        print("=" * 100)

        print(f"\n📋 测试订单信息:")
        print(f"   订单ID: 20251205041521460958")
        print(f"   创建时间: 2025-12-05 04:15:21 (从订单ID推断)")

        print(f"\n💡 后续建议:")
        print(f"   1. 如果返回了云主机ID，可以使用这些ID进行实例管理操作")
        print(f"   2. 如果订单状态是'开通中'，建议等待5-10分钟后再次查询")
        print(f"   3. 如果订单失败，请检查订单参数或联系天翼云技术支持")
        print(f"   4. 可以将此API集成到自动化工作流中")

        print(f"\n🔗 相关API:")
        print(f"   - 查询云主机详情: GET /v4ecs/ecs/query-instances-detail")
        print(f"   - 查询云主机列表: GET /v4ecs/ecs/query-instances")
        print(f"   - 重启云主机: POST /v4ecs/ecs/restart-servers")
    else:
        print("\n" + "=" * 100)
        print("❌ 测试失败")
        print("   请检查网络连接和认证信息")
        print("=" * 100)


if __name__ == "__main__":
    main()