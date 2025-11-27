#!/usr/bin/env python3
"""
天翼云CLI工具安装配置
"""

from setuptools import setup, find_packages
import os
import sys

# Python版本检查
if sys.version_info < (3, 8):
    sys.exit('ctyun-cli需要Python 3.8或更高版本')

# 读取文件内容
def read_file(filename):
    """读取文件内容"""
    here = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(here, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ''

# requirements.txt中的依赖
RUNTIME_REQUIREMENTS = [
    'requests>=2.31.0',
    'click>=8.1.0',
    'cryptography>=41.0.0',
    'colorama>=0.4.6',
    'tabulate>=0.9.0',
    'pyyaml>=6.0'
]

# 开发依赖
DEV_REQUIREMENTS = [
    'pytest>=7.4.0',
    'pytest-cov>=4.1.0',
    'black>=23.0.0',
    'flake8>=6.0.0',
    'build>=0.10.0',
    'twine>=4.0.0'
]

setup(
    # 基本包信息
    name="ctyun-cli",
    version="1.3.9",
    description="天翼云CLI工具 - 基于终端的云资源管理平台",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",

    # 作者信息
    author="Y.FENG",
    author_email="popfrog@gmail.com",
    maintainer="Y.FENG",
    maintainer_email="popfrog@gmail.com",

    # 项目链接
    url="https://github.com/fengyucn/ctyun-cli",
    project_urls={
        "Documentation": "https://github.com/fengyucn/ctyun-cli",
        "Source": "https://github.com/fengyucn/ctyun-cli",
        "Tracker": "https://github.com/fengyucn/ctyun-cli/issues",
        "Changelog": "https://github.com/fengyucn/ctyun-cli/commits/master",
        "Homepage": "https://pypi.org/project/ctyun-cli/",
    },

    # 包配置
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Python版本要求
    python_requires=">=3.8",

    # 依赖管理
    install_requires=RUNTIME_REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
        'test': ['pytest>=7.4.0', 'pytest-cov>=4.1.0'],
        'lint': ['black>=23.0.0', 'flake8>=6.0.0'],
        'build': ['build>=0.10.0', 'twine>=4.0.0']
    },

    # 命令行入口点 - 直接使用CLI主入口
    entry_points={
        "console_scripts": [
            "ctyun-cli=cli.main:cli",
        ],
    },

    # 包含数据文件
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },

    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP",
        "Environment :: Console",
    ],

    # 关键词
    keywords=[
        "ctyun", "cloud", "cli", "management", "monitoring", "ecs",
        "redis", "distributed-cache", "query", "snapshot", "keypair",
        "volume", "backup", "affinity-group", "flavor", "resize",
        "vnc", "statistics", "api", "devops"
    ],

    # 许可证
    license="MIT",

    # 平台支持
    platforms=["any"],

    # 安全配置
    zip_safe=False,
)