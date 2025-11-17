# 天翼云CLI工具使用指南

## 安装

### 环境要求
- Python 3.8+
- 操作系统: Windows, macOS, Linux

### 安装依赖
```bash
pip install -r requirements.txt
```

### 安装CLI工具
```bash
pip install -e .
```

## 配置

### 初始化配置
```bash
python setup_config.py
```

### 手动配置
```bash
# 设置认证信息
python -m ctyun-cli configure \
  --access-key YOUR_ACCESS_KEY \
  --secret-key YOUR_SECRET_KEY \
  --region cn-north-1

# 查看当前配置
python -m ctyun-cli show-config

# 列出所有配置文件
python -m ctyun-cli list-profiles
```

### 配置文件格式
配置文件保存在 `~/.ctyun/config`，格式如下：

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

## 基本用法

### 全局选项
- `--profile`: 指定配置文件
- `--output`: 输出格式 (table/json/yaml)
- `--debug`: 启用调试模式
- `--region`: 指定区域
- `--access-key`: 访问密钥
- `--secret-key`: 密钥

### 命令格式
```bash
python -m ctyun-cli [全局选项] <命令组> <子命令> [选项] [参数]
```

## 云服务器(ECS)管理

### 列出实例
```bash
# 列出所有实例
python -m ctyun-cli ecs list

# 分页列出实例
python -m ctyun-cli ecs list --page 1 --page-size 10

# 按状态过滤
python -m ctyun-cli ecs list --status running

# 按实例规格过滤
python -m ctyun-cli ecs list --instance-type s6.small
```

### 实例管理
```bash
# 查看实例详情
python -m ctyun-cli ecs show i-12345678

# 创建实例
python -m ctyun-cli ecs create \
  --name "my-instance" \
  --instance-type s6.small \
  --image-id img-ubuntu20 \
  --system-disk-size 50

# 启动实例
python -m ctyun-cli ecs start i-12345678

# 停止实例
python -m ctyun-cli ecs stop i-12345678

# 重启实例
python -m ctyun-cli ecs reboot i-12345678

# 删除实例 (需要确认)
python -m ctyun-cli ecs delete i-12345678 --confirm
```

### 批量操作
```bash
# 批量启动实例
python -m ctyun-cli ecs batch-start i-12345678 i-87654321

# 批量停止实例
python -m ctyun-cli ecs batch-stop i-12345678 i-87654321

# 批量删除实例 (需要确认)
python -m ctyun-cli ecs batch-delete i-12345678 i-87654321 --confirm
```

### 实例规格管理
```bash
# 列出可用实例规格
python -m ctyun-cli ecs instance-types

# 调整实例规格
python -m ctyun-cli ecs resize i-12345678 s6.medium
```

### 镜像管理
```bash
# 列出公共镜像
python -m ctyun-cli ecs images --type public

# 列出Ubuntu镜像
python -m ctyun-cli ecs images --os-type Ubuntu

# 创建实例镜像
python -m ctyun-cli ecs create-image i-12345678 --name "my-image" --description "My custom image"
```

### 控制台和监控
```bash
# 获取实例控制台URL
python -m ctyun-cli ecs console i-12345678

# 获取实例监控数据
python -m ctyun-cli ecs monitoring i-12345678 CPUUtilization 2024-01-01T00:00:00Z 2024-01-01T23:59:59Z
```

## 输出格式

### 表格格式 (默认)
```bash
python -m ctyun-cli ecs list --output table
```

### JSON格式
```bash
python -m ctyun-cli ecs list --output json
```

### YAML格式
```bash
python -m ctyun-cli ecs list --output yaml
```

## 错误处理

### 常见错误码
- `InvalidAccessKey`: 访问密钥无效
- `SignatureMismatch`: 签名不匹配
- `InstanceNotFound`: 实例不存在
- `InsufficientBalance`: 余额不足
- `QuotaExceeded`: 配额超限

### 调试模式
```bash
python -m ctyun-cli --debug ecs list
```

## 高级功能

### 多配置文件
```bash
# 创建开发环境配置
python -m ctyun-cli configure --profile dev \
  --access-key DEV_ACCESS_KEY \
  --secret-key DEV_SECRET_KEY \
  --region cn-north-1

# 使用开发环境配置
python -m ctyun-cli --profile dev ecs list
```

### 环境变量
```bash
export CTYUN_ACCESS_KEY=YOUR_ACCESS_KEY
export CTYUN_SECRET_KEY=YOUR_SECRET_KEY
export CTYUN_REGION=cn-north-1

python -m ctyun-cli ecs list
```

### 配置文件覆盖
```bash
# 命令行参数覆盖配置文件
python -m ctyun-cli --region cn-east-1 ecs list
```

## 最佳实践

### 1. 安全配置
- 不要在脚本中硬编码密钥
- 使用环境变量或配置文件
- 定期轮换密钥
- 限制配置文件权限 (600)

### 2. 批量操作
- 使用批量操作提高效率
- 在批量删除前先列出不确认
- 监控批量操作状态

### 3. 监控和日志
- 启用调试模式排查问题
- 配置日志文件记录操作
- 设置监控告警

### 4. 自动化脚本
```bash
#!/bin/bash
# 自动化脚本示例

# 检查实例状态
python -m ctyun-cli ecs show i-12345678 --output json | jq -r '.status'

# 批量启动停止的实例
for instance in $(python -m ctyun-cli ecs list --status stopped --output json | jq -r '.[].instanceId'); do
    python -m ctyun-cli ecs start $instance
    echo "启动实例: $instance"
done
```

## 故障排除

### 常见问题

**Q: 连接API超时**
A: 检查网络连接，增加超时时间，使用代理

**Q: 签名失败**
A: 检查系统时间，确认密钥正确，检查区域设置

**Q: 实例不存在**
A: 确认实例ID正确，检查区域设置

**Q: 权限不足**
A: 检查密钥权限，联系管理员

### 日志位置
- 配置文件: `~/.ctyun/config`
- 日志文件: 配置文件中指定的路径
- 调试输出: 使用 `--debug` 选项

## 支持和帮助

### 获取帮助
```bash
# 查看主帮助
python -m ctyun-cli --help

# 查看子命令帮助
python -m ctyun-cli ecs --help
python -m ctyun-cli ecs list --help
```

### 版本信息
```bash
python -m ctyun-cli --version
```

### 测试连接
```bash
python -m ctyun-cli test
```