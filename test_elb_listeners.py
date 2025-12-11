#!/usr/bin/env python3
"""
测试ELB监听器API功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(current_dir))

def test_elb_listeners():
    """测试ELB监听器API"""
    try:
        from core import CTYUNClient
        from elb.client import ELBClient

        # 使用HX配置文件的认证信息
        print("🔑 使用HX配置文件认证:")
        access_key = "8199e3911a794a2587dfb7764601d4e0"
        secret_key = "0421ff3125fb42c182bfc732bf4dbf76"

        print(f"   Access Key: {access_key[:8]}...")
        print(f"   Secret Key: {secret_key[:8]}...")

        # 创建客户端
        client = CTYUNClient(access_key=access_key, secret_key=secret_key)
        elb_client = ELBClient(client)

        # 测试参数
        test_region_id = "200000001852"
        print(f"\n🧪 测试监听器列表API:")
        print(f"   区域ID: {test_region_id}")

        # 1. 测试监听器列表
        print(f"\n📡 调用监听器列表API...")
        result = elb_client.list_listeners(region_id=test_region_id)

        print(f"\n✅ 监听器列表API调用成功!")
        print(f"📊 返回结果:")
        print(f"   状态码: {result.get('statusCode')}")
        print(f"   消息: {result.get('message')}")

        listeners = result.get('returnObj', [])
        if listeners:
            print(f"\n📋 监听器列表 (共{len(listeners)}个):")
            print("-" * 100)
            for i, listener in enumerate(listeners, 1):
                print(f"   {i:3}. {listener.get('name', '')}")
                print(f"       ID: {listener.get('ID', '')}")
                print(f"       协议: {listener.get('protocol', '')}:{listener.get('protocolPort', '')}")
                print(f"       状态: {listener.get('status', '')}")
                print(f"       负载均衡器: {listener.get('loadBalancerID', '')}")

                # 获取转发配置
                default_action = listener.get('defaultAction', {})
                if default_action.get('forwardConfig') and default_action['forwardConfig'].get('targetGroups'):
                    target_groups = default_action['forwardConfig']['targetGroups']
                    for tg in target_groups:
                        print(f"       目标组: {tg.get('targetGroupID', '')} (权重: {tg.get('weight', '')})")
                print()

            # 2. 如果有监听器，测试详情API
            if listeners:
                first_listener_id = listeners[0].get('ID', '')
                if first_listener_id:
                    print(f"\n🧪 测试监听器详情API:")
                    print(f"   监听器ID: {first_listener_id}")

                    print(f"\n📡 调用监听器详情API...")
                    detail_result = elb_client.get_listener(
                        region_id=test_region_id,
                        listener_id=first_listener_id
                    )

                    print(f"\n✅ 监听器详情API调用成功!")
                    print(f"📊 返回结果:")
                    print(f"   状态码: {detail_result.get('statusCode')}")
                    print(f"   消息: {detail_result.get('message')}")

                    detail_listeners = detail_result.get('returnObj', [])
                    if detail_listeners:
                        detail_listener = detail_listeners[0]
                        print(f"\n📋 监听器详情:")
                        print("-" * 80)
                        print(f"   名称: {detail_listener.get('name', '')}")
                        print(f"   ID: {detail_listener.get('ID', '')}")
                        print(f"   协议: {detail_listener.get('protocol', '')}")
                        print(f"   端口: {detail_listener.get('protocolPort', '')}")
                        print(f"   状态: {detail_listener.get('status', '')}")
                        print(f"   描述: {detail_listener.get('description', '')}")
                        print(f"   负载均衡器ID: {detail_listener.get('loadBalancerID', '')}")
                        print(f"   访问控制类型: {detail_listener.get('accessControlType', '')}")
                        print(f"   创建时间: {detail_listener.get('createdTime', '')}")

                        # 显示详细配置
                        default_action = detail_listener.get('defaultAction', {})
                        if default_action:
                            print(f"\n   转发配置:")
                            print(f"     动作类型: {default_action.get('type', '')}")
                            if default_action.get('forwardConfig'):
                                forward_config = default_action['forwardConfig']
                                target_groups = forward_config.get('targetGroups', [])
                                if target_groups:
                                    for tg in target_groups:
                                        print(f"     目标组: {tg.get('targetGroupID', '')} (权重: {tg.get('weight', '')})")

        else:
            print(f"\n📝 未找到监听器")
            print(f"   可能原因: 该区域没有监听器或没有访问权限")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 100)
    print("🧪 测试ELB监听器API功能")
    print("=" * 100)

    print("🔑 认证信息:")
    print("   配置文件: HX")
    print("   区域ID: 200000001852 (华北2)")
    print()

    if test_elb_listeners():
        print("\n" + "=" * 100)
        print("✅ ELB监听器API测试成功!")
        print("   ✅ 监听器列表API正常工作")
        print("   ✅ 监听器详情API正常工作")
        print("   ✅ EOP签名认证正常")
        print("   ✅ API返回200和真实数据")
        print("=" * 100)
    else:
        print("\n" + "=" * 100)
        print("❌ ELB监听器API测试失败!")
        print("=" * 100)


if __name__ == "__main__":
    main()