#!/usr/bin/env python3
"""
Python导入路径检查脚本
检查是否存在不正确的 'from src.' 或 'import src.' 导入
"""

import re
import sys
from pathlib import Path


def check_imports(file_path):
    """检查单个文件的导入语句"""
    errors = []
    warnings = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # 跳过注释
        if line_stripped.startswith('#'):
            continue

        # 检查是否有 'from src.' 导入
        if re.match(r'^\s*from\s+src\.', line):
            errors.append(f'第{i}行: 不应使用 "from src." 导入，请使用相对导入 "from .module import"')

        # 检查是否有 'import src.' 导入
        elif re.match(r'^\s*import\s+src\.', line):
            errors.append(f'第{i}行: 不应使用 "import src." 导入，请使用相对导入')

        # 检查相对导入是否正确
        elif re.match(r'^\s*from\s+\.\.', line):
            warnings.append(f'第{i}行: 使用了 ".." 相对导入，请确认包结构正确')

    return errors, warnings


def check_all_imports(src_dir='src'):
    """检查src目录下所有Python文件"""
    src_path = Path(src_dir)
    if not src_path.exists():
        print(f'❌ 源目录 {src_dir} 不存在')
        return False

    all_errors = []
    all_warnings = []
    python_files = list(src_path.rglob('*.py'))

    # 跳过__pycache__目录
    python_files = [f for f in python_files if '__pycache__' not in str(f)]

    for py_file in python_files:
        # 跳过__init__.py的导入检查（因为它们通常使用相对导入）
        if py_file.name == '__init__.py':
            continue

        errors, warnings = check_imports(py_file)
        if errors:
            all_errors.extend([f'{py_file}: {error}' for error in errors])
        if warnings:
            all_warnings.extend([f'{py_file}: {warning}' for warning in warnings])

    # 输出结果
    if all_warnings:
        print('⚠️  警告:')
        for warning in all_warnings:
            print(f'   {warning}')
        print()

    if all_errors:
        print('❌ 错误:')
        for error in all_errors:
            print(f'   {error}')
        print()
        print('请修复以上导入错误后再提交代码')
        return False
    else:
        print('✅ 导入路径检查通过')
        return True


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 检查单个文件
        file_path = sys.argv[1]
        if not file_path.endswith('.py'):
            print('❌ 请提供Python文件路径')
            return False

        errors, warnings = check_imports(file_path)

        if warnings:
            print('⚠️  警告:')
            for warning in warnings:
                print(f'   {warning}')
            print()

        if errors:
            print('❌ 错误:')
            for error in errors:
                print(f'   {error}')
            return False
        else:
            print('✅ 导入检查通过')
            return True
    else:
        # 检查所有文件
        return check_all_imports()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)