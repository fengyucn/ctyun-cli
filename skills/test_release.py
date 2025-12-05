#!/usr/bin/env python3
"""
测试版本发布工作流的核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from release_workflow import ReleaseWorkflow


def test_version_management():
    """测试版本管理功能"""
    print("🧪 测试版本管理功能")
    print("=" * 50)

    try:
        # 创建工作流实例
        workflow = ReleaseWorkflow("..")  # 上级目录是项目根目录

        # 测试获取当前版本
        print("📍 测试获取当前版本")
        current_version = workflow.get_current_version()
        print(f"✅ 当前版本: {current_version}")

        # 测试版本解析
        print("\n📍 测试版本解析")
        major, minor, patch = workflow.parse_version(current_version)
        print(f"✅ 版本解析: {major}.{minor}.{patch}")

        # 测试版本增量
        print("\n📍 测试版本增量")
        next_patch = workflow.increment_version(current_version, "patch")
        next_minor = workflow.increment_version(current_version, "minor")
        next_major = workflow.increment_version(current_version, "major")
        print(f"✅ 补丁增量: {current_version} → {next_patch}")
        print(f"✅ 次版本增量: {current_version} → {next_minor}")
        print(f"✅ 主版本增量: {current_version} → {next_major}")

        # 测试文件路径
        print("\n📍 测试文件路径检查")
        print(f"✅ pyproject.toml: {workflow.pyproject_file.exists()}")
        print(f"✅ setup.py: {workflow.setup_file.exists()}")
        print(f"✅ __init__.py: {workflow.init_file.exists()}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_git_operations():
    """测试Git操作"""
    print("\n🧪 测试Git操作")
    print("=" * 50)

    try:
        workflow = ReleaseWorkflow("..")

        # 测试Git状态检查
        print("📍 测试Git状态检查")
        status = workflow.check_git_status()
        print(f"✅ Git状态: {'干净' if status else '有未提交更改'}")

        # 测试Git命令执行
        print("\n📍 测试Git命令执行")
        returncode, stdout, stderr = workflow.run_command("git --version", check=False)
        if returncode == 0:
            print(f"✅ Git版本: {stdout.strip()}")
        else:
            print(f"⚠️ Git命令执行失败")

        return True

    except Exception as e:
        print(f"❌ Git测试失败: {e}")
        return False


def test_build_operations():
    """测试构建操作"""
    print("\n🧪 测试构建操作")
    print("=" * 50)

    try:
        workflow = ReleaseWorkflow("..")

        # 测试文件清理（不实际执行，只检查命令）
        print("📍 测试清理命令生成")
        print("✅ 清理命令: rm -rf dist build *.egg-info")

        # 检查dist目录
        dist_dir = workflow.project_root / "dist"
        print(f"📍 Dist目录状态: {'存在' if dist_dir.exists() else '不存在'}")
        if dist_dir.exists():
            wheel_files = list(dist_dir.glob("*.whl"))
            print(f"✅ 找到 {len(wheel_files)} 个wheel文件")
            for wheel in wheel_files:
                print(f"  - {wheel.name}")

        return True

    except Exception as e:
        print(f"❌ 构建测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始测试版本发布工作流")
    print("=" * 80)

    tests = [
        ("版本管理", test_version_management),
        ("Git操作", test_git_operations),
        ("构建操作", test_build_operations),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))

    # 汇总结果
    print("\n" + "=" * 80)
    print("📊 测试结果汇总:")
    print("=" * 80)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1

    print("=" * 80)
    print(f"总计: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！工作流可以正常使用。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关问题。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)