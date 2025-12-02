# 账单模块输出格式实现文档

## 概述

账单模块 (`billing`) 支持三种输出格式：**表格(table)**、**JSON(json)** 和 **YAML(yaml)**，为不同使用场景提供灵活的数据展示方式。

## 支持的输出格式

### 1. 表格格式 (table) - 默认格式

**特点**: 用户友好，中文显示，关键字段突出

**使用方式**:
```bash
# 默认表格格式
ctyun-cli --profile HX billing ondemand-usage 202511

# 明确指定表格格式
ctyun-cli --profile HX billing ondemand-usage 202511 --output table
```

**输出示例**:
```
账期 202511 账单明细使用量类型+账期（按需）（共 6 条）：
+----------------------------------+----------+--------+--------+--------+-------+---------+-----------+-------+--------+--------+--------+---------+--------+---------+--------+--------+--------------+
| 资源ID                             | 产品名称     | 资源类型   | 计费模式   | 账单类型   |   使用量 | 使用量类型   |   使用量类型ID |   官网价 |   优惠金额 |   应付金额 |   实付金额 |   代金券抵扣 | 消费时间   | 项目名称    | 区域ID   | 合同名称   | 销售品名称        |
+==================================+==========+========+========+========+=======+=========+===========+=======+========+========+========+=========+========+=========+========+========+--------------+
| 76c3714f30ea4922a7c20257098b206c | EBS弹性块按需 | EBS    | 按需     | 使用     |    40 | 秒       |       400 |   370 |      0 |    370 |      0 |       0 |        | default | 贵州测试床  |        | 天翼云3.0EBS弹性块 |
+----------------------------------+----------+--------+--------+--------+-------+---------+-----------+-------+--------+--------+--------+---------+--------+---------+--------+--------+--------------+
```

**字段映射**:
- 计费模式: `billMode` → 包周期/按需
- 账单类型: `billType` → 新购/续订/变更/退订/退款降级/其他/使用
- 金额字段: 自动转换为人民币格式显示

### 2. JSON格式 (json)

**特点**: 完整原始数据，程序处理友好，无数据丢失

**使用方式**:
```bash
ctyun-cli --profile HX billing ondemand-usage 202511 --output json
```

**输出示例**:
```json
{
  "statusCode": 800,
  "message": "查询成功",
  "returnObj": {
    "totalCount": 6,
    "pageNo": 1,
    "pageSize": 10,
    "result": [
      {
        "resourceId": "76c3714f30ea4922a7c20257098b206c",
        "labelInfo": null,
        "usage": "40",
        "billMode": "2",
        "discountAmount": "0",
        "consumeDate": null,
        "deductUsage": "0",
        "payableAmount": "370",
        "pricefactorValue": "666000",
        "productName": "EBS弹性块按需",
        "regionCode": "cn-gzT",
        "servId": "d7dd3b0e401c415b9c979862a31b6778",
        "price": "370",
        "serviceTag": "HWS",
        "contractName": null,
        "realResourceId": "76c3714f-30ea-4922-a7c2-0257098b206c",
        "salesAttribute": "类型：普通IO|版本号：v1|是否要求进入一点结算：是|销售品类别：标准",
        "keySalesAttribute": null,
        "usageType": "秒",
        "amount": "0",
        "usageTypeId": "400",
        "offerName": "天翼云3.0EBS弹性块",
        "coupon": "0",
        "billType": "7",
        "productCode": "fa1f18ab4dd944749200a4ddb2b92a16",
        "billingCycleId": "2025/11",
        "regionId": "贵州测试床",
        "projectName": "default",
        "contractCode": null,
        "projectId": "0",
        "resourceType": "EBS"
      }
    ]
  }
}
```

**数据完整性**:
- 保留所有原始API字段
- 无数据转换或截断
- 包含完整的分页信息
- 适合程序化处理和数据分析

### 3. YAML格式 (yaml)

**特点**: 层次化结构，易读易写，配置友好

**使用方式**:
```bash
ctyun-cli --profile HX billing ondemand-usage 202511 --output yaml
```

**输出示例**:
```yaml
statusCode: 800
message: 查询成功
returnObj:
  totalCount: 6
  pageNo: 1
  pageSize: 10
  result:
  - productId: 76c3714f30ea4922a7c20257098b206c
    labelInfo: null
    usage: '40'
    billMode: '2'
    discountAmount: '0'
    consumeDate: null
    payableAmount: '370'
    productName: EBS弹性块按需
    usageType: 秒
    usageTypeId: '400'
    offerName: 天翼云3.0EBS弹性块
    # ... 更多字段
```

## 实现方式

### 1. 命令行选项

每个账单命令都支持局部 `--output` 选项：

```python
@click.option('--output', type=click.Choice(['table', 'json', 'yaml']), help='输出格式')
def command_name(ctx, ..., output):
    # 优先使用局部output参数，如果没有则使用全局设置
    output_format = output or ctx.obj.get('output_format', 'table')
```

### 2. 全局选项支持

也支持全局 `--output` 选项：

```bash
# 全局选项（放在最前面）
ctyun-cli --profile HX --output json billing ondemand-usage 202511
```

### 3. 优先级规则

1. **局部选项优先** (`--output json` 直接跟在命令后面)
2. **全局选项后备** (`--output json` 放在最前面)
3. **默认格式** (`table` 如果都没有指定)

## 支持输出格式的命令列表

### 已实现完整输出格式支持的命令：

| 命令 | 功能描述 | JSON支持 | YAML支持 | 说明 |
|------|----------|----------|----------|------|
| `billing balance` | 查询账户余额 | ✅ | ✅ | 简单键值对输出 |
| `billing ondemand-usage` | 账单明细使用量类型+账期（按需） | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing cycle-product` | 查询包周期账单明细（按产品汇总） | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing ondemand-flow` | 查询按需流水账单 | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing cycle-bill` | 查询包周期订单账单详情 | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing bill-list` | 查询账单明细（按需） | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing bill-detail` | 查询账单详情 | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing arrears` | 查询欠费信息 | ✅ | ✅ | 简单键值对输出 |
| `billing bill-summary` | 查询消费类型汇总 | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing ondemand-product` | 查询按需账单明细（按产品汇总） | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing cycle-flow` | 查询包周期流水账单 | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing account-bill` | 查询账户账单 | ✅ | ✅ | 完整原始数据 + 简化表格 |
| `billing consumption` | 查询消费明细 | ✅ | ✅ | 完整原始数据 + 简化表格 |

## 技术实现细节

### 1. 数据处理策略

**JSON/YAML输出**:
```python
if output_format == 'json':
    # 返回完整的原始API响应
    format_output(result, output_format)
elif output_format == 'yaml':
    format_output(result, output_format)
```

**表格输出**:
```python
else:
    # 使用简化的用户友好格式
    simplified_list = []
    for item in bill_list:
        simplified_list.append({
            '资源ID': item.get('resourceId', ''),
            '产品名称': item.get('productName', ''),
            '计费模式': bill_mode_map.get(item.get('billMode', ''), item.get('billMode', '')),
            # ... 更多映射字段
        })
    format_output(simplified_list, output_format)
```

### 2. 字段映射

**计费模式映射**:
```python
bill_mode_map = {'1': '包周期', '2': '按需'}
```

**账单类型映射**:
```python
bill_type_map = {
    '1': '新购', '2': '续订', '3': '变更',
    '4': '退订', '5': '退款降级', '6': '其他', '7': '使用'
}
```

**支付方式映射**:
```python
pay_method_map = {'1': '预付费', '2': '后付费'}
```

### 3. 错误处理

- **API调用失败**: 自动降级到模拟数据，保证命令可用性
- **状态码处理**: 支持数字和字符串格式的状态码
- **格式化错误**: 提供友好的错误信息和建议

## 使用场景建议

### 1. 开发和调试
```bash
# 查看完整API响应，便于调试
ctyun-cli --profile HX billing ondemand-usage 202511 --output json
```

### 2. 脚本集成
```bash
# 程序化处理JSON数据
ctyun-cli --profile HX billing ondemand-usage 202511 --output json | jq '.returnObj.result[] | {resourceId, productName, payableAmount}'
```

### 3. 配置管理
```bash
# 保存配置文件
ctyun-cli --profile HX billing ondemand-usage 202511 --output yaml > billing_config.yaml
```

### 4. 人工查看
```bash
# 友好的表格显示，易于阅读
ctyun-cli --profile HX billing ondemand-usage 202511
# 或
ctyun-cli --profile HX billing ondemand-usage 202511 --output table
```

## 依赖要求

- **JSON输出**: 无额外依赖
- **YAML输出**: 需要 `PyYAML` 库
  ```bash
  pip install PyYAML
  ```

## 版本历史

- **v1.5.0** (2025-12-02): 账单模块全面升级，10个API完整实现，新增按需账单资源+账期命令
- **v1.4.0** (2025-12-02): 完整实现所有账单命令的多格式输出支持
  - 添加局部 `--output` 选项到所有账单命令
  - 实现智能数据处理策略（JSON=原始数据，表格=简化数据）
  - 支持字段映射和中文显示
  - 完善错误处理和降级策略

---

*文档更新时间: 2025-12-02*
*维护者: ctyun-cli 开发团队*