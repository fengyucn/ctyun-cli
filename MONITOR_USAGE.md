# 天翼云监控服务完整功能手册

## 📋 目录

- [功能概述](#功能概述)
- [快速开始](#快速开始)
- [API功能分类](#api功能分类)
  - [指标查询（8个API）](#指标查询8个api)
  - [Top-N查询（6个API）](#top-n查询6个api)
  - [告警管理（7个API）](#告警管理7个api)
  - [通知与模板（4个API）](#通知与模板4个api)
  - [巡检功能（5个API）](#巡检功能5个api)
- [通用参数说明](#通用参数说明)
- [Python SDK使用](#python-sdk使用)

## 功能概述

天翼云监控服务提供**28个完整的API接口**，涵盖指标查询、告警管理、Top-N查询、巡检功能等核心监控能力。

**API端点**: `https://monitor-global.ctapi.ctyun.cn`  
**认证方式**: EOP签名认证

## 快速开始

### 安装

```bash
pip install ctyun-cli
```

### 配置认证

```bash
# 推荐使用环境变量
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key
```

### 基本使用

```bash
# 查询监控数据
ctyun-cli monitor query-data \
    --region-id 200000001852 \
    --metric CPUUtilization

# 查询告警历史
ctyun-cli monitor query-alert-history \
    --region-id 200000001852

# 查询CPU Top-N
ctyun-cli monitor query-cpu-top \
    --region-id 200000001852 \
    --number 10
```

## API功能分类

### 指标查询（8个API）

#### 1. 查询监控数据
**CLI命令**: `ctyun-cli monitor query-data`

查询指定资源的监控指标数据。

```bash
# 查询CPU使用率
ctyun-cli monitor query-data \
    --region-id 200000001852 \
    --metric CPUUtilization \
    --start-time 1699000000 \
    --end-time 1699086400

# 指定资源ID查询
ctyun-cli monitor query-data \
    --region-id 200000001852 \
    --metric CPUUtilization \
    --resource-id instance-xxx
```

#### 2. 批量查询监控数据
**CLI命令**: `ctyun-cli monitor query-data-batch`

批量查询多个资源的监控数据。

```bash
ctyun-cli monitor query-data-batch \
    --region-id 200000001852 \
    --service ctecs \
    --resource-ids instance-1 instance-2
```

#### 3. 查询指标列表
**CLI命令**: `ctyun-cli monitor query-metric-list`

查询指定服务的可用监控指标列表。

```bash
ctyun-cli monitor query-metric-list \
    --region-id 200000001852 \
    --service ctecs
```

#### 4. 查询告警历史
**CLI命令**: `ctyun-cli monitor query-alert-history`

查询资源池的告警历史记录。

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
    --page-size 20
```

#### 5. 查询事件历史
**CLI命令**: `ctyun-cli monitor query-event-history`

查询事件监控历史。

```bash
ctyun-cli monitor query-event-history \
    --region-id 200000001852 \
    --start-time 1699000000 \
    --end-time 1699086400
```

#### 6. 查询资源列表
**CLI命令**: `ctyun-cli monitor query-resource-list`

查询指定服务的资源列表。

```bash
ctyun-cli monitor query-resource-list \
    --region-id 200000001852 \
    --service ctecs
```

#### 7. 查询维度值
**CLI命令**: `ctyun-cli monitor query-dimension-values`

查询指定维度的可用值列表。

```bash
ctyun-cli monitor query-dimension-values \
    --region-id 200000001852 \
    --service ctecs \
    --dimension instance
```

#### 8. 查询已告警指标
**CLI命令**: `ctyun-cli monitor query-alerted-metrics`

查询当前处于告警状态的指标。

```bash
ctyun-cli monitor query-alerted-metrics \
    --region-id 200000001852
```

### Top-N查询（6个API）

#### 1. CPU使用率Top-N
**CLI命令**: `ctyun-cli monitor query-cpu-top`

查询CPU使用率最高的资源。

```bash
# 查询Top 3
ctyun-cli monitor query-cpu-top \
    --region-id 200000001852

# 查询Top 10
ctyun-cli monitor query-cpu-top \
    --region-id 200000001852 \
    --number 10
```

#### 2. 内存使用率Top-N
**CLI命令**: `ctyun-cli monitor query-mem-top`

查询内存使用率最高的资源。

```bash
ctyun-cli monitor query-mem-top \
    --region-id 200000001852 \
    --number 10
```

#### 3. 维度值Top-N
**CLI命令**: `ctyun-cli monitor query-dimension-top`

查询指定维度的Top-N值。

```bash
ctyun-cli monitor query-dimension-top \
    --region-id 200000001852 \
    --dimension instance \
    --metric CPUUtilization
```

#### 4. 资源Top-N
**CLI命令**: `ctyun-cli monitor query-resource-top`

查询资源使用Top-N。

```bash
ctyun-cli monitor query-resource-top \
    --region-id 200000001852 \
    --service ctecs \
    --number 10
```

#### 5. 指标Top-N
**CLI命令**: `ctyun-cli monitor query-metric-top`

查询指标值Top-N。

```bash
ctyun-cli monitor query-metric-top \
    --region-id 200000001852 \
    --metric CPUUtilization \
    --number 10
```

#### 6. 事件Top-N
**CLI命令**: `ctyun-cli monitor query-event-top`

查询事件发生次数Top-N。

```bash
ctyun-cli monitor query-event-top \
    --region-id 200000001852 \
    --number 10
```

### 告警管理（7个API）

#### 1. 查询告警规则列表
**CLI命令**: `ctyun-cli monitor query-alarm-rules`

查询告警规则列表。

```bash
# 查询所有告警规则
ctyun-cli monitor query-alarm-rules \
    --region-id 200000001852

# 按服务类型过滤
ctyun-cli monitor query-alarm-rules \
    --region-id 200000001852 \
    --service ctecs

# 分页查询
ctyun-cli monitor query-alarm-rules \
    --region-id 200000001852 \
    --page-no 1 \
    --page-size 20
```

#### 2. 查询告警规则详情
**CLI命令**: `ctyun-cli monitor query-alarm-rule-detail`

查询指定告警规则的详细信息。

```bash
ctyun-cli monitor query-alarm-rule-detail \
    --alarm-rule-id rule-xxx
```

#### 3. 查询联系人列表
**CLI命令**: `ctyun-cli monitor query-contacts`

查询告警联系人列表。

```bash
# 查询所有联系人
ctyun-cli monitor query-contacts

# 分页查询
ctyun-cli monitor query-contacts \
    --page-no 1 \
    --page-size 20
```

#### 4. 查询联系人详情
**CLI命令**: `ctyun-cli monitor query-contact-detail`

查询联系人详细信息。

```bash
ctyun-cli monitor query-contact-detail \
    --contact-id contact-xxx
```

#### 5. 查询联系人组列表
**CLI命令**: `ctyun-cli monitor query-contact-groups`

查询联系人组列表。

```bash
ctyun-cli monitor query-contact-groups
```

#### 6. 查询联系人组详情
**CLI命令**: `ctyun-cli monitor query-contact-group-detail`

查询联系人组详细信息。

```bash
ctyun-cli monitor query-contact-group-detail \
    --contact-group-id group-xxx
```

#### 7. 查询告警黑名单
**CLI命令**: `ctyun-cli monitor query-alarm-blacklist`

查询告警黑名单配置。

```bash
ctyun-cli monitor query-alarm-blacklist \
    --region-id 200000001852
```

### 通知与模板（4个API）

#### 1. 查询通知模板列表
**CLI命令**: `ctyun-cli monitor query-notice-templates`

查询通知模板列表。

```bash
ctyun-cli monitor query-notice-templates \
    --page-no 1 \
    --page-size 20
```

#### 2. 查询通知模板详情
**CLI命令**: `ctyun-cli monitor query-notice-template-detail`

查询通知模板详细信息。

```bash
ctyun-cli monitor query-notice-template-detail \
    --template-id template-xxx
```

#### 3. 查询模板变量
**CLI命令**: `ctyun-cli monitor query-template-variables`

查询通知模板可用变量。

```bash
ctyun-cli monitor query-template-variables
```

#### 4. 查询通知记录
**CLI命令**: `ctyun-cli monitor query-message-records`

查询通知发送记录。

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
    --page-size 20
```

### 巡检功能（5个API）

#### 1. 查询巡检任务结果总览
**CLI命令**: `ctyun-cli monitor query-inspection-task-overview`

查询巡检任务执行结果的总览信息。

```bash
# 查询所有巡检任务
ctyun-cli monitor query-inspection-task-overview \
    --region-id 200000001852

# 查询指定任务
ctyun-cli monitor query-inspection-task-overview \
    --region-id 200000001852 \
    --task-id task-xxx
```

**输出说明**:
- 任务状态: 运行中(1)、已完成(2)、失败(3)
- 包含任务ID、创建时间、完成时间等信息

#### 2. 查询巡检任务结果详情
**CLI命令**: `ctyun-cli monitor query-inspection-task-detail`

查询巡检任务的详细检查结果。

```bash
# 查询健康评估详情
ctyun-cli monitor query-inspection-task-detail \
    --task-id task-xxx \
    --inspection-type 1

# 查询风险识别详情
ctyun-cli monitor query-inspection-task-detail \
    --task-id task-xxx \
    --inspection-type 2 \
    --page-no 1 \
    --page-size 20
```

**参数说明**:
- `--inspection-type`: 巡检类型（1=健康评估, 2=风险识别）
- 支持分页查询详细结果

#### 3. 查询巡检项
**CLI命令**: `ctyun-cli monitor query-inspection-items`

查询系统支持的巡检项列表。

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

**输出内容**:
- 巡检项ID和名称
- 巡检类型（健康评估/风险识别）
- 巡检项描述

#### 4. 查询巡检历史列表
**CLI命令**: `ctyun-cli monitor query-inspection-history-list`

查询历史巡检任务列表。

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
    --page-size 20
```

**输出信息**:
- 任务ID、执行时间
- 巡检结果统计
- 任务状态

#### 5. 查询巡检历史详情
**CLI命令**: `ctyun-cli monitor query-inspection-history-detail`

查询指定巡检任务的详细历史记录。

```bash
ctyun-cli monitor query-inspection-history-detail \
    --task-id task-xxx \
    --inspection-item 1

# 分页查询
ctyun-cli monitor query-inspection-history-detail \
    --task-id task-xxx \
    --inspection-item 1 \
    --page-no 1 \
    --page-size 20
```

**参数说明**:
- `--task-id`: 巡检任务ID
- `--inspection-item`: 巡检项编号
- 支持分页查询详细结果

## 通用参数说明

### 必需参数

- `--region-id`: 资源池ID（例如：`200000001852` 表示华北2）

### 可选参数

- `--output`: 输出格式，可选值：`table`（默认）、`json`、`yaml`
- `--page-no`: 页码，默认为1
- `--page-size`: 每页条数，默认为10
- `--number`: Top-N查询的N值，默认为3
- `--start-time`: 开始时间（Unix时间戳，秒）
- `--end-time`: 结束时间（Unix时间戳，秒）

### 常用资源池ID

| 资源池名称 | Region ID |
|-----------|-----------|
| 华北2 | 200000001852 |
| 华东1 | bb9fdb42056f11eda1610242ac110002 |

更多资源池ID请参考天翼云官方文档。

## Python SDK使用

### 基本用法

```python
from src.client import CTYUNClient
from src.monitor.client import MonitorClient

# 初始化客户端
client = CTYUNClient(
    access_key='your_access_key',
    secret_key='your_secret_key',
    region='cn-north-1'
)

monitor_client = MonitorClient(client)

# 查询CPU使用率Top-N
result = monitor_client.query_cpu_top(
    region_id='200000001852',
    number=10
)

if result.get('returnCode') == '0000':
    print(result['returnObj'])
```

### 高级用法

```python
# 查询告警历史
result = monitor_client.query_alert_history(
    region_id='200000001852',
    start_time=1699000000,
    end_time=1699086400,
    page_no=1,
    page_size=20
)

# 查询告警规则
result = monitor_client.query_alarm_rules(
    region_id='200000001852',
    service='ctecs'
)

# 查询巡检任务总览
result = monitor_client.query_inspection_task_overview(
    region_id='200000001852',
    task_id='task-xxx'
)

# 查询巡检历史
result = monitor_client.query_inspection_history_list(
    region_id='200000001852',
    start_time=1699000000,
    end_time=1699086400
)
```

## 完整API列表

| 分类 | API数量 | 功能说明 |
|-----|---------|---------|
| 指标查询 | 8 | 监控数据、指标列表、告警历史、事件历史等 |
| Top-N查询 | 6 | CPU、内存、维度、资源、指标、事件Top-N |
| 告警管理 | 7 | 告警规则、联系人、联系人组、黑名单管理 |
| 通知与模板 | 4 | 通知模板、模板变量、通知记录查询 |
| 巡检功能 | 5 | 任务总览、任务详情、巡检项、巡检历史 |
| **总计** | **28** | **完整监控能力覆盖** |

## 输出格式示例

### 表格格式（默认）

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

### JSON格式

```bash
ctyun-cli monitor query-cpu-top --region-id 200000001852 --output json
```

输出完整的JSON数据，便于程序处理。

### YAML格式

```bash
ctyun-cli monitor query-cpu-top --region-id 200000001852 --output yaml
```

输出YAML格式数据，便于配置管理。

## 调试模式

启用调试模式查看详细的API请求和响应：

```bash
ctyun-cli --debug monitor query-alert-history --region-id 200000001852
```

## 常见问题

### Q: 如何获取资源池ID？

A: 使用ECS命令查询：
```bash
ctyun-cli ecs regions
```

### Q: 时间参数格式是什么？

A: Unix时间戳（秒），可以使用命令生成：
```bash
date +%s  # 当前时间戳
```

### Q: 如何处理分页数据？

A: 使用 `--page-no` 和 `--page-size` 参数：
```bash
ctyun-cli monitor query-alert-history \
    --region-id 200000001852 \
    --page-no 1 \
    --page-size 50
```

### Q: 支持哪些输出格式？

A: 支持三种格式：
- `table`: 表格格式（默认，适合阅读）
- `json`: JSON格式（适合程序处理）
- `yaml`: YAML格式（适合配置管理）

## 更多信息

- [项目主页](https://pypi.org/project/ctyun-cli/)
- [天翼云监控文档](https://www.ctyun.cn/document/monitor)
- [GitHub仓库](https://github.com/yourusername/ctyun-cli)
