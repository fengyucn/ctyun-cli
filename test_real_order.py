#!/usr/bin/env python3
"""
使用真实订单ID测试查询云主机UUID API
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_real_order():
    """使用真实订单ID测试API"""
    try:
        from core import CTYUNClient
        from auth.eop_signature import CTYUNEOPAuth

        # 使用环境变量或测试密钥
        access_key = os.environ.get('CTYUN_ACCESS_KEY')
        secret_key = os.environ.get('CTYUN_SECRET_KEY')

        if not access_key or not secret_key:
            print("❌ 请设置环境变量 CTYUN_ACCESS_KEY 和 CTYUN_SECRET_KEY")
            return False

        print(f"🔑 使用认证信息: {access_key[:8]}...")

        # 创建客户端
        client = CTYUNClient(access_key=access_key, secret_key=secret_key)
        ecs_client = TestECSClient(client)

        # 真实订单ID
        real_order_id = "20251205041521460958"
        test_region_id = "200000001852"

        print(f"🧪 使用真实订单ID测试:")
        print(f"   订单ID: {real_order_id}")
        print(f"   区域ID: {test_region_id}")

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
                print("-" * 80)
                for i, instance_id in enumerate(instance_id_list, 1):
                    print(f"   {i:2}. {instance_id}")

                if order_status == '3':  # 完成
                    print(f"\n✅ 订单已完成! 成功获取 {len(instance_id_list)} 个云主机ID")
                else:
                    print(f"\n⏳ 订单状态: {status_text}")
                    if order_status == '14':
                        print("   💡 订单正在开通中，请稍后重试")
                    elif order_status == '1':
                        print("   💳 订单待支付，请完成支付后再查询")
            else:
                print(f"\n📝 云主机ID列表: 无")
                if order_status == '3':
                    print("   ⚠️  订单已完成但未返回云主机ID，可能不涉及云主机创建")
                else:
                    print(f"   💡 当前状态: {status_text}")
        else:
            print(f"\n⚠️  返回数据为空")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


class TestECSClient:
    """测试用的ECS客户端"""

    def __init__(self, client):
        self.client = client
        self.service = 'ecs'
        self.base_endpoint = 'ctecs-global.ctapi.ctyun.cn'
        # 初始化EOP签名认证器
        self.eop_auth = CTYUNEOPAuth(client.access_key, client.secret_key)

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
                body=None
            )

            response = self.client.session.get(
                url,
                params=query_params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # 检查返回状态码
            if result.get('statusCode') != 800:
                error_code = result.get('errorCode', 'UNKNOWN_ERROR')
                error_msg = result.get('description', '未知错误')
                print(f"❌ API错误 [{error_code}]: {error_msg}")
                raise Exception(f"API错误 [{error_code}]: {error_msg}")

            # 解析返回结果
            return_obj = result.get('returnObj', {})
            order_status = return_obj.get('orderStatus', '')
            instance_ids = return_obj.get('instanceIDList', [])

            print(f"📋 API返回状态码: {result.get('statusCode')}")
            print(f"📊 订单状态码: {order_status}")
            print(f"📊 云主机数量: {len(instance_ids)}")

            return result

        except Exception as e:
            print(f"❌ 查询订单UUID失败: {str(e)}")
            raise


def main():
    print("=" * 80)
    print("🧪 使用真实订单ID测试查询云主机UUID API")
    print("=" * 80)

    # 显示环境变量提示
    access_key = os.environ.get('CTYUN_ACCESS_KEY')
    secret_key = os.environ.get('CTYUN_SECRET_KEY')

    if not access_key:
        print("🔑 环境变量设置示例:")
        print("   export CTYUN_ACCESS_KEY='your_access_key'")
        print("   export CTYUN_SECRET_KEY='your_secret_key'")
        print("   python test_real_order.py")
        print("")

    print(f"🔑 当前认证状态:")
    print(f"   CTYUN_ACCESS_KEY: {'已设置' if access_key else '未设置'}")
    print(f"   CTYUN_SECRET_KEY: {'已设置' if secret_key else '未设置'}")
    print("")

    # 测试真实订单
    if test_real_order():
        print("\n" + "=" * 80)
        print("✅ 真实订单ID测试完成!")
        print("=" * 80)

        print("\n📋 测试订单信息:")
        print(f"   订单ID: 20251205041521460958")
        print(f"   区域ID: 200000001852 (华北2)")

        print("\n💡 后续操作:")
        print("   1. 如果返回云主机ID，可以用于实例管理")
        print("   2. 如果订单状态是'开通中'，可以稍后重试")
        print("   3. 可以将此API集成到自动化流程中")
    else:
        print("\n" + "=" * 80)
        print("❌ 测试失败")
        print("=" * 80)


if __name__ == "__main__":
    main()