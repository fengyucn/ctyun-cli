from setuptools import setup, find_packages
import os

# 读取README作为long_description
def read_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="ctyun-cli",
    version="1.0.1",
    description="天翼云CLI工具 - 基于终端的云资源管理平台",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="Ctyun CLI Team",
    author_email="ctyun-cli@example.com",
    url="https://github.com/yourusername/ctyun-cli",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "click>=8.1.0",
        "cryptography>=41.0.0",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ctyun-cli=cli.main:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords="ctyun cloud cli management monitoring",
    project_urls={
        "Documentation": "https://github.com/yourusername/ctyun-cli",
        "Source": "https://github.com/yourusername/ctyun-cli",
    },
)