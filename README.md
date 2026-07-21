# 天翼云 CLI 工具 🚀

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![APIs](https://img.shields.io/badge/APIs-830+-brightgreen.svg)](docs/MODULES/README.md#api统计)
[![Commands](https://img.shields.io/badge/Commands-785+-orange.svg)](docs/MODULES/README.md#命令统计)
[![Modules](https://img.shields.io/badge/Modules-27+-blue.svg)](docs/MODULES/README.md)

**天翼云CLI工具** 是功能强大的企业级命令行工具，帮助您轻松管理天翼云资源。支持云服务器(ECS)、监控告警、安全防护、Redis分布式缓存、弹性负载均衡(ELB)、容器引擎(CCE)、VPC网络、费用查询等核心功能。

[English](README_EN.md) | 简体中文

## ✨ 为什么选择天翼云 CLI？

- 🚀 **高效便捷** - 一行命令完成云资源查询和管理，告别繁琐的控制台操作
- 🔐 **安全可靠** - 企业级EOP签名认证，支持环境变量配置保护密钥安全
- 📊 **功能全面** - 覆盖830+个API，支持27大服务模块
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
ctyun-cli --help
```

## ⚡ 快速开始

详细步骤请参考：[5分钟快速上手指南](docs/QUICKSTART.md)

### 第一步：配置认证信息

推荐使用环境变量方式（更安全）：

```bash
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key
```

或使用命令行配置：

```bash
ctyun-cli configure \
  --access-key your_access_key \
  --secret-key your_secret_key \
  --region cn-north-1
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
| **ECS (云服务器)** | 71 | 74 | 实例管理、快照备份、密钥对、订单查询、资源池查询、云助手、宿主机、网卡、安全组 | [详细文档](docs/MODULES/ecs.md) |
| **Monitor (监控服务)** | 82 | 74 | 监控数据、告警管理、Top-N统计、事件管理 | [详细文档](docs/MODULES/monitor.md) |
| **LTS (云日志服务)** | 168 | 169 | 日志项目/单元、主机组、采集配置、检索、转储、加工、告警、仪表盘、快速查询 | - |
| **CCE (容器引擎)** | 92 | 93 | Kubernetes集群、节点池、工作负载、配置管理、任务管理、命名空间 | [详细文档](docs/MODULES/cce.md) |
| **Aone (边缘安全加速平台)** | 45 | 46 | 域名管理、证书管理、缓存刷新/预取、数据统计、安全防护（CC/WAF/DDoS） | - |
| **APM (应用性能监控)** | 44 | 47 | 元数据、应用管理、链路追踪、性能分析、用量统计、告警、通知、Webhook | - |
| **ZOS (对象存储)** | 39 | 40 | 桶管理、对象管理、IAM、标签操作 | - |
| **ELB (弹性负载均衡)** | 34 | 33 | 负载均衡器、目标组、后端主机、访问控制、证书、网关负载均衡 | [详细文档](docs/MODULES/elb.md) |
| **IAM (身份访问管理)** | 34 | 34 | 用户/用户组/权限/策略/委托/AK-SK/MFA/企业项目/身份供应商/敏感操作 | [详细文档](docs/MODULES/iam.md) |
| **RDS (云数据库Redis)** | 33 | 36 | 实例管理、性能监控、网络配置、费用查询、运维管理 | [详细文档](docs/MODULES/redis.md) |
| **VPC (私有网络)** | 23 | 26 | VPC网络、子网、路由表、安全组、弹性IP、标签管理 | [详细文档](docs/MODULES/vpc.md) |
| **CDA (云专线)** | 20 | 6 | 专线网关、物理专线、VPC管理、健康检查、链路探测 | [详细文档](docs/MODULES/cda.md) |
| **AIServer (AI服务器)** | 19 | 24 | AI服务器实例管理 | - |
| **Billing (计费查询)** | 12 | 12 | 账单查询、费用分析、消费统计 | [详细文档](docs/MODULES/billing.md) |
| **CSSCN (云安全中心)** | 10 | 13 | 资产查询、风险统计、漏洞、告警、病毒检测、配额 | - |
| **CTMySQL (云数据库MySQL)** | 9 | 11 | 实例查询、标签管理、监控、询价 | - |
| **CloudPC (云桌面)** | 9 | 16 | 云桌面实例管理 | - |
| **Audit (云审计)** | 8 | 13 | 事件查询、资源池管理、跟踪任务管理 | [详细文档](docs/MODULES/audit.md) |
| **DPS (数据迁移服务)** | 8 | 9 | 数据迁移任务管理 | - |
| **Security (安全卫士)** | 6 | 22 | 安全扫描、漏洞管理、风险评估 | [详细文档](docs/MODULES/security.md) |
| **EMR (翼MapReduce)** | 6 | 10 | 集群、节点组、Hive元数据管理 | [详细文档](docs/MODULES/emr.md) |
| **Kafka (分布式消息服务)** | 5 | 7 | 实例列表、节点状态、弹性IP、配置查询、标签 | [详细文档](docs/MODULES/kafka.md) |
| **CSS (云搜索服务)** | 3 | 5 | OpenSearch/Elasticsearch/Logstash 实例管理 | [详细文档](docs/MODULES/css.md) |
| **IMS (镜像服务)** | 2 | 7 | 镜像查询、镜像详细信息 | [详细文档](docs/MODULES/ims.md) |
| **OceanFS (海量文件服务)** | 2 | 2 | 海量文件存储管理 | - |
| **EBS (弹性块存储)** | 1 | 1 | 块存储管理 | [详细文档](docs/MODULES/ebs.md) |
| **SFS (弹性文件服务)** | - | - | 弹性文件存储管理（实现中） | - |
| **总计** | **785** | **830** | **覆盖天翼云核心服务** | [所有模块](docs/MODULES/) |

📊 **规模统计：61,000+行代码，830+个API，785+个命令，27大服务模块**

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

**最新版本**: v1.26.1 (2026-07-21)
- 🚀 **EBS 模块新增 6 个命令**：云硬盘详情/按名称查询、快照列表/容量/策略

**v1.26.0** (2026-07-20)
- 🚀 **Redis 模块大幅扩展**：新增 52 个命令，涵盖备份管理、安全配置、Key 分析、监控诊断、参数模板、迁移任务等

**v1.25.0** (2026-07-17)
- 🆕 **新增 APM（应用性能监控）模块**：44 个命令，涵盖元数据、应用管理、链路追踪、性能分析、用量统计、告警、通知、Webhook

**v1.24.6** (2026-07-17)
- 🚀 **ELB 模块新增 19 个命令**：访问控制、监控、SLA/证书、转发策略、健康检查、网关负载均衡、IP 监听

**v1.24.5** (2026-07-17)
- 🚀 **LTS 模块大幅扩展 + ZOS 模块新增命令**：LTS 新增 168 个命令（项目/单元/主机组/采集/检索/转储/加工/告警/仪表盘等），ZOS 新增 39 个命令（桶/对象/IAM/标签管理）

**v1.24.4** (2026-07-17)
- 🚀 **CCE 模块新增命令**：`query-cluster-id-by-order-id` 根据订单 ID 查询集群 ID

**v1.24.3** (2026-07-17)
- 🚀 **ECS 模块新增 6 个命令**：安全组查询/详情、规格族实例、专属宿主机规格、元数据、命令执行结果

**v1.24.2** (2026-07-01)
- 🚀 **多模块新增 13 个标签管理 API**：VPC（6个）/ CTMySQL（3个）/ ECS / ELB / Kafka / Redis 标签管理命令

**v1.24.1** (2026-07-01)
- 🔧 **Billing 模块对齐最新 API 文档**：删除 `balance`/`arrears` 无效命令，清理 11 个 mock 方法，保留 11 个有效命令全部对齐真实 API，完善模块帮助信息

**v1.24.0** (2026-06-30)
- 🆕 **新增 CSSCN（云安全中心）模块**：10 个命令，涵盖资产查询、风险/服务器/Agent 统计、漏洞、告警、病毒检测、配额

**v1.23.0** (2026-06-30)
- 🆕 **新增 CTMySQL（云数据库 MySQL）模块**：6 个命令，涵盖实例查询、标签管理、监控、询价（新购/升配/续订）

**v1.22.0** (2026-06-29)
- 🆕 **新增 DPS（数据迁移服务）模块**：8 个命令，涵盖源端 OS/元数据/网卡/磁盘查询、迁移镜像、库存、任务列表与详情

**v1.21.0** (2026-06-29)
- 🆕 **新增 ZOS（对象存储）模块**：`zos query-price` 存储套餐询价
- 🚀 **多模块扩展 8 个 API**：ECS 续订询价、ELB PGELB 询价（3个）、Monitor 拨测查询（2个）、OceanFS 续订/升配询价（2个）

**v1.20.6** (2026-06-23)
- 🚀 **Redis 模块新增 7 个监控与查询 API**：`proxy-monitor-history` / `rw-sep` / `groups` / `cluster-member-info` / `node-memory` / `node-state` / `available-regions`

**v1.20.5** (2026-06-23)
- 🔧 **`redis price` 参数文档完善**：为实例类型、主机类型、版本等参数补充枚举值说明和 `click.Choice` 约束

**v1.20.4** (2026-06-23)
- 🚀 **Redis 模块新增费用查询 API**：`redis price`，支持 9 种订单类型询价（订购/续费/升配/扩容/缩容/增减分片/增减副本）

**v1.20.3** (2026-06-23)
- 🚀 **Redis 模块新增 6 个运维 API**：`node-list` / `log-download` / `replication-state` / `labels` / `running-logs` / `accounts`

**v1.20.2** (2026-05-21)
- 🔧 **CLI 框架修复**：修复 `handle_error` 装饰器丢失函数元信息（7 个模块），删除无效的 `billing consumption` 命令，`monitor query-alert-history` 添加局部 `--output` 选项

**v1.20.1** (2026-05-19)
- 🚀 **Monitor 模块新增数据导出任务**：`data-export-tasks` / `create-data-export-task` / `delete-data-export-task` / `download-data-export-task`

**v1.20.0** (2026-05-18)
- 🆕 **新增 IMS（镜像服务）模块**：`ims list-available` / `describe`，终端节点 `ctimage-global.ctapi.ctyun.cn`

**v1.19.0** (2026-05-18)
- 🆕 **新增 Audit（云审计）模块**：8 个查询 API，涵盖事件查询、资源池管理、跟踪任务管理

**v1.18.5** (2026-05-14)
- 🚀 **Monitor 模块扩展**：新增 21 个查询 API，涵盖数据订阅、套餐管理、监控看板、资源列表

**v1.18.4** (2026-05-14)
- 🚀 **ECS 查询扩展**：新增 12 个 API，涵盖资源池、云助手、宿主机、网卡

**v1.18.1** (2026-03-01)
- 🔧 **CLI 初始化优化**: 基础命令无需预先配置认证

**v1.18.0** (2026-05-12)
- 🆕 **IAM 全面扩展**：34 个 API，12 大功能分类
- 🚀 **CCE 持续增强**：79 个命令，新增命名空间/任务/标签管理

查看完整历史请参阅 [CHANGELOG.md](CHANGELOG.md)

## 📜 开源协议

本项目采用 [MIT 协议](LICENSE) 开源，欢迎使用和贡献。

**作者：Y.FENG | 邮箱：popfrog@gmail.com**

---

**🚀 让天翼云资源管理更简单！立即安装体验！**

**安装命令:** `pip install ctyun-cli`
