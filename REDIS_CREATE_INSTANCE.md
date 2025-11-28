# Redis实例创建功能使用指南

## 概述

天翼云CLI工具新增了Redis实例创建功能，支持通过命令行快速创建和管理Redis分布式缓存实例。

## 主要功能

### 1. 创建Redis实例 (create-instance)

创建新的Redis实例，支持多种配置选项。

#### 基础语法
```bash
ctyun redis create-instance [OPTIONS]
```

#### 必需参数
- `--instance-name, -n`: 实例名称 (长度不超过60个字符)
- `--edition, -e`: 实例版本类型 (Basic/Enhance/Classic)
- `--version, -v`: Redis版本号 (如: 5.0, 6.0)
- `--capacity, -c`: 实例容量GB (如: 4, 8, 16)
- `--availability-zone, -z`: 可用区 (如: cn-huabei2-tj-2a-public-ctcloud)
- `--vpc-id`: VPC网络ID
- `--subnet-id`: 子网ID
- `--password, -p`: 访问密码 (长度8-32位字符)

#### 可选参数
- `--shard-count`: 分片数量 (默认: 1)
- `--copies-count`: 副本数量 (默认: 1)
- `--region-id, -r`: 区域ID (默认: 200000001852)
- `--product-type`: 产品类型 (默认: PayPerUse)
- `--charge-mode`: 计费模式 (默认: PayPerUse)
- `--period`: 购买时长 (包年包月时需要)
- `--period-unit`: 购买时长单位 (默认: Month)
- `--auto-renew/--no-auto-renew`: 是否自动续费 (默认: 否)
- `--enterprise-project-id`: 企业项目ID (默认: 0)
- `--description, -d`: 实例描述
- `--format, -f`: 输出格式 (table/json/summary)
- `--timeout, -t`: 请求超时时间 (默认: 60秒)
- `--check-resources`: 创建前检查可用规格

### 2. 查询可用规格 (check-resources)

在创建实例前查询可用的规格配置。

#### 基础语法
```bash
ctyun redis check-resources [OPTIONS]
```

#### 必需参数
- `--edition, -e`: 实例版本类型 (Basic/Enhance/Classic)
- `--version, -v`: Redis版本号 (如: 5.0, 6.0)

#### 可选参数
- `--region-id, -r`: 区域ID (默认: 200000001852)
- `--format, -f`: 输出格式 (table/json/summary)
- `--timeout, -t`: 请求超时时间 (默认: 30秒)

## 使用示例

### 示例1: 创建基础版Redis实例 (按需付费)
```bash
ctyun redis create-instance \
    --instance-name my-redis-cache \
    --edition Basic \
    --version 5.0 \
    --capacity 4 \
    --availability-zone cn-huabei2-tj-2a-public-ctcloud \
    --vpc-id vpc-12345678 \
    --subnet-id subnet-12345678 \
    --password YourPassword123
```

### 示例2: 创建增强版实例 (包年包月，自动续费)
```bash
ctyun redis create-instance \
    -n prod-redis-enhanced \
    -e Enhance \
    -v 6.0 \
    -c 8 \
    -z cn-huabei2-tj-2a-public-ctcloud \
    --vpc-id vpc-12345678 \
    --subnet-id subnet-12345678 \
    -p SecurePassword123 \
    --period 1 \
    --auto-renew \
    --enterprise-project-id ep-123456
```

### 示例3: 创建集群版实例 (高可用配置)
```bash
ctyun redis create-instance \
    --instance-name cluster-redis \
    --edition Classic \
    --version 5.0 \
    --capacity 16 \
    --shard-count 2 \
    --copies-count 2 \
    --availability-zone cn-huabei2-tj-2a-public-ctcloud \
    --vpc-id vpc-12345678 \
    --subnet-id subnet-12345678 \
    --password ClusterPassword123 \
    --check-resources \
    --format table
```

### 示例4: 查询可用规格
```bash
# 查询基础版Redis 5.0的可用规格
ctyun redis check-resources --edition Basic --version 5.0

# 查询增强版Redis 6.0的详细规格表格
ctyun redis check-resources -e Enhance -v 6.0 --format table

# 查询集群版Redis 5.0的规格摘要
ctyun redis check-resources -e Classic -v 5.0 --format summary
```

## 实例版本类型说明

| 版本类型 | 描述 | 适用场景 |
|---------|------|---------|
| Basic | 基础版：单节点实例 | 开发测试、简单缓存场景 |
| Enhance | 增强版：主备实例 | 生产环境、需要高可用 |
| Classic | 经典版：集群版实例 | 大数据量、高并发场景 |

## 创建后操作

创建成功后，可以使用以下命令管理实例：

### 查看实例列表
```bash
ctyun redis list
ctyun redis list --name my-redis-cache
```

### 查看实例详情
```bash
ctyun redis describe --instance-id <instance-id>
```

### 监控实例状态
```bash
ctyun redis monitor-history --instance-id <instance-id> --metric memory_usage --days 7
```

### 查看可用区信息
```bash
ctyun redis zones
ctyun redis zones --region-id 200000001852
```

## 常见问题

### Q: 如何选择合适的实例版本？
A:
- **开发/测试环境**: 选择Basic基础版，成本低
- **生产环境**: 选择Enhance增强版，提供主备高可用
- **大数据量场景**: 选择Classic集群版，支持数据分片

### Q: 如何设置密码？
A: 密码长度必须为8-32位字符，建议包含大小写字母、数字和特殊字符。

### Q: 创建失败怎么办？
A:
1. 检查网络配置是否正确（VPC、子网）
2. 确认账户余额和配额
3. 使用`--check-resources`参数检查可用规格
4. 查看错误日志了解具体原因

### Q: 如何查看创建进度？
A: 实例创建是异步过程，可以通过以下命令查看状态：
```bash
ctyun redis list --name <instance-name>
ctyun redis describe --instance-id <instance-id>
```

## 错误码说明

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| DCS2_1001 | 无效的输入 | 检查参数格式和取值范围 |
| DCS2_1002 | 缺少参数 | 确认所有必需参数都已提供 |
| DCS2_9008 | 实例数量超过了配额 | 申请提高配额或删除无用实例 |
| DCS2_9009 | 存储容量超过了配额 | 申请提高配额或减少容量需求 |

## 注意事项

1. **创建时间**: Redis实例创建通常需要几分钟时间
2. **配额限制**: 确认账户配额充足，避免超出限制
3. **网络配置**: 确保VPC和子网存在且配置正确
4. **密码安全**: 密码必须符合安全要求
5. **实例命名**: 实例名称在账户内必须唯一
6. **区域选择**: 确保选择的区域和可用区支持Redis服务

## 最佳实践

1. **创建前检查**: 使用`--check-resources`参数验证规格可用性
2. **合理命名**: 使用有意义的实例名称，便于管理
3. **高可用配置**: 生产环境建议使用Enhance版本，启用自动续费
4. **容量规划**: 根据业务需求选择合适的容量，预留扩展空间
5. **安全设置**: 使用强密码，定期更新
6. **监控告警**: 创建后及时配置监控和告警

## 版本信息

- **CLI版本**: v1.3.10+
- **支持区域**: 华北2 (200000001852) 等主要区域
- **支持版本**: Redis 5.0, 6.0等主流版本
- **API端点**: dcs2-global.ctapi.ctyun.cn