#!/usr/bin/env python3
"""
Python __init__.py 文件检查脚本
确保所有包含Python代码的目录都有__init__.py文件
"""

import os
from pathlib import Path


def check_init_files(project_root='.'):
    """检查__init__.py文件完整性"""
    src_path = Path(project_root) / 'src'
    if not src_path.exists():
        print(f'❌ 源目录 src/ 不存在')
        return False

    missing_inits = []
    empty_inits = []
    packages_found = []

    # 遍历src目录下的所有子目录
    for item in src_path.rglob('*'):
        if item.is_dir() and '__pycache__' not in str(item):
            # 检查是否包含Python文件
            py_files = list(item.glob('*.py'))

            if py_files:
                packages_found.append(item.relative_to(src_path))
                init_file = item / '__init__.py'

                if not init_file.exists():
                    missing_inits.append(item.relative_to(src_path))
                elif init_file.stat().st_size == 0:
                    empty_inits.append(item.relative_to(src_path))

    # 输出结果
    print('🔍 扫描Python包目录...')
    for pkg in sorted(packages_found):
        print(f'   📦 src/{pkg}')

    print()

    if empty_inits:
        print('⚠️  空的 __init__.py 文件:')
        for empty in sorted(empty_inits):
            print(f'   📄 src/{empty}/__init__.py (空文件)')
        print('   💡 建议: 添加适当的导入和 __all__ 定义')
        print()

    if missing_inits:
        print('❌ 缺少 __init__.py 文件的目录:')
        for missing in sorted(missing_inits):
            print(f'   📄 src/{missing}/__init__.py (缺失)')
        print()
        print('请添加缺失的 __init__.py 文件，示例内容:')
        print('"""')
        print('模块描述')
        print('"""')
        print()
        print('from .client import ModuleClient')
        print()
        print('__all__ = [\'ModuleClient\']')
        print()
        return False
    else:
        print('✅ __init__.py 文件检查通过')
        return True


def generate_init_template(package_name, exports=None):
    """生成 __init__.py 文件模板"""
    if exports is None:
        exports = ['ModuleClient']

    template = f'''"""
{package_name}模块
"""

{chr(10).join([f"from .{export.lower()} import {export}" for export in exports])}

__all__ = {exports}
'''
    return template


def main():
    """主函数"""
    success = check_init_files()
    return success


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)