# 天翼云 CLI 工具 🚀

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![APIs](https://img.shields.io/badge/APIs-1132+-brightgreen.svg)](docs/MODULES/README.md#api统计)
[![Commands](https://img.shields.io/badge/Commands-1080+-orange.svg)](docs/MODULES/README.md#命令统计)
[![Modules](https://img.shields.io/badge/Modules-31+-blue.svg)](docs/MODULES/README.md)

**天翼云CLI工具** 是功能强大的企业级命令行工具，帮助您轻松管理天翼云资源。支持云服务器(ECS)、监控告警、安全防护、Redis分布式缓存、弹性负载均衡(ELB)、容器引擎(CCE)、VPC网络、费用查询等核心功能。

[English](README_EN.md) | 简体中文

## 🆚 与天翼云官方 CLI 的对比

天翼云官方已于 2026 年推出命令行工具（Go 实现，命令名同为 `ctyun-cli`）。
以下对比基于 **官方 v0.3.0 实测**（2026-09-20）：

| 维度 | 官方 CLI | ctyun-cli (本项目) |
|------|---------|-------------------|
| 实现 | Go，OpenAPI 自动生成 | Python，手工精编封装 |
| 规模 | 51 模块 / 3,650 命令 | 31 模块 / 1,075 命令（1,132+ API） |
| 命令风格 | API 名原样 `ctyun-cli ecs ListEcsInstances` | 动词式 `ctyun-cli ecs list` |
| 参数风格 | API 参数原名（`--instanceIDList`、`--pageNo`） | 人性化 kebab-case 命名 |
| 命令结构 | 扁平，一模块一长串 | 嵌套子命令组（`vpc eip list`） |
| 输出格式 | json / table | json / table / yaml |
| 配置 | `~/.ctyun-cli.yaml`，环境变量 `CTYUN_AK/SK` | `~/.ctyun/config`(INI)，多 profile，环境变量 `CTYUN_ACCESS_KEY/SECRET_KEY` |
| 特色能力 | `--cli-query`（JMESPath）、`--body` 透传 | 响应统一校验(800)、结果缓存、表格友好输出 |

### 能力差异

- **官方覆盖更全**：弹性伸缩、资源编排、SD-WAN、备份(CSBS/VBS)、DRDS/SQLServer/MongoDB/ClickHouse、DTS、容器镜像(CRS)、CCEOne、MQTT/RabbitMQ/RocketMQ、内网DNS、VPCE 等
- **本项目独有**：CFW 云防火墙(66)、CSSCN 云安全中心、CloudPC 云电脑、Security 安全卫士、Billing 账务增强、OceanFS/IMS 询价、MSE 云原生网关细化命令

### 定位

官方 CLI 走 **API 直通**路线（参数即文档，灵活但繁琐）；本项目走 **开发者体验**路线（贴近 AWS CLI 风格的高层封装，常用操作一行完成）。例如查询运行中的云主机：

- 官方：`ctyun-cli ecs ListEcsInstances --regionID xxx --state running`
- 本项目：`ctyun-cli --region cn-north-1 ecs list --state running`

两者可共存（安装方式见下方⚠️说明），按需选用。

## ✨ 为什么选择天翼云 CLI？

- 🚀 **高效便捷** - 一行命令完成云资源查询和管理，告别繁琐的控制台操作
- 🔐 **安全可靠** - 企业级EOP签名认证，支持环境变量配置保护密钥安全
- 📊 **功能全面** - 覆盖1,132+个API，支持31大服务模块
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

### ⚠️ 与官方 CLI 同名共存

天翼云官方 CLI 的命令名同为 `ctyun-cli`，且其安装脚本默认写入 `/usr/local/bin`（优先级高于 pip 的 `~/.local/bin`）。如果安装过官方 CLI，本工具的命令可能被其覆盖。

**检测方法：**

```bash
which -a ctyun-cli              # 本工具在 ~/.local/bin 或 miniforge3/bin，官方在 /usr/local/bin
ctyun-cli --help 2>&1 | head -3 # 本工具显示"天翼云CLI工具"，官方显示"天翼云命令行工具 (CTYUN CLI)"
```

**推荐共存方案（任选其一）：**

1. **pipx 隔离安装**（推荐）：
   ```bash
   pipx install ctyun-cli
   ```
2. **为官方 CLI 指定非 PATH 安装目录**，让 `ctyun-cli` 归本工具：
   ```bash
   sudo INSTALL_DIR=/opt/ctyun-official/bin sh install-cli.sh
   ```
3. **为本工具设置别名**：
   ```bash
   alias ct='~/.local/bin/ctyun-cli'
   ```

## ⚡ 快速开始

完整参数说明请参阅：[命令参考手册](docs/COMMAND_MANUAL.md)

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
| **LTS (云日志服务)** | 171 | 171 | 日志项目/单元、主机组、采集配置、检索、转储、加工、告警、仪表盘、快速查询 | - |
| **CCE (容器引擎)** | 102 | 103 | Kubernetes集群、节点池、工作负载、Pod/Service/Job、存储卷/PVC/Secret、巡检、任务管理、命名空间、V2查询API | [模块总览](docs/MODULES/README.md) |
| **VPC (私有网络)** | 102 | 104 | VPC/子网/路由表/安全组/EIP/NAT网关、对等连接、ACL、前缀列表、流日志、镜像流量、IPv6、网关路由、l2gw、HAVIP、DHCP、网络诊断、询价 | [模块总览](docs/MODULES/README.md) |
| **Redis (分布式缓存)** | 85 | 89 | 实例管理、监控(V1/V2/代理)、备份与策略、参数模板、账号、SSL、大热key/离线key分析、诊断任务、迁移任务、回收站、询价 | [模块总览](docs/MODULES/README.md) |
| **Monitor (监控服务)** | 82 | 84 | 监控数据、告警管理、Top-N统计、事件管理 | [模块总览](docs/MODULES/README.md) |
| **CFW (云防火墙)** | 66 | 66 | 防火墙管理、概览、资产、防护规则、黑白名单、地址簿、IPS、应用、告警、日志、报表、询价 | - |
| **MSE (微服务引擎)** | 48 | 48 | Nacos注册配置中心、Nacos服务/配置/命名空间管理、微服务实例、云原生API网关（实例/路由/服务/域名/ELB） | - |
| **ECS (云服务器)** | 46 | 76 | 实例管理、快照备份、密钥对、订单查询、资源池查询、云助手、宿主机、网卡、安全组 | [模块总览](docs/MODULES/README.md) |
| **Aone (边缘安全加速平台)** | 45 | 45 | 域名管理、证书管理、缓存刷新/预取、数据统计、安全防护（CC/WAF/DDoS） | - |
| **APM (应用性能监控)** | 44 | 44 | 元数据、应用管理、链路追踪、性能分析、用量统计、告警、通知、Webhook | - |
| **ZOS (对象存储)** | 39 | 39 | 桶管理、对象管理、IAM、标签操作 | - |
| **IAM (身份访问管理)** | 34 | 34 | 用户/用户组/权限/策略/委托/AK-SK/MFA/企业项目/身份供应商/敏感操作 | [模块总览](docs/MODULES/README.md) |
| **ELB (弹性负载均衡)** | 34 | 34 | 负载均衡器、目标组、后端主机、访问控制、证书、网关负载均衡 | [模块总览](docs/MODULES/README.md) |
| **AIServer (AI服务器)** | 19 | 20 | AI服务器实例管理 | - |
| **CDA (云专线)** | 22 | 24 | 专线网关、物理专线、VPC管理、静态/BGP路由、QOS查询、健康检查、链路探测 | [模块总览](docs/MODULES/README.md) |
| **CloudPC (云桌面)** | 15 | 19 | 云桌面实例管理、询价 | - |
| **Billing (计费查询)** | 17 | 17 | 账单查询、费用分析、消费统计、新版账单详情 | [模块总览](docs/MODULES/README.md) |
| **Kafka (分布式消息服务)** | 10 | 11 | 实例列表、节点状态、弹性IP、配置查询、标签、5类询价 | [模块总览](docs/MODULES/README.md) |
| **CSSCN (云安全中心)** | 10 | 11 | 资产查询、风险统计、漏洞、告警、病毒检测、配额 | - |
| **CTMySQL (云数据库MySQL)** | 9 | 9 | 实例查询、标签管理、监控、询价 | - |
| **DPS (物理机)** | 8 | 8 | 物理机管理 | - |
| **Audit (云审计)** | 8 | 8 | 事件查询、资源池管理、跟踪任务管理 | [模块总览](docs/MODULES/README.md) |
| **EBS (弹性块存储)** | 7 | 7 | 块存储管理、快照及快照策略 | [模块总览](docs/MODULES/README.md) |
| **EMR (翼MapReduce)** | 6 | 9 | 集群、节点组、Hive元数据管理 | [模块总览](docs/MODULES/README.md) |
| **Security (安全卫士)** | 6 | 13 | 安全扫描、漏洞管理、风险评估 | [模块总览](docs/MODULES/README.md) |
| **SFS (弹性文件服务)** | 3 | 3 | 弹性文件存储管理、询价 | - |
| **OceanFS (海量文件服务)** | 3 | 3 | 海量文件存储管理、询价 | - |
| **CSS (云搜索服务)** | 3 | 4 | OpenSearch/Elasticsearch/Logstash 实例管理 | [模块总览](docs/MODULES/README.md) |
| **EC (云间高速)** | 3 | 3 | 云间高速连接管理 | - |
| **IMS (镜像服务)** | 2 | 2 | 镜像查询、镜像详细信息 | [模块总览](docs/MODULES/README.md) |
| **SWR (容器镜像服务)** | 18 | 18 | 实例列表/详情/配额/数量/存储配置/资源池、命名空间、仓库、Tag、制品、Chart | - |
| **总计** | **1,075** | **1,132** | **另有 configure 等 5 个工具命令，合计 1,080+** | [所有模块](docs/MODULES/) |

📊 **规模统计：71,000+行代码，1,132+个API，1,080+个命令，31大服务模块**

## 📚 完整文档

### 📖 功能文档
- [服务模块总览](docs/MODULES/README.md) - 全部模块命令/API 统计
- [命令参考](docs/COMMAND_MANUAL.md) - 所有命令的完整参数说明
- [输出格式指南](docs/OUTPUT_FORMAT_GUIDE.md) - table/json/yaml格式使用说明

### 🔧 专项指南
- [Redis 使用指南](docs/REDIS_USAGE.md)
- [监控服务使用指南](docs/MONITOR_USAGE.md)
- [IAM 使用指南](docs/IAM_USAGE.md)
- [安全加固指南](docs/SECURITY-GUIDE.md)

### ❓ 帮助支持
- [版本历史](CHANGELOG.md) - 详细的版本更新记录
- [English README](README_EN.md)

## 🤝 技术支持

如果您在使用过程中遇到问题或有任何建议，欢迎：

- 📧 **邮箱**: popfrog@gmail.com
- 💬 **Issues**: [提交问题反馈](https://github.com/fengyucn/ctyun-cli/issues)
- 📖 **文档**: 查看[完整文档](docs/)获取帮助

## 📝 更新日志

**最新版本**: v1.33.4 (2026-11-06)
- 🆕 **ELB 补齐访问控制策略组管理**：`create-access-control` / `update-access-control` / `delete-access-control`（`/v4/elb/*-access-control`），`clientToken` 不传自动生成

**v1.33.3** (2026-11-06)
- 🆕 **Aone 新增 `access-control-modify`**：按 `rule_id` 修改访问控制策略并设置优先级（`POST /ctapi/v1/accessControlConf/updateAccessControl`），规则 JSON 原样透传

**v1.33.2** (2026-11-06)
- 🆕 **Aone 边缘云版新增 `manage-domain`**：按域名维度停用/启用/删除域名（`POST /ctapi/v1/accessone/domain/manage`），支持 010/011/020 产品；与 `change-domain-status`（009/024，支持无域名接入）是两个不同接口

**v1.33.1** (2026-11-05)
- 🆕 **SWR 容器镜像服务新增 16 个只读查询命令**：实例详情/配额/个数/资源池/存储配置、命名空间、仓库详情、Tag 列表与详情、制品列表与详情、Chart 命名空间/仓库/版本，SWR 模块由 2 个命令扩到 18 个
- 🔧 **SWR 接口修正**：资源池列表兼容 `regionId`/`regionCode`/`regionName` 实际字段，实例详情补充 `enterpriseProjectName`/`chartAddress` 等返回字段，错误输出统一为 `查询失败 [错误码]: 摘要 -- 详情`

**v1.33.0** (2026-11-05)
- 🆕 **Aone 模块新增 2 个管理命令**：`change-domain-status`（停用/启用/删除域名，支持域名接入与无域名接入）、`access-control-insert`（多域名批量下发访问控制策略）
- 🆕 **ELB 新增 `listener stop`**：停止监听器（`POST /v4/elb/stop-listener`，支持 `--client-token` 幂等存根）

**v1.32.4** (2026-10-26)
- 🔧 **Aone 边缘安全加速平台接口修复**：`query-domain-protocol` / `query-resource-packages` 修正 API 路径（此前分别返回 "API Not Found" 和"参数校验失败"），`query-service-detail` 与 `query-bandwidth-data` 表格输出重构（状态字典、可读时间、带宽 bps/Mbps 双列）
- 🔧 **修复 4 处选项 `--help` 崩溃**：`click.Choice` 整型枚举导致 `vpc price nat create/modify`、`ctmysql batch-monitor`、`redis task-center-list` 的帮助信息抛 TypeError

**v1.32.3** (2026-10-25)
- 🆕 **CDA 云专线新增 3 个 QOS 查询命令**：`qos list` / `qos policy list` / `qos rule list`，并修复 `vpc list`、`vpc count`、`static-route list` 的真实传参（`GET` + `vrfName`）

**v1.32.2** (2026-10-25)
- 🆕 **Billing 模块新增 5 个新版账单详情命令**：`product-cycle-v2` / `resource-detail-v2` / `resource-cycle-v2` / `usage-detail-v2` / `usage-cycle-v2`（包周期+按需合并，支持按天分组）

**v1.32.1** (2026-09-20)
- 🚀 **LTS 模块首批可用命令**：`unit list-v1` / `unit get-index-v1` / `search logs-v1`（日志检索，支持 SQL 分析语句与游标翻页）

**v1.32.0** (2026-09-20)
- 🆕 **新增 SWR（容器镜像服务）模块**：镜像实例列表（`list-instances`，支持全资源池查询）、镜像仓库列表（`list-repositories`）

**v1.31.3** (2026-09-20)
- 🔒 **安全加固**：启用全量 TLS 证书校验、debug 日志认证头脱敏、凭据文件权限收紧（600/700），修复 APM 表格输出崩溃

**v1.31.2** (2026-08-26)
- 🔧 **Aone 模块响应解析修复**：修复 CLI 误报"查询失败: success"问题（兼容 statusCode/code 两种响应结构），并修正 WAF/访问控制查询的参数命名

**v1.31.1** (2026-08-21)
- 🔧 **Redis 模块监控 API 修复**：修复 4 个监控类 API 路径错误（404），并修正参数名、时间格式与签名编码，`monitor-items`/`monitor-history`/`clients` 恢复正常

**v1.31.0** (2026-08-07)
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
