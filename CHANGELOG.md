# 更新日志

本文档记录了天翼云CLI工具的所有版本更新历史。

---

## v1.17.1 (2026-05-09)

### 🚀 新增Aone查询API
- **Aone（边缘安全加速平台）**：实现 45 个查询类 API
  - **域名管理**（6个）：域名列表、配置信息、状态查询、协议类型、基础配置
  - **服务管理**（2个）：服务基本信息、资源包列表
  - **证书管理**（3个）：证书列表、详情、关联域名
  - **缓存管理**（4个）：刷新/预取任务查询及额度查询
  - **数据统计**（17个）：带宽、流量、QPS、请求数、PV/UV、状态码、响应时间、成功率等
  - **安全防护**（10个）：CC攻击报表/事件、DDoS趋势、WAF配置、规则引擎、防篡改、IPv6检测
  - **辅助工具**（3个）：IP归属、回源IP查询
- **终端节点**：统一使用 `accessone-global.ctapi.ctyun.cn`

---

## v1.17.0 (2026-05-08)

### 🚀 新增功能
- **EIP 弹性公网IP增强**：实现真实可用的 EIP 查询 API
  - `vpc eip detail`：查看EIP详情（GET /v4/eip/show），支持查看带宽/绑定/计费等信息
  - `vpc eip shared-bandwidths`：查询共享带宽列表（GET /v4/bandwidth/new-list），支持模糊搜索
- **ECS 文档标记**：完成 48 个 ECS 查询类 API 文档标记

### 📚 使用示例
```bash
ctyun-cli vpc eip detail --region-id <资源池ID> --eip-id <EIP_ID>
ctyun-cli vpc eip shared-bandwidths --region-id <资源池ID>
```

---

## v1.16.0 (2026-05-08)

### 🚀 新增功能
- **VPC EIP 查询修复**：将 VPC 模块中 `describe_eips` 从 TODO 空壳实现为真实的 POST 请求
  - `vpc eip list` 现在可正常查询弹性公网IP列表

---

## v1.15.0 (2026-05-08)

### 🚀 新增模块
- **AIServer（模型推理服务）**：新增 `aiserver` 模块，终端节点 `ctinfer-global.ctapi.ctyun.cn`
  - 计费查询：`billing-models`（预置模型列表）/ `billing-product`（销售品信息）
  - 订单管理：`create-order` / `orders`（分页查询）/ `unsubscribe`
  - 服务组管理：`service-groups` / `service-group-models` / `add-service-group` / `delete-service-group`
  - 模型管理：`models`（预置+我的模型）/ `child-accounts`
  - 服务监控：8 个报表命令（调用次数/失败率/QPS/响应时延/首token延迟/非首token时延/整句Token时延/Token调用量）

### 📚 使用示例
```bash
ctyun-cli aiserver billing-models
ctyun-cli aiserver billing-product --model-id <模型ID>
ctyun-cli aiserver models --user-ids <用户ID>
ctyun-cli aiserver orders --size 10
```

---

## v1.14.0 (2026-05-07)

### 🚀 新增模块
- **CloudPC（云电脑/政企版）**：新增 `cloudpc` 模块，终端节点 `ecpc-global.ctapi.ctyun.cn`
  - `cloudpc list`：查询云电脑列表，支持按别名/状态/VPC过滤
  - `cloudpc ecs-list`：查询弹性云电脑(ECS型)列表
  - `cloudpc service-status`：查询云电脑服务开通状态
  - `cloudpc images`：查询可用镜像列表
  - `cloudpc volumes`：查询云硬盘列表
  - `cloudpc vpcs` / `cloudpc subnets`：查询VPC和子网
  - `cloudpc users` / `cloudpc orgs`：查询用户和部门列表

### 🤷‍♂️ 求助
云电脑查询 API 已实现并验证通过，认证签名、请求参数全部正确。但云电脑使用独立的资源池 ID 体系，`200000001852` 等已知区域 ID 均提示 `unknown region`。如有知道云电脑正确的资源池 ID，请联系作者或在 GitHub Issues 中告知！

### 📚 使用示例
```bash
ctyun-cli cloudpc service-status --region-id <云电脑资源池ID>
ctyun-cli cloudpc list --region-id <云电脑资源池ID>
ctyun-cli cloudpc vpcs --region-id <云电脑资源池ID>
ctyun-cli cloudpc users --region-id <云电脑资源池ID>
```

---

## v1.13.0 (2026-05-02)

### 🚀 新增功能
- **ECS监控增强**：新增 8 个实时与历史监控命令，支持 CPU/内存/网卡/磁盘 四大维度
  - `ecs cpu-latest` / `ecs mem-latest` / `ecs network-latest` / `ecs disk-latest`
  - `ecs cpu-history` / `ecs mem-history` / `ecs network-history` / `ecs disk-history`
- **ECS订单查询增强**：新增 `query-dedicated-host-uuid` 和 `query-order-uuid` 命令，支持宿主机和通用资源UUID查询

### 📚 使用示例
```bash
# 查询CPU实时监控
ctyun-cli ecs cpu-latest --region-id <区域ID> --device-ids <实例ID>

# 查询CPU历史数据（过去24小时）
ctyun-cli ecs cpu-history --region-id <区域ID> --device-ids <实例ID> \
  --start-time $(date -d '24 hours ago' '+%Y-%m-%d %H:%M:%S') \
  --end-time $(date '+%Y-%m-%d %H:%M:%S')

# 查询宿主机订单UUID
ctyun-cli ecs query-dedicated-host-uuid --region-id <区域ID> --master-order-id <订单ID>

# 查询任意资源订单UUID
ctyun-cli ecs query-order-uuid --region-id <区域ID> --master-order-id <订单ID>
```

---

## v1.12.0 (2026-04-30)

### 🚀 新增模块
- **EMR（翼MapReduce）**：新增 `emr` 模块，终端节点 `emr-global.ctapi.ctyun.cn`
  - `emr list`：查询集群列表（支持V1/V2 API），支持名称/状态/类型过滤，分页展示
  - `emr describe`：查询集群详情（支持V1/V2 API），展示类型/版本/状态/VPC/组件
  - `emr node-groups`：查询节点组信息（支持V1/V2），展示类型/主机数/规格
  - `emr node-detail`：查询节点组详情（V2），展示主机名称/IP/状态/角色
  - `emr meta-overview`：查询Hive元数据概览，展示库/表/存储量/文件数
  - `emr meta-table`：查询指定Hive表的元数据，展示文件数/存储/分区/冷热分区统计

### 📚 使用示例
```bash
ctyun-cli emr list --region-id <资源池ID>
ctyun-cli emr describe --cluster-id <集群ID>
ctyun-cli emr node-groups --cluster-id <集群ID> --v2
ctyun-cli emr node-detail --cluster-id <集群ID>
ctyun-cli emr meta-overview --cluster-id <集群ID>
ctyun-cli emr meta-table --cluster-id <集群ID> --database test_db --table test_table
```

---

## v1.11.0 (2026-04-30)

### 🚀 新增模块
- **CSS（云搜索服务）**：新增 `css` 模块，终端节点 `ctcsx-global.ctapi.ctyun.cn`
  - `css list`：查询 OpenSearch/Elasticsearch 实例列表，支持类型/名称/状态过滤，分页展示
  - `css describe`：查询实例详情，展示健康状态/规格/VPC/各类型节点信息
  - `css logstash-list`：查询 Logstash 实例列表，展示管道/节点/关联实例

### 📚 使用示例
```bash
ctyun-cli css list --region-id <资源池ID> --type 1
ctyun-cli css describe --cluster-id <实例ID>
ctyun-cli css logstash-list --region-id <资源池ID>
```

---

## v1.10.0 (2026-04-30)

### 🚀 新增模块
- **Kafka（分布式消息服务）**：新增 `kafka` 模块，终端节点 `ctgkafka-global.ctapi.ctyun.cn`
  - `kafka list`：查询实例列表，支持按名称（精确/模糊匹配）、状态过滤，分页展示
  - `kafka node-status`：查看实例节点状态，展示各节点IP及健康状态
  - `kafka floating-ips`：查询可绑定的弹性IP列表
  - `kafka config`：获取实例配置，展示配置项名称/当前值/默认值/类型/有效值

### 📚 使用示例
```bash
ctyun-cli kafka list --region-id <资源池ID>
ctyun-cli kafka list -r xxx --name test --exact-match
ctyun-cli kafka node-status -r xxx -i <实例ID>
ctyun-cli kafka floating-ips -r xxx
ctyun-cli kafka config -r xxx -i <实例ID>
```

---

## v1.9.0 (2026-04-29)

### 🚀 新增模块
- **LTS（云日志服务）**：新增 `lts` 模块脚手架，终端节点 `ctlts-global.ctapi.ctyun.cn`，支持 134 个接口的后续实现
- **SFS（弹性文件服务）**：新增 `sfs` 模块脚手架，终端节点 `ctsfs-global.ctapi.ctyun.cn`
- **OceanFS（海量文件服务）**：新增 `oceanfs` 模块脚手架，终端节点 `oceanfs-global.ctapi.ctyun.cn`
- **Aone（边缘安全加速平台）**：新增 `aone` 模块脚手架，终端节点 `aone-global.ctapi.ctyun.cn`

### 🎯 Redis 模块完善
- **新增 `redis topology` 命令**：查询实例逻辑拓扑，展示主从节点关系和接入机代理节点
- **新增 `redis cluster-nodes` 命令**：批量查询实例集群节点信息，支持分页，含 18 种实例类型枚举映射
- **修复 `redis network` 命令**：更正 API 路径为 `describeDBInstanceNetInfo`，参数改为 `prodInstId`，显示字段对齐真实响应（连接地址/弹性IP/VPC网络/架构类型）
- **修复 `redis describe` 命令**：更正 API 路径为 `instanceManageMgrServant/describeInstancesOverview`，参数改为 `prodInstId`（header 传 `regionId`），支持 `--region-id` 参数，显示函数完全重写（含规格/带宽/计费/节点拓扑）

### 📚 使用示例
```bash
ctyun-cli lts --help
ctyun-cli sfs --help
ctyun-cli oceanfs --help
ctyun-cli aone --help
ctyun-cli redis topology --instance-id <实例ID>
ctyun-cli redis cluster-nodes
ctyun-cli redis describe --instance-id <实例ID> -f table
```

---

## v1.8.4 (2026-04-22)

### 🚀 新增功能
- **ELB 后端主机详情查询**：新增 `show_target` API（GET /v4/elb/show-target），查看后端主机详细信息
  - `elb targetgroup targets show`：CLI 命令，支持查询后端主机IP、端口、权重、健康状态等

### 📚 使用示例
```bash
# 查询后端主机详情
ctyun-cli elb targetgroup targets show --region-id 200000001852 --target-id target-xxx
```

---

## v1.8.3 (2026-04-22)

### 🚀 新增功能
- **CCE 任务管理**：新增 5 个任务管理 API，支持任务查询与生命周期控制
  - `get_task_detail`：查询任务详情（GET /v2/cce/tasks/{taskId}）
  - `get_cluster_events`：查询指定集群事件列表（GET /v2/cce/events/{clusterId}），支持 eventType、taskId 过滤
  - `resume_task`：恢复任务（POST /v2/cce/tasks/{taskId}/resume）
  - `cancel_task`：取消任务（POST /v2/cce/tasks/{taskId}/cancel）
  - `pause_task`：暂停任务（POST /v2/cce/tasks/{taskId}/pause）
- **CCE 标签管理**：新增集群标签查询 API
  - `query_cluster_tags`：查询集群标签列表（GET /v2/cce/clusters/{clusterId}/tags）

### 🔧 Bug 修复
- **修复 bind_cluster_tag URL 路径错误**：从 `/cse-apig/v2/clusters/{id}/tags/bind` 修正为 `/v2/cce/clusters/{id}/tags`
- **修复 bind_cluster_tag 请求体格式错误**：从 `{tagKey, tagValue}` 修正为 `{tags: [{key, value}]}`
- **修复 query_cluster_tags 响应解析**：实际 API 返回 `tags` 字段而非文档中的 `records`

### 📚 使用示例
```bash
# 查询任务详情
ctyun-cli cce get-task --region-id 200000001852 --task-id task-xxx

# 查询集群事件列表
ctyun-cli cce list-cluster-events --region-id 200000001852 --cluster-id xxx

# 查询集群标签
ctyun-cli cce tag list --region-id 200000001852 --cluster-id xxx

# 绑定集群标签
ctyun-cli cce tag bind --region-id 200000001852 --cluster-id xxx --tags "key1=value1,key2=value2"
```

---

## v1.8.2 (2026-04-15)

### 🚀 新增功能
- **ECS 云主机标签管理**：新增编辑云主机标签 API（API ID: 17815），支持增加、修改、删除标签操作
  - `update_ecs_label`：编辑云主机标签，支持 ADD/UPDATE/DELETE 三种操作
  - `ecs update-label`：CLI 命令，格式 `--labels key1=value1,key2=value2`
- **模块化架构优化**：修复 `cli/__init__.py` 预导入导致的 RuntimeWarning

### 📚 使用示例
```bash
# 增加标签
ctyun-cli ecs update-label --region-id xxx --instance-id xxx --action ADD --labels "env=prod,team=devops"

# 修改标签
ctyun-cli ecs update-label --region-id xxx --instance-id xxx --action UPDATE --labels "env=staging"

# 删除标签
ctyun-cli ecs update-label --region-id xxx --instance-id xxx --action DELETE --labels "env=prod"
```

---

## v1.8.1 (2026-03-30)

### 🚀 新增功能
- **CCE Namespace 命名空间管理**：新增 5 个 Namespace API，支持完整的 Kubernetes 命名空间生命周期管理
  - `create_namespace`：创建命名空间，支持 YAML 格式资源配置
  - `delete_namespace`：删除命名空间，级联删除该命名空间下所有资源
  - `update_namespace`：更新命名空间配置，支持标签、注解等元数据修改
  - `get_namespace`：查询命名空间详情，返回完整 YAML 配置
  - `list_namespaces`：查询命名空间列表，支持 labelSelector 和 fieldSelector 过滤
- **CLI 命令扩展**：新增 `cce namespace` 命令组，包含以下子命令
  - `cce namespace create`：创建命名空间
  - `cce namespace delete`：删除命名空间（带确认提示）
  - `cce namespace update`：更新命名空间
  - `cce namespace show`：查询命名空间详情
  - `cce namespace list`：查询命名空间列表

### 📚 使用示例
```bash
# 创建命名空间
ctyun-cli cce namespace create \
  --region-id <region_id> \
  --cluster-name <cluster_id> \
  --namespace-yaml "apiVersion: v1\nkind: Namespace\nmetadata:\n  name: my-namespace"

# 查询命名空间列表
ctyun-cli cce namespace list \
  --region-id <region_id> \
  --cluster-name <cluster_id>

# 查询命名空间详情
ctyun-cli cce namespace show \
  --region-id <region_id> \
  --cluster-name <cluster_id> \
  --namespace-name default

# 删除命名空间
ctyun-cli cce namespace delete \
  --region-id <region_id> \
  --cluster-name <cluster_id> \
  --namespace-name my-namespace
```

---

## v1.8.0 (2026-03-28)

### 🔧 Bug 修复
- **彻底解决 `redis` 模块命名冲突问题**：将 `src/redis/` 重命名为 `src/rdscmd/`，从根源上解决与 Python 第三方库 `redis-py` 的命名冲突。
  - 模块重命名：`redis` → `rdscmd`
  - CLI命令保持不变：`ctyun redis zones`、`ctyun redis list` 等命令无需修改
  - 删除 `cli/__init__.py` 中的 sys.path hack 临时修复代码
  - 用户无感知升级，零兼容性问题

### 🧹 代码清理
- 移除 `src/cli/__init__.py` 中的 sys.path 路径操作代码（约10行）
- 代码更简洁，无需任何导入路径的 hack 处理

---

## v1.7.17 (2026-03-27)

### 🔧 Bug 修复
- **修复 PyPI 安装后 `redis` 导入冲突问题**：v1.7.16 中 `cli/__init__.py` 的路径修复逻辑在安装到 `site-packages` 后无法正确工作，导致导入系统 `redis` 包而非项目内的 `redis` 模块。修复方案：在 `cli/__init__.py` 中强制将项目所在的 `site-packages` 目录插入 `sys.path` 最前面，确保优先导入项目内的 `redis` 包。

## v1.7.16 (2026-03-27)

### 🚀 新增功能
- **ECS 订单询价 API**：新增 `query_order_price` 方法，支持购买前询价
  - URI: `POST /v4/new-order/query-price`
  - 支持 9 种资源类型：VM / EBS / IP / IP_POOL / NAT / BMS / PGELB / CBR_VM / CBR_VBS
  - 支持包周期（MONTH/YEAR）和按需两种计费模式
  - 返回原价、折后价、最终价及子订单明细
- **CLI 命令 `ecs query-price`**：完整命令行支持，含所有资源类型专属参数

### 🔧 Bug 修复
- **修复 `ctyun-cli` 命令启动失败问题**：`site-packages` 中的系统 `redis` 包优先级高于项目 `src/redis/`，导致 `ImportError`。在 `src/cli/__init__.py` 中强制将 `src/` 插入 `sys.path[0]` 修复。

### 📚 使用示例
```bash
# VM 包周期询价
ctyun-cli ecs query-price \
  --region-id <region_id> \
  --resource-type VM \
  --flavor-name s7.2xlarge.2 \
  --image-uuid <image_uuid> \
  --sys-disk-type SATA --sys-disk-size 50 \
  --cycle-type MONTH --cycle-count 1

# VM 按需询价
ctyun-cli ecs query-price \
  --region-id <region_id> \
  --resource-type VM \
  --flavor-name s7.2xlarge.2 \
  --image-uuid <image_uuid> \
  --sys-disk-type SATA --sys-disk-size 50 \
  --on-demand

# EBS 包周期询价
ctyun-cli ecs query-price \
  --region-id <region_id> \
  --resource-type EBS \
  --disk-type SSD --disk-size 100 --disk-mode VBD \
  --cycle-type MONTH --cycle-count 6
```

---

## v1.7.8 (2025-12-11)

### 🚀 新增功能
- **CCE ConfigMap管理API**：
  - 新增`get_config_map_detail` API方法，支持查看ConfigMap详细配置信息
  - 新增`list_config_maps` API方法，支持查询ConfigMap列表
  - 支持标签选择器（labelSelector）和字段选择器（fieldSelector）过滤
- **CCE集群日志查询API**：
  - 新增`query_cluster_logs` API方法，支持分页查询集群操作日志
  - 支持多种日志类型识别（插件、集群、节点等）
- **CLI命令扩展**：
  - 新增`cce configmap`命令组，包含list和show子命令
  - 新增`cce logs query`命令，支持集群日志查询和分页
  - 支持JSON、YAML、表格三种输出格式

### 🔧 技术改进
- **EOP签名认证**：为新增CCE API方法集成企业级EOP签名认证机制
- **ConfigMap数据解析**：支持完整的YAML格式ConfigMap数据解析
- **日志智能处理**：自动识别日志类型，提供统计和分类显示
- **分页查询优化**：支持灵活的分页参数和数据统计
- **多格式输出**：新增API支持多种输出格式，满足不同使用场景

### 📊 功能增强
- **容器引擎模块扩展**：新增ConfigMap和日志管理功能
- **运维支持增强**：提供完整的集群日志查询和分析能力
- **配置管理完善**：支持Kubernetes ConfigMap配置的查询和管理
- **用户体验优化**：提供清晰的命令结构和使用示例

### 📚 使用示例
```bash
# 查询ConfigMap列表
ctyun-cli cce configmap list --region-id <region_id> \\
  --cluster-id <cluster_id> --namespace default

# 查看ConfigMap详情
ctyun-cli cce configmap show --region-id <region_id> \\
  --cluster-id <cluster_id> --namespace default --name <configmap_name>

# 查询集群日志
ctyun-cli cce logs query --region-id <region_id> \\
  --cluster-name <cluster_name> --page-size 20
```

### ✅ 测试验证
- **API功能测试**：所有新增API均通过EOP签名认证验证
- **CLI命令测试**：完整的命令结构和使用示例验证
- **分页功能测试**：验证分页查询和数据统计功能
- **错误处理验证**：完善了各种错误场景的处理机制

---

## v1.7.7 (2025-12-11)

### 🚀 新增功能
- **ELB健康检查详情API**：新增`get_health_check` API方法，支持查看健康检查详细配置信息
- **ELB监控API增强**：
  - 新增`query_realtime_monitor` API方法，支持实时监控数据查询
  - 新增`query_history_monitor` API方法，支持历史监控数据查询
- **CLI命令扩展**：
  - 新增`elb health-check show`命令，提供完整的健康检查详情查询功能
  - 新增`elb monitor realtime`命令，支持实时监控数据查询
  - 新增`elb monitor history`命令，支持历史监控数据查询
  - 新增`elb monitor`命令组，统一管理ELB监控相关命令

### 🔧 技术改进
- **EOP签名认证**：为新增API方法集成企业级EOP签名认证机制
- **健康检查配置解析**：支持完整的健康检查配置信息解析，包括基础配置、HTTP配置、高级功能
- **监控数据处理**：支持多种监控指标和时间范围查询，灵活的数据聚合周期设置
- **多格式输出**：新增API支持JSON、YAML、表格三种输出格式
- **智能配置建议**：为健康检查配置提供智能化的参数建议和警告提示

### 📊 API和命令统计更新
- **API总数**：从215+个更新至283+个
- **命令总数**：从208+个更新至217+个
- **服务模块**：保持11个核心服务模块

### 📚 使用示例
```bash
# 查看健康检查详情
ctyun-cli elb health-check show --region-id 200000001852 --health-check-id <health_check_id>

# 查询实时监控数据
ctyun-cli elb monitor realtime --region-id 200000001852 --device-ids "<device_id_1>,<device_id_2>"

# 查询历史监控数据
ctyun-cli elb monitor history --region-id 200000001852 \
  --device-ids "<device_id>" \
  --metric-names "<metric_names>" \
  --start-time "2025-12-01 00:00:00" \
  --end-time "2025-12-02 00:00:00"
```

### ✅ 测试验证
- **API功能测试**：所有新增API均通过HTTP 200状态码验证
- **真实数据测试**：成功获取真实的环境健康检查和监控数据
- **错误处理验证**：完善了各种错误场景的处理机制
- **CLI命令集成**：所有命令均通过帮助文档和参数验证测试

---

## v1.7.5 (2025-12-08)

### 🚀 新增功能
- **ECS订单查询API**：新增`query_uuid_by_order` API方法，支持根据订单ID查询云主机UUID
- **CLI命令扩展**：新增`ecs query-uuid`命令，提供完整的命令行操作支持
- **EOP签名认证**：集成天翼云EOP签名认证机制，确保API调用安全性

### 🔧 技术改进
- **订单状态映射**：支持22种订单状态，包括待支付、已支付、完成、开通中等状态
- **多格式输出**：支持JSON、YAML、表格三种输出格式
- **错误处理优化**：完善API错误处理和用户友好的错误提示
- **语法错误修复**：修复了`src/ecs/commands.py`文件中的语法错误

### 📚 使用示例
```bash
# 查询订单状态和云主机ID
ctyun-cli --profile HX ecs query-uuid \
  --region-id 200000001852 \
  --master-order-id <order_id>

# JSON格式输出
ctyun-cli ecs query-uuid \
  --region-id 200000001852 \
  --master-order-id <order_id> \
  --output json
```

### 📊 统计数据更新
- **ECS (云服务器)**：41个命令，38个API接口（新增1个命令和1个API）
- 其他模块统计数据保持不变
- **总计统计**：209个CLI命令，216个API接口，覆盖天翼云核心服务

---

## v1.6.0 (2025-12-03)

### 🚀 新增功能 (Added)
- **VPC new系列API完整实现** - 实现基于游标分页的高性能VPC查询
  - `vpc new-list` - 新版VPC列表查询，支持游标分页
  - `vpc subnet new-list` - 新版子网列表查询，支持幂等性和游标分页
  - `vpc security new-query` - 新版安全组查询，支持模糊查询
  - `vpc show` - VPC详情查询，获取单个VPC的完整信息

### ⚡ 性能优化 (Improved)
- **游标分页支持** - 基于nextToken的分页机制，支持大数据量高性能查询
- **查询功能增强** - 支持按VPC ID、实例ID、安全组名称等多维度筛选
- **幂等性保证** - 子网查询支持clientToken，确保请求幂等性
- **模糊查询支持** - 安全组查询支持按ID或名称进行模糊匹配

### 🔧 技术改进 (Technical)
- **API端点优化** - 新版API使用更高效的端点设计
- **错误处理增强** - 完善的异常处理和模拟数据降级机制
- **输出格式统一** - 所有新命令支持table、json、yaml三种输出格式
- **参数验证完善** - 增强的CLI参数验证和帮助信息

### 📊 统计数据更新
- **VPC模块**：支持11个API接口，覆盖完整的网络管理场景
- **新增命令**：4个新的CLI命令，提升网络管理效率
- **API覆盖率**：VPC网络管理功能覆盖率达95%+

### 📚 文档更新
- 新增 `VERSION_RULES.md` - 版本号刷新规则文档
- 更新所有API文档标记为已完成状态
- 完善CLI命令帮助文档

---

## v1.5.0 (2025-12-02)

### 💰 账单模块全面升级
- **10个账单API完整实现** - 实现包周期、按需、消费类型汇总等完整账单查询体系
- **新增按需账单资源+账期命令** - `ondemand-resource-cycle` 支持按资源维度和按天查询
- **优化所有账单命令输出格式** - 统一支持 `--output json/yaml/table` 参数
- **修复金额显示问题** - 移除科学计数法，添加千分位分隔符，提升可读性
- **智能数据返回策略** - JSON/YAML返回完整原始数据，table返回用户友好格式

---

## v1.4.12 (2025-11-28)

### 🚄 云专线CDA模块上线
- **14个API完整实现** - 专线网关、物理专线、VPC管理、健康检查、链路探测等
- **4个核心CLI命令** - 支持专线全生命周期管理
- **企业级功能** - 支持监控告警、自动故障切换、带宽智能调度

---

## v1.3.12 (2025-11-25)

### 🏗️ CCE容器引擎任务管理
- **任务查询API** - 支持集群任务、节点任务、作业任务查询
- **资源统计** - 集群资源使用情况和配额统计
- **监控集成** - 与监控服务无缝集成

---

## v1.3.0 (2025-11-20)

### 📋 基础功能完善
- **多输出格式支持** - 统一支持table、json、yaml格式
- **配置管理优化** - 改善配置文件处理逻辑
- **错误处理增强** - 更友好的错误信息和异常处理

---

## v1.2.0 (2025-11-15)

### 🔐 IAM身份访问管理
- **IAM模块上线** - 用户、角色、权限管理
- **安全策略** - 支持细粒度权限控制
- **访问密钥管理** - AK/SK生命周期管理

---

## v1.1.0 (2025-11-10)

### 💾 Redis分布式缓存
- **Redis模块完整实现** - 实例管理、监控、备份恢复
- **多实例类型支持** - BASIC、PLUS、Classic版本
- **高可用配置** - 主从复制、集群模式支持

---

## v1.0.0 (2025-11-01)

### 🎉 首次正式发布
- **ECS云服务器管理** - 完整的ECS生命周期管理
- **监控服务集成** - 28个监控API，全方位资源监控
- **安全卫士支持** - 主机安全、漏洞扫描、威胁检测
- **计费查询** - 实时账单、成本分析
- **VPC网络管理** - 虚拟私有云、子网、安全组管理
- **EBS存储管理** - 云硬盘、快照、备份管理

---

## 📈 版本统计

### 版本发布节奏
- **主版本**：每年1-2次重大架构升级
- **次版本**：每2-4周功能迭代更新
- **修订版本**：根据bug修复需要随时发布

### 功能覆盖统计
- **云服务覆盖**：8大核心天翼云服务
- **API接口**：156+个完整API实现
- **CLI命令**：136+个用户命令
- **输出格式**：支持table、json、yaml三种格式
- **认证方式**：支持AK/SK、环境变量、配置文件

---

*最后更新：2025-12-08*
*维护团队：CTyun CLI开发团队*