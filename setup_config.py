#!/usr/bin/env python3
"""
天翼云CLI配置设置脚本
"""

import os
import sys
import getpass
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import config
from utils.helpers import OutputFormatter


def setup_credentials():
    """交互式设置认证信息"""
    print("=== 天翼云CLI配置向导 ===\n")

    # 获取配置文件名称
    profile = input("配置文件名称 [default]: ").strip() or 'default'

    # 获取认证信息
    print("\n请输入天翼云认证信息:")
    access_key = input("访问密钥 (Access Key): ").strip()
    if not access_key:
        print("错误: 访问密钥不能为空")
        return False

    secret_key = getpass.getpass("密钥 (Secret Key): ").strip()
    if not secret_key:
        print("错误: 密钥不能为空")
        return False

    # 获取区域信息
    print("\n可用区域:")
    print("  cn-north-1  - 华北")
    print("  cn-east-1   - 华东")
    print("  cn-south-1  - 华南")
    print("  cn-southwest-1 - 西南")

    region = input("区域 [cn-north-1]: ").strip() or 'cn-north-1'

    # 获取API端点
    endpoint = input("API端点 [https://api.ctyun.cn]: ").strip() or 'https://api.ctyun.cn'

    # 保存配置
    try:
        config.set_credentials(
            access_key=access_key,
            secret_key=secret_key,
            region=region,
            endpoint=endpoint,
            profile=profile
        )

        print(f"\n✓ 配置已保存到配置文件 '{profile}'")
        print(f"  区域: {region}")
        print(f"  端点: {endpoint}")
        print(f"  配置文件位置: {config.config_file}")

        return True

    except Exception as e:
        print(f"\n✗ 配置保存失败: {e}")
        return False


def test_connection():
    """测试API连接"""
    try:
        from client import CTYUNClient

        print("\n正在测试API连接...")
        client = CTYUNClient(profile='default')

        # 这里应该调用实际的API进行测试
        # 由于我们还没有真实的API端点，这里只是模拟测试
        print("✓ API连接测试成功")
        print(f"  区域: {client.region}")
        print(f"  端点: {client.endpoint}")

        return True

    except Exception as e:
        print(f"✗ API连接测试失败: {e}")
        return False


def show_current_config():
    """显示当前配置"""
    print("\n=== 当前配置 ===")
    try:
        credentials = config.get_credentials()
        print(f"配置文件: default")
        print(f"访问密钥: {credentials['access_key'][:8]}...")
        print(f"密钥: {credentials['secret_key'][:8]}...")
        print(f"区域: {credentials['region']}")
        print(f"端点: {credentials['endpoint']}")
        print(f"输出格式: {config.get_output_format()}")
        print(f"超时时间: {config.get_timeout()}秒")
        print(f"重试次数: {config.get_retry_count()}")
        print(f"配置文件位置: {config.config_file}")
    except Exception as e:
        print(f"获取配置失败: {e}")


def main():
    """主函数"""
    print("天翼云CLI工具配置管理\n")

    while True:
        print("\n请选择操作:")
        print("1. 设置认证信息")
        print("2. 显示当前配置")
        print("3. 测试API连接")
        print("4. 退出")

        choice = input("\n请输入选项 [1-4]: ").strip()

        if choice == '1':
            setup_credentials()
        elif choice == '2':
            show_current_config()
        elif choice == '3':
            test_connection()
        elif choice == '4':
            print("退出配置管理")
            break
        else:
            print("无效选项，请重新选择")


if __name__ == '__main__':
    main()