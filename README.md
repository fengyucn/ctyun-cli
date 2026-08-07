# 天翼云 CLI 工具 🚀

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![APIs](https://img.shields.io/badge/APIs-943+-brightgreen.svg)](docs/MODULES/README.md#api统计)
[![Commands](https://img.shields.io/badge/Commands-898+-orange.svg)](docs/MODULES/README.md#命令统计)
[![Modules](https://img.shields.io/badge/Modules-28+-blue.svg)](docs/MODULES/README.md)

**天翼云CLI工具** 是功能强大的企业级命令行工具，帮助您轻松管理天翼云资源。支持云服务器(ECS)、监控告警、安全防护、Redis分布式缓存、弹性负载均衡(ELB)、容器引擎(CCE)、VPC网络、费用查询等核心功能。

[English](README_EN.md) | 简体中文

## 🎉 庆祝天翼云官方 CLI 正式上线！

热烈祝贺天翼云官方命令行工具正式发布！官方 CLI 的推出标志着天翼云开发者生态的进一步完善。作为社区开源项目，ctyun-cli 与官方 CLI **互补共存**，共同为开发者提供高效的云端操作体验。

### 📋 命令与能力对比报告：官方CLI vs ctyun-cli

#### 命令风格

| 维度 | 官方CLI (Go) | ctyun-cli (Python) |
|------|-------------|-------------------|
| 命名 | API 动作名原样 `ListEbmInstance`（PascalCase） | 动词式 `list`/`detail`（kebab-case） |
| 结构 | 扁平，一模块一长串 | 嵌套子命令组 `vpc eip list` |
| 来源 | 照 OpenAPI 自动生成 | 手工精编封装 |

#### 能力覆盖

| 域 | 官方CLI | ctyun-cli |
|----|--------|-----------|
| VPC/网络查询（EIP/NAT/安全组/路由/子网/终端节点） | ~71 | ~73 |
| ECS/ELB/EVS/DPS/IMS | ✓（更全） | ✓ |
| 弹性伸缩/SD-WAN/资源编排/云间高速/备份/VPN/并行文件/专属云 | ✓ 独占 | ✗ |
| Redis/CCE（容器60+）/Kafka/CSS/EMR | ✗ | ✓ 独占 |
| IAM/账务/CDN(WAF)/云电脑/监控 | ✗ | ✓ 独占 |

#### 结论

- **网络核心查询两者对等**（各约 70 条）
- **官方CLI 强于边缘 IaaS**（伸缩/编排/备份/SD-WAN）；**ctyun-cli 强于 PaaS/账务/容器**（Redis/CCE/Kafka/IAM）
- **二者互补而非包含**。选型建议：IaaS 网络明细 → 官方CLI；容器/中间件/账务 → ctyun-cli

## ✨ 为什么选择天翼云 CLI？

- 🚀 **高效便捷** - 一行命令完成云资源查询和管理，告别繁琐的控制台操作
- 🔐 **安全可靠** - 企业级EOP签名认证，支持环境变量配置保护密钥安全
- 📊 **功能全面** - 覆盖943+个API，支持28大服务模块
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
| **CFW (云防火墙)** | 66 | 66 | 防火墙管理、概览、资产、防护规则、黑白名单、地址簿、IPS、应用、告警、日志、报表、询价 | - |
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
| **总计** | **898** | **943** | **覆盖天翼云核心服务** | [所有模块](docs/MODULES/) |

📊 **规模统计：61,000+行代码，943+个API，898+个命令，28大服务模块**

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

## 🤝 技术支持

如果您在使用过程中遇到问题或有任何建议，欢迎：

- 📧 **邮箱**: popfrog@gmail.com
- 💬 **Issues**: [提交问题反馈](https://github.com/fengyucn/ctyun-cli/issues)
- 📖 **文档**: 查看[完整文档](docs/)获取帮助

## 📝 更新日志

**最新版本**: v1.31.0 (2026-08-07)
- 🚀 **CCE 模块新增 V2 查询 API**：新增 10 个 V2 版本查询命令（升级类 6 个 + 全新类 4 个），与现有 V1.1 接口并存

**v1.30.0** (2026-07-27)
- 🆕 **新增 CFW（云防火墙）模块**：涵盖防火墙管理、概览、资产、防护规则、黑白名单、地址簿、IPS、应用、告警、日志、报表、询价，共 66 个命令

**v1.29.2** (2026-07-27)
- 🚀 **MSE 模块新增云原生 API 网关管理**：涵盖网关实例/路由/服务/域名/ELB 管理，共 18 个新命令

**v1.29.1** (2026-07-27)
- 🚀 **MSE 模块补充**：新增 Nacos 命名空间/黑白名单/用户与角色/AKSK 认证管理，共 8 个新命令

**v1.29.0** (2026-07-27)
- 🚀 **MSE 模块大幅扩展**：新增 Nacos 注册配置中心管理，涵盖实例管理（4个）、Nacos 服务管理（9个）、Nacos 配置管理（8个），共 21 个新命令

**v1.28.1** (2026-07-24)
- 🔧 **VPC 模块优化**：`describe-eips` 命令新增 `--page` / `--page-size` 分页参数

**v1.28.0** (2026-07-24)
- 🆕 **新增 EC（云间高速）/ MSE（微服务引擎）模块** + 多模块询价 API 大幅扩展：VPC/CloudPC/Kafka/ECS/SFS/OceanFS 共新增 37 个询价命令

查看完整历史请参阅 [CHANGELOG.md](CHANGELOG.md)

## 📜 开源协议

本项目采用 [MIT 协议](LICENSE) 开源，欢迎使用和贡献。

**作者：Y.FENG | 邮箱：popfrog@gmail.com**

---

**🚀 让天翼云资源管理更简单！立即安装体验！**

**安装命令:** `pip install ctyun-cli`
