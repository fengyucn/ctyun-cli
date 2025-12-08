#!/usr/bin/env python3
"""
使用HX配置文件和真实订单ID测试查询云主机UUID
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(current_dir))

def test_hx_order():
    """使用HX配置测试真实订单"""
    try:
        from core import CTYUNClient
        from auth.eop_signature import CTYUNEOPAuth

        # 使用HX配置文件的认证信息
        print("🔑 使用HX配置文件认证:")
        access_key = "8199e3911a794a2587dfb7764601d4e0"
        secret_key = "0421ff3125fb42c182bfc732bf4dbf76"

        print(f"   Access Key: {access_key[:8]}...")
        print(f"   Secret Key: {secret_key[:8]}...")

        # 创建客户端
        client = CTYUNClient(access_key=access_key, secret_key=secret_key)
        ecs_client = TestECSClient(client)

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
    if test_hx_order():
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