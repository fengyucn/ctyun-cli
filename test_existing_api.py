#!/usr/bin/env python3
"""
测试现有的ECS API是否工作正常
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(current_dir))

def test_existing_ecs_api():
    """测试现有的ECS API"""
    try:
        from core import CTYUNClient
        from ecs.client import ECSClient

        # 使用HX配置文件的认证信息
        print("🔑 使用HX配置文件认证:")
        access_key = "8199e3911a794a2587dfb7764601d4e0"
        secret_key = "0421ff3125fb42c182bfc732bf4dbf76"

        print(f"   Access Key: {access_key[:8]}...")
        print(f"   Secret Key: {secret_key[:8]}...")

        # 创建客户端
        client = CTYUNClient(access_key=access_key, secret_key=secret_key)
        ecs_client = ECSClient(client)

        # 测试现有的API
        test_region_id = "200000001852"
        print(f"\n🧪 测试现有API - get_customer_resources:")
        print(f"   区域ID: {test_region_id}")

        # 调用现有API
        print(f"\n📡 调用天翼云API...")
        result = ecs_client.get_customer_resources(region_id=test_region_id)

        print(f"\n✅ API调用成功!")
        print(f"📊 返回结果:")
        print(f"   状态码: {result.get('statusCode')}")
        print(f"   消息: {result.get('message')}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 80)
    print("🧪 测试现有ECS API的EOP签名认证")
    print("=" * 80)

    if test_existing_ecs_api():
        print("\n" + "=" * 80)
        print("✅ 现有ECS API测试成功!")
        print("   说明EOP签名认证机制工作正常")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ 现有ECS API测试失败!")
        print("   说明EOP签名认证机制存在问题")
        print("=" * 80)


if __name__ == "__main__":
    main()