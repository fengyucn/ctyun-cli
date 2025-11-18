# 天翼云 CLI 工具

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一款不太强大不太完整的天翼云命令行工具，帮助您在终端中轻松管理云资源。支持云服务器、监控告警、安全防护、费用查询等核心功能。

简体中文 | [English](README_EN.md)

## ✨ 为什么选择天翼云 CLI？

- 🚀 **高效便捷** - 控制台太丑、API太烂，CLI没有，只好自己写个CLI，一行命令完成云资源查询和管理，告别繁琐的控制台操作
- 🔐 **安全可靠** - 采用企业级 EOP 签名认证，支持环境变量配置保护密钥安全
- 📊 **功能全面** - 涵盖 70+ 个 API，管理云服务器、监控告警、安全防护、费用账单
- 🎯 **简单易用** - 清晰的命令结构，丰富的使用示例，5分钟快速上手
- 🔧 **灵活配置** - 支持配置文件、环境变量等多种配置方式

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

## 🎯 核心功能

### 🖥️ 云服务器管理（ECS）

管理您的云服务器实例，包括查询、监控、快照、备份等完整功能。

```bash
# 查看所有云服务器实例
ctyun-cli ecs list

# 查询资源池信息
ctyun-cli ecs regions

# 查询云服务器自动续订配置
ctyun-cli ecs get-auto-renew-config --region-id cn-north-1 --instance-id i-xxxxx

# 查询快照列表
ctyun-cli ecs list-snapshots --region-id cn-north-1

# 查询云硬盘统计信息
ctyun-cli ecs get-volume-statistics --region-id cn-north-1

# 查询密钥对列表
ctyun-cli ecs list-keypairs --region-id cn-north-1

# 查询备份策略
ctyun-cli ecs list-backup-policies --region-id cn-north-1

# 查询云主机组列表
ctyun-cli ecs list-affinity-groups --region-id cn-north-1
```

**支持的功能清单：**
- ✅ 实例查询与状态管理
- ✅ 资源池与可用区查询
- ✅ 快照管理（列表、详情）
- ✅ 云硬盘管理与统计
- ✅ 密钥对管理
- ✅ 备份策略与状态查询
- ✅ DNS 记录查询
- ✅ 云主机组管理
- ✅ 异步任务查询
- ✅ 自动续订配置

### 📊 监控与告警

实时监控云资源运行状态，设置告警规则，及时发现问题。

```bash
# 查询监控数据（CPU使用率）
ctyun-cli monitor query-data --region-id cn-north-1 --metric CPUUtilization

# 查询告警历史
ctyun-cli monitor query-alert-history --region-id cn-north-1

# 查询告警规则
ctyun-cli monitor query-alarm-rules --region-id cn-north-1 --service ctecs

# 查询 CPU 使用率 Top 10
ctyun-cli monitor query-cpu-top --region-id cn-north-1 --top-n 10

# 查询内存使用率 Top 10
ctyun-cli monitor query-mem-top --region-id cn-north-1 --top-n 10

# 查询巡检任务总览
ctyun-cli monitor query-inspection-task-overview --region-id cn-north-1
```

**监控功能模块：**
- 📈 **指标查询**（8个API）- 监控数据、指标列表、告警历史、事件历史
- 🔝 **Top-N 查询**（6个API）- CPU、内存、维度、资源、指标、事件排行
- 🚨 **告警管理**（7个API）- 告警规则、联系人、联系人组、黑名单
- 📋 **通知管理**（4个API）- 通知模板、模板变量、通知记录
- 🔍 **巡检功能**（5个API）- 巡检任务、巡检项、巡检历史

详细使用说明请参考 → [监控服务完整文档](MONITOR_USAGE.md)

### 🛡️ 安全防护

查看安全防护状态，管理漏洞扫描和安全策略。

```bash
# 查看安全客户端列表
ctyun-cli security agents

# 查询安全扫描结果
ctyun-cli security scan-result

# 查询特定客户端的漏洞列表
ctyun-cli security vuln-list <agent_guid>
```

### 💰 费用管理

随时掌握云资源费用情况，查询账单和消费明细。

```bash
# 查询账户余额
ctyun-cli billing balance

# 查询月度账单
ctyun-cli billing bills --month 202411

# 查询消费明细
ctyun-cli billing details --start-date 2024-11-01 --end-date 2024-11-30
```

## 🔧 高级配置

### 配置文件位置

配置文件默认保存在 `~/.ctyun/config`，采用 INI 格式：

```ini
[default]
access_key = YOUR_ACCESS_KEY
secret_key = YOUR_SECRET_KEY
region = cn-north-1
endpoint = https://api.ctyun.cn
output_format = table
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

### 输出格式

支持三种输出格式，满足不同场景需求：

```bash
# 表格格式（默认，适合阅读）
ctyun-cli ecs list --output table

# JSON 格式（适合程序处理）
ctyun-cli ecs list --output json

# YAML 格式（适合配置管理）
ctyun-cli ecs list --output yaml
```

### 调试模式

遇到问题时，启用调试模式查看详细信息：

```bash
ctyun-cli --debug security scan-result
```

## 📚 完整文档

- [使用指南](docs/usage.md) - 详细的使用说明和最佳实践
- [监控服务文档](MONITOR_USAGE.md) - 28个监控API完整使用指南
- [项目概述](docs/overview.md) - 架构设计和技术说明
- [安全指南](docs/security-guide.md) - 安全配置和最佳实践

## 🤝 技术支持

如果您在使用过程中遇到问题或有任何建议，欢迎：

- 📧 发送邮件至技术支持团队
- 💬 提交 Issue 反馈问题
- 📖 查看完整文档获取帮助

## 📋 系统要求

- Python 3.8 或更高版本
- 稳定的网络连接
- 天翼云账号和 Access Key

## 🔐 安全提示

- ⚠️ 请勿在代码中硬编码 Access Key 和 Secret Key
- ✅ 推荐使用环境变量配置认证信息
- ✅ 定期轮换您的访问密钥
- ✅ 为不同用途创建不同的访问密钥

## 📝 版本信息

**当前版本：** 1.1.0

**更新内容：**
- ✨ 新增 19 个 ECS 查询类 API
- ✨ 完整的监控服务支持（28个API）
- 🔧 优化认证机制，支持 EOP 签名
- 🐛 修复若干已知问题

## 📜 开源协议

本项目采用 MIT 协议开源，欢迎使用和贡献。

---

**开始使用天翼云 CLI，让云资源管理更简单！** 🚀
