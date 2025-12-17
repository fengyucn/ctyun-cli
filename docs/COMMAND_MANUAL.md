# 天翼云CLI完整指令手册

## 📚 目录

- [1. 安装与配置](#1-安装与配置)
- [2. 全局选项](#2-全局选项)
- [3. ECS云服务器管理](#3-ecs云服务器管理)
- [4. 监控服务（28个API）](#4-监控服务28个api)
  - [4.1 指标查询（8个API）](#41-指标查询8个api)
  - [4.2 Top-N查询（6个API）](#42-top-n查询6个api)
  - [4.3 告警管理（7个API）](#43-告警管理7个api)
  - [4.4 通知与模板（4个API）](#44-通知与模板4个api)
  - [4.5 巡检功能（5个API）](#45-巡检功能5个api)
  - [4.6 自定义监控](#46-自定义监控)
  - [4.7 云专线监控](#47-云专线监控)
- [5. 安全卫士管理](#5-安全卫士管理)
- [6. 计费查询](#6-计费查询)
- [7. 配置管理](#7-配置管理)
- [8. 输出格式](#8-输出格式)
- [9. 常见问题](#9-常见问题)

---

## 1. 安装与配置

### 1.1 环境要求
- Python 3.8+
- 操作系统: Windows, macOS, Linux

### 1.2 安装

#### 从PyPI安装（推荐）
```bash
pip install ctyun-cli
```

#### 从源码安装
```bash
git clone https://github.com/fengyucn/ctyun-cli.git
cd ctyun_cli
pip install -e .
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 验证安装
```bash
ctyun-cli --version
```

### 1.3 配置认证

#### 方式1: 环境变量（推荐，最安全）
```bash
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key
export CTYUN_REGION=cn-north-1  # 可选
```

#### 方式2: 交互式配置
```bash
ctyun-cli configure
```

#### 方式3: 命令行配置
```bash
ctyun-cli configure \
    --access-key YOUR_ACCESS_KEY \
    --secret-key YOUR_SECRET_KEY \
    --region cn-north-1 \
    --output table
```

#### 方式4: 手动配置脚本
```bash
# 对于旧版本，可以使用
python setup_config.py
```

### 1.4 配置文件

#### 配置文件位置
配置文件默认保存在：`~/.ctyun/config`

#### 配置文件格式（INI）
```ini
[default]
access_key = YOUR_ACCESS_KEY
secret_key = YOUR_SECRET_KEY
region = cn-north-1
endpoint = https://api.ctyun.cn
timeout = 30
retry = 3
output_format = table

[logging]
level = INFO
file =
max_size = 10MB
backup_count = 5
```

#### 查看当前配置
```bash
ctyun-cli show-config
```

#### 列出所有配置文件
```bash
ctyun-cli list-profiles
```

### 1.5 基本用法

#### 全局选项
- `--profile`: 指定配置文件
- `--output`: 输出格式 (table/json/yaml)
- `--debug`: 启用调试模式
- `--region`: 指定区域
- `--access-key`: 访问密钥
- `--secret-key`: 密钥

#### 命令格式
```bash
ctyun-cli [全局选项] <命令组> <子命令> [选项] [参数]
```

#### 多配置文件支持
```bash
# 创建开发环境配置
ctyun-cli configure --profile dev \
    --access-key YOUR_DEV_ACCESS_KEY \
    --secret-key YOUR_DEV_SECRET_KEY \
    --region cn-north-1

# 使用开发环境配置
ctyun-cli --profile dev ecs list
```

### 1.6 高级配置

#### 环境变量覆盖
```bash
export CTYUN_ACCESS_KEY=YOUR_ACCESS_KEY
export CTYUN_SECRET_KEY=YOUR_SECRET_KEY
export CTYUN_REGION=cn-north-1

ctyun-cli ecs list
```

#### 配置文件覆盖
```bash
# 命令行参数覆盖配置文件
ctyun-cli --region cn-east-1 ecs list
```

#### 1.8 安全配置示例
```bash
# 生产环境配置示例
ctyun-cli configure --profile production \
    --access-key YOUR_PROD_ACCESS_KEY \
    --secret-key YOUR_PROD_SECRET_KEY \
    --region cn-north-1

# 测试环境配置示例
ctyun-cli configure --profile staging \
    --access-key YOUR_STAGING_ACCESS_KEY \
    --secret-key YOUR_STAGING_SECRET_KEY \
    --region cn-north-1
```

#### 临时使用环境变量
```bash
CTYUN_ACCESS_KEY=xxx CTYUN_SECRET_KEY=yyy ctyun-cli ecs list
```

### 1.7 安全最佳实践

#### 1.7.1 安全配置建议
- 不要在脚本中硬编码密钥
- 使用环境变量或配置文件
- 定期轮换密钥
- 限制配置文件权限 (600)

#### 1.7.2 批量操作注意事项
- 使用批量操作提高效率
- 在批量删除前先列出不确认
- 监控批量操作状态

#### 1.7.3 监控和日志
- 启用调试模式排查问题
- 配置日志文件记录操作
- 设置监控告警

#### 1.7.4 自动化脚本示例
```bash
#!/bin/bash
# 自动化脚本示例

# 检查实例状态
ctyun-cli ecs show i-12345678 --output json | jq -r '.status'

# 批量启动停止的实例
for instance in $(ctyun-cli ecs list --status stopped --output json | jq -r '.[].instanceId'); do
    ctyun-cli ecs start $instance
    echo "启动实例: $instance"
done
```

---

## 2. 全局选项

所有命令都支持以下全局选项：

```bash
ctyun-cli [全局选项] <命令> [命令选项]
```

### 全局选项列表

| 选项 | 说明 | 默认值 | 示例 |
|-----|------|--------|------|
| `--version` | 显示版本信息 | - | `ctyun-cli --version` |
| `--help` | 显示帮助信息 | - | `ctyun-cli --help` |
| `--debug` | 启用调试模式（显示详细日志） | False | `ctyun-cli --debug monitor query-data ...` |
| `--output` | 输出格式 | table | `ctyun-cli --output json monitor query-data ...` |
| `--profile` | 使用指定配置文件 | default | `ctyun-cli --profile prod monitor query-data ...` |

### 示例
```bash
# 调试模式查询监控数据
ctyun-cli --debug monitor query-cpu-top --region-id 200000001852

# JSON格式输出
ctyun-cli --output json security agents

# 使用生产环境配置
ctyun-cli --profile prod ecs list
```

---

## 3. ECS云服务器管理

### 3.1 查询资源池列表
```bash
ctyun-cli ecs regions
```

### 3.2 列出云服务器实例
```bash
# 列出所有实例
ctyun-cli ecs list

# 指定资源池
ctyun-cli ecs list --region-id 200000001852

# JSON格式输出
ctyun-cli ecs list --output json
```

### 3.3 创建云服务器
```bash
ctyun-cli ecs create \
    --name "my-server" \
    --instance-type "s6.small" \
    --region-id 200000001852
```

### 3.4 查询镜像列表
```bash
ctyun-cli ecs images --region-id 200000001852
```

### 3.5 实例管理

#### 启动、停止、重启实例
```bash
# 启动实例
ctyun-cli ecs start <instance-id>

# 停止实例
ctyun-cli ecs stop <instance-id>

# 重启实例
ctyun-cli ecs reboot <instance-id>

# 删除实例 (需要确认)
ctyun-cli ecs delete <instance-id> --confirm
```

#### 批量操作
```bash
# 批量启动实例
ctyun-cli ecs batch-start <instance-id1> <instance-id2> [<instance-id3> ...]

# 批量停止实例
ctyun-cli ecs batch-stop <instance-id1> <instance-id2> [<instance-id3> ...]

# 批量删除实例 (需要确认)
ctyun-cli ecs batch-delete <instance-id1> <instance-id2> [--confirm]
```

#### 实例规格管理
```bash
# 列出可用实例规格
ctyun-cli ecs instance-types

# 调整实例规格
ctyun-cli ecs resize <instance-id> <instance-type>
```

#### 镜像管理
```bash
# 列出公共镜像
ctyun-cli ecs images --type public

# 列出Ubuntu镜像
ctyun-cli ecs images --os-type Ubuntu

# 创建实例镜像
ctyun-cli ecs create-image <instance-id> --name "<image-name>" --description "<image-description>"
```

#### 控制台和监控
```bash
# 获取实例控制台URL
ctyun-cli ecs console <instance-id>

# 获取实例监控数据
ctyun-cli ecs monitoring <instance-id> <metric-name> <start-time> <end-time>
```

#### 示例使用
```bash
# 启动实例示例
ctyun-cli ecs start i-12345678

# 批量启动实例示例
ctyun-cli ecs batch-start i-12345678 i-87654321 i-55555555

# 调整实例规格示例
ctyun-cli ecs resize i-12345678 s6.medium

# 创建镜像示例
ctyun-cli ecs create-image i-12345678 --name "my-server-backup" --description "Weekly backup image"

# 监控CPU使用率示例
ctyun-cli ecs monitoring i-12345678 CPUUtilization 2024-01-01T00:00:00Z 2024-01-01T23:59:59Z
```

---

## 4. 监控服务（28个API）

天翼云监控服务提供完整的监控能力，包括指标查询、告警管理、Top-N查询、巡检功能等。

**API端点**: `https://monitor-global.ctapi.ctyun.cn`  
**认证方式**: EOP签名认证  
**总API数量**: 28个

---

## 4.1 指标查询（8个API）

### 4.1.1 查询监控数据

查询指定资源的监控指标数据。

```bash
ctyun-cli monitor query-data \
    --region-id <资源池ID> \
    --metric <指标名称>
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--region-id` | 是 | 资源池ID | `200000001852` 或 `bb9fdb42056f11eda1610242ac110002` |
| `--metric` | 是 | 指标名称 | `CPUUtilization`、`MemoryUtilization` |
| `--resource-id` | 否 | 资源ID | `i-12345678` |
| `--start-time` | 否 | 开始时间（Unix时间戳，秒） | `1699000000` |
| `--end-time` | 否 | 结束时间（Unix时间戳，秒） | `1699086400` |
| `--period` | 否 | 聚合周期（秒） | `300` |

#### 示例
```bash
# 查询CPU使用率
ctyun-cli monitor query-data \
    --region-id <region-id> \
    --metric CPUUtilization

# 指定时间范围和资源ID
ctyun-cli monitor query-data \
    --region-id <region-id> \
    --metric CPUUtilization \
    --resource-id <resource-id> \
    --start-time 1699000000 \
    --end-time 1699086400

# 具体示例
ctyun-cli monitor query-data \
    --region-id 200000001852 \
    --metric CPUUtilization

ctyun-cli monitor query-data \
    --region-id 200000001852 \
    --metric CPUUtilization \
    --resource-id i-12345678 \
    --start-time 1699000000 \
    --end-time 1699086400
```

#### 常用指标名称
- `CPUUtilization`: CPU使用率
- `MemoryUtilization`: 内存使用率
- `DiskUtilization`: 磁盘使用率
- `NetworkInBytes`: 网络流入字节数
- `NetworkOutBytes`: 网络流出字节数

---

### 4.1.2 批量查询监控数据

批量查询多个资源的监控数据。

```bash
ctyun-cli monitor query-data-batch \
    --region-id <资源池ID> \
    --service <服务类型>
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--region-id` | 是 | 资源池ID | `200000001852` |
| `--service` | 是 | 服务类型 | `ctecs` |
| `--resource-ids` | 否 | 资源ID列表（多个） | `instance-1 instance-2` |
| `--metric` | 否 | 指标名称 | `CPUUtilization` |

#### 示例
```bash
ctyun-cli monitor query-data-batch \
    --region-id 200000001852 \
    --service ctecs \
    --resource-ids instance-1 instance-2 instance-3
```

---

### 4.1.3 查询指标列表

查询指定服务的可用监控指标列表。

```bash
ctyun-cli monitor query-metric-list \
    --region-id <资源池ID> \
    --service <服务类型>
```

#### 示例
```bash
# 查询ECS服务的所有可用指标
ctyun-cli monitor query-metric-list \
    --region-id 200000001852 \
    --service ctecs

# JSON格式输出
ctyun-cli --output json monitor query-metric-list \
    --region-id 200000001852 \
    --service ctecs
```

---

### 4.1.4 查询告警历史

查询资源池的告警历史记录。

```bash
ctyun-cli monitor query-alert-history \
    --region-id <资源池ID>
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--region-id` | 是 | 资源池ID | `200000001852` |
| `--start-time` | 否 | 开始时间 | `1699000000` |
| `--end-time` | 否 | 结束时间 | `1699086400` |
| `--page-no` | 否 | 页码 | `1` |
| `--page-size` | 否 | 每页条数 | `20` |

#### 示例
```bash
# 查询最近告警
ctyun-cli monitor query-alert-history \
    --region-id 200000001852

# 指定时间范围和分页
ctyun-cli monitor query-alert-history \
    --region-id 200000001852 \
    --start-time 1699000000 \
    --end-time 1699086400 \
    --page-no 1 \
    --page-size 50
```

---

### 4.1.5 查询事件历史

查询事件监控历史。

```bash
ctyun-cli monitor query-event-history \
    --region-id <资源池ID>
```

#### 示例
```bash
ctyun-cli monitor query-event-history \
    --region-id 200000001852 \
    --start-time 1699000000 \
    --end-time 1699086400
```

---

### 4.1.6 查询资源列表

查询指定服务的资源列表。

```bash
ctyun-cli monitor query-resource-list \
    --region-id <资源池ID> \
    --service <服务类型>
```

#### 示例
```bash
ctyun-cli monitor query-resource-list \
    --region-id 200000001852 \
    --service ctecs
```

---

### 4.1.7 查询维度值

查询指定维度的可用值列表。

```bash
ctyun-cli monitor query-dimension-values \
    --region-id <资源池ID> \
    --service <服务类型> \
    --dimension <维度名称>
```

#### 示例
```bash
ctyun-cli monitor query-dimension-values \
    --region-id 200000001852 \
    --service ctecs \
    --dimension instance
```

---

### 4.1.8 查询已告警指标

查询当前处于告警状态的指标。

```bash
ctyun-cli monitor query-alerted-metrics \
    --region-id <资源池ID>
```

#### 示例
```bash
ctyun-cli monitor query-alerted-metrics \
    --region-id 200000001852
```

---

## 4.2 Top-N查询（6个API）

### 4.2.1 CPU使用率Top-N

查询CPU使用率最高的资源。

```bash
ctyun-cli monitor query-cpu-top \
    --region-id <资源池ID> \
    [--number <N>]
```

#### 参数说明
| 参数 | 必需 | 说明 | 默认值 | 示例 |
|-----|------|------|--------|------|
| `--region-id` | 是 | 资源池ID | - | `200000001852` 或 `bb9fdb42056f11eda1610242ac110002` |
| `--number` | 否 | Top数量 | 3 | `10` |

#### 示例
```bash
# 查询Top 3（默认）
ctyun-cli monitor query-cpu-top \
    --region-id 200000001852

# 查询Top 10
ctyun-cli monitor query-cpu-top \
    --region-id 200000001852 \
    --number 10

# JSON格式输出
ctyun-cli --output json monitor query-cpu-top \
    --region-id 200000001852 \
    --number 10
```

#### 输出示例
```
云主机CPU使用率 Top 3
================================================================================
排名    设备ID                                    设备名称         CPU使用率(%)
#1      3080069a-ca2b-fca1-f038-5e6e00dd7630     prod-server     56.69%
#2      0582fe3b-97bd-ac16-2b88-1c1a84fe89ce     test-server     46.70%
#3      b7862cdf-6b1b-bdfd-8410-ba71d2a7ecb8     dev-server      45.03%

共找到 3 台云主机
CPU使用率统计:
  最高: 56.69%
  最低: 45.03%
  平均: 49.47%
```

---

### 4.2.2 内存使用率Top-N

查询内存使用率最高的资源。

```bash
ctyun-cli monitor query-mem-top \
    --region-id <资源池ID> \
    [--number <N>]
```

#### 示例
```bash
# 查询Top 10
ctyun-cli monitor query-mem-top \
    --region-id 200000001852 \
    --number 10
```

---

### 4.2.3 维度值Top-N

查询指定维度的Top-N值。

```bash
ctyun-cli monitor query-dimension-top \
    --region-id <资源池ID> \
    --dimension <维度名称> \
    --metric <指标名称>
```

#### 示例
```bash
ctyun-cli monitor query-dimension-top \
    --region-id 200000001852 \
    --dimension instance \
    --metric CPUUtilization
```

---

### 4.2.4 资源Top-N

查询资源使用Top-N。

```bash
ctyun-cli monitor query-resource-top \
    --region-id <资源池ID> \
    --service <服务类型>
```

#### 示例
```bash
ctyun-cli monitor query-resource-top \
    --region-id 200000001852 \
    --service ctecs \
    --number 10
```

---

### 4.2.5 指标Top-N

查询指标值Top-N。

```bash
ctyun-cli monitor query-metric-top \
    --region-id <资源池ID> \
    --metric <指标名称>
```

#### 示例
```bash
ctyun-cli monitor query-metric-top \
    --region-id 200000001852 \
    --metric CPUUtilization \
    --number 10
```

---

### 4.2.6 事件Top-N

查询事件发生次数Top-N。

```bash
ctyun-cli monitor query-event-top \
    --region-id <资源池ID>
```

#### 示例
```bash
ctyun-cli monitor query-event-top \
    --region-id 200000001852 \
    --number 10
```

---

## 4.3 告警管理（7个API）

### 4.3.1 查询告警规则列表

查询告警规则列表。

```bash
ctyun-cli monitor query-alarm-rules \
    --region-id <资源池ID> \
    --service <服务类型>
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--region-id` | 是 | 资源池ID | `200000001852` |
| `--service` | 是 | 服务类型 | `ctecs` |
| `--alarm-status` | 否 | 告警状态（0=停用，1=启用） | `1` |
| `--page-no` | 否 | 页码 | `1` |
| `--page-size` | 否 | 每页条数 | `20` |

#### 示例
```bash
# 查询所有告警规则
ctyun-cli monitor query-alarm-rules \
    --region-id 200000001852 \
    --service ctecs

# 只查询启用的规则
ctyun-cli monitor query-alarm-rules \
    --region-id 200000001852 \
    --service ctecs \
    --alarm-status 1

# 分页查询
ctyun-cli monitor query-alarm-rules \
    --region-id 200000001852 \
    --service ctecs \
    --page-no 1 \
    --page-size 50
```

---

### 4.3.2 查询告警规则详情

查询指定告警规则的详细信息。

```bash
ctyun-cli monitor describe-alarm-rule \
    --region-id <资源池ID> \
    --alarm-rule-id <告警规则ID>
```

#### 示例
```bash
ctyun-cli monitor describe-alarm-rule \
    --region-id 200000001852 \
    --alarm-rule-id rule-xxx
```

---

### 4.3.3 查询联系人列表

查询告警联系人列表。

```bash
ctyun-cli monitor query-contacts
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--name` | 否 | 联系人姓名（模糊搜索） | `张三` |
| `--email` | 否 | 联系人邮箱 | `user@example.com` |
| `--page-no` | 否 | 页码 | `1` |
| `--page-size` | 否 | 每页条数 | `20` |

#### 示例
```bash
# 查询所有联系人
ctyun-cli monitor query-contacts

# 按姓名搜索
ctyun-cli monitor query-contacts --name "张三"

# 分页查询
ctyun-cli monitor query-contacts \
    --page-no 1 \
    --page-size 50
```

---

### 4.3.4 查询联系人详情

查询联系人详细信息。

```bash
ctyun-cli monitor describe-contact \
    --contact-id <联系人ID>
```

#### 示例
```bash
ctyun-cli monitor describe-contact \
    --contact-id <contact-id>

# 具体示例
ctyun-cli monitor describe-contact \
    --contact-id 12345678-1234-1234-1234-123456789abc
```

---

### 4.3.5 查询联系人组列表

查询联系人组列表。

```bash
ctyun-cli monitor query-contact-groups
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--name` | 否 | 联系人组名称（模糊搜索） | `运维组` |
| `--page-no` | 否 | 页码 | `1` |
| `--page-size` | 否 | 每页条数 | `20` |

#### 示例
```bash
# 查询所有联系人组
ctyun-cli monitor query-contact-groups

# 按名称搜索
ctyun-cli monitor query-contact-groups --name "运维组"
```

---

### 4.3.6 查询联系人组详情

查询联系人组详细信息。

```bash
ctyun-cli monitor describe-contact-group \
    --contact-group-id <联系人组ID>
```

#### 示例
```bash
ctyun-cli monitor describe-contact-group \
    --contact-group-id <contact-group-id>

# 具体示例
ctyun-cli monitor describe-contact-group \
    --contact-group-id 12345678-1234-1234-1234-123456789abc
```

---

### 4.3.7 查询告警黑名单

查询告警黑名单配置。

```bash
ctyun-cli monitor query-alarm-blacklist \
    --region-id <资源池ID>
```

#### 示例
```bash
ctyun-cli monitor query-alarm-blacklist \
    --region-id 200000001852
```

---

## 4.4 通知与模板（4个API）

### 4.4.1 查询通知模板列表

查询通知模板列表。

```bash
ctyun-cli monitor query-notice-templates
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--page-no` | 否 | 页码 | `1` |
| `--page-size` | 否 | 每页条数 | `20` |

#### 示例
```bash
# 查询所有通知模板
ctyun-cli monitor query-notice-templates

# 分页查询
ctyun-cli monitor query-notice-templates \
    --page-no 1 \
    --page-size 50
```

---

### 4.4.2 查询通知模板详情

查询通知模板详细信息。

```bash
ctyun-cli monitor describe-notice-template \
    --template-id <模板ID>
```

#### 示例
```bash
ctyun-cli monitor describe-notice-template \
    --template-id template-xxx
```

---

### 4.4.3 查询模板变量

查询通知模板可用变量。

```bash
ctyun-cli monitor query-template-variables
```

#### 示例
```bash
ctyun-cli monitor query-template-variables
```

---

### 4.4.4 查询通知记录

查询通知发送记录。

```bash
ctyun-cli monitor query-message-records \
    --start-time <开始时间> \
    --end-time <结束时间>
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--start-time` | 是 | 开始时间（Unix时间戳，秒） | `1699000000` |
| `--end-time` | 是 | 结束时间（Unix时间戳，秒） | `1699086400` |
| `--page-no` | 否 | 页码 | `1` |
| `--page-size` | 否 | 每页条数 | `20` |

#### 示例
```bash
# 查询最近通知记录
ctyun-cli monitor query-message-records \
    --start-time 1699000000 \
    --end-time 1699086400

# 分页查询
ctyun-cli monitor query-message-records \
    --start-time 1699000000 \
    --end-time 1699086400 \
    --page-no 1 \
    --page-size 50
```

---

## 4.5 巡检功能（5个API）

### 4.5.1 查询巡检任务结果总览

查询巡检任务执行结果的总览信息。

```bash
ctyun-cli monitor query-inspection-task-overview \
    --region-id <资源池ID>
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--region-id` | 是 | 资源池ID | `200000001852` 或 `bb9fdb42056f11eda1610242ac110002` |
| `--task-id` | 否 | 巡检任务ID | `<task-uuid>` |

#### 示例
```bash
# 查询所有巡检任务
ctyun-cli monitor query-inspection-task-overview \
    --region-id 200000001852

# 查询指定任务
ctyun-cli monitor query-inspection-task-overview \
    --region-id <region-id> \
    --task-id <task-id>

# 具体示例
ctyun-cli monitor query-inspection-task-overview \
    --region-id 200000001852 \
    --task-id 12345678-1234-1234-1234-123456789abc
```

#### 输出说明
- **任务状态**: 运行中(1)、已完成(2)、失败(3)
- 包含任务ID、创建时间、完成时间、巡检结果等信息

---

### 4.5.2 查询巡检任务结果详情

查询巡检任务的详细检查结果。

```bash
ctyun-cli monitor query-inspection-task-detail \
    --task-id <任务ID> \
    --inspection-type <巡检类型>
```

#### 参数说明
| 参数 | 必需 | 说明 | 可选值 |
|-----|------|------|--------|
| `--task-id` | 是 | 巡检任务ID | - |
| `--inspection-type` | 是 | 巡检类型 | `1`=健康评估, `2`=风险识别 |
| `--page-no` | 否 | 页码 | 默认1 |
| `--page-size` | 否 | 每页条数 | 默认20 |

#### 示例
```bash
# 查询健康评估详情
ctyun-cli monitor query-inspection-task-detail \
    --task-id <task-id> \
    --inspection-type 1

# 查询风险识别详情（分页）
ctyun-cli monitor query-inspection-task-detail \
    --task-id <task-id> \
    --inspection-type 2 \
    --page-no 1 \
    --page-size 50

# 具体示例
ctyun-cli monitor query-inspection-task-detail \
    --task-id 12345678-1234-1234-1234-123456789abc \
    --inspection-type 1

ctyun-cli monitor query-inspection-task-detail \
    --task-id 12345678-1234-1234-1234-123456789abc \
    --inspection-type 2 \
    --page-no 1 \
    --page-size 50
```

---

### 4.5.3 查询巡检项

查询系统支持的巡检项列表。

```bash
ctyun-cli monitor query-inspection-items
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--inspection-type` | 否 | 巡检类型（1=健康评估，2=风险识别） | `1` |
| `--search` | 否 | 搜索关键字 | `CPU` |

#### 示例
```bash
# 查询所有巡检项
ctyun-cli monitor query-inspection-items

# 按类型过滤
ctyun-cli monitor query-inspection-items \
    --inspection-type 1

# 模糊搜索
ctyun-cli monitor query-inspection-items \
    --search "CPU"
```

#### 输出内容
- 巡检项ID和名称
- 巡检类型（健康评估/风险识别）
- 巡检项描述

---

### 4.5.4 查询巡检历史列表

查询历史巡检任务列表。

```bash
ctyun-cli monitor query-inspection-history-list \
    --region-id <资源池ID>
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--region-id` | 是 | 资源池ID | `200000001852` |
| `--start-time` | 否 | 开始时间 | `1699000000` |
| `--end-time` | 否 | 结束时间 | `1699086400` |
| `--page-no` | 否 | 页码 | `1` |
| `--page-size` | 否 | 每页条数 | `20` |

#### 示例
```bash
# 查询所有历史记录
ctyun-cli monitor query-inspection-history-list \
    --region-id 200000001852

# 指定时间范围
ctyun-cli monitor query-inspection-history-list \
    --region-id 200000001852 \
    --start-time 1699000000 \
    --end-time 1699086400

# 分页查询
ctyun-cli monitor query-inspection-history-list \
    --region-id 200000001852 \
    --page-no 1 \
    --page-size 50
```

#### 输出信息
- 任务ID、执行时间
- 巡检结果统计
- 任务状态

---

### 4.5.5 查询巡检历史详情

查询指定巡检任务的详细历史记录。

```bash
ctyun-cli monitor query-inspection-history-detail \
    --task-id <任务ID> \
    --inspection-item <巡检项>
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--task-id` | 是 | 巡检任务ID | `<task-uuid>` |
| `--inspection-item` | 是 | 巡检项编号 | `1` |
| `--page-no` | 否 | 页码 | `1` |
| `--page-size` | 否 | 每页条数 | `20` |

#### 示例
```bash
ctyun-cli monitor query-inspection-history-detail \
    --task-id task-xxx \
    --inspection-item 1

# 分页查询
ctyun-cli monitor query-inspection-history-detail \
    --task-id task-xxx \
    --inspection-item 1 \
    --page-no 1 \
    --page-size 50
```

---

## 4.6 自定义监控

### 4.6.1 查询自定义监控趋势数据

查询自定义监控项的时序指标趋势监控数据。

```bash
ctyun-cli monitor custom-trend \
    --region-id <资源池ID> \
    --custom-item-id <自定义监控项ID>
```

#### 参数说明
| 参数 | 必需 | 说明 | 示例 |
|-----|------|------|------|
| `--region-id` | 是 | 资源池ID | `81f7728662dd11ec810800155d307d5b` |
| `--custom-item-id` | 是 | 自定义监控项ID | `<custom-item-uuid>` |
| `--start-time` | 否 | 开始时间（Unix时间戳，秒） | `1687158009` |
| `--end-time` | 否 | 结束时间（Unix时间戳，秒） | `1687158309` |
| `--period` | 否 | 聚合周期（秒） | `300` |
| `--dimension` | 否 | 维度过滤（可多次指定） | `uuid=xxx` |

#### 示例
```bash
# 查询最近24小时的监控数据
ctyun-cli monitor custom-trend \
    --region-id <region-id> \
    --custom-item-id <custom-item-id>

# 查询指定时间段和维度的监控数据
ctyun-cli monitor custom-trend \
    --region-id <region-id> \
    --custom-item-id <custom-item-id> \
    --start-time 1687158009 \
    --end-time 1687158309 \
    --dimension uuid=<uuid-value> \
    --dimension job=virtual_machine,bare_metal

# 具体示例
ctyun-cli monitor custom-trend \
    --region-id 81f7728662dd11ec810800155d307d5b \
    --custom-item-id 12345678-1234-1234-1234-123456789abc

ctyun-cli monitor custom-trend \
    --region-id 81f7728662dd11ec810800155d307d5b \
    --custom-item-id 12345678-1234-1234-1234-123456789abc \
    --start-time 1687158009 \
    --end-time 1687158309 \
    --dimension uuid=00350e57-67af-f1db-1fa5-20193d873f5d \
    --dimension job=virtual_machine,bare_metal
```

---

### 4.6.2 查询自定义监控历史数据

查询自定义监控的历史数据。

```bash
ctyun-cli monitor query-custom-history \
    --region-id <资源池ID> \
    --custom-item-id <自定义监控项ID>
```

---

### 4.6.3 查询自定义监控维度值

查询自定义监控的维度值列表。

```bash
ctyun-cli monitor query-custom-dimension-values \
    --region-id <资源池ID> \
    --custom-item-id <自定义监控项ID>
```

---

### 4.6.4 查询自定义监控项列表

查询自定义监控项列表。

```bash
ctyun-cli monitor query-custom-items \
    --region-id <资源池ID>
```

---

### 4.6.5 查询自定义告警规则

查询自定义监控告警规则列表。

```bash
ctyun-cli monitor query-custom-alarm-rules \
    --region-id <资源池ID>
```

---

### 4.6.6 查询自定义告警规则详情

查询自定义监控告警规则详细信息。

```bash
ctyun-cli monitor describe-custom-alarm-rule \
    --region-id <资源池ID> \
    --alarm-rule-id <告警规则ID>
```

---

## 4.7 云专线监控

### 4.7.1 查询云专线设备列表

查询云专线设备列表。

```bash
ctyun-cli monitor dcaas-list \
    --region-id <资源池ID>
```

#### 示例
```bash
ctyun-cli monitor dcaas-list \
    --region-id bb9fdb42056f11eda1610242ac110002
```

---

### 4.7.2 查询云专线流量

查询云专线流量监控数据。

```bash
ctyun-cli monitor dcaas-traffic \
    --device-id <设备ID> \
    --region-id <资源池ID> \
    --metric <指标名称>
```

#### 参数说明
| 参数 | 必需 | 说明 | 可选值 |
|-----|------|------|--------|
| `--device-id` | 是 | 设备ID | - |
| `--region-id` | 是 | 资源池ID | - |
| `--metric` | 是 | 指标名称 | `network_incoming_bytes`, `network_outgoing_bytes` |
| `--start-time` | 否 | 开始时间 | Unix时间戳（秒） |
| `--end-time` | 否 | 结束时间 | Unix时间戳（秒） |
| `--period` | 否 | 聚合周期（秒） | 默认300 |

#### 示例
```bash
# 查询流入流量
ctyun-cli monitor dcaas-traffic \
    --device-id <device-id> \
    --region-id <region-id> \
    --metric network_incoming_bytes

# 查询流出流量（指定时间范围）
ctyun-cli monitor dcaas-traffic \
    --device-id <device-id> \
    --region-id <region-id> \
    --metric network_outgoing_bytes \
    --start-time 1699000000 \
    --end-time 1699086400

# 具体示例
ctyun-cli monitor dcaas-traffic \
    --device-id dc-device-001 \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --metric network_incoming_bytes

ctyun-cli monitor dcaas-traffic \
    --device-id dc-device-001 \
    --region-id bb9fdb42056f11eda1610242ac110002 \
    --metric network_outgoing_bytes \
    --start-time 1699000000 \
    --end-time 1699086400
```

---

## 5. 安全卫士管理

天翼云安全卫士提供漏洞扫描、客户端管理等安全服务。

**API端点**: `https://ctcsscn-global.ctapi.ctyun.cn`  
**认证方式**: EOP签名认证

### 5.1 查询客户端列表

查询已安装的安全卫士客户端列表。

```bash
ctyun-cli security agents
```

#### 输出格式
```bash
# 表格格式（默认）
ctyun-cli security agents

# JSON格式
ctyun-cli --output json security agents
```

---

### 5.2 查询扫描结果

查询漏洞扫描结果。

```bash
ctyun-cli security scan-result
```

---

### 5.3 查询漏洞列表

查询指定客户端的漏洞列表。

```bash
ctyun-cli security vuln-list \
    --agent-guid <客户端GUID>
```

#### 示例
```bash
ctyun-cli security vuln-list \
    --agent-guid <agent-guid>

# 具体示例
ctyun-cli security vuln-list \
    --agent-guid 12345678-1234-1234-1234-123456789abc
```

---

## 6. 计费查询

账单模块支持三种输出格式，满足不同使用场景：

```bash
# 表格格式（默认，适合阅读）
ctyun-cli billing balance

# JSON格式（适合程序处理）
ctyun-cli billing balance --output json

# YAML格式（适合配置管理）
ctyun-cli billing balance --output yaml
```

### 6.1 查询账户余额

查询账户余额信息。

```bash
ctyun-cli billing balance
ctyun-cli billing balance --output json  # JSON格式
```

---

### 6.2 查询月度账单

查询指定月份的账单。

```bash
ctyun-cli billing bills \
    --month <年月>
```

#### 参数说明
| 参数 | 必需 | 说明 | 格式 | 示例 |
|-----|------|------|------|------|
| `--month` | 是 | 账单月份 | YYYYMM | `202411` |

#### 示例
```bash
# 查询2024年11月账单
ctyun-cli billing bills --month 202411

# JSON格式输出
ctyun-cli --output json billing bills --month 202411
```

---

### 6.3 查询消费明细

查询账户消费明细。

```bash
ctyun-cli billing expenses \
    --start-date <开始日期> \
    --end-date <结束日期>
```

#### 参数说明
| 参数 | 必需 | 说明 | 格式 | 示例 |
|-----|------|------|------|------|
| `--start-date` | 是 | 开始日期 | YYYY-MM-DD | `2024-11-01` |
| `--end-date` | 是 | 结束日期 | YYYY-MM-DD | `2024-11-07` |

#### 示例
```bash
ctyun-cli billing expenses \
    --start-date 2024-11-01 \
    --end-date 2024-11-07
```

---

### 6.4 查询账户流水

查询账户资金流水。

```bash
ctyun-cli billing transactions \
    --start-date <开始日期> \
    --end-date <结束日期>
```

---

## 7. 配置管理

### 7.1 配置认证信息

```bash
# 交互式配置
ctyun-cli configure

# 命令行配置
ctyun-cli configure \
    --access-key YOUR_AK \
    --secret-key YOUR_SK \
    --region cn-north-1 \
    --output table
```

---

### 7.2 查看当前配置

```bash
ctyun-cli show-config
```

#### 输出示例
```
当前配置:
  Access Key: <masked-access-key>
  Secret Key: <masked-secret-key>
  Region: cn-north-1
  Endpoint: https://api.ctyun.cn
  Output Format: table
```

---

### 7.3 使用多配置文件

天翼云CLI支持多个配置文件（profile）。

#### 创建新配置文件
```bash
ctyun-cli configure --profile prod \
    --access-key PROD_AK \
    --secret-key PROD_SK \
    --region cn-north-1
```

#### 使用指定配置文件
```bash
ctyun-cli --profile prod ecs list
```

#### 配置文件位置
```
~/.ctyun/
├── config          # 默认配置 [default]
├── config.prod     # 生产环境配置 [prod]
└── config.test     # 测试环境配置 [test]
```

---

## 8. 输出格式

天翼云CLI支持三种输出格式：

### 8.1 表格格式（默认）

适合人类阅读，格式化的表格输出。

```bash
ctyun-cli monitor query-cpu-top --region-id 200000001852
```

### 8.2 JSON格式

适合程序处理，完整的JSON数据。

```bash
ctyun-cli --output json monitor query-cpu-top --region-id 200000001852
```

### 8.3 YAML格式

适合配置管理，YAML格式数据。

```bash
ctyun-cli --output yaml monitor query-cpu-top --region-id 200000001852
```

### 8.4 在配置文件中设置默认格式

编辑 `~/.ctyun/config`：

```ini
[default]
output_format = json
```

---

## 9. 错误处理和故障排除

### 9.1 常见错误码和解决方法

#### 认证相关错误
| 错误码 | 说明 | 解决方法 |
|--------|------|----------|
| `InvalidAccessKey` | 访问密钥无效 | 检查AK是否正确，重新生成 |
| `SignatureMismatch` | 签名不匹配 | 检查系统时间，确认SK正确 |
| `Unauthorized` | 认证失败 | 检查AK/SK是否过期 |

#### 资源相关错误
| 错误码 | 说明 | 解决方法 |
|--------|------|----------|
| `InstanceNotFound` | 实例不存在 | 确认实例ID正确，检查区域设置 |
| `InsufficientBalance` | 余额不足 | 充值账户余额 |
| `QuotaExceeded` | 配额超限 | 申请提高资源配额 |

### 9.2 调试模式

启用调试模式查看详细的请求和响应信息：

```bash
ctyun-cli --debug monitor query-cpu-top --region-id 200000001852
```

调试模式会显示：
- 请求URL和方法
- 请求头（含签名信息）
- 请求体
- 响应状态码
- 响应内容

### 9.3 常见问题解答

#### Q: 连接API超时怎么办？
A:
- 检查网络连接
- 增加超时时间配置
- 使用代理（如需要）

#### Q: 签名失败怎么处理？
A:
- 检查系统时间是否准确
- 确认AK/SK是否正确
- 检查区域ID设置

#### Q: 实例不存在错误？
A:
- 确认实例ID拼写正确
- 检查是否在正确的资源池中
- 验证区域ID设置

#### Q: 权限不足错误？
A:
- 检查AK/SK权限范围
- 联系管理员分配相应权限
- 确认IAM策略配置

### 9.4 日志和帮助

#### 获取帮助
```bash
# 查看主帮助
ctyun-cli --help

# 查看子命令帮助
ctyun-cli ecs --help
ctyun-cli ecs list --help
```

#### 日志位置
- 配置文件: `~/.ctyun/config`
- 日志文件: 配置文件中指定的路径
- 调试输出: 使用 `--debug` 选项

#### 版本和连接测试
```bash
# 查看版本信息
ctyun-cli --version

# 测试连接
ctyun-cli test
```

### 9.5 高级技巧

#### 导出JSON数据到文件
```bash
# 导出到文件
ctyun-cli --output json monitor query-cpu-top \
    --region-id 200000001852 > cpu_top.json

# 使用jq处理JSON数据
ctyun-cli --output json monitor query-cpu-top \
    --region-id 200000001852 | jq '.data'
```

#### 简化长命令
```bash
# 使用Shell脚本
#!/bin/bash
# query_monitor.sh
REGION_ID="200000001852"

ctyun-cli monitor query-cpu-top \
    --region-id "$REGION_ID" \
    --number 10

# 使用Bash别名（添加到 ~/.bashrc）
alias ctyun-monitor='ctyun-cli monitor --region-id 200000001852'
ctyun-monitor query-cpu-top --number 10
```

---

## 10. 更多信息和参考

### 10.1 项目信息
- **PyPI包**: https://pypi.org/project/ctyun-cli/
- **GitHub项目**: https://github.com/fengyucn/ctyun-cli/
- **当前版本**: 1.7.10
- **代码规模**: 15,000+行Python代码
- **API数量**: 156+个API接口
- **命令数量**: 136+个CLI命令
- **服务模块**: 7大核心服务模块

### 10.2 资源池信息

#### 常用资源池ID
| 资源池名称 | Region ID | 描述 |
|-----------|-----------|------|
| 华北2 | 200000001852 | 华北2区域 |
| 华东1 | bb9fdb42056f11eda1610242ac110002 | 华东1区域 |

#### 查询资源池列表
```bash
ctyun-cli ecs regions
```

### 10.3 时间参数格式

所有时间参数使用Unix时间戳（秒）：

#### 生成时间戳
```bash
# 当前时间戳
date +%s

# 指定时间的时间戳
date -d "2024-11-01 00:00:00" +%s

# 1小时前
date -d "1 hour ago" +%s

# 24小时前
date -d "1 day ago" +%s
```

### 10.4 分页数据处理

使用 `--page-no` 和 `--page-size` 参数：

```bash
# 第1页，每页50条
ctyun-cli monitor query-alert-history \
    --region-id 200000001852 \
    --page-no 1 \
    --page-size 50

# 第2页
ctyun-cli monitor query-alert-history \
    --region-id 200000001852 \
    --page-no 2 \
    --page-size 50
```

### 10.5 技术支持

#### 获取帮助
```bash
# 主帮助
ctyun-cli --help

# 子命令帮助
ctyun-cli ecs --help
ctyun-cli monitor --help
```

#### 问题反馈
- **GitHub Issues**: https://github.com/fengyucn/ctyun-cli/issues
- **PyPI支持页面**: https://pypi.org/project/ctyun-cli/#project-description

#### 文档和指南
- **完整命令手册**: 本文档
- **项目README**: https://github.com/fengyucn/ctyun-cli/blob/main/README.md
- **变更日志**: https://github.com/fengyucn/ctyun-cli/blob/main/CHANGELOG.md

---

## 附录：完整命令清单

### 全局命令
- `ctyun-cli --version` - 显示版本
- `ctyun-cli --help` - 显示帮助
- `ctyun-cli configure` - 配置认证
- `ctyun-cli show-config` - 显示配置

### ECS云服务器命令
- `ctyun-cli ecs list` - 列出实例
- `ctyun-cli ecs regions` - 查询资源池
- `ctyun-cli ecs create` - 创建实例
- `ctyun-cli ecs start` - 启动实例
- `ctyun-cli ecs stop` - 停止实例
- `ctyun-cli ecs reboot` - 重启实例
- `ctyun-cli ecs delete` - 删除实例
- `ctyun-cli ecs batch-start` - 批量启动
- `ctyun-cli ecs batch-stop` - 批量停止
- `ctyun-cli ecs batch-delete` - 批量删除
- `ctyun-cli ecs resize` - 调整实例规格
- `ctyun-cli ecs images` - 查询镜像
- `ctyun-cli ecs console` - 获取控制台URL

### 监控命令（28个API）

#### 指标查询
- `ctyun-cli monitor query-data` - 查询监控数据
- `ctyun-cli monitor query-data-batch` - 批量查询监控数据
- `ctyun-cli monitor query-metric-list` - 查询指标列表
- `ctyun-cli monitor query-alert-history` - 查询告警历史
- `ctyun-cli monitor query-event-history` - 查询事件历史
- `ctyun-cli monitor query-resource-list` - 查询资源列表
- `ctyun-cli monitor query-dimension-values` - 查询维度值
- `ctyun-cli monitor query-alerted-metrics` - 查询已告警指标

#### Top-N查询
- `ctyun-cli monitor query-cpu-top` - CPU使用率Top-N
- `ctyun-cli monitor query-mem-top` - 内存使用率Top-N
- `ctyun-cli monitor query-dimension-top` - 维度值Top-N
- `ctyun-cli monitor query-resource-top` - 资源Top-N
- `ctyun-cli monitor query-metric-top` - 指标Top-N
- `ctyun-cli monitor query-event-top` - 事件Top-N

#### 告警管理
- `ctyun-cli monitor query-alarm-rules` - 查询告警规则列表
- `ctyun-cli monitor describe-alarm-rule` - 查询告警规则详情
- `ctyun-cli monitor query-contacts` - 查询联系人列表
- `ctyun-cli monitor describe-contact` - 查询联系人详情
- `ctyun-cli monitor query-contact-groups` - 查询联系人组列表
- `ctyun-cli monitor describe-contact-group` - 查询联系人组详情
- `ctyun-cli monitor query-alarm-blacklist` - 查询告警黑名单

#### 通知与模板
- `ctyun-cli monitor query-notice-templates` - 查询通知模板列表
- `ctyun-cli monitor describe-notice-template` - 查询通知模板详情
- `ctyun-cli monitor query-template-variables` - 查询模板变量
- `ctyun-cli monitor query-message-records` - 查询通知记录

#### 巡检功能
- `ctyun-cli monitor query-inspection-task-overview` - 查询巡检任务总览
- `ctyun-cli monitor query-inspection-task-detail` - 查询巡检任务详情
- `ctyun-cli monitor query-inspection-items` - 查询巡检项
- `ctyun-cli monitor query-inspection-history-list` - 查询巡检历史列表
- `ctyun-cli monitor query-inspection-history-detail` - 查询巡检历史详情

#### 自定义监控
- `ctyun-cli monitor custom-trend` - 查询自定义监控趋势
- `ctyun-cli monitor query-custom-history` - 查询自定义监控历史
- `ctyun-cli monitor query-custom-dimension-values` - 查询自定义监控维度值
- `ctyun-cli monitor query-custom-items` - 查询自定义监控项列表
- `ctyun-cli monitor query-custom-alarm-rules` - 查询自定义告警规则
- `ctyun-cli monitor describe-custom-alarm-rule` - 查询自定义告警规则详情

#### 云专线监控
- `ctyun-cli monitor dcaas-list` - 查询云专线设备列表
- `ctyun-cli monitor dcaas-traffic` - 查询云专线流量

### 安全卫士命令
- `ctyun-cli security agents` - 查询客户端列表
- `ctyun-cli security scan-result` - 查询扫描结果
- `ctyun-cli security vuln-list` - 查询漏洞列表

### Redis分布式缓存命令
- `ctyun-cli redis list` - 列出Redis实例
- `ctyun-cli redis zones` - 查询可用区
- `ctyun-cli redis version` - 查询版本信息
- `ctyun-cli redis engine-version` - 查询引擎版本
- `ctyun-cli redis instance-version` - 查询实例详细版本

### 计费命令
- `ctyun-cli billing balance` - 查询账户余额
- `ctyun-cli billing bills` - 查询月度账单
- `ctyun-cli billing expenses` - 查询消费明细
- `ctyun-cli billing transactions` - 查询账户流水

---

**文档版本**: 2.0.0
**最后更新**: 2025-12-16
**涵盖版本**: ctyun-cli v1.7.10

---

*天翼云CLI工具 - 专业、高效、易用的云资源管理解决方案*
