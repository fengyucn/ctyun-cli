#!/usr/bin/env python3
"""
CLI工具测试脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_cli():
    """测试CLI工具"""
    print("=== 天翼云CLI工具测试 ===\n")

    try:
        # 导入主CLI模块
        from cli.main import cli
        print("✓ CLI模块导入成功")

        # 显示帮助信息
        print("\n1. 显示主帮助信息:")
        cli(['--help'])

        print("\n2. 显示ECS帮助信息:")
        cli(['ecs', '--help'])

        print("\n3. 列出ECS实例 (模拟数据):")
        cli(['ecs', 'list'])

        print("\n4. 显示配置信息:")
        cli(['show-config'])

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n=== 测试完成 ===")
    return True

if __name__ == '__main__':
    success = test_cli()
    sys.exit(0 if success else 1)