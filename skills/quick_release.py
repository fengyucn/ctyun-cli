#!/usr/bin/env python3
"""
Claude Skills - 快速版本发布

这是一个简化版本，专为Claude使用场景优化
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from release_workflow import ReleaseWorkflow


def quick_release():
    """快速版本发布 - 补丁增量"""
    print("🚀 Claude Skills - 快速版本发布")
    print("=" * 50)

    try:
        # 创建工作流实例
        workflow = ReleaseWorkflow("..")

        # 显示当前信息
        current_version = workflow.get_current_version()
        next_version = workflow.increment_version(current_version, "patch")

        print(f"📋 当前版本: {current_version}")
        print(f"📋 发布版本: {next_version}")
        print(f"📋 项目路径: {workflow.project_root.absolute()}")

        # 确认操作
        print("\n⚠️  即将执行以下操作:")
        print("  1. 更新版本号")
        print("  2. Git提交和推送")
        print("  3. 构建wheel包")
        print("  4. 发布到PyPI")

        # 在自动化环境中直接执行
        print("\n🔄 开始执行发布流程...")

        success = workflow.release(
            version=next_version,
            auto_increment=None,
            commit_message=f"chore: 版本号更新到{next_version}",
            skip_git_check=True,  # 跳过Git状态检查以适应自动化环境
            release_only=False
        )

        if success:
            print(f"\n🎉 版本发布成功！v{next_version}")
            print(f"📦 安装命令: pip install ctyun-cli=={next_version}")
            return True
        else:
            print("\n❌ 版本发布失败")
            return False

    except Exception as e:
        print(f"❌ 发布过程出错: {e}")
        return False


if __name__ == "__main__":
    success = quick_release()
    sys.exit(0 if success else 1)