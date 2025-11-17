#!/usr/bin/env python3
"""
天翼云CLI快速开始示例
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from client import CTYUNClient
from ecs.client import ECSClient
from config.settings import config
from utils.helpers import OutputFormatter


def main():
    """快速开始示例"""
    print("=== 天翼云CLI快速开始示例 ===\n")

    # 1. 使用配置文件创建客户端
    try:
        print("1. 初始化API客户端...")
        client = CTYUNClient(profile='default')
        print("✓ 客户端初始化成功")
    except Exception as e:
        print(f"✗ 客户端初始化失败: {e}")
        print("请先运行 'python setup_config.py' 配置认证信息")
        return

    # 2. 创建ECS客户端
    ecs_client = ECSClient(client)
    print("✓ ECS客户端创建成功")

    # 3. 查询可用实例规格
    print("\n2. 查询可用实例规格...")
    try:
        instance_types = ecs_client.list_instance_types()
        print(f"✓ 查询到 {len(instance_types.get('instanceTypes', []))} 种实例规格")

        # 显示前5种规格
        if 'instanceTypes' in instance_types:
            print("前5种实例规格:")
            for i, instance_type in enumerate(instance_types['instanceTypes'][:5]):
                print(f"  {i+1}. {instance_type.get('type', 'Unknown')} - {instance_type.get('description', 'No description')}")
    except Exception as e:
        print(f"✗ 查询实例规格失败: {e}")

    # 4. 查询可用镜像
    print("\n3. 查询可用镜像...")
    try:
        images = ecs_client.list_images(image_type='public', os_type='Ubuntu')
        print(f"✓ 查询到 {len(images.get('images', []))} 个Ubuntu镜像")

        # 显示前3个镜像
        if 'images' in images:
            print("前3个Ubuntu镜像:")
            for i, image in enumerate(images['images'][:3]):
                print(f"  {i+1}. {image.get('imageId', 'Unknown')} - {image.get('imageName', 'No name')}")
    except Exception as e:
        print(f"✗ 查询镜像失败: {e}")

    # 5. 查询现有实例
    print("\n4. 查询现有实例...")
    try:
        instances = ecs_client.list_instances(page=1, page_size=10)
        instance_list = instances.get('instances', [])
        print(f"✓ 查询到 {len(instance_list)} 个实例")

        if instance_list:
            print("实例列表:")
            for i, instance in enumerate(instance_list):
                status = instance.get('status', 'Unknown')
                name = instance.get('instanceName', 'Unknown')
                instance_id = instance.get('instanceId', 'Unknown')
                print(f"  {i+1}. {name} ({instance_id}) - {status}")
        else:
            print("  没有找到实例")
    except Exception as e:
        print(f"✗ 查询实例失败: {e}")

    # 6. 创建实例示例 (注释掉，避免实际创建)
    print("\n5. 创建实例示例代码...")
    print("""
    # 以下是如何创建一个实例的示例代码:

    try:
        result = ecs_client.create_instance(
            name="my-quickstart-instance",
            instance_type="s6.small",
            image_id="img-ubuntu20",
            system_disk_type="SSD",
            system_disk_size=40,
            count=1
        )
        print(f"✓ 实例创建成功: {result}")
    except Exception as e:
        print(f"✗ 实例创建失败: {e}")
    """)

    # 7. 显示配置信息
    print("\n6. 当前配置信息:")
    credentials = config.get_credentials()
    print(f"  区域: {credentials['region']}")
    print(f"  端点: {credentials['endpoint']}")
    print(f"  输出格式: {config.get_output_format()}")
    print(f"  超时时间: {config.get_timeout()}秒")
    print(f"  重试次数: {config.get_retry_count()}")

    print("\n=== 快速开始示例完成 ===")
    print("\n更多用法请参考:")
    print("  - python -m ctyun-cli --help")
    print("  - python -m ctyun-cli ecs --help")
    print("  - docs/usage.md")


if __name__ == '__main__':
    main()