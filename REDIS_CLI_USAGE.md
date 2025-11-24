# Redis分布式缓存服务CLI使用指南

## 概述

Redis分布式缓存服务CLI已成功集成到ctyun-cli中，提供完整的Redis实例可用区查询功能。

## 安装和配置

### 1. 配置天翼云凭证

```bash
# 方式1: 通过参数传递
python3 cli/main.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY redis zones

# 方式2: 使用配置文件（推荐）
python3 cli/main.py configure --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY
```

### 2. 验证集成

```bash
# 查看Redis命令组帮助
python3 cli/main.py redis --help

# 查看zones命令帮助
python3 cli/main.py redis zones --help
```

## 使用方法

### 基本命令

#### 1. 查询单个区域可用区

```bash
# 使用默认区域 (200000001852)
python3 cli/main.py redis zones

# 指定区域
python3 cli/main.py redis zones --region-id 200000001852

# 自定义超时时间
python3 cli/main.py redis zones --timeout 60

# JSON格式输出
python3 cli/main.py redis zones --format json

# 摘要格式输出
python3 cli/main.py redis zones --format summary
```

#### 2. 查询多个区域可用区

```bash
# 查询多个指定区域
python3 cli/main.py redis zones-multi --regions 200000001852,200000001853

# 使用默认区域（只查询主要区域）
python3 cli/main.py redis zones-multi

# JSON格式输出
python3 cli/main.py redis zones-multi --format json

# 自定义超时时间
python3 cli/main.py redis zones-multi --timeout 45
```

### 输出格式

#### 1. 表格格式 (table)
```
📍 Redis实例可用区查询结果 (区域: 200000001852)
================================================================================
📊 查询成功! 共找到 3 个可用区

📍 可用区详细信息:
--------------------------------------------------------------------------------
序号 可用区ID                       可用区名称               状态
--------------------------------------------------------------------------------
1    cn-huabei2-tj1a-public-ctcloud 华北2-天津1A-公共云    available
2    cn-huabei2-tj1b-public-ctcloud 华北2-天津1B-公共云    available
3    cn-huabei2-tj2a-public-ctcloud 华北2-天津2A-公共云    available
```

#### 2. 摘要格式 (summary)
```
📋 Redis实例可用区查询摘要
============================================================
🏷️  区域ID: 200000001852
✅ 查询状态: 成功
📢 结果消息: 查询成功
📈 可用区数量: 3

📍 可用区列表:
   1. cn-huabei2-tj1a-public-ctcloud
      名称: 华北2-天津1A-公共云
      状态: available
```

#### 3. JSON格式 (json)
```json
{
  "success": true,
  "message": "查询成功",
  "region_id": "200000001852",
  "zones_count": 3,
  "zones": [
    {
      "zone_id": "cn-huabei2-tj1a-public-ctcloud",
      "zone_name": "华北2-天津1A-公共云",
      "zone_status": "available",
      "region_id": "200000001852"
    }
  ],
  "full_result": {...}
}
```

## 实际使用示例

### 1. 快速查询当前区域可用区

```bash
# 配置好凭证后，直接查询
python3 cli/main.py redis zones --format summary
```

### 2. 批量查询多个区域

```bash
# 查询主要生产区域
python3 cli/main.py redis zones-multi --regions "200000001852,200000001853" --format json
```

### 3. DevOps自动化集成

```bash
# 在脚本中使用JSON输出
RESULT=$(python3 cli/main.py redis zones --format json)
ZONE_COUNT=$(echo $RESULT | jq '.zones_count')
echo "可用区数量: $ZONE_COUNT"

# 获取第一个可用区
FIRST_ZONE=$(echo $RESULT | jq -r '.zones[0].zone_id')
echo "首选可用区: $FIRST_ZONE"
```

## API端点信息

- **基础URL**: `https://dcs2-global.ctapi.ctyun.cn`
- **API路径**: `/ebp/api/ctyun/redis/getZones`
- **认证方式**: EOP签名认证 (HMAC-SHA256)
- **请求方法**: GET
- **必需参数**: `regionId`

## 错误处理

### 常见错误码

1. **HTTP 401** - 认证失败
   - 检查Access Key和Secret Key是否正确
   - 确认账户状态正常

2. **HTTP 404** - API未找到
   - 确认API端点正确
   - 检查区域ID是否有效

3. **请求超时**
   - 使用 `--timeout` 参数增加超时时间
   - 检查网络连接

### 错误示例处理

```bash
# 增加超时时间到60秒
python3 cli/main.py redis zones --timeout 60

# 使用JSON格式便于程序处理
python3 cli/main.py redis zones --format json > redis_zones.json
```

## 技术特性

### ✅ 已实现功能

- [x] **EOP签名认证** - 自动生成符合天翼云规范的HMAC-SHA256签名
- [x] **多区域查询** - 支持同时查询多个区域的可用区信息
- [x] **多种输出格式** - 表格、JSON、摘要三种输出格式
- [x] **错误处理** - 完整的错误处理和用户友好的错误信息
- [x] **CLI集成** - 无缝集成到ctyun-cli主命令行工具
- [x] **超时控制** - 可配置的请求超时时间
- [x] **参数验证** - 完整的输入参数验证和提示

### 🔧 技术架构

```
ctyun-cli/
├── src/
│   ├── cli/main.py          # 主CLI入口（已集成redis命令组）
│   └── redis/
│       ├── __init__.py      # Redis模块初始化
│       ├── client.py        # Redis API客户端（EOP签名认证）
│       └── commands.py      # Click命令实现
```

## 开发和测试

### 运行测试

```bash
# 运行Redis模块测试
python3 test_redis_cli.py

# 测试CLI命令
python3 cli/main.py redis --help
```

### 开发环境设置

```bash
# 安装依赖
pip install requests click

# 运行开发模式
export PYTHONPATH=./ctyun_cli/src
python3 -m cli.main redis zones --help
```

## 故障排查

### 1. 导入错误
```bash
# 确保在正确的目录
cd /path/to/ctyun-cli/src
python3 cli/main.py redis --help
```

### 2. 认证问题
```bash
# 检查凭证配置
python3 cli/main.py show-config

# 重新配置凭证
python3 cli/main.py configure --access-key NEW_KEY --secret-key NEW_SECRET
```

### 3. 网络问题
```bash
# 增加超时时间
python3 cli/main.py redis zones --timeout 120

# 测试网络连通性
curl -I https://dcs2-global.ctapi.ctyun.cn
```

---

## 版本信息

- **版本**: v1.0
- **创建时间**: 2025-11-24
- **兼容性**: 天翼云EOP API v2.0
- **依赖**: Python 3.6+, requests, click

## 支持

如有问题，请参考：
1. 天翼云官方API文档
2. ctyun-cli项目文档
3. Redis分布式缓存服务使用指南

---

**注意**: 本工具需要有效的天翼云账户和Redis服务权限才能正常工作。