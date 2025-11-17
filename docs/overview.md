# 天翼云CLI工具 - 项目概述

## 项目简介

天翼云CLI工具是一个基于终端的云资源管理平台，提供完整的天翼云API操作功能。该工具基于Python开发，采用模块化架构设计，支持云服务器、存储、网络等多种云资源的管理操作。

## 核心特性

### 🔐 安全认证
- **AK/SK签名认证**: 实现天翼云标准的签名认证机制
- **多配置文件支持**: 支持开发、测试、生产等多环境配置
- **安全存储**: 配置文件加密存储，支持环境变量覆盖

### 🖥️ 云服务器管理
- **生命周期管理**: 创建、启动、停止、重启、删除实例
- **批量操作**: 支持批量启动、停止、删除实例
- **规格调整**: 在线调整实例配置规格
- **镜像管理**: 创建、查询、管理自定义镜像
- **控制台访问**: 获取实例远程控制台URL

### 💾 存储管理
- **对象存储**: 文件上传、下载、删除、权限管理
- **云硬盘**: 创建、挂载、卸载、扩容云硬盘
- **备份管理**: 自动化备份策略和备份清理

### 🌐 网络管理
- **VPC管理**: 创建、配置虚拟私有网络
- **安全组**: 配置网络安全组和防火墙规则
- **弹性IP**: 管理、分配、释放弹性公网IP

### 📊 监控查询
- **实时监控**: CPU、内存、磁盘、网络等监控数据
- **日志查询**: 查询操作日志和系统日志
- **告警管理**: 配置监控告警规则

### ⚡ 高级功能
- **自动化脚本**: 提供完整的自动化运维示例
- **多种输出格式**: 支持表格、JSON、YAML等输出格式
- **错误处理**: 完善的错误处理和重试机制
- **调试支持**: 详细的调试日志和错误追踪

## 技术架构

### 架构设计原则
- **SOLID原则**: 遵循单一职责、开闭原则等设计原则
- **模块化**: 高内聚、低耦合的模块设计
- **可扩展性**: 易于添加新的云服务和功能
- **可维护性**: 清晰的代码结构和完整的文档

### 核心模块

```
ctyun-cli/
├── src/
│   ├── auth/           # 认证模块
│   │   └── signature.py    # AK/SK签名认证实现
│   ├── client.py           # 核心API客户端
│   ├── config/             # 配置管理
│   │   └── settings.py     # 配置文件处理
│   ├── ecs/                # 云服务器管理
│   │   ├── client.py       # ECS API客户端
│   │   └── commands.py     # ECS命令行接口
│   ├── cli/                # 命令行界面
│   │   └── main.py         # CLI主入口
│   └── utils/              # 工具函数
│       └── helpers.py      # 通用辅助函数
├── tests/                  # 测试文件
├── docs/                   # 文档
├── examples/               # 示例代码
└── requirements.txt        # Python依赖
```

### 技术栈
- **Python 3.8+**: 主要开发语言
- **Click**: 命令行界面框架
- **Requests**: HTTP客户端库
- **Cryptography**: 加密和签名算法
- **Tabulate**: 表格格式化
- **Colorama**: 终端彩色输出
- **PyYAML**: YAML格式支持

## 安装和部署

### 环境要求
- Python 3.8或更高版本
- 操作系统: Windows, macOS, Linux
- 网络连接 (用于访问天翼云API)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd ctyun-cli
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置认证信息**
   ```bash
   python setup_config.py
   ```

4. **测试安装**
   ```bash
   python -m ctyun-cli test
   ```

### 配置说明

配置文件位置: `~/.ctyun/config`

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

## 使用示例

### 基本命令

```bash
# 查看帮助
python -m ctyun-cli --help

# 列出云服务器实例
python -m ctyun-cli ecs list

# 创建实例
python -m ctyun-cli ecs create \
  --name "my-server" \
  --instance-type s6.small \
  --image-id img-ubuntu20

# 批量启动实例
python -m ctyun-cli ecs batch-start i-12345678 i-87654321
```

### 自动化脚本

```python
from src.client import CTYUNClient
from src.ecs.client import ECSClient

# 创建客户端
client = CTYUNClient()
ecs_client = ECSClient(client)

# 列出运行中的实例
instances = ecs_client.list_instances(status='running')
for instance in instances['instances']:
    print(f"实例: {instance['instanceName']} ({instance['instanceId']})")
```

## 开发指南

### 添加新的云服务

1. **创建服务客户端**
   ```python
   # src/newservice/client.py
   class NewServiceClient:
       def __init__(self, client: CTYUNClient):
           self.client = client
           self.service = 'newservice'
   ```

2. **创建命令行接口**
   ```python
   # src/newservice/commands.py
   import click
   from cli.main import handle_error, format_output

   @click.group()
   def newservice():
       """新服务管理"""
       pass
   ```

3. **注册到主CLI**
   ```python
   # src/cli/main.py
   from newservice.commands import newservice
   cli.add_command(newservice, name='newservice')
   ```

### 测试

```bash
# 运行基本测试
python tests/test_basic.py

# 使用pytest运行所有测试
pytest tests/
```

### 代码规范

- 遵循PEP 8编码规范
- 使用类型提示 (Type Hints)
- 编写完整的文档字符串
- 保持函数简洁和单一职责

## 路线图

### 近期计划 (v1.1)
- [ ] 完善存储管理功能
- [ ] 增强监控和日志功能
- [ ] 添加更多实例规格选项
- [ ] 优化批量操作性能

### 中期计划 (v1.5)
- [ ] 支持容器服务管理
- [ ] 添加负载均衡器管理
- [ ] 实现配置模板功能
- [ ] 支持多区域部署

### 长期计划 (v2.0)
- [ ] Web界面管理
- [ ] 图形化配置工具
- [ ] 插件系统
- [ ] 国际化支持

## 贡献指南

### 如何贡献

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 问题反馈

- 使用GitHub Issues报告问题
- 提供详细的错误信息和复现步骤
- 包含相关的日志和配置信息

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: [GitHub Repository]
- 文档: [Documentation Link]
- 问题反馈: [Issues Link]
- 邮箱: your.email@example.com

---

**注意**: 这是一个演示项目，用于展示天翼云CLI工具的设计和实现。在实际使用中，需要根据天翼云官方API文档进行相应的调整和完善。