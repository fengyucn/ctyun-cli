#!/usr/bin/env python3
"""
直接测试项目中现有的EOP签名实现
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

def test_project_eop():
    """测试项目中现有的EOP签名实现"""
    try:
        # 导入项目中的EOP认证
        from auth.eop_signature import CTYUNEOPAuth

        # 使用HX配置文件的认证信息
        print("🔑 使用HX配置文件认证:")
        access_key = "8199e3911a794a2587dfb7764601d4e0"
        secret_key = "0421ff3125fb42c182bfc732bf4dbf76"

        print(f"   Access Key: {access_key[:8]}...")
        print(f"   Secret Key: {secret_key[:8]}...")

        # 创建EOP认证器
        eop_auth = CTYUNEOPAuth(access_key, secret_key)

        # 测试参数
        url = 'https://ctecs-global.ctapi.ctyun.cn/v4/ecs/order/query-uuid'
        query_params = {
            'regionID': '200000001852',
            'masterOrderID': '20251205041523001327'
        }

        print(f"\n🧪 测试EOP签名生成:")
        print(f"   URL: {url}")
        print(f"   查询参数: {query_params}")

        # 生成签名
        headers = eop_auth.sign_request(
            method='GET',
            url=url,
            query_params=query_params,
            body='',
            extra_headers={}
        )

        print(f"\n📋 生成的请求头:")
        for k, v in headers.items():
            print(f"   {k}: {v}")

        # 发送请求
        import requests
        session = requests.Session()

        print(f"\n📡 发送HTTP请求...")
        response = session.get(
            url,
            params=query_params,
            headers=headers,
            timeout=30
        )

        print(f"📊 HTTP状态码: {response.status_code}")
        print(f"📝 响应内容: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ API调用成功!")
            print(f"📊 返回结果:")
            print(f"   状态码: {result.get('statusCode')}")
            print(f"   消息: {result.get('message')}")

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
                else:
                    print(f"\n📝 云主机ID列表: 无")
            else:
                print(f"\n⚠️  返回数据为空")

            return True
        else:
            print(f"\n❌ API调用失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 100)
    print("🧪 使用新订单ID测试API - 20251205041523001327")
    print("=" * 100)

    if test_project_eop():
        print("\n" + "=" * 100)
        print("✅ 项目EOP签名认证测试成功!")
        print("   订单ID: 20251205041523001327")
        print("   API功能正常工作")
        print("=" * 100)
    else:
        print("\n" + "=" * 100)
        print("❌ 项目EOP签名认证测试失败!")
        print("=" * 100)


if __name__ == "__main__":
    main()