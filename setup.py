from setuptools import setup, find_packages
import os

# 专为PyPI优化的详细项目描述
def get_long_description():
    return """
# 天翼云 CLI 工具 🚀

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**天翼云CLI工具** 是一款功能强大的命令行工具，帮助您在终端中轻松管理天翼云资源。支持云服务器(ECS)、监控告警、安全防护、Redis分布式缓存服务、费用查询等核心功能。

## ✨ 核心特性

- 🚀 **高效便捷** - 一行命令完成云资源查询和管理，告别繁琐的控制台操作
- 🔐 **安全可靠** - 采用企业级EOP签名认证，支持环境变量配置保护密钥安全
- 📊 **功能全面** - 覆盖70+个API，支持ECS、监控、安全、Redis、计费等服务
- 🎯 **简单易用** - 清晰的命令结构，丰富的使用示例，5分钟快速上手
- 🔧 **灵活配置** - 支持配置文件、环境变量等多种配置方式
- 📈 **实时监控** - 完整的监控服务支持，包括指标查询、告警管理、Top-N统计

## 🎯 支持的服务

### 🖥️ 云服务器管理 (ECS)
- **19个查询API** - 实例管理、快照备份、云硬盘、密钥对、备份策略等
- 支持资源池查询、自动续订配置、云主机组管理
- 异步任务状态跟踪和DNS记录查询

### 📊 监控与告警服务
- **28个监控API** - 完整的监控解决方案
- 指标查询、告警管理、Top-N统计、巡检功能
- CPU/内存使用率排行、告警历史、事件记录

### 🗄️ Redis分布式缓存服务
- Redis实例管理、性能监控、配置查询
- 分布式缓存集群运维支持

### 🛡️ 安全卫士服务
- 安全客户端管理、漏洞扫描、安全策略配置
- 实时安全状态监控和风险评估

### 💰 费用管理服务
- 账户余额查询、月度账单、消费明细统计
- 实时费用监控和预算管理

### 👤 身份与访问管理 (IAM)
- 用户管理、角色权限、访问控制策略配置
- 企业级权限治理支持

### 💾 云硬盘服务 (EBS)
- 云硬盘管理、快照备份、性能监控
- 存储资源统计和优化建议

## 📦 快速安装

```bash
pip install ctyun-cli
```

## ⚡ 快速开始

### 1. 配置认证信息
```bash
# 推荐使用环境变量（更安全）
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key

# 或使用交互式配置
ctyun-cli configure
```

### 2. 开始使用
```bash
# 查看云服务器列表
ctyun-cli ecs list

# 查询监控数据
ctyun-cli monitor query-metric-data --namespace ecs --metric_name cpu_util

# 查看账户余额
ctyun-cli billing balance

# 查看安全状态
ctyun-cli security agents
```

## 🔧 高级功能

### 多种输出格式
```bash
# 表格格式（默认）
ctyun-cli ecs list --output table

# JSON格式（适合程序处理）
ctyun-cli ecs list --output json

# YAML格式（适合配置管理）
ctyun-cli ecs list --output yaml
```

### 多环境配置
```bash
# 配置不同环境
ctyun-cli configure --profile production
ctyun-cli configure --profile testing

# 切换环境
ctyun-cli --profile production ecs list
```

### 调试模式
```bash
ctyun-cli --debug ecs list
```

## 📚 文档与支持

- **完整文档**: https://github.com/fengyucn/ctyun-cli
- **项目主页**: https://pypi.org/project/ctyun-cli/
- **问题反馈**: https://github.com/fengyucn/ctyun-cli/issues

## 📋 系统要求

- Python 3.8+
- 稳定的网络连接
- 天翼云账号和有效的Access Key

## 🔐 安全提示

- ✅ 使用环境变量配置认证信息
- ✅ 定期轮换访问密钥
- ❌ 避免在代码中硬编码密钥

## 📜 许可证

本项目采用 MIT 许可证开源。

---

**让天翼云资源管理更简单！立即安装体验！** 🚀
"""

setup(
    name="ctyun-cli",
    version="1.3.3",
    description="天翼云CLI工具 - 基于终端的云资源管理平台（支持ECS、监控、Redis分布式缓存服务）",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Y.FENG",
    author_email="popfrog@gmail.com",
    url="https://github.com/fengyucn/ctyun-cli",
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
    keywords="ctyun cloud cli management monitoring ecs redis distributed-cache query snapshot keypair volume backup affinity-group flavor resize vnc statistics",
    project_urls={
        "Documentation": "https://github.com/fengyucn/ctyun-cli",
        "Source": "https://github.com/fengyucn/ctyun-cli",
        "Tracker": "https://github.com/fengyucn/ctyun-cli/issues",
        "Changelog": "https://github.com/fengyucn/ctyun-cli/commits/master",
        "Homepage": "https://pypi.org/project/ctyun-cli/",
    },
)