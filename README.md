# 天翼云CLI工具

[![PyPI version](https://badge.fury.io/py/ctyun-cli.svg)](https://pypi.org/project/ctyun-cli/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

基于终端的天翼云API操作平台，提供完整的云资源管理功能。

## 📦 安装

### 从PyPI安装（推荐）

```bash
pip install ctyun-cli
```

### 从源码安装

```bash
git clone <repository-url>
cd ctyun_cli
pip install -e .
```

## 📊 项目规模

- **代码量**: 13,516 行 Python 代码
- **文件数**: 23 个核心模块
- **文档**: 1,754 行完整文档
- **模块**: 5 大核心服务模块
- **PyPI版本**: 1.0.1

## 功能特性

- 🔐 **安全认证**: 基于AK/SK的EOP签名认证机制，支持环境变量配置
- 🖥️ **ECS管理**: 云服务器、镜像、资源池等完整生命周期管理
- 🛡️ **安全卫士**: 漏洞扫描、客户端管理、安全策略配置
- 📊 **监控服务**: 28个监控API，覆盖指标查询、告警管理、事件追踪、巡检功能
- 💰 **计费查询**: 账单、消费明细、余额查询等财务管理
- 📝 **配置管理**: 灵活的配置文件和环境变量支持

## 项目结构

```
ctyun_cli/
├── src/
│   ├── auth/           # 认证模块 (EOP签名、传统签名)
│   ├── ecs/            # 云服务器管理 (1,068行)
│   ├── monitor/        # 监控服务 (6,057行 - 最大模块)
│   ├── security/       # 安全卫士 (1,439行)
│   ├── billing/        # 计费查询 (1,913行)
│   ├── cli/            # 命令行界面 (1,488行)
│   ├── config/         # 配置管理
│   ├── client.py       # 核心API客户端
│   └── utils/          # 工具函数
├── tests/              # 测试文件
├── docs/               # 文档
│   ├── usage.md        # 使用指南
│   ├── overview.md     # 项目概述
│   └── security-guide.md  # 安全指南
├── MONITOR_USAGE.md    # 监控服务使用文档
├── requirements.txt    # Python依赖
└── README.md          # 项目说明
```

## 快速开始

### 安装

```bash
# 从PyPI安装
pip install ctyun-cli

# 验证安装
ctyun-cli --version
```

### 配置认证（推荐使用环境变量）

```bash
# 方式1: 环境变量（推荐，更安全）
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key

# 方式2: 交互式配置
ctyun-cli configure

# 方式3: 命令行配置
ctyun-cli configure --access-key YOUR_AK --secret-key YOUR_SK --region cn-north-1
```

### 基本使用

```bash
# 查看帮助
ctyun-cli --help

# 显示配置
ctyun-cli show-config

# 云服务器管理
ctyun-cli ecs list                    # 列出实例
ctyun-cli ecs regions                 # 查询资源池
ctyun-cli ecs create --name "test"    # 创建实例

# 监控服务（28个API）
ctyun-cli monitor query-data --region-id <id> --metric CPUUtilization
ctyun-cli monitor query-alert-history --region-id <id>
ctyun-cli monitor query-alarm-rules --region-id <id> --service ctecs
ctyun-cli monitor query-inspection-task-overview --region-id <id>

# 安全卫士
ctyun-cli security agents             # 客户端列表
ctyun-cli security scan-result        # 扫描结果

# 计费查询
ctyun-cli billing balance             # 查询余额
ctyun-cli billing bills --month 202411  # 月度账单
```

## 监控服务功能清单

天翼云CLI提供28个完整的监控API，涵盖以下功能模块：

### 📈 指标查询（8个API）
- `query-data` - 查询监控数据
- `query-data-batch` - 批量查询监控数据
- `query-metric-list` - 查询指标列表
- `query-alert-history` - 查询告警历史
- `query-event-history` - 查询事件历史
- `query-resource-list` - 查询资源列表
- `query-dimension-values` - 查询维度值
- `query-alerted-metrics` - 查询已告警指标

### 🔝 Top-N查询（6个API）
- `query-cpu-top` - CPU使用率Top-N
- `query-mem-top` - 内存使用率Top-N
- `query-dimension-top` - 维度值Top-N
- `query-resource-top` - 资源Top-N
- `query-metric-top` - 指标Top-N
- `query-event-top` - 事件Top-N

### 🚨 告警管理（7个API）
- `query-alarm-rules` - 查询告警规则列表
- `query-alarm-rule-detail` - 查询告警规则详情
- `query-contacts` - 查询告警联系人列表
- `query-contact-detail` - 查询联系人详情
- `query-contact-groups` - 查询联系人组列表
- `query-contact-group-detail` - 查询联系人组详情
- `query-alarm-blacklist` - 查询告警黑名单

### 📋 通知与模板（3个API）
- `query-notice-templates` - 查询通知模板列表
- `query-notice-template-detail` - 查询通知模板详情
- `query-template-variables` - 查询模板变量
- `query-message-records` - 查询通知记录

### 🔍 巡检功能（5个API）
- `query-inspection-task-overview` - 查询巡检任务结果总览
- `query-inspection-task-detail` - 查询巡检任务结果详情
- `query-inspection-items` - 查询巡检项
- `query-inspection-history-list` - 查询巡检历史列表
- `query-inspection-history-detail` - 查询巡检历史详情

详细使用说明请参考 [MONITOR_USAGE.md](MONITOR_USAGE.md)

## 技术栈

- **语言**: Python 3.8+
- **CLI框架**: Click
- **HTTP客户端**: requests
- **认证机制**: 
  - 天翼云EOP签名认证（HMAC-SHA256）
  - 传统AK/SK签名
- **配置管理**: INI配置文件 + 环境变量
- **测试框架**: pytest

## 核心特性

### 🔒 安全性
- ✅ 支持环境变量配置（避免硬编码密钥）
- ✅ EOP签名认证（安全卫士、监控服务）
- ✅ 传统签名认证（ECS、计费服务）
- ✅ 所有测试文件已移除硬编码AK/SK

### 📊 监控服务（最大模块 - 6,057行）
- **28个监控API**完整覆盖：
  - 指标查询（8个）：监控数据、指标列表、告警历史、事件历史等
  - Top-N查询（6个）：CPU、内存、维度、资源、指标、事件
  - 告警管理（7个）：告警规则、联系人、联系人组、黑名单
  - 通知与模板（4个）：通知模板、模板变量、通知记录
  - 巡检功能（5个）：任务总览、任务详情、巡检项、巡检历史
- 自定义监控、告警规则、联系人管理
- 详见 [MONITOR_USAGE.md](MONITOR_USAGE.md)

### 🛡️ 安全卫士
- 漏洞扫描结果查询
- 客户端管理
- 专用EOP签名认证

### 💰 计费查询
- 账户余额、账单查询
- 消费明细、账户流水
- 月度消费统计

## 文档

- [使用指南](docs/usage.md) - 详细的使用说明
- [监控服务文档](MONITOR_USAGE.md) - 20+ 监控API使用指南
- [项目概述](docs/overview.md) - 架构设计说明
- [安全指南](docs/security-guide.md) - 安全最佳实践
- [开发指南](AGENTS.md) - 开发者参考