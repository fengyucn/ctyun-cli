# 天翼云 CLI 工具 🚀

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API Count](https://img.shields.io/badge/APIs-175+-brightgreen.svg)](#api统计)
[![Commands](https://img.shields.io/badge/Commands-151+-orange.svg)](#功能概览)
[![Modules](https://img.shields.io/badge/Modules-8+-blue.svg)](#功能概览)

**天翼云CLI工具** 是一款功能强大的企业级命令行工具，帮助您在终端中轻松管理天翼云资源。支持云服务器(ECS)、监控告警、安全防护、Redis分布式缓存服务、费用查询等核心功能。


简体中文 | [English](README_EN.md)

## ✨ 为什么选择天翼云 CLI？

- 🚀 **高效便捷** - 一行命令完成云资源查询和管理，告别繁琐的控制台操作
- 🔐 **安全可靠** - 采用企业级EOP签名认证，支持环境变量配置保护密钥安全
- 📊 **功能全面** - 覆盖175+个API，支持8大核心服务模块
- 🎯 **简单易用** - 清晰的命令结构，丰富的使用示例，5分钟快速上手
- 🔧 **灵活配置** - 支持配置文件、环境变量等多种配置方式
- 📈 **实时监控** - 完整的监控服务支持，包括指标查询、告警管理、Top-N统计

## 📦 快速安装

只需一条命令即可安装：

```bash
pip install ctyun-cli
```

验证安装成功：

```bash
ctyun-cli --version
```

## ⚡ 5分钟快速上手

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

# 查看当前配置
ctyun-cli show-config

# 查看云服务器列表
ctyun-cli ecs list

# 查询账户余额
ctyun-cli billing balance
```

## 📊 功能概览

| 服务模块 | 命令数量 | API数量 | 功能描述 |
|---------|---------|---------|----------|
| **ECS (云服务器)** | 50 | 42 | 实例管理、快照备份、密钥对、云主机组等 |
| **Monitor (监控服务)** | 54 | 54 | 监控数据、告警管理、Top-N统计、事件管理 |
| **Redis (分布式缓存)** | 13 | 16 | 实例管理、性能监控、网络配置、完整创建功能等 |
| **Billing (计费查询)** | 12 | 20 | 账单查询、费用分析、消费统计 |
| **Security (安全卫士)** | 5 | 21 | 安全扫描、漏洞管理、风险评估 |
| **IAM (身份访问管理)** | 2 | 2 | 项目管理、权限控制 |
| **EBS (弹性块存储)** | 1 | 1 | 块存储管理 |
| **CDA (云专线)** | 14 | 19 | 专线网关、物理专线、VPC管理、健康检查、链路探测等 |
| **总计** | **151** | **175** | **覆盖天翼云核心服务** |

**📊 规模统计：15,000+行代码，175+个API，151+个命令，8大服务模块**

### 📈 模块详情

#### 🖥️ ECS模块 - 云服务器管理 (50命令/42API)
**核心功能：**
- 实例生命周期管理
- 快照和备份策略
- 密钥对和安全组
- 云主机组管理
- 自动续订配置
- DNS记录管理

**常用命令：**
```bash
ctyun-cli ecs list                              # 查看实例列表
ctyun-cli ecs get-instance-detail             # 获取实例详情
ctyun-cli ecs list-snapshots                   # 查询快照列表
ctyun-cli ecs list-keypairs                    # 查询密钥对
ctyun-cli ecs get-auto-renew-config           # 查询自动续订配置
```

#### 📊 Monitor模块 - 监控告警服务 (54命令/54API)
**核心功能：**
- 监控指标查询 (8个API)
- Top-N统计排行 (6个API)
- 告警规则管理 (7个API)
- 通知管理 (4个API)
- 巡检功能 (5个API)
- 事件历史查询 (24个API)

**常用命令：**
```bash
ctyun-cli monitor query-metric-data            # 查询监控数据
ctyun-cli monitor query-cpu-top               # CPU使用率Top-N
ctyun-cli monitor query-mem-top               # 内存使用率Top-N
ctyun-cli monitor query-alarm-rules           # 查询告警规则
ctyun-cli monitor query-inspection-tasks      # 查询巡检任务
```

#### 🗄️ Redis模块 - 分布式缓存服务 (13命令/16API)
**核心功能：**
- 🔥 **完整实例创建** - 支持25+API参数的完整Redis实例创建功能
- Redis实例管理和查询
- 性能监控和诊断分析
- 网络配置管理
- 备份和恢复操作
- 资源规格检查

**新增功能亮点 (v1.3.11)：**
- 📊 **分页查询支持** - 灵活的分页参数，支持大量任务数据的分页展示
- 🎯 **智能响应处理** - 兼容数组和分页对象两种响应格式，提供友好的表格输出
- ⚡ **多格式输出** - 支持table/json/yaml三种输出格式，满足不同使用场景

**常用命令：**
```bash
# 🔥 新功能：完整Redis实例创建 (支持25+参数)
ctyun-cli redis create-instance \
  --instance-name my-redis \
  --edition StandardSingle \
  --engine-version 6.0 \
  --shard-mem-size 8 \
  --zone-name cn-huabei2-tj-1a-public-ctcloud \
  --vpc-id vpc-grqvu4741a \
  --subnet-id subnet-gr36jdeyt0 \
  --secgroups sg-ufrtt04xq1 \
  --password Test@123456 \
  --dry-run

# 基础Redis实例管理
ctyun-cli redis list-instances                 # 查看Redis实例列表
ctyun-cli redis get-instance-metrics         # 获取实例性能指标
ctyun-cli redis create-backup                # 创建实例备份
ctyun-cli redis list-network-configs         # 查看网络配置
ctyun-cli redis check-resources              # 检查可用规格
ctyun-cli redis zones                        # 查询可用区信息
```

#### 💰 Billing模块 - 计费管理 (12命令/20API)
**核心功能：**
- 账户余额查询
- 月度账单统计
- 消费明细分析
- 预算管理

**常用命令：**
```bash
ctyun-cli billing balance                      # 查询账户余额
ctyun-cli billing bills                        # 查询月度账单
ctyun-cli billing details                      # 查询消费明细
ctyun-cli billing consumption-statistics     # 消费统计分析
```

#### 🛡️ Security模块 - 安全卫士 (5命令/21API)
**核心功能：**
- 安全客户端管理
- 漏洞扫描和评估
- 安全策略配置
- 风险分析报告

**常用命令：**
```bash
ctyun-cli security agents                      # 查看安全客户端
ctyun-cli security scan-result                # 查询扫描结果
ctyun-cli security vuln-list                  # 查看漏洞列表
ctyun-cli security security-risks             # 查看安全风险
```

#### 👤 IAM模块 - 身份访问管理 (2命令/2API)
**核心功能：**
- 项目管理
- 用户权限控制

**常用命令：**
```bash
ctyun-cli iam list-projects                    # 查看项目列表
ctyun-cli iam get-project-detail             # 获取项目详情
```

#### 💾 EBS模块 - 弹性块存储 (1命令/1API)
**核心功能：**
- 云硬盘管理

**常用命令：**
```bash
ctyun-cli ebs list-disks                       # 查看云硬盘列表
```

#### 🔌 CDA模块 - 云专线管理 (14命令/19API) ⭐ **NEW! (2025-12-02)**
**核心功能：**
- 专线网关生命周期管理
- 物理专线接入和配置
- VPC网络管理和路由配置
- 健康检查和链路探测
- 跨账号授权管理
- 专线交换机监控

**今日新增API (2025-12-02)：**
- 云专线健康检查状态查询
- 云专线链路探测查询
- 云专线VPC详情查询
- 专线交换机查询 (返回358台设备)
- 专线网关绑定的云间高速查询

**常用命令：**
```bash
# 专线网关管理
ctyun-cli cda gateway list                   # 查看专线网关列表
ctyun-cli cda gateway count                  # 统计专线网关数量
ctyun-cli cda gateway physical-lines        # 查看绑定的物理专线
ctyun-cli cda gateway cloud-express          # 查询绑定的云间高速 ⭐ 新增

# VPC管理
ctyun-cli cda vpc list                       # 查看VPC列表
ctyun-cli cda vpc count                      # 统计VPC数量
ctyun-cli cda vpc info                        # 查询VPC详细信息 ⭐ 新增

# 物理专线管理
ctyun-cli cda physical-line list            # 查看物理专线列表
ctyun-cli cda physical-line access-points   # 查询接入点列表
ctyun-cli cda physical-line count            # 统计物理专线数量

# 健康检查和链路探测
ctyun-cli cda health-check config           # 查询健康检查配置
ctyun-cli cda health-check status           # 查询健康检查状态 ⭐ 新增
ctyun-cli cda health-check link-probe        # 查询链路探测历史 ⭐ 新增

# 路由管理
ctyun-cli cda static-route list             # 查询静态路由
ctyun-cli cda bgp-route list                 # 查询BGP路由

# 跨账号授权
ctyun-cli cda account-auth list             # 查询跨账号授权
ctyun-cli cda account-auth count             # 统计跨账号授权

# 交换机管理
ctyun-cli cda switches                       # 查询专线交换机 ⭐ 新增
```


## 🔧 高级功能

### 多种输出格式

支持三种输出格式，满足不同场景需求：

```bash
# 表格格式（默认，适合阅读）
ctyun-cli ecs list --output table

# JSON格式（适合程序处理）
ctyun-cli ecs list --output json

# YAML格式（适合配置管理）
ctyun-cli ecs list --output yaml
```

### 多环境配置

支持配置多个环境（profile），方便在不同账号间切换：

```bash
# 配置生产环境
ctyun-cli configure --profile production

# 配置测试环境
ctyun-cli configure --profile testing

# 使用特定环境
ctyun-cli --profile production ecs list
```

### 调试模式

遇到问题时，启用调试模式查看详细信息：

```bash
ctyun-cli --debug security scan-result
```

### 管道操作

支持与其他命令组合使用：

```bash
# 将结果保存到文件
ctyun-cli ecs list --output json > instances.json

# 统计实例数量
ctyun-cli ecs list --output json | jq '. | length'

# 过滤特定状态的实例
ctyun-cli ecs list --output json | jq '.[] | select(.status == "running")'
```

## 📚 完整文档

- **[使用指南](docs/usage.md)** - 详细的使用说明和最佳实践
- **[监控服务完整文档](MONITOR_USAGE.md)** - 54个监控API完整使用指南
- **[Redis服务文档](REDIS_CLI_USAGE.md)** - Redis分布式缓存服务使用指南
- **[IAM服务文档](IAM_USAGE.md)** - 身份访问管理服务使用指南
- **[项目概述](docs/overview.md)** - 架构设计和技术说明
- **[安全指南](docs/security-guide.md)** - 安全配置和最佳实践

## 🤝 技术支持

如果您在使用过程中遇到问题或有任何建议，欢迎：

- 📧 发送邮件至技术支持团队
- 💬 提交 Issue 反馈问题：https://github.com/fengyucn/ctyun-cli/issues
- 📖 查看完整文档获取帮助

## 📋 系统要求

- Python 3.8 或更高版本
- 稳定的网络连接
- 天翼云账号和有效的 Access Key

## 🔐 安全提示

- ⚠️ 请勿在代码中硬编码 Access Key 和 Secret Key
- ✅ 推荐使用环境变量配置认证信息
- ✅ 定期轮换您的访问密钥
- ✅ 为不同用途创建不同的访问密钥

## 📝 版本信息

**当前版本：** 1.6.0 (Latest)

**重大更新 v1.6.0 - VPC模块全面升级 (2025-12-03)：**
- 🚀 **VPC new系列API完整实现** - 支持游标分页的高性能VPC查询
- ✨ **新增4个核心VPC命令** - `vpc new-list`、`vpc subnet new-list`、`vpc security new-query`、`vpc show`
- ⚡ **性能大幅提升** - 基于nextToken的游标分页，支持大数据量查询
- 🔍 **查询功能增强** - 支持模糊查询、多维度筛选、幂等性保证
- 📋 **API统计更新** - VPC模块支持11+个API接口，覆盖完整的网络管理场景

**历史版本 v1.5.0 - 账单模块全面升级 (2025-12-02)：**
- 🎉 **10个账单API完整实现** - 实现包周期、按需、消费类型汇总等完整账单查询体系
- 🆕 **新增按需账单资源+账期命令** - `ondemand-resource-cycle` 支持按资源维度和按天查询
- 🔧 **优化所有账单命令输出格式** - 统一支持 `--output json/yaml/table` 参数
- 💰 **修复金额显示问题** - 移除科学计数法，添加千分位分隔符，提升可读性
- 📊 **智能数据返回策略** - JSON/YAML返回完整原始数据，table返回用户友好格式
- 🗂️ **完整字段映射体系** - 计费模式、账单类型、支付方式等中文映射
- 🔍 **增强过滤和分页功能** - 支持产品编码、资源ID、合同ID等多维度过滤

**重大更新 v1.4.0 - 云专线CDA模块完整上线 (2025-12-02)：**
- 🔥 **全新云专线CDA服务模块** - 新增14个命令，覆盖19个API接口
- ✨ **专线网关全生命周期管理** - 创建、查询、删除、绑定物理专线等
- ✨ **物理专线接入管理** - 接入点查询、专线数量统计、详细信息获取
- ✨ **VPC网络智能管理** - VPC列表、详情查询、数量统计、路由配置
- ✨ **健康检查监控系统** - 配置查询、状态监控、链路探测历史分析
- ✨ **路由管理功能** - 静态路由和BGP路由查询配置
- ✨ **跨账号授权管理** - 授权列表查询和统计分析
- ✨ **专线交换机监控** - 358台设备实时监控和详细信息
- 🔧 **企业级EOP签名认证** - 完整的天翼云API签名机制
- 🔧 **多端点自动重试** - 提高API调用成功率和稳定性
- 📊 **完整CLI输出格式** - 支持表格、JSON、YAML三种展示格式

**重大更新 v1.3.11 - 功能增强：**
- 📊 **分页查询支持** - 灵活的pageNumber和pageSize参数，支持大量任务数据的分页展示
- 🎯 **智能响应处理** - 兼容数组和分页对象两种响应格式，提供友好的表格输出
- ⚡ **多格式输出** - 支持table/json/yaml三种输出格式，满足不同使用场景

**重大更新 v1.3.10 - IAM功能增强：**
- 🔥 **新增IAM分页查询资源信息API** - 支持完整资源字段显示
- ✨ **增强IAM命令行接口** - 包含accountid、projectsetid等完整信息
- 🔧 **优化资源数据展示** - 10列详细信息，支持智能截断和格式化

**重大更新 v1.3.9 - Redis功能全面升级：**
- 🔥 **重新开发Redis create-instance命令** - 支持完整25+API参数
- ✨ **企业级Redis实例管理** - 支持BASIC/PLUS/Classic三种版本类型
- ✨ **智能参数验证系统** - 全面的参数验证和错误提示
- ✨ **预览和资源检查功能** - --dry-run和--check-resources选项
- ✨ **完整计费模式支持** - 包年包月、自动续费、按需计费
- ✨ **高可用部署方案** - 多可用区、双副本、集群部署支持

**历史更新：**
- ✨ 新增 IAM 和 EBS 服务模块
- ✨ 优化认证机制，支持 EOP 签名
- 🔧 完善项目文档和使用指南
- 🐛 修复若干已知问题和性能优化

## 📜 开源协议

本项目采用 MIT 协议开源，欢迎使用和贡献。

**作者：Y.FENG | 邮箱：popfrog@gmail.com**

---

**🚀 让天翼云资源管理更简单！立即安装体验！**

**安装命令：** `pip install ctyun-cli`