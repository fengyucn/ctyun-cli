# 天翼云服务器安全卫士CLI指南

## 功能概述

天翼云服务器安全卫士CLI提供了完整的漏洞查询和管理功能，支持通过命令行界面查询服务器安全状态、漏洞信息和统计数据。

## 终端节点

- **终端节点**: `ctcsscn-global.ctapi.ctyun.cn`
- **API版本**: v1
- **认证方式**: AK/SK签名认证

## 支持的功能

### 1. 客户端管理
- 查询安全卫士客户端列表
- 显示客户端状态信息
- 获取客户端配置详情

### 2. 漏洞查询
- 查询服务器漏洞列表
- 按CVE编号过滤查询
- 按处理状态过滤查询
- 按漏洞名称模糊查询
- 支持分页查询

### 3. 统计分析
- 漏洞统计摘要
- 按危险等级分类统计
- 按处理状态分类统计
- 修复需求统计

### 4. 类型查询
- 漏洞类型列表查询
- 漏洞分类说明

## 命令参考

### 主命令结构
```bash
ctyun_cli security [子命令] [选项] [参数]
```

### 1. 客户端列表查询

#### 查看所有客户端
```bash
ctyun_cli security agents
```

#### JSON格式输出
```bash
ctyun_cli security agents --output json
```

**输出示例**:
```json
[
  {
    "agentGuid": "BDCE7EB2-069D-42C6-88FA-80967122975C",
    "hostname": "web-server-01",
    "ip": "123.456.78.90",
    "osType": "Linux",
    "osVersion": "CentOS 7.9",
    "status": "ONLINE",
    "lastScanTime": "2025-01-30 14:30:00",
    "agentVersion": "2.5.1"
  }
]
```

### 2. 漏洞列表查询

#### 基本查询
```bash
ctyun_cli security vuln-list <agent_guid>
```

#### 分页查询
```bash
ctyun_cli security vuln-list <agent_guid> --page 1 --page-size 5
```

#### 按CVE编号过滤
```bash
ctyun_cli security vuln-list <agent_guid> --cve CVE-2024-20696
```

#### 按处理状态过滤
```bash
ctyun_cli security vuln-list <agent_guid> --status UN_HANDLED
```

#### 按漏洞名称过滤
```bash
ctyun_cli security vuln-list <agent_guid> --title "OpenSSL"
```

#### JSON格式输出
```bash
ctyun_cli security vuln-list <agent_guid> --output json
```

**输出字段说明**:
- `vulAnnouncementId`: 漏洞公告ID
- `vulAnnouncementTitle`: 漏洞标题
- `fixLevel`: 修复优先级 (LOW/MIDDLE/HIGH)
- `vulType`: 漏洞类型
- `rebootRequired`: 是否需要重启
- `cveList`: CVE编号列表
- `status`: 处理状态 (0-未处理, 1-已处理, 2-已忽略)
- `timestamp`: 最后发现时间

### 3. 漏洞统计

#### 基本统计
```bash
ctyun_cli security summary <agent_guid>
```

#### JSON格式输出
```bash
ctyun_cli security summary <agent_guid> --output json
```

**统计指标**:
- 总漏洞数
- 高危/中危/低危漏洞数量
- 未处理/已处理/已忽略数量
- 需要重启的漏洞数量

### 4. 漏洞类型查询

#### 查看所有类型
```bash
ctyun_cli security vuln-types
```

#### JSON格式输出
```bash
ctyun_cli security vuln-types --output json
```

**支持的类型**:
- `LINUX`: Linux漏洞
- `WINDOWS`: Windows漏洞
- `WEB_CMS`: Web应用漏洞
- `APPLIACTION`: 应用程序漏洞

### 5. 使用示例

查看帮助和使用示例:
```bash
ctyun_cli security examples
```

## 完整使用流程

### 1. 查看客户端列表
```bash
ctyun_cli security agents
```

### 2. 选择目标客户端的agent_guid
从客户端列表中复制需要查询的服务器的agent_guid。

### 3. 查询漏洞信息
```bash
# 查询所有漏洞
ctyun_cli security vuln-list <agent_guid>

# 查询未处理的高危漏洞
ctyun_cli security vuln-list <agent_guid> --status UN_HANDLED

# 查询特定CVE漏洞
ctyun_cli security vuln-list <agent_guid> --cve CVE-2024-20696
```

### 4. 获取统计概览
```bash
ctyun_cli security summary <agent_guid>
```

## 配置要求

### 1. 认证配置
需要配置天翼云API的Access Key和Secret Key:
```bash
ctyun_cli configure --access-key YOUR_KEY --secret-key YOUR_SECRET
```

### 2. 网络要求
- 需要访问天翼云API端点
- 支持HTTPS协议
- 端口: 443

### 3. 权限要求
- 需要服务器安全卫士服务权限
- 需要API访问权限
- 需要相关的查询权限

## 错误处理

### 常见错误码
- `CTCSSCN_000000`: 成功
- `CTCSSCN_000001`: 失败
- `CTCSSCN_000003`: 用户未签署协议
- `CTCSSCN_000004`: 鉴权错误
- `CTCSSCN_000005`: 用户没有付费版配额

### 故障排除
1. **认证失败**: 检查Access Key和Secret Key是否正确
2. **权限不足**: 确认已开通安全卫士服务
3. **网络问题**: 检查网络连接和防火墙设置
4. **客户端不存在**: 确认agent_guid是否正确

## 最佳实践

### 1. 定期检查
建议定期使用CLI工具检查服务器安全状态：
```bash
# 每日检查脚本
ctyun_cli security agents | grep OFFLINE
ctyun_cli security summary <agent_guid> | grep "高危漏洞"
```

### 2. 自动化集成
可以将CLI工具集成到自动化运维流程中：
```bash
#!/bin/bash
# 安全检查脚本

AGENTS=$(ctyun_cli security agents --output json | jq -r '.[].agentGuid')

for agent in $AGENTS; do
    echo "检查服务器: $agent"

    # 检查高危漏洞
    HIGH_RISK=$(ctyun_cli security summary $agent --output json | jq '.high_risk')
    if [ "$HIGH_RISK" -gt 0 ]; then
        echo "警告: 发现 $HIGH_RISK 个高危漏洞"
    fi

    # 检查未处理漏洞
    UNHANDLED=$(ctyun_cli security summary $agent --output json | jq '.unhandled')
    if [ "$UNHANDLED" -gt 0 ]; then
        echo "警告: 发现 $UNHANDLED 个未处理漏洞"
    fi
done
```

### 3. 监控告警
结合监控工具设置告警：
- 高危漏洞数量告警
- 未处理漏洞数量告警
- 客户端离线状态告警

## 注意事项

1. **仅查询功能**: 当前版本只支持查询功能，不包含修改或操作功能
2. **数据实时性**: 漏洞数据可能存在一定的延迟
3. **权限限制**: 需要相应的服务权限才能查询数据
4. **API限制**: 注意API调用频率限制
5. **数据安全**: 敏感信息请注意保护

## 更新日志

- v1.0.0: 初始版本，支持基本的漏洞查询功能
- 支持客户端列表查询
- 支持漏洞列表查询和过滤
- 支持漏洞统计摘要
- 支持漏洞类型查询

---

**注意**: 本指南基于天翼云服务器安全卫士API实现，具体功能以实际API为准。