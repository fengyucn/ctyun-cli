#!/usr/bin/env python3
"""
Claude Skills - 版本发布工作流

这个技能提供了自动化的版本发布流程，包括：
1. 版本号更新
2. Git提交和推送
3. 包构建
4. PyPI发布

使用方法：
- 自动增量版本号：python skills/release_workflow.py --auto
- 指定版本号：python skills/release_workflow.py --version 1.7.0
- 仅发布现有版本：python skills/release_workflow.py --release-only
"""

import os
import sys
import re
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
import json


class ReleaseWorkflow:
    """版本发布工作流管理器"""

    def __init__(self, project_root: Optional[str] = None):
        """
        初始化工作流

        Args:
            project_root: 项目根目录，默认为当前工作目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.pyproject_file = self.project_root / "pyproject.toml"
        self.setup_file = self.project_root / "setup.py"
        self.init_file = self.project_root / "src" / "ctyun_cli" / "__init__.py"

    def run_command(self, command: str, check: bool = True) -> Tuple[int, str, str]:
        """
        执行命令行命令

        Args:
            command: 要执行的命令
            check: 是否检查返回码

        Returns:
            返回码、标准输出、标准错误
        """
        print(f"🔄 执行命令: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )

        if check and result.returncode != 0:
            print(f"❌ 命令执行失败: {command}")
            print(f"错误输出: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, command)

        if result.stdout:
            print(f"✅ 输出: {result.stdout.strip()}")

        return result.returncode, result.stdout, result.stderr

    def get_current_version(self) -> str:
        """获取当前版本号"""
        try:
            # 从pyproject.toml读取版本
            with open(self.pyproject_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        except FileNotFoundError:
            pass

        try:
            # 从setup.py读取版本
            with open(self.setup_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        except FileNotFoundError:
            pass

        raise ValueError("无法找到版本号信息")

    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """解析版本号为元组"""
        try:
            parts = version.split('.')
            return int(parts[0]), int(parts[1]), int(parts[2])
        except (IndexError, ValueError):
            raise ValueError(f"无效的版本号格式: {version}")

    def increment_version(self, current_version: str, increment_type: str = "patch") -> str:
        """
        增量版本号

        Args:
            current_version: 当前版本号
            increment_type: 增量类型 (major, minor, patch)

        Returns:
            新版本号
        """
        major, minor, patch = self.parse_version(current_version)

        if increment_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment_type == "minor":
            minor += 1
            patch = 0
        elif increment_type == "patch":
            patch += 1
        else:
            raise ValueError(f"无效的增量类型: {increment_type}")

        return f"{major}.{minor}.{patch}"

    def update_version_in_file(self, file_path: Path, old_version: str, new_version: str) -> bool:
        """
        更新文件中的版本号

        Args:
            file_path: 文件路径
            old_version: 旧版本号
            new_version: 新版本号

        Returns:
            是否成功更新
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找并替换版本号
            updated_content = re.sub(
                rf'version\s*=\s*["\']{re.escape(old_version)}["\']',
                f'version = "{new_version}"',
                content
            )

            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"✅ 更新版本号: {file_path} ({old_version} → {new_version})")
                return True
            return False
        except FileNotFoundError:
            print(f"⚠️  文件不存在: {file_path}")
            return False

    def update_version(self, new_version: str) -> bool:
        """
        更新所有相关文件中的版本号

        Args:
            new_version: 新版本号

        Returns:
            是否成功更新
        """
        print(f"🔄 更新版本号到: {new_version}")
        old_version = self.get_current_version()

        updated_files = []

        # 更新pyproject.toml
        if self.update_version_in_file(self.pyproject_file, old_version, new_version):
            updated_files.append(str(self.pyproject_file))

        # 更新setup.py
        if self.update_version_in_file(self.setup_file, old_version, new_version):
            updated_files.append(str(self.setup_file))

        # 更新__init__.py
        if self.update_version_in_file(self.init_file, old_version, new_version):
            updated_files.append(str(self.init_file))

        if updated_files:
            print(f"✅ 版本号更新完成，修改了 {len(updated_files)} 个文件")
            return True
        else:
            print("⚠️  没有文件需要更新")
            return False

    def check_git_status(self) -> bool:
        """检查Git状态"""
        print("🔍 检查Git状态")
        try:
            _, stdout, _ = self.run_command("git status --porcelain")
            if stdout.strip():
                print("⚠️  存在未提交的更改")
                print(stdout)
                return False
            return True
        except subprocess.CalledProcessError:
            print("❌ Git状态检查失败")
            return False

    def git_add_and_commit(self, version: str, commit_message: str = None) -> bool:
        """
        Git添加和提交

        Args:
            version: 版本号
            commit_message: 自定义提交信息

        Returns:
            是否成功
        """
        print("🔄 Git提交操作")

        if not commit_message:
            commit_message = f"chore: 版本号更新到{version}"

        try:
            # 检查Git状态
            _, stdout, _ = self.run_command("git status --porcelain")
            if not stdout.strip():
                print("ℹ️  没有更改需要提交")
                return True

            # 添加文件
            files_to_add = [self.pyproject_file, self.setup_file, self.init_file]
            for file_path in files_to_add:
                if file_path.exists():
                    self.run_command(f"git add {file_path}")

            # 提交
            self.run_command(f'git commit -m "{commit_message}"')
            print("✅ Git提交成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Git提交失败: {e}")
            return False

    def git_push(self) -> bool:
        """Git推送到远程仓库"""
        print("🔄 Git推送操作")
        try:
            self.run_command("git push origin master")
            print("✅ Git推送成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Git推送失败: {e}")
            return False

    def clean_build_files(self) -> bool:
        """清理构建文件"""
        print("🧹 清理构建文件")
        try:
            dirs_to_remove = ["dist", "build", "*.egg-info"]
            for pattern in dirs_to_remove:
                if "*" in pattern:
                    self.run_command(f"rm -f {pattern}", check=False)
                else:
                    self.run_command(f"rm -rf {pattern}", check=False)
            print("✅ 构建文件清理完成")
            return True
        except Exception as e:
            print(f"⚠️  清理构建文件失败: {e}")
            return False

    def build_package(self) -> bool:
        """构建包"""
        print("🔨 构建包")
        try:
            self.clean_build_files()
            self.run_command("python -m build --wheel --no-isolation")

            # 检查构建结果
            dist_dir = self.project_root / "dist"
            wheel_files = list(dist_dir.glob("*.whl"))
            if wheel_files:
                print(f"✅ 构建成功: {wheel_files[0].name}")
                return True
            else:
                print("❌ 构建失败：未找到wheel文件")
                return False
        except subprocess.CalledProcessError as e:
            print(f"❌ 构建失败: {e}")
            return False

    def upload_to_pypi(self, test: bool = False) -> bool:
        """
        上传到PyPI

        Args:
            test: 是否上传到测试PyPI

        Returns:
            是否成功
        """
        print(f"🚀 发布到{'测试' if test else '生产'}PyPI")
        try:
            repo_arg = "--repository testpypi" if test else ""
            self.run_command(f"python -m twine upload {repo_arg} dist/*")

            if test:
                print("✅ 上传到测试PyPI成功")
                print("🔗 https://test.pypi.org/project/ctyun-cli/")
            else:
                print("✅ 上传到生产PyPI成功")
                print("🔗 https://pypi.org/project/ctyun-cli/")

            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyPI上传失败: {e}")
            return False

    def release(self,
                version: str = None,
                auto_increment: str = "patch",
                commit_message: str = None,
                skip_git_check: bool = False,
                release_only: bool = False) -> bool:
        """
        完整的发布流程

        Args:
            version: 指定版本号
            auto_increment: 自动增量类型 (major/minor/patch)
            commit_message: 自定义提交信息
            skip_git_check: 跳过Git状态检查
            release_only: 仅发布，不更新版本号

        Returns:
            是否成功
        """
        try:
            print("🚀 开始版本发布流程")
            print("=" * 50)

            # 1. 检查Git状态
            if not release_only and not skip_git_check:
                if not self.check_git_status():
                    print("⚠️  请先提交或暂存未提交的更改")
                    return False

            # 2. 版本号处理
            if not release_only:
                if version:
                    print(f"📌 使用指定版本号: {version}")
                else:
                    current_version = self.get_current_version()
                    version = self.increment_version(current_version, auto_increment)
                    print(f"📌 自动增量版本号: {current_version} → {version}")

                # 3. 更新版本号
                if not self.update_version(version):
                    return False

            # 4. Git提交
            if not release_only:
                if not self.git_add_and_commit(version, commit_message):
                    return False

                # 5. Git推送
                if not self.git_push():
                    return False

            # 6. 构建包
            if not self.build_package():
                return False

            # 7. 发布到测试PyPI
            print("🧪 先发布到测试PyPI验证...")
            if not self.upload_to_pypi(test=True):
                return False

            # 8. 发布到生产PyPI
            print("🚀 发布到生产PyPI...")
            if not self.upload_to_pypi(test=False):
                return False

            print("=" * 50)
            print(f"🎉 版本发布成功！v{version}")
            print(f"📦 PyPI: https://pypi.org/project/ctyun-cli/{version}/")
            print(f"🧪 测试PyPI: https://test.pypi.org/project/ctyun-cli/{version}/")

            # 保存发布记录
            self.save_release_record(version)

            return True

        except Exception as e:
            print(f"❌ 发布失败: {e}")
            return False

    def save_release_record(self, version: str):
        """保存发布记录"""
        record_file = self.project_root / ".release_history.json"
        try:
            records = []
            if record_file.exists():
                with open(record_file, 'r') as f:
                    records = json.load(f)

            from datetime import datetime
            record = {
                "version": version,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            records.append(record)

            # 只保留最近10次记录
            records = records[-10:]

            with open(record_file, 'w') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)

            print(f"📝 发布记录已保存: {record_file}")

        except Exception as e:
            print(f"⚠️  保存发布记录失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Claude Skills - 版本发布工作流")

    # 版本号选项
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument(
        "--version", "-v",
        help="指定要发布的版本号 (例如: 1.7.0)"
    )
    version_group.add_argument(
        "--auto", "-a",
        choices=["major", "minor", "patch"],
        default="patch",
        help="自动增量版本号 (默认: patch)"
    )

    # 其他选项
    parser.add_argument(
        "--commit-message", "-m",
        help="自定义提交信息"
    )
    parser.add_argument(
        "--skip-git-check",
        action="store_true",
        help="跳过Git状态检查"
    )
    parser.add_argument(
        "--release-only",
        action="store_true",
        help="仅发布现有版本，不更新版本号"
    )
    parser.add_argument(
        "--project-root",
        help="项目根目录路径 (默认: 当前目录)"
    )

    args = parser.parse_args()

    # 创建工作流实例
    workflow = ReleaseWorkflow(args.project_root)

    # 执行发布流程
    success = workflow.release(
        version=args.version,
        auto_increment=args.auto,
        commit_message=args.commit_message,
        skip_git_check=args.skip_git_check,
        release_only=args.release_only
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()