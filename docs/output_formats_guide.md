# 天翼云CLI输出格式使用指南

## 概述

天翼云CLI工具支持三种输出格式：**表格(table)**、**JSON(json)** 和 **YAML(yaml)**，为不同使用场景提供灵活的数据展示方式。

## 快速开始

### 基本用法

```bash
# 表格格式（默认）
ctyun-cli ecs list

# JSON格式
ctyun-cli ecs list --output json

# YAML格式
ctyun-cli ecs list --output yaml
```

### 全局输出格式

在CLI最前面指定全局输出格式，影响后续所有命令：

```bash
# 全局JSON格式
ctyun-cli --output json ecs list
ctyun-cli --output json billing balance

# 全局YAML格式
ctyun-cli --output yaml ecs list
ctyun-cli --output yaml monitor query-metric-data
```

## 三种输出格式详解

### 1. 表格格式 (table)

**特点**:
- 🎯 用户友好，易于阅读
- 🔤 中文字段名，直观易懂
- 📊 关键信息突出显示
- 👀 适合人工查看和快速浏览

**适用场景**:
- 日常运维查看资源状态
- 快速浏览数据概览
- 命令行交互使用
- 调试和问题排查

**示例输出**:
```
+----------------------+--------------+------------+--------+--------+
| 实例ID              | 实例名称       | 状态       | 规格   | 地区   |
+======================+==============+============+========+========+
| i-1234567890abcdef0 | web-server-1 | running    | s6.large | cn-north-1 |
| i-abcdef1234567890  | db-server-1  | running    | s6.medium| cn-north-1 |
+----------------------+--------------+------------+--------+--------+
```

### 2. JSON格式 (json)

**特点**:
- 🔧 完整原始数据，无信息丢失
- 📦 结构化数据，程序处理友好
- 🔗 适合API集成和脚本调用
- ⚡ 支持管道操作和数据处理

**适用场景**:
- 脚本自动化和集成
- 数据分析和处理
- API调用和数据传输
- 配置文件生成

**示例输出**:
```json
{
  "statusCode": 800,
  "message": "查询成功",
  "returnObj": {
    "totalCount": 2,
    "pageNo": 1,
    "pageSize": 10,
    "result": [
      {
        "instanceId": "i-1234567890abcdef0",
        "instanceName": "web-server-1",
        "status": "running",
        "instanceType": "s6.large",
        "regionId": "cn-north-1",
        "createTime": "2024-01-15 10:30:00",
        "publicIp": "123.456.78.90",
        "privateIp": "10.0.1.100"
      }
    ]
  }
}
```

**JSON处理示例**:
```bash
# 使用jq提取特定字段
ctyun-cli ecs list --output json | jq '.returnObj.result[] | {instanceId, instanceName, status}'

# 计算运行中的实例数量
ctyun-cli ecs list --output json | jq '.returnObj.result[] | select(.status == "running") | length'

# 导出为CSV格式
ctyun-cli ecs list --output json | jq -r '.returnObj.result[] | [.instanceId, .instanceName, .status] | @csv'
```

### 3. YAML格式 (yaml)

**特点**:
- 📋 层次化结构，清晰易读
- ⚙️ 配置管理友好
- 📝 注释支持，文档友好
- 🔤 人类和机器都可读

**适用场景**:
- 配置文件管理
- 文档生成和展示
- 系统配置备份
- 模板文件创建

**示例输出**:
```yaml
statusCode: 800
message: 查询成功
returnObj:
  totalCount: 2
  pageNo: 1
  pageSize: 10
  result:
  - instanceId: i-1234567890abcdef0
    instanceName: web-server-1
    status: running
    instanceType: s6.large
    regionId: cn-north-1
    createTime: '2024-01-15 10:30:00'
    publicIp: 123.456.78.90
    privateIp: 10.0.1.100
```

**YAML处理示例**:
```bash
# 保存为配置文件
ctyun-cli ecs list --output yaml > instances_config.yaml

# 使用yq处理YAML数据
ctyun-cli ecs list --output yaml | yq '.returnObj.result[].instanceName'

# 合并多个YAML配置
echo "database:" > config.yaml
ctyun-cli billing balance --output yaml | yq '.returnObj' >> config.yaml
```

## 模块输出格式支持

### 支持完整输出格式的模块

| 模块 | 支持命令数 | 说明 |
|------|-----------|------|
| **ECS** | 40+ | 所有命令支持三种格式 |
| **Monitor** | 28+ | 监控数据完整支持 |
| **Security** | 3+ | 安全数据格式化输出 |
| **Billing** | 13+ | ✅ 新增完整支持 |
| **Redis** | 15+ | Redis数据多格式展示 |
| **IAM** | 10+ | 权限管理数据展示 |
| **EBS** | 12+ | 存储数据格式支持 |

### 各模块特色功能

#### ECS模块
- 实例详情完整字段展示
- 资源统计信息表格化
- 镜像和规格列表优化显示

#### Monitor模块
- 指标数据时序展示
- 告警规则配置YAML格式
- Top-N数据排行榜式显示

#### Billing模块 ⭐
- 金额字段自动格式化
- 计费模式中文映射
- 使用量类型详细展示

#### Security模块
- 漏洞信息分级显示
- 扫描结果状态统计

## 高级使用技巧

### 1. 管道操作

```bash
# JSON → 筛选 → 表格
ctyun-cli ecs list --output json | jq '.returnObj.result[] | select(.status == "running")' | \
  python -c "import sys, json; data=json.load(sys.stdin); \
  [print(f'{item[\"instanceId\"]} | {item[\"instanceName\"]}') for item in data]"

# 监控数据实时流处理
ctyun-cli monitor query-metric-data --output json | \
  while read line; do
    timestamp=$(echo "$line" | jq -r '.timestamp')
    value=$(echo "$line" | jq -r '.value')
    echo "$timestamp: $value" >> metrics.log
  done
```

### 2. 批量操作

```bash
# 批量查询多个区域的资源
regions=("cn-north-1" "cn-east-1" "cn-south-1")
for region in "${regions[@]}"; do
  echo "=== $region ==="
  ctyun-cli --region "$region" ecs list --output json | \
    jq -r '.returnObj.result[] | "\(.instanceId)\t\(.instanceName)\t\(.status)"'
done

# 批量导出账单数据
for month in 202501 202502 202503; do
  ctyun-cli billing ondemand-usage "$month" --output json > "billing_$month.json"
done
```

### 3. 配置文件模板

```bash
# 生成ECS实例配置模板
cat > ecs_template.yaml << EOF
# ECS实例配置模板 - 生成时间: $(date)
instances:
EOF

ctyun-cli ecs list --output yaml | \
  yq '.returnObj.result[] | {
    instanceId,
    instanceName,
    instanceType,
    imageId
  }' >> ecs_template.yaml

# 生成监控配置模板
ctyun-cli monitor query-metric-data \
  --metric-name cpu_util \
  --start-time "2024-01-01 00:00:00" \
  --end-time "2024-01-01 23:59:59" \
  --output yaml > monitoring_config.yaml
```

### 4. 数据分析和报表

```bash
# 生成资源使用报表
echo "=== ECS实例使用报表 ===" > report.txt
echo "生成时间: $(date)" >> report.txt
echo "" >> report.txt

# 总数统计
total=$(ctyun-cli ecs list --output json | jq '.returnObj.totalCount')
echo "总实例数: $total" >> report.txt

# 按状态统计
ctyun-cli ecs list --output json | \
  jq -r '.returnObj.result[] | .status' | \
  sort | uniq -c | \
  awk '{print $2 " 状态: " $1 " 个"}' >> report.txt

# 按规格统计
ctyun-cli ecs list --output json | \
  jq -r '.returnObj.result[] | .instanceType' | \
  sort | uniq -c | \
  awk '{print $2 " 规格: " $1 " 个"}' >> report.txt

echo "" >> report.txt
echo "详细实例列表:" >> report.txt
ctyun-cli ecs list --output json | \
  jq -r '.returnObj.result[] | "\(.instanceId)\t\(.instanceName)\t\(.status)\t\(.instanceType)"' >> report.txt
```

## 故障排除

### 常见问题

#### 1. YAML格式输出问题

**问题**: YAML输出时提示需要安装PyYAML
```bash
# 解决方案：安装PyYAML
pip install PyYAML

# 或使用系统包管理器
sudo apt-get install python3-yaml  # Ubuntu/Debian
sudo yum install python3-PyYAML      # CentOS/RHEL
```

#### 2. JSON输出截断

**问题**: JSON输出被截断或换行显示异常
```bash
# 解决方案：使用less或more分页查看
ctyun-cli ecs list --output json | less

# 保存到文件
ctyun-cli ecs list --output json > output.json

# 使用jq格式化显示
ctyun-cli ecs list --output json | jq .
```

#### 3. 中文字符显示问题

**问题**: 终端中文字符显示异常
```bash
# 检查终端编码
echo $LANG

# 设置UTF-8编码
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 或者指定表格格式避免编码问题
ctyun-cli ecs list --output table
```

#### 4. 大数据量性能问题

**问题**: 大量数据查询时输出慢
```bash
# 解决方案：
# 1. 分页查询
ctyun-cli ecs list --page 1 --page-size 10 --output json

# 2. 使用过滤条件
ctyun-cli ecs list --state running --output json

# 3. 直接查询JSON减少表格格式化开销
ctyun-cli ecs list --output json > data.json
```

## 最佳实践

### 1. 脚本集成
```bash
#!/bin/bash
# 推荐使用JSON格式进行脚本集成
instances=$(ctyun-cli ecs list --output json | jq -r '.returnObj.result[].instanceId')

for instance in $instances; do
  echo "处理实例: $instance"
  # 处理逻辑
done
```

### 2. 定时任务
```bash
#!/bin/bash
# 定时备份配置
backup_dir="/backup/config/$(date +%Y%m%d)"
mkdir -p "$backup_dir"

# 导出ECS配置
ctyun-cli ecs list --output yaml > "$backup_dir/ecs_instances.yaml"

# 导出账单信息
ctyun-cli billing balance --output yaml > "$backup_dir/billing_balance.yaml"

# 导出监控配置
ctyun-cli monitor query-alert-rules --output yaml > "$backup_dir/monitoring_alerts.yaml"
```

### 3. 监控告警
```bash
#!/bin/bash
# 检查资源状态，发送告警
# 检查ECS实例状态
stopped_instances=$(ctyun-cli ecs list --output json | \
  jq -r '.returnObj.result[] | select(.status == "stopped") | .instanceId')

if [ -n "$stopped_instances" ]; then
  echo "警告: 发现已停止的实例: $stopped_instances"
  # 发送告警逻辑
fi

# 检查账户余额
balance=$(ctyun-cli billing balance --output json | jq -r '.returnObj.balance')
if [ "$balance" -lt 100 ]; then
  echo "警告: 账户余额不足: ¥$balance"
  # 发送告警逻辑
fi
```

---

## 版本历史

- **v1.5.0** (2025-12-02): 账单模块全面升级，10个API完整实现
- **v1.4.0** (2025-12-02): 账单模块完整输出格式支持
- **v1.3.0** (2024-11-01): 监控模块多格式输出优化
- **v1.2.0** (2024-10-01): ECS模块输出格式统一化
- **v1.1.0** (2024-09-01): 基础JSON/YAML格式支持

---

*文档更新时间: 2025-12-02*
*维护者: ctyun-cli 开发团队*