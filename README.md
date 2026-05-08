# 天翼云 CLI 工具 🚀

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![APIs](https://img.shields.io/badge/APIs-263+-brightgreen.svg)](docs/MODULES/README.md#api统计)
[![Commands](https://img.shields.io/badge/Commands-260+-orange.svg)](docs/MODULES/README.md#命令统计)
[![Modules](https://img.shields.io/badge/Modules-17+-blue.svg)](docs/MODULES/README.md)

**天翼云CLI工具** 是功能强大的企业级命令行工具，帮助您轻松管理天翼云资源。支持云服务器(ECS)、监控告警、安全防护、Redis分布式缓存、弹性负载均衡(ELB)、容器引擎(CCE)、VPC网络、费用查询等核心功能。

[English](README_EN.md) | 简体中文

## ✨ 为什么选择天翼云 CLI？

- 🚀 **高效便捷** - 一行命令完成云资源查询和管理，告别繁琐的控制台操作
- 🔐 **安全可靠** - 企业级EOP签名认证，支持环境变量配置保护密钥安全
- 📊 **功能全面** - 覆盖260+个API，支持17大服务模块
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
| **ECS (云服务器)** | 52 | 41 | 实例管理、快照备份、密钥对、订单查询 | [详细文档](docs/MODULES/ecs.md) |
| **Monitor (监控服务)** | 52 | 54 | 监控数据、告警管理、Top-N统计、事件管理 | [详细文档](docs/MODULES/monitor.md) |
| **Redis (分布式缓存)** | 18 | 22 | 实例管理、性能监控、网络配置、完整创建功能 | [详细文档](docs/MODULES/redis.md) |
| **Billing (计费查询)** | 15 | 14 | 账单查询、费用分析、消费统计 | [详细文档](docs/MODULES/billing.md) |
| **Security (安全卫士)** | 6 | 13 | 安全扫描、漏洞管理、风险评估 | [详细文档](docs/MODULES/security.md) |
| **IAM (身份访问管理)** | 3 | 3 | 项目管理、权限控制 | [详细文档](docs/MODULES/iam.md) |
| **EBS (弹性块存储)** | 1 | 1 | 块存储管理 | [详细文档](docs/MODULES/ebs.md) |
| **CDA (云专线)** | 20 | 21 | 专线网关、物理专线、VPC管理、健康检查、链路探测 | [详细文档](docs/MODULES/cda.md) |
| **VPC (私有网络)** | 15 | 15 | VPC网络、子网、路由表、安全组、弹性IP | [详细文档](docs/MODULES/vpc.md) |
| **CCE (容器引擎)** | 49 | 50 | Kubernetes集群、节点池、工作负载、配置管理 | [详细文档](docs/MODULES/cce.md) |
| **ELB (弹性负载均衡)** | 11 | 11 | 负载均衡器、目标组、后端主机管理 | [详细文档](docs/MODULES/elb.md) |
| **Kafka (分布式消息服务)** | 4 | 5 | 实例列表、节点状态、弹性IP、配置查询 | [详细文档](docs/MODULES/kafka.md) |
| **CSS (云搜索服务)** | 3 | 4 | OpenSearch/Elasticsearch/Logstash 实例管理 | [详细文档](docs/MODULES/css.md) |
| **EMR (翼MapReduce)** | 6 | 9 | 集群、节点组、Hive元数据管理 | [详细文档](docs/MODULES/emr.md) |
| **SFS (弹性文件服务)** | - | - | 弹性文件存储管理（实现中） | - |
| **OceanFS (海量文件服务)** | - | - | 海量文件存储管理（实现中） | - |
| **Aone (边缘安全加速平台)** | - | - | 边缘安全与加速管理（实现中） | - |
| **LTS (云日志服务)** | - | - | 日志采集、检索、投递、告警管理（实现中） | - |
| **总计** | **260** | **263** | **覆盖天翼云核心服务** | [所有模块](docs/MODULES/) |

📊 **规模统计：39,000+行代码，263+个API，260+个命令，17大服务模块**

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

**最新版本**: v1.17.0 (2026-05-08)
- 🚀 **EIP 弹性公网IP增强**：实现真实可用的 EIP 查询 API
  - `vpc eip detail`：查看EIP详情（带宽/绑定/计费信息）
  - `vpc eip shared-bandwidths`：查询共享带宽列表（支持模糊搜索）
- 🔧 **VPC EIP 查询修复**：`vpc eip list` 从空壳实现为可用状态，支持按状态/IP/实例过滤

**v1.16.0** (2026-05-08)
- 🔧 **VPC EIP 查询实现**：`vpc eip list` 从 TODO 空壳变为真实的 POST 查询

**v1.15.0** (2026-05-08)
- 🆕 **新增 AIServer（模型推理服务）模块**：终端节点 `ctinfer-global.ctapi.ctyun.cn`，实现 19 个 API
  - `aiserver billing-models` / `billing-product` / `orders` / `service-groups` / `models` / `report-call` 等

**v1.14.0** (2026-05-07)
- 🆕 **新增 CloudPC（云电脑/政企版）模块**：终端节点 `ecpc-global.ctapi.ctyun.cn`，实现 10 个查询 API
  - `cloudpc list` / `cloudpc ecs-list` / `cloudpc images` / `cloudpc volumes` / `cloudpc vpcs` / `cloudpc subnets` / `cloudpc users` / `cloudpc orgs` / `cloudpc service-status`
- 🤷‍♂️ **求助**：云电脑查询 API 已实现并验证通过，但云电脑使用独立的资源池 ID 体系

**v1.13.0** (2026-05-02)
- 🚀 **ECS监控增强**：新增 `cpu-latest`/`mem-latest`/`network-latest`/`disk-latest` 实时监控命令，以及 `cpu-history`/`mem-history`/`network-history`/`disk-history` 历史数据查询命令
- 📋 **ECS订单查询增强**：新增 `query-dedicated-host-uuid`（宿主机）和 `query-order-uuid`（通用资源）命令

**v1.12.0** (2026-04-30)
- 🆕 **新增 EMR（翼MapReduce）模块**：终端节点 `emr-global.ctapi.ctyun.cn`，实现 8 个 API

**v1.11.0** (2026-04-30)
- 🆕 **新增 CSS（云搜索服务）模块**：终端节点 `ctcsx-global.ctapi.ctyun.cn`，实现 3 个 API

**v1.10.0** (2026-04-30)
- 🆕 **新增 Kafka（分布式消息服务）模块**：终端节点 `ctgkafka-global.ctapi.ctyun.cn`，实现 4 个 API

**v1.9.0** (2026-04-29)
- 🆕 **新增 LTS/SFS/OceanFS/Aone 模块脚手架**
- 🎯 **Redis 模块完善**：新增 `topology`/`cluster-nodes` 命令，修复 `network`/`describe` 命令

**v1.8.4** (2026-04-22)
- 🔍 **ELB 后端主机详情查询**：新增 `elb targetgroup targets show` 命令

**v1.8.3** (2026-04-22)
- 🏷️ **CCE 任务管理**：新增 5 个任务管理 API（查询/恢复/取消/暂停），以及集群事件列表查询
- 🔧 **CCE 标签管理**：修复 `cce tag bind` API 路径和请求体格式

**v1.8.2** (2026-04-15)
- 🏷️ **ECS 云主机标签管理**：新增 `ecs update-label` 命令，支持增加/修改/删除标签（ADD/UPDATE/DELETE）

**v1.8.1** (2026-03-30)
- 🚀 **CCE Namespace 命名空间管理**：新增 5 个 Namespace API，支持完整的 Kubernetes 命名空间生命周期管理
  - 新增 `cce namespace` 命令组（create/delete/update/show/list）

**v1.8.0** (2026-03-28)
- 🔧 **彻底解决模块命名冲突**：将 `redis` 模块重命名为 `rdscmd`，从根源解决与 `redis-py` 库的命名冲突问题
- ✅ **零兼容性影响**：用户命令 `ctyun redis xxx` 保持不变

查看完整的更新历史请参阅 [CHANGELOG.md](CHANGELOG.md)

## 📜 开源协议

本项目采用 [MIT 协议](LICENSE) 开源，欢迎使用和贡献。

**作者：Y.FENG | 邮箱：popfrog@gmail.com**

---

**🚀 让天翼云资源管理更简单！立即安装体验！**

**安装命令:** `pip install ctyun-cli`