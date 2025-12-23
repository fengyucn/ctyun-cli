# 天翼云 CLI 工具 🚀

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![APIs](https://img.shields.io/badge/APIs-200+-brightgreen.svg)](docs/MODULES/README.md#api统计)
[![Commands](https://img.shields.io/badge/Commands-209+-orange.svg)](docs/MODULES/README.md#命令统计)
[![Modules](https://img.shields.io/badge/Modules-11+-blue.svg)](docs/MODULES/README.md)

**天翼云CLI工具** 是功能强大的企业级命令行工具，帮助您轻松管理天翼云资源。支持云服务器(ECS)、监控告警、安全防护、Redis分布式缓存、弹性负载均衡(ELB)、容器引擎(CCE)、VPC网络、费用查询等核心功能。

[English](README_EN.md) | 简体中文

## ✨ 为什么选择天翼云 CLI？

- 🚀 **高效便捷** - 一行命令完成云资源查询和管理，告别繁琐的控制台操作
- 🔐 **安全可靠** - 企业级EOP签名认证，支持环境变量配置保护密钥安全
- 📊 **功能全面** - 覆盖200+个API，支持11大服务模块
- 🎯 **简单易用** - 清晰的命令结构，丰富的使用示例，5分钟快速上手
- 🔧 **灵活配置** - 支持配置文件、环境变量等多种配置方式
- 📈 **实时监控** - 完整的监控服务支持，包括指标查询、告警管理、Top-N统计

## 📦 安装

只需一条命令即可安装：

```bash
pip install ctyun-cli
```

验证安装成功：

```bash
ctyun-cli --version
```

## ⚡ 快速开始

详细步骤请参考：[5分钟快速上手指南](docs/QUICKSTART.md)

### 第一步：配置认证信息

推荐使用环境变量方式（更安全）：

```bash
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key
```

或使用交互式配置：

```bash
ctyun-cli configure
```

### 第二步：开始使用

```bash
# 查看所有可用命令
ctyun-cli --help

# 查看云服务器列表
ctyun-cli ecs list

# 查询账户余额
ctyun-cli billing balance

# 查看负载均衡器
ctyun-cli elb loadbalancer list

# 查看容器集群
ctyun-cli cce list-clusters
```

## 📊 功能概览

| 服务模块 | 命令数 | API数 | 核心功能 | 文档 |
|---------|--------|-------|----------|------|
| **ECS (云服务器)** | 41 | 38 | 实例管理、快照备份、密钥对、订单查询 | [详细文档](docs/MODULES/ecs.md) |
| **Monitor (监控服务)** | 53 | 54 | 监控数据、告警管理、Top-N统计、事件管理 | [详细文档](docs/MODULES/monitor.md) |
| **Redis (分布式缓存)** | 14 | 19 | 实例管理、性能监控、网络配置、完整创建功能 | [详细文档](docs/MODULES/redis.md) |
| **Billing (计费查询)** | 15 | 14 | 账单查询、费用分析、消费统计 | [详细文档](docs/MODULES/billing.md) |
| **Security (安全卫士)** | 5 | 11 | 安全扫描、漏洞管理、风险评估 | [详细文档](docs/MODULES/security.md) |
| **IAM (身份访问管理)** | 3 | 3 | 项目管理、权限控制 | [详细文档](docs/MODULES/iam.md) |
| **EBS (弹性块存储)** | 1 | 1 | 块存储管理 | [详细文档](docs/MODULES/ebs.md) |
| **CDA (云专线)** | 19 | 19 | 专线网关、物理专线、VPC管理、健康检查、链路探测 | [详细文档](docs/MODULES/cda.md) |
| **VPC (私有网络)** | 15 | 15 | VPC网络、子网、路由表、安全组、弹性IP | [详细文档](docs/MODULES/vpc.md) |
| **CCE (容器引擎)** | 36 | 37 | Kubernetes集群、节点池、工作负载、配置管理 | [详细文档](docs/MODULES/cce.md) |
| **ELB (弹性负载均衡)** | 7 | 5 | 负载均衡器、目标组、后端主机管理 | [详细文档](docs/MODULES/elb.md) |
| **总计** | **209** | **216** | **覆盖天翼云核心服务** | [所有模块](docs/MODULES/) |

📊 **规模统计：39,000+行代码，216+个API，209+个命令，11大服务模块**

## 📚 完整文档

### 🚀 快速开始
- [5分钟快速上手](docs/QUICKSTART.md) - 从安装到第一个命令的完整指南
- [安装指南](docs/GUIDES/INSTALLATION.md) - 详细的安装说明和故障排除
- [配置指南](docs/GUIDES/CONFIGURATION.md) - 认证配置和多环境设置

### 📖 功能文档
- [功能概览](docs/FEATURES.md) - 完整功能介绍和特性说明
- [模块详细文档](docs/MODULES/) - 各服务模块的详细使用说明
- [命令参考](docs/COMMAND_MANUAL.md) - 所有命令的完整参数说明

### 🔧 高级功能
- [高级功能](docs/GUIDES/ADVANCED.md) - 管道操作、调试模式等高级特性
- [输出格式](docs/GUIDES/OUTPUT_FORMATS.md) - table/json/yaml格式使用说明
- [最佳实践](docs/BEST_PRACTICES.md) - 使用技巧和最佳实践

### ❓ 帮助支持
- [常见问题](docs/FAQ.md) - 常见问题解答和解决方案
- [故障排除](docs/TROUBLESHOOTING.md) - 错误诊断和解决方法
- [版本历史](CHANGELOG.md) - 详细的版本更新记录

## 🔗 相关链接

### 外部资源
- **PyPI包**: https://pypi.org/project/ctyun-cli/
- **GitHub仓库**: https://github.com/fengyucn/ctyun-cli
- **问题反馈**: https://github.com/fengyucn/ctyun-cli/issues

### 内部文档
- [使用指南](docs/GUIDES/)
- [API参考](docs/MODULES/)
- [配置说明](docs/GUIDES/CONFIGURATION.md)

## 🤝 技术支持

如果您在使用过程中遇到问题或有任何建议，欢迎：

- 📧 **邮箱**: popfrog@gmail.com
- 💬 **Issues**: [提交问题反馈](https://github.com/fengyucn/ctyun-cli/issues)
- 📖 **文档**: 查看[完整文档](docs/)获取帮助

## 📝 更新日志

**最新版本**: v1.7.5 (2025-12-08)
- 🚀 **新增ECS订单查询API**: 根据订单ID查询云主机UUID
- 📊 **统计数据更新**: 209个CLI命令，216个API接口，11大服务模块
- 🔧 **技术改进**: EOP签名认证、多格式输出、错误处理优化

查看完整的更新历史请参阅 [CHANGELOG.md](CHANGELOG.md)

## 📜 开源协议

本项目采用 [MIT 协议](LICENSE) 开源，欢迎使用和贡献。

**作者：Y.FENG | 邮箱：popfrog@gmail.com**

---

**🚀 让天翼云资源管理更简单！立即安装体验！**

**安装命令:** `pip install ctyun-cli`